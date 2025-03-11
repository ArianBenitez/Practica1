# areas.py
import threading
import time

class AreaThread(threading.Thread):
    def __init__(self, zonas, result_dict):
        super().__init__()
        self.zonas = zonas
        self.result_dict = result_dict
        self._stop_event = threading.Event()

    def run(self):
        # Calcula las áreas una vez
        self.calcular_areas()
        # En un bucle por si quieres recalcular o mantener vivo el hilo
        while not self._stop_event.is_set():
            time.sleep(2)

    def calcular_areas(self):
        total = 0
        for _, (ancho, alto) in self.zonas.items():
            total += ancho * alto
        self.result_dict['superficie_total'] = total
        print(f"[AreaThread] Superficie total: {total}")

    def stop(self):
        self._stop_event.set()
