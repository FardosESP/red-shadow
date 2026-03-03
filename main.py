#!/usr/bin/env python3
"""
RED-SHADOW v4.0 - Advanced Forensic Engine
Launcher interactivo completo - Solo ejecuta: python main.py
Todo se maneja desde la terminal.
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

INSTALL_DIR = Path(__file__).parent.resolve()
VERSION_FILE = INSTALL_DIR / ".version"

PROJECT_FILES = [
    "red_shadow_destroyer_v4.py",
    "red_shadow_destroyer_v3.py",
    "red_shadow_destroyer_v2.py",
    "web_gui.py",
    "main.py",
    "README.md",
    ".version",
]

# ============================================================================
# COLORES ANSI (sin dependencias)
# ============================================================================

class C:
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    CN = "\033[96m"
    M = "\033[95m"
    W = "\033[97m"
    GR = "\033[90m"
    B = "\033[1m"
    X = "\033[0m"
    BR = "\033[91m\033[1m"
    BG = "\033[92m\033[1m"
    BY = "\033[93m\033[1m"
    BC = "\033[96m\033[1m"


if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        for attr in dir(C):
            if not attr.startswith('_'):
                setattr(C, attr, '')


# ============================================================================
# BANNER
# ============================================================================

BANNER = f"""{C.BR}
 ########  ######## ########           ######  ##     ##    ###    ########   #######  ##      ##
 ##     ## ##       ##     ##         ##    ## ##     ##   ## ##   ##     ## ##     ## ##  ##  ##
 ##     ## ##       ##     ##         ##       ##     ##  ##   ##  ##     ## ##     ## ##  ##  ##
 ########  ######   ##     ## ####### ######   ######### ##     ## ##     ## ##     ## ##  ##  ##
 ##   ##   ##       ##     ##               ## ##     ## ######### ##     ## ##     ## ##  ##  ##
 ##    ##  ##       ##     ##         ##    ## ##     ## ##     ## ##     ## ##     ##  ##  ##  ##
 ##     ## ######## ########           ######  ##     ## ##     ## ########   #######    ###  ###
{C.X}
{C.BY}              RED-SHADOW "Destroyer" v4.0 - Advanced Forensic Engine{C.X}
{C.GR}              FiveM / redENGINE Dump Analysis | github.com/FardosESP{C.X}
"""

SEP = f"{C.CN}{'=' * 75}{C.X}"
SUBSEP = f"{C.GR}{'-' * 75}{C.X}"


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def log(msg, level="INFO"):
    colors = {"INFO": C.CN, "OK": C.G, "WARN": C.Y, "ERROR": C.R, "UPDATE": C.M}
    color = colors.get(level, C.W)
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{ts}] [{level:6}] {msg}{C.X}")


def prompt(text=""):
    try:
        return input(f"{C.BY}  {text}> {C.X}").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def pause():
    try:
        input(f"\n{C.GR}  Presiona ENTER para continuar...{C.X}")
    except (EOFError, KeyboardInterrupt):
        pass


def box(title, lines, width=73, color=C.CN):
    """Caja ASCII"""
    out = []
    out.append(f"{color}+{'-' * width}+{C.X}")
    out.append(f"{color}| {C.B}{title:<{width - 2}}{C.X}{color} |{C.X}")
    out.append(f"{color}+{'-' * width}+{C.X}")
    for line in lines:
        clean = len(line) - len(line.encode('unicode_escape').decode('ascii')) + len(line)
        # Simple padding - just use the line as-is with minimal padding
        out.append(f"{color}|{C.X} {line}")
    out.append(f"{color}+{'-' * width}+{C.X}")
    return '\n'.join(out)


# ============================================================================
# UPDATER / INSTALLER
# ============================================================================

def download_file(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        log(f"Error descargando: {e}", "ERROR")
        return False


def get_remote_content(filename):
    url = f"{GITHUB_RAW}/{filename}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RED-SHADOW"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


def get_latest_commit():
    try:
        url = f"{GITHUB_API}/commits/main"
        req = urllib.request.Request(url, headers={"User-Agent": "RED-SHADOW"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("sha", "")
    except Exception:
        return None


def get_local_version():
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "unknown", "commit": "", "updated": ""}


def save_local_version(version, commit):
    with open(VERSION_FILE, 'w') as f:
        json.dump({"version": version, "commit": commit, "updated": datetime.now().isoformat()}, f, indent=2)


def file_hash(filepath):
    if not Path(filepath).exists():
        return None
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def has_git():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def is_git_repo():
    return (INSTALL_DIR / ".git").exists()


def check_install():
    """Verificar si el motor v4 esta instalado"""
    return (INSTALL_DIR / "red_shadow_destroyer_v4.py").exists()


def install_project():
    """Instalar el proyecto completo"""
    log("Descargando RED-SHADOW desde GitHub...", "UPDATE")

    if has_git() and not is_git_repo():
        log("Clonando repositorio con git...", "UPDATE")
        try:
            temp = INSTALL_DIR / "_temp_clone"
            subprocess.run(["git", "clone", f"https://github.com/{GITHUB_REPO}.git", str(temp)],
                           check=True, capture_output=True)
            for item in temp.iterdir():
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
            shutil.rmtree(str(temp), ignore_errors=True)
            log("Repositorio clonado correctamente", "OK")
            return True
        except Exception as e:
            log(f"Error clonando: {e}. Descarga directa...", "WARN")
            temp = INSTALL_DIR / "_temp_clone"
            if temp.exists():
                shutil.rmtree(str(temp), ignore_errors=True)

    # Descarga directa
    ok = 0
    for fname in PROJECT_FILES:
        if fname == "main.py":
            continue  # No sobreescribir el launcher en ejecucion
        dest = INSTALL_DIR / fname
        url = f"{GITHUB_RAW}/{fname}"
        if download_file(url, str(dest)):
            ok += 1
            log(f"  {fname} OK", "OK")

    if ok > 0:
        commit = get_latest_commit()
        if commit:
            save_local_version("4.0", commit)
        log(f"Instalacion completada ({ok} archivos)", "OK")
        return True

    log("Instalacion fallida", "ERROR")
    return False


def check_updates():
    """Verificar y aplicar actualizaciones"""
    local_info = get_local_version()
    local_commit = local_info.get("commit", "")

    log(f"Version local: {local_info.get('version', '?')}", "INFO")

    # Git pull si es repo
    if is_git_repo() and has_git():
        try:
            result = subprocess.run(["git", "pull", "origin", "main"],
                                    cwd=str(INSTALL_DIR), capture_output=True, text=True, check=True)
            if "Already up to date" in result.stdout or "Already up-to-date" in result.stdout:
                log("Sin actualizaciones", "OK")
                return False
            else:
                log("Actualizacion aplicada via git", "OK")
                commit = get_latest_commit()
                if commit:
                    new_info = get_local_version()
                    save_local_version(new_info.get("version", "4.0"), commit)
                return True
        except Exception:
            pass

    # Comparacion por hash
    remote_commit = get_latest_commit()
    if not remote_commit:
        log("Sin conexion a GitHub", "WARN")
        return False

    if local_commit == remote_commit:
        log("Sin actualizaciones", "OK")
        return False

    log("Nueva version disponible. Actualizando...", "UPDATE")
    updated = 0
    for fname in PROJECT_FILES:
        remote = get_remote_content(fname)
        if remote is None:
            continue
        rh = hashlib.md5(remote).hexdigest()
        lh = file_hash(INSTALL_DIR / fname)
        if rh != lh:
            try:
                with open(INSTALL_DIR / fname, 'wb') as f:
                    f.write(remote)
                updated += 1
                log(f"  {fname} actualizado", "OK")
            except Exception:
                pass

    if updated > 0:
        save_local_version(get_local_version().get("version", "4.0"), remote_commit)
        log(f"{updated} archivos actualizados", "OK")
        if "main.py" in [f for f in PROJECT_FILES]:
            log("Launcher actualizado. Reinicia para usar la nueva version.", "WARN")
    return updated > 0


def check_deps():
    """Instalar colorama si falta"""
    try:
        import colorama
    except ImportError:
        log("Instalando colorama...", "UPDATE")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "colorama", "--quiet"],
                           check=True, capture_output=True)
            log("colorama instalado", "OK")
        except Exception:
            log("Instala manualmente: pip install colorama", "WARN")


# ============================================================================
# MOTOR DE ANALISIS (importado dinamicamente)
# ============================================================================

def run_engine(dump_path, no_gui=False, cmd_gui=False):
    """Ejecutar el motor de analisis v4"""
    engine_path = INSTALL_DIR / "red_shadow_destroyer_v4.py"
    if not engine_path.exists():
        log("Motor v4 no encontrado. Reinstala con la opcion del menu.", "ERROR")
        return

    cmd = [sys.executable, str(engine_path), dump_path]
    if no_gui:
        cmd.append("--no-gui")
    elif cmd_gui:
        cmd.append("--cmd-gui")
    # Default: web GUI (no flag needed)

    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        log(f"Error ejecutando motor: {e}", "ERROR")


# ============================================================================
# MENU PRINCIPAL INTERACTIVO
# ============================================================================

def main_menu():
    """Menu principal interactivo - todo se gestiona desde aqui"""
    dump_path = None
    last_analysis = None

    while True:
        clear()
        print(BANNER)
        print(SEP)

        # Estado actual
        version_info = get_local_version()
        installed = check_install()

        status_lines = []
        if installed:
            status_lines.append(f"  {C.G}[INSTALADO]{C.X} RED-SHADOW v{version_info.get('version', '?')}")
            status_lines.append(f"  {C.GR}Ultima actualizacion: {version_info.get('updated', 'N/A')}{C.X}")
        else:
            status_lines.append(f"  {C.R}[NO INSTALADO]{C.X} Motor de analisis no encontrado")

        if dump_path:
            status_lines.append(f"  {C.CN}Dump cargado: {dump_path}{C.X}")
        else:
            status_lines.append(f"  {C.Y}Dump: No seleccionado{C.X}")

        for line in status_lines:
            print(line)

        print(f"\n{SEP}")

        # Menu
        print(f"""
  {C.BC}[1]{C.X} Seleccionar ruta del dump
  {C.BC}[2]{C.X} Ejecutar analisis (Web Dashboard)
  {C.BC}[3]{C.X} Ejecutar analisis (sin interfaz, solo exportar)
  {C.BC}[4]{C.X} Ejecutar analisis (terminal legacy)
  {C.BC}[5]{C.X} Buscar actualizaciones
  {C.BC}[6]{C.X} Reinstalar / Reparar herramienta
  {C.BC}[7]{C.X} Informacion del proyecto
  {C.BC}[0]{C.X} Salir
