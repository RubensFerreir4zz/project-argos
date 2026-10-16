@echo off
setlocal
cd /d "%~dp0"

REM Localiza o executavel do python na raiz (.venv)
set "PYTHON_PATH="
if exist ".venv\Scripts\python.exe" set "PYTHON_PATH=.venv\Scripts\python.exe"

if "%PYTHON_PATH%"=="" (
    echo ========================================================
    echo [ERRO] Ambiente virtual (.venv) nao encontrado!
    echo Execute setup\setup_ambiente.bat para preparar o ambiente.
    echo ========================================================
    pause
    exit /b 1
)

echo [INFO] Iniciando Argos - Sistema de Checking de Midia...
"%PYTHON_PATH%" "scripts\save_print.py"

endlocal
