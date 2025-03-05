import pygame
import random


# Colores para el fondo y las zonas
COLOR_FONDO = (30, 30, 30)
COLOR_ZONA = (100, 100, 200)
COLOR_ASPIRADOR = (255, 255, 0)
COLOR_POLVO = (255, 255, 255)

def startVisualizacion(zonas, escala = 1):
    '''
    Inicia la ventana de pygame y muestra:
    - Las zonas dibujadas como rectángulos.
    - El aspirador
    - Motas de polvo distribuidas por cada zona
    '''

    pygame.init()

    #Calcular el tamaño total de la ventana
    ancho_ventana = 600 * escala
    alto_ventana = 700 * escala
    screen = pygame.display.set_mode((ancho_ventana, alto_ventana))
    pygame.display.set_caption("RoomBA Espacial")

    #Reloj que controla FPS
    clock = pygame.time.Clock()

    #Posición inicial del aspirador
    roombae_x = ancho_ventana // 2
    roombae_y = alto_ventana //2
    roombae_vel = 3

    #Generar motas de polvo en cada zona
    motas = []
    for nombre_zona, (largo, ancho) in zonas.items():
        #Convierto en píxeles
        px_largo = int(largo * escala)
        px_ancho = int (ancho * escala)

        offset_x, offset_y = (50, 50)

        for _ in range(20):
            x = random.randint(offset_x, offset_x + px_largo - 1)
            y = random.randint(offset_y, offset_y + px_ancho - 1)
            motas.append((x, y))
    

    #Bucle principal
    running = True
    while running:
        #Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #Control manual del aspirador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            roombae_x -= roombae_vel
        if keys[pygame.K_RIGHT]:
            roombae_x += roombae_vel
        if keys[pygame.K_UP]:
            roombae_y -= roombae_vel
        if keys[pygame.K_DOWN]:
            roombae_y += roombae_vel

        #Limpiar la pantalla
        screen.fill(COLOR_FONDO)

