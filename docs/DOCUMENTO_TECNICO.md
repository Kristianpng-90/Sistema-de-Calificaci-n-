# Documento técnico — Sistema de Calificaciones

**Versión:** 1.0.0  
**Autor:** Cristian Camilo Girata Ravelo  
**Institución:** Universidad Manuela Beltrán — Ingeniería de Software  
**Lenguaje:** Python 3.8+ (solo biblioteca estándar)

---

## 1. Propósito

Sistema de consola que permite al docente registrar las notas de sus estudiantes, calcular promedios (simple y ponderado) y determinar automáticamente si cada estudiante aprueba, reprueba o aún tiene evaluaciones pendientes.

## 2. Requerimientos

### 2.1 Funcionales

| ID | Requerimiento |
|----|---------------|
| RF01 | Registrar estudiantes con código único y nombre. |
| RF02 | Registrar notas con descripción, valor (0.0–5.0) y porcentaje. |
| RF03 | Impedir que la suma de porcentajes de un estudiante supere el 100 %. |
| RF04 | Calcular el promedio simple y el promedio ponderado. |
| RF05 | Determinar el estado: APROBADO (≥ 3.0), REPROBADO, INCOMPLETO o SIN NOTAS. |
| RF06 | Calcular la nota necesaria en el porcentaje restante para aprobar. |
| RF07 | Generar un reporte del curso con estadísticas. |
| RF08 | Eliminar notas y estudiantes. |
| RF09 | Guardar los datos de forma permanente. |

### 2.2 No funcionales

| ID | Requerimiento |
|----|---------------|
| RNF01 | Funcionar sin dependencias externas (solo Python estándar). |
| RNF02 | Distribuirse como ejecutable independiente. |
| RNF03 | No cerrarse ante datos inválidos; mostrar un mensaje y volver a pedir el dato. |
| RNF04 | No dañar los datos si el programa se cierra durante el guardado (escritura atómica). |

## 3. Arquitectura

Se usa una **arquitectura en capas**: cada capa solo conoce a la de abajo.

```
┌──────────────────────────────┐
│  consola.py  (presentación)  │  menú, lectura de teclado, impresión
├──────────────────────────────┤
│  calculos.py (negocio)       │  promedios, estado, resumen  ← funciones puras
├──────────────────────────────┤
│  modelos.py  (dominio)       │  Nota, Estudiante, validaciones
├──────────────────────────────┤
│  repositorio.py (datos)      │  lectura/escritura en calificaciones.json
└──────────────────────────────┘
```

Ventaja: la lógica de cálculo se prueba sin teclado ni archivos, y la interfaz podría cambiarse (por ejemplo, a una ventana gráfica) sin tocar los cálculos.

### 3.1 Diagrama de clases

```
┌────────────────────────┐ 1      * ┌──────────────────────┐
│      Estudiante        │◆────────│        Nota          │
├────────────────────────┤          ├──────────────────────┤
│ codigo: str            │          │ descripcion: str     │
│ nombre: str            │          │ valor: float (0–5)   │
│ notas: list[Nota]      │          │ peso: float (0–100]  │
├────────────────────────┤          ├──────────────────────┤
│ peso_acumulado         │          │ a_dict()             │
│ agregar_nota(nota)     │          │ desde_dict(d)        │
│ eliminar_nota(i)       │          └──────────────────────┘
│ a_dict() / desde_dict()│
└───────────┬────────────┘
            │ * gestionados por 1
┌───────────▼────────────┐
│ RepositorioEstudiantes │
├────────────────────────┤
│ ruta: str              │
├────────────────────────┤
│ listar() buscar()      │
│ agregar() eliminar()   │
│ guardar() cargar()     │
└────────────────────────┘
```

## 4. Algoritmo principal

### 4.1 Pseudocódigo — determinar el estado

```
FUNCIÓN estado(notas)
    SI notas está vacía ENTONCES
        RETORNAR "SIN NOTAS"
    pesoTotal ← SUMA(nota.peso PARA CADA nota)
    SI pesoTotal < 100 ENTONCES
        RETORNAR "INCOMPLETO"
    promedio ← SUMA(nota.valor × nota.peso) / pesoTotal
    SI promedio ≥ 3.0 ENTONCES
        RETORNAR "APROBADO"
    SINO
        RETORNAR "REPROBADO"
FIN FUNCIÓN
```

### 4.2 Pseudocódigo — nota necesaria para aprobar

