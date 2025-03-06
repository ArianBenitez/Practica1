# game.py
import pygame
import time

def run_game(shared_mites, lock):
    """
    Corre el bucle principal de Pygame. 
    Recibe la lista de ácaros compartida y un lock para leerla de forma segura.
    """
    pygame.init()
    screen = pygame.display.set_mode((600, 700))
    pygame.display.set_caption("RoomBA Espacial")
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(30)  # 30 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Lógica del juego: por ejemplo, dibujar ácaros
        screen.fill((30,30,30))

        with lock:
            for mite in shared_mites:
                if mite["active"]:
                    # dibujar un puntito blanco
                    pygame.draw.circle(screen, (255,255,255), (mite["x"], mite["y"]), 3)

        # (Podrías también leer la posición de la roomba si fuera compartida en roomba_thread)
        # ...

        pygame.display.flip()

    pygame.quit()
