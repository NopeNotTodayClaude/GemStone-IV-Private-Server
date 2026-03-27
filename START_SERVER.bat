@echo off
title GemStone IV - Server
echo Starting GemStone IV Private Server...
echo.
cd /d "%~dp0"
"C:\Users\unrea\AppData\Local\Python\pythoncore-3.14-64\python.exe" server\main.py
pause
