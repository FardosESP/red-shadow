#!/usr/bin/env python3
"""
RED-SHADOW "Destroyer" v4.0 - Advanced Forensic Engine
Herramienta profesional de analisis forense de volcados redENGINE (FiveM)

Nuevas tecnicas avanzadas v4:
- GUI interactivo en CMD con menu de navegacion
- Deteccion de ofuscacion (base64, hex, string manipulation)
- Analisis de Server Callbacks y Natives
- Deteccion de inyeccion SQL en queries
- Deteccion de filtracion de tokens/credenciales
- Analisis de comunicacion cifrada
- Analisis de resource manifests (fxmanifest/resource)
- Grafo de dependencias entre recursos
- Fingerprinting avanzado de anticheats (30+ firmas)
- Analisis de cadena de triggers (flujo cross-file)
- Deteccion de codigo clonado/similar
- Analisis de entropia para strings ofuscadas
- Exportacion HTML de reportes
"""

import os
import re
import json
import sys
import math
import base64
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import colorama
from colorama import Fore, Back, Style, init

init(autoreset=True)


# ============================================================================
# COLORES Y ESTILOS
# ============================================================================

class C:
    """Paleta de colores compacta"""
    G = Fore.GREEN
    R = Fore.RED
    Y = Fore.YELLOW
    CN = Fore.CYAN
    M = Fore.MAGENTA
    W = Fore.WHITE
    GR = Fore.LIGHTBLACK_EX
    BG = Fore.LIGHTGREEN_EX
    BR = Fore.LIGHTRED_EX
    BY = Fore.LIGHTYELLOW_EX
    BC = Fore.LIGHTCYAN_EX
    BM = Fore.LIGHTMAGENTA_EX
    X = Style.RESET_ALL
    B = Style.BRIGHT
    D = Style.DIM


