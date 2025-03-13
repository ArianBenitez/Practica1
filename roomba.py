import threading
import time
import math
from collections import deque

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
# Hueco más abajo, ancho=89, alto=160 => se puede rodear
HUECO_RECT = (151, 380, 89, 160)
GRID_STEP = 10

class RoombaThread(threading.Thread):
    def __init__(self, roomba_state, shared_mites, lock, radiation_state=None):
        super().__init__()
        self.state = roomba_state
        self.shared_mites = shared_mites
        self.lock = lock
        self.radiation_state = radiation_state
        self._stop_event = threading.Event()

        self.current_path = []
        self.target_mite = None

        self.cleaning_started = False
        self.start_time = None
        self.end_time = None

    def run(self):
        while not self._stop_event.is_set():
            # Checar game_over radiación
            if self.radiation_state and self.radiation_state.get('game_over', False):
                print("[RoombaThread] ¡Game Over por radiación!")
                time.sleep(1)
                continue

            # Checar vidas
            if self.state.get('vidas', 1) <= 0:
                print("[RoombaThread] ¡El robot se quedó sin vidas! Game Over.")
                time.sleep(1)
                continue

            # Iniciar cronómetro si hay virus
            if not self.cleaning_started and self.there_are_mites():
                self.cleaning_started = True
                self.start_time = time.time()
                print("[RoombaThread] Empieza la limpieza...")

            # Si no hay virus y habíamos empezado => limpieza terminada
            if self.cleaning_started and not self.there_are_mites():
                if not self.end_time:
                    self.end_time = time.time()
                    total_time = self.end_time - self.start_time
                    self.state['clean_time'] = total_time
                    print(f"[RoombaThread] ¡Limpieza terminada! Tiempo total: {total_time:.2f} s")
                time.sleep(1)
                continue

            # BFS
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

                if self.check_mite_collected(self.target_mite):
                    self.handle_virus_collected(self.target_mite)
            else:
                self.target_mite = None

            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()

    def there_are_mites(self):
        with self.lock:
            for m in self.shared_mites:
                if m.get('active', True):
                    return True
        return False

    def get_closest_mite(self):
        rx, ry = self.state['x'], self.state['y']
        closest = None
        min_dist = float('inf')
        with self.lock:
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
        dist_sq = dx*dx + dy*dy
        return dist_sq < (self.state['radius'] + 3)**2

    def handle_virus_collected(self, mite):
        with self.lock:
            mite['active'] = False

        # Sumar puntuación
        if 'score' in self.state:
            self.state['score'] += 10

        # Solo virus verdes reducen la radiación
        if self.radiation_state and mite.get('color') == 'green':
            self.reduce_radiation_10_percent()

        # Reset
        self.target_mite = None
        self.current_path = []

    def reduce_radiation_10_percent(self):
        with threading.Lock():
            rad_level = self.radiation_state.get('radiacion', 0)
            new_level = rad_level * 0.5  # reduce 10%
            self.radiation_state['radiacion'] = max(0, new_level)

    # ================ BFS ================
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
            if 0 <= nx < WINDOW_WIDTH and 0 <= ny < WINDOW_HEIGHT:
                if not self.in_hueco(nx, ny, self.state['radius']):
                    neighbors.append((nx, ny))
        return neighbors

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
