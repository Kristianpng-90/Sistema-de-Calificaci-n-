#!/usr/bin/env bash
# Genera dist/linux/SistemaCalificaciones en Linux
set -e
python3 -m unittest discover -s tests -t .
python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller --onefile --console --clean --name SistemaCalificaciones \
  --distpath dist/linux main.py
echo "Listo: dist/linux/SistemaCalificaciones"
