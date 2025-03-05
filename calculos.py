import concurrent.futures
from visual_01 import start_visualizacion


def calcular_area(largo, ancho):
    """Calcula el área de una zona multiplicando largo por ancho."""
    return largo * ancho
 
def main():
    # Definición de las zonas con sus dimensiones (largo, ancho)
    zonas = {
        'Zona 1': (500, 150),
        'Zona 2': (101, 480),
        'Zona 3': (309, 480),
        'Zona 4': (90, 220)
    }
    
    # Tasa de limpieza (por ejemplo, 1000 cm²/segundo)
    tasa_limpeza = 1000  # cm²/s
    
    # Diccionario para almacenar el área calculada de cada zona
    areas = {}
    
    # Uso de ThreadPoolExecutor para ejecutar los cálculos de forma concurrente
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Asignamos cada cálculo a un hilo
        future_to_zona = {
            executor.submit(calcular_area, largo, ancho): zona
            for zona, (largo, ancho) in zonas.items()
        }
        
        # Recogemos los resultados a medida que se van completando
        for future in concurrent.futures.as_completed(future_to_zona):
            zona = future_to_zona[future]
            try:
                area = future.result()
            except Exception as exc:
                print(f"{zona} generó una excepción: {exc}")
            else:
                areas[zona] = area
                print(f"{zona}: {area} cm²")
                
    # Calcular la superficie total sumando las áreas parciales
    superficie_total = sum(areas.values())
    # Calcular el tiempo de limpieza
    tiempo_limpieza = superficie_total / tasa_limpeza
    # Pasar el tiempo a minutos
    tiempo_limpieza_min = tiempo_limpieza / 60
    
    print(f"\nSuperficie total a limpiar: {superficie_total} cm²")
    print(f"Tiempo estimado de limpieza: {tiempo_limpieza:.2f} segundos")
    print(f"Tiempo estimado de limpieza en minutos: {tiempo_limpieza_min:.2f} minutos")


    start_visualizacion(zonas, escala=1)
    
if __name__ == '__main__':
    main()