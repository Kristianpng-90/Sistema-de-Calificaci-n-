"""
Modelos de datos del Sistema de Calificaciones.

Define las entidades Nota y Estudiante. Toda la validación de datos de
entrada (rangos de nota y porcentaje) vive aquí, para que ninguna otra
capa pueda crear un objeto inválido.

Autor: Cristian Camilo Girata Ravelo
"""

from dataclasses import dataclass, field

# Escala de calificación colombiana (Universidad Manuela Beltrán)
NOTA_MINIMA = 0.0
NOTA_MAXIMA = 5.0
PESO_TOTAL = 100.0


class DatoInvalidoError(ValueError):
    """Se lanza cuando un dato ingresado no cumple las reglas del sistema."""


@dataclass
class Nota:
    """Una calificación con su porcentaje (peso) dentro de la nota final."""

    descripcion: str
    valor: float
    peso: float  # porcentaje, de 0 a 100

    def __post_init__(self):
        self.descripcion = self.descripcion.strip()
        if not self.descripcion:
            raise DatoInvalidoError("La descripción de la nota no puede estar vacía.")
        try:
            self.valor = float(self.valor)
            self.peso = float(self.peso)
        except (TypeError, ValueError):
            raise DatoInvalidoError("La nota y el porcentaje deben ser números.")
        if not NOTA_MINIMA <= self.valor <= NOTA_MAXIMA:
            raise DatoInvalidoError(
                f"La nota debe estar entre {NOTA_MINIMA} y {NOTA_MAXIMA}."
            )
        if not 0 < self.peso <= PESO_TOTAL:
            raise DatoInvalidoError("El porcentaje debe ser mayor que 0 y máximo 100.")

    def a_dict(self):
        return {"descripcion": self.descripcion, "valor": self.valor, "peso": self.peso}

    @classmethod
    def desde_dict(cls, datos):
        return cls(datos["descripcion"], datos["valor"], datos["peso"])


@dataclass
class Estudiante:
    """Un estudiante identificado por su código, con su lista de notas."""

    codigo: str
    nombre: str
    notas: list = field(default_factory=list)

    def __post_init__(self):
        self.codigo = str(self.codigo).strip()
        self.nombre = self.nombre.strip()
        if not self.codigo:
            raise DatoInvalidoError("El código del estudiante no puede estar vacío.")
        if not self.nombre:
            raise DatoInvalidoError("El nombre del estudiante no puede estar vacío.")

    @property
    def peso_acumulado(self):
        return round(sum(n.peso for n in self.notas), 2)

    def agregar_nota(self, nota):
        """Agrega una nota sin permitir que los porcentajes superen el 100 %."""
        if self.peso_acumulado + nota.peso > PESO_TOTAL + 1e-9:
            disponible = round(PESO_TOTAL - self.peso_acumulado, 2)
            raise DatoInvalidoError(
                f"El porcentaje excede el 100 %. Disponible: {disponible} %."
            )
        self.notas.append(nota)

    def eliminar_nota(self, indice):
        if not 0 <= indice < len(self.notas):
            raise DatoInvalidoError("No existe una nota con ese número.")
        return self.notas.pop(indice)

    def a_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "notas": [n.a_dict() for n in self.notas],
        }

    @classmethod
    def desde_dict(cls, datos):
        est = cls(datos["codigo"], datos["nombre"])
        for n in datos.get("notas", []):
            est.agregar_nota(Nota.desde_dict(n))
        return est
