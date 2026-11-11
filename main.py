"""
Punto de entrada del Sistema de Calificaciones.

Ejecutar:  python main.py

Autor: Cristian Camilo Girata Ravelo
"""

from calificaciones.consola import main

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")
