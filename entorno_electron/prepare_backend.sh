#!/usr/bin/env bash
# Preparar el directorio backend para Electron
# Copia la aplicación Flask al directorio entorno_electron/backend e instala dependencias

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$SCRIPT_DIR/backend"
PYTHON_WIN_DIR="$BACKEND_DIR/python-win"

echo "Preparando backend para Electron..."

# Crear directorio backend si no existe
mkdir -p "$BACKEND_DIR"

# Función para copiar si el origen existe
copy_if_exists() {
    local src="$1"
    local dest="$2"
    if [ -e "$src" ]; then
        echo "Copiando $(basename "$src")..."
        cp -r "$src" "$dest"
    else
        if [ -e "$dest/$(basename "$src")" ]; then
            echo "$(basename "$src") ya existe en el destino, saltando copia."
        else
            echo "ADVERTENCIA: No se encontró $src y no existe en el destino."
        fi
    fi
}

# Intentar copiar archivos de la aplicación Flask desde el root del proyecto
copy_if_exists "$PROJECT_ROOT/app" "$BACKEND_DIR/"
copy_if_exists "$PROJECT_ROOT/run.py" "$BACKEND_DIR/"
copy_if_exists "$PROJECT_ROOT/config.py" "$BACKEND_DIR/"
copy_if_exists "$PROJECT_ROOT/requirements.txt" "$BACKEND_DIR/"
copy_if_exists "$PROJECT_ROOT/backend.spec" "$BACKEND_DIR/"

# Copiar .env si existe
if [ -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env" "$BACKEND_DIR/"
fi

# 1. Preparar entorno local (Linux) para desarrollo
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "Creando entorno virtual local (Linux)..."
    python3 -m venv "$BACKEND_DIR/venv"
    source "$BACKEND_DIR/venv/bin/activate"
    pip install -r "$BACKEND_DIR/requirements.txt" > /dev/null 2>&1
    echo "Dependencias locales instaladas."
fi



echo "Backend preparado con éxito en: $BACKEND_DIR"

# --- Crear estructura de datos persistentes junto al ejecutable ---
# Este directorio data/ es donde el backend busca .env, instance/ y logs/
# cuando se ejecuta desde el ejecutable empaquetado con PyInstaller.
DIST_BACKEND_DIR="$BACKEND_DIR/dist/inventario_backend"
if [ -d "$DIST_BACKEND_DIR" ]; then
    DATA_DIR="$DIST_BACKEND_DIR/data"
    echo "Creando estructura de datos persistentes en: $DATA_DIR"
    mkdir -p "$DATA_DIR/instance"
    mkdir -p "$DATA_DIR/logs"

    # Copiar .env al directorio de datos si existe
    if [ -f "$BACKEND_DIR/.env" ]; then
        cp "$BACKEND_DIR/.env" "$DATA_DIR/"
        echo ".env copiado a $DATA_DIR/"
    else
        echo "ADVERTENCIA: No se encontró .env en $BACKEND_DIR. Deberás crearlo manualmente en $DATA_DIR/"
    fi
else
    echo "NOTA: El directorio dist/ aún no existe. Ejecuta PyInstaller primero y luego vuelve a correr este script."
fi
