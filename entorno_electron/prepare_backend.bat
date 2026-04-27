@echo off
REM Preparar el directorio backend para entorno_electron en Windows

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
copy /Y "%PROJECT_ROOT%\backend.spec" "%BACKEND_DIR%\backend.spec"

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

REM --- Crear estructura de datos persistentes junto al ejecutable ---
REM Este directorio data/ es donde el backend busca .env, instance/ y logs/
set DIST_BACKEND_DIR=%BACKEND_DIR%\dist\inventario_backend
if exist "%DIST_BACKEND_DIR%" (
    set DATA_DIR=%DIST_BACKEND_DIR%\data
    echo Creando estructura de datos persistentes en: %DIST_BACKEND_DIR%\data
    if not exist "%DIST_BACKEND_DIR%\data\instance" mkdir "%DIST_BACKEND_DIR%\data\instance"
    if not exist "%DIST_BACKEND_DIR%\data\logs" mkdir "%DIST_BACKEND_DIR%\data\logs"

    if exist "%BACKEND_DIR%\.env" (
        copy /Y "%BACKEND_DIR%\.env" "%DIST_BACKEND_DIR%\data\.env" >nul
        echo .env copiado a la carpeta de datos.
    ) else (
        echo ADVERTENCIA: No se encontro .env en %BACKEND_DIR%. Deberas crearlo manualmente.
    )
) else (
    echo NOTA: El directorio dist/ aun no existe. Ejecuta PyInstaller y vuelve a correr esto.
)
echo.
echo Para iniciar la app Electron:
echo   cd %SCRIPT_DIR%
echo   npm install
echo   npm start
pause
