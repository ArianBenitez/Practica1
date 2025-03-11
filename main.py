# main.py
import threading
import areas
import roomba
import spawn_mites
import game

def main():
    """
    Lanza hilos para:
      - Cálculo de áreas (AreaThread)
      - Lógica del robot con BFS (RoombaThread)
      - Aparición concurrente de ácaros (MitesThread)
    Y corre Pygame en el hilo principal para dibujar
    las zonas, el hueco, el robot y los ácaros desde el inicio.
    """

    # Zonas con sus dimensiones
    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }

    # Diccionario para guardar la superficie total calculada
    areas_result = {}

    # Estado del robot (posición, radio, etc.)
    # Agregamos un campo 'clean_time' inicializado a None
    roomba_state = {
        'x': 100,    # Posición inicial del robot
        'y': 100,
        'radius': 10,
        'stop': False,
        'clean_time': None  # Guardaremos aquí el tiempo de limpieza final
    }

    # Lista de ácaros compartida
    shared_mites = []
    shared_mites_lock = threading.Lock()

    # Crear hilos
    area_thread = areas.AreaThread(zonas, areas_result)
    roomba_thread = roomba.RoombaThread(roomba_state, shared_mites, shared_mites_lock)
    # Este hilo generará ácaros indefinidamente (o hasta que lo detengas)
    mites_thread = spawn_mites.MitesThread(zonas, shared_mites, shared_mites_lock)

    # Iniciar hilos
    area_thread.start()
    roomba_thread.start()
    mites_thread.start()

    # Correr el juego en el hilo principal
    game.run_game(zonas, areas_result, roomba_state, shared_mites, shared_mites_lock)

    # Al salir del juego, detener los hilos
    area_thread.stop()
    roomba_thread.stop()
    mites_thread.stop()

    # Esperar a que finalicen
    area_thread.join()
    roomba_thread.join()
    mites_thread.join()

    print("Todos los hilos finalizados. Saliendo...")

if __name__ == "__main__":
    main()
