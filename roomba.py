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

        self.current_path = []
        self.target_mite = None

        self.cleaning_started = False
        self.start_time = None
        self.end_time = None

    def run(self):
        control_mode = self.state.get('control_mode', 'auto')

        while not self._stop_event.is_set():
            # Si es manual => BFS inactivo
            if control_mode == 'manual':
                time.sleep(0.1)
                continue

            # Radiación game over
            if self.radiation_state and self.radiation_state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por radiación!")
                time.sleep(1)
                continue

            # Vidas game over
            if self.state.get('vidas', 1) <= 0:
                print("[RoombaThread] ¡El robot se quedó sin vidas! Game Over.")
                time.sleep(1)
                continue

            # Iniciar cronómetro si hay virus
            if not self.cleaning_started and self.there_are_mites():
                self.cleaning_started = True
                self.start_time = time.time()
                print("[RoombaThread] Empieza la limpieza (automática)...")

            # Si no hay virus => limpieza terminada
            if self.cleaning_started and not self.there_are_mites():
                if not self.end_time:
                    self.end_time = time.time()
                    total_time = self.end_time - self.start_time
                    self.state['clean_time'] = total_time
                    print(f"[RoombaThread] ¡Limpieza terminada! Tiempo total: {total_time:.2f} s")
                time.sleep(1)
                continue

            # BFS para virus
            if not self.target_mite:
                mite = self.get_closest_mite()
                if mite:
                    self.target_mite = mite
                    self.current_path = self.compute_path_to(mite['x'], mite['y'])
                else:
                    time.sleep(1)
                    continue

            if self.current_path:
                nx, ny = self.current_path.pop(0)
                self.state['x'] = nx
                self.state['y'] = ny

                # Checar colisión con el virus
                if self.check_mite_collected(self.target_mite):
                    self.handle_virus_collected(self.target_mite)

                # Checar colisión con enemigos => quitan 1 vida
                self.check_enemy_collisions()

            else:
                self.target_mite = None

            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()

    # =========== Virus Lógica ===========
    def there_are_mites(self):
        with self.mites_lock:
            for m in self.shared_mites:
                if m.get('active', True):
                    return True
        return False

    def get_closest_mite(self):
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
        rx, ry = self.state['x'], self.state['y']
        dx = mite['x'] - rx
        dy = mite['y'] - ry
        dist_sq = dx**2 + dy**2
        return dist_sq < (self.state['radius'] + 3)**2

    def handle_virus_collected(self, mite):
        with self.mites_lock:
            mite['active'] = False

        # Sumar puntuación
        if 'score' in self.state:
            self.state['score'] += 10

        # Si es verde => reduce radiación
        if self.radiation_state and mite.get('color') == 'green':
            self.reduce_radiation_10_percent()

        self.target_mite = None
        self.current_path = []

    # =========== Enemigos Lógica ===========
    def check_enemy_collisions(self):
        """
        Checa si el robot colisiona con algún enemigo.
        Si colisiona => quita 1 vida y desactiva el enemigo.
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
                        # Colisión => resta 1 vida
                        enemy['active'] = False
                        self.state['vidas'] -= 1
                        print("[RoombaThread] ¡Colisión con enemigo! Vidas restantes:", self.state['vidas'])
                        if self.state['vidas'] <= 0:
                            self.state['vidas'] = 0
                            # Marcamos game_over
                            self.state['game_over'] = True
                            print("[RoombaThread] ¡El robot se quedó sin vidas! Game Over.")

    # =========== Radiación ===========
    def reduce_radiation_10_percent(self):
        rad_level = self.radiation_state.get('radiacion', 0)
        new_level = rad_level * 0.9
        self.radiation_state['radiacion'] = max(0, new_level)

    # =========== BFS ===========
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

        return []

    def snap(self, val):
        return int(round(val / GRID_STEP) * GRID_STEP)

    def get_neighbors(self, cx, cy):
        neighbors = []
        for dx, dy in [(GRID_STEP,0), (-GRID_STEP,0), (0,GRID_STEP), (0,-GRID_STEP)]:
            nx = cx + dx
            ny = cy + dy
            if self.in_barrera(nx, ny, self.state['radius']) and not self.in_hueco(nx, ny, self.state['radius']):
                neighbors.append((nx, ny))
        return neighbors

    def in_barrera(self, x, y, r):
        min_x, min_y, max_x, max_y = BARRERA
        return (x - r >= min_x and
                x + r <  max_x and
                y - r >= min_y and
                y + r <  max_y)

    def in_hueco(self, x, y, r):
        hx, hy, hw, hh = HUECO_RECT
        closest_x = max(hx, min(x, hx+hw))
        closest_y = max(hy, min(y, hy+hh))
        dist_x = x - closest_x
        dist_y = y - closest_y
        dist_sq = dist_x**2 + dist_y**2
        return dist_sq < (r*r)

    def build_path(self, parent, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent[current]
        path.append(start)
        path.reverse()
        return path
