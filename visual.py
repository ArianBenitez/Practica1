import pygame
import random
import os
import sys

# ============== CONFIGURACIÓN ==============
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

# Hueco NO transitable (x, y, w, h)
HUECO_RECT = (151, 180, 89, 260)

# Colores
COLOR_FONDO   = (30, 30, 30)
COLOR_ZONA    = (100, 100, 200)
COLOR_ROOMBA  = (255, 255, 0)
COLOR_MOTA    = (255, 255, 255)
COLOR_ENEMIGO = (255, 50, 50)
COLOR_SOMBRA  = (20, 20, 20)
COLOR_TEXTO   = (180, 255, 180)

# Zonas para dibujar y generar motas
zona_offsets = {
    'Zona 1': (50, 30),    # Ancho=500, Alto=150
    'Zona 2': (50, 180),   # Ancho=480, Alto=101
    'Zona 3': (240, 180),  # Ancho=309, Alto=480
    'Zona 4': (151, 440),  # Ancho=90,  Alto=220
}

# ============== FUNCIONES DE COLISIÓN ==============
def clamp(value, min_val, max_val):
    """Recorta 'value' para que esté entre min_val y max_val."""
    return max(min_val, min(value, max_val))

def circle_rect_collision(cx, cy, radius, rx, ry, rw, rh):
    """
    Devuelve True si el círculo (cx, cy, radius) colisiona con el rectángulo (rx, ry, rw, rh).
    Se dispara apenas el círculo 'toque' el borde del rectángulo.
    """
    closest_x = clamp(cx, rx, rx + rw)
    closest_y = clamp(cy, ry, ry + rh)
    dist_x = cx - closest_x
    dist_y = cy - closest_y
    dist_sq = dist_x**2 + dist_y**2
    return dist_sq < (radius**2)

def dentro_de_ventana(cx, cy, radius):
    """Devuelve True si el círculo (cx, cy, radius) se mantiene dentro de [0,0,WINDOW_WIDTH,WINDOW_HEIGHT]."""
    if cx - radius < 0 or cx + radius > WINDOW_WIDTH:
        return False
    if cy - radius < 0 or cy + radius > WINDOW_HEIGHT:
        return False
    return True

def movimiento_valido(nuevo_x, nuevo_y, radius):
    """
    Para el robot: movimiento válido si:
      1) Está dentro de la ventana.
      2) No colisiona con el hueco central.
    """
    # 1) Ventana
    if not dentro_de_ventana(nuevo_x, nuevo_y, radius):
        return False
    
    # 2) Hueco
    if circle_rect_collision(nuevo_x, nuevo_y, radius, *HUECO_RECT):
        return False
    
    return True

# ============== REINICIAR PROGRAMA ==============
def restart_program():
    pygame.quit()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ============== ENEMIGOS ==============
def crear_enemigos(num_enemigos=3):
    """
    Crea enemigos con posiciones y velocidades aleatorias.
    Cada enemigo es un dict: {'x':..., 'y':..., 'vx':..., 'vy':...}.
    """
    enemigos = []
    for _ in range(num_enemigos):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = random.randint(50, WINDOW_HEIGHT - 50)
        vx = random.choice([-2, 2])
        vy = random.choice([-2, 2])
        enemigos.append({'x': x, 'y': y, 'vx': vx, 'vy': vy})
    return enemigos

def mover_enemigos(enemigos, enemy_radius):
    """
    Actualiza la posición de cada enemigo y evita que atraviesen el hueco.
    También rebotan en los bordes de la ventana.
    """
    for e in enemigos:
        old_x = e['x']
        old_y = e['y']
        
        # Mover según la velocidad
        e['x'] += e['vx']
        e['y'] += e['vy']
        
        # Rebote en bordes de la ventana
        if e['x'] - enemy_radius < 0 or e['x'] + enemy_radius > WINDOW_WIDTH:
            e['vx'] *= -1
            e['x'] = clamp(e['x'], enemy_radius, WINDOW_WIDTH - enemy_radius)
        if e['y'] - enemy_radius < 0 or e['y'] + enemy_radius > WINDOW_HEIGHT:
            e['vy'] *= -1
            e['y'] = clamp(e['y'], enemy_radius, WINDOW_HEIGHT - enemy_radius)
        
        # Comprobar si colisiona con el hueco
        if circle_rect_collision(e['x'], e['y'], enemy_radius, *HUECO_RECT):
            # Revertir el movimiento
            e['x'] = old_x
            e['y'] = old_y
            # Invertir la velocidad (rebote)
            # Puedes mejorarlo si quieres un rebote más real
            e['vx'] *= -1
            e['vy'] *= -1

