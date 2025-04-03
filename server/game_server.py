import pygame
import os, sys

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

# Dimensiones y posición del hueco radiactivo
HUECO_RECT = (151, 280, 89, 260)
# Barrera que engloba las zonas
BARRERA = (50, 130, 550, 760)

def run_game(
    zonas,
    areas_result,
    roomba_state,
    shared_mites, mites_lock,
    shared_enemies, enemies_lock,
    radiation_state=None
):
    """
    Bucle principal de Pygame:
    - Dibuja el 'Laboratorio de Virus' con sus zonas.
    - Muestra el hueco radiactivo con una imagen de espacio.
    - Representa al nanobot y a los enemigos con sprites.
    - Control manual (flechas) o automático (BFS) en roomba.py.
    - Pantalla de Game Over y botón para reiniciar.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Laboratorio de Virus - Limpieza en Progreso")
    clock = pygame.time.Clock()

    fuente = pygame.font.SysFont(None, 24)

    # ========== CARGA DE SPRITES ==========
    # Robot
    robot_sprite = pygame.image.load("GreenRobotSprite.png").convert_alpha()
    robot_sprite = pygame.transform.scale(robot_sprite, (100, 64))

    # Hueco (espacio)
    hueco_image = pygame.image.load("Space1.png").convert_alpha()
    hueco_image = pygame.transform.scale(hueco_image, (HUECO_RECT[2], HUECO_RECT[3]))  

    # Enemigos (virus rojos)
    enemy_sprite = pygame.image.load("VirusRojo.png").convert_alpha()
    enemy_sprite = pygame.transform.scale(enemy_sprite, (48, 48))  

    zona_offsets = {
        'Zona 1': (50, 130),
        'Zona 2': (50, 280),
        'Zona 3': (240, 280),
        'Zona 4': (151, 540),
    }

    control_mode = roomba_state.get('control_mode', 'auto')
    print(f"[Game] Modo de control: {control_mode}")

    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Si estamos en Game Over, checar clic en botón Reiniciar
            if roomba_state.get('game_over', False):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if 190 <= mouse_x <= 390 and 400 <= mouse_y <= 450:
                        restart_program()

        # Pantalla de Game Over si sin vidas
        if roomba_state.get('game_over', False) or roomba_state['vidas'] <= 0:
            screen.fill((211, 211, 211))  # gris claro
            game_over_text = fuente.render("¡GAME OVER! Te has quedado sin vidas.", True, (255, 0, 0))
            screen.blit(game_over_text, (150, 300))

            boton_rect = pygame.Rect(190, 400, 200, 50)
            pygame.draw.rect(screen, (0, 0, 255), boton_rect)
            texto_btn = fuente.render("Reiniciar", True, (255, 255, 255))
            screen.blit(texto_btn, (boton_rect.x + 60, boton_rect.y + 15))

            pygame.display.flip()
            continue

        # =========================
        # CONTROL MANUAL
        # =========================
        if control_mode == 'manual':
            keys = pygame.key.get_pressed()
            step = 2
            new_x = roomba_state['x']
            new_y = roomba_state['y']

            if keys[pygame.K_LEFT]:
                new_x -= step
            if keys[pygame.K_RIGHT]:
                new_x += step
            if keys[pygame.K_UP]:
                new_y -= step
            if keys[pygame.K_DOWN]:
                new_y += step

            if in_barrera(new_x, new_y, roomba_state['radius']):
                if not in_hueco(new_x, new_y, roomba_state['radius']):
                    roomba_state['x'] = new_x
                    roomba_state['y'] = new_y

            # Colisiones en modo manual
            check_virus_collisions(roomba_state, shared_mites, mites_lock, radiation_state)
            check_enemy_collisions(roomba_state, shared_enemies, enemies_lock)

        # ========== DIBUJAR ESCENA ==========
        screen.fill((211, 211, 211))  # Gris claro

        # Zonas
        for nombre_zona, (ancho, alto) in zonas.items():
            ox, oy = zona_offsets[nombre_zona]
            pygame.draw.rect(screen, (100, 100, 200), (ox, oy, ancho, alto), width=2)

        # Hueco => Space.png
        hx, hy, hw, hh = HUECO_RECT
        screen.blit(hueco_image, (hx, hy))

        # Robot => GreenRobotSprite.png
        rx = roomba_state.get('x', 0)
        ry = roomba_state.get('y', 0)
        sprite_w = robot_sprite.get_width()
        sprite_h = robot_sprite.get_height()
        robot_pos = (rx - sprite_w//2, ry - sprite_h//2)
        screen.blit(robot_sprite, robot_pos)

        # Virus (motas)
        with mites_lock:
            for virus in shared_mites:
                if virus.get('active', True):
                    color = (0,200,0) if virus.get('color') == 'green' else (0,0,255)
                    pygame.draw.circle(screen, color, (virus['x'], virus['y']), 3)

        # Enemigos => VirusRojo.png
        with enemies_lock:
            for enemy in shared_enemies:
                if enemy.get('active', True):
                    ex, ey = enemy['x'], enemy['y']
                    ew, eh = enemy_sprite.get_width(), enemy_sprite.get_height()
                    screen.blit(enemy_sprite, (ex - ew//2, ey - eh//2))

        # ========== HUD ==========
        sup_total = areas_result.get('superficie_total', 0)
        texto_area = f"Superficie: {sup_total} cm²"
        render_texto_area = fuente.render(texto_area, True, (0, 0, 0))
        screen.blit(render_texto_area, (10, 10))

        tiempo_est_s = areas_result.get('tiempo_est_s', None)
        tiempo_est_m = areas_result.get('tiempo_est_m', None)
        if tiempo_est_s is not None and tiempo_est_m is not None:
            texto_tiempo = f"Tiempo teórico: {tiempo_est_s:.2f} s ({tiempo_est_m:.2f} min)"
            render_texto_tiempo = fuente.render(texto_tiempo, True, (0, 0, 0))
            screen.blit(render_texto_tiempo, (10, 30))

        vidas = roomba_state.get('vidas', None)
        if vidas is not None:
            texto_vidas = f"Vidas: {vidas}"
            render_texto_vidas = fuente.render(texto_vidas, True, (0, 0, 0))
            screen.blit(render_texto_vidas, (10, 50))

        score = roomba_state.get('score', None)
        if score is not None:
            texto_score = f"Puntuación: {score}"
            render_texto_score = fuente.render(texto_score, True, (0, 0, 0))
            screen.blit(render_texto_score, (10, 70))

        clean_time = roomba_state.get('clean_time', None)
        if clean_time is not None:
            texto_clean = f"Tiempo real de limpieza: {clean_time:.2f} s"
            render_texto_clean = fuente.render(texto_clean, True, (0, 0, 0))
            screen.blit(render_texto_clean, (10, 90))

        if radiation_state is not None:
            rad_level = radiation_state.get('radiacion', 0)
            texto_rad = f"Radiación: {rad_level:.0f}%"
            render_texto_rad = fuente.render(texto_rad, True, (255, 0, 0))
            screen.blit(render_texto_rad, (400, 10))

            if radiation_state.get('game_over', False):
                msg_go = "¡Radiación Crítica! Game Over."
                render_msg_go = fuente.render(msg_go, True, (255, 0, 0))
                screen.blit(render_msg_go, (200, 350))

        pygame.display.flip()

    pygame.quit()

# --------------------- FUNCIONES AUX ---------------------
def restart_program():
    """
    Permite reiniciar todo el juego al hacer clic en 'Reiniciar'.
    """
    os.execv(sys.executable, [sys.executable] + sys.argv)

def in_barrera(x, y, r):
    """
    Verifica si (x,y) con radio r está dentro de la barrera 
    que engloba las zonas del laboratorio.
    """
    min_x, min_y, max_x, max_y = BARRERA
    return (x - r >= min_x and
            x + r <  max_x and
            y - r >= min_y and
            y + r <  max_y)

def in_hueco(x, y, r):
    """
    Checa si (x,y) con radio r colisiona con el hueco radiactivo central.
    """
    hx, hy, hw, hh = HUECO_RECT
    closest_x = max(hx, min(x, hx+hw))
    closest_y = max(hy, min(y, hy+hh))
    dist_x = x - closest_x
    dist_y = y - closest_y
    dist_sq = dist_x**2 + dist_y**2
    return dist_sq < (r*r)

def check_virus_collisions(roomba_state, shared_mites, lock, radiation_state):
    """
    Si el robot está cerca de un virus (blanco o verde), lo absorbe. 
    Si es verde, reduce radiación.
    """
    rx = roomba_state['x']
    ry = roomba_state['y']
    rradius = roomba_state['radius']

    with lock:
        for virus in shared_mites:
            if virus.get('active', True):
                dx = virus['x'] - rx
                dy = virus['y'] - ry
                dist_sq = dx*dx + dy*dy
                if dist_sq < (rradius + 3)**2:
                    virus['active'] = False
                    if 'score' in roomba_state:
                        roomba_state['score'] += 10
                    if radiation_state and virus.get('color') == 'green':
                        reduce_radiation_10_percent(radiation_state)

def check_enemy_collisions(roomba_state, shared_enemies, lock):
    """
    Resta 1 vida si el robot colisiona con un enemigo rojo.
    """
    rx = roomba_state['x']
    ry = roomba_state['y']
    rradius = roomba_state['radius']

    with lock:
        for enemy in shared_enemies:
            if enemy.get('active', True):
                dx = enemy['x'] - rx
                dy = enemy['y'] - ry
                dist_sq = dx*dx + dy*dy
                if dist_sq < (rradius + 10)**2:
                    enemy['active'] = False
                    roomba_state['vidas'] -= 1
                    print("[Game] ¡Colisión con enemigo! Vidas restantes:", roomba_state['vidas'])
                    if roomba_state['vidas'] <= 0:
                        roomba_state['vidas'] = 0
                        roomba_state['game_over'] = True
                        print("[Game] El robot se quedó sin vidas. Game Over.")

def reduce_radiation_10_percent(radiation_state):
    """
    Reduce en un 10% la radiación total, 
    como si el virus verde generara un 'antídoto' temporal.
    """
    rad_level = radiation_state.get('radiacion', 0)
    new_level = rad_level * 0.9
    radiation_state['radiacion'] = max(0, new_level)
