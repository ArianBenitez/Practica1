# spawn_mites.py
import threading
import random
import time

class MitesThread(threading.Thread):
    def __init__(self, shared_mites_list, lock):
        """
        :param shared_mites_list: lista compartida donde se añaden los ácaros
        :param lock: lock para sincronizar acceso a la lista
        """
        super().__init__()
        self.shared_mites = shared_mites_list
        self.lock = lock
        self._stop_event = threading.Event()

    def run(self):
        """
        Genera ácaros de forma aleatoria cada cierto tiempo
        hasta que se pida detener el hilo.
        """
        while not self._stop_event.is_set():
            time.sleep(random.uniform(1.0, 3.0))  # cada 1-3 segundos
            new_mite = {
                "x": random.randint(0, 600),
                "y": random.randint(0, 700),
                "active": True
            }
            with self.lock:
                self.shared_mites.append(new_mite)
            print(f"[MitesThread] Aparece un nuevo ácaro en {new_mite['x']}, {new_mite['y']}")

    def stop(self):
        self._stop_event.set()