def colision_robot_enemigos(roomBA_x, roomBA_y, roomBA_radius, enemigos, enemy_radius):
    """
    Devuelve True si el robot colisiona con AL MENOS un enemigo (círculo-círculo).
    Esto hace que el robot pierda solo 1 de vida por frame, aunque colisione con varios.
    """
    for e in enemigos:
        dx = e['x'] - roomBA_x
        dy = e['y'] - roomBA_y
        dist_sq = dx**2 + dy**2
        if dist_sq < (roomBA_radius + enemy_radius)**2:
            return True
    return False

# ============== VISUALIZACIÓN ==============
def start_visualizacion(zonas, escala=1, tiempo_limite=30):
    """
    - Hueco NO transitable para robot y enemigos.
    - Cuenta atrás.
    - Robot con vida (pierde solo 1 por frame si colisiona con enemigos).
    - Game Over si vida=0 o se acaba el tiempo. Reinicio tras 2s.
    """
    pygame.init()
    ancho_ventana = int(WINDOW_WIDTH * escala)
    alto_ventana = int(WINDOW_HEIGHT * escala)
    screen = pygame.display.set_mode((ancho_ventana, alto_ventana))
    pygame.display.set_caption("Robot Aspirador - RoomBA Espacial")
    
    clock = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 24)
    
    # Generar motas
    motas = []
    for nombre_zona, (largo_cm, ancho_cm) in zonas.items():
        px_largo = int(largo_cm * escala)
        px_ancho = int(ancho_cm * escala)
        offset_x, offset_y = zona_offsets[nombre_zona]
        
        for _ in range(20):
            x = random.randint(offset_x, offset_x + px_largo - 1)
            y = random.randint(offset_y, offset_y + px_ancho - 1)
            motas.append((x, y))
    
    # Robot
    roomBA_vel = 3
    roomBA_radius = 10
    robot_life = 3
    
    # Posición inicial (por ejemplo, centro de 'Zona 3')
    initial_zone = 'Zona 3'
    z_offset_x, z_offset_y = zona_offsets[initial_zone]
    z_largo, z_ancho = zonas[initial_zone]
    px_largo = int(z_largo * escala)
    px_ancho = int(z_ancho * escala)
    roomBA_x = z_offset_x + px_largo // 2
    roomBA_y = z_offset_y + px_ancho // 2
    
    # Tiempo
    tiempo_restante = tiempo_limite
    
    # Enemigos
    enemy_radius = 10
    enemigos = crear_enemigos(num_enemigos=3)
    
    # Game Over
    game_over = False
    game_over_time = 0
    
    running = True
    while running:
        dt = clock.tick(30)
        dt_seg = dt / 1000.0
        
        # Cuenta atrás (si no hay game_over)
        if not game_over and tiempo_restante > 0:
            tiempo_restante -= dt_seg
            if tiempo_restante < 0:
                tiempo_restante = 0
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Lógica de Game Over
        if robot_life <= 0 or (tiempo_restante <= 0 and not game_over):
            game_over = True
            game_over_time = 2.0  # Esperar 2 segundos
        
        if game_over:
            game_over_time -= dt_seg
            if game_over_time <= 0:
                pygame.time.wait(500)
                restart_program()
        
        # Movimiento del robot (si no hay game_over y queda tiempo)
        nuevo_x = roomBA_x
        nuevo_y = roomBA_y
        if not game_over and tiempo_restante > 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                nuevo_x -= roomBA_vel
            if keys[pygame.K_RIGHT]:
                nuevo_x += roomBA_vel
            if keys[pygame.K_UP]:
                nuevo_y -= roomBA_vel
            if keys[pygame.K_DOWN]:
                nuevo_y += roomBA_vel
            
            if movimiento_valido(nuevo_x, nuevo_y, roomBA_radius):
                roomBA_x = nuevo_x
                roomBA_y = nuevo_y
        
        # Mover enemigos (si no hay game_over)
        if not game_over:
            mover_enemigos(enemigos, enemy_radius)
        
        # Colisión robot-enemigos (1 de vida por frame si hay colisión)
        if not game_over:
            if colision_robot_enemigos(roomBA_x, roomBA_y, roomBA_radius, enemigos, enemy_radius):
                robot_life -= 1
                if robot_life < 0:
                    robot_life = 0
        
        # RENDER
        screen.fill(COLOR_FONDO)
        
        # Dibujar zonas
        for nombre_zona, (largo_cm, ancho_cm) in zonas.items():
            px_largo = int(largo_cm)
            px_ancho = int(ancho_cm)
            offset_x, offset_y = zona_offsets[nombre_zona]
            pygame.draw.rect(
                screen, COLOR_ZONA,
                (offset_x, offset_y, px_largo, px_ancho),
                width=2
            )
        
        # Dibujar hueco
        pygame.draw.rect(screen, (200, 50, 50), HUECO_RECT, width=0)
        
        # Dibujar enemigos
        for e in enemigos:
            pygame.draw.circle(screen, COLOR_ENEMIGO, (int(e['x']), int(e['y'])), enemy_radius)
        
        # Dibujar robot
        pygame.draw.circle(screen, COLOR_ROOMBA, (roomBA_x, roomBA_y), roomBA_radius)
        
        # Dibujar motas
        nuevas_motas = []
        for (mx, my) in motas:
            dist_x = mx - roomBA_x
            dist_y = my - roomBA_y
            dist_sq = dist_x**2 + dist_y**2
            if dist_sq < roomBA_radius**2:
                continue
            else:
                nuevas_motas.append((mx, my))
                pygame.draw.circle(screen, COLOR_MOTA, (mx, my), 2)
        motas = nuevas_motas
        
        # Mensaje si no quedan motas
        if not motas and not game_over:
            texto_fin = fuente.render("¡Limpieza completada!", True, (255, 255, 255))
            screen.blit(texto_fin, (10, 40))
        
        # HUD: tiempo y vida
        # a) Tiempo
        tiempo_int = int(tiempo_restante)
        texto_tiempo = f"Tiempo: {tiempo_int} s"
        render_sombra_tiempo = fuente.render(texto_tiempo, True, COLOR_SOMBRA)
        render_texto_tiempo = fuente.render(texto_tiempo, True, COLOR_TEXTO)
        screen.blit(render_sombra_tiempo, (12, 10))
        screen.blit(render_texto_tiempo, (10, 10))
        
        # b) Vida
        texto_vida = f"Vida: {robot_life}"
        render_sombra_vida = fuente.render(texto_vida, True, COLOR_SOMBRA)
        render_texto_vida = fuente.render(texto_vida, True, COLOR_TEXTO)
        screen.blit(render_sombra_vida, (12, 30))
        screen.blit(render_texto_vida, (10, 30))
        
        # Mensajes de game over o tiempo agotado
        if robot_life <= 0:
            msg_go = "¡GAME OVER! Reiniciando..."
            sombra_go = fuente.render(msg_go, True, COLOR_SOMBRA)
            texto_go = fuente.render(msg_go, True, (255, 100, 100))
            screen.blit(sombra_go, (12, 60))
            screen.blit(texto_go, (10, 60))
        
        elif tiempo_restante <= 0:
            msg_timeout = "¡Se acabó el tiempo! Reiniciando..."
            sombra_to = fuente.render(msg_timeout, True, COLOR_SOMBRA)
            texto_to = fuente.render(msg_timeout, True, (255, 100, 100))
            screen.blit(sombra_to, (12, 60))
            screen.blit(texto_to, (10, 60))
        
        pygame.display.flip()
    
    pygame.quit()
