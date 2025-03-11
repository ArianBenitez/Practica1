# roomba.py
import threading
import time
import math
from collections import deque

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
HUECO_RECT = (151, 180, 89, 260)  # (x, y, w, h) no transitable
GRID_STEP = 10  # tamaño de celda para BFS

class RoombaThread(threading.Thread):
    def __init__(self, roomba_state, shared_mites, lock):
        super().__init__()
        self.state = roomba_state
        self.shared_mites = shared_mites
        self.lock = lock
        self._stop_event = threading.Event()
        self.current_path = []
        self.target_mite = None

        self.cleaning_started = False   # Indica si hemos empezado a limpiar
        self.start_time = None         # Momento en que empieza a limpiar
        self.end_time = None           # Momento en que termina (cuando no queden ácaros)

    def run(self):
        while not self._stop_event.is_set():
            # Si no hemos iniciado la limpieza y hay al menos un ácaro,
            # marcamos el inicio (start_time)
            if not self.cleaning_started:
                if self.there_are_mites():
                    self.cleaning_started = True
                    self.start_time = time.time()
                    print("[RoombaThread] Empieza la limpieza...")

            # Si no hay ácaros activos, puede que hayamos terminado
            if self.cleaning_started and not self.there_are_mites():
                # Si no teníamos end_time, lo fijamos
                if not self.end_time:
                    self.end_time = time.time()
                    total_time = self.end_time - self.start_time
                    self.state['clean_time'] = total_time
                    print(f"[RoombaThread] ¡Limpieza terminada! Tiempo total: {total_time:.2f} s")

                # Ya no hay nada que hacer; podemos dormir un rato
                time.sleep(1)
                continue

            # Lógica normal de BFS para recoger ácaros
            if not self.target_mite:
                mite = self.get_closest_mite()
                if mite:
                    self.target_mite = mite
                    self.current_path = self.compute_path_to(mite['x'], mite['y'])
                else:
                    # No hay ácaros activos
                    time.sleep(1)
                    continue

            if self.current_path:
                nx, ny = self.current_path.pop(0)
                self.state['x'] = nx
                self.state['y'] = ny
                # Comprobar si recogimos el ácaro
                if self.check_mite_collected(self.target_mite):
                    with self.lock:
                        self.target_mite['active'] = False
                    self.target_mite = None
                    self.current_path = []
            else:
                # No hay camino => descartar este ácaro
                self.target_mite = None

            time.sleep(0.1)  # velocidad del robot (más lento)

    def stop(self):
        self._stop_event.set()

    def there_are_mites(self):
        """
        Retorna True si hay al menos un ácaro activo.
        """
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
