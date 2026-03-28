@echo off
setlocal
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0EXPORT_SANITIZED_DB.ps1"
if errorlevel 1 (
    echo.
    echo Export failed.
    pause
    exit /b 1
)

echo.
echo USETHIS.sql updated successfully.
pause
