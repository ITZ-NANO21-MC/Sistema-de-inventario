# AGENTS.md - Guidelines for Agentic Coding in Inventario App

## Project Overview
This is a Flask web application for inventory management with SQLAlchemy ORM. The application manages products, phone models, and their compatibility relationships.

## Directory Structure
```
inventario_app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── controllers/         # Business logic controllers
│   ├── models.py            # Database models
│   ├── services/            # Service layer
│   ├── views/               # View functions/routes
│   ├── templates/           # HTML templates
│   └── static/              # Static assets (CSS, JS, images)
├── migrations/              # Alembic database migrations
├── instance/                # Instance-specific files (database, config)
├── config.py                # Configuration settings
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flake8 black isort
```

### Running the Application
```bash
# Development server
python run.py

# Production server (example)
gunicorn --bind 0.0.0.0:5000 run:app
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_producto.py

# Run a specific test function
pytest tests/test_producto.py::test_crear_producto

# Run tests with verbose output
pytest -v
```

### Linting and Formatting
```bash
# Check code style with flake8
flake8 app/

# Auto-format with black
black app/

# Sort imports with isort
isort app/

# Run all formatting checks
flake8 app/ && black --check app/ && isort --check-only app/
```

### Database Management
```bash
# Initialize database (handled automatically in run.py)
# For manual initialization:
flask db init

# Create migration
flask db migrate -m "description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## Code Style Guidelines

### Python Version
Target Python 3.8+ for compatibility with dependencies.

### Import Organization
1. Standard library imports (alphabetically)
2. Third-party imports (alphabetically)
3. Local application imports (alphabetically)
4. Separate each section with a blank line

Example:
```python
import os
import sys
from typing import Optional, List

from flask import Flask
from sqlalchemy import Integer, String
from sqlalchemy.orm import declarative_base

from app import db
from app.models import Producto
```

### Formatting (Black)
- Line length: 88 characters (Black default)
- Use trailing commas in multi-line expressions
- No unnecessary blank lines
- Black handles most formatting automatically

### Type Hints
- Use type hints for all function parameters and return values
- Use `Optional[T]` for values that can be None
- Use `List[T]`, `Dict[K, V]` for collections
- Import typing constructs from `typing` module

Example:
```python
def obtener_por_id(id: int) -> Optional[Producto]:
    return Producto.query.get(id)
```

### Naming Conventions
- Classes: PascalCase (e.g., `ProductoController`)
- Functions and variables: snake_case (e.g., `obtener_todos`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_STOCK`)
- Private methods/variables: _leading_underscore
- Database tables: lowercase with underscores (e.g., `productos`)
- Database columns: lowercase with underscores

### Docstrings
- Use triple double quotes for docstrings
- Follow Google-style or NumPy-style docstrings
- Document parameters, return values, and exceptions
- For simple one-line functions, a brief description is sufficient

Example:
```python
def crear(data: dict, modelos_ids: list = None) -> Producto:
    """Create a new product with optional compatible models.
    
    Args:
        data: Dictionary containing product information
        modelos_ids: List of model IDs compatible with this product
        
    Returns:
        Producto: The created product instance
    """
```

### Error Handling
- Catch specific exceptions rather than bare `except`
- Log errors appropriately using Flask's logger
- Return meaningful error messages to users
- In controllers, raise exceptions that can be handled by error handlers

Example:
```python
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Error saving product: {e}")
    raise
```

### Flask-Specific Guidelines
- Use application factory pattern (already implemented)
- Access current app via `current_app` proxy
- Use `url_for()` for generating URLs
- Use flash messages for user feedback
- Implement proper error handlers (404, 500, etc.)

### SQLAlchemy Guidelines
- Use relationship loading options (`joinedload`, `selectinload`) to avoid N+1 queries
- Commit transactions explicitly
- Rollback on exceptions
- Use model methods for business logic when appropriate
- Keep models focused on data representation

### Controller Layer
- Controllers handle business logic
- Keep controllers thin; move complex logic to services
- Static methods are acceptable for stateless operations
- Return model instances or None/not found indicators
- Handle validation in controllers or forms

### Security
- Validate all user input
- Use parameterized queries to prevent SQL injection
- Implement CSRF protection for forms
- Hash passwords (if authentication is added)
- Use Flask-WTF for secure forms when applicable

### Testing Guidelines
- Write unit tests for controllers and models
- Use pytest fixtures for database setup/teardown
- Mock external dependencies
- Test both success and failure cases
- Aim for high coverage of critical paths
- Use factories (like factory_boy) for test data when needed

### Git Practices
- Commit frequently with descriptive messages
- Use feature branches for new work
- Keep commits focused on single changes
- Write clear commit messages explaining why
- Follow conventional commits format when possible:
  - feat: new feature
  - fix: bug fix
  - docs: documentation changes
  - style: formatting changes
  - refactor: code restructuring
  - test: adding/modifying tests
  - chore: maintenance tasks

## Specific Project Observations

Based on code review:
- The project uses SQLAlchemy ORM with Flask
- Models define many-to-many relationships through association table
- Controllers use static methods for business logic
- Debug prints are present in controller methods (should be replaced with logging)
- Type hints are used selectively (should be expanded)
- No explicit test suite exists yet

## Recommended Next Steps
1. Add proper logging instead of print statements
2. Expand type hints throughout the codebase
3. Implement a test suite with pytest
4. Add flake8, black, and isort configuration files
5. Consider adding service layer for complex business logic
6. Implement input validation using WTForms or similar
7. Add API endpoints if needed for frontend consumption