#!/usr/bin/env python3
"""
RED-SHADOW Main Launcher / Installer / Auto-Updater
- Si el proyecto no esta descargado: clona el repositorio completo
- Si ya esta descargado: verifica actualizaciones y aplica cambios
- Lanza el motor de analisis seleccionado
"""

import os
import sys
import json
import subprocess
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

# ============================================================================
# CONFIGURACION
# ============================================================================

GITHUB_REPO = "FardosESP/red-shadow"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

# Directorio donde se instala el proyecto
INSTALL_DIR = Path(__file__).parent.resolve()
VERSION_FILE = INSTALL_DIR / ".version"

# Archivos del proyecto que se descargan/actualizan
PROJECT_FILES = [
    "red_shadow_destroyer_v4.py",
    "red_shadow_destroyer_v3.py",
    "red_shadow_destroyer_v2.py",
    "README.md",
    ".version",
]

# Motor principal (v4 por defecto)
DEFAULT_ENGINE = "red_shadow_destroyer_v4.py"

# ============================================================================
# COLORES (sin dependencias externas)
# ============================================================================

class Col:
    """Colores ANSI que funcionan en Windows 10+ y Linux/Mac"""
    R = "\033[91m"    # rojo
    G = "\033[92m"    # verde
    Y = "\033[93m"    # amarillo
    C = "\033[96m"    # cyan
    M = "\033[95m"    # magenta
    W = "\033[97m"    # blanco
    GR = "\033[90m"   # gris
    B = "\033[1m"     # bold
    X = "\033[0m"     # reset


# Habilitar colores ANSI en Windows
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        # Fallback: sin colores
        for attr in ['R', 'G', 'Y', 'C', 'M', 'W', 'GR', 'B', 'X']:
            setattr(Col, attr, '')


# ============================================================================
# BANNER
# ============================================================================

BANNER = f"""{Col.R}
 ########  ######## ########           ######  ##     ##    ###    ########   #######  ##      ##
 ##     ## ##       ##     ##         ##    ## ##     ##   ## ##   ##     ## ##     ## ##  ##  ##
 ##     ## ##       ##     ##         ##       ##     ##  ##   ##  ##     ## ##     ## ##  ##  ##
 ########  ######   ##     ## ####### ######   ######### ##     ## ##     ## ##     ## ##  ##  ##
 ##   ##   ##       ##     ##               ## ##     ## ######### ##     ## ##     ## ##  ##  ##
 ##    ##  ##       ##     ##         ##    ## ##     ## ##     ## ##     ## ##     ##  ##  ##  ##
 ##     ## ######## ########           ######  ##     ## ##     ## ########   #######    ###  ###
{Col.X}
{Col.Y}{Col.B}              RED-SHADOW Launcher / Installer / Auto-Updater{Col.X}
{Col.GR}              github.com/{GITHUB_REPO}{Col.X}
"""


# ============================================================================
# UTILIDADES
# ============================================================================

def log(msg, level="INFO"):
    colors = {"INFO": Col.C, "OK": Col.G, "WARN": Col.Y, "ERROR": Col.R, "UPDATE": Col.M}
    color = colors.get(level, Col.W)
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{ts}] [{level:6}] {msg}{Col.X}")


def download_file(url, dest):
    """Descargar un archivo desde una URL"""
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        log(f"Error descargando {url}: {e}", "ERROR")
        return False


def get_remote_file_content(filename):
    """Obtener contenido de un archivo del repositorio"""
    url = f"{GITHUB_RAW}/{filename}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


