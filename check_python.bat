@echo off
python -c "import sys; print(sys.executable)" > N:\GemStoneIVServer\logs\python_info.txt 2>&1
python -c "import mysql.connector; print('mysql OK')" >> N:\GemStoneIVServer\logs\python_info.txt 2>&1
python -c "import bcrypt; print('bcrypt OK')" >> N:\GemStoneIVServer\logs\python_info.txt 2>&1
python -m pip install mysql-connector-python bcrypt >> N:\GemStoneIVServer\logs\python_info.txt 2>&1
