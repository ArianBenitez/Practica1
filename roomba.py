import threading
import time
import math
from collections import deque

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

HUECO_RECT = (151, 280, 89, 260)
BARRERA = (50, 130, 550, 760)
GRID_STEP = 10

class RoombaThread(threading.Thread):
    def __init__(self, roomba_state, shared_mites, mites_lock, shared_enemies, enemies_lock, radiation_state=None):
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

        # Variables para la ruta actual y objetivo
        self.current_path = None
        self.current_target = None
        self.path_index = 0

        # Variables para detectar si el robot se queda atascado
        self.stuck_counter = 0
        self.last_position = (self.state['x'], self.state['y'])

    def run(self):
        control_mode = self.state.get('control_mode', 'auto')
        while not self._stop_event.is_set():
            # Modo manual: no se aplica BFS
            if control_mode == 'manual':
                time.sleep(0.1)
                continue

            # Verificar condiciones de Game Over
            if self.radiation_state and self.radiation_state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por radiación!")
                time.sleep(0.5)
                continue
            if self.state.get('vidas', 1) <= 0 or self.state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por vidas!")
                time.sleep(0.5)
                continue

            # Iniciar cronómetro si hay virus
            if not self.cleaning_started and self.there_are_mites():
                self.cleaning_started = True
                self.start_time = time.time()
                print("[RoombaThread] Empieza la limpieza (automática)...")

            # Si se inició y no hay virus, terminar la limpieza
            if self.cleaning_started and not self.there_are_mites():
                if not self.end_time:
                    self.end_time = time.time()
                    total_time = self.end_time - self.start_time
                    self.state['clean_time'] = total_time
                    print(f"[RoombaThread] ¡Limpieza terminada! Tiempo total: {total_time:.2f} s")
                time.sleep(0.5)
                continue

            # Si no hay ruta actual o el objetivo dejó de estar activo, buscar un virus alcanzable
            if not self.current_path or not self.current_target or not self.current_target.get('active', False):
                target, path = self.get_reachable_mite()
                if target is None or not path:
                    time.sleep(0.1)
                    continue
                self.current_target = target
                self.current_path = path
                self.path_index = 0

            # Si la ruta es demasiado corta, reiniciar para recalcular
            if not self.current_path or len(self.current_path) < 2:
                self.current_path = None
                time.sleep(0.1)
                continue

            # Avanzar un paso en la ruta calculada
            self.path_index += 1
            if self.path_index >= len(self.current_path):
                self.current_path = None
                continue

            next_x, next_y = self.current_path[self.path_index]
            self.state['x'] = next_x
            self.state['y'] = next_y

            # Detectar si el robot se queda atascado
            current_position = (self.state['x'], self.state['y'])
            if current_position == self.last_position:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
            self.last_position = current_position

            if self.stuck_counter >= 3:
                print("[RoombaThread] Robot atascado, recalculando ruta...")
                self.current_path = None
                self.stuck_counter = 0
                time.sleep(0.1)
                continue

            # Verificar colisión con el virus objetivo
            if self.check_mite_collected(self.current_target):
                self.handle_virus_collected(self.current_target)
                self.current_path = None  # Reiniciar para buscar otro virus

            # Verificar colisión con enemigos
            self.check_enemy_collisions()

            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()

    # ================== Lógica para Virus ==================
    def there_are_mites(self):
        with self.mites_lock:
            # Eliminar virus inactivos para evitar acumulación
            self.shared_mites[:] = [m for m in self.shared_mites if m.get('active', True)]
            for m in self.shared_mites:
                if m.get('active', True):
                    return True
        return False

    def get_reachable_mite(self):
        """
        Itera sobre todos los virus activos y retorna el primero (o el más cercano)
        que tenga una ruta válida (longitud >= 2) según BFS.
        """
        reachable = []
        with self.mites_lock:
            # Limpiar la lista eliminando virus inactivos
            self.shared_mites[:] = [m for m in self.shared_mites if m.get('active', True)]
            for m in self.shared_mites:
                if m.get('active', True):
                    path = self.compute_path_to(m['x'], m['y'])
                    if path and len(path) >= 2:
                        dist = math.hypot(m['x'] - self.state['x'], m['y'] - self.state['y'])
                        reachable.append((dist, m, path))
        if reachable:
            reachable.sort(key=lambda x: x[0])
            return reachable[0][1], reachable[0][2]
        return None, None

    def check_mite_collected(self, mite):
        rx, ry = self.state['x'], self.state['y']
        dx = mite['x'] - rx
        dy = mite['y'] - ry
        dist_sq = dx * dx + dy * dy
        return dist_sq < (self.state['radius'] + 3) ** 2

    def handle_virus_collected(self, mite):
        with self.mites_lock:
            if mite in self.shared_mites:
                self.shared_mites.remove(mite)
        if 'score' in self.state:
            self.state['score'] += 10
        if self.radiation_state and mite.get('color') == 'green':
            self.reduce_radiation_10_percent()

    # ================== Lógica para Enemigos ==================
    def check_enemy_collisions(self):
        rx = self.state['x']
        ry = self.state['y']
        rrad = self.state['radius']
        with self.enemies_lock:
            for enemy in self.shared_enemies:
                if enemy.get('active', True):
                    dx = enemy['x'] - rx
                    dy = enemy['y'] - ry
                    dist_sq = dx * dx + dy * dy
                    if dist_sq < (rrad + 10) ** 2:
                        enemy['active'] = False
                        self.state['vidas'] -= 1
                        print("[RoombaThread] ¡Colisión con enemigo! Vidas restantes:", self.state['vidas'])
                        if self.state['vidas'] <= 0:
                            self.state['vidas'] = 0
                            self.state['game_over'] = True
                            print("[RoombaThread] El robot se quedó sin vidas. Game Over.")

    def reduce_radiation_10_percent(self):
        rad_level = self.radiation_state.get('radiacion', 0)
        new_level = rad_level * 0.9
        self.radiation_state['radiacion'] = max(0, new_level)

    # ================== BFS ==================
    def compute_path_to(self, tx, ty):
        start = (self.snap(self.state['x']), self.snap(self.state['y']))
        goal = (self.snap(tx), self.snap(ty))
        queue = deque([start])
        visited = set([start])
        parent = {}
        while queue:
            current = queue.popleft()
            if current == goal:
                return self.build_path(parent, start, goal)
            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        return []  # No se encontró ruta

    def snap(self, val):
        return int(round(val / GRID_STEP) * GRID_STEP)

    def get_neighbors(self, cx, cy):
        neighbors = []
        for dx, dy in [(GRID_STEP, 0), (-GRID_STEP, 0), (0, GRID_STEP), (0, -GRID_STEP)]:
            nx = cx + dx
            ny = cy + dy
            if self.in_barrera(nx, ny, self.state['radius']) and not self.in_hueco(nx, ny, self.state['radius']):
                neighbors.append((nx, ny))
        return neighbors

    def in_barrera(self, x, y, r):
        min_x, min_y, max_x, max_y = BARRERA
        return (x - r >= min_x and
                x + r < max_x and
                y - r >= min_y and
                y + r < max_y)

    def in_hueco(self, x, y, r):
        hx, hy, hw, hh = HUECO_RECT
        closest_x = max(hx, min(x, hx + hw))
        closest_y = max(hy, min(y, hy + hh))
        dist_x = x - closest_x
        dist_y = y - closest_y
        dist_sq = dist_x ** 2 + dist_y ** 2
        return dist_sq < (r * r)

    def build_path(self, parent, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent[current]
        path.append(start)
        path.reverse()
        return path
