@echo off
REM Preparar el directorio backend para Electron en Windows

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set BACKEND_DIR=%SCRIPT_DIR%backend

echo Preparando backend para Electron...

REM Crear directorio backend
if not exist "%BACKEND_DIR%" mkdir "%BACKEND_DIR%"

REM Copiar archivos de la aplicacion Flask
xcopy /E /I /Y "%PROJECT_ROOT%\app" "%BACKEND_DIR%\app"
copy /Y "%PROJECT_ROOT%\run.py" "%BACKEND_DIR%\run.py"
copy /Y "%PROJECT_ROOT%\config.py" "%BACKEND_DIR%\config.py"
copy /Y "%PROJECT_ROOT%\requirements.txt" "%BACKEND_DIR%\requirements.txt"

REM Copiar .env si existe
if exist "%PROJECT_ROOT%\.env" copy /Y "%PROJECT_ROOT%\.env" "%BACKEND_DIR%\.env"

REM Crear venv en backend si no existe
if not exist "%BACKEND_DIR%\venv" (
    echo Creando entorno virtual...
    python -m venv "%BACKEND_DIR%\venv"
    call "%BACKEND_DIR%\venv\Scripts\activate.bat"
    pip install -r "%BACKEND_DIR%\requirements.txt" >nul 2>&1
    echo Dependencias instaladas.
)

echo.
echo Backend listo en: %BACKEND_DIR%
echo.
echo Para iniciar la app Electron:
echo   cd %SCRIPT_DIR%
echo   npm install
echo   npm start
pause
