# areas.py
import threading
import time

# Tasa de limpieza hipotética en cm²/segundo
CLEANING_RATE = 200.0

class AreaThread(threading.Thread):
    def __init__(self, zonas, result_dict):
        super().__init__()
        self.zonas = zonas
        self.result_dict = result_dict
        self._stop_event = threading.Event()

    def run(self):
        """
        Hilo que:
          1) Calcula la superficie total de las zonas.
          2) Estima el tiempo de limpieza teórico (segundos y minutos).
          3) Almacena esos valores en result_dict para que otros módulos los usen.
        """
        # 1) Calcular áreas
        self.calcular_areas()
        # 2) Estimar el tiempo
        self.estimar_tiempo_limpieza()

        # Mantener vivo el hilo, por si queremos recalcular o quedarnos escuchando
        while not self._stop_event.is_set():
            time.sleep(2)

    def calcular_areas(self):
        """
        Suma el ancho*alto de cada zona y lo guarda en result_dict['superficie_total'].
        """
        total = 0
        for _, (ancho, alto) in self.zonas.items():
            total += ancho * alto
        self.result_dict['superficie_total'] = total
        print(f"[AreaThread] Superficie total: {total} cm²")

    def estimar_tiempo_limpieza(self):
        """
        Con la superficie total calculada, estima el tiempo en segundos y minutos,
        asumiendo una tasa de limpieza (CLEANING_RATE) en cm²/s.
        Guarda los resultados en result_dict.
        """
        total_area = self.result_dict.get('superficie_total', 0)
        CLEANING_RATE = 200.0  # cm²/seg, por ejemplo
        if total_area > 0:
            time_seconds = total_area / CLEANING_RATE
            time_minutes = time_seconds / 60.0
            self.result_dict['tiempo_est_s'] = time_seconds
            self.result_dict['tiempo_est_m'] = time_minutes
            print(f"[AreaThread] Tiempo estimado: {time_seconds:.2f} s ({time_minutes:.2f} min)")
        else:
            self.result_dict['tiempo_est_s'] = 0
            self.result_dict['tiempo_est_m'] = 0
            print("[AreaThread] No hay superficie para limpiar.")


    def stop(self):
        """
        Permite detener el hilo desde fuera (main.py).
        """
        self._stop_event.set()
