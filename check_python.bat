@echo off
cd /d "%~dp0"
set "GEMSTONE_ROOT=%~dp0"
set "PYINFO=%~dp0logs\python_info.txt"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 -c "import sys; print(sys.executable)" > "%PYINFO%" 2>&1
    py -3 -c "import mysql.connector; print('mysql OK')" >> "%PYINFO%" 2>&1
    py -3 -c "import bcrypt; print('bcrypt OK')" >> "%PYINFO%" 2>&1
    py -3 -m pip install mysql-connector-python bcrypt >> "%PYINFO%" 2>&1
) else (
    python -c "import sys; print(sys.executable)" > "%PYINFO%" 2>&1
    python -c "import mysql.connector; print('mysql OK')" >> "%PYINFO%" 2>&1
    python -c "import bcrypt; print('bcrypt OK')" >> "%PYINFO%" 2>&1
    python -m pip install mysql-connector-python bcrypt >> "%PYINFO%" 2>&1
)
