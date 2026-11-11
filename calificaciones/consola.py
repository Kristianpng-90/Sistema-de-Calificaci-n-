"""
Interfaz de consola (menú) del Sistema de Calificaciones.

Esta capa solo pide datos y muestra resultados; los cálculos los hace
el módulo `calculos` y el guardado el módulo `repositorio`.

Autor: Cristian Camilo Girata Ravelo
"""

import os
import sys

from . import __version__
from .calculos import (
    APROBADO, INCOMPLETO, REPROBADO,
    estado, nota_acumulada, nota_necesaria,
    promedio_ponderado, promedio_simple, resumen_curso,
)
from .modelos import DatoInvalidoError, Estudiante, Nota
from .repositorio import RepositorioEstudiantes

LINEA = "=" * 64


def ruta_datos():
    """El archivo JSON se guarda junto al ejecutable o junto a main.py."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "calificaciones.json")


# --- Utilidades de entrada --------------------------------------------
def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  ! Este campo es obligatorio.")


def pedir_numero(mensaje, minimo=None, maximo=None):
    """Pide un número; acepta coma o punto decimal y repite hasta que sea válido."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            numero = float(texto)
        except ValueError:
            print("  ! Escriba un número válido (por ejemplo 3.5).")
            continue
        if (minimo is not None and numero < minimo) or (maximo is not None and numero > maximo):
            print(f"  ! El valor debe estar entre {minimo} y {maximo}.")
            continue
        return numero


def pausar():
    input("\nPresione Enter para continuar...")


def elegir_estudiante(repo):
    if not repo.listar():
        print("  ! Todavía no hay estudiantes registrados.")
        return None
    codigo = pedir_texto("Código del estudiante: ")
    est = repo.buscar(codigo)
    if est is None:
        print("  ! No existe un estudiante con ese código.")
    return est


# --- Presentación -----------------------------------------------------
def mostrar_detalle(est):
    print(f"\n{LINEA}\n  {est.nombre}  (código {est.codigo})\n{LINEA}")
    if not est.notas:
        print("  Sin notas registradas.")
        return
    print(f"  {'#':<3}{'Descripción':<26}{'Nota':>7}{'Peso %':>9}{'Aporte':>9}")
    for i, n in enumerate(est.notas, start=1):
        aporte = n.valor * n.peso / 100
        print(f"  {i:<3}{n.descripcion[:25]:<26}{n.valor:>7.2f}{n.peso:>9.1f}{aporte:>9.2f}")
    print("  " + "-" * 54)
    print(f"  Porcentaje evaluado ..........: {est.peso_acumulado:.1f} %")
    print(f"  Promedio simple ..............: {promedio_simple(est.notas):.2f}")
    print(f"  Promedio ponderado ...........: {promedio_ponderado(est.notas):.2f}")
    print(f"  Nota acumulada (sobre 100 %) .: {nota_acumulada(est.notas):.2f}")
    situacion = estado(est.notas)
    print(f"  Estado .......................: {situacion}")
    if situacion == INCOMPLETO:
        necesaria = nota_necesaria(est.notas)
        if necesaria > 5.0:
            print(f"  Necesita {necesaria:.2f} en lo restante: ya no alcanza a aprobar.")
        else:
            print(f"  Necesita {necesaria:.2f} en el {100 - est.peso_acumulado:.1f} % restante para aprobar.")


