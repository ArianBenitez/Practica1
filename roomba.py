# roomba.py
import threading
import time

class RoombaThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        # Aquí podrías recibir parámetros, como la posición inicial, etc.
        self.pos_x = 100
        self.pos_y = 100

    def run(self):
        """
        Lógica de la Roomba (robot). 
        Por ejemplo, moverse de forma autónoma en un bucle infinito hasta stop().
        """
        while not self._stop_event.is_set():
            # Actualizar posición
            self.pos_x += 1
            # Lógica de colisiones, pathfinding, etc.

            # Esperar un poco para no saturar la CPU
            time.sleep(0.01)

    def stop(self):
        self._stop_event.set()
