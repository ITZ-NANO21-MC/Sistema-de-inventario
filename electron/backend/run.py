from app import create_app
import os
import signal
import sys

app = create_app()


def _shutdown_handler(signum, frame):
    """Apagar limpiamente APScheduler y salir al recibir SIGTERM/SIGINT."""
    from app import scheduler
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGTERM, _shutdown_handler)
signal.signal(signal.SIGINT, _shutdown_handler)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)