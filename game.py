# game.py
import pygame

HUECO_RECT = (151, 380, 89, 160)

def run_game(zonas, areas_result, roomba_state, shared_mites, shared_mites_lock, radiation_state=None):
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Laboratorio de Virus - Limpieza en Progreso")
    clock = pygame.time.Clock()

    fuente = pygame.font.SysFont(None, 24)

    zona_offsets = {
        'Zona 1': (50, 130),
        'Zona 2': (50, 280),
        'Zona 3': (240, 280),
        'Zona 4': (151, 540),
    }

    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))

        # Zonas
        for nombre_zona, (ancho, alto) in zonas.items():
            ox, oy = zona_offsets[nombre_zona]
            pygame.draw.rect(
                screen,
                (100, 100, 200),
                (ox, oy, ancho, alto),
                width=2
            )

        # Hueco
        pygame.draw.rect(screen, (200, 50, 50), HUECO_RECT, width=0)

        # Robot
        rx = roomba_state.get('x', 0)
        ry = roomba_state.get('y', 0)
        rradius = roomba_state.get('radius', 10)
        pygame.draw.circle(screen, (255, 255, 0), (int(rx), int(ry)), rradius)

        # Virus
        with shared_mites_lock:
            for virus in shared_mites:
                if virus.get('active', True):
                    color = (0,255,0) if virus.get('color') == 'green' else (255,255,255)
                    pygame.draw.circle(screen, color, (virus['x'], virus['y']), 3)

        # HUD
        sup_total = areas_result.get('superficie_total', 0)
        texto_area = f"Superficie: {sup_total} cm²"
        render_texto_area = fuente.render(texto_area, True, (255, 255, 255))
        screen.blit(render_texto_area, (10, 10))

        tiempo_est_s = areas_result.get('tiempo_est_s', None)
        tiempo_est_m = areas_result.get('tiempo_est_m', None)
        if tiempo_est_s is not None and tiempo_est_m is not None:
            texto_tiempo = f"Tiempo teórico: {tiempo_est_s:.2f} s ({tiempo_est_m:.2f} min)"
            render_texto_tiempo = fuente.render(texto_tiempo, True, (255, 255, 255))
            screen.blit(render_texto_tiempo, (10, 30))

        vidas = roomba_state.get('vidas', None)
        if vidas is not None:
            texto_vidas = f"Vidas: {vidas}"
            render_texto_vidas = fuente.render(texto_vidas, True, (255, 255, 255))
            screen.blit(render_texto_vidas, (10, 50))

        score = roomba_state.get('score', None)
        if score is not None:
            texto_score = f"Puntuación: {score}"
            render_texto_score = fuente.render(texto_score, True, (255, 255, 255))
            screen.blit(render_texto_score, (10, 70))

        clean_time = roomba_state.get('clean_time', None)
        if clean_time is not None:
            texto_clean = f"Tiempo real de limpieza: {clean_time:.2f} s"
            render_texto_clean = fuente.render(texto_clean, True, (255, 255, 255))
            screen.blit(render_texto_clean, (10, 90))

        if radiation_state is not None:
            rad_level = radiation_state.get('radiacion', 0)
            texto_rad = f"Radiación: {rad_level:.0f}%"
            render_texto_rad = fuente.render(texto_rad, True, (255, 100, 100))
            screen.blit(render_texto_rad, (400, 10))

            if radiation_state.get('game_over', False):
                msg_go = "¡Radiación Crítica! Game Over."
                render_msg_go = fuente.render(msg_go, True, (255, 50, 50))
                screen.blit(render_msg_go, (200, 350))

        pygame.display.flip()

    pygame.quit()