```
FUNCIÓN notaNecesaria(notas)
    restante ← 100 − SUMA(nota.peso)
    SI restante ≤ 0 ENTONCES RETORNAR NULO
    acumulada ← SUMA(nota.valor × nota.peso) / 100
    RETORNAR MÁXIMO(0, (3.0 − acumulada) × 100 / restante)
FIN FUNCIÓN
```

### 4.3 Diagrama de flujo — registrar una nota

```
        ( Inicio )
            │
   [Pedir código estudiante]
            │
     ◇ ¿Existe? ──No──► [Mensaje de error] ──► ( Fin )
            │Sí
     ◇ ¿Peso acumulado < 100? ──No──► [“Ya tiene el 100 %”] ──► ( Fin )
            │Sí
   [Pedir descripción]
            │
   [Pedir nota] ◄──────────┐
            │              │
     ◇ ¿0 ≤ nota ≤ 5? ──No─┘
            │Sí
   [Pedir porcentaje] ◄────┐
            │              │
     ◇ ¿0 < % ≤ disponible? ─No─┘
            │Sí
   [Agregar nota y guardar JSON]
            │
   [Mostrar promedio y estado]
            │
        ( Fin )
```

## 5. Fórmulas

| Concepto | Fórmula |
|----------|---------|
| Promedio simple | Σ valorᵢ / n |
| Promedio ponderado | Σ(valorᵢ × pesoᵢ) / Σ pesoᵢ |
| Nota acumulada | Σ(valorᵢ × pesoᵢ) / 100 |
| Nota necesaria | (3.0 − acumulada) × 100 / (100 − Σ pesoᵢ) |

Todos los resultados se redondean a dos decimales.

## 6. Persistencia

Archivo `calificaciones.json`, ubicado junto al ejecutable (o junto a `main.py`):

```json
[
  {
    "codigo": "1001",
    "nombre": "María Pérez",
    "notas": [
      {"descripcion": "Parcial 1", "valor": 4.2, "peso": 30.0}
    ]
  }
]
```

Se escribe primero en `calificaciones.json.tmp` y luego se reemplaza el original (`os.replace`), así un cierre inesperado no deja el archivo a medias. Si el archivo está dañado, el programa avisa en lugar de sobrescribirlo.

## 7. Manejo de errores

| Situación | Respuesta del sistema |
|-----------|-----------------------|
| Texto donde va un número | “Escriba un número válido” y vuelve a pedir |
| Nota fuera de 0.0–5.0 | “El valor debe estar entre 0.0 y 5.0” y vuelve a pedir |
| Porcentaje que excede el disponible | Indica el máximo y vuelve a pedir |
| Código duplicado | “Ya existe un estudiante con el código …” |
| Estudiante inexistente | “No existe un estudiante con ese código” |
| JSON dañado | Mensaje de error; no borra los datos |
| Ctrl+C durante una operación | Cancela la operación y vuelve al menú |

Todas las validaciones de dominio lanzan `DatoInvalidoError`, que la consola captura y muestra.

## 8. Pruebas

Se usa `unittest` (biblioteca estándar). Ejecutar: `python -m unittest discover -s tests -t . -v`

| Grupo | Casos | Qué valida |
|-------|-------|------------|
| Validación | CP01–CP07 | Rangos de nota y porcentaje, límites 0.0 y 5.0, texto no numérico, tope de 100 %, nombre vacío |
| Cálculos | CP08–CP12 | Promedio simple y ponderado, lista vacía, nota acumulada, nota necesaria |
| Aprobación | CP13–CP18 | Aprueba, reprueba, 3.0 exacto aprueba, 2.95 reprueba, incompleto, resumen del curso |
| Persistencia | CP19–CP21 | Guardar y recargar, código duplicado, archivo dañado |

**Resultado:** 21/21 pruebas superadas. El flujo de GitHub Actions las ejecuta en Windows y Linux en cada *push*.

## 9. Generación del ejecutable

Se usa **PyInstaller** en modo `--onefile`, que empaqueta el intérprete de Python y el código en un solo archivo.

- Windows: `build_windows.bat` → `dist\SistemaCalificaciones.exe`
- Linux: `build_linux.sh` → `dist/linux/SistemaCalificaciones`
- GitHub Actions (`.github/workflows/build.yml`): compila para ambos sistemas y publica el ejecutable en *Artifacts*; al crear una etiqueta `v1.0.0` lo publica en *Releases*.

## 10. Posibles mejoras

- Interfaz gráfica (Tkinter) reutilizando las capas de negocio y datos.
- Exportar el reporte a CSV o Excel.
- Configurar la nota mínima aprobatoria y la escala desde el menú.
- Manejar varias asignaturas por estudiante.
