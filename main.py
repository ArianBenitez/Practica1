# main.py
import threading
import roomba
import areas
import spawn_mites
import time

def main():
    """
    - Lanza hilos de:
       1) Cálculo de áreas
       2) Roomba (lógica de movimiento)
       3) Aparición de ácaros (mites)
    - Corre el bucle de Pygame en el hilo principal.
    """
    # 1) Crear contenedores de datos compartidos
    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }
    areas_result = {}  # dict para guardar resultado del cálculo de áreas

    shared_mites = []  # lista compartida de ácaros
    shared_mites_lock = threading.Lock()  # para sincronizar acceso a la lista

    # 2) Crear los hilos
    area_thread = areas.AreaThread(zonas, areas_result)
    roomba_thread = roomba.RoombaThread()
    mites_thread = spawn_mites.MitesThread(shared_mites, shared_mites_lock)

    # 3) Iniciar los hilos
    area_thread.start()
    roomba_thread.start()
    mites_thread.start()

    # 4) Correr Pygame en este mismo hilo principal
    #    (Suponiendo que tienes una función run_game que use shared_mites)
    import game  # si deseas separar la lógica del juego
    game.run_game(shared_mites, shared_mites_lock)

    # 5) Una vez sales del juego, puedes indicar a los hilos que paren
    area_thread.stop()
    roomba_thread.stop()
    mites_thread.stop()

    # 6) Esperar a que finalicen
    area_thread.join()
    roomba_thread.join()
    mites_thread.join()

    print("Todos los hilos han finalizado. Saliendo del programa.")

if __name__ == "__main__":
    main()
