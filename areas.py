import threading
import time

# Tasa de limpieza hipotética en cm²/segundo (para el laboratorio de virus)
CLEANING_RATE = 200.0

class AreaThread(threading.Thread):
    """
    Hilo que calcula la superficie total del 'Laboratorio de Virus' 
    y estima el tiempo teórico de limpieza. Representa la parte de 
    investigación que cuantifica el tamaño de las zonas a desinfectar.
    """
    def __init__(self, zonas, result_dict):
        """
        :param zonas: dict con {'Zona 1': (ancho, alto), ...}
        :param result_dict: dict compartido para guardar resultados (áreas, tiempo)
        """
        super().__init__()
        self.zonas = zonas
        self.result_dict = result_dict
        self._stop_event = threading.Event()

    def run(self):
        """
        1) Calcula la superficie total de las zonas contaminadas.
        2) Estima el tiempo de limpieza teórico (segundos y minutos).
        3) Almacena esos valores en result_dict para que el nanobot 
           (en roomba.py) y la interfaz (game.py) puedan mostrarlos.
        """
        print("[AreaThread] Iniciando cálculo de la superficie del laboratorio contaminado...")
        self.calcular_areas()
        self.estimar_tiempo_limpieza()

        # Mantener vivo el hilo, por si se requiere recalcular
        while not self._stop_event.is_set():
            time.sleep(2)

    def calcular_areas(self):
        """
        Suma ancho*alto de cada zona y lo guarda en result_dict['superficie_total'].
        """
        total = 0
        for nombre_zona, (ancho, alto) in self.zonas.items():
            total += ancho * alto
        self.result_dict['superficie_total'] = total
        print(f"[AreaThread] Superficie total del laboratorio: {total} cm²")

    def estimar_tiempo_limpieza(self):
        """
        Con la superficie total calculada, estima el tiempo en segundos y minutos,
        asumiendo CLEANING_RATE cm²/s. Sirve como referencia teórica para 
        la desinfección que el nanobot realiza.
        """
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
        """
        Detiene este hilo de cálculo.
        """
        self._stop_event.set()
