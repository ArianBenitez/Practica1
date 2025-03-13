import threading
import time
import math
from collections import deque

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

# Hueco radiactivo
HUECO_RECT = (151, 280, 89, 260)
# Límite de la barrera (rectángulo que engloba las zonas)
BARRERA = (50, 130, 550, 760)
GRID_STEP = 10

class RoombaThread(threading.Thread):
    """
    Hilo principal del nanobot (robot aspirador) que:
      - En modo automático: busca virus con BFS en cada iteración.
      - En modo manual: se mantiene inactivo para BFS y permite control externo.
      - Checa colisiones con virus (descontamina) y con enemigos (restan vidas).
      - Interactúa con la radiación: reduce al recoger virus verdes.
    """
    def __init__(
        self,
        roomba_state,
        shared_mites, mites_lock,
        shared_enemies, enemies_lock,
        radiation_state=None
    ):
        super().__init__()
        self.state = roomba_state
        self.shared_mites = shared_mites
        self.mites_lock = mites_lock
        self.shared_enemies = shared_enemies
        self.enemies_lock = enemies_lock
        self.radiation_state = radiation_state
        self._stop_event = threading.Event()

        self.cleaning_started = False
        self.start_time = None
        self.end_time = None

    def run(self):
        """
        Bucle principal:
          - Si modo manual, duerme y deja que game.py controle al robot.
          - Si modo automático, en cada iteración:
              1) Busca virus más cercano (euclídeo).
              2) Hace BFS en la rejilla discretizada a (virus.x, virus.y).
              3) Si la ruta es muy corta o repite la misma posición, descarta.
              4) Mueve un solo paso y checa colisiones.
              5) Repite mientras haya virus y no sea game_over.
        """
        control_mode = self.state.get('control_mode', 'auto')

        while not self._stop_event.is_set():
            # --- Modo Manual => no BFS ---
            if control_mode == 'manual':
                time.sleep(0.1)
                continue

            # --- Checar Game Over (radiación o vidas) ---
            if self.radiation_state and self.radiation_state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por radiación!")
                time.sleep(1)
                continue
            if self.state.get('vidas', 1) <= 0 or self.state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por vidas!")
                time.sleep(1)
                continue

            # --- Iniciar cronómetro si detecta virus ---
            if not self.cleaning_started and self.there_are_mites():
                self.cleaning_started = True
                self.start_time = time.time()
                print("[RoombaThread] Empieza la limpieza (automática)...")

            # --- Si ya no hay virus => limpieza terminada ---
            if self.cleaning_started and not self.there_are_mites():
                if not self.end_time:
                    self.end_time = time.time()
                    total_time = self.end_time - self.start_time
                    self.state['clean_time'] = total_time
                    print(f"[RoombaThread] ¡Limpieza terminada! Tiempo total: {total_time:.2f} s")
                time.sleep(1)
                continue

            # =========== BFS en cada iteración ===========
            # 1) Buscar virus más cercano
            mite = self.get_closest_mite()
            if not mite:
                # No hay virus activos
                time.sleep(1)
                continue

            # 2) Calcular BFS en la rejilla
            path = self.compute_path_to(mite['x'], mite['y'])
            if len(path) < 2:
                # Ruta vacía o solo 1 nodo => sin movimiento
                time.sleep(0.5)
                continue

            # 3) Mover un solo paso: path[1]
            next_x, next_y = path[1]
            # Evitar quedarse parado si BFS sugiere la misma posición
            if (next_x == self.state['x']) and (next_y == self.state['y']):
                time.sleep(0.5)
                continue

            # Avanzamos un paso
            self.state['x'] = next_x
            self.state['y'] = next_y

            # 4) Checar colisiones con virus y enemigos
            if self.check_mite_collected(mite):
                self.handle_virus_collected(mite)
            self.check_enemy_collisions()

            time.sleep(0.1)

    def stop(self):
        """
        Permite detener este hilo desde fuera.
        """
        self._stop_event.set()

    # ================== Lógica Virus ==================
    def there_are_mites(self):
        """
        Verifica si aún hay virus (motas) activos.
        """
        with self.mites_lock:
            for m in self.shared_mites:
                if m.get('active', True):
                    return True
        return False

    def get_closest_mite(self):
        """
        Devuelve el virus activo más cercano a la posición del nanobot 
        usando distancia euclídea.
        """
        rx, ry = self.state['x'], self.state['y']
        closest = None
        min_dist = float('inf')
        with self.mites_lock:
            for m in self.shared_mites:
                if m.get('active', True):
                    dx = m['x'] - rx
                    dy = m['y'] - ry
                    dist = math.hypot(dx, dy)
                    if dist < min_dist:
                        min_dist = dist
                        closest = m
        return closest

    def check_mite_collected(self, mite):
        """
        Revisa si el nanobot está lo bastante cerca del virus 
        para considerarlo recogido (desinfectado).
        """
        rx, ry = self.state['x'], self.state['y']
        dx = mite['x'] - rx
        dy = mite['y'] - ry
        dist_sq = dx*dx + dy*dy
        return dist_sq < (self.state['radius'] + 3)**2

    def handle_virus_collected(self, mite):
        """
        Marca el virus como inactivo, aumenta puntuación y 
        reduce radiación si es un virus verde (antídoto).
        """
        with self.mites_lock:
            mite['active'] = False
        if 'score' in self.state:
            self.state['score'] += 10
        if self.radiation_state and mite.get('color') == 'green':
            self.reduce_radiation_10_percent()

    # ================== Lógica Enemigos ==================
    def check_enemy_collisions(self):
        """
        Verifica si hay colisión con enemigos rojos, 
        restando 1 vida al robot en caso de impacto.
        """
        rx = self.state['x']
        ry = self.state['y']
        rrad = self.state['radius']

        with self.enemies_lock:
            for enemy in self.shared_enemies:
                if enemy.get('active', True):
                    dx = enemy['x'] - rx
                    dy = enemy['y'] - ry
                    dist_sq = dx**2 + dy**2
                    if dist_sq < (rrad + 10)**2:
                        enemy['active'] = False
                        self.state['vidas'] -= 1
                        print("[RoombaThread] ¡Colisión con enemigo! Vidas restantes:", self.state['vidas'])
                        if self.state['vidas'] <= 0:
                            self.state['vidas'] = 0
                            self.state['game_over'] = True
                            print("[RoombaThread] El robot se quedó sin vidas. Game Over.")

    # ================== Radiación ==================
    def reduce_radiation_10_percent(self):
        """
        Cada virus verde reduce un 10% la radiación del laboratorio.
        """
        rad_level = self.radiation_state.get('radiacion', 0)
        new_level = rad_level * 0.9
        self.radiation_state['radiacion'] = max(0, new_level)

    # ================== BFS en la Rejilla ==================
    def compute_path_to(self, tx, ty):
        """
        Recalcula un camino BFS desde la posición actual del robot
        hasta (tx, ty), discretizando a GRID_STEP=10.

        Devuelve la lista de celdas (x,y) si hay ruta, o [] si no hay.
        """
        # 1) Snap a la rejilla
        start = (self.snap(self.state['x']), self.snap(self.state['y']))
        goal = (self.snap(tx), self.snap(ty))

        # BFS
        queue = deque([start])
        visited = set([start])
        parent = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                return self.build_path(parent, start, goal)

            # Expansión a vecinos
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        # No se encontró ruta
        return []

    def snap(self, val):
        """
        Ajusta val al múltiplo de GRID_STEP más cercano (discretización BFS).
        """
        return int(round(val / GRID_STEP) * GRID_STEP)

    def get_neighbors(self, cell):
        """
        Retorna celdas adyacentes (arriba, abajo, izq, der) en la rejilla
        si no chocan con el hueco ni salen de la barrera.
        """
        cx, cy = cell
        directions = [(GRID_STEP,0), (-GRID_STEP,0), (0,GRID_STEP), (0,-GRID_STEP)]
        neighbors = []
        for dx, dy in directions:
            nx = cx + dx
            ny = cy + dy
            if self.is_passable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def is_passable(self, x, y):
        """
        Verifica que (x,y) esté dentro de la barrera y fuera del hueco,
        y dentro de la ventana. Ajusta si deseas.
        """
        # 1) Dentro de la ventana
        if x < 0 or x >= WINDOW_WIDTH or y < 0 or y >= WINDOW_HEIGHT:
            return False

        # 2) Dentro de la barrera
        min_x, min_y, max_x, max_y = BARRERA
        # Ajustamos la colisión con radius=10 si deseas
        # pero aquí asumimos la celda en el grid
        if not (min_x <= x < max_x and min_y <= y < max_y):
            return False

        # 3) Fuera del hueco radiactivo
        hx, hy, hw, hh = HUECO_RECT
        # Verificamos si (x,y) cae en el rect del hueco
        if (hx <= x < hx+hw) and (hy <= y < hy+hh):
            return False

        return True

    def build_path(self, parent, start, goal):
        """
        Reconstruye la ruta BFS con parent[] hasta llegar a start.
        """
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent[current]
        path.append(start)
        path.reverse()
        return path
