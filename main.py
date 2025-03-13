import threading
import areas
import roomba
import spawn_mites
import game
import radiation

def main():
    # Zonas desplazadas +100 px en Y
    zonas = {
        'Zona 1': (500, 150),  # offset: (50,130)
        'Zona 2': (101, 480),  # offset: (50,280)
        'Zona 3': (309, 480),  # offset: (240,280)
        'Zona 4': (90, 220),   # offset: (151,540)
    }

    areas_result = {}

    # Robot dentro de la Zona 1, en (200,180) => [50..549], [130..279]
    roomba_state = {
        'x': 200,
        'y': 180,
        'radius': 10,
        'stop': False,
        'clean_time': None,
        'vidas': 3,
        'score': 0
    }

    # Radiación inicial
    radiation_state = {
        'radiacion': 0,
        'game_over': False
    }

    # Lista de virus compartida
    shared_mites = []
    shared_mites_lock = threading.Lock()

    # Hilos
    area_thread = areas.AreaThread(zonas, areas_result)
    roomba_thread = roomba.RoombaThread(roomba_state, shared_mites, shared_mites_lock, radiation_state)
    mites_thread = spawn_mites.MitesThread(zonas, shared_mites, shared_mites_lock)
    radiation_thread = radiation.RadiationThread(radiation_state)  # sube radiacion lento

    # Iniciar
    area_thread.start()
    roomba_thread.start()
    mites_thread.start()
    radiation_thread.start()

    # Correr juego
    game.run_game(
        zonas,
        areas_result,
        roomba_state,
        shared_mites,
        shared_mites_lock,
        radiation_state
    )

    # Parar
    area_thread.stop()
    roomba_thread.stop()
    mites_thread.stop()
    radiation_thread.stop()

    area_thread.join()
    roomba_thread.join()
    mites_thread.join()
    radiation_thread.join()

    print("Todos los hilos finalizados. Saliendo...")

if __name__ == "__main__":
    main()
