# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build configuration for the Flask backend.
Generates a standalone executable with all dependencies included.
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all Flask-related submodules
hidden_imports = [
    'flask',
    'flask_sqlalchemy',
    'flask_migrate',
    'flask_mail',
    'flask_apscheduler',
    'flask_wtf',
    'flask_login',
    'flask_talisman',
    'wtforms',
    'wtforms.validators',
    'jinja2',
    'jinja2.ext',
    'werkzeug',
    'werkzeug.security',
    'werkzeug.serving',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'alembic',
    'dotenv',
    'email_validator',
    'openpyxl',
]

# Collect template and static files
datas = [
    ('app/templates', 'app/templates'),
    ('app/static', 'app/static'),
    ('config.py', '.'),
    ('run.py', '.'),
]

# Instance folder for SQLite database
datas.append(('instance', 'instance'))

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='inventario_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
