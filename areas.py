# areas.py
import threading
import time

class AreaThread(threading.Thread):
    def __init__(self, zonas, result_dict):
        """
        :param zonas: dict con dimensiones de cada zona
        :param result_dict: dict para guardar el resultado de las áreas
        """
        super().__init__()
        self.zonas = zonas
        self.result_dict = result_dict
        self._stop_event = threading.Event()

    def run(self):
        """
        Cálculo de áreas concurrente. Por ejemplo, en un bucle
        para recalcular cada cierto tiempo, o una sola vez.
        """
        # Supongamos que calculamos solo una vez al inicio
        # y luego dormimos en bucle, por ejemplo
        self.calcular_areas()
        while not self._stop_event.is_set():
            # Podrías volver a calcular si cambian las dimensiones, etc.
            time.sleep(1.0)

    def calcular_areas(self):
        total = 0
        for nombre, (largo, ancho) in self.zonas.items():
            area = largo * ancho
            total += area
        self.result_dict["superficie_total"] = total
        print(f"[AreaThread] Superficie total calculada: {total}")

    def stop(self):
        self._stop_event.set()
