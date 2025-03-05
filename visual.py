import pygame
import random

# Colores (R, G, B)
COLOR_FONDO = (30, 30, 30)
COLOR_ZONA = (100, 100, 200)
COLOR_ROOMBA = (255, 255, 0)
COLOR_MOTA = (255, 255, 255)

# Asigna a cada zona una posición en la ventana
zona_offsets = {
    'Zona 1' : (30, 0),   #Ancho = 500, Alto = 150
    'Zona 2' : (40, 150),   #Ancho = 480, Alto = 101
    'Zona 3' : (30, 210),   #Ancho = 309, Alto = 480
    'Zona 4' : (470, 210),   #Ancho = 90, Alto = 220
}

def start_visualizacion(zonas, escala=1):
    """
    Inicia la ventana de pygame y muestra:
    - Las zonas dibujadas como rectángulos.
    - Un 'Pac-Man' que se mueve.
    - Motas de polvo distribuidas en cada zona.
    
    :param zonas: dict con {'Zona 1': (largo, ancho), ...}
    :param escala: cuántos píxeles equivalen a 1 cm.
    """
    pygame.init()
    
    # Calcular el tamaño total de la ventana
    # (Opcional: si tienes un plano general, ajusta a su dimensión)
    # Aquí asumimos que la dimensión mayor no supera 600~700 px, como ejemplo.
    # Podríamos usar la zona más grande para definir la ventana.
    
    ancho_ventana = 560 * escala
    alto_ventana = 690 * escala
    screen = pygame.display.set_mode((ancho_ventana, alto_ventana))
    pygame.display.set_caption("Robot Aspirador - RoomBA Espacial")
    
    # Reloj para controlar FPS
    clock = pygame.time.Clock()
    
    # Posición inicial de Pac-Man (al centro de la ventana, por ejemplo)
    roomBA_x = ancho_ventana // 2
    roomBA_y = alto_ventana // 2
    roomBA_vel = 3  # Velocidad de movimiento (píxeles por frame)
    roomBA_radius = 10
    
    # Generar motas de polvo en cada zona
    # Para simplicidad, creamos una lista global de motas con (x, y) en píxeles
    motas = []
    for nombre_zona, (largo, ancho) in zonas.items():
        # Convertir a píxeles
        px_largo = int(largo * escala)
        px_ancho = int(ancho * escala)
        
        #Obten la posicion de la zona para dibujarla en el lugar correcto
        offset_x, offset_y = zona_offsets[nombre_zona]

        
        # Crear motas aleatorias dentro de la zona
        for _ in range(20):  # 20 motas por zona
            x = random.randint(offset_x, offset_x + px_largo - 1)
            y = random.randint(offset_y, offset_y + px_ancho - 1)
            motas.append((x, y))
    
    # Bucle principal
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Controles de Pac-Man con flechas (opcional)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            roomBA_x -= roomBA_vel
        if keys[pygame.K_RIGHT]:
            roomBA_x += roomBA_vel
        if keys[pygame.K_UP]:
            roomBA_y -= roomBA_vel
        if keys[pygame.K_DOWN]:
            roomBA_y += roomBA_vel
        
        # Limpiar la pantalla
        screen.fill(COLOR_FONDO)
        
        # Dibujar cada zona en su posición.
        for nombre_zona, (largo, ancho) in zonas.items():
            px_largo = int(largo * escala)
            px_ancho = int(ancho * escala)
            offset_x, offset_y = zona_offsets[nombre_zona]

            pygame.draw.rect(
                screen, 
                COLOR_ZONA, 
                (offset_x, offset_y, px_largo, px_ancho),
                width=2 
            )
        
        # Dibujar Pac-Man (un círculo amarillo)
        pacman_radius = 10
        pygame.draw.circle(screen, COLOR_ROOMBA, (roomBA_x, roomBA_y), roomBA_radius)
        
        # Dibujar motas y detectar colisiones
        nuevas_motas = []
        for (mx, my) in motas:
            dist_x = mx - roomBA_x
            dist_y = my - roomBA_y
            dist_sq = dist_x**2 + dist_y**2

            # Si está muy cerca (colisión), no se vuelve a dibujar la mota
            if dist_sq < roomBA_radius**2:
                continue
            else:
                nuevas_motas.append((mx, my))
                pygame.draw.circle(screen, COLOR_MOTA, (mx, my), 2)
        
        motas = nuevas_motas
        
        # Si no quedan motas, mostrar un mensaje de "Limpieza completada"
        if not motas:
            fuente = pygame.font.SysFont(None, 36)
            texto = fuente.render("¡Limpieza completada!", True, (255, 255, 255))
            screen.blit(texto, (50, 10))
        
        # Actualizar la pantalla
        pygame.display.flip()
        
        clock.tick(30)
    
    pygame.quit()
