# backend.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
        ('migrations', 'migrations'),          # si usas Flask-Migrate
        # instance/ y .env se excluyen del ejecutable intencionalmente.
        # Viven en data/ al lado del ejecutable (ver config.get_data_dir()).
    ],
    hiddenimports=[
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_login',
        'flask_wtf',
        'wtforms',
        'flask_apscheduler',
        'flask_talisman',
        'werkzeug',
        'email',
        'smtplib',
        'sqlalchemy',
        'alembic',
        'tomli',           # necesario para alembic en Python < 3.11
        'pkg_resources',
        'python-dotenv',
        'pytest',
        'openpyxl',
        'email-validator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=True,          # mantén la consola para ver logs (luego puedes cambiarlo a False)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