# ============================================================================
# ASCII ART Y BANNERS
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
{C.BY}                    RED-SHADOW "Destroyer" v4.0 - Advanced Forensic Engine{C.X}
{C.GR}                    FiveM / redENGINE Dump Analysis | github.com/FardosESP{C.X}
"""

BOX_TL = "+"
BOX_TR = "+"
BOX_BL = "+"
BOX_BR = "+"
BOX_H = "-"
BOX_V = "|"

SEPARATOR = f"{C.CN}{'=' * 75}{C.X}"
SUBSEP = f"{C.GR}{'-' * 75}{C.X}"


def box(title: str, content: List[str], width: int = 73, color=C.CN) -> str:
    """Generar caja ASCII con titulo y contenido"""
    lines = []
    lines.append(f"{color}{BOX_TL}{BOX_H * width}{BOX_TR}{C.X}")
    lines.append(f"{color}{BOX_V} {C.B}{title:<{width - 2}}{C.X}{color} {BOX_V}{C.X}")
    lines.append(f"{color}{BOX_V}{'-' * width}{BOX_V}{C.X}")
    for line in content:
        # Truncar lineas largas
        visible = line[:width - 4] if len(line) > width - 4 else line
        pad = width - 2 - len(re.sub(r'\x1b\[[0-9;]*m', '', visible))
        if pad < 0:
            pad = 0
        lines.append(f"{color}{BOX_V}{C.X} {visible}{' ' * pad}{color}{BOX_V}{C.X}")
    lines.append(f"{color}{BOX_BL}{BOX_H * width}{BOX_BR}{C.X}")
    return '\n'.join(lines)


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class TriggerEvent:
    event_name: str
    event_type: str  # 'RegisterNetEvent', 'AddEventHandler', 'TriggerServerEvent', 'TriggerClientEvent'
    file: str
    line: int
    handler_function: str
    parameters: List[str]
    calls_functions: List[str]
    has_validation: bool
    has_reward_logic: bool
    has_ban_logic: bool
    reward_type: str
    risk_score: float
    is_honeypot: bool
    code_context: str = ""


@dataclass
class LuaFunction:
    name: str
    file: str
    line: int
    parameters: List[str]
    calls: List[str]
    has_ban_logic: bool = False
    has_validation: bool = False
    risk_score: float = 0.0


@dataclass
class ObfuscationResult:
    file: str
    line: int
    obf_type: str  # 'BASE64', 'HEX', 'STRING_CONCAT', 'LOADSTRING', 'CHAR_CODE', 'XOR'
    snippet: str
    confidence: float


@dataclass
class NativeCall:
    native_hash: str
    file: str
    line: int
    context: str
    category: str  # 'PLAYER', 'VEHICLE', 'WEAPON', 'WORLD', 'NETWORK', 'UNKNOWN'


@dataclass
class ServerCallback:
    name: str
    file: str
    line: int
    has_validation: bool
    parameters: List[str]
    risk_score: float


@dataclass
class ResourceManifest:
    resource_name: str
    file: str
    scripts_server: List[str]
    scripts_client: List[str]
    dependencies: List[str]
    exports: List[str]
    has_ui_page: bool


@dataclass
class SecurityIssue:
    issue_type: str  # 'SQL_INJECTION', 'TOKEN_LEAK', 'CREDENTIAL_LEAK', 'INSECURE_NATIVE'
    file: str
    line: int
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    description: str
    snippet: str


# ============================================================================
# ANTICHEAT DATABASE (30+ firmas)
# ============================================================================

ANTICHEAT_DB = {
    'WaveShield': {
        'signatures': ['WaveShield', 'Wave.lua', 'wave_check', 'wave_protection', 'WaveAC'],
        'description': 'WaveShield Anti-Cheat - Proteccion avanzada con deteccion de inyeccion',
    },
    'Phoenix AC': {
        'signatures': ['Phoenix', 'phoenix_ac', 'PhoenixAC', 'phoenix_anticheat', 'phx_check'],
        'description': 'Phoenix Anti-Cheat - Sistema de proteccion con webhooks Discord',
    },
    'Nexus AC': {
        'signatures': ['Nexus', 'nexus_ac', 'NexusAC', 'nexus_guard', 'nexus_protect'],
        'description': 'Nexus Anti-Cheat - Validacion de integridad de recursos',
    },
    'FireAC': {
        'signatures': ['FireAC', 'fire_ac', 'FireAntiCheat', 'fire_protect', 'fire_guard'],
        'description': 'FireAC - Anti-cheat con deteccion de eventos falsos',
    },
    'Anticheese': {
        'signatures': ['anticheese', 'AntiCheese', 'cheese_detect'],
        'description': 'Anticheese - Sistema anti-exploit ligero',
    },
    'EasyAdmin': {
        'signatures': ['EasyAdmin', 'easyadmin', 'ea_ban', 'ea_kick', 'ea_warn'],
        'description': 'EasyAdmin - Panel de administracion con protecciones integradas',
    },
    'txAdmin': {
        'signatures': ['txAdmin', 'txadmin', 'tx-admin', 'txAdminClient'],
        'description': 'txAdmin - Panel de gestion con sistema anti-cheat integrado',
    },
    'Badger AC': {
        'signatures': ['BadgerAC', 'badger_ac', 'badger_anticheat', 'BadgerAntiCheat'],
        'description': 'Badger Anti-Cheat - Deteccion de explosiones y god mode',
    },
    'Spectate Guard': {
        'signatures': ['SpectateGuard', 'spectate_guard', 'anti_spectate'],
        'description': 'Spectate Guard - Anti-spectate y anti-freecam',
    },
    'NoPixel AC': {
        'signatures': ['np-anticheat', 'np_anticheat', 'NoPixelAC', 'nopixel_ac'],
        'description': 'NoPixel Anti-Cheat - Sistema propietario de NoPixel',
    },
    'FiveGuard': {
        'signatures': ['FiveGuard', 'fiveguard', 'five_guard', 'fg_detect'],
        'description': 'FiveGuard - Proteccion con HWID ban',
    },
    'Anticheat QBCore': {
        'signatures': ['qb-anticheat', 'qb_anticheat', 'QBAntiCheat'],
        'description': 'QBCore Anti-Cheat - Integrado con framework QBCore',
    },
    'Anticheat ESX': {
        'signatures': ['esx_anticheatx', 'esx_anticheat', 'es_anticheat'],
        'description': 'ESX Anti-Cheat - Integrado con framework ESX',
    },
    'vRP Guard': {
        'signatures': ['vrp_guard', 'vRPGuard', 'vrp_anticheat'],
        'description': 'vRP Guard - Proteccion para framework vRP',
    },
    'Clean AC': {
        'signatures': ['CleanAC', 'clean_ac', 'clean_anticheat'],
        'description': 'Clean AC - Anti-cheat minimalista y eficiente',
    },
    'FairPlay': {
        'signatures': ['FairPlay', 'fairplay_ac', 'fair_play'],
        'description': 'FairPlay - Sistema anti-cheat con machine learning',
    },
    'Shield AC': {
        'signatures': ['ShieldAC', 'shield_ac', 'shield_protect', 'shield_anticheat'],
        'description': 'Shield AC - Proteccion multi-capa',
    },
    'Lynx AC': {
        'signatures': ['LynxAC', 'lynx_ac', 'lynx_guard', 'lynx_anticheat'],
        'description': 'Lynx AC - Anti-cheat con deteccion de menu de inyeccion',
    },
    'Cerberus': {
        'signatures': ['Cerberus', 'cerberus_ac', 'cerberus_guard'],
        'description': 'Cerberus - Triple capa de proteccion',
    },
    'Overwatch AC': {
        'signatures': ['OverwatchAC', 'overwatch_ac', 'ow_anticheat'],
        'description': 'Overwatch AC - Deteccion pasiva de anomalias',
    },
    'Custom Webhook Ban': {
        'signatures': ['discord.com/api/webhooks', 'webhook_url.*ban', 'PerformHttpRequest.*ban'],
        'description': 'Sistema de ban via Discord Webhook personalizado',
    },
}

# ============================================================================
# NATIVE CATEGORIES
# ============================================================================

NATIVE_CATEGORIES = {
    'PLAYER': [
        r'GetPlayerPed', r'SetEntityHealth', r'SetPlayerInvincible', r'SetEntityVisible',
        r'SetPlayerWantedLevel', r'GiveWeaponToPed', r'SetPedArmour',
        r'NetworkResurrectLocalPlayer', r'SetEntityCoords',
    ],
    'VEHICLE': [
        r'CreateVehicle', r'SetVehicleModKit', r'SetVehicleColours',
        r'SetVehicleEngineHealth', r'SetVehicleNumberPlateText',
        r'SetVehicleDoorsLocked', r'DeleteVehicle', r'SetVehicleOnGroundProperly',
    ],
    'WEAPON': [
        r'GiveWeaponToPed', r'RemoveAllPedWeapons', r'SetPedAmmo',
        r'AddAmmoToPed', r'GetSelectedPedWeapon', r'SetCurrentPedWeapon',
        r'GiveDelayedWeaponToPed',
    ],
    'WORLD': [
        r'SetWeatherTypeNow', r'SetClockTime', r'CreateObject',
        r'DeleteEntity', r'SetEntityAsNoLongerNeeded', r'CreatePed',
    ],
    'NETWORK': [
        r'TriggerServerEvent', r'TriggerClientEvent', r'RegisterNetEvent',
        r'NetworkGetNetworkIdFromEntity', r'PerformHttpRequest',
        r'NetworkIsSessionStarted',
    ],
    'MONEY': [
        r'AddCash', r'RemoveCash', r'SetCash', r'xPlayer\.addMoney',
        r'xPlayer\.removeMoney', r'Player\.Functions\.AddMoney',
        r'Player\.Functions\.RemoveMoney', r'exports\[.bank.\]',
    ],
}


# ============================================================================
# MOTOR DE ANALISIS AVANZADO v4
# ============================================================================

class RedShadowV4:
    """Motor de analisis forense avanzado con GUI interactivo"""

    def __init__(self, dump_path: str):
        self.dump_path = Path(dump_path)
        self.files: Dict[str, str] = {}
        self.lua_files: Dict[str, str] = {}
        self.manifest_files: Dict[str, str] = {}
        self.total_lines = 0

        # Resultados de analisis
        self.triggers: Dict[str, TriggerEvent] = {}
        self.functions: Dict[str, LuaFunction] = {}
        self.obfuscations: List[ObfuscationResult] = []
        self.natives: List[NativeCall] = []
        self.callbacks: List[ServerCallback] = []
        self.manifests: List[ResourceManifest] = []
        self.security_issues: List[SecurityIssue] = []
        self.anticheat_detected: Dict[str, dict] = {}
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)
        self.trigger_chains: List[List[str]] = []
        self.code_hashes: Dict[str, List[str]] = defaultdict(list)  # hash -> [files]

        self._analysis_done = False

    # ====================================================================
    # UTILIDADES DE TERMINAL
    # ====================================================================

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_status(msg: str, status: str = "INFO"):
        colors = {
            "INFO": C.CN, "OK": C.G, "WARN": C.Y, "ERROR": C.R,
            "SCAN": C.M, "CRIT": C.BR, "DEBUG": C.GR,
        }
        color = colors.get(status, C.W)
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{ts}] [{status:5}] {msg}{C.X}")

    @staticmethod
    def progress_bar(current: int, total: int, label: str = "", width: int = 40):
        if total == 0:
            return
        pct = current / total
        filled = int(width * pct)
        bar = "#" * filled + "." * (width - filled)
        print(f"  {C.CN}[{bar}] {pct:5.1%} {label}{C.X}", end='\r')
        if current == total:
            print()

    def print_banner(self):
        print(BANNER)

    # ====================================================================
    # CARGA DE ARCHIVOS
    # ====================================================================

    def load_files(self) -> int:
        """Cargar todos los archivos del dump"""
        self.print_status("Escaneando directorio del dump...", "SCAN")

        all_files = list(self.dump_path.rglob("*"))
        file_count = 0

        for f in all_files:
            if not f.is_file():
                continue
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()

                rel = str(f.relative_to(self.dump_path))
                self.files[rel] = content

                if f.suffix in ('.lua',):
                    self.lua_files[rel] = content
                    self.total_lines += content.count('\n') + 1
                elif f.name in ('fxmanifest.lua', '__resource.lua', 'resource.lua'):
                    self.manifest_files[rel] = content
                    self.lua_files[rel] = content
                    self.total_lines += content.count('\n') + 1

                file_count += 1
            except Exception:
                pass

        self.print_status(f"{len(self.lua_files)} archivos Lua cargados ({self.total_lines} lineas)", "OK")
        self.print_status(f"{len(self.manifest_files)} manifests detectados", "OK")
        self.print_status(f"{file_count} archivos totales en el dump", "INFO")
        return len(self.lua_files)

    # ====================================================================
    # FASE 1: EXTRACCION DE FUNCIONES
    # ====================================================================

    def extract_functions(self):
        """Extraer todas las funciones Lua"""
        self.print_status("Extrayendo funciones Lua...", "SCAN")
        func_pattern = r'(?:local\s+)?function\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\((.*?)\)'

        total = len(self.lua_files)
        for idx, (fpath, content) in enumerate(self.lua_files.items(), 1):
            lines = content.split('\n')
            for lnum, line in enumerate(lines, 1):
                for m in re.finditer(func_pattern, line):
                    fname = m.group(1)
                    params = [p.strip() for p in m.group(2).split(',') if p.strip()]

                    # Extraer bloque de contexto (siguiente 30 lineas)
                    block_end = min(len(lines), lnum + 30)
                    block = '\n'.join(lines[lnum - 1:block_end])
                    calls = self._extract_calls(block)

                    self.functions[fname] = LuaFunction(
                        name=fname,
                        file=fpath,
                        line=lnum,
                        parameters=params,
                        calls=calls,
                        has_ban_logic=self._has_ban_logic(block),
                        has_validation=self._has_validation(block),
                    )
            self.progress_bar(idx, total, f"Funciones: {Path(fpath).name}")

        self.print_status(f"{len(self.functions)} funciones extraidas", "OK")

    # ====================================================================
    # FASE 2: DETECCION DE TRIGGERS (avanzada)
    # ====================================================================

    def detect_triggers(self):
        """Detectar triggers con analisis de contexto extendido"""
        self.print_status("Detectando triggers con contexto extendido...", "SCAN")

        patterns = {
            'RegisterNetEvent': r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\']',
            'AddEventHandler': r'AddEventHandler\s*\(\s*["\']([^"\']+)["\']',
            'TriggerServerEvent': r'TriggerServerEvent\s*\(\s*["\']([^"\']+)["\']',
            'TriggerClientEvent': r'TriggerClientEvent\s*\(\s*["\']([^"\']+)["\']',
            'RegisterServerEvent': r'RegisterServerEvent\s*\(\s*["\']([^"\']+)["\']',
            'RegisterCommand': r'RegisterCommand\s*\(\s*["\']([^"\']+)["\']',
        }

        total = len(self.lua_files)
        for idx, (fpath, content) in enumerate(self.lua_files.items(), 1):
            lines = content.split('\n')
            for lnum, line in enumerate(lines, 1):
                for ptype, pattern in patterns.items():
                    for m in re.finditer(pattern, line):
                        ename = m.group(1)

                        # Contexto extendido: 20 lineas antes y despues
                        ctx_start = max(0, lnum - 20)
                        ctx_end = min(len(lines), lnum + 20)
                        ctx = '\n'.join(lines[ctx_start:ctx_end])

                        has_val = self._has_validation(ctx)
                        has_rew = self._has_reward(ctx)
                        has_ban = self._has_ban_logic(ctx)
                        rtype = self._classify_reward(ctx)
                        risk = self._calc_trigger_risk(ename, has_val, has_rew, has_ban, ctx)
                        is_hp = self._is_honeypot(ename, has_ban, has_rew, ctx)
                        handler = self._extract_handler(ctx)
                        params = self._extract_params(ctx)
                        calls = self._extract_calls(ctx)

                        self.triggers[ename] = TriggerEvent(
                            event_name=ename,
                            event_type=ptype,
                            file=fpath,
                            line=lnum,
                            handler_function=handler,
                            parameters=params,
                            calls_functions=calls,
                            has_validation=has_val,
                            has_reward_logic=has_rew,
                            has_ban_logic=has_ban,
                            reward_type=rtype,
                            risk_score=risk,
                            is_honeypot=is_hp,
                            code_context=ctx[:500],
                        )
            self.progress_bar(idx, total, f"Triggers: {Path(fpath).name}")

        self.print_status(f"{len(self.triggers)} triggers detectados", "OK")

    # ====================================================================
    # FASE 3: DETECCION DE OFUSCACION
    # ====================================================================

    def detect_obfuscation(self):
        """Detectar patrones de ofuscacion en el codigo"""
        self.print_status("Escaneando ofuscacion de codigo...", "SCAN")

        obf_patterns = {
            'LOADSTRING': (r'loadstring\s*\(', 0.9),
            'BASE64': (r'[A-Za-z0-9+/]{40,}={0,2}', 0.6),
            'HEX_STRING': (r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){5,}', 0.8),
            'CHAR_CODE': (r'string\.char\s*\(\s*\d+\s*(?:,\s*\d+\s*){3,}\)', 0.85),
            'STRING_CONCAT': (r'(?:\.\.\s*["\'][^"\']{1,3}["\']){5,}', 0.7),
            'XOR_CIPHER': (r'bxor|bit\.bxor|bit32\.bxor', 0.75),
            'BYTE_ARRAY': (r'\{\s*\d+\s*,\s*\d+\s*(?:,\s*\d+\s*){10,}\}', 0.7),
            'EVAL_PATTERN': (r'load\s*\(\s*["\']', 0.9),
            'GSUB_DECODE': (r'gsub\s*\(.*\\d.*string\.char', 0.85),
            'GETFENV': (r'getfenv|setfenv', 0.8),
        }

        total = len(self.lua_files)
        for idx, (fpath, content) in enumerate(self.lua_files.items(), 1):
            lines = content.split('\n')
            for lnum, line in enumerate(lines, 1):
                for otype, (pattern, confidence) in obf_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        # Calcular entropia de la linea para ajustar confianza
                        entropy = self._calc_entropy(line)
                        adjusted_conf = min(1.0, confidence + (entropy - 4.0) * 0.05)

                        self.obfuscations.append(ObfuscationResult(
                            file=fpath,
                            line=lnum,
                            obf_type=otype,
                            snippet=line.strip()[:120],
                            confidence=max(0.1, adjusted_conf),
                        ))
            self.progress_bar(idx, total, f"Ofuscacion: {Path(fpath).name}")

        self.print_status(f"{len(self.obfuscations)} patrones de ofuscacion detectados", "OK")

    # ====================================================================
    # FASE 4: ANALISIS DE NATIVES
    # ====================================================================

    def analyze_natives(self):
        """Detectar y categorizar llamadas a natives de FiveM"""
        self.print_status("Analizando llamadas a natives...", "SCAN")

        # Patron generico de native + patrones especificos
        native_hash_pattern = r'Citizen\.InvokeNative\s*\(\s*(0x[0-9a-fA-F]+)'
        invoke_pattern = r'Invoke\s*\(\s*(0x[0-9a-fA-F]+)'

        total = len(self.lua_files)
        for idx, (fpath, content) in enumerate(self.lua_files.items(), 1):
            lines = content.split('\n')

            # Detectar natives por hash
            for lnum, line in enumerate(lines, 1):
                for pattern in [native_hash_pattern, invoke_pattern]:
                    for m in re.finditer(pattern, line):
                        nhash = m.group(1)
                        ctx_s = max(0, lnum - 3)
                        ctx_e = min(len(lines), lnum + 3)
                        ctx = '\n'.join(lines[ctx_s:ctx_e])

                        self.natives.append(NativeCall(
                            native_hash=nhash,
                            file=fpath,
                            line=lnum,
                            context=ctx[:300],
                            category='UNKNOWN',
                        ))

            # Detectar natives por nombre
            for category, cat_patterns in NATIVE_CATEGORIES.items():
                for pat in cat_patterns:
                    for lnum, line in enumerate(lines, 1):
                        if re.search(pat, line, re.IGNORECASE):
                            ctx_s = max(0, lnum - 2)
                            ctx_e = min(len(lines), lnum + 2)
                            ctx = '\n'.join(lines[ctx_s:ctx_e])

                            self.natives.append(NativeCall(
                                native_hash=pat,
                                file=fpath,
                                line=lnum,
                                context=ctx[:300],
                                category=category,
                            ))

            self.progress_bar(idx, total, f"Natives: {Path(fpath).name}")

        self.print_status(f"{len(self.natives)} llamadas a natives detectadas", "OK")

    # ====================================================================
    # FASE 5: SERVER CALLBACKS
    # ====================================================================

    def analyze_callbacks(self):
        """Analizar server callbacks (ESX, QBCore, etc.)"""
        self.print_status("Analizando server callbacks...", "SCAN")

        cb_patterns = [
            r'ESX\.RegisterServerCallback\s*\(\s*["\']([^"\']+)["\']',
            r'QBCore\.Functions\.CreateCallback\s*\(\s*["\']([^"\']+)["\']',
            r'RegisterServerCallback\s*\(\s*["\']([^"\']+)["\']',
            r'lib\.callback\.register\s*\(\s*["\']([^"\']+)["\']',
            r'exports\[.*\]:.*Callback\s*\(\s*["\']([^"\']+)["\']',
        ]

        for fpath, content in self.lua_files.items():
            lines = content.split('\n')
            for lnum, line in enumerate(lines, 1):
                for pattern in cb_patterns:
                    for m in re.finditer(pattern, line):
                        cb_name = m.group(1)
                        ctx_s = max(0, lnum - 5)
                        ctx_e = min(len(lines), lnum + 20)
                        ctx = '\n'.join(lines[ctx_s:ctx_e])

                        has_val = self._has_validation(ctx)
                        params = self._extract_params(ctx)
                        risk = 30.0
                        if not has_val:
                            risk += 25.0
                        if self._has_reward(ctx):
                            risk += 20.0
                        if self._has_ban_logic(ctx):
                            risk += 15.0

                        self.callbacks.append(ServerCallback(
                            name=cb_name,
                            file=fpath,
                            line=lnum,
                            has_validation=has_val,
                            parameters=params,
                            risk_score=min(100, risk),
                        ))

        self.print_status(f"{len(self.callbacks)} server callbacks analizados", "OK")

    # ====================================================================
    # FASE 6: RESOURCE MANIFESTS
    # ====================================================================

    def analyze_manifests(self):
        """Analizar fxmanifest.lua y __resource.lua"""
        self.print_status("Analizando resource manifests...", "SCAN")

        for fpath, content in self.manifest_files.items():
            resource_name = Path(fpath).parent.name or Path(fpath).stem

            server_scripts = re.findall(r'server_scripts?\s*\{([^}]+)\}', content, re.DOTALL)
            client_scripts = re.findall(r'client_scripts?\s*\{([^}]+)\}', content, re.DOTALL)
            deps = re.findall(r'dependencies?\s*\{([^}]+)\}', content, re.DOTALL)
            exports_found = re.findall(r'exports?\s*\{([^}]+)\}', content, re.DOTALL)
            has_ui = bool(re.search(r'ui_page|nui_url', content, re.IGNORECASE))

            def extract_strings(blocks):
                items = []
                for block in blocks:
                    items.extend(re.findall(r'["\']([^"\']+)["\']', block))
                return items

            self.manifests.append(ResourceManifest(
                resource_name=resource_name,
                file=fpath,
                scripts_server=extract_strings(server_scripts),
                scripts_client=extract_strings(client_scripts),
                dependencies=extract_strings(deps),
                exports=extract_strings(exports_found),
                has_ui_page=has_ui,
            ))

        self.print_status(f"{len(self.manifests)} manifests analizados", "OK")

    # ====================================================================
    # FASE 7: SECURITY ISSUES
    # ====================================================================

    def detect_security_issues(self):
        """Detectar problemas de seguridad: SQL injection, token leaks, etc."""
        self.print_status("Escaneando vulnerabilidades de seguridad...", "SCAN")

        security_patterns = {
            'SQL_INJECTION': {
                'patterns': [
                    r'MySQL\.Async\.execute\s*\(\s*["\'].*\.\.',
                    r'MySQL\.Async\.fetchAll\s*\(\s*["\'].*%s',
                    r'exports\[.oxmysql.\].*\.\..*source',
                    r'string\.format\s*\(\s*["\'].*SELECT.*FROM',
                    r'string\.format\s*\(\s*["\'].*INSERT.*INTO',
                    r'string\.format\s*\(\s*["\'].*UPDATE.*SET',
                    r'string\.format\s*\(\s*["\'].*DELETE.*FROM',
                    r'execute\s*\(\s*["\'].*\.\.\s*',
                ],
                'severity': 'CRITICAL',
                'desc': 'Posible inyeccion SQL: query construida con concatenacion de strings',
            },
            'TOKEN_LEAK': {
                'patterns': [
                    r'discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+',
                    r'Bot\s+[A-Za-z0-9_.-]{50,}',
                    r'token\s*=\s*["\'][A-Za-z0-9._-]{20,}["\']',
                    r'api[_\s]*key\s*=\s*["\'][^"\']{15,}["\']',
                ],
                'severity': 'CRITICAL',
                'desc': 'Token o credencial expuesta en el codigo fuente',
            },
            'CREDENTIAL_LEAK': {
                'patterns': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'mysql://\w+:\w+@',
                    r'db_password\s*=',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                ],
                'severity': 'HIGH',
                'desc': 'Credencial hardcodeada detectada',
            },
            'INSECURE_HTTP': {
                'patterns': [
                    r'PerformHttpRequest\s*\(\s*["\']http://',
                    r'http://\d+\.\d+\.\d+\.\d+',
                ],
                'severity': 'MEDIUM',
                'desc': 'Comunicacion HTTP sin cifrar detectada',
            },
            'DANGEROUS_EXPORT': {
                'patterns': [
                    r'exports\[.*\]:.*[Dd]rop[Pp]layer',
                    r'exports\[.*\]:.*[Bb]an',
                    r'exports\[.*\]:.*[Kk]ick',
                    r'exports\[.*\]:.*[Ss]et[Mm]oney',
                    r'exports\[.*\]:.*[Aa]dd[Mm]oney',
                ],
                'severity': 'HIGH',
                'desc': 'Export peligroso accesible desde client-side',
            },
        }

        total = len(self.lua_files)
        for idx, (fpath, content) in enumerate(self.lua_files.items(), 1):
            lines = content.split('\n')
            for lnum, line in enumerate(lines, 1):
                for issue_type, config in security_patterns.items():
                    for pattern in config['patterns']:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.security_issues.append(SecurityIssue(
                                issue_type=issue_type,
                                file=fpath,
                                line=lnum,
                                severity=config['severity'],
                                description=config['desc'],
                                snippet=line.strip()[:150],
                            ))
            self.progress_bar(idx, total, f"Security: {Path(fpath).name}")

        self.print_status(f"{len(self.security_issues)} problemas de seguridad detectados", "OK")

    # ====================================================================
    # FASE 8: ANTICHEAT FINGERPRINTING
    # ====================================================================

    def fingerprint_anticheats(self):
        """Fingerprinting avanzado de anticheats con 30+ firmas"""
        self.print_status("Ejecutando fingerprinting de anticheats...", "SCAN")

        all_code = '\n'.join(self.lua_files.values())
        all_filenames = ' '.join(self.lua_files.keys())

        for ac_name, ac_info in ANTICHEAT_DB.items():
            matched_sigs = []
            for sig in ac_info['signatures']:
                if sig in all_code or sig.lower() in all_filenames.lower():
                    matched_sigs.append(sig)

            if matched_sigs:
                self.anticheat_detected[ac_name] = {
                    'description': ac_info['description'],
                    'matched_signatures': matched_sigs,
                    'confidence': min(1.0, len(matched_sigs) / len(ac_info['signatures'])),
                }

        self.print_status(f"{len(self.anticheat_detected)} anticheats identificados", "OK")

    # ====================================================================
    # FASE 9: TRIGGER CHAIN ANALYSIS
    # ====================================================================

    def analyze_trigger_chains(self):
        """Rastrear cadenas de triggers a traves de archivos"""
        self.print_status("Analizando cadenas de triggers cross-file...", "SCAN")

        # Construir grafo: trigger -> triggers que llama
        trigger_graph: Dict[str, Set[str]] = defaultdict(set)

        for tname, trigger in self.triggers.items():
            # Buscar referencias a otros triggers en el contexto
            for other_name in self.triggers:
                if other_name != tname and other_name in trigger.code_context:
                    trigger_graph[tname].add(other_name)

            # Buscar en funciones llamadas
            for func_name in trigger.calls_functions:
                if func_name in self.functions:
                    func = self.functions[func_name]
                    for other_name in self.triggers:
                        if other_name in '\n'.join(self.lua_files.get(func.file, '').split('\n')):
                            trigger_graph[tname].add(other_name)

        # Encontrar cadenas (DFS)
        visited = set()
        for start in trigger_graph:
            if start not in visited:
                chain = []
                self._dfs_chain(start, trigger_graph, visited, chain)
                if len(chain) > 1:
                    self.trigger_chains.append(chain)

        # Cross-references
        for tname in self.triggers:
            files_with_ref = set()
            for fpath, content in self.lua_files.items():
                if tname in content:
                    files_with_ref.add(fpath)
            if len(files_with_ref) > 1:
                self.cross_references[tname] = files_with_ref

        self.print_status(f"{len(self.trigger_chains)} cadenas de triggers detectadas", "OK")
        self.print_status(f"{len(self.cross_references)} triggers con referencias cruzadas", "OK")

    def _dfs_chain(self, node, graph, visited, chain):
        if node in visited:
            return
        visited.add(node)
        chain.append(node)
        for neighbor in graph.get(node, []):
            self._dfs_chain(neighbor, graph, visited, chain)

    # ====================================================================
    # FASE 10: CODE CLONE DETECTION
    # ====================================================================

    def detect_code_clones(self):
        """Detectar bloques de codigo duplicado/similar entre archivos"""
        self.print_status("Detectando codigo clonado...", "SCAN")

        # Hash de bloques de 5 lineas para detectar clones
        block_size = 5

        for fpath, content in self.lua_files.items():
            lines = content.split('\n')
            for i in range(len(lines) - block_size):
                block = '\n'.join(line.strip() for line in lines[i:i + block_size])
                if len(block.strip()) < 30:
                    continue  # Ignorar bloques muy cortos
                h = hashlib.md5(block.encode()).hexdigest()
                self.code_hashes[h].append(f"{fpath}:{i + 1}")

        # Filtrar solo duplicados reales
        clones = {h: files for h, files in self.code_hashes.items() if len(files) > 1}

        self.print_status(f"{len(clones)} bloques de codigo duplicado detectados", "OK")

    # ====================================================================
    # HELPERS DE ANALISIS
    # ====================================================================

    def _has_ban_logic(self, code: str) -> bool:
        keywords = [
            'DropPlayer', 'Ban', 'kick', 'banear', 'BanPlayer',
            'KickPlayer', 'dropPlayer', 'ban_player', 'tempban',
            'permanent_ban', 'webhook.*ban', 'discord.*ban',
        ]
        code_lower = code.lower()
        return any(kw.lower() in code_lower for kw in keywords)

    def _has_validation(self, code: str) -> bool:
        keywords = [
            'if source', 'if not source', 'check', 'verify', 'validate',
            'assert', 'tonumber(source)', 'GetPlayerIdentifier',
            'IsPlayerAceAllowed', 'GetPlayerName',
        ]
        return any(kw in code for kw in keywords)

    def _has_reward(self, code: str) -> bool:
        keywords = [
            'addMoney', 'addItem', 'giveWeapon', 'addInventory',
            'AddMoney', 'AddItem', 'GiveItem', 'addAccountMoney',
            'xPlayer.addMoney', 'Player.Functions.AddMoney',
            'exports.*inventory', 'TriggerClientEvent',
        ]
        return any(kw in code for kw in keywords)

    def _classify_reward(self, code: str) -> str:
        cl = code.lower()
        if any(w in cl for w in ['addmoney', 'money', 'cash', 'bank', 'account']):
            return 'MONEY'
        elif any(w in cl for w in ['additem', 'inventory', 'item', 'giveitem']):
            return 'ITEMS'
        elif any(w in cl for w in ['giveweapon', 'weapon', 'ammo']):
            return 'WEAPONS'
        elif any(w in cl for w in ['vehicle', 'car', 'spawn']):
            return 'VEHICLES'
        elif any(w in cl for w in ['xp', 'experience', 'level', 'rank']):
            return 'XP'
        return 'UNKNOWN'

    def _calc_trigger_risk(self, name: str, has_val: bool, has_rew: bool,
                           has_ban: bool, ctx: str) -> float:
        risk = 50.0
        if has_val:
            risk -= 20
        if has_rew:
            risk += 15
        if has_ban:
            risk += 30
        suspicious = ['admin', 'ban', 'kick', 'trap', 'check', 'anticheat', 'detect']
        if any(s in name.lower() for s in suspicious):
            risk += 25
        # Bonus: si no tiene source check y tiene reward
        if has_rew and 'source' not in ctx[:200]:
            risk += 10
        return max(0, min(100, risk))

    def _is_honeypot(self, name: str, has_ban: bool, has_reward: bool, ctx: str) -> bool:
        if has_ban and not has_reward:
            return True
        trap_words = ['trap', 'honeypot', 'bait', 'fake', 'test_event']
        if any(w in name.lower() for w in trap_words):
            return True
        return False

    def _extract_handler(self, ctx: str) -> str:
        m = re.search(r'function\s+([A-Za-z_]\w*)', ctx)
        return m.group(1) if m else "anonymous"

    def _extract_params(self, ctx: str) -> List[str]:
        m = re.search(r'function\s*\((.*?)\)', ctx)
        if m:
            return [p.strip() for p in m.group(1).split(',') if p.strip()]
        return []

    def _extract_calls(self, code: str) -> List[str]:
        pattern = r'([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\('
        matches = re.findall(pattern, code)
        # Filtrar keywords de Lua
        lua_kw = {'if', 'for', 'while', 'function', 'local', 'return', 'end', 'do', 'then', 'else', 'elseif', 'repeat', 'until', 'not', 'and', 'or', 'in', 'print'}
        return list(set(m for m in matches if m.lower() not in lua_kw))

    def _calc_entropy(self, text: str) -> float:
        """Calcular entropia de Shannon de un string"""
        if not text:
            return 0.0
        freq = Counter(text)
        length = len(text)
        return -sum((c / length) * math.log2(c / length) for c in freq.values())

    # ====================================================================
    # EJECUCION COMPLETA
    # ====================================================================

    def run_full_analysis(self):
        """Ejecutar todas las fases de analisis"""
        print(SEPARATOR)
        self.print_status("Iniciando analisis forense completo...", "INFO")
        print(SEPARATOR)

        phases = [
            ("Fase 1/10: Extraccion de funciones", self.extract_functions),
            ("Fase 2/10: Deteccion de triggers", self.detect_triggers),
            ("Fase 3/10: Deteccion de ofuscacion", self.detect_obfuscation),
            ("Fase 4/10: Analisis de natives", self.analyze_natives),
            ("Fase 5/10: Server callbacks", self.analyze_callbacks),
            ("Fase 6/10: Resource manifests", self.analyze_manifests),
            ("Fase 7/10: Vulnerabilidades de seguridad", self.detect_security_issues),
            ("Fase 8/10: Fingerprinting anticheats", self.fingerprint_anticheats),
            ("Fase 9/10: Cadenas de triggers", self.analyze_trigger_chains),
            ("Fase 10/10: Deteccion de clones", self.detect_code_clones),
        ]

        for phase_name, phase_func in phases:
            print(f"\n{C.BC}{phase_name}{C.X}")
            phase_func()

        self._analysis_done = True
        print(f"\n{SEPARATOR}")
        self.print_status("Analisis forense completo finalizado", "OK")
        print(SEPARATOR)

    # ====================================================================
    # GUI INTERACTIVO EN CMD
    # ====================================================================

    def interactive_menu(self):
        """Menu interactivo principal en CMD"""
        if not self._analysis_done:
            self.print_status("Ejecuta el analisis primero", "ERROR")
            return

        while True:
            self.clear_screen()
            self.print_banner()

            menu_content = [
                f"{C.BC}[1]{C.X} Resumen general del analisis",
                f"{C.BC}[2]{C.X} Triggers detectados (clasificados)",
                f"{C.BC}[3]{C.X} Honeypots y trampas",
                f"{C.BC}[4]{C.X} Anticheats detectados",
                f"{C.BC}[5]{C.X} Ofuscacion detectada",
                f"{C.BC}[6]{C.X} Llamadas a Natives",
                f"{C.BC}[7]{C.X} Server Callbacks",
                f"{C.BC}[8]{C.X} Vulnerabilidades de seguridad",
                f"{C.BC}[9]{C.X} Resource Manifests",
                f"{C.BC}[10]{C.X} Cadenas de triggers",
                f"{C.BC}[11]{C.X} Codigo duplicado",
                f"{C.BC}[12]{C.X} Buscar trigger por nombre",
                f"{C.BC}[13]{C.X} Exportar reporte JSON",
                f"{C.BC}[14]{C.X} Exportar reporte HTML",
                f"{C.BC}[0]{C.X} Salir",
            ]
            print(box("MENU PRINCIPAL - RED-SHADOW v4.0", menu_content))

            try:
                choice = input(f"\n{C.BY}  Selecciona opcion > {C.X}").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if choice == '0':
                self.print_status("Saliendo...", "INFO")
                break
            elif choice == '1':
                self._view_summary()
            elif choice == '2':
                self._view_triggers()
            elif choice == '3':
                self._view_honeypots()
            elif choice == '4':
                self._view_anticheats()
            elif choice == '5':
                self._view_obfuscation()
            elif choice == '6':
                self._view_natives()
            elif choice == '7':
                self._view_callbacks()
            elif choice == '8':
                self._view_security()
            elif choice == '9':
                self._view_manifests()
            elif choice == '10':
                self._view_trigger_chains()
            elif choice == '11':
                self._view_code_clones()
            elif choice == '12':
                self._search_trigger()
            elif choice == '13':
                self._export_json()
            elif choice == '14':
                self._export_html()
            else:
                self.print_status("Opcion no valida", "WARN")
                self._pause()

    def _pause(self):
        try:
            input(f"\n{C.GR}  Presiona ENTER para continuar...{C.X}")
        except (EOFError, KeyboardInterrupt):
            pass

    # ====================================================================
    # VISTAS DEL MENU
    # ====================================================================

    def _view_summary(self):
        self.clear_screen()
        safe = [t for t in self.triggers.values() if t.risk_score < 40]
        caution = [t for t in self.triggers.values() if 40 <= t.risk_score < 70]
        dangerous = [t for t in self.triggers.values() if t.risk_score >= 70]
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]

        overall_risk = (sum(t.risk_score for t in self.triggers.values()) / len(self.triggers)) if self.triggers else 0

        risk_color = C.R if overall_risk >= 60 else (C.Y if overall_risk >= 35 else C.G)

        content = [
            f"Archivos Lua analizados:    {C.CN}{len(self.lua_files)}{C.X}",
            f"Lineas de codigo:           {C.CN}{self.total_lines}{C.X}",
            f"Resource manifests:         {C.CN}{len(self.manifests)}{C.X}",
            "",
            f"Funciones extraidas:        {C.CN}{len(self.functions)}{C.X}",
            f"Triggers detectados:        {C.CN}{len(self.triggers)}{C.X}",
            f"  - Seguros (< 40%):        {C.G}{len(safe)}{C.X}",
            f"  - Advertencia (40-70%):   {C.Y}{len(caution)}{C.X}",
            f"  - Peligrosos (>= 70%):    {C.R}{len(dangerous)}{C.X}",
            f"  - Honeypots:              {C.BR}{len(honeypots)}{C.X}",
            "",
            f"Server callbacks:           {C.CN}{len(self.callbacks)}{C.X}",
            f"Llamadas a natives:         {C.CN}{len(self.natives)}{C.X}",
            f"Patrones de ofuscacion:     {C.M}{len(self.obfuscations)}{C.X}",
            f"Problemas de seguridad:     {C.R}{len(self.security_issues)}{C.X}",
            f"Anticheats detectados:      {C.Y}{len(self.anticheat_detected)}{C.X}",
            f"Cadenas de triggers:        {C.CN}{len(self.trigger_chains)}{C.X}",
            f"Referencias cruzadas:       {C.CN}{len(self.cross_references)}{C.X}",
            "",
            f"Riesgo general:             {risk_color}{overall_risk:.1f}%{C.X}",
        ]
        print(box("RESUMEN GENERAL DEL ANALISIS", content))

        # Recomendaciones
        recs = self._generate_recommendations()
        if recs:
            print(f"\n{C.BY}  RECOMENDACIONES:{C.X}")
            for rec in recs:
                print(f"  {C.Y}>{C.X} {rec}")

        self._pause()

    def _view_triggers(self):
        self.clear_screen()
        safe = sorted([t for t in self.triggers.values() if t.risk_score < 40], key=lambda t: t.risk_score)
        caution = sorted([t for t in self.triggers.values() if 40 <= t.risk_score < 70], key=lambda t: t.risk_score)
        dangerous = sorted([t for t in self.triggers.values() if t.risk_score >= 70], key=lambda t: t.risk_score, reverse=True)

        print(f"\n{C.G}  === TRIGGERS SEGUROS ({len(safe)}) ==={C.X}")
        for t in safe[:20]:
            hp_tag = f" {C.BR}[HONEYPOT]{C.X}" if t.is_honeypot else ""
            val_tag = f" {C.G}[VAL]{C.X}" if t.has_validation else ""
            print(f"  {C.G}[{t.risk_score:5.1f}%]{C.X} {t.event_name:<40} {t.reward_type:<10}{val_tag}{hp_tag}")

        print(f"\n{C.Y}  === TRIGGERS ADVERTENCIA ({len(caution)}) ==={C.X}")
        for t in caution[:15]:
            hp_tag = f" {C.BR}[HONEYPOT]{C.X}" if t.is_honeypot else ""
            val_tag = f" {C.G}[VAL]{C.X}" if t.has_validation else ""
            print(f"  {C.Y}[{t.risk_score:5.1f}%]{C.X} {t.event_name:<40} {t.reward_type:<10}{val_tag}{hp_tag}")

        print(f"\n{C.R}  === TRIGGERS PELIGROSOS ({len(dangerous)}) ==={C.X}")
        for t in dangerous[:15]:
            hp_tag = f" {C.BR}[HONEYPOT]{C.X}" if t.is_honeypot else ""
            ban_tag = f" {C.R}[BAN]{C.X}" if t.has_ban_logic else ""
            print(f"  {C.R}[{t.risk_score:5.1f}%]{C.X} {t.event_name:<40} {t.reward_type:<10}{ban_tag}{hp_tag}")

        self._pause()

    def _view_honeypots(self):
        self.clear_screen()
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]

        if not honeypots:
            print(f"\n{C.G}  No se detectaron honeypots en este dump.{C.X}")
            self._pause()
            return

        content = []
        for t in honeypots:
            content.append(f"{C.BR}[HONEYPOT]{C.X} {t.event_name}")
            content.append(f"  Archivo: {Path(t.file).name}:{t.line}")
            content.append(f"  Tipo: {t.event_type} | Riesgo: {t.risk_score:.0f}%")
            content.append(f"  Logica ban: {'SI' if t.has_ban_logic else 'NO'} | Reward: {'SI' if t.has_reward_logic else 'NO'}")
            content.append("")

        print(box(f"HONEYPOTS DETECTADOS ({len(honeypots)})", content))
        print(f"\n  {C.R}ATENCION: Ejecutar estos triggers resultara en BAN inmediato.{C.X}")
        self._pause()

    def _view_anticheats(self):
        self.clear_screen()
        if not self.anticheat_detected:
            print(f"\n{C.G}  No se detectaron anticheats conocidos.{C.X}")
            self._pause()
            return

        content = []
        for ac_name, ac_info in self.anticheat_detected.items():
            conf = ac_info['confidence']
            conf_color = C.R if conf > 0.7 else (C.Y if conf > 0.3 else C.G)
            content.append(f"{C.BY}{ac_name}{C.X} [{conf_color}Confianza: {conf:.0%}{C.X}]")
            content.append(f"  {ac_info['description']}")
            content.append(f"  Firmas: {', '.join(ac_info['matched_signatures'])}")
            content.append("")

        print(box(f"ANTICHEATS DETECTADOS ({len(self.anticheat_detected)})", content))
        self._pause()

    def _view_obfuscation(self):
        self.clear_screen()
        if not self.obfuscations:
            print(f"\n{C.G}  No se detecto ofuscacion de codigo.{C.X}")
            self._pause()
            return

        by_type = defaultdict(list)
        for obf in self.obfuscations:
            by_type[obf.obf_type].append(obf)

        content = []
        for otype, items in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            content.append(f"{C.M}[{otype}]{C.X} - {len(items)} detecciones")
            for item in items[:3]:
                content.append(f"  {Path(item.file).name}:{item.line} [{item.confidence:.0%}]")
                content.append(f"    {C.GR}{item.snippet[:80]}{C.X}")
            if len(items) > 3:
                content.append(f"  ... y {len(items) - 3} mas")
            content.append("")

        print(box(f"OFUSCACION DETECTADA ({len(self.obfuscations)} patrones)", content))
        self._pause()

    def _view_natives(self):
        self.clear_screen()
        if not self.natives:
            print(f"\n{C.G}  No se detectaron llamadas a natives.{C.X}")
            self._pause()
            return

        by_cat = defaultdict(list)
        for n in self.natives:
            by_cat[n.category].append(n)

        content = []
        for cat, items in sorted(by_cat.items(), key=lambda x: len(x[1]), reverse=True):
            cat_color = C.R if cat in ('WEAPON', 'MONEY') else (C.Y if cat in ('PLAYER', 'NETWORK') else C.CN)
            content.append(f"{cat_color}[{cat}]{C.X} - {len(items)} llamadas")
            for item in items[:5]:
                content.append(f"  {item.native_hash} -> {Path(item.file).name}:{item.line}")
            if len(items) > 5:
                content.append(f"  ... y {len(items) - 5} mas")
            content.append("")

        print(box(f"NATIVES DETECTADAS ({len(self.natives)})", content))
        self._pause()

    def _view_callbacks(self):
        self.clear_screen()
        if not self.callbacks:
            print(f"\n{C.G}  No se detectaron server callbacks.{C.X}")
            self._pause()
            return

        sorted_cbs = sorted(self.callbacks, key=lambda c: c.risk_score, reverse=True)
        content = []
        for cb in sorted_cbs[:25]:
            risk_color = C.R if cb.risk_score >= 70 else (C.Y if cb.risk_score >= 40 else C.G)
            val_tag = f"{C.G}[VAL]{C.X}" if cb.has_validation else f"{C.R}[NO-VAL]{C.X}"
            content.append(f"{risk_color}[{cb.risk_score:5.1f}%]{C.X} {cb.name} {val_tag}")
            content.append(f"  {C.GR}{Path(cb.file).name}:{cb.line}{C.X}")

        if len(self.callbacks) > 25:
            content.append(f"  ... y {len(self.callbacks) - 25} mas")

        print(box(f"SERVER CALLBACKS ({len(self.callbacks)})", content))
        self._pause()

    def _view_security(self):
        self.clear_screen()
        if not self.security_issues:
            print(f"\n{C.G}  No se detectaron vulnerabilidades de seguridad.{C.X}")
            self._pause()
            return

        by_type = defaultdict(list)
        for issue in self.security_issues:
            by_type[issue.issue_type].append(issue)

        content = []
        for itype, issues in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            severity = issues[0].severity
            sev_color = C.BR if severity == 'CRITICAL' else (C.R if severity == 'HIGH' else (C.Y if severity == 'MEDIUM' else C.CN))
            content.append(f"{sev_color}[{severity}] {itype}{C.X} - {len(issues)} detecciones")
            content.append(f"  {issues[0].description}")
            for issue in issues[:3]:
                content.append(f"    {Path(issue.file).name}:{issue.line}")
                content.append(f"    {C.GR}{issue.snippet[:80]}{C.X}")
            if len(issues) > 3:
                content.append(f"    ... y {len(issues) - 3} mas")
            content.append("")

        print(box(f"VULNERABILIDADES DE SEGURIDAD ({len(self.security_issues)})", content))
        self._pause()

    def _view_manifests(self):
        self.clear_screen()
        if not self.manifests:
            print(f"\n{C.G}  No se encontraron resource manifests.{C.X}")
            self._pause()
            return

        content = []
        for m in self.manifests:
            ui_tag = f" {C.M}[NUI]{C.X}" if m.has_ui_page else ""
            content.append(f"{C.BY}{m.resource_name}{C.X}{ui_tag}")
            if m.scripts_server:
                content.append(f"  Server: {', '.join(m.scripts_server[:5])}")
            if m.scripts_client:
                content.append(f"  Client: {', '.join(m.scripts_client[:5])}")
            if m.dependencies:
                content.append(f"  Deps: {', '.join(m.dependencies[:5])}")
            if m.exports:
                content.append(f"  Exports: {', '.join(m.exports[:5])}")
            content.append("")

        print(box(f"RESOURCE MANIFESTS ({len(self.manifests)})", content))
        self._pause()

    def _view_trigger_chains(self):
        self.clear_screen()
        if not self.trigger_chains:
            print(f"\n{C.G}  No se detectaron cadenas de triggers.{C.X}")
            self._pause()
            return

        content = []
        for i, chain in enumerate(self.trigger_chains[:15], 1):
            content.append(f"{C.CN}Cadena #{i}:{C.X} ({len(chain)} triggers)")
            chain_str = f" -> ".join(chain[:8])
            if len(chain) > 8:
                chain_str += f" -> ... (+{len(chain) - 8})"
            content.append(f"  {chain_str}")
            content.append("")

        print(box(f"CADENAS DE TRIGGERS ({len(self.trigger_chains)})", content))

        if self.cross_references:
            print(f"\n{C.BY}  REFERENCIAS CRUZADAS (triggers en multiples archivos):{C.X}")
            for tname, files in list(self.cross_references.items())[:10]:
                print(f"  {C.CN}{tname}{C.X} -> {len(files)} archivos")

        self._pause()

    def _view_code_clones(self):
        self.clear_screen()
        clones = {h: files for h, files in self.code_hashes.items() if len(files) > 1}

        if not clones:
            print(f"\n{C.G}  No se detecto codigo duplicado.{C.X}")
            self._pause()
            return

        content = [
            f"Total bloques duplicados: {len(clones)}",
            "",
        ]

        for i, (h, files) in enumerate(list(clones.items())[:10], 1):
            content.append(f"{C.Y}Clone #{i}{C.X} (encontrado en {len(files)} ubicaciones):")
            for f in files[:5]:
                content.append(f"  {f}")
            if len(files) > 5:
                content.append(f"  ... y {len(files) - 5} mas")
            content.append("")

        print(box(f"CODIGO DUPLICADO ({len(clones)} bloques)", content))
        self._pause()

    def _search_trigger(self):
        self.clear_screen()
        try:
            query = input(f"\n{C.BY}  Nombre del trigger a buscar > {C.X}").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if not query:
            return

        results = []
        for tname, trigger in self.triggers.items():
            if query.lower() in tname.lower():
                results.append(trigger)

        if not results:
            print(f"\n{C.Y}  No se encontraron triggers con '{query}'{C.X}")
            self._pause()
            return

        for t in results[:10]:
            risk_color = C.R if t.risk_score >= 70 else (C.Y if t.risk_score >= 40 else C.G)
            hp_tag = f" {C.BR}[HONEYPOT]{C.X}" if t.is_honeypot else ""

            content = [
                f"Nombre:     {t.event_name}",
                f"Tipo:       {t.event_type}",
                f"Archivo:    {t.file}:{t.line}",
                f"Handler:    {t.handler_function}",
                f"Parametros: {', '.join(t.parameters) if t.parameters else 'N/A'}",
                f"Funciones:  {', '.join(t.calls_functions[:8]) if t.calls_functions else 'N/A'}",
                f"Validacion: {'SI' if t.has_validation else 'NO'}",
                f"Reward:     {'SI' if t.has_reward_logic else 'NO'} ({t.reward_type})",
                f"Ban logic:  {'SI' if t.has_ban_logic else 'NO'}",
                f"Riesgo:     {t.risk_score:.1f}%",
            ]

            print(box(f"TRIGGER: {t.event_name}{' [HONEYPOT]' if t.is_honeypot else ''}", content, color=risk_color))

            if t.code_context:
                print(f"\n{C.GR}  --- Contexto de codigo ---{C.X}")
                for line in t.code_context.split('\n')[:15]:
                    print(f"  {C.GR}{line}{C.X}")
            print()

        self._pause()

    # ====================================================================
    # EXPORTACION
    # ====================================================================

    def _export_json(self):
        fname = f"red_shadow_v4_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            'tool': 'RED-SHADOW Destroyer v4.0',
            'timestamp': datetime.now().isoformat(),
            'dump_path': str(self.dump_path),
            'stats': {
                'lua_files': len(self.lua_files),
                'total_lines': self.total_lines,
                'functions': len(self.functions),
                'triggers': len(self.triggers),
                'callbacks': len(self.callbacks),
                'natives': len(self.natives),
                'obfuscations': len(self.obfuscations),
                'security_issues': len(self.security_issues),
                'anticheats': len(self.anticheat_detected),
            },
            'triggers': [asdict(t) for t in self.triggers.values()],
            'callbacks': [asdict(c) for c in self.callbacks],
            'natives': [asdict(n) for n in self.natives],
            'obfuscations': [asdict(o) for o in self.obfuscations],
            'security_issues': [asdict(s) for s in self.security_issues],
            'anticheats': self.anticheat_detected,
            'manifests': [asdict(m) for m in self.manifests],
            'trigger_chains': self.trigger_chains,
            'cross_references': {k: list(v) for k, v in self.cross_references.items()},
            'recommendations': self._generate_recommendations(),
        }

        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        self.print_status(f"Reporte JSON exportado: {fname}", "OK")
        self._pause()

    def _export_html(self):
        fname = f"red_shadow_v4_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        safe = [t for t in self.triggers.values() if t.risk_score < 40]
        caution = [t for t in self.triggers.values() if 40 <= t.risk_score < 70]
        dangerous = [t for t in self.triggers.values() if t.risk_score >= 70]
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]
        overall_risk = (sum(t.risk_score for t in self.triggers.values()) / len(self.triggers)) if self.triggers else 0

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>RED-SHADOW v4.0 - Reporte Forense</title>
<style>
body {{ background: #0a0a0a; color: #c0c0c0; font-family: 'Courier New', monospace; padding: 20px; }}
h1 {{ color: #ff3333; text-align: center; }}
h2 {{ color: #00cccc; border-bottom: 1px solid #333; padding-bottom: 5px; }}
h3 {{ color: #cccc00; }}
.box {{ background: #111; border: 1px solid #333; padding: 15px; margin: 10px 0; border-radius: 4px; }}
.stat {{ display: inline-block; margin: 10px 20px; text-align: center; }}
.stat-value {{ font-size: 24px; font-weight: bold; }}
.safe {{ color: #00cc00; }}
.warn {{ color: #cccc00; }}
.danger {{ color: #ff3333; }}
.critical {{ color: #ff0066; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
th {{ background: #1a1a1a; color: #00cccc; padding: 8px; text-align: left; border: 1px solid #333; }}
td {{ padding: 8px; border: 1px solid #222; }}
tr:hover {{ background: #1a1a1a; }}
.tag {{ padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
.tag-honeypot {{ background: #ff0066; color: white; }}
.tag-safe {{ background: #00cc00; color: black; }}
.tag-warn {{ background: #cccc00; color: black; }}
.tag-danger {{ background: #ff3333; color: white; }}
</style>
</head>
<body>
<h1>RED-SHADOW "Destroyer" v4.0</h1>
<p style="text-align:center;color:#666;">Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Dump: {self.dump_path}</p>

<h2>Resumen General</h2>
<div class="box">
<div class="stat"><div class="stat-value" style="color:#00cccc">{len(self.lua_files)}</div>Archivos Lua</div>
<div class="stat"><div class="stat-value" style="color:#00cccc">{self.total_lines}</div>Lineas</div>
<div class="stat"><div class="stat-value safe">{len(safe)}</div>Seguros</div>
<div class="stat"><div class="stat-value warn">{len(caution)}</div>Advertencia</div>
<div class="stat"><div class="stat-value danger">{len(dangerous)}</div>Peligrosos</div>
<div class="stat"><div class="stat-value critical">{len(honeypots)}</div>Honeypots</div>
<div class="stat"><div class="stat-value" style="color:{'#ff3333' if overall_risk >= 60 else '#cccc00' if overall_risk >= 35 else '#00cc00'}">{overall_risk:.1f}%</div>Riesgo</div>
</div>

<h2>Anticheats Detectados ({len(self.anticheat_detected)})</h2>
<div class="box">
"""
        if self.anticheat_detected:
            html += "<table><tr><th>Anticheat</th><th>Confianza</th><th>Descripcion</th></tr>"
            for ac_name, ac_info in self.anticheat_detected.items():
                conf = ac_info['confidence']
                html += f"<tr><td><b>{ac_name}</b></td><td>{conf:.0%}</td><td>{ac_info['description']}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No se detectaron anticheats conocidos.</p>"

        html += """</div>

<h2>Triggers Detectados</h2>
<div class="box">
<table>
<tr><th>Trigger</th><th>Tipo</th><th>Archivo</th><th>Reward</th><th>Riesgo</th><th>Tags</th></tr>
"""
        for t in sorted(self.triggers.values(), key=lambda x: x.risk_score, reverse=True):
            risk_class = 'danger' if t.risk_score >= 70 else ('warn' if t.risk_score >= 40 else 'safe')
            tags = ""
            if t.is_honeypot:
                tags += '<span class="tag tag-honeypot">HONEYPOT</span> '
            if t.has_ban_logic:
                tags += '<span class="tag tag-danger">BAN</span> '
            if t.has_validation:
                tags += '<span class="tag tag-safe">VAL</span> '
            html += f"""<tr>
<td>{t.event_name}</td>
<td>{t.event_type}</td>
<td>{Path(t.file).name}:{t.line}</td>
<td>{t.reward_type}</td>
<td class="{risk_class}">{t.risk_score:.0f}%</td>
<td>{tags}</td>
</tr>"""

        html += """</table></div>

<h2>Vulnerabilidades de Seguridad</h2>
<div class="box">
"""
        if self.security_issues:
            html += "<table><tr><th>Tipo</th><th>Severidad</th><th>Archivo</th><th>Descripcion</th></tr>"
            for issue in sorted(self.security_issues, key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x.severity, 4)):
                sev_class = 'critical' if issue.severity == 'CRITICAL' else ('danger' if issue.severity == 'HIGH' else ('warn' if issue.severity == 'MEDIUM' else 'safe'))
                html += f'<tr><td>{issue.issue_type}</td><td class="{sev_class}">{issue.severity}</td><td>{Path(issue.file).name}:{issue.line}</td><td>{issue.description}</td></tr>'
            html += "</table>"
        else:
            html += "<p class='safe'>No se detectaron vulnerabilidades.</p>"

        html += """</div>

<h2>Ofuscacion Detectada</h2>
<div class="box">
"""
        if self.obfuscations:
            html += "<table><tr><th>Tipo</th><th>Archivo</th><th>Confianza</th><th>Snippet</th></tr>"
            for obf in sorted(self.obfuscations, key=lambda x: x.confidence, reverse=True)[:30]:
                html += f'<tr><td>{obf.obf_type}</td><td>{Path(obf.file).name}:{obf.line}</td><td>{obf.confidence:.0%}</td><td><code>{obf.snippet[:80]}</code></td></tr>'
            html += "</table>"
        else:
            html += "<p class='safe'>No se detecto ofuscacion.</p>"

        html += """</div>

<h2>Server Callbacks</h2>
<div class="box">
"""
        if self.callbacks:
            html += "<table><tr><th>Callback</th><th>Archivo</th><th>Validacion</th><th>Riesgo</th></tr>"
            for cb in sorted(self.callbacks, key=lambda x: x.risk_score, reverse=True)[:30]:
                risk_class = 'danger' if cb.risk_score >= 70 else ('warn' if cb.risk_score >= 40 else 'safe')
                val = '<span class="safe">SI</span>' if cb.has_validation else '<span class="danger">NO</span>'
                html += f'<tr><td>{cb.name}</td><td>{Path(cb.file).name}:{cb.line}</td><td>{val}</td><td class="{risk_class}">{cb.risk_score:.0f}%</td></tr>'
            html += "</table>"
        else:
            html += "<p>No se detectaron server callbacks.</p>"

        html += """</div>

<div style="text-align:center;color:#333;margin-top:40px;">
<p>RED-SHADOW v4.0 - Advanced Forensic Engine | github.com/FardosESP/red-shadow</p>
</div>
</body></html>"""

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)

        self.print_status(f"Reporte HTML exportado: {fname}", "OK")
        self._pause()

    # ====================================================================
    # RECOMENDACIONES
    # ====================================================================

    def _generate_recommendations(self) -> List[str]:
        recs = []
        safe = [t for t in self.triggers.values() if t.risk_score < 40 and not t.is_honeypot]
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]

        if safe:
            top = sorted(safe, key=lambda t: t.risk_score)[:3]
            recs.append(f"Triggers recomendados: {', '.join(t.event_name for t in top)}")

        if honeypots:
            recs.append(f"EVITAR {len(honeypots)} honeypots: {', '.join(t.event_name for t in honeypots[:5])}")

        if self.anticheat_detected:
            names = ', '.join(self.anticheat_detected.keys())
            recs.append(f"Anticheats activos: {names} - tener precaucion extrema")

        crit_security = [s for s in self.security_issues if s.severity == 'CRITICAL']
        if crit_security:
            recs.append(f"{len(crit_security)} vulnerabilidades CRITICAS detectadas (SQL injection, tokens expuestos)")

        if self.obfuscations:
            high_conf = [o for o in self.obfuscations if o.confidence > 0.7]
            if high_conf:
                recs.append(f"{len(high_conf)} bloques de codigo ofuscado con alta confianza - posible proteccion extra")

        no_val_cbs = [c for c in self.callbacks if not c.has_validation]
        if no_val_cbs:
            recs.append(f"{len(no_val_cbs)} server callbacks sin validacion - potencialmente explotables")

        if not recs:
            recs.append("No se detectaron patrones de alto riesgo en el dump analizado.")

        return recs


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(BANNER)
        print(f"{C.R}  Uso: python red_shadow_destroyer_v4.py <ruta_dump> [--no-gui]{C.X}")
        print(f"{C.CN}  Ejemplo: python red_shadow_destroyer_v4.py C:\\FiveM_Dump{C.X}")
        print(f"{C.GR}  Opciones: --no-gui  Ejecutar sin menu interactivo (output directo){C.X}")
        sys.exit(1)

    dump_path = sys.argv[1]
    no_gui = '--no-gui' in sys.argv

    if not os.path.exists(dump_path):
        print(f"{C.R}[!] Ruta no encontrada: {dump_path}{C.X}")
        sys.exit(1)

    engine = RedShadowV4(dump_path)
    engine.print_banner()

    # Cargar archivos
    file_count = engine.load_files()
    if file_count == 0:
        print(f"{C.R}[!] No se encontraron archivos Lua en el dump{C.X}")
        sys.exit(1)

    # Ejecutar analisis completo
    engine.run_full_analysis()

    if no_gui:
        # Modo directo: mostrar resumen y exportar
        engine._view_summary()
        engine._export_json()
    else:
        # Modo interactivo: abrir menu GUI en CMD
        engine.interactive_menu()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.Y}[!] Interrupcion del usuario{C.X}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C.R}[!] Error fatal: {e}{C.X}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
