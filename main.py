import threading
import areas
import roomba
import spawn_mites
import spawn_enemies
import game
import radiation

def main():
    """
    Función principal que lanza los hilos y el juego. 

    Historia:
    En este 'Laboratorio de Virus', el nanobot (robot aspirador) 
    deberá desinfectar las zonas, mientras que la radiación sube 
    lentamente y los enemigos (virus rojos) intentan dañarlo. 
    El usuario puede elegir controlar manualmente al robot 
    o dejarlo actuar automáticamente con BFS.
    """
    modo = input("¿Deseas control manual (M) o automático (A)? [M/A]: ").strip().lower()
    if modo == 'm':
        control_mode = 'manual'
    else:
        control_mode = 'auto'

    # Zonas del laboratorio
    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }

    # Diccionario para almacenar resultados de áreas y tiempos
    areas_result = {}

    # Estado del robot (nanobot), incluyendo sus vidas y modo de control
    roomba_state = {
        'x': 200,
        'y': 180,
        'radius': 10,
        'stop': False,
        'clean_time': None,
        'vidas': 3,
        'score': 0,
        'control_mode': control_mode,
        'game_over': False
    }

    # Estado de la radiación en el laboratorio
    radiation_state = {
        'radiacion': 0,
        'game_over': False
    }

    # Listas compartidas (virus blancos/verdes y enemigos rojos)
    shared_mites = []
    shared_mites_lock = threading.Lock()

    shared_enemies = []
    shared_enemies_lock = threading.Lock()

    # Hilos concurrentes
    area_thread = areas.AreaThread(zonas, areas_result)
    roomba_thread = roomba.RoombaThread(
        roomba_state,
        shared_mites, shared_mites_lock,
        shared_enemies, shared_enemies_lock,
        radiation_state
    )
    mites_thread = spawn_mites.MitesThread(zonas, shared_mites, shared_mites_lock)
    enemies_thread = spawn_enemies.EnemiesThread(zonas, shared_enemies, shared_enemies_lock)
    radiation_thread = radiation.RadiationThread(radiation_state)

    # Iniciar hilos
    area_thread.start()
    roomba_thread.start()
    mites_thread.start()
    enemies_thread.start()
    radiation_thread.start()

    # Correr el juego en el hilo principal (interfaz Pygame)
    game.run_game(
        zonas,
        areas_result,
        roomba_state,
        shared_mites, shared_mites_lock,
        shared_enemies, shared_enemies_lock,
        radiation_state
    )

    # Detener hilos al salir
    area_thread.stop()
    roomba_thread.stop()
    mites_thread.stop()
    enemies_thread.stop()
    radiation_thread.stop()

    area_thread.join()
    roomba_thread.join()
    mites_thread.join()
    enemies_thread.join()
    radiation_thread.join()

    print("Todos los hilos han finalizado. Saliendo...")

if __name__ == "__main__":
    main()
