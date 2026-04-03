@echo off
title GemStone IV - Creature Content Validation
echo Validating creature Lua, Adventurer's Guild refs, and low-level ability coverage...
echo.
cd /d "%~dp0"
set "GEMSTONE_ROOT=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 tools\validate_creature_content.py
) else (
    python tools\validate_creature_content.py
)
echo.
pause
