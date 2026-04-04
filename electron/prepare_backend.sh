#!/usr/bin/env bash
# Preparar el directorio backend para Electron
# Copia la aplicación Flask al directorio electron/backend e instala dependencias

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

# 2. Preparar dependencias para Windows (Portable) - Proceso Cross-platform
if [ -d "$PYTHON_WIN_DIR" ]; then
    echo "Instalando dependencias para Windows en python-win/site-packages..."
    mkdir -p "$PYTHON_WIN_DIR/site-packages"
    
    # Usamos el pip del venv recién creado para descargar binarios de Windows
    source "$BACKEND_DIR/venv/bin/activate"
    
    echo "Instalando dependencias para Windows..."
    
    # 1. Instalar la mayoría desde binarios oficiales para Windows
    # Usamos --only-binary=:all: para asegurar que NO intentamos compilar para Linux
    # Esto descargará e instalará directamente los .whl adecuados (incluyendo pure-python como 'any')
    python -m pip install \
        --target "$PYTHON_WIN_DIR/site-packages" \
        --platform win_amd64 \
        --only-binary=:all: \
        --no-compile \
        -r "$BACKEND_DIR/requirements.txt" || echo "  Algunos paquetes no tienen binarios, se instalarán por separado..."
    
    # 2. Instalar individualmente los que sabemos que son problemáticos o solo fuente
    # Como Flask-APScheduler. Al no usar --platform, pip lo bajará como fuente
    # Y lo "instalará" (descomprimirá) en el destino. Al ser pure-python, funciona.
    echo "Instalando paquetes fuente (pure-python)..."
    python -m pip install \
        --target "$PYTHON_WIN_DIR/site-packages" \
        --no-deps \
        --no-compile \
        Flask-APScheduler
    
    deactivate
    
    echo "Dependencias de Windows instaladas con éxito."
fi

echo "Backend preparado con éxito en: $BACKEND_DIR"
