@echo off
setlocal
cd /d "%~dp0\.."

echo ========================================================
echo    ARGOS - INSTALADOR DO AMBIENTE VIRTUAL (VENV)
echo ========================================================

REM 1. Criando ambiente virtual na raiz do projeto
if not exist ".venv" (
    echo [1/3] Criando ambiente virtual .venv na raiz...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERRO] Falha ao criar a venv. Verifique se o Python esta instalado.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente .venv ja existe na raiz.
)

REM 2. Instalando dependencias da raiz
echo [2/3] Instalando dependencias do requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\pip.exe" install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

REM 3. Instalando o navegador Chromium do Playwright (opcional se tiver Chrome/Edge)
echo [3/3] Verificando navegador para o Playwright...
".venv\Scripts\playwright.exe" install chromium
if %ERRORLEVEL% neq 0 (
    echo [AVISO] Nao foi possivel baixar o Chromium do Playwright.
    echo Nao se preocupe: o robo usara automaticamente o Google Chrome ou Edge do seu Windows!
)

echo.
echo ========================================================
echo [SUCESSO] Ambiente configurado e pronto para uso!
echo ========================================================
pause
endlocal
