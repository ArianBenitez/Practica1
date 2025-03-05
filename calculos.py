"""
==========================================================
 INFECCION EN LA ESTACION ESPACIAL
==========================================================

==========================================================
"""

import concurrent.futures

def calcular_area(largo, ancho):
    """
    Calcula el area de una zona multiplicando largo por ancho.
    """
    return largo * ancho

def main():
    """
    Funcion principal que:
    1. Define las dimensiones de cada zona.
    2. Usa concurrencia para calcular el area de cada zona.
    3. Suma las areas totales.
    4. Calcula el tiempo de limpieza.
    5. Muestra los resultados en consola.
    """

    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (480, 101),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }
    
    # Tasa de limpieza en cm²/segundo (fija)
    tasa_limpeza = 1000  # cm²/s
    
    # Diccionario para almacenar el area calculada de cada zona
    areas = {}

    # Usamos ThreadPoolExecutor para lanzar hilos concurrentes
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_zona = {
            executor.submit(calcular_area, largo, ancho): zona
            for zona, (largo, ancho) in zonas.items()
        }
        
        # Recolectamos los resultados a medida que se completan
        for future in concurrent.futures.as_completed(future_to_zona):
            zona = future_to_zona[future]
            try:
                area = future.result()
            except Exception as exc:
                print(f"{zonas} genero una excepcion: {exc}")
            else:
                areas[zonas] = area
                print(f"{zonas}: {area} cm²")
    
    # Sumar las áreas totales
    superficie_total = sum(areas.values())
    
    # Calcular el tiempo de limpieza en segundos
    tiempo_limpeza_seg = superficie_total / tasa_limpeza
    
    # Conversion a minutos
    # tiempo_limpeza_min = tiempo_limpeza_seg / 60
    
    # Mostrar los resultados
    print("\n=======================================")
    print("      RESULTADOS DEL CALCULO          ")
    print("=======================================")
    print(f"\nSuperficie total a limpiar: {superficie_total} cm²")
    print(f"\nTiempo estimado de limpieza: {tiempo_limpeza_seg:.2f} segundos")
    print(f" Equivalente a: {tiempo_limpeza_min:.2f} minutos")

if __name__ == '__main__':
    main()
