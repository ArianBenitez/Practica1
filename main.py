import threading
import areas
import roomba
import spawn_mites
import spawn_enemies
import game
import radiation

def main():
    modo = input("¿Deseas control manual (M) o automático (A)? [M/A]: ").strip().lower()
    control_mode = 'manual' if modo == 'm' else 'auto'

    # Zonas definidas
    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }

    areas_result = {}

    # Estado compartido (se usa como game_state)
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

    radiation_state = {
        'radiacion': 0,
        'game_over': False
    }

    shared_mites = []
    shared_mites_lock = threading.Lock()

    shared_enemies = []
    shared_enemies_lock = threading.Lock()

    # Creación de hilos (se pasa roomba_state como game_state a los hilos que lo requieren)
    area_thread = areas.AreaThread(zonas, areas_result, roomba_state)
    roomba_thread = roomba.RoombaThread(roomba_state, shared_mites, shared_mites_lock, shared_enemies, shared_enemies_lock, radiation_state)
    mites_thread = spawn_mites.MitesThread(zonas, shared_mites, shared_mites_lock, roomba_state)
    enemies_thread = spawn_enemies.EnemiesThread(zonas, shared_enemies, shared_enemies_lock, roomba_state)
    radiation_thread = radiation.RadiationThread(radiation_state)

    # Iniciar hilos
    area_thread.start()
    roomba_thread.start()
    mites_thread.start()
    enemies_thread.start()
    radiation_thread.start()

    # Ejecutar el juego (ventana, sprites, HUD, game over, botón reiniciar)
    game.run_game(zonas, areas_result, roomba_state, shared_mites, shared_mites_lock, shared_enemies, shared_enemies_lock, radiation_state)

    # Una vez que se cierra la ventana, detener y esperar a que terminen todos los hilos
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

    print("Todos los hilos se han detenido. Saliendo...")

if __name__ == "__main__":
    main()
