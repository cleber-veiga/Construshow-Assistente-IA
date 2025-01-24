@echo off
setlocal

:: Solicita o nome de usuário
set /p username="Digite o nome de usuário (formato DOMAIN\username): "

:: Solicita a senha usando PowerShell para ocultar a entrada
echo password:
for /f "delims=" %%P in ('powershell -Command "Read-Host -AsSecureString | ConvertFrom-SecureString"') do set secure_password=%%P
set password=^%secure_password%

:: Nome do Serviço
set servicename=ViasoftServerConstruShowIA

:: Caminhos
set apppath=D:\Viasoft\Server\ConstruShow\ViasoftServerConstruShowIA.exe
set appdir=D:\Viasoft\Server\ConstruShow
set logfile=D:\Viasoft\Server\ConstruShow\Log\ViasoftServerConstruShowIA.log

:: Instalação do Serviço
nssm install %servicename% "%apppath%"
nssm set %servicename% AppDirectory "%appdir%"
nssm set %servicename% DisplayName "ViasoftServerConstruShowIA"
nssm set %servicename% Description "ViasoftServerConstruShowIA"
nssm set %servicename% Start SERVICE_AUTO_START

:: Configuração de Logon
nssm set %servicename% ObjectName "%username%" "%password%"

:: Configuração de Exit Actions
nssm set %servicename% AppExit 1000
nssm set %servicename% AppRestartDelay 10000

:: Configuração de I/O
nssm set %servicename% AppStdout "%logfile%"
nssm set %servicename% AppStderr "%logfile%"

:: Inicia o Serviço
nssm start %servicename%

echo.
echo Serviço "%servicename%" instalado e iniciado com sucesso!
pause
