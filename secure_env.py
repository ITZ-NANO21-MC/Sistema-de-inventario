import os
import secrets

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

def ensure_env_vars():
    # Leer el contenido actual
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
    # Verificar si SECRET_KEY ya está configurada
    has_secret_key = any(line.startswith('SECRET_KEY=') for line in lines)
    has_debug = any(line.startswith('FLASK_DEBUG=') for line in lines)
    
    with open(env_path, 'a') as f:
        if not has_secret_key:
            # Generar clave secreta segura de 64 caracteres
            print("Generando nueva SECRET_KEY segura...")
            new_key = secrets.token_hex(32)
            if lines and not lines[-1].endswith('\n'):
                f.write('\n')
            f.write(f"SECRET_KEY={new_key}\n")
            
        if not has_debug:
            print("Añadiendo configuración FLASK_DEBUG por defecto a .env...")
            f.write("FLASK_DEBUG=False\n")

if __name__ == '__main__':
    ensure_env_vars()
    print("Variables de entorno aseguradas correctamente.")
