# AGENTS.md - Inventario App

Flask inventory management web app with SQLAlchemy ORM. Manages products, phone models, and compatibility relationships.

## Directory Structure
```
app/
├── __init__.py          # App factory
├── controllers/         # Business logic
├── models.py            # DB models
├── services/            # Service layer
├── views/               # Routes
├── templates/           # HTML templates
└── static/              # CSS, JS, images
```

## Commands

### Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python run.py                          # Dev server
gunicorn --bind 0.0.0.0:5000 run:app   # Prod
```

### Test (pytest)
```bash
pytest                                 # All tests
pytest tests/test_file.py              # Single file
pytest tests/test_file.py::test_func   # Single test
pytest -v                              # Verbose
pytest --cov=app --cov-report=term-missing  # Coverage
```

### Lint & Format
```bash
flake8 app/                            # Lint
black app/                             # Format
isort app/                             # Sort imports
flake8 app/ && black --check app/ && isort --check-only app/  # Check all
```

### Database
```bash
flask db migrate -m "description"      # Create migration
flask db upgrade                       # Apply
flask db downgrade                     # Rollback
```

## Code Style

### Imports
Order: stdlib → third-party → local (each alphabetically, blank line between groups)
```python
import os
from typing import Optional, List

from flask import Flask, current_app
from sqlalchemy.orm import joinedload

from app import db
from app.models import Producto
```

### Formatting
- Black (88 char line length)
- Trailing commas in multi-line expressions
- Run `black app/` before committing

### Type Hints
Use for all parameters and returns. Use `Optional[T]`, `List[T]`, `Dict[K, V]`.
```python
def obtener_por_id(id: int) -> Optional[Producto]:
    return Producto.query.get(id)
```

### Naming
- Classes: `PascalCase` (ProductoController)
- Functions/variables: `snake_case` (obtener_todos)
- Constants: `UPPER_SNAKE_CASE` (MAX_STOCK)
- Private: `_leading_underscore`
- DB tables/columns: `lowercase_underscore`

### Docstrings
Triple double quotes, Google/NumPy style.
```python
def crear(data: dict, modelos_ids: list = None) -> Producto:
    """Create a new product with optional compatible models.
    
    Args:
        data: Product data dictionary
        modelos_ids: Compatible model IDs
        
    Returns:
        Created product instance
    """
```

### Error Handling
Catch specific exceptions, log with `current_app.logger`, rollback DB on errors.
```python
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Error: {e}")
    raise
```

### Flask
- Use application factory pattern
- Access app via `current_app` proxy
- Use `url_for()` for URLs
- Flash messages for user feedback
- Implement 404/500 error handlers

### SQLAlchemy
- Use `joinedload`/`selectinload` to avoid N+1 queries
- Explicit commit/rollback
- Keep models focused on data representation

### Controllers
- Thin controllers; complex logic → services
- Static methods OK for stateless operations
- Handle validation in controllers or forms

### Security
- Validate all input
- Parameterized queries (SQLAlchemy handles this)
- CSRF protection via Flask-WTF
- Use Flask-Talisman for security headers

### Testing
- Unit tests for controllers and models
- Use pytest fixtures for DB setup
- Mock external dependencies
- Test success and failure paths
- No test suite exists yet — create one

### Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- Feature branches, descriptive messages
- Never commit secrets or `.env` files