#!/usr/bin/env python3
"""
RED-SHADOW Main Launcher with Auto-Updater
Detects GitHub changes and updates automatically
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error
import colorama
from colorama import Fore, Style, init

init(autoreset=True)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

GITHUB_REPO = "FardosESP/red-shadow"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
LOCAL_VERSION_FILE = Path(__file__).parent / ".version"
MAIN_SCRIPT_V3 = Path(__file__).parent / "red_shadow_destroyer_v3.py"
MAIN_SCRIPT_V4 = Path(__file__).parent / "red_shadow_destroyer_v4.py"

# ============================================================================
# UTILIDADES
# ============================================================================

def print_banner():
    """Mostrar banner"""
    banner = f"""{Fore.RED}
╔═══════════════════════════════════════════════════════════════╗
║                    RED-SHADOW LAUNCHER                        ║
║              Auto-Updater & Execution Engine                  ║
╚═══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(banner)

def get_local_version():
    """Obtener versión local"""
    if LOCAL_VERSION_FILE.exists():
        with open(LOCAL_VERSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('version'), data.get('commit')
    return None, None

def save_local_version(version, commit):
    """Guardar versión local"""
    with open(LOCAL_VERSION_FILE, 'w') as f:
        json.dump({
            'version': version,
            'commit': commit,
            'updated': datetime.now().isoformat()
        }, f)

def get_remote_version():
    """Obtener versión remota de GitHub"""
    try:
        url = f"{GITHUB_API}/releases/latest"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data.get('tag_name'), data.get('target_commitish')
    except Exception as e:
        print(f"{Fore.YELLOW}[!] No se pudo conectar a GitHub: {e}{Style.RESET_ALL}")
        return None, None

def get_latest_commit():
    """Obtener último commit de GitHub"""
    try:
        url = f"{GITHUB_API}/commits/main"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data.get('sha')
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Error obteniendo commits: {e}{Style.RESET_ALL}")
        return None

def download_file(url, destination):
    """Descargar archivo de GitHub"""
    try:
        print(f"{Fore.CYAN}[*] Descargando {Path(url).name}...{Style.RESET_ALL}")
        urllib.request.urlretrieve(url, destination)
        print(f"{Fore.GREEN}[+] Descargado correctamente{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Error descargando: {e}{Style.RESET_ALL}")
        return False

def check_updates():
    """Verificar si hay actualizaciones"""
    print(f"\n{Fore.CYAN}[*] Verificando actualizaciones...{Style.RESET_ALL}")
    
    local_version, local_commit = get_local_version()
    remote_commit = get_latest_commit()
    
    if not remote_commit:
        print(f"{Fore.YELLOW}[!] No se pudo verificar actualizaciones (sin conexión){Style.RESET_ALL}")
        return False
    
    if local_commit == remote_commit:
        print(f"{Fore.GREEN}[+] Versión actualizada{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.YELLOW}[!] Nueva versión disponible{Style.RESET_ALL}")
    return True

def update_tool():
    """Actualizar la herramienta"""
    print(f"\n{Fore.CYAN}[*] Iniciando actualización...{Style.RESET_ALL}")
    
    try:
        # Descargar archivos principales
        files_to_update = [
            'red_shadow_destroyer_v4.py',
            'red_shadow_destroyer_v3.py',
            'red_shadow_destroyer_v2.py',
        ]
        
        for filename in files_to_update:
            url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{filename}"
            destination = Path(__file__).parent / filename
            
            if not download_file(url, destination):
                print(f"{Fore.RED}[!] Fallo al descargar {filename}{Style.RESET_ALL}")
                return False
        
        # Actualizar versión local
        remote_commit = get_latest_commit()
        if remote_commit:
            save_local_version("latest", remote_commit)
            print(f"{Fore.GREEN}[+] Actualización completada{Style.RESET_ALL}")
            return True
        
        return False
    
    except Exception as e:
        print(f"{Fore.RED}[!] Error durante actualización: {e}{Style.RESET_ALL}")
        return False

def select_version():
    """Permitir al usuario seleccionar version del destroyer"""
    print(f"\n{Fore.CYAN}Selecciona la version del motor de analisis:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} v4.0 - Advanced Forensic Engine (GUI interactivo, tecnicas avanzadas)")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} v3.0 - Terminal Hacker Edition")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} v2.0 - Advanced Analysis Engine")

    # Default to v4
    if MAIN_SCRIPT_V4.exists():
        return MAIN_SCRIPT_V4
    elif MAIN_SCRIPT_V3.exists():
        return MAIN_SCRIPT_V3
    return MAIN_SCRIPT_V3


def run_destroyer(dump_path, extra_args=None):
    """Ejecutar RED-SHADOW Destroyer"""
    script = select_version()

    if not script.exists():
        print(f"{Fore.RED}[!] Script principal no encontrado: {script}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.CYAN}[*] Ejecutando RED-SHADOW Destroyer ({script.name})...{Style.RESET_ALL}\n")

    cmd = [sys.executable, str(script), dump_path]
    if extra_args:
        cmd.extend(extra_args)

    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"{Fore.RED}[!] Error ejecutando destroyer: {e}{Style.RESET_ALL}")
        sys.exit(1)

def main():
    """Main entry point"""
    print_banner()
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print(f"{Fore.RED}[!] Uso: python main.py <ruta_dump> [--no-update]{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Ejemplo: python main.py C:\\Dump{Style.RESET_ALL}")
        sys.exit(1)
    
    dump_path = sys.argv[1]
    no_update = '--no-update' in sys.argv
    
    # Verificar que la ruta existe
    if not os.path.exists(dump_path):
        print(f"{Fore.RED}[!] Ruta no encontrada: {dump_path}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Verificar actualizaciones
    if not no_update:
        if check_updates():
            response = input(f"\n{Fore.YELLOW}¿Descargar actualización? (s/n): {Style.RESET_ALL}").lower()
            if response == 's':
                if update_tool():
                    print(f"{Fore.GREEN}[+] Ejecutando versión actualizada...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[!] Continuando con versión actual...{Style.RESET_ALL}")
    
    # Ejecutar destroyer
    run_destroyer(dump_path)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupción del usuario{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error fatal: {e}{Style.RESET_ALL}")
        sys.exit(1)
