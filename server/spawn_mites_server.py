import threading
import random
import time

class MitesThread(threading.Thread):
    def __init__(self, zonas, shared_mites, lock, game_state):
        super().__init__()
        self.zonas = zonas
        self.shared_mites = shared_mites
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
        print("[MitesThread] Iniciando la dispersión de virus (blancos y verdes)...")
        while not self._stop_event.is_set():
            if self.game_state.get('game_over', False):
                break
            time.sleep(random.uniform(0.5, 1.5))
            zona_key = random.choice(list(self.zonas.keys()))
            ancho, alto = self.zonas[zona_key]
            ox, oy = self.zona_offsets[zona_key]
            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)
            virus_color = 'green' if random.random() < 0.2 else 'white'
            virus = {
                'x': x,
                'y': y,
                'active': True,
                'color': virus_color
            }
            with self.lock:
                self.shared_mites.append(virus)
            color_txt = "VERDE" if virus_color == 'green' else "BLANCO"
            print(f"[MitesThread] Nuevo virus {color_txt} en {zona_key}: ({x}, {y})")

    def stop(self):
        self._stop_event.set()
