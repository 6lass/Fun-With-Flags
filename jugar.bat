@echo off
title Guess the Flag - Juego de Escritorio
echo Iniciando Guess the Flag en Python (Tkinter + Pillow)...
.venv\Scripts\python.exe game.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error critico al ejecutar el juego en el entorno virtual.
    pause
)
