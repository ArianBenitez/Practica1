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

    def run(self):
        while not self._stop_event.is_set():
            # Si no tenemos objetivo, buscar el ácaro más cercano
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

            time.sleep(0.05)

    def stop(self):
        self._stop_event.set()

    def get_closest_mite(self):
        """
        Devuelve el ácaro activo más cercano al robot, o None si no hay.
        """
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
        """
        Verifica si la posición del robot está lo bastante cerca
        del ácaro para considerarlo recogido.
        """
        rx, ry = self.state['x'], self.state['y']
        dx = mite['x'] - rx
        dy = mite['y'] - ry
        dist_sq = dx*dx + dy*dy
        return dist_sq < (self.state['radius'] + 3)**2

    def compute_path_to(self, tx, ty):
        """
        BFS en una rejilla de 10 px para evitar el hueco.
        Devuelve lista de (x, y).
        """
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
        dist_sq = dist_x*dist_x + dist_y*dist_y
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
