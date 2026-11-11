"""
Pruebas unitarias del Sistema de Calificaciones.

Ejecutar:  python -m unittest discover -s tests -v
"""

import os
import tempfile
import unittest

from calificaciones.calculos import (
    APROBADO, INCOMPLETO, REPROBADO, SIN_NOTAS,
    estado, nota_acumulada, nota_necesaria,
    promedio_ponderado, promedio_simple, resumen_curso,
)
from calificaciones.modelos import DatoInvalidoError, Estudiante, Nota
from calificaciones.repositorio import RepositorioEstudiantes


def notas(*pares):
    return [Nota(f"N{i}", v, p) for i, (v, p) in enumerate(pares, start=1)]


class PruebasValidacion(unittest.TestCase):
    def test_cp01_nota_valida(self):
        n = Nota("Parcial", 4.5, 30)
        self.assertEqual((n.valor, n.peso), (4.5, 30.0))

    def test_cp02_nota_fuera_de_rango(self):
        for valor in (-0.1, 5.1, 10):
            with self.assertRaises(DatoInvalidoError):
                Nota("X", valor, 30)

    def test_cp03_limites_de_la_escala(self):
        self.assertEqual(Nota("Min", 0.0, 10).valor, 0.0)
        self.assertEqual(Nota("Max", 5.0, 10).valor, 5.0)

    def test_cp04_porcentaje_invalido(self):
        for peso in (0, -5, 101):
            with self.assertRaises(DatoInvalidoError):
                Nota("X", 3.0, peso)

    def test_cp05_texto_no_numerico(self):
        with self.assertRaises(DatoInvalidoError):
            Nota("X", "abc", 30)

    def test_cp06_porcentajes_no_superan_100(self):
        e = Estudiante("1", "Ana")
        e.agregar_nota(Nota("P1", 4, 60))
        with self.assertRaises(DatoInvalidoError):
            e.agregar_nota(Nota("P2", 4, 50))
        self.assertEqual(len(e.notas), 1)

    def test_cp07_estudiante_sin_nombre(self):
        with self.assertRaises(DatoInvalidoError):
            Estudiante("1", "   ")


class PruebasCalculos(unittest.TestCase):
    def test_cp08_promedio_simple(self):
        self.assertEqual(promedio_simple(notas((3, 30), (4, 30), (5, 40))), 4.0)

    def test_cp09_promedio_ponderado(self):
        # 3*0.3 + 4*0.3 + 5*0.4 = 0.9 + 1.2 + 2.0 = 4.1
        self.assertEqual(promedio_ponderado(notas((3, 30), (4, 30), (5, 40))), 4.1)

    def test_cp10_lista_vacia(self):
        self.assertEqual(promedio_simple([]), 0.0)
        self.assertEqual(promedio_ponderado([]), 0.0)

    def test_cp11_nota_acumulada_parcial(self):
        # 4.0 en 30 % aporta 1.2
        self.assertEqual(nota_acumulada(notas((4, 30))), 1.2)

    def test_cp12_nota_necesaria(self):
        # Acumulado 1.2 con 70 % restante → (3.0 - 1.2) / 0.7 = 2.57
        self.assertEqual(nota_necesaria(notas((4, 30))), 2.57)
        self.assertIsNone(nota_necesaria(notas((4, 100))))


class PruebasAprobacion(unittest.TestCase):
    def test_cp13_aprueba(self):
        self.assertEqual(estado(notas((3, 30), (4, 30), (5, 40))), APROBADO)

    def test_cp14_reprueba(self):
        self.assertEqual(estado(notas((2, 30), (2.5, 30), (3, 40))), REPROBADO)

    def test_cp15_limite_exacto_3_0_aprueba(self):
        self.assertEqual(estado(notas((3, 50), (3, 50))), APROBADO)

    def test_cp16_justo_debajo_reprueba(self):
        self.assertEqual(estado(notas((2.9, 50), (3.0, 50))), REPROBADO)

    def test_cp17_incompleto_y_sin_notas(self):
        self.assertEqual(estado(notas((5, 30))), INCOMPLETO)
        self.assertEqual(estado([]), SIN_NOTAS)

    def test_cp18_resumen_del_curso(self):
        a = Estudiante("1", "Ana"); a.notas = notas((4, 100))
        b = Estudiante("2", "Luis"); b.notas = notas((2, 100))
        c = Estudiante("3", "Sara"); c.notas = notas((5, 40))  # incompleto
        r = resumen_curso([a, b, c])
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["con_nota_final"], 2)
        self.assertEqual((r["aprobados"], r["reprobados"]), (1, 1))
        self.assertEqual(r["promedio_curso"], 3.0)


class PruebasRepositorio(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.dir.name, "datos.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_cp19_guardar_y_recargar(self):
        repo = RepositorioEstudiantes(self.ruta)
        e = Estudiante("100", "María Pérez")
        repo.agregar(e)
        e.agregar_nota(Nota("Parcial 1", 4.2, 30))
        repo.guardar()

        recargado = RepositorioEstudiantes(self.ruta).buscar("100")
        self.assertEqual(recargado.nombre, "María Pérez")
        self.assertEqual(recargado.notas[0].valor, 4.2)

    def test_cp20_codigo_duplicado(self):
        repo = RepositorioEstudiantes(self.ruta)
        repo.agregar(Estudiante("1", "Ana"))
        with self.assertRaises(DatoInvalidoError):
            repo.agregar(Estudiante("1", "Otra"))

    def test_cp21_archivo_danado(self):
        with open(self.ruta, "w", encoding="utf-8") as f:
            f.write("{esto no es json")
        with self.assertRaises(DatoInvalidoError):
            RepositorioEstudiantes(self.ruta)


if __name__ == "__main__":
    unittest.main()