def get_latest_commit():
    """Obtener SHA del ultimo commit en main"""
    try:
        url = f"{GITHUB_API}/commits/main"
        req = urllib.request.Request(url, headers={"User-Agent": "RED-SHADOW-Updater"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("sha", "")
    except Exception:
        return None


def get_local_version():
    """Leer version local"""
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "unknown", "commit": "", "updated": ""}


def save_local_version(version, commit):
    """Guardar version local"""
    with open(VERSION_FILE, 'w') as f:
        json.dump({
            "version": version,
            "commit": commit,
            "updated": datetime.now().isoformat(),
        }, f, indent=2)


def file_hash(filepath):
    """Calcular hash MD5 de un archivo"""
    if not filepath.exists():
        return None
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def has_git():
    """Verificar si git esta instalado"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def is_git_repo():
    """Verificar si el directorio actual es un repo git"""
    return (INSTALL_DIR / ".git").exists()


# ============================================================================
# INSTALADOR: Descarga el proyecto completo si no existe
# ============================================================================

def install_project():
    """Instalar el proyecto desde cero"""
    print(f"\n{Col.Y}{Col.B}  === INSTALACION DE RED-SHADOW ==={Col.X}\n")

    # Opcion 1: Clonar con git
    if has_git():
        log("Git detectado. Clonando repositorio...", "UPDATE")
        clone_url = f"https://github.com/{GITHUB_REPO}.git"

        try:
            subprocess.run(
                ["git", "clone", clone_url, str(INSTALL_DIR / "_temp_clone")],
                check=True, capture_output=True
            )

            # Mover archivos del clone al directorio actual
            temp_dir = INSTALL_DIR / "_temp_clone"
            for item in temp_dir.iterdir():
                dest = INSTALL_DIR / item.name
                if item.name == ".git":
                    if not (INSTALL_DIR / ".git").exists():
                        shutil.move(str(item), str(dest))
                elif item.is_file():
                    shutil.copy2(str(item), str(dest))
                elif item.is_dir():
                    if dest.exists():
                        shutil.rmtree(str(dest))
                    shutil.copytree(str(item), str(dest))

            shutil.rmtree(str(temp_dir), ignore_errors=True)
            log("Repositorio clonado correctamente", "OK")
            return True

        except subprocess.CalledProcessError as e:
            log(f"Error clonando: {e}", "WARN")
            log("Intentando descarga directa...", "INFO")
            # Limpiar temp
            temp_dir = INSTALL_DIR / "_temp_clone"
            if temp_dir.exists():
                shutil.rmtree(str(temp_dir), ignore_errors=True)

    # Opcion 2: Descarga directa de archivos (sin git)
    log("Descargando archivos del proyecto...", "UPDATE")

    success_count = 0
    for filename in PROJECT_FILES:
        dest = INSTALL_DIR / filename
        url = f"{GITHUB_RAW}/{filename}"
        log(f"  Descargando {filename}...", "INFO")

        if download_file(url, str(dest)):
            success_count += 1
            log(f"  {filename} descargado", "OK")
        else:
            log(f"  Error descargando {filename}", "ERROR")

    # Descargar tambien main.py (este archivo) si no existe
    main_url = f"{GITHUB_RAW}/main.py"
    main_dest = INSTALL_DIR / "main.py"
    # No sobreescribir main.py si ya estamos ejecutando desde el
    # Solo descargar los demas archivos

    if success_count > 0:
        log(f"{success_count}/{len(PROJECT_FILES)} archivos descargados", "OK")

        # Guardar version
        remote_commit = get_latest_commit()
        if remote_commit:
            save_local_version("4.0", remote_commit)

        return True
    else:
        log("No se pudo descargar ningun archivo", "ERROR")
        return False


# ============================================================================
# ACTUALIZADOR: Compara y aplica cambios
# ============================================================================

def check_and_update():
    """Verificar actualizaciones y aplicar cambios si los hay"""
    print(f"\n{Col.C}  === VERIFICANDO ACTUALIZACIONES ==={Col.X}\n")

    local_info = get_local_version()
    local_commit = local_info.get("commit", "")
    local_version = local_info.get("version", "unknown")

    log(f"Version local: {local_version} (commit: {local_commit[:8] if local_commit else 'N/A'})", "INFO")

    # Opcion 1: Actualizar con git pull
    if is_git_repo() and has_git():
        log("Repositorio git detectado. Ejecutando git pull...", "UPDATE")
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=str(INSTALL_DIR),
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout.strip()
            if "Already up to date" in output or "Already up-to-date" in output:
                log("Ya tienes la ultima version", "OK")
                return False
            else:
                log("Actualizacion aplicada via git pull", "OK")
                # Actualizar version local
                remote_commit = get_latest_commit()
                if remote_commit:
                    # Leer version del .version remoto
                    new_info = get_local_version()
                    save_local_version(new_info.get("version", local_version), remote_commit)
                return True

        except subprocess.CalledProcessError:
            log("Error en git pull. Intentando actualizacion directa...", "WARN")

    # Opcion 2: Comparar hashes de archivos y descargar los que cambiaron
    log("Comparando archivos con el repositorio remoto...", "UPDATE")

    remote_commit = get_latest_commit()
    if not remote_commit:
        log("No se pudo conectar a GitHub. Saltando actualizacion.", "WARN")
        return False

    if local_commit == remote_commit:
        log("Ya tienes la ultima version", "OK")
        return False

    log(f"Nueva version disponible (commit: {remote_commit[:8]})", "UPDATE")

    updated_count = 0
    for filename in PROJECT_FILES:
        local_path = INSTALL_DIR / filename

        # Descargar version remota
        remote_content = get_remote_file_content(filename)
        if remote_content is None:
            continue

        # Comparar con local
        remote_hash = hashlib.md5(remote_content).hexdigest()
        local_md5 = file_hash(local_path)

        if local_md5 != remote_hash:
            log(f"  Actualizando {filename}...", "UPDATE")
            try:
                with open(local_path, 'wb') as f:
                    f.write(remote_content)
                updated_count += 1
                log(f"  {filename} actualizado", "OK")
            except Exception as e:
                log(f"  Error escribiendo {filename}: {e}", "ERROR")
        else:
            log(f"  {filename} sin cambios", "INFO")

    # Actualizar main.py tambien (el propio launcher)
    main_remote = get_remote_file_content("main.py")
    if main_remote:
        main_hash = hashlib.md5(main_remote).hexdigest()
        main_local_hash = file_hash(INSTALL_DIR / "main.py")
        if main_hash != main_local_hash:
            log("  Actualizando main.py (launcher)...", "UPDATE")
            try:
                with open(INSTALL_DIR / "main.py", 'wb') as f:
                    f.write(main_remote)
                updated_count += 1
                log("  main.py actualizado. Reinicia el launcher para usar la nueva version.", "WARN")
            except Exception as e:
                log(f"  Error actualizando main.py: {e}", "ERROR")

    if updated_count > 0:
        save_local_version(get_local_version().get("version", "4.0"), remote_commit)
        log(f"{updated_count} archivos actualizados", "OK")
        return True
    else:
        save_local_version(local_version, remote_commit)
        log("Todos los archivos estan al dia", "OK")
        return False


# ============================================================================
# SELECTOR DE VERSION
# ============================================================================

def select_and_run(dump_path, extra_args=None):
    """Seleccionar version del motor y ejecutar"""
    engines = [
        ("red_shadow_destroyer_v4.py", "v4.0 Advanced Forensic Engine (GUI interactivo)"),
        ("red_shadow_destroyer_v3.py", "v3.0 Terminal Hacker Edition"),
        ("red_shadow_destroyer_v2.py", "v2.0 Advanced Analysis Engine"),
    ]

    available = []
    for eng_file, desc in engines:
        if (INSTALL_DIR / eng_file).exists():
            available.append((eng_file, desc))

    if not available:
        log("No se encontro ningun motor de analisis. Ejecuta la instalacion primero.", "ERROR")
        sys.exit(1)

    # Si solo hay uno, usarlo directamente
    if len(available) == 1:
        selected = available[0][0]
    else:
        print(f"\n{Col.Y}{Col.B}  Selecciona el motor de analisis:{Col.X}\n")
        for i, (eng_file, desc) in enumerate(available, 1):
            default_tag = f" {Col.G}(recomendado){Col.X}" if eng_file == DEFAULT_ENGINE else ""
            print(f"  {Col.C}[{i}]{Col.X} {desc}{default_tag}")

        print(f"\n  {Col.GR}Presiona ENTER para usar el motor recomendado{Col.X}")

        try:
            choice = input(f"\n{Col.Y}  > {Col.X}").strip()
        except (EOFError, KeyboardInterrupt):
            choice = ""

        if choice == "" or not choice.isdigit():
            selected = DEFAULT_ENGINE if (INSTALL_DIR / DEFAULT_ENGINE).exists() else available[0][0]
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                selected = available[idx][0]
            else:
                selected = available[0][0]

    # Ejecutar
    script_path = INSTALL_DIR / selected
    log(f"Ejecutando {selected}...", "OK")

    cmd = [sys.executable, str(script_path), dump_path]
    if extra_args:
        cmd.extend(extra_args)

    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        log(f"Error ejecutando {selected}: {e}", "ERROR")
        sys.exit(1)


# ============================================================================
# INSTALACION DE DEPENDENCIAS
# ============================================================================

def check_dependencies():
    """Verificar e instalar dependencias necesarias"""
    try:
        import colorama
    except ImportError:
        log("Instalando dependencia: colorama...", "UPDATE")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "colorama", "--quiet"],
                check=True, capture_output=True
            )
            log("colorama instalado correctamente", "OK")
        except Exception:
            log("No se pudo instalar colorama. Instala manualmente: pip install colorama", "WARN")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print(BANNER)

    # Verificar dependencias
    check_dependencies()

    # Determinar modo de ejecucion
    engine_exists = (INSTALL_DIR / DEFAULT_ENGINE).exists()
    has_args = len(sys.argv) >= 2

    # Caso 1: No hay motor instalado -> instalar
    if not engine_exists:
        log("RED-SHADOW no esta instalado. Iniciando instalacion...", "UPDATE")
        success = install_project()
        if not success:
            log("Instalacion fallida. Verifica tu conexion a internet.", "ERROR")
            sys.exit(1)
        log("Instalacion completada.", "OK")

        if not has_args:
            print(f"\n{Col.G}  RED-SHADOW instalado correctamente.{Col.X}")
            print(f"{Col.C}  Uso: python main.py <ruta_dump>{Col.X}")
            print(f"{Col.C}  Ejemplo: python main.py C:\\FiveM_Dump{Col.X}")
            sys.exit(0)

    # Caso 2: Ya instalado -> verificar updates
    else:
        no_update = "--no-update" in sys.argv
        if not no_update:
            check_and_update()

    # Caso 3: Sin argumentos -> mostrar ayuda
    if not has_args:
        version_info = get_local_version()
        print(f"\n{Col.W}  Version instalada: {Col.G}{version_info.get('version', 'unknown')}{Col.X}")
        print(f"{Col.W}  Ultima actualizacion: {Col.GR}{version_info.get('updated', 'N/A')}{Col.X}")
        print(f"\n{Col.R}  Uso: python main.py <ruta_dump> [opciones]{Col.X}")
        print(f"{Col.C}  Ejemplo: python main.py C:\\FiveM_Dump{Col.X}")
        print(f"\n{Col.W}  Opciones:{Col.X}")
        print(f"  {Col.GR}--no-update    Saltar verificacion de actualizaciones{Col.X}")
        print(f"  {Col.GR}--no-gui       Ejecutar sin menu interactivo (v4){Col.X}")
        print()
        sys.exit(0)

    # Caso 4: Con ruta de dump -> ejecutar analisis
    dump_path = sys.argv[1]

    if dump_path in ("--no-update", "--no-gui", "--help", "-h"):
        print(f"{Col.R}  Uso: python main.py <ruta_dump>{Col.X}")
        sys.exit(1)

    if not os.path.exists(dump_path):
        log(f"Ruta no encontrada: {dump_path}", "ERROR")
        sys.exit(1)

    # Extraer argumentos extra
    extra_args = [a for a in sys.argv[2:] if a != "--no-update"]

    select_and_run(dump_path, extra_args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Col.Y}[!] Interrupcion del usuario{Col.X}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Col.R}[!] Error fatal: {e}{Col.X}")
        sys.exit(1)
