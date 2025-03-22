@echo off

REM Path to your Conda executable (adjust if necessary)
REM set CONDA_EXE=C:\Users\YourUsername\Anaconda3\Scripts\activate.bat

REM Path to your Conda environment
set current_dir=%~dp0

set CONDA_ENV_PATH=%current_dir%env
REM Path to your Python script
set SCRIPT_PATH_0=src\app\change_ip.py
set SCRIPT_PATH_1=src\app\main.py
set SCRIPT_PATH_2=src\app\main_backend.py
set SCRIPT_PATH_3=src\app\main_update.py
set SCRIPT_PATH_4=src\app\main_status.py
set SCRIPT_PATH_5=src\app\main_all.py

REM Open first terminal
start "Change ip" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_0%""
timeout /t 2 /nobreak

start "main.py" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_1%""

REM Open second terminal
start "main_backend.py" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_2%""

REM Open third terminal
start "main_update.py" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_3%""

REM Open fourth terminal
start "main_status" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_4%""

REM Open fifth terminal
start "main_all" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_5%""
