import threading
import time

# Tasa de limpieza hipotética en cm²/segundo (para el laboratorio de virus)
CLEANING_RATE = 200.0

class AreaThread(threading.Thread):
    def __init__(self, zonas, result_dict, game_state):
        """
        :param zonas: dict con {'Zona 1': (ancho, alto), ...}
        :param result_dict: dict compartido para guardar resultados
        :param game_state: diccionario compartido (ej. roomba_state) que incluye 'game_over'
        """
        super().__init__()
        self.zonas = zonas
        self.result_dict = result_dict
        self.game_state = game_state
        self._stop_event = threading.Event()

    def run(self):
        print("[AreaThread] Iniciando cálculo de la superficie del laboratorio contaminado...")
        self.calcular_areas()
        self.estimar_tiempo_limpieza()

        # Bucle de espera: si se activa game_over, se sale inmediatamente
        while not self._stop_event.is_set():
            if self.game_state.get('game_over', False):
                break
            time.sleep(2)

    def calcular_areas(self):
        total = 0
        for nombre_zona, (ancho, alto) in self.zonas.items():
            total += ancho * alto
        self.result_dict['superficie_total'] = total
        print(f"[AreaThread] Superficie total del laboratorio: {total} cm²")

    def estimar_tiempo_limpieza(self):
        total_area = self.result_dict.get('superficie_total', 0)
        if total_area > 0:
            time_seconds = total_area / CLEANING_RATE
            time_minutes = time_seconds / 60.0
            self.result_dict['tiempo_est_s'] = time_seconds
            self.result_dict['tiempo_est_m'] = time_minutes
            print(f"[AreaThread] Tiempo teórico de desinfección: {time_seconds:.2f} s ({time_minutes:.2f} min)")
        else:
            self.result_dict['tiempo_est_s'] = 0
            self.result_dict['tiempo_est_m'] = 0
            print("[AreaThread] No hay zonas contaminadas que limpiar.")

    def stop(self):
        self._stop_event.set()
