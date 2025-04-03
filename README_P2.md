https://github.com/ArianBenitez/Practica1.git


RoomBA – Sistema Cliente-Servidor con Verificación de Números Primos
Esta práctica extiende el proyecto RoomBA original (simulación de un robot aspirador en un laboratorio) para incorporar una funcionalidad adicional: la verificación remota de números primos utilizando un sistema cliente-servidor basado en TCP.

Descripción
El proyecto se divide en dos grandes módulos:

Simulación RoomBA:

Representa un laboratorio con zonas delimitadas, un robot aspirador que se mueve (en modo manual o automático) y genera elementos como ácaros (virus) y enemigos.

La simulación se ejecuta en el cliente usando Pygame y se actualiza a partir del estado enviado por el servidor.

Verificación de Números Primos:

Se incorpora una función isprime(n) en el servidor que determina si un número entero es primo.

El servidor procesa el comando CHECK_PRIME recibido desde el cliente y responde con el mensaje correspondiente (por ejemplo, "El número 7 es primo" o "El número 10 no es primo").

La actividad se registra en un archivo de log (opcional) para seguimiento y análisis.

Estructura del Proyecto
bash
Copy
RoomBA_ClientServer/
├── client/
│   ├── main_client.py       # Cliente con Pygame que actualiza la simulación y permite verificar primos.
│   ├── net_client.py        # Gestión de la comunicación TCP desde el cliente.
├── server/
│   ├── main_server.py       # Servidor que integra la lógica de la simulación y el nuevo comando CHECK_PRIME.
│   ├── game_state.py        # Almacena el estado global del juego (robot, zonas, ácaros, etc.).
│   ├── areas_server.py      # Hilo para cálculo de áreas del laboratorio.
│   ├── roomba_server.py     # Lógica del movimiento del robot (BFS, colisiones, etc.).
│   ├── spawn_mites_server.py# Hilo que genera ácaros/virus.
│   ├── spawn_enemies_server.py # Hilo que genera enemigos.
│   ├── radiation_server.py  # Hilo que gestiona el incremento de la radiación.
├── main_principal.py        # Script principal que lanza el servidor y luego el cliente.
└── README.md                # Este archivo.
Cómo Ejecutar el Proyecto
Requisitos:

Python 3.

Biblioteca Pygame (pip install pygame).

Ejecución:

Desde la terminal:
Ejecuta el script principal para iniciar el sistema completo:

bash
Copy
python main_principal.py
Este script lanza el servidor (que maneja la simulación y la verificación de números primos) y, tras un tiempo de espera para que el servidor se inicie, lanza el cliente.

Interacción en el Cliente:

La ventana del cliente mostrará la simulación del laboratorio con el robot, zonas, ácaros y enemigos.

Movimientos: Usa las teclas de flecha para mover el robot (modo manual).

Verificación de Primos:
Presiona la tecla P para activar la verificación. Se te solicitará (en la terminal) que ingreses un número entero; tras ingresarlo, el cliente enviará el comando al servidor y mostrará el resultado en la pantalla y en la consola.

Finalización:

Cierra la ventana del cliente o presiona ESC para salir.

El script principal se encargará de cerrar el cliente y terminar el proceso del servidor.

Desarrollo y Desafíos
Modularización y Concurrencia:
Se integraron múltiples hilos en el servidor para gestionar de manera concurrente distintas tareas (cálculo de áreas, movimiento del robot, generación de ácaros y enemigos, y el incremento de la radiación). Se utilizó un objeto GameState compartido con un lock para garantizar la consistencia del estado.

Implementación del Sistema TCP:
Se utilizó la biblioteca socket de Python para crear un servidor TCP que escucha en 127.0.0.1:5000 (o 8809 para la funcionalidad de verificación, dependiendo de la integración).
Se añadió el comando CHECK_PRIME para enviar y recibir datos relativos a la verificación de números primos, gestionando la conversión entre bytes y cadenas.

Integración de la Funcionalidad de Primos en RoomBA:
Uno de los principales retos fue integrar la lógica de verificación de números primos sin afectar la simulación original. Se resolvió añadiendo un nuevo comando en el servidor y actualizando el cliente para que, mediante la tecla "P", se solicite y muestre el resultado de la verificación.

Sincronización y Fluidez en la Interfaz:
Se implementó un hilo de escucha en el cliente para actualizar periódicamente el estado desde el servidor y evitar bloqueos en el bucle principal de Pygame. Asimismo, se consideró el manejo de entradas bloqueantes (por ejemplo, input()) y se documentaron posibles mejoras para implementar una entrada no bloqueante en el futuro.

Estrategias para la Verificación de Números Primos
La función isprime(n) se implementó utilizando un método optimizado que:

Elimina números menores o iguales a 1.

Valida directamente números hasta 3.

Descarta divisibilidad por 2 y 3.

Itera en saltos de 6, comprobando divisibilidad por i y i+2, lo que reduce significativamente el número de iteraciones necesarias para números grandes.

Conclusión
Esta práctica demuestra la integración de un sistema cliente-servidor en el contexto de una simulación interactiva (RoomBA), extendiéndola para incluir el procesamiento remoto de datos (verificación de números primos). El proyecto es modular, usa concurrencia de manera efectiva y sigue buenas prácticas en la comunicación por red, lo que lo hace escalable y fácilmente ampliable a futuras funcionalidades.