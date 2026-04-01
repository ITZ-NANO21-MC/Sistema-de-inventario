"""
Script: tunnel.py
Descripción: Inicia el servidor Flask y expone la aplicación al internet
             mediante un túnel (Cloudflare o zrok).
Uso:
    python Scripts/tunnel.py                    # Cloudflare por defecto
    python Scripts/tunnel.py --tool zrok        # Usar zrok
    python Scripts/tunnel.py --flask-only       # Solo Flask, sin túnel
    python Scripts/tunnel.py --port 8080        # Puerto personalizado
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import re
import shutil
import threading


class Colors:
    """Códigos ANSI para colores en terminal."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def banner():
    """Muestra el banner del script."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 60)
    print("  Sistema de Inventario - Exposición Local")
    print("=" * 60)
    print(f"{Colors.END}")


def check_command(command):
    """Verifica si un comando está disponible en el PATH."""
    return shutil.which(command) is not None


def detect_tools():
    """Detecta qué herramientas de túnel están disponibles."""
    tools = {}
    tools['cloudflared'] = check_command('cloudflared')
    tools['zrok'] = check_command('zrok')
    return tools


def find_project_root():
    """Encuentra la raíz del proyecto (donde está run.py)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    run_py = os.path.join(project_root, 'run.py')
    if os.path.exists(run_py):
        return project_root
    raise FileNotFoundError(
        f"No se encontró run.py en {project_root}. "
        "Asegúrate de que el script está en Scripts/ dentro del proyecto."
    )


