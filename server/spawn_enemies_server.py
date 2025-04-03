import threading
import random
import time

class EnemiesThread(threading.Thread):
    def __init__(self, zonas, shared_enemies, lock, game_state):
        super().__init__()
        self.zonas = zonas
        self.shared_enemies = shared_enemies
        self.lock = lock
        self.game_state = game_state
        self._stop_event = threading.Event()
        self.zona_offsets = {
            'Zona 1': (50, 130),
            'Zona 2': (50, 280),
            'Zona 3': (240, 280),
            'Zona 4': (151, 540),
        }

    def run(self):
        print("[EnemiesThread] Iniciando la aparición de enemigos rojos...")
        while not self._stop_event.is_set():
            if self.game_state.get('game_over', False):
                break
            time.sleep(random.uniform(2.0, 4.0))
            zona_key = random.choice(list(self.zonas.keys()))
            ancho, alto = self.zonas[zona_key]
            ox, oy = self.zona_offsets[zona_key]
            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)
            enemy = {
                'x': x,
                'y': y,
                'active': True,
                'color': 'red'
            }
            with self.lock:
                self.shared_enemies.append(enemy)
            print(f"[EnemiesThread] ¡Nuevo enemigo en {zona_key}: ({x}, {y})")

    def stop(self):
        self._stop_event.set()
