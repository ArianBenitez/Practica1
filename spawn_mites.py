import threading
import random
import time

class MitesThread(threading.Thread):
    """
    Hilo que genera 'virus' blancos o verdes en distintas zonas.
    - Blancos no reducen radiación.
    - Verdes (20% de prob.) reducen radiación al ser recogidos por el nanobot.
    """
    def __init__(self, zonas, shared_mites, lock):
        super().__init__()
        self.zonas = zonas
        self.shared_mites = shared_mites
        self.lock = lock
        self._stop_event = threading.Event()

        # Offsets para cada zona (desplazadas +100 en Y)
        self.zona_offsets = {
            'Zona 1': (50, 130),
            'Zona 2': (50, 280),
            'Zona 3': (240, 280),
            'Zona 4': (151, 540),
        }

    def run(self):
        """
        Dispersa virus de manera concurrente.
        Representa la contaminación que aparece constantemente 
        en el Laboratorio de Virus.
        """
        print("[MitesThread] Iniciando la dispersión de virus (blancos y verdes)...")
        while not self._stop_event.is_set():
            time.sleep(random.uniform(0.5, 1.5))

            zona_key = random.choice(list(self.zonas.keys()))
            ancho, alto = self.zonas[zona_key]
            ox, oy = self.zona_offsets[zona_key]

            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)

            # 20% verdes, 80% blancos
            if random.random() < 0.2:
                virus_color = 'green'
            else:
                virus_color = 'white'

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
        """
        Detiene este hilo que genera virus.
        """
        self._stop_event.set()
