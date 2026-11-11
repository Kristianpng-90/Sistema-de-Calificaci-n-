"""
Persistencia de los estudiantes en un archivo JSON.

Autor: Cristian Camilo Girata Ravelo
"""

import json
import os

from .modelos import DatoInvalidoError, Estudiante


class RepositorioEstudiantes:
    """Guarda y recupera estudiantes. Mantiene el orden de registro."""

    def __init__(self, ruta_archivo="calificaciones.json"):
        self.ruta = ruta_archivo
        self._estudiantes = {}
        self.cargar()

    # --- Operaciones de consulta ---------------------------------------
    def listar(self):
        return list(self._estudiantes.values())

    def buscar(self, codigo):
        return self._estudiantes.get(str(codigo).strip())

    # --- Operaciones de modificación -----------------------------------
    def agregar(self, estudiante):
        if estudiante.codigo in self._estudiantes:
            raise DatoInvalidoError(
                f"Ya existe un estudiante con el código {estudiante.codigo}."
            )
        self._estudiantes[estudiante.codigo] = estudiante
        self.guardar()

    def eliminar(self, codigo):
        est = self._estudiantes.pop(str(codigo).strip(), None)
        if est is None:
            raise DatoInvalidoError("No existe un estudiante con ese código.")
        self.guardar()
        return est

    # --- Archivo -------------------------------------------------------
    def guardar(self):
        datos = [e.a_dict() for e in self._estudiantes.values()]
        temporal = self.ruta + ".tmp"
        with open(temporal, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        os.replace(temporal, self.ruta)  # escritura atómica

    def cargar(self):
        if not os.path.exists(self.ruta):
            return
        try:
            with open(self.ruta, encoding="utf-8") as f:
                datos = json.load(f)
            self._estudiantes = {
                d["codigo"]: Estudiante.desde_dict(d) for d in datos
            }
        except (json.JSONDecodeError, KeyError, DatoInvalidoError) as error:
            raise DatoInvalidoError(
                f"El archivo {self.ruta} está dañado y no se pudo leer: {error}"
            )
