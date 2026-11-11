# Sistema de Calificaciones

Programa de consola en Python para **registrar notas, calcular promedios y determinar si un estudiante aprueba**.
Taller individual — Ingeniería de Software, Universidad Manuela Beltrán.

**Autor:** Cristian Camilo Girata Ravelo

---

## Funcionalidades

| # | Opción del menú | Qué hace |
|---|-----------------|----------|
| 1 | Registrar estudiante | Crea un estudiante con código único y nombre. |
| 2 | Registrar nota | Agrega una nota (0.0–5.0) con su porcentaje; impide que los porcentajes superen el 100 %. |
| 3 | Consultar estudiante | Muestra las notas, el promedio simple, el promedio ponderado, la nota acumulada, el estado y la nota que le falta para aprobar. |
| 4 | Reporte general | Lista a todos los estudiantes con su estado, y las estadísticas del curso (aprobados, reprobados, promedio, nota más alta y más baja). |
| 5 | Eliminar una nota | Corrige una nota mal ingresada. |
| 6 | Eliminar estudiante | Borra un estudiante (pide confirmación). |

Los datos se guardan automáticamente en `calificaciones.json`, junto al programa, así que no se pierden al cerrar.

## Reglas de calificación

- Escala de **0.0 a 5.0**. Se acepta coma o punto decimal (`4,5` o `4.5`).
- **Promedio ponderado** = Σ(nota × porcentaje) / Σ(porcentajes).
- El estudiante **APRUEBA** si tiene el 100 % evaluado y su nota final es **≥ 3.0**.
- Estados posibles: `APROBADO`, `REPROBADO`, `INCOMPLETO` (aún no suma 100 %) y `SIN NOTAS`.
- Mientras está incompleto, el sistema calcula la **nota necesaria** en el porcentaje restante para llegar a 3.0.

## Cómo ejecutarlo

### Opción A — Ejecutable (sin instalar Python)

1. Abra **[Releases → v1.0.0](https://github.com/Kristianpng-90/Sistema-de-Calificaci-n-/releases/latest)**.
2. Descargue `SistemaCalificaciones-Windows.exe` y haga doble clic para abrirlo.

También se puede descargar desde la pestaña **Actions** → la última ejecución verde → sección **Artifacts**.

> Si Windows SmartScreen muestra una advertencia, elija *Más información → Ejecutar de todas formas* (el ejecutable no está firmado digitalmente).

### Opción B — Con Python 3.8 o superior

```bash
git clone https://github.com/Kristianpng-90/Sistema-de-Calificaci-n-.git
cd Sistema-de-Calificaci-n-
python main.py
```

No requiere librerías externas.

## Pruebas

```bash
python -m unittest discover -s tests -t . -v
```

21 casos de prueba (CP01–CP21) cubren validaciones, cálculos, aprobación en los límites (3.0 exacto y 2.95) y persistencia.

## Generar el ejecutable

| Sistema | Comando | Resultado |
|---------|---------|-----------|
| Windows | `build_windows.bat` | `dist\SistemaCalificaciones.exe` |
| Linux   | `./build_linux.sh`  | `dist/linux/SistemaCalificaciones` |
| GitHub  | Automático al hacer *push* o publicar una versión | **Releases** y **Actions → Artifacts** |

## Estructura del proyecto

```
Sistema-de-Calificaci-n-/
├── main.py                     Punto de entrada
├── calificaciones/
│   ├── modelos.py              Clases Nota y Estudiante + validaciones
│   ├── calculos.py             Promedios, estado de aprobación, resumen del curso
│   ├── repositorio.py          Guardado y lectura en JSON
│   └── consola.py              Menú e interacción con el usuario
├── tests/test_calificaciones.py  Pruebas unitarias
├── docs/DOCUMENTO_TECNICO.md   Documentación técnica
├── dist/linux/                 Ejecutable para Linux
├── build_windows.bat / build_linux.sh
└── .github/workflows/build.yml Pruebas y ejecutable automáticos
```

## Ejemplo de uso

```
================================================================
  María Pérez  (código 1001)
================================================================
  #  Descripción                  Nota   Peso %   Aporte
  1  Parcial 1                    4.20     30.0     1.26
  2  Parcial 2                    3.80     30.0     1.14
  3  Examen final                 4.50     40.0     1.80
  ------------------------------------------------------
  Porcentaje evaluado ..........: 100.0 %
  Promedio simple ..............: 4.17
  Promedio ponderado ...........: 4.20
  Nota acumulada (sobre 100 %) .: 4.20
  Estado .......................: APROBADO
```

Más detalle en [docs/DOCUMENTO_TECNICO.md](docs/DOCUMENTO_TECNICO.md).
