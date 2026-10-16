@echo off
setlocal
cd /d "%~dp0\.."

set "NOME_TAREFA=Argos_Checking_98FM"
set "CAMINHO_BAT=%CD%\executar_robo.bat"

echo ========================================================
echo    ARGOS - AGENDADOR DE CHECKING DE MIDIA (WINDOWS)
echo ========================================================
echo Script Alvo: %CAMINHO_BAT%
echo Nome da Tarefa: %NOME_TAREFA%
echo ========================================================
echo.
echo Escolha uma opcao:
echo   [1] Agendar diariamente as 09:00
echo   [2] Agendar em horario personalizado
echo   [3] Consultar status da tarefa
echo   [4] Remover tarefa agendada
echo   [5] Sair
echo.

set /p OPCAO="Digite a opcao desejada (1-5): "

if "%OPCAO%"=="1" goto AGENDAR_PADRAO
if "%OPCAO%"=="2" goto AGENDAR_PERSONALIZADO
if "%OPCAO%"=="3" goto STATUS
if "%OPCAO%"=="4" goto REMOVER
if "%OPCAO%"=="5" goto FIM
goto FIM

:AGENDAR_PADRAO
set "HORARIO=09:00"
goto CRIAR_TAREFA

:AGENDAR_PERSONALIZADO
set /p HORARIO="Digite o horario desejado no formato HH:MM (ex: 14:30): "
goto CRIAR_TAREFA

:CRIAR_TAREFA
echo.
echo Criando tarefa no Agendador do Windows com sessao interativa (/it)...
schtasks /create /tn "%NOME_TAREFA%" /tr "\"%CAMINHO_BAT%\"" /sc DAILY /st %HORARIO% /it /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCESSO] Tarefa '%NOME_TAREFA%' agendada com sucesso para todos os dias as %HORARIO%!
    echo A tarefa foi configurada para rodar com o usuario logado (necessario para o print de tela).
) else (
    echo.
    echo [ERRO] Falha ao criar tarefa. Tente executar este .bat como Administrador se necessario.
)
goto PAUSA

:STATUS
echo.
echo Consultando tarefa no Agendador...
schtasks /query /tn "%NOME_TAREFA%" /v /fo LIST
goto PAUSA

:REMOVER
echo.
echo Removendo tarefa agendada...
schtasks /delete /tn "%NOME_TAREFA%" /f
if %ERRORLEVEL% equ 0 (
    echo [SUCESSO] Tarefa '%NOME_TAREFA%' removida com sucesso.
) else (
    echo [INFO] Tarefa nao encontrada ou erro ao remover.
)
goto PAUSA

:PAUSA
echo.
pause

:FIM
endlocal
