https://github.com/ArianBenitez/Practica1.git

# Robot Cleaning - Laboratorio de Virus

Este proyecto simula la limpieza de un "Laboratorio de Virus" utilizando un robot aspirador (nanobot) que opera en modo automático o manual. La simulación se desarrolla en Python y utiliza Pygame para la visualización y gestión de la interfaz gráfica, 
mientras que la lógica del juego (movimiento, colisiones, generación de virus y enemigos, incremento de radiación, etc.) se gestiona de forma concurrente mediante hilos (threads).

## Características

- **Modularidad y Concurrencia:**  
  Se utilizan hilos para gestionar el cálculo de áreas, el movimiento del robot, la dispersión de virus y enemigos, y el incremento gradual de la radiación.
  
- **Modos de Control:**  
  El usuario puede seleccionar entre modo manual (usando las flechas del teclado) o modo automático (donde se utiliza un algoritmo BFS para la navegación).

- **Interacción y Game Over:**  
  Al agotarse las vidas o alcanzar un nivel crítico de radiación, el juego muestra una pantalla de Game Over con la opción de reiniciar.

## Requisitos

- **Python 3.6 o superior**
- **Pygame**  
  Para instalar las dependencias, ejecuta:
  ```bash
  pip install -r requirements.txt
