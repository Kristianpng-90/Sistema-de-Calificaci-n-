@echo off
REM Genera dist\SistemaCalificaciones.exe en Windows
echo Ejecutando pruebas...
python -m unittest discover -s tests -t . || goto :error
echo Instalando PyInstaller...
python -m pip install --upgrade pyinstaller || goto :error
echo Compilando...
python -m PyInstaller --onefile --console --clean --name SistemaCalificaciones main.py || goto :error
echo.
echo Listo: dist\SistemaCalificaciones.exe
pause
exit /b 0
:error
echo Ocurrio un error.
pause
exit /b 1
