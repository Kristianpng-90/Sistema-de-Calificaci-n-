"""
Reglas de negocio: cálculo de promedios y decisión de aprobación.

Funciones puras (no leen teclado ni archivos) para que puedan probarse
de forma aislada con pruebas unitarias.

Autor: Cristian Camilo Girata Ravelo
"""

from .modelos import PESO_TOTAL

NOTA_APROBATORIA = 3.0

APROBADO = "APROBADO"
REPROBADO = "REPROBADO"
INCOMPLETO = "INCOMPLETO"
SIN_NOTAS = "SIN NOTAS"


def promedio_simple(notas):
    """Media aritmética de los valores, sin tener en cuenta los porcentajes."""
    if not notas:
        return 0.0
    return round(sum(n.valor for n in notas) / len(notas), 2)


def promedio_ponderado(notas):
    """
    Promedio ponderado sobre el porcentaje evaluado hasta el momento.

        promedio = Σ(valor_i × peso_i) / Σ(peso_i)
    """
    total_peso = sum(n.peso for n in notas)
    if total_peso == 0:
        return 0.0
    return round(sum(n.valor * n.peso for n in notas) / total_peso, 2)


def nota_acumulada(notas):
    """Aporte real a la nota final: Σ(valor_i × peso_i) / 100."""
    return round(sum(n.valor * n.peso for n in notas) / PESO_TOTAL, 2)


def nota_necesaria(notas):
    """
    Nota mínima que se necesita en el porcentaje restante para llegar a 3.0.
    Devuelve None si ya no queda porcentaje por evaluar.
    """
    restante = PESO_TOTAL - sum(n.peso for n in notas)
    if restante <= 0:
        return None
    faltante = NOTA_APROBATORIA - nota_acumulada(notas)
    return round(max(0.0, faltante * PESO_TOTAL / restante), 2)


def estado(notas):
    """
    Determina la situación del estudiante:
      - SIN NOTAS: no tiene notas registradas.
      - INCOMPLETO: los porcentajes aún no suman 100 %.
      - APROBADO: porcentajes completos y nota final ≥ 3.0.
      - REPROBADO: porcentajes completos y nota final < 3.0.
    """
    if not notas:
        return SIN_NOTAS
    if round(sum(n.peso for n in notas), 2) < PESO_TOTAL:
        return INCOMPLETO
    return APROBADO if promedio_ponderado(notas) >= NOTA_APROBATORIA else REPROBADO


def resumen_curso(estudiantes):
    """Estadísticas del grupo considerando solo a quienes tienen el 100 % evaluado."""
    finales = [
        promedio_ponderado(e.notas)
        for e in estudiantes
        if estado(e.notas) in (APROBADO, REPROBADO)
    ]
    aprobados = sum(1 for f in finales if f >= NOTA_APROBATORIA)
    return {
        "total": len(estudiantes),
        "con_nota_final": len(finales),
        "aprobados": aprobados,
        "reprobados": len(finales) - aprobados,
        "promedio_curso": round(sum(finales) / len(finales), 2) if finales else 0.0,
        "nota_mas_alta": max(finales) if finales else 0.0,
        "nota_mas_baja": min(finales) if finales else 0.0,
    }