def mostrar_reporte(repo):
    estudiantes = repo.listar()
    if not estudiantes:
        print("  ! Todavía no hay estudiantes registrados.")
        return
    print(f"\n{LINEA}\n  REPORTE GENERAL DEL CURSO\n{LINEA}")
    print(f"  {'Código':<12}{'Nombre':<26}{'%':>6}{'Prom.':>7}  Estado")
    for e in estudiantes:
        print(
            f"  {e.codigo:<12}{e.nombre[:25]:<26}{e.peso_acumulado:>6.0f}"
            f"{promedio_ponderado(e.notas):>7.2f}  {estado(e.notas)}"
        )
    r = resumen_curso(estudiantes)
    print("  " + "-" * 60)
    print(f"  Estudiantes registrados : {r['total']}")
    print(f"  Con nota final (100 %)  : {r['con_nota_final']}")
    print(f"  Aprobados / Reprobados  : {r['aprobados']} / {r['reprobados']}")
    if r["con_nota_final"]:
        print(f"  Promedio del curso      : {r['promedio_curso']:.2f}")
        print(f"  Nota más alta / más baja: {r['nota_mas_alta']:.2f} / {r['nota_mas_baja']:.2f}")


# --- Acciones del menú ------------------------------------------------
def registrar_estudiante(repo):
    codigo = pedir_texto("Código: ")
    nombre = pedir_texto("Nombre completo: ")
    repo.agregar(Estudiante(codigo, nombre))
    print(f"  ✓ Estudiante {nombre} registrado.")


def registrar_nota(repo):
    est = elegir_estudiante(repo)
    if est is None:
        return
    disponible = 100 - est.peso_acumulado
    if disponible <= 0:
        print("  ! Este estudiante ya tiene el 100 % evaluado.")
        return
    print(f"  Porcentaje disponible: {disponible:.1f} %")
    descripcion = pedir_texto("Descripción (ej. Parcial 1): ")
    valor = pedir_numero("Nota (0.0 a 5.0): ", 0.0, 5.0)
    peso = pedir_numero(f"Porcentaje (máx. {disponible:g} %): ", 0.1, disponible)
    est.agregar_nota(Nota(descripcion, valor, peso))
    repo.guardar()
    print("  ✓ Nota registrada.")
    mostrar_detalle(est)


def consultar_estudiante(repo):
    est = elegir_estudiante(repo)
    if est is not None:
        mostrar_detalle(est)


def eliminar_nota(repo):
    est = elegir_estudiante(repo)
    if est is None:
        return
    mostrar_detalle(est)
    if not est.notas:
        return
    numero = int(pedir_numero("Número de la nota a eliminar: "))
    nota = est.eliminar_nota(numero - 1)
    repo.guardar()
    print(f"  ✓ Nota '{nota.descripcion}' eliminada.")


def eliminar_estudiante(repo):
    codigo = pedir_texto("Código del estudiante a eliminar: ")
    confirmar = input("¿Seguro? Esta acción no se puede deshacer (s/n): ").strip().lower()
    if confirmar == "s":
        est = repo.eliminar(codigo)
        print(f"  ✓ Estudiante {est.nombre} eliminado.")
    else:
        print("  Operación cancelada.")


OPCIONES = {
    "1": ("Registrar estudiante", registrar_estudiante),
    "2": ("Registrar nota", registrar_nota),
    "3": ("Consultar estudiante (promedio y estado)", consultar_estudiante),
    "4": ("Reporte general del curso", mostrar_reporte),
    "5": ("Eliminar una nota", eliminar_nota),
    "6": ("Eliminar estudiante", eliminar_estudiante),
}


def main():
    try:
        repo = RepositorioEstudiantes(ruta_datos())
    except DatoInvalidoError as error:
        print(f"Error: {error}")
        pausar()
        return

    while True:
        print(f"\n{LINEA}\n  SISTEMA DE CALIFICACIONES  v{__version__}")
        print("  Escala 0.0 – 5.0  |  Nota mínima aprobatoria: 3.0")
        print(LINEA)
        for clave, (texto, _) in OPCIONES.items():
            print(f"  {clave}. {texto}")
        print("  0. Salir")
        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "0":
            print("Datos guardados. ¡Hasta luego!")
            break
        if opcion not in OPCIONES:
            print("  ! Opción no válida.")
            continue
        try:
            OPCIONES[opcion][1](repo)
        except DatoInvalidoError as error:
            print(f"  ! {error}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Operación cancelada.")
        pausar()
