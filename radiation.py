import threading
import time

class RadiationThread(threading.Thread):
    def __init__(self, state_dict):
        super().__init__()
        self.state_dict = state_dict
        self._stop_event = threading.Event()

        self.MAX_RADIATION = 100
        self._lock = threading.Lock()

    def run(self):
        print("[RadiationThread] Subida de radiación lenta (1 punto cada 3s).")
        while not self._stop_event.is_set():
            time.sleep(3)
            with self._lock:
                rad = self.state_dict.get('radiacion', 0)
                rad += 1
                if rad >= self.MAX_RADIATION:
                    rad = self.MAX_RADIATION
                    self.state_dict['game_over'] = True
                    print("[RadiationThread] ¡Radiación crítica! Game Over.")
                self.state_dict['radiacion'] = rad

    def stop(self):
        self._stop_event.set()