""")

        choice = prompt("Opcion")

        if choice == '0':
            print(f"\n{C.GR}  Hasta luego.{C.X}\n")
            break

        elif choice == '1':
            dump_path = menu_select_dump()

        elif choice == '2':
            if not installed:
                log("Motor no instalado. Usa la opcion 6 para instalar.", "ERROR")
                pause()
                continue
            if not dump_path:
                dump_path = menu_select_dump()
                if not dump_path:
                    continue
            run_engine(dump_path)
            pause()

        elif choice == '3':
            if not installed:
                log("Motor no instalado. Usa la opcion 6 para instalar.", "ERROR")
                pause()
                continue
            if not dump_path:
                dump_path = menu_select_dump()
                if not dump_path:
                    continue
            run_engine(dump_path, no_gui=True)
            pause()

        elif choice == '4':
            if not installed:
                log("Motor no instalado. Usa la opcion 6 para instalar.", "ERROR")
                pause()
                continue
            if not dump_path:
                dump_path = menu_select_dump()
                if not dump_path:
                    continue
            run_engine(dump_path, cmd_gui=True)
            pause()

        elif choice == '5':
            menu_update()
            pause()

        elif choice == '6':
            menu_reinstall()
            pause()

        elif choice == '7':
            menu_info()
            pause()

        else:
            log("Opcion no valida", "WARN")
            pause()


def menu_select_dump():
    """Menu para seleccionar la ruta del dump"""
    clear()
    print(BANNER)
    print(f"\n{C.BY}  === SELECCIONAR RUTA DEL DUMP ==={C.X}\n")
    print(f"  {C.W}Escribe la ruta completa de la carpeta del dump de FiveM.{C.X}")
    print(f"  {C.GR}Ejemplo: C:\\Users\\user\\Desktop\\FiveM_Dump{C.X}")
    print(f"  {C.GR}Ejemplo: /home/user/dumps/server1{C.X}")
    print(f"  {C.GR}Escribe 'cancel' para volver al menu{C.X}\n")

    path = prompt("Ruta del dump")

    if not path or path.lower() == 'cancel':
        return None

    # Expandir ~ y resolver
    path = os.path.expanduser(path)
    path = os.path.abspath(path)

    if not os.path.exists(path):
        log(f"Ruta no encontrada: {path}", "ERROR")
        print(f"\n  {C.Y}Quieres crear la carpeta? (s/n){C.X}")
        resp = prompt("")
        if resp.lower() == 's':
            try:
                os.makedirs(path, exist_ok=True)
                log(f"Carpeta creada: {path}", "OK")
            except Exception as e:
                log(f"Error creando carpeta: {e}", "ERROR")
                pause()
                return None
        else:
            pause()
            return None

    if not os.path.isdir(path):
        log("La ruta debe ser un directorio, no un archivo", "ERROR")
        pause()
        return None

    # Verificar que hay archivos Lua
    lua_count = len(list(Path(path).rglob("*.lua")))
    if lua_count == 0:
        log(f"No se encontraron archivos .lua en {path}", "WARN")
        print(f"  {C.Y}Continuar de todos modos? (s/n){C.X}")
        resp = prompt("")
        if resp.lower() != 's':
            return None

    log(f"Dump seleccionado: {path} ({lua_count} archivos Lua)", "OK")
    pause()
    return path


def menu_update():
    """Menu de actualizaciones"""
    clear()
    print(BANNER)
    print(f"\n{C.BY}  === BUSCAR ACTUALIZACIONES ==={C.X}\n")
    check_deps()
    check_updates()


def menu_reinstall():
    """Reinstalar/reparar"""
    clear()
    print(BANNER)
    print(f"\n{C.BY}  === REINSTALAR / REPARAR ==={C.X}\n")
    print(f"  {C.W}Esto descargara todos los archivos del proyecto desde GitHub.{C.X}")
    print(f"  {C.Y}Los archivos existentes seran sobreescritos.{C.X}\n")

    resp = prompt("Continuar? (s/n)")
    if resp.lower() != 's':
        return

    check_deps()
    install_project()


def menu_info():
    """Info del proyecto"""
    clear()
    print(BANNER)

    info = get_local_version()
    installed = check_install()

    lines = [
        f"  {C.W}Proyecto:    {C.CN}RED-SHADOW - FiveM Dump Analysis Engine{C.X}",
        f"  {C.W}Repositorio: {C.CN}github.com/{GITHUB_REPO}{C.X}",
        f"  {C.W}Version:     {C.G}{info.get('version', 'N/A')}{C.X}",
        f"  {C.W}Commit:      {C.GR}{info.get('commit', 'N/A')[:12]}{C.X}",
        f"  {C.W}Actualizado: {C.GR}{info.get('updated', 'N/A')}{C.X}",
        f"  {C.W}Instalado:   {C.G if installed else C.R}{'Si' if installed else 'No'}{C.X}",
        "",
        f"  {C.BY}Motores disponibles:{C.X}",
    ]

    engines = [
        ("red_shadow_destroyer_v4.py", "v4.0 Advanced Forensic Engine"),
        ("red_shadow_destroyer_v3.py", "v3.0 Terminal Hacker Edition"),
        ("red_shadow_destroyer_v2.py", "v2.0 Advanced Analysis Engine"),
    ]
    for eng, desc in engines:
        exists = (INSTALL_DIR / eng).exists()
        status = f"{C.G}OK{C.X}" if exists else f"{C.R}NO{C.X}"
        lines.append(f"    [{status}] {desc}")

    lines.extend([
        "",
        f"  {C.BY}Tecnicas v4.0:{C.X}",
        f"    - GUI interactivo en CMD con 14 secciones",
        f"    - Web Dashboard embebido (se abre en el navegador)",
        f"    - Deteccion de ofuscacion (10 patrones + entropia Shannon)",
        f"    - Analisis de natives por hash y nombre",
        f"    - Server callbacks (ESX, QBCore, ox_lib)",
        f"    - Fingerprinting anticheats (21+ firmas)",
        f"    - Vulnerabilidades: SQL injection, token leaks, credentials",
        f"    - Cadenas de triggers cross-file (DFS)",
        f"    - Deteccion de codigo duplicado (MD5 blocks)",
        f"    - Resource manifest parsing",
        f"    - Exportacion JSON + HTML",
    ])

    for line in lines:
        print(line)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    # Habilitar UTF-8 en Windows
    if os.name == 'nt':
        os.system('chcp 65001 >nul 2>&1')

    # Si se pasan argumentos, modo legacy compatible
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        clear()
        print(BANNER)
        check_deps()
        if not check_install():
            install_project()
        check_updates()
        no_gui = "--no-gui" in sys.argv
        cmd_gui = "--cmd-gui" in sys.argv
        run_engine(sys.argv[1], no_gui=no_gui, cmd_gui=cmd_gui)
        return

    # Modo interactivo
    check_deps()

    # Auto-instalar si no esta
    if not check_install():
        clear()
        print(BANNER)
        print(f"\n{C.Y}  RED-SHADOW no esta instalado. Instalando...{C.X}\n")
        install_project()

    # Abrir menu principal
    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.Y}[!] Interrupcion del usuario{C.X}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C.R}[!] Error fatal: {e}{C.X}")
        sys.exit(1)
