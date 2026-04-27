# Sistema de Inventario - Aplicación Web Flask

Aplicación web para la gestión de inventario de repuestos y accesorios para teléfonos móviles. Permite administrar productos, modelos de teléfono, compatibilidades, alertas de stock bajo, informes automáticos y respaldos de base de datos.

---

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Estructura de Directorios](#estructura-de-directorios)
- [Componentes del Sistema](#componentes-del-sistema)
  - [Modelos de Base de Datos](#modelos-de-base-de-datos)
  - [Controladores](#controladores)
  - [Servicios](#servicios)
  - [Vistas y Rutas](#vistas-y-rutas)
  - [Formularios](#formularios)
  - [Plantillas HTML](#plantillas-html)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Pruebas](#pruebas)
- [Tareas Programadas](#tareas-programadas)
- [Seguridad](#seguridad)
- [Migraciones de Base de Datos](#migraciones-de-base-de-datos)

---

## Características

- **CRUD completo** de productos con categorías, marcas, proveedores y precios en Bs/USD
- **Gestión de modelos** de teléfono con marcas predefinidas
- **Compatibilidad** muchos-a-muchos entre productos (pantallas) y modelos de teléfono
- **Filtros avanzados** por nombre, categoría, marca, precio, proveedor y nivel de stock
- **Alertas automáticas** de stock bajo por correo electrónico
- **Informes periódicos** del estado del inventario (mañana y tarde)
- **Respaldo automático** de la base de datos comprimido en ZIP
- **Actualización automática** de precios en Bs al cambiar la tasa de cambio
- **Exportación a Excel** del inventario completo
- **Actualización rápida** de stock desde la vista de lista
- **Autenticación** con Flask-Login y registro de auditoría de seguridad
- **Cabeceras de seguridad** HTTP con Flask-Talisman (CSP)

---

## Arquitectura del Proyecto

La aplicación sigue el patrón **MVC (Modelo-Vista-Controlador)** con una capa de servicios adicional:

```
Cliente (Navegador)
    │
    ▼
┌─────────────────┐
│   Vistas/Rutas   │  ← Controladores de rutas Flask (Blueprints)
│   (Views)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Controladores   │  ← Lógica de negocio (ProductoController, AlertaController)
│  (Controllers)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Servicios      │  ← Servicios externos (email, auditoría, backup)
│   (Services)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Modelos        │  ← Capa de datos SQLAlchemy ORM
│   (Models)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLite DB      │  ← Base de datos relacional
└─────────────────┘
```

---

## Estructura de Directorios

```
inventario_app/
├── app/
│   ├── __init__.py           # Factory de aplicación, inicialización de extensiones
│   ├── models.py             # Modelos SQLAlchemy (Producto, ModeloTelefono, etc.)
│   ├── forms.py              # Formularios WTForms (Login, Producto, Modelo)
│   ├── controllers/
│   │   ├── producto.py       # Lógica de negocio de productos
│   │   └── alertas.py        # Lógica de negocio de alertas
│   ├── services/
│   │   ├── alertas.py        # Envío de emails, informes, backup
│   │   └── audit.py          # Registro de auditoría de seguridad
│   ├── views/
│   │   ├── auth_routes.py    # Login / Logout
│   │   ├── producto_routes.py # CRUD productos + alertas + exportación
│   │   ├── modelo_routes.py  # CRUD modelos de teléfono
│   │   ├── config_routes.py  # Panel de configuración y jobs
│   │   └── alertas_routes.py # Vista de alertas de stock
│   ├── templates/
│   │   ├── base.html         # Plantilla base con navegación
│   │   ├── auth/login.html   # Formulario de inicio de sesión
│   │   ├── listar.html       # Lista de productos con filtros
│   │   ├── producto/crear.html
│   │   ├── producto/editar.html
│   │   ├── modelo/listar.html
│   │   ├── modelo/crear.html
│   │   ├── modelo/editar.html
│   │   ├── config/jobs.html  # Panel de configuración
│   │   ├── alertas/index.html
│   │   └── email/
│   │       ├── alerta_stock.html
│   │       └── informe_general.html
│   └── static/               # CSS, JS, imágenes
├── migrations/               # Migraciones Flask-Migrate
├── tests/                    # Pruebas unitarias (180 tests)
│   ├── conftest.py           # Fixtures de pytest
│   ├── factories.py          # Helpers de creación de datos
│   ├── test_config.py
│   ├── test_factories.py
│   ├── test_models/          # Tests de modelos (45 tests)
│   ├── test_forms/           # Tests de formularios (32 tests)
│   ├── test_controllers/     # Tests de controladores (44 tests)
│   ├── test_services/        # Tests de servicios (12 tests)
│   └── test_views/           # Tests de rutas (40 tests)
├── logs/                     # Logs de auditoría (security.log)
├── instance/                 # Base de datos SQLite
├── config.py                 # Configuración centralizada
├── run.py                    # Punto de entrada
├── requirements.txt          # Dependencias
├── pytest.ini                # Configuración de pytest
└── .env                      # Variables de entorno (no versionado)
```

---

## Componentes del Sistema

### Modelos de Base de Datos

#### Producto
Representa un artículo del inventario.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `nombre` | String(100) | Nombre del producto |
| `descripcion` | String(200) | Descripción opcional |
| `categoria` | String(50) | pantalla, bateria, funda, cable, cargador, otro |
| `marca` | String(50) | Marca del producto |
| `cantidad_stock` | Integer | Stock actual (default: 0) |
| `stock_minimo` | Integer | Stock mínimo de alerta (default: 5) |
| `proveedor` | String(100) | Proveedor del producto |
| `precio_mayor_bs/usd` | Numeric(10,2) | Precio por mayor |
| `precio_detal_bs/usd` | Numeric(10,2) | Precio al detal |
| `precio_tecnico_bs/usd` | Numeric(10,2) | Precio técnico |
| `modelos_compatibles` | Relación M:N | Modelos de teléfono compatibles |

#### ModeloTelefono
Modelos de teléfono para compatibilidad con productos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `nombre` | String(100) | Nombre único del modelo |
| `marca` | String(50) | Marca del teléfono |

#### Compatibilidad
Tabla de asociación muchos-a-muchos entre Producto y ModeloTelefono.

#### ConfiguracionSistema
Almacena configuraciones clave-valor (ej: última alerta global).

#### Usuario
Usuarios del sistema con autenticación.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `username` | String(64) | Nombre de usuario único |
| `password_hash` | String(256) | Hash de contraseña (werkzeug) |
| `rol` | String(20) | Rol del usuario (default: admin) |
| `is_active` | Boolean | Estado de la cuenta |

---

### Controladores

#### ProductoController (`app/controllers/producto.py`)
- `obtener_todos()` - Lista todos los productos ordenados por nombre
- `obtener_con_filtros()` - Filtra por nombre, categoría, marca, precio, proveedor, stock
- `obtener_por_id(id)` - Obtiene un producto con sus modelos compatibles
- `crear(data, modelos_ids)` - Crea un producto y notifica si el stock es bajo
- `actualizar(id, data, modelos_ids)` - Actualiza un producto existente
- `eliminar(id)` - Elimina un producto
- `actualizar_stock_rapido(id, nueva_cantidad)` - Actualización rápida de stock

#### AlertaController (`app/controllers/alertas.py`)
- `obtener_productos_bajos()` - Productos con stock <= mínimo
- `obtener_productos_bajos_count()` - Conteo de productos con stock bajo
- `obtener_ultima_alerta_global()` - Fecha de la última alerta enviada
- `guardar_fecha_global()` - Registra la fecha de alerta actual
- `guardar_fechas_productos(productos)` - Registra notificación por producto

---

### Servicios

#### Alertas (`app/services/alertas.py`)
- `verificar_stock_y_notificar(app)` - Verifica stock bajo y envía email
- `enviar_alerta_email(app, productos)` - Envía alerta de stock por correo
- `generar_informe_general(app)` - Genera informe completo del inventario
- `enviar_informe_general_email(app, productos, estadisticas)` - Envía informe por correo
- `realizar_backup_automatico(app)` - Comprime DB y envía por correo

#### Auditoría (`app/services/audit.py`)
- `configurar_audit_logger(app)` - Configura logger rotativo (5MB, 5 backups)
- `registrar_evento(accion, detalle, usuario)` - Registra eventos de seguridad

Eventos registrados: `LOGIN_EXITOSO`, `LOGIN_FALLIDO`, `LOGOUT`, `ELIMINAR_PRODUCTO`, `MODIFICAR_CONFIGURACION`

---

### Vistas y Rutas

| Blueprint | Prefijo | Rutas | Protección |
|-----------|---------|-------|------------|
| `auth_bp` | - | `/login`, `/logout` | Pública |
| `producto_bp` | `/productos` | `/`, `/crear`, `/editar/<id>`, `/eliminar/<id>`, `/actualizar-stock/<id>`, `/enviar-alerta-manual`, `/enviar-informe-manual`, `/exportar-excel` | Login required |
| `modelo_bp` | `/modelos` | `/`, `/crear`, `/editar/<id>`, `/eliminar/<id>` | Login required |
| `config_bp` | - | `/configuracion`, `/configuracion/jobs/actualizar`, `/configuracion/backup-manual` | Login required |
| `alertas_bp` | - | `/alertas`, `/alertas/enviar` | Login required |

---

### Formularios

#### LoginForm
- `username` (requerido)
- `password` (requerido)
- `remember_me` (opcional)

#### ProductoForm
- `nombre` (requerido, max 100 chars)
- `descripcion` (opcional, max 200 chars)
- `categoria` (requerido: pantalla, bateria, funda, cable, cargador, otro)
- `marca` (opcional, 14 marcas predefinidas)
- `cantidad_stock` (requerido, >= 0)
- `stock_minimo` (requerido, >= 1)
- `proveedor` (opcional, max 100 chars)
- `modelos_compatibles` (checkboxes dinámicos desde BD)
- 6 campos de precio (mayor, detal, técnico en Bs y USD)

#### ModeloForm
- `nombre` (requerido, max 100 chars)
- `marca` (opcional, 14 marcas predefinidas)

---

### Plantillas HTML

| Plantilla | Propósito |
|-----------|-----------|
| `base.html` | Layout base con navegación, sidebar, flash messages |
| `auth/login.html` | Formulario de inicio de sesión |
| `listar.html` | Lista de productos con filtros y acciones |
| `producto/crear.html` | Formulario de creación de producto |
| `producto/editar.html` | Formulario de edición de producto |
| `modelo/listar.html` | Lista de modelos con filtros |
| `modelo/crear.html` | Formulario de creación de modelo |
| `modelo/editar.html` | Formulario de edición de modelo |
| `config/jobs.html` | Panel de configuración de jobs, correo y tasa de cambio |
| `alertas/index.html` | Vista de productos con stock bajo |
| `email/alerta_stock.html` | Plantilla de email de alerta de stock |
| `email/informe_general.html` | Plantilla de email de informe general |

---

## Requisitos del Sistema

- Python 3.10+
- pip

---

## Instalación

```bash
# Clonar o acceder al directorio del proyecto
cd inventario_app

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración

Crear un archivo `.env` en la raíz del proyecto:

```env
# Clave secreta (mínimo 32 caracteres, requerida)
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui

# Base de datos (SQLite por defecto)
DATABASE_URL=sqlite:///inventario.db

# Configuración de correo (Gmail ejemplo)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
MAIL_DEFAULT_SENDER=tu-email@gmail.com

# Forzar HTTPS en producción
FORCE_HTTPS=false

# Tasa de cambio USD a Bs
TASA_CAMBIO_USD_BS=0

# Jobs programados (hora:minuto, activo/inactivo)
JOB_ALERTA_STOCK_HORA=8
JOB_ALERTA_STOCK_MINUTO=0
JOB_ALERTA_STOCK_ACTIVO=true

JOB_INFORME_MANANA_HORA=7
JOB_INFORME_MANANA_MINUTO=0
JOB_INFORME_MANANA_ACTIVO=true

JOB_INFORME_TARDE_HORA=19
JOB_INFORME_TARDE_MINUTO=0
JOB_INFORME_TARDE_ACTIVO=true

JOB_BACKUP_HORA=21
JOB_BACKUP_MINUTO=0
JOB_BACKUP_ACTIVO=true

# Modo debug para desarrollo
FLASK_DEBUG=true
```

---

## Ejecución

```bash
# Desarrollo
python run.py

# Producción con Gunicorn
gunicorn --bind 0.0.0.0:5000 run:app
```

La aplicación estará disponible en `http://localhost:5000`.

---

## Pruebas

El proyecto cuenta con **180 pruebas unitarias** organizadas en 7 fases:

```bash
# Todas las pruebas
pytest

# Una fase específica
pytest tests/test_models/
pytest tests/test_forms/
pytest tests/test_controllers/
pytest tests/test_services/
pytest tests/test_views/

# Un archivo específico
pytest tests/test_controllers/test_producto_controller.py

# Una prueba individual
pytest tests/test_controllers/test_producto_controller.py::TestCrear::test_crear_minimo

# Con cobertura
pytest --cov=app --cov-report=term-missing

# Verbose
pytest -v
```

| Fase | Archivo(s) | Tests | Cobertura |
|------|-----------|-------|-----------|
| 1. Infraestructura | `conftest.py`, `factories.py` | 7 | Fixtures y helpers |
| 2. Modelos | `test_models/*.py` | 45 | 100% models.py |
| 3. Formularios | `test_forms/*.py` | 32 | 100% forms.py |
| 4. Controladores | `test_controllers/*.py` | 44 | 94% producto.py, 100% alertas.py |
| 5. Servicios | `test_services/*.py` | 12 | 98% alertas.py |
| 6. Vistas/Rutas | `test_views/*.py` | 40 | Integration tests |
| **Total** | | **180** | |

---

## Tareas Programadas

El sistema utiliza **Flask-APScheduler** para ejecutar 4 tareas automáticas configurables desde el panel de configuración:

| Job | Función | Default | Descripción |
|-----|---------|---------|-------------|
| Alerta Stock Bajo | `verificar_stock_y_notificar` | 8:00 AM | Envía email si hay productos con stock <= mínimo |
| Informe Mañana | `generar_informe_general` | 7:00 AM | Envía informe completo del inventario |
| Informe Tarde | `generar_informe_general` | 7:00 PM | Envía informe completo del inventario |
| Backup Diario | `realizar_backup_automatico` | 9:00 PM | Comprime la DB y la envía por email |

Cada job puede activarse/desactivarse y reprogramarse desde `/configuracion`.

---

## Seguridad

| Característica | Implementación |
|----------------|---------------|
| **Autenticación** | Flask-Login con sesiones seguras |
| **Contraseñas** | Hash con werkzeug (scrypt) |
| **CSRF** | Protección automática con Flask-WTF |
| **Cabeceras HTTP** | Flask-Talisman con Content Security Policy |
| **Auditoría** | Logger rotativo en `logs/security.log` |
| **Autorización** | `@login_required` en todas las rutas protegidas |
| **Open Redirect** | Validación de parámetro `next` en login |
| **Clave secreta** | Validación de longitud mínima (32 chars) |

---

## Migraciones de Base de Datos

```bash
# Crear nueva migración
flask db migrate -m "descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade
```
