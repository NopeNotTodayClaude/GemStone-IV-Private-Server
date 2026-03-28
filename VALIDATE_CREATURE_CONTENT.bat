@echo off
title GemStone IV - Creature Content Validation
echo Validating creature Lua, Adventurer's Guild refs, and low-level ability coverage...
echo.
cd /d "%~dp0"
"C:\Users\unrea\AppData\Local\Python\pythoncore-3.14-64\python.exe" tools\validate_creature_content.py
echo.
pause
