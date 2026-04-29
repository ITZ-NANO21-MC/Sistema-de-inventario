# AGENTS.md - Sistema de Inventario

Desktop inventory management app: Electron shell + Flask backend (SQLAlchemy/SQLite) + Jinja2 templates. Manages products, phone models, compatibility, auth, email alerts, and Excel export.

## Directory Structure
```
inventario_app/
├── app/                     # Flask application
│   ├── __init__.py  # App factory (create_app)
│   ├── models.py    # SQLAlchemy models
│   ├── forms.py     # WTForms definitions
│   ├── controllers/ # Business logic (thin)
│   ├── services/    # Email, audit, tunnel
│   ├── views/       # Flask blueprints (routes)
│   ├── templates/   # Jinja2 HTML
│   └── static/      # CSS, JS, images
├── tests/           # Pytest suite
├── Scripts/         # Utility scripts
├── config.py        # Configuration
├── run.py           # Entry point
├── backend.spec     # PyInstaller spec
├── requirements.txt # Python dependencies
└── entorno_electron/
    ├── prepare_backend.sh   # Build script for Linux
    ├── prepare_backend.bat  # Build script for Windows
    ├── main.js              # Electron main process
    ├── preload.js           # Context bridge (IPC)
    ├── package.json         # Electron deps & build config
    └── resources/           # Icons, cloudflared binary
```

## Commands

### Electron (from `entorno_electron/`)
```bash
npm start                    # Run Electron app
npm run dev                  # Dev mode
npm run build:win            # Build Windows (NSIS + portable)
npm run build:linux          # Build Linux (AppImage)
npm run build:mac            # Build macOS
```

### Flask Backend (from project root `inventario_app/`)
```bash
python -m venv venv && source venv/bin/activate   # Setup
pip install -r requirements.txt                    # Install deps
python run.py                                      # Dev server
flask db migrate -m "msg"                          # Create migration
flask db upgrade                                   # Apply migration
flask db downgrade                                 # Rollback
```

### Test (from project root `inventario_app/`)
```bash
pytest                                    # All tests
pytest tests/test_file.py                 # Single file
pytest tests/test_file.py::TestClass::test_method  # Single test
pytest -v                                 # Verbose
pytest --cov=app --cov-report=term-missing  # Coverage
```
Tests use `conftest.py` fixtures (`app`, `db`, `client`, `auth_client`) and `factories.py` helpers (`create_producto()`, `create_modelo()`, `create_usuario()`). Class-based organization: `class TestCrear:`, methods `test_crear_con_modelos`.

### Lint & Format (from project root `inventario_app/`)
```bash
black app/                                # Format
isort app/                                # Sort imports
flake8 app/                               # Lint
black --check app/ && isort --check-only app/ && flake8 app/  # Check all
```

## Code Style

### Python
- **Imports**: stdlib → third-party → local (alphabetical within groups, blank line between)
- **Formatting**: Black (88 chars), trailing commas in multi-line
- **Type hints**: All params/returns. Use `Optional[T]`, `List[T]`, `Dict[K, V]`
- **Naming**: Classes `PascalCase`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`, private `_leading_underscore`
- **Docstrings**: Triple double quotes, Google style
- **Error handling**: Catch specific exceptions, `db.session.rollback()` on DB errors, log via `current_app.logger`, re-raise after logging
- **Spanish identifiers** are standard throughout the codebase

### JavaScript (Electron)
- **Modules**: CommonJS `require()`, no ES modules
- **Indentation**: 2 spaces
- **Quotes**: Single quotes
- **Naming**: `camelCase` for functions/vars, `PascalCase` for constructors
- **Security**: `contextIsolation: true`, `nodeIntegration: false` always
- **Error handling**: Promise rejections logged with `[Tag]` prefix (e.g., `[Flask]`, `[Tunnel]`, `[App]`)
- **Process management**: Always clean up child processes in `cleanup()`

### Flask Patterns
- Application factory pattern via `create_app()`
- Access app config via `current_app` (never import app directly)
- Use `url_for()` for URLs, `flash()` for user feedback
- Blueprints with `*_bp` naming (e.g., `producto_bp`)
- Thin controllers; move complex logic to services

### SQLAlchemy
- Use `joinedload`/`selectinload` to avoid N+1 queries
- Explicit `db.session.commit()`/`db.session.rollback()`
- Models focused on data representation only

### Testing
- Mock external dependencies (email, tunnel)
- Test both success and failure paths
- Use `db` fixture for database lifecycle

### Database Migrations
- **Automated**: The app runs `flask db upgrade` automatically on startup (within `create_app`) to ensure the production database matches the bundled code.
- **Manual**: Use `flask db migrate -m "description"` to create new migrations during development.

### Stock Requirements
- **Producto Model**: Includes `stock_minimo` (alert threshold) and `stock_requerido` (target level).
- **Alerts**: Sent when `cantidad_stock <= stock_minimo`.
- **Reports**: Include "Faltante" calculation (`stock_requerido - cantidad_stock`).

### Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Feature branches, descriptive messages
- Never commit secrets, `.env`, or `AGENTS.md` (except for structural changes)
