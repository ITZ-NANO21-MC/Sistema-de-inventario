# GEMINI.md - Context for Inventario App

## Project Overview
This is a **Flask-based inventory management application** designed to track products and their compatibility with various phone models. It features automated stock alerts and reports sent via email using scheduled tasks.

### Main Technologies
- **Framework:** Flask
- **ORM:** Flask-SQLAlchemy (SQLite by default)
- **Migrations:** Flask-Migrate (Alembic)
- **Scheduling:** Flask-APScheduler (for stock alerts and reports)
- **Emailing:** Flask-Mail
- **Forms:** Flask-WTF

### Architecture
The project follows a standard Flask application factory pattern:
- `app/__init__.py`: Application factory and scheduler initialization.
- `app/models.py`: Database models (`Producto`, `ModeloTelefono`, `Compatibilidad`).
- `app/controllers/`: Business logic for handling data operations.
- `app/views/`: Flask Blueprints for routing and request handling.
- `app/services/`: Background services like email alerts and report generation.
- `app/templates/`: Jinja2 templates for web UI and email bodies.
- `run.py`: Entry point that ensures the database exists and starts the development server.

## Building and Running

### Environment Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file for configuration (refer to `config.py` for variables like `SECRET_KEY`, `MAIL_SERVER`, etc.).

### Running the Project
```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`.

### Database Management
- **Initialize migrations (one-time):** `flask db init`
- **Create a migration:** `flask db migrate -m "Description of change"`
- **Apply migrations:** `flask db upgrade`

### Testing
Tests should be placed in a `tests/` directory (if not already present).
```bash
pytest
```

## Development Conventions

### Coding Style
- Follow **PEP 8** standards.
- Use **Type Hints** for function parameters and return values.
- **Docstrings:** Use Google-style docstrings for complex logic.
- **Logging:** Prefer Flask's `current_app.logger` over `print()` statements for production-ready code.

### Workflow
- **Models:** Define data structures in `app/models.py`.
- **Controllers:** Place business logic in `app/controllers/` to keep views thin.
- **Views:** Use Blueprints to organize routes by feature (e.g., `producto_bp`, `modelo_bp`).
- **Templates:** Organize templates into subdirectories matching the blueprint names.

### Key Files
- `run.py`: Main entry point.
- `config.py`: Configuration class using environment variables.
- `AGENTS.md`: Detailed guidelines for AI agents and development standards.
- `app/services/alertas.py`: Logic for automated notifications.