def start_flask(project_root, port):
    """Inicia el servidor Flask como proceso hijo."""
    print(f"{Colors.YELLOW}[Flask] Iniciando servidor en puerto {port}...{Colors.END}")

    env = os.environ.copy()
    env['FLASK_DEBUG'] = 'False'

    process = subprocess.Popen(
        [sys.executable, 'run.py'],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Esperar a que Flask arranque
    time.sleep(2)
    if process.poll() is not None:
        print(f"{Colors.RED}[Flask] Error al iniciar el servidor.{Colors.END}")
        return None

    print(f"{Colors.GREEN}[Flask] Servidor iniciado en http://localhost:{port}{Colors.END}")
    return process


def start_cloudflared(port):
    """Inicia un túnel de Cloudflare y captura la URL pública."""
    print(f"{Colors.YELLOW}[Cloudflare] Iniciando túnel rápido...{Colors.END}")
    print(f"{Colors.YELLOW}[Cloudflare] Conectando a http://localhost:{port}{Colors.END}")

    process = subprocess.Popen(
        ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    url = None
    print(f"{Colors.CYAN}[Cloudflare] Esperando URL pública...{Colors.END}")

    for line in iter(process.stdout.readline, ''):
        if not line:
            break
        match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
        if match:
            url = match.group(0)
            break

    if url:
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("=" * 60)
        print(f"  URL PÚBLICA: {url}")
        print("=" * 60)
        print(f"{Colors.END}")
        print(f"{Colors.YELLOW}[Cloudflare] Túnel activo. Presiona Ctrl+C para detener.{Colors.END}\n")
        return process, url
    else:
        print(f"{Colors.RED}[Cloudflare] No se pudo obtener la URL del túnel.{Colors.END}")
        return None, None


def start_zrok(port):
    """Inicia un túnel de zrok y captura la URL pública."""
    print(f"{Colors.YELLOW}[zrok] Iniciando túnel público...{Colors.END}")

    process = subprocess.Popen(
        ['zrok', 'share', 'public', f'http://localhost:{port}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    url = None
    print(f"{Colors.CYAN}[zrok] Esperando URL pública...{Colors.END}")

    for line in iter(process.stdout.readline, ''):
        # zrok muestra URLs como https://abc123.shared.zrok.io
        match = re.search(r'https://[a-z0-9-]+\.shared\.zrok\.io', line)
        if match:
            url = match.group(0)
            break

    if url:
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("=" * 60)
        print(f"  URL PÚBLICA: {url}")
        print("=" * 60)
        print(f"{Colors.END}")
        print(f"{Colors.YELLOW}[zrok] Túnel activo. Presiona Ctrl+C para detener.{Colors.END}\n")
        return process, url
    else:
        print(f"{Colors.RED}[zrok] No se pudo obtener la URL del túnel.{Colors.END}")
        return None, None


def print_status(tools, selected_tool):
    """Muestra el estado de las herramientas disponibles."""
    print(f"{Colors.BOLD}Herramientas detectadas:{Colors.END}")
    for tool, available in tools.items():
        status = f"{Colors.GREEN}Disponible{Colors.END}" if available else f"{Colors.RED}No instalado{Colors.END}"
        print(f"  {tool}: {status}")

    if selected_tool not in tools or not tools.get(selected_tool):
        print(f"\n{Colors.RED}Error: '{selected_tool}' no está instalado.{Colors.END}")
        if selected_tool == 'cloudflared':
            print(f"\n{Colors.YELLOW}Instalación en Linux (Debian/Ubuntu):{Colors.END}")
            print("  curl -LO https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
            print("  sudo dpkg -i cloudflared-linux-amd64.deb")
        elif selected_tool == 'zrok':
            print(f"\n{Colors.YELLOW}Instalación de zrok:{Colors.END}")
            print("  curl -sSL https://get.zrok.io | sudo bash")
            print("  zrok enable <tu_token>")
        print()
        sys.exit(1)


def cleanup(processes):
    """Detiene todos los procesos de forma limpia."""
    print(f"\n{Colors.YELLOW}Deteniendo servicios...{Colors.END}")
    for name, proc in processes.items():
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"{Colors.GREEN}[{name}] Detenido.{Colors.END}")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"{Colors.RED}[{name}] Forzado a detenerse.{Colors.END}")
    print(f"{Colors.GREEN}Todos los servicios detenidos.{Colors.END}")


def main():
    parser = argparse.ArgumentParser(
        description='Inicia el servidor Flask y lo expone al internet mediante un túnel.'
    )
    parser.add_argument(
        '--tool', '-t',
        choices=['cloudflared', 'zrok'],
        default='cloudflared',
        help='Herramienta de túnel a usar (default: cloudflared)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='Puerto del servidor Flask (default: 5000)'
    )
    parser.add_argument(
        '--flask-only',
        action='store_true',
        help='Inicia solo Flask sin túnel'
    )
    parser.add_argument(
        '--tunnel-only',
        action='store_true',
        help='Inicia solo el túnel (Flask debe estar corriendo)'
    )

    args = parser.parse_args()

    banner()

    # Detectar herramientas (solo si se necesita túnel)
    tools = detect_tools()
    if not args.flask_only:
        print_status(tools, args.tool)

    # Encontrar raíz del proyecto
    try:
        project_root = find_project_root()
        print(f"{Colors.GREEN}[OK] Proyecto encontrado en: {project_root}{Colors.END}\n")
    except FileNotFoundError as e:
        print(f"{Colors.RED}[Error] {e}{Colors.END}")
        sys.exit(1)

    processes = {}
    flask_proc = None

    # Configurar manejo de señales para limpieza
    def signal_handler(sig, frame):
        cleanup(processes)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Iniciar Flask (a menos que sea solo túnel)
    if not args.tunnel_only:
        flask_proc = start_flask(project_root, args.port)
        if flask_proc is None:
            sys.exit(1)
        processes['Flask'] = flask_proc

    # Modo solo Flask
    if args.flask_only:
        print(f"\n{Colors.GREEN}{Colors.BOLD}Flask corriendo en http://localhost:{args.port}{Colors.END}")
        print(f"{Colors.YELLOW}Presiona Ctrl+C para detener.{Colors.END}\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup(processes)
        return

    # Iniciar túnel
    if args.tool == 'cloudflared':
        tunnel_proc, url = start_cloudflared(args.port)
    else:
        tunnel_proc, url = start_zrok(args.port)

    if tunnel_proc is None:
        cleanup(processes)
        sys.exit(1)

    processes['Tunnel'] = tunnel_proc

    # Mantener el script activo
    try:
        while True:
            # Verificar que los procesos sigan vivos
            for name, proc in processes.items():
                if proc and proc.poll() is not None:
                    print(f"{Colors.RED}[{name}] Proceso terminado inesperadamente.{Colors.END}")
                    cleanup(processes)
                    sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(processes)


if __name__ == '__main__':
    main()
