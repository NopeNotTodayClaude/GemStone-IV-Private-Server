@echo off
title GemStone IV - Server
echo Starting GemStone IV Private Server...
echo.
cd /d "%~dp0"
set "GEMSTONE_ROOT=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 server\main.py
) else (
    python server\main.py
)
pause
