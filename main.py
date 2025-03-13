import threading
import areas
import roomba
import spawn_mites
import spawn_enemies
import game
import radiation

def main():
    """
    Pregunta al usuario si desea control manual (M) o automático (A).
    Lanza hilos:
      - Área (AreaThread)
      - Robot (RoombaThread)
      - Virus (MitesThread)
      - Enemigos (EnemiesThread)
      - Radiación (RadiationThread)
    Y corre el juego en el hilo principal (game.run_game).
    """

    modo = input("¿Deseas control manual (M) o automático (A)? [M/A]: ").strip().lower()
    if modo == 'm':
        control_mode = 'manual'
    else:
        control_mode = 'auto'

    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }

    areas_result = {}

    # Robot dentro de Zona 1
    roomba_state = {
        'x': 200,
        'y': 180,
        'radius': 10,
        'stop': False,
        'clean_time': None,
        'vidas': 3,
        'score': 0,
        'control_mode': control_mode
    }

    # Radiación
    radiation_state = {
        'radiacion': 0,
        'game_over': False
    }

    # Virus
    shared_mites = []
    shared_mites_lock = threading.Lock()

    # Enemigos
    shared_enemies = []
    shared_enemies_lock = threading.Lock()

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

    # Correr juego
    game.run_game(
        zonas,
        areas_result,
        roomba_state,
        shared_mites, shared_mites_lock,
        shared_enemies, shared_enemies_lock,
        radiation_state
    )

    # Parar hilos
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

    print("Todos los hilos finalizados. Saliendo...")

if __name__ == "__main__":
    main()
