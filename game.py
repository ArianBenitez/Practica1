# game.py
import pygame

HUECO_RECT = (151, 180, 89, 260)

def run_game(zonas, areas_result, roomba_state, shared_mites, shared_mites_lock):
    pygame.init()
    screen = pygame.display.set_mode((600, 700))
    pygame.display.set_caption("Robot Aspirador - RoomBA Espacial")
    clock = pygame.time.Clock()

    fuente = pygame.font.SysFont(None, 24)

    # Offsets de cada zona
    zona_offsets = {
        'Zona 1': (50, 30),
        'Zona 2': (50, 180),
        'Zona 3': (240, 180),
        'Zona 4': (151, 440),
    }

    running = True
    while running:
        dt = clock.tick(30)  # 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))

        # 1) Dibujar zonas
        for nombre_zona, (ancho, alto) in zonas.items():
            ox, oy = zona_offsets[nombre_zona]
            pygame.draw.rect(
                screen,
                (100, 100, 200),
                (ox, oy, ancho, alto),
                width=2
            )

        # 2) Dibujar hueco
        pygame.draw.rect(screen, (200, 50, 50), HUECO_RECT, width=0)

        # 3) Dibujar robot
        rx = roomba_state['x']
        ry = roomba_state['y']
        rradius = roomba_state['radius']
        pygame.draw.circle(screen, (255, 255, 0), (int(rx), int(ry)), rradius)

        # 4) Dibujar ácaros
        with shared_mites_lock:
            for mite in shared_mites:
                if mite.get('active', True):
                    pygame.draw.circle(screen, (255, 255, 255), (mite['x'], mite['y']), 3)

        # 5) Mostrar superficie total
        sup_total = areas_result.get('superficie_total', 0)
        texto_area = f"Superficie: {sup_total} cm²"
        render_texto_area = fuente.render(texto_area, True, (255, 255, 255))
        screen.blit(render_texto_area, (10, 10))

        # 6) Mostrar tiempo estimado
        tiempo_est_s = areas_result.get('tiempo_est_s', None)
        tiempo_est_m = areas_result.get('tiempo_est_m', None)
        if tiempo_est_s is not None and tiempo_est_m is not None:
            texto_tiempo = f"Tiempo teórico: {tiempo_est_s:.2f} s ({tiempo_est_m:.2f} min)"
            render_texto_tiempo = fuente.render(texto_tiempo, True, (255, 255, 255))
            screen.blit(render_texto_tiempo, (300, 10))

        pygame.display.flip()

    pygame.quit()
