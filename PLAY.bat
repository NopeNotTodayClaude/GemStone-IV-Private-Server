@echo off
title GemStone IV - Play
cd /d "%~dp0"
set "GEMSTONE_ROOT=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 PLAY.py
) else (
    python PLAY.py
)
pause
