# spawn_mites.py
import threading
import random
import time

class MitesThread(threading.Thread):
    def __init__(self, zonas, shared_mites, lock):
        """
        :param zonas: dict con {'Zona 1': (ancho, alto), ...}
        :param shared_mites: lista donde se guardan los ácaros
        :param lock: lock para sincronizar acceso
        """
        super().__init__()
        self.zonas = zonas
        self.shared_mites = shared_mites
        self.lock = lock
        self._stop_event = threading.Event()

        # Offsets para cada zona
        self.zona_offsets = {
            'Zona 1': (50, 30),
            'Zona 2': (50, 180),
            'Zona 3': (240, 180),
            'Zona 4': (151, 440),
        }

    def run(self):
        """
        Bucle infinito que, cada 0.5-1.5 segundos, genera un ácaro
        en una zona aleatoria, en una posición aleatoria.
        """
        while not self._stop_event.is_set():
            time.sleep(random.uniform(0.5, 1.5))

            zona_key = random.choice(list(self.zonas.keys()))
            ancho, alto = self.zonas[zona_key]
            ox, oy = self.zona_offsets[zona_key]

            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)
            mite = {
                'x': x,
                'y': y,
                'active': True
            }
            with self.lock:
                self.shared_mites.append(mite)

            print(f"[MitesThread] Nuevo ácaro en {zona_key}: ({x}, {y})")

    def stop(self):
        self._stop_event.set()
