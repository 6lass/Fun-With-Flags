@echo off
title Guess the Flag - Juego de Escritorio
echo Iniciando Guess the Flag en Python (Tkinter + Pillow)...

:: Check if virtual environment exists
if exist .venv goto run_game

echo.
echo [INFO] No se encontro el entorno virtual (.venv).
echo [INFO] Creando un entorno virtual nuevo e instalando Pillow...

python -m venv .venv
if errorlevel 1 goto fallback_global

echo [INFO] Instalando Pillow en el entorno virtual...
.venv\Scripts\pip install pillow
if errorlevel 1 goto install_failed

echo [INFO] Entorno virtual preparado con exito.
echo.

:run_game
.venv\Scripts\python.exe game.py
if errorlevel 1 goto run_failed
goto end

:fallback_global
echo.
echo [ADVERTENCIA] No se pudo crear el entorno virtual.
echo [INFO] Intentando ejecutar con el Python global...
python game.py
if errorlevel 1 goto run_failed
goto end

:install_failed
echo.
echo [ERROR] Error instalando la libreria Pillow.
pause
exit /b 1

:run_failed
echo.
echo [ERROR] Ocurrio un error critico al ejecutar el juego.
pause
exit /b 1

:end
