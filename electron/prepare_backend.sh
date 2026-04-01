#!/usr/bin/env bash
# Preparar el directorio backend para Electron
# Copia la aplicación Flask al directorio electron/backend

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "Preparando backend para Electron..."

# Crear directorio backend
mkdir -p "$BACKEND_DIR"

# Copiar archivos de la aplicación Flask
cp -r "$PROJECT_ROOT/app" "$BACKEND_DIR/"
cp "$PROJECT_ROOT/run.py" "$BACKEND_DIR/"
cp "$PROJECT_ROOT/config.py" "$BACKEND_DIR/"
cp "$PROJECT_ROOT/requirements.txt" "$BACKEND_DIR/"

# Copiar .env si existe
if [ -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env" "$BACKEND_DIR/"
fi

# Crear venv en backend si no existe
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv "$BACKEND_DIR/venv"
    source "$BACKEND_DIR/venv/bin/activate"
    pip install -r "$BACKEND_DIR/requirements.txt" > /dev/null 2>&1
    echo "Dependencias instaladas."
fi

echo "Backend listo en: $BACKEND_DIR"
echo ""
echo "Para iniciar la app Electron:"
echo "  cd $SCRIPT_DIR"
echo "  npm install"
echo "  npm start"
