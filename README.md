# Sistema de Inventario

Aplicación de escritorio para gestión de inventario de productos de telefonía (pantallas, baterías, fundas, cables, cargadores), modelos de teléfonos, compatibilidades, autenticación, alertas por email y exportación a Excel.

## Arquitectura

La aplicación utiliza una arquitectura de dos capas: **Electron** como shell de escritorio y **Flask** como backend web que sirve la interfaz completa.

```
┌─────────────────────────────────────────────────────┐
│                    ELECTRON MAIN                     │
│                                                      │
│  ┌──────────┐   ┌───────────┐   ┌───────────────┐   │
│  │startFlask│   │startTunnel│   │ createWindow  │   │
│  │(child)   │   │(child)    │   │  → :5000      │   │
│  └────┬─────┘   └─────┬─────┘   └───────┬───────┘   │
│       │               │                 │            │
│       ▼               ▼                 │            │
│  ┌──────────┐   ┌───────────┐           │            │
│  │Python /  │   │cloudflared│           │            │
│  │PyInstaller│  │ binary    │           │            │
│  └────┬─────┘   └─────┬─────┘           │            │
│       │               │                  │            │
│       └───────────────┘                  │            │
│               │                          │            │
│               ▼                          │            │
│  ┌───────────────────────────────────────┘            │
│  │  IPC: tunnel-url → preload → window.electronAPI   │
│  └───────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   FLASK BACKEND (:5000)              │
│                                                      │
│  Views (Blueprints) → Controllers → Services        │
│                        → Models → SQLite             │
│                                                      │
│  APScheduler: alertas, informes, backup             │
└─────────────────────────────────────────────────────┘
```

### Flujo de arranque

1. **Electron** inicia y ejecuta `startApp()`
2. Lanza **Flask** como proceso hijo (`python run.py` en dev, binario PyInstaller en prod)
3. Espera ~6 segundos a que Flask esté listo en `http://127.0.0.1:5000`
4. Inicia **Cloudflare Tunnel** como proceso hijo opcional (acceso remoto)
5. Crea **BrowserWindow** cargando la URL de Flask
6. Si Flask no está listo, reintenta automáticamente cada 1 segundo

### Integración Electron ↔ Flask

| Canal | Dirección | Propósito |
|-------|-----------|-----------|
| `http://127.0.0.1:5000` | BrowserWindow → Flask | Toda la UI (Jinja2 templates) |
| `POST /api/tunnel/register` | Electron → Flask | Registrar URL del túnel |
| `ipcRenderer` / `contextBridge` | Main → Renderer | Enviar URL del túnel a la UI |
| `openExternal` | Renderer → Main | Abrir URLs en navegador del sistema |

**Electron es un shell delgado**: no contiene lógica de negocio. Solo gestiona procesos hijos (Flask, cloudflared), la ventana de la aplicación y el puente IPC para la URL del túnel.

### Modo desarrollo vs producción

| Aspecto | Desarrollo | Producción |
|---------|-----------|------------|
| Backend | `venv/bin/python run.py` | Binario PyInstaller empaquetado |
| Cloudflared | `resources/binaries/` | `process.resourcesPath/binaries/` |
| Base de datos | `instance/inventario.db` | Misma ruta relativa al binario |
| SECRET_KEY | Obligatorio (validación estricta) | Fallback con advertencia si falta |

## Estructura del proyecto

```
inventario_app/
└── electron/
    ├── main.js                  # Proceso principal Electron
    ├── preload.js               # Context bridge (IPC seguro)
    ├── package.json             # Dependencias y config de electron-builder
    ├── prepare_backend.sh       # Script Linux: copia Flask + crea venv
    ├── prepare_backend.bat      # Script Windows: copia Flask + crea venv
    ├── resources/               # Iconos, binario cloudflared
    └── backend/                 # Aplicación Flask
        ├── app/
        │   ├── __init__.py      # Application factory (create_app)
        │   ├── models.py        # Modelos SQLAlchemy
        │   ├── forms.py         # Formularios WTForms
        │   ├── controllers/     # Lógica de negocio (delgada)
        │   ├── services/        # Capa de servicios (email, auditoría, túnel)
        │   ├── views/           # Blueprints Flask (rutas)
        │   ├── templates/       # Templates Jinja2
        │   └── static/          # CSS, JS, imágenes
        ├── tests/               # Suite de pruebas (pytest)
        ├── config.py            # Configuración (dev/prod, PyInstaller detection)
        ├── run.py               # Punto de entrada Flask
        └── requirements.txt     # Dependencias Python
```

## Modelos de datos

```
Producto ────< Compatibilidad >──── ModeloTelefono
   │
   ├── nombre, categoría, marca, proveedor
   ├── cantidad_stock, stock_minimo
   ├── precio_compra_bs/usd, precio_venta_bs/usd, precio_mayor_bs/usd
   └── ultima_notificacion

Usuario (Flask-Login UserMixin)
ConfiguracionSistema (clave-valor para jobs, email, tasa de cambio)
```

## Tareas programadas (APScheduler)

| Tarea | Hora | Función |
|-------|------|---------|
| Alerta de stock bajo | 08:00 | Envía email con productos bajo mínimo |
| Informe matutino | 07:00 | Reporte diario de inventario |
| Informe vespertino | 19:00 | Reporte de cambios del día |
| Backup de BD | 21:00 | Copia de seguridad SQLite |

Cada tarea se puede activar/desactivar desde la configuración del sistema.

## Instalación

### Requisitos

- Node.js 16+
- Python 3.8+

### Backend Flask

```bash
cd electron/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Electron

```bash
cd electron
npm install
npm start
```

### Scripts de preparación

Los scripts `prepare_backend.sh` (Linux) y `prepare_backend.bat` (Windows) automatizan la copia del código Flask desde el directorio raíz hacia `electron/backend/` y la creación del entorno virtual con dependencias.

## Construcción de distribuciones

```bash
cd electron
npm run build:win     # Windows (NSIS + portable)
npm run build:linux   # Linux (AppImage)
npm run build:mac     # macOS
```

El empaquetado incluye: binario PyInstaller del backend, binario cloudflared, iconos y recursos estáticos.

## Pruebas

```bash
cd electron/backend
pytest                                    # Todas las pruebas
pytest tests/test_controllers/test_producto.py  # Un archivo
pytest tests/test_controllers/test_producto.py::TestCrear::test_crear_con_modelos  # Una prueba
pytest --cov=app --cov-report=term-missing  # Cobertura
```

## Seguridad

- **Flask-Talisman**: Headers CSP y HTTPS forzado
- **Flask-Login**: Autenticación con sesiones seguras
- **Flask-WTF**: Protección CSRF en todos los formularios
- **Auditoría**: Registro rotativo de eventos de seguridad (login, cambios críticos)
- **Electron**: `contextIsolation: true`, `nodeIntegration: false`
- **Credenciales por defecto**: `admin` / `admin123` (cambiar inmediatamente)

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Shell desktop | Electron 22, electron-builder 23 |
| Backend web | Flask 3, Jinja2 |
| Base de datos | SQLAlchemy, SQLite |
| Formularios | WTForms, Flask-WTF |
| Autenticación | Flask-Login, Werkzeug |
| Email | Flask-Mail |
| Tareas programadas | Flask-APScheduler |
| Túnel remoto | Cloudflared (binario embebido) |
| Exportación | OpenPyXL (Excel) |
| Pruebas | pytest |
