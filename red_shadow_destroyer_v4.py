#!/usr/bin/env python3
"""
RED-SHADOW DESTROYER v4.0 - Motor de Análisis Forense Avanzado
Análisis offline con Machine Learning y detección avanzada
"""

import re
import os
import sys
import hashlib
import math
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import json
import colorama
from colorama import Fore, Back, Style, init

init(autoreset=True)


# ============================================================================
# COLORES
# ============================================================================

class C:
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


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Trigger:
    event_name: str
    event_type: str
    file: str
    line: int
    handler_function: str
    parameters: List[str]
    has_validation: bool
    has_rate_limiting: bool
    has_reward_logic: bool
    reward_type: str
    has_ban_logic: bool
    is_honeypot: bool
    risk_score: float
    code_context: str
    validation_strength: str = 'none'   # none / weak / strong
    framework: str = ''                  # ESX / QBCore / vRP / ox / standalone
    observed_args: List[str] = None      # args seen at call sites


@dataclass
class Native:
    native_hash: str
    category: str
    file: str
    line: int


@dataclass
class Callback:
    name: str
    file: str
    line: int
    has_validation: bool
    risk_score: float


@dataclass
class Obfuscation:
    obf_type: str
    file: str
    line: int
    snippet: str
    confidence: float


@dataclass
class SecurityIssue:
    issue_type: str
    severity: str
    file: str
    line: int
    description: str
    snippet: str


@dataclass
class Manifest:
    resource_name: str
    file: str
    scripts_server: List[str]
    scripts_client: List[str]
    dependencies: List[str]
    exports: List[str]
    has_ui_page: bool


@dataclass
class Backdoor:
    backdoor_type: str
    file: str
    line: int
    severity: str
    confidence: float
    description: str
    code_snippet: str


@dataclass
class Anomaly:
    anomaly_type: str
    file: str
    line: int
    score: float
    description: str
    indicators: List[str]


@dataclass
class ComplexityMetrics:
    file: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    lines_of_code: int
    is_suspicious: bool


@dataclass
class RPLocation:
    coords: Tuple[float, float, float]
    activity_type: str
    location_name: str
    file_path: str
    line_number: int
    confidence: float
    metadata: Dict[str, Any]
    risk_score: float
    category: str
    context_code: str

    def to_dict(self) -> Dict[str, Any]:
        parts = self.activity_type.split('_')
        drug_type = parts[1] if len(parts) >= 2 and parts[0] == 'drug' else None
        return {
            'coords': {'x': self.coords[0], 'y': self.coords[1], 'z': self.coords[2]},
            'activity_type': self.activity_type,
            'drug_type': drug_type,
            'location_name': self.location_name,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'risk_score': self.risk_score,
            'category': self.category,
            'context_code': self.context_code,
        }

    def get_coordinate_string(self) -> str:
        return f"vector3({self.coords[0]:.2f}, {self.coords[1]:.2f}, {self.coords[2]:.2f})"

    def is_high_value_target(self) -> bool:
        return self.risk_score >= 70.0



# ============================================================================
# RED-SHADOW DESTROYER V4 ENGINE
# ============================================================================

class RedShadowV4:

    def __init__(self, dump_path: str):
        self.dump_path = Path(dump_path)
        self.lua_files: List[Path] = []
        self.total_lines = 0

        self.functions: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.triggers: Dict[str, Trigger] = {}
        self.callbacks: List[Callback] = []
        self.natives: List[Native] = []
        self.obfuscations: List[Obfuscation] = []
        self.security_issues: List[SecurityIssue] = []
        self.manifests: List[Manifest] = []

        self.anticheat_detected: Dict[str, Dict] = {}
        self.trigger_chains: List[List[str]] = []
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)
        self.code_hashes: Dict[str, List[str]] = defaultdict(list)

        self.backdoors: List[Backdoor] = []
        self.anomalies: List[Anomaly] = []
        self.complexity_metrics: List[ComplexityMetrics] = []
        self.rp_locations: List[RPLocation] = []
        self.webhooks: List[Dict] = []

        self.ml_predictions: Dict = {}
        self.entropy_scores: Dict = {}
        self.pattern_scores: Dict = {}

        self.vector3_pattern = re.compile(
            r'vector3\s*\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)',
            re.IGNORECASE
        )
        self.vector2_pattern = re.compile(
            r'vector2\s*\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)',
            re.IGNORECASE
        )
        self.table_coords_pattern = re.compile(
            r'\{\s*x\s*=\s*(-?\d+\.?\d*)\s*,\s*y\s*=\s*(-?\d+\.?\d*)\s*,\s*z\s*=\s*(-?\d+\.?\d*)\s*\}',
            re.IGNORECASE
        )
        self.config_locations_pattern = re.compile(
            r'(Config\.Locations|Config\.Zones|Locations)\s*=\s*\{',
            re.IGNORECASE
        )

        self.drug_type_keywords = {
            'weed':    ['weed', 'marihuana', 'marijuana', 'cannabis', 'hierba', 'mota', 'porro', 'joint',
                        'blunt', 'kush', 'weedplant', 'weed_plant', 'weed_sell', 'weed_process',
                        'weed_lab', 'weedlab', 'weed_field', 'weedfield'],
            'meth':    ['meth', 'metanfetamina', 'crystal', 'cristal', 'ice', 'hielo', 'cook', 'cocinar',
                        'meth_lab', 'methlab', 'meth_cook', 'meth_sell', 'meth_process', 'meth_field',
                        'methamphetamine', 'speed'],
            'cocaine': ['cocaine', 'cocaina', 'coca', 'coke', 'perico', 'polvo', 'blow', 'snow',
                        'cocaine_lab', 'cocainelab', 'cocaine_sell', 'cocaine_process', 'cocaine_field',
                        'coke_lab', 'cokelab', 'coke_sell'],
            'heroin':  ['heroin', 'heroina', 'smack', 'junk', 'horse', 'dope', 'opium', 'opio',
                        'heroin_lab', 'heroinlab', 'heroin_sell', 'heroin_process', 'heroin_field',
                        'opiate', 'opiato'],
            'mdma':    ['mdma', 'ecstasy', 'extasis', 'molly', 'pill', 'pastilla', 'xtc',
                        'mdma_lab', 'mdma_sell', 'mdma_process', 'pill_lab'],
            'lsd':     ['lsd', 'acid', 'acido', 'trip', 'tabs', 'blotter', 'lsd_lab', 'lsd_sell'],
            'mush':    ['mushroom', 'hongo', 'shroom', 'psilocybin', 'mush', 'fungi',
                        'mushroom_field', 'shroom_sell'],
            'generic': ['droga', 'drug', 'narcotic', 'narcotico', 'ilegal', 'illegal', 'cartel',
                        'dealer', 'traficante', 'trafficker', 'drug_sell', 'drug_lab', 'druglab',
                        'drug_field', 'drugfield', 'drug_process', 'narcotrafic', 'drug_deal',
                        'plantar', 'plant', 'sembrar', 'cultivar', 'grow', 'seed', 'siembra',
                        'procesar', 'process', 'empaquetar', 'package', 'refinar', 'refine',
                        'vender', 'sell', 'narcotrafic'],
        }

        self.drug_keywords = {
            'planting':   ['plantar', 'plant', 'sembrar', 'cultivar', 'grow', 'seed', 'siembra'],
            'processing': ['procesar', 'process', 'empaquetar', 'package', 'refinar', 'refine', 'transformar', 'transform'],
            'selling':    ['vender', 'sell', 'comprar', 'buy', 'trade', 'comercio', 'negocio', 'narcotrafic', 'drug_deal'],
        }

        self.illegal_activity_keywords = {
            'robbery': ['robo', 'rob', 'robbery', 'atraco', 'heist', 'steal', 'robar', 'asalto', 'assault',
                        'robstore', 'rob_store', 'robbank', 'rob_bank', 'fleeca', 'pacific', 'paleto',
                        'jewelry', 'joyeria', 'tienda_robo', 'convenience_rob', 'gasstation_rob'],
            'heist': ['heist', 'golpe', 'coup', 'bigheist', 'big_heist', 'bankheist', 'bank_heist',
                      'casino_heist', 'casinoheist', 'doomsday', 'cayo', 'island_heist',
                      'setup', 'prep', 'preparacion', 'finale', 'final_cut'],
            'chop_shop': ['chopshop', 'chop_shop', 'chop', 'desguace', 'despiece', 'scrapyard', 'chatarra',
                          'stolen_car', 'coche_robado', 'vehiculo_robado', 'car_theft', 'robo_coche',
                          'carjack', 'carjacking', 'boost', 'boosted', 'export_vehicle'],
            'arms_dealing': ['arms', 'armas_ilegales', 'illegal_weapons', 'black_market_weapons',
                             'gunrunning', 'gun_running', 'traficante_armas', 'arms_dealer', 'arms_deal',
                             'weapon_traffic', 'trafico_armas', 'illegal_gun', 'illegal_weapon',
                             'underground_weapons', 'bunker', 'weapon_bunker', 'weapon_storage'],
            'illegal_mining': ['mineria_ilegal', 'illegal_mining', 'mina_ilegal', 'illegal_mine',
                               'mineral_ilegal', 'illegal_mineral', 'black_market_ore', 'ore_theft',
                               'robo_mineral', 'contraband_ore', 'illegal_quarry', 'cantera_ilegal'],
            'illegal_trade': ['mercado_negro', 'black_market', 'blackmarket', 'contrabando', 'contraband',
                              'smuggling', 'smuggle', 'trafico', 'trafficking', 'fence', 'perista',
                              'underground_market', 'illegal_trade', 'comercio_ilegal',
                              'black_money', 'dinero_negro', 'money_laundering', 'lavado', 'launder',
                              'dirty_money', 'dinero_sucio'],
        }

        self.job_keywords = {
            'mining':   ['minero', 'miner', 'pickaxe', 'pico', 'mineral', 'quarry', 'cantera', 'mining'],
            'fishing':  ['pesca', 'fish', 'pescador', 'fisher', 'rod', 'cana', 'anzuelo', 'hook'],
            'farming':  ['granja', 'farm', 'granjero', 'farmer', 'harvest', 'cosecha', 'campo', 'field'],
            'trucking': ['camion', 'truck', 'delivery', 'entrega', 'transporte', 'transport'],
            'taxi':     ['taxi', 'cab', 'passenger', 'pasajero', 'conductor', 'driver'],
            'mechanic': ['mecanico', 'mechanic', 'repair', 'reparar', 'taller', 'workshop'],
        }

        self.shop_keywords = {
            'weapon':   ['arma', 'weapon', 'gun', 'pistol', 'rifle', 'pistola', 'fusil', 'armeria'],
            'clothing': ['ropa', 'cloth', 'outfit', 'vestir', 'tienda de ropa', 'clothing'],
            'vehicle':  ['vehiculo', 'vehicle', 'car', 'coche', 'dealership', 'concesionario', 'auto'],
            'general':  ['tienda', 'shop', 'store', 'market', 'compra', 'mercado', '24/7'],
        }

        self.service_keywords = {
            'atm':      ['atm', 'cajero', 'cash', 'efectivo', 'fleeca'],
            'bank':     ['banco', 'bank', 'deposit', 'deposito', 'cuenta', 'account'],
            'garage':   ['garaje', 'parking', 'estacionamiento', 'aparcamiento', 'impound'],
            'hospital': ['hospital', 'doctor', 'medic', 'ems', 'medico', 'pillbox'],
            'police':   ['policia', 'police', 'comisaria', 'station', 'lspd', 'bcso', 'sheriff'],
        }

    # -------------------------------------------------------------------------
    # FILE LOADING
    # -------------------------------------------------------------------------

    def load_files(self) -> int:
        self.lua_files = list(self.dump_path.rglob('*.lua'))
        return len(self.lua_files)

    @staticmethod
    def print_status(msg: str, status: str = "INFO"):
        colors = {"INFO": Fore.CYAN, "OK": Fore.GREEN, "WARN": Fore.YELLOW,
                  "ERROR": Fore.RED, "SCAN": Fore.MAGENTA, "CRIT": Fore.LIGHTRED_EX}
        color = colors.get(status, Fore.WHITE)
        print(f"{color}[{status}] {msg}{Style.RESET_ALL}")

    def print_banner(self):
        print(BANNER)



    # -------------------------------------------------------------------------
    # AMBANI TRIGGERS PARSER
    # -------------------------------------------------------------------------

    def parse_ambani_triggers_lua(self, triggers_lua_path: str) -> int:
        path = Path(triggers_lua_path)
        if not path.exists():
            return 0
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return 0

        imported = 0
        seen: Set[str] = set(self.triggers.keys())

        for m in re.finditer(
            r'(?:RegisterNetEvent|AddEventHandler|TriggerEvent|TriggerServerEvent)\s*\(\s*["\']([^"\']+)["\']',
            content, re.IGNORECASE
        ):
            name = m.group(1).strip()
            if name and name not in seen:
                seen.add(name)
                self.triggers[name] = self._build_trigger_from_name(
                    name, str(path), content[:m.start()].count('\n') + 1)
                imported += 1

        for m in re.finditer(r'["\']([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-:\.]+)["\']', content):
            name = m.group(1).strip()
            if name and name not in seen and ':' in name:
                seen.add(name)
                self.triggers[name] = self._build_trigger_from_name(
                    name, str(path), content[:m.start()].count('\n') + 1)
                imported += 1

        for m in re.finditer(
            r'\{\s*name\s*=\s*["\']([^"\']+)["\'](?:[^}]*type\s*=\s*["\']([^"\']*)["\'])?(?:[^}]*source\s*=\s*["\']([^"\']*)["\'])?',
            content, re.IGNORECASE
        ):
            name = m.group(1).strip()
            etype = m.group(2) or 'RegisterNetEvent'
            source = m.group(3) or str(path)
            if name and name not in seen:
                seen.add(name)
                self.triggers[name] = self._build_trigger_from_name(
                    name, source, content[:m.start()].count('\n') + 1, event_type=etype)
                imported += 1

        return imported

    def _build_trigger_from_name(self, name: str, file: str, line: int,
                                  event_type: str = 'RegisterNetEvent') -> 'Trigger':
        name_lower = name.lower()
        money_kw = ['addmoney', 'givemoney', 'setmoney', 'addcash', 'addbank', 'salary',
                    'pagar', 'dinero', 'cash', 'bank', 'wage', 'paycheck']
        item_kw  = ['additem', 'giveitem', 'addweapon', 'giveweapon', 'inventory', 'item', 'weapon', 'drug', 'droga']
        xp_kw    = ['addxp', 'addexp', 'addlevel', 'xp', 'experience', 'level']

        has_reward, reward_type = False, ''
        if any(k in name_lower for k in money_kw):
            has_reward, reward_type = True, 'money'
        elif any(k in name_lower for k in item_kw):
            has_reward, reward_type = True, 'item'
        elif any(k in name_lower for k in xp_kw):
            has_reward, reward_type = True, 'xp'

        honeypot_kw = ['givemoney', 'addcash', 'spawnvehicle', 'giveweapon',
                       'setgodmode', 'adminmenu', 'freeitems', 'unlimitedmoney',
                       'hackserver', 'getadmin', 'bypass']
        ban_kw = ['ban', 'kick', 'report', 'detect', 'honeypot', 'trap']
        has_ban = any(k in name_lower for k in ban_kw)
        is_honeypot = has_ban and any(k in name_lower for k in honeypot_kw)

        risk = self._calculate_risk_score(False, False, has_reward, has_ban)
        return Trigger(
            event_name=name, event_type=event_type, file=file, line=line,
            handler_function='(ambani_dump)', parameters=[],
            has_validation=False, has_rate_limiting=False,
            has_reward_logic=has_reward, reward_type=reward_type,
            has_ban_logic=has_ban, is_honeypot=is_honeypot,
            risk_score=risk,
            code_context='[Importado desde triggers.lua de Ambani — sin contexto de código]',
        )

    # -------------------------------------------------------------------------
    # ANALYSIS PHASES
    # -------------------------------------------------------------------------

    def extract_functions(self):
        func_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\('
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    self.total_lines += len(lines)
                    for i, line in enumerate(lines, 1):
                        for match in re.finditer(func_pattern, line):
                            self.functions[match.group(1)].append((str(lua_file), i))
            except Exception:
                pass

    def detect_triggers(self):
        patterns = {
            'RegisterNetEvent': r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\']',
            'AddEventHandler':  r'AddEventHandler\s*\(\s*["\']([^"\']+)["\']',
            'RegisterServerCallback': r'(?:ESX|QBCore)\.(?:RegisterServerCallback|Functions\.CreateCallback)\s*\(\s*["\']([^"\']+)["\']',
            'RegisterCommand':  r'RegisterCommand\s*\(\s*["\']([^"\']+)["\']',
        }
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                lines = content.split('\n')
                for event_type, pattern in patterns.items():
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        event_name = match.group(1)
                        line_num = content[:match.start()].count('\n') + 1
                        start_line = max(0, line_num - 1)
                        end_line = min(len(lines), line_num + 19)
                        context = '\n'.join(lines[start_line:end_line])
                        self.triggers[event_name] = self._analyze_trigger(
                            event_name, event_type, str(lua_file), line_num, context)
            except Exception:
                pass

    def _analyze_trigger(self, name: str, event_type: str, file: str,
                          line: int, context: str) -> Trigger:
        validation_patterns = [
            r'if\s+not\s+source', r'if\s+source\s*==\s*["\']',
            r'IsPlayerAceAllowed', r'xPlayer\.getGroup',
            r'QBCore\.Functions\.HasPermission', r'Player\.PlayerData\.job',
            r'CheckPlayerPermission', r'IsAdmin', r'HasPermission',
        ]
        has_validation = any(re.search(p, context, re.I) for p in validation_patterns)

        rate_limit_patterns = [r'cooldown', r'lastUsed', r'rateLimiter',
                                r'throttle', r'debounce', r'os\.time\(\)\s*-\s*last']
        has_rate_limiting = any(re.search(p, context, re.I) for p in rate_limit_patterns)

        reward_patterns = {
            'money': [r'addMoney', r'addAccountMoney', r'AddMoney', r'giveMoney', r'setMoney',
                      r'\.addMoney', r'\.addAccountMoney'],
            'item':  [r'addItem', r'giveItem', r'AddItem', r'addInventoryItem',
                      r'\.addItem', r'\.addInventoryItem', r'\.giveItem'],
            'xp':    [r'addXP', r'addExperience', r'addLevel', r'\.addXP',
                      r'\.addExperience', r'\.addLevel'],
        }
        has_reward, reward_type = False, ''
        for rtype, pats in reward_patterns.items():
            if any(re.search(p, context, re.I) for p in pats):
                has_reward, reward_type = True, rtype
                break

        ban_patterns = [r'BanPlayer', r'DropPlayer.*["\']cheat', r'DropPlayer.*["\']hack',
                        r'DropPlayer.*["\']exploit', r'TriggerEvent.*ban', r'webhook.*banned']
        has_ban = any(re.search(p, context, re.I) for p in ban_patterns)

        attractive_names = ['giveMoney', 'addCash', 'spawnVehicle', 'giveWeapon',
                            'setGodMode', 'adminMenu', 'freeItems', 'unlimitedMoney']
        is_honeypot = has_ban and any(a.lower() in name.lower() for a in attractive_names)

        params = self._extract_parameters(context)
        handler_match = re.search(r'function\s*\(([^)]*)\)', context)
        handler_func = handler_match.group(0) if handler_match else 'anonymous'
        risk = self._calculate_risk_score(has_validation, has_rate_limiting, has_reward, has_ban)

        return Trigger(
            event_name=name, event_type=event_type, file=file, line=line,
            handler_function=handler_func, parameters=params,
            has_validation=has_validation, has_rate_limiting=has_rate_limiting,
            has_reward_logic=has_reward, reward_type=reward_type,
            has_ban_logic=has_ban, is_honeypot=is_honeypot,
            risk_score=risk, code_context=context[:500],
            validation_strength=self._calc_validation_strength(has_validation, context),
            framework=self._detect_framework(file, context),
            observed_args=[],
        )

    def _extract_parameters(self, context: str) -> List[str]:
        match = re.search(r'function\s*\(([^)]*)\)', context)
        if match:
            return [p.strip() for p in match.group(1).split(',') if p.strip()]
        return []

    def _calculate_risk_score(self, has_validation: bool, has_rate_limiting: bool,
                               has_reward: bool, has_ban: bool) -> float:
        score = 30.0
        if not has_validation:   score += 30.0
        if not has_rate_limiting: score += 20.0
        if has_reward:            score += 15.0
        if has_ban:               score += 5.0
        return min(100.0, score)

    def detect_obfuscation(self):
        patterns = {
            'loadstring':  (r'loadstring\s*\(', 0.9),
            'string.char': (r'string\.char\s*\(', 0.8),
            'base64':      (r'base64', 0.7),
            'xor_cipher':  (r'bit\.bxor', 0.8),
            'bytecode':    (r'\\x[0-9a-fA-F]{2}', 0.9),
            'hex_strings': (r'\\[0-9]{3}', 0.6),
        }
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for obf_type, (pattern, confidence) in patterns.items():
                        if re.search(pattern, line, re.I):
                            self.obfuscations.append(Obfuscation(
                                obf_type=obf_type, file=str(lua_file), line=i,
                                snippet=line.strip()[:100], confidence=confidence))
            except Exception:
                pass

    def analyze_natives(self):
        native_categories = {
            'WEAPON':  ['GIVE_WEAPON', 'ADD_AMMO', 'SET_WEAPON', 'REMOVE_WEAPON'],
            'MONEY':   ['ADD_MONEY', 'SET_MONEY', 'GIVE_MONEY'],
            'PLAYER':  ['SET_PLAYER', 'GET_PLAYER', 'NETWORK_GET_PLAYER'],
            'VEHICLE': ['CREATE_VEHICLE', 'SET_VEHICLE', 'DELETE_VEHICLE'],
            'WORLD':   ['CREATE_OBJECT', 'DELETE_OBJECT', 'SET_ENTITY'],
            'NETWORK': ['TRIGGER_SERVER', 'TRIGGER_CLIENT', 'NETWORK_'],
        }
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for match in re.finditer(r'0x[0-9A-Fa-f]{8,16}', line):
                        category = 'UNKNOWN'
                        for cat, keywords in native_categories.items():
                            if any(kw in line.upper() for kw in keywords):
                                category = cat
                                break
                        self.natives.append(Native(
                            native_hash=match.group(0), category=category,
                            file=str(lua_file), line=i))
            except Exception:
                pass

    def analyze_callbacks(self):
        patterns = [
            r'(?:ESX|QBCore)\.(?:RegisterServerCallback|Functions\.CreateCallback)\s*\(\s*["\']([^"\']+)["\']',
            r'lib\.callback\.register\s*\(\s*["\']([^"\']+)["\']',
        ]
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                lines = content.split('\n')
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.I):
                        cb_name = match.group(1)
                        line_num = content[:match.start()].count('\n') + 1
                        start = max(0, line_num - 1)
                        end = min(len(lines), line_num + 10)
                        context = '\n'.join(lines[start:end])
                        has_val = bool(re.search(r'if\s+not\s+source', context, re.I))
                        self.callbacks.append(Callback(
                            name=cb_name, file=str(lua_file), line=line_num,
                            has_validation=has_val, risk_score=30.0 if has_val else 70.0))
            except Exception:
                pass

    def detect_security_issues(self):
        issues = [
            ('SQL_INJECTION',       'CRITICAL', r'MySQL\.Async\.execute.*%s'),
            ('COMMAND_INJECTION',   'CRITICAL', r'os\.execute\s*\('),
            ('PATH_TRAVERSAL',      'HIGH',     r'\.\.\/'),
            ('HARDCODED_PASSWORD',  'HIGH',     r'password\s*=\s*["\'][^"\']{6,}["\']'),
            ('INSECURE_RANDOM',     'MEDIUM',   r'math\.random\s*\('),
            ('EVAL_USAGE',          'CRITICAL', r'loadstring\s*\('),
        ]
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for issue_type, severity, pattern in issues:
                        if re.search(pattern, line, re.I):
                            self.security_issues.append(SecurityIssue(
                                issue_type=issue_type, severity=severity,
                                file=str(lua_file), line=i,
                                description=f"Posible {issue_type.replace('_', ' ').lower()}",
                                snippet=line.strip()[:150]))
            except Exception:
                pass

    def analyze_manifests(self):
        for lua_file in self.lua_files:
            if lua_file.name in ['fxmanifest.lua', '__resource.lua']:
                try:
                    with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    resource_name = lua_file.parent.name

                    def extract_strings(blocks):
                        items = []
                        for block in blocks:
                            items.extend(re.findall(r'["\']([^"\']+)["\']', block))
                        return items

                    ss = re.findall(r'server_scripts?\s*{([^}]+)}', content, re.I | re.S)
                    cs = re.findall(r'client_scripts?\s*{([^}]+)}', content, re.I | re.S)
                    ds = re.findall(r'dependencies?\s*{([^}]+)}', content, re.I | re.S)
                    es = re.findall(r'exports?\s*{([^}]+)}', content, re.I | re.S)

                    self.manifests.append(Manifest(
                        resource_name=resource_name, file=str(lua_file),
                        scripts_server=extract_strings(ss), scripts_client=extract_strings(cs),
                        dependencies=extract_strings(ds), exports=extract_strings(es),
                        has_ui_page=bool(re.search(r'ui_page', content, re.I))))
                except Exception:
                    pass

    def analyze_trigger_chains(self):
        trigger_graph = defaultdict(list)
        for trigger_name, trigger in self.triggers.items():
            trigger_calls = re.findall(
                r'Trigger(?:Server)?Event\s*\(\s*["\']([^"\']+)["\']',
                trigger.code_context, re.I)
            for called in trigger_calls:
                if called in self.triggers:
                    trigger_graph[trigger_name].append(called)
                    self.cross_references[called].add(trigger.file)

        visited = set()
        MAX_CHAINS = 200

        def dfs(node, path):
            if len(self.trigger_chains) >= MAX_CHAINS:
                return
            if node in visited or len(path) > 8:
                return
            if len(path) > 1:
                self.trigger_chains.append(path.copy())
            visited.add(node)
            for neighbor in trigger_graph.get(node, []):
                dfs(neighbor, path + [neighbor])

        for trigger_name in trigger_graph:
            dfs(trigger_name, [trigger_name])

    def detect_code_clones(self):
        BLOCK = 8
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('--')]
                for i in range(0, len(lines) - BLOCK, BLOCK):
                    block = ' '.join(lines[i:i + BLOCK])
                    if len(block) < 40:
                        continue
                    h = hashlib.md5(block.encode()).hexdigest()
                    self.code_hashes[h].append(str(lua_file))
            except Exception:
                pass



    # -------------------------------------------------------------------------
    # ADVANCED ANALYSIS
    # -------------------------------------------------------------------------

    def calculate_cyclomatic_complexity(self, code: str) -> int:
        control_structures = [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\brepeat\b',
                               r'\band\b', r'\bor\b', r'\belseif\b']
        complexity = 1
        for pattern in control_structures:
            complexity += len(re.findall(pattern, code, re.I))
        return complexity

    def calculate_nesting_depth(self, code: str) -> int:
        max_depth, current_depth = 0, 0
        for line in code.split('\n'):
            if re.search(r'\b(if|while|for|function|repeat)\b', line, re.I):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            if re.search(r'\bend\b', line, re.I):
                current_depth = max(0, current_depth - 1)
        return max_depth

    def analyze_code_complexity(self):
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                lines = content.split('\n')
                cyclomatic = self.calculate_cyclomatic_complexity(content)
                nesting = self.calculate_nesting_depth(content)
                loc = len([l for l in lines if l.strip() and not l.strip().startswith('--')])
                cognitive = cyclomatic + (nesting * 2)
                is_suspicious = (cyclomatic > 50 or nesting > 8 or
                                  (loc > 100 and cyclomatic / max(loc, 1) > 0.5))
                self.complexity_metrics.append(ComplexityMetrics(
                    file=str(lua_file), cyclomatic_complexity=cyclomatic,
                    cognitive_complexity=cognitive, nesting_depth=nesting,
                    lines_of_code=loc, is_suspicious=is_suspicious))
                if is_suspicious:
                    self.anomalies.append(Anomaly(
                        anomaly_type='high_complexity', file=str(lua_file), line=1,
                        score=min(cyclomatic / 2, 100),
                        description=f'Complejidad anormalmente alta (CC:{cyclomatic}, Nesting:{nesting})',
                        indicators=[f'cyclomatic={cyclomatic}', f'nesting={nesting}', f'cognitive={cognitive}']))
            except Exception:
                pass

    def detect_backdoors(self):
        backdoor_patterns = [
            ('remote_code_execution', r'loadstring\s*\(\s*.*WebRequest', 0.95, 'CRITICAL'),
            ('remote_code_execution', r'load\s*\(\s*.*HttpPost', 0.90, 'CRITICAL'),
            ('command_injection',     r'os\.execute\s*\(\s*.*\.\.\s*', 0.85, 'CRITICAL'),
            ('command_injection',     r'io\.popen\s*\(\s*.*\.\.\s*', 0.85, 'CRITICAL'),
            ('privilege_escalation',  r'setmetatable.*_G', 0.80, 'HIGH'),
            ('privilege_escalation',  r'debug\.getupvalue', 0.75, 'HIGH'),
            ('privilege_escalation',  r'debug\.setupvalue', 0.75, 'HIGH'),
            ('data_exfiltration',     r'PerformHttpRequest.*password', 0.90, 'CRITICAL'),
            ('data_exfiltration',     r'WebRequest.*token', 0.85, 'HIGH'),
            ('persistence',           r'RegisterNetEvent.*__cfx_internal', 0.80, 'HIGH'),
            ('persistence',           r'AddEventHandler.*playerConnecting.*ban', 0.70, 'HIGH'),
        ]
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for backdoor_type, pattern, confidence, severity in backdoor_patterns:
                        if re.search(pattern, line, re.I):
                            self.backdoors.append(Backdoor(
                                backdoor_type=backdoor_type, file=str(lua_file), line=i,
                                severity=severity, confidence=confidence,
                                description=f'Posible {backdoor_type.replace("_", " ")}',
                                code_snippet=line.strip()[:150]))
            except Exception:
                pass

    def detect_behavioral_anomalies(self):
        for trigger_name, trigger in self.triggers.items():
            indicators = []
            anomaly_score = 0.0

            generic_names = ['event', 'handler', 'callback', 'process', 'handle']
            if any(gn in trigger_name.lower() for gn in generic_names):
                if len(trigger.code_context) > 500:
                    indicators.append('generic_name_complex_logic')
                    anomaly_score += 20

            if not trigger.has_validation:
                operations = len(re.findall(r'[=\+\-\*/]', trigger.code_context))
                if operations > 20:
                    indicators.append('no_validation_many_operations')
                    anomaly_score += 25

            if trigger.has_reward_logic and not trigger.has_rate_limiting:
                indicators.append('reward_no_ratelimit')
                anomaly_score += 30

            if trigger.has_ban_logic and trigger.has_reward_logic:
                indicators.append('honeypot_pattern')
                anomaly_score += 40

            code_len = len(trigger.code_context)
            if code_len < 50 or code_len > 2000:
                indicators.append('anomalous_code_length')
                anomaly_score += 15

            native_count = len(re.findall(r'0x[0-9A-Fa-f]{8,16}', trigger.code_context))
            if native_count > 10:
                indicators.append('excessive_natives')
                anomaly_score += 20

            if anomaly_score > 30:
                self.anomalies.append(Anomaly(
                    anomaly_type='suspicious_trigger', file=trigger.file, line=trigger.line,
                    score=min(anomaly_score, 100),
                    description=f'Trigger "{trigger_name}" muestra patrones anomalos',
                    indicators=indicators))

    def detect_webhooks(self):
        discord_pattern = re.compile(
            r'https?://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]+',
            re.IGNORECASE)
        generic_pattern = re.compile(
            r'https?://[a-zA-Z0-9._/-]+/(?:webhook|hook|notify|log|alert)[^\s\'"]*',
            re.IGNORECASE)
        seen_urls: set = set()
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for pattern, wtype in [(discord_pattern, 'discord'), (generic_pattern, 'http')]:
                        for m in pattern.finditer(line):
                            url = m.group(0).rstrip('\'",) ')
                            if url in seen_urls:
                                continue
                            seen_urls.add(url)
                            self.webhooks.append({
                                'url': url, 'webhook_type': wtype,
                                'file': str(lua_file), 'line': i})
            except Exception:
                pass



    # -------------------------------------------------------------------------
    # ANTICHEAT FINGERPRINTING
    # -------------------------------------------------------------------------

    def fingerprint_anticheats(self):
        AC_INTEL = {
            # ---- COMMERCIAL ACs ----
            'ElectronAC': {
                'patterns': [
                    r'electronac', r'electron_ac', r'electron-ac',
                    r'electron_anticheat', r'electronanticheat',
                    r'electron-services', r'electron_services',
                ],
                'description': 'AC comercial moderno. Deteccion client-side + server-side. Muy usado en 2024-2025.',
                'detection_method': 'Fingerprinting de executors + monitoreo de eventos + checksums',
                'disable_method': (
                    'Ambani Resource Stopper → detener "ElectronAC" o "electron_ac". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'ElectronAC tiene listener onResourceStop — Stop Resource puede enviar alerta al webhook del admin. '
                    'Destroy Resource elimina el recurso sin triggear el handler.'
                ),
                'bypass_notes': (
                    'ElectronAC detecta executors conocidos por fingerprint. '
                    'Si Ambani no esta en su lista negra, los triggers server-side funcionan con el AC activo. '
                    'Detenerlo solo si hay bans activos por el executor.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'FiveGuard': {
                'patterns': [
                    r'fg_anticheat', r'fiveguard', r'fg_core', r'fg_client',
                    r'fg_server', r'fiveguard_core', r'fiveguard_client',
                ],
                'description': 'AC comercial popular. Monitorea eventos del cliente y checksums de recursos.',
                'detection_method': 'Monitoreo de eventos + checksums de recurso + screenshots',
                'disable_method': (
                    'Ambani Resource Stopper → detener "fg_anticheat" o "fiveguard". '
                    'Si no aparece, buscar "fg_core" o "fg_client". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'Stop Resource triggea onResourceStop y puede loggear el evento en el webhook del admin.'
                ),
                'bypass_notes': (
                    'FiveGuard no valida logica server-side. '
                    'Los triggers de dinero/items funcionan igual con el AC activo. '
                    'Solo detenerlo si banea por spam de eventos.'
                ),
                'safe_to_disable': True,
                'risk_level': 'MEDIUM',
            },
            'Guardian': {
                'patterns': [
                    r'guardian', r'grd_anticheat', r'guardian_ac', r'grd_core',
                    r'guardian_core', r'guardian_client', r'guardian_server',
                ],
                'description': 'AC con sistema de reputacion y analisis de patrones de comportamiento.',
                'detection_method': 'Analisis de comportamiento + historial de jugador',
                'disable_method': (
                    'Ambani Resource Stopper → detener "guardian" o "grd_anticheat". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'Guardian tiene onResourceStop listener — Stop Resource envia alerta al webhook del admin. '
                    'Destroy Resource elimina el recurso sin triggear el handler de onResourceStop.'
                ),
                'bypass_notes': (
                    'Si no puedes detenerlo: Guardian detecta patrones repetitivos. '
                    'Espaciar las llamadas y no repetir el mismo trigger mas de 3 veces seguidas. '
                    'Sesion corta e intensa es menos detectable que spam prolongado.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'WaveShield': {
                'patterns': [
                    r'waveshield', r'wave_shield', r'ws_anticheat', r'ws_core', r'wshield',
                    r'waveshield_core', r'waveshield_client', r'waveshield_server',
                ],
                'description': 'AC comercial con deteccion de executors (Eulen, redENGINE, Skript.GG).',
                'detection_method': 'Fingerprinting de executors + deteccion de inyeccion Lua client-side',
                'disable_method': (
                    'Ambani Resource Stopper → detener "waveshield" o "ws_anticheat". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'WaveShield tiene onResourceStop listener — Stop Resource envia alerta al webhook del admin. '
                    'Destroy Resource elimina el recurso sin triggear el handler de onResourceStop.'
                ),
                'bypass_notes': (
                    'WaveShield detecta executors por fingerprint del cliente, no por triggers server-side. '
                    'Si Ambani esta actualizado y no detectado, los triggers de recompensa funcionan aunque WaveShield este activo. '
                    'Detenerlo solo si hay bans activos. '
                    'Si el servidor tiene anti-resource-stop, ejecutar triggers directamente sin detener WaveShield.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'SentinelAC': {
                'patterns': [
                    r'sentinelac', r'sentinel_ac', r'sentinel-ac',
                    r'sentinel_anticheat', r'sentinelanticheat',
                    r'caronet', r'sentinel_core', r'sentinel_client',
                ],
                'description': 'AC cloud-based con ML. Detecta patrones de comportamiento y executors.',
                'detection_method': 'ML cloud-based + analisis de comportamiento + checksums',
                'disable_method': (
                    'Ambani Resource Stopper → detener "SentinelAC" o "sentinel_ac". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'SentinelAC reporta al servidor cloud — Destroy Resource es mas limpio.'
                ),
                'bypass_notes': (
                    'SentinelAC es cloud-based, parte de la deteccion ocurre en servidores externos. '
                    'Detener el recurso local puede no ser suficiente si ya hay datos enviados al cloud. '
                    'Espaciar triggers y evitar patrones repetitivos.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'FIREAC': {
                'patterns': [
                    r'fireac', r'fire_ac', r'fireanticheat', r'fire_anticheat',
                    r'fireac_core', r'fireac_client', r'fireac_server',
                    r'amirrezajaberi',
                ],
                'description': 'AC avanzado open-source con deteccion server-side y client-side.',
                'detection_method': 'Analisis server-side + client-side heuristico + ML',
                'disable_method': (
                    'Ambani Resource Stopper → detener "fireac" o "fire_ac". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'Stop Resource puede triggear onResourceStop y loggear el evento.'
                ),
                'bypass_notes': (
                    'FIREAC tiene deteccion server-side. Incluso detenido, algunos checks pueden persistir en otros recursos. '
                    'Espaciar triggers. Evitar spam de eventos.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'Badger-Anticheat': {
                'patterns': [
                    r'badger.anticheat', r'badger_anticheat', r'badgerac',
                    r'badger_ac', r'badger-ac', r'badgeranti',
                ],
                'description': 'AC open-source basico. Detecta props blacklisteados y eventos sospechosos.',
                'detection_method': 'Blacklist de props + monitoreo de eventos basico',
                'disable_method': (
                    'Ambani Resource Stopper → detener "badger-anticheat" o "badgerac". '
                    'Destroy Resource es suficiente — no usar Stop Resource.'
                ),
                'bypass_notes': 'Badger-AC es basico. Sin el recurso activo, no hay deteccion. Triggers de recompensa son explotables libremente.',
                'safe_to_disable': True,
                'risk_level': 'LOW',
            },
            'PhoenixAC': {
                'patterns': [
                    r'phoenixac', r'phoenix_ac', r'phoenix-ac',
                    r'phoenix_anticheat', r'phoenixanticheat',
                    r'pac_core', r'pac_client', r'pac_server',
                ],
                'description': 'AC con analisis de comportamiento y screenshots bajo demanda.',
                'detection_method': 'Analisis de comportamiento + screenshots + validacion de eventos',
                'disable_method': (
                    'Ambani Resource Stopper → detener "PhoenixAC" o "phoenix_ac". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'PhoenixAC monitorea paradas de recursos criticos.'
                ),
                'bypass_notes': (
                    'PhoenixAC detecta patrones repetitivos. '
                    'Espaciar llamadas. Sesion corta es menos detectable.'
                ),
                'safe_to_disable': True,
                'risk_level': 'HIGH',
            },
            'MxShield': {
                'patterns': [
                    r'mxshield', r'mx_shield', r'mx-shield',
                    r'mx_anticheat', r'mxanticheat', r'mx_ac',
                ],
                'description': 'AC con +100 detecciones. Anti-executor, anti-teleport, anti-godmode.',
                'detection_method': 'Deteccion de executors + validacion de eventos + anti-script-stop',
                'disable_method': (
                    'Ambani Resource Stopper → detener "mxshield" o "mx_shield". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'MxShield tiene Anti Script start/stop — puede detectar la parada del recurso.'
                ),
                'bypass_notes': (
                    'MxShield tiene Anti Anticheat stop — puede detectar intentos de parar el AC. '
                    'Si no puedes detenerlo, ejecutar triggers directamente. '
                    'La validacion server-side es independiente del AC client-side.'
                ),
                'safe_to_disable': False,
                'risk_level': 'HIGH',
            },
            'PegasusAC': {
                'patterns': [
                    r'pegasusac', r'pegasus_ac', r'pegasus-ac',
                    r'pegasus_anticheat', r'pegasusanticheat',
                ],
                'description': 'AC con proteccion de eventos, anti-Lua menu y proteccion de spawn.',
                'detection_method': 'Proteccion de eventos + anti-Lua menu + validacion de spawn',
                'disable_method': (
                    'Ambani Resource Stopper → detener "PegasusAC" o "pegasus_ac". '
                    'Destroy Resource es suficiente.'
                ),
                'bypass_notes': 'PegasusAC es de dificultad media. Triggers server-side sin validacion siguen siendo explotables.',
                'safe_to_disable': True,
                'risk_level': 'MEDIUM',
            },
            'IcarusAC': {
                'patterns': [
                    r'icarusac', r'icarus_ac', r'icarus-ac',
                    r'icarus_anticheat', r'icarusanticheat',
                    r'icarusadvanced', r'icarus_advanced',
                ],
                'description': 'AC open-source avanzado para FiveM.',
                'detection_method': 'Deteccion de exploits + validacion de eventos',
                'disable_method': (
                    'Ambani Resource Stopper → detener "IcarusAC" o "icarus_ac". '
                    'Destroy Resource es suficiente.'
                ),
                'bypass_notes': 'IcarusAC es open-source. Revisar el codigo para entender las validaciones especificas del servidor.',
                'safe_to_disable': True,
                'risk_level': 'MEDIUM',
            },
            'PrettyPackets': {
                'patterns': [
                    r'prettypackets', r'pretty_packets', r'prettypacketac',
                    r'pretty_packet', r'ppac',
                ],
                'description': 'AC moderno con capa de seguridad framework-aware.',
                'detection_method': 'Analisis de paquetes + validacion de eventos + framework integration',
                'disable_method': (
                    'Ambani Resource Stopper → detener "PrettyPackets" o "prettypacketac". '
                    'Destroy Resource es suficiente.'
                ),
                'bypass_notes': 'PrettyPackets es relativamente nuevo (2025). Triggers sin validacion siguen siendo explotables.',
                'safe_to_disable': True,
                'risk_level': 'MEDIUM',
            },
            'Qprotect': {
                'patterns': [
                    r'qprotect', r'q_protect', r'q-protect',
                    r'qprotect_core', r'qp_main', r'qprotect_monitor',
                ],
                'description': 'AC con logging exhaustivo y alertas de admin via webhook.',
                'detection_method': 'Logging completo + alertas webhook + monitoreo de recursos',
                'disable_method': (
                    'Ambani Resource Stopper → detener "Qprotect". '
                    'IMPORTANTE: usar Destroy Resource, NO Stop Resource. '
                    'Qprotect monitorea paradas de recursos y envia alertas al admin.'
                ),
                'bypass_notes': (
                    'Qprotect se enfoca en logging y alertas. '
                    'Bloquear el webhook de Discord a nivel de red es mas seguro que detener el recurso. '
                    'Evitar detener componentes de logging core.'
                ),
                'safe_to_disable': False,
                'risk_level': 'HIGH',
            },
            'esx_anticheat': {
                'patterns': [
                    r'esx_anticheat', r'esx_ac', r'esx-anticheat',
                    r'esx_cheatdetect', r'esx_protection',
                ],
                'description': 'AC basico para ESX. Deteccion de eventos sospechosos en el framework.',
                'detection_method': 'Validacion de eventos ESX + checks de inventario',
                'disable_method': (
                    'Ambani Resource Stopper → detener "esx_anticheat". '
                    'Destroy Resource es suficiente. Riesgo bajo.'
                ),
                'bypass_notes': 'esx_anticheat es basico. Sin el recurso activo, no hay deteccion adicional a la del framework.',
                'safe_to_disable': True,
                'risk_level': 'LOW',
            },
            'sasAC': {
                'patterns': [
                    r'sasac', r'sas_ac', r'sas-ac',
                    r'sas_anticheat', r'sasanticheat',
                ],
                'description': 'AC open-source para FiveM.',
                'detection_method': 'Deteccion de exploits basica + validacion de eventos',
                'disable_method': (
                    'Ambani Resource Stopper → detener "sasAC" o "sas_ac". '
                    'Destroy Resource es suficiente.'
                ),
                'bypass_notes': 'sasAC es open-source y basico. Facil de bypassear.',
                'safe_to_disable': True,
                'risk_level': 'LOW',
            },
            # ---- FRAMEWORKS (no son ACs pero tienen validaciones) ----
            'es_extended': {
                'patterns': [
                    r'es_extended', r'esx_core', r'esx\.getsharedobject',
                    r'ESX\s*=\s*exports', r'ESX\.GetSharedObject',
                ],
                'description': 'Framework ESX — no es un AC pero tiene validaciones en algunos eventos criticos.',
                'detection_method': 'Validacion de permisos por job/grupo + checks de inventario',
                'disable_method': (
                    'NO detener con Resource Stopper — rompe todo el servidor. '
                    'Usar los triggers de la seccion Explotables que ya tienen validacion debil o nula. '
                    'ESX tiene muchos handlers sin verificacion de permisos.'
                ),
                'bypass_notes': (
                    'ESX valida algunos eventos con xPlayer.getJob() o xPlayer.getMoney(). '
                    'Los triggers marcados como SIN VAL en Explotables no tienen estas validaciones — son los mas seguros.'
                ),
                'safe_to_disable': False,
                'risk_level': 'FRAMEWORK',
            },
            'qb-core': {
                'patterns': [
                    r'qb-core', r'qbcore', r'qb_core', r'QBCore\.Functions',
                    r'QBCore\.GetCoreObject', r'QBCore\s*=\s*exports',
                ],
                'description': 'Framework QBCore — sistema de permisos mas estricto que ESX.',
                'detection_method': 'QBCore.Functions.HasPermission + checks de job',
                'disable_method': (
                    'NO detener con Resource Stopper — rompe todo el servidor. '
                    'Buscar triggers en Explotables marcados como SIN VAL. '
                    'QBCore tiene mejor validacion que ESX, pero recursos de terceros mal configurados siguen siendo vulnerables.'
                ),
                'bypass_notes': (
                    'Priorizar triggers de recursos de terceros (jobs, minijuegos, eventos) sobre los core. '
                    'Los recursos custom del servidor suelen tener validacion debil o nula.'
                ),
                'safe_to_disable': False,
                'risk_level': 'FRAMEWORK',
            },
        }

        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                content_lower = content.lower()
                for ac_name, ac_data in AC_INTEL.items():
                    if ac_name in self.anticheat_detected:
                        continue
                    for pattern in ac_data['patterns']:
                        if re.search(pattern, content_lower, re.IGNORECASE):
                            self.anticheat_detected[ac_name] = {
                                'description':      ac_data['description'],
                                'detection_method': ac_data['detection_method'],
                                'disable_method':   ac_data['disable_method'],
                                'bypass_notes':     ac_data.get('bypass_notes', ''),
                                'safe_to_disable':  ac_data['safe_to_disable'],
                                'risk_level':       ac_data['risk_level'],
                                'confidence':       0.85,
                                'file':             str(lua_file),
                            }
                            break
            except Exception:
                pass

        # --- Second pass: scan folder names for obfuscated ACs ---
        seen_paths = set()
        for lua_file in self.lua_files:
            parts = Path(lua_file).parts
            for part in parts:
                part_lower = part.lower()
                if part_lower in seen_paths:
                    continue
                seen_paths.add(part_lower)
                for ac_name, ac_data in AC_INTEL.items():
                    if ac_name in self.anticheat_detected:
                        continue
                    for pattern in ac_data['patterns']:
                        if re.search(pattern, part_lower, re.IGNORECASE):
                            self.anticheat_detected[ac_name] = {
                                'description':      ac_data['description'],
                                'detection_method': ac_data['detection_method'] + ' [folder-name match]',
                                'disable_method':   ac_data['disable_method'],
                                'bypass_notes':     ac_data.get('bypass_notes', ''),
                                'safe_to_disable':  ac_data['safe_to_disable'],
                                'risk_level':       ac_data['risk_level'],
                                'confidence':       0.70,
                                'file':             str(lua_file),
                            }
                            break

    # -------------------------------------------------------------------------
    # FRAMEWORK DETECTION + VALIDATION STRENGTH
    # -------------------------------------------------------------------------

    def _detect_framework(self, file: str, context: str) -> str:
        file_lower = file.lower()
        ctx_lower = context.lower()
        if any(p in file_lower or p in ctx_lower for p in ['esx', 'es_extended', 'esx_core']):
            return 'ESX'
        if any(p in file_lower or p in ctx_lower for p in ['qb-core', 'qbcore', 'qb_core']):
            return 'QBCore'
        if any(p in file_lower or p in ctx_lower for p in ['vrp']):
            return 'vRP'
        if any(p in file_lower or p in ctx_lower for p in ['ox_inventory', 'ox_lib', 'ox_core']):
            return 'ox'
        return 'standalone'

    def _calc_validation_strength(self, has_validation: bool, context: str) -> str:
        if not has_validation:
            return 'none'
        strong_patterns = [
            r'IsPlayerAceAllowed', r'QBCore\.Functions\.HasPermission',
            r'xPlayer\.getGroup', r'CheckPlayerPermission',
        ]
        import re as _re
        if any(_re.search(p, context, _re.I) for p in strong_patterns):
            return 'strong'
        return 'weak'

    # -------------------------------------------------------------------------
    # OBFUSCATION DECODE
    # -------------------------------------------------------------------------

    def detect_string_obfuscation(self):
        """Decode string.char(...) sequences in Lua files."""
        import re as _re
        char_pattern = _re.compile(r'string\.char\(([0-9,\s]+)\)')
        results = []
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                for m in char_pattern.finditer(code):
                    try:
                        decoded = ''.join(chr(int(n.strip())) for n in m.group(1).split(',') if n.strip())
                        if len(decoded) > 3:
                            results.append({'file': str(lua_file), 'type': 'string.char', 'decoded': decoded[:200]})
                    except Exception:
                        pass
            except Exception:
                pass
        self.obfuscated_strings = results

    # -------------------------------------------------------------------------
    # CALL GRAPH
    # -------------------------------------------------------------------------

    def build_call_graph(self):
        """Record observed args at TriggerServerEvent call sites."""
        import re as _re
        call_pattern = _re.compile(
            r'TriggerServerEvent\s*\(\s*["\'](.*?)["\'\']\s*,?\s*(.*?)\)',
            _re.IGNORECASE | _re.DOTALL)
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                for m in call_pattern.finditer(code):
                    name = m.group(1)
                    args_raw = m.group(2).strip()
                    if name in self.triggers and args_raw:
                        args = [a.strip() for a in args_raw.split(',') if a.strip()][:5]
                        existing = self.triggers[name].observed_args or []
                        self.triggers[name].observed_args = list(dict.fromkeys(existing + args))[:10]
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # RESOURCE SUMMARY
    # -------------------------------------------------------------------------

    def build_resource_summary(self) -> Dict:
        """Aggregate trigger stats per top-level resource folder."""
        summary: Dict[str, Dict] = {}
        for trigger in self.triggers.values():
            parts = Path(trigger.file).parts
            resource = parts[1] if len(parts) > 1 else parts[0]
            if resource not in summary:
                summary[resource] = {
                    'resource': resource,
                    'trigger_count': 0,
                    'exploitable': 0,
                    'honeypots': 0,
                    'max_risk': 0.0,
                    'framework': trigger.framework or 'standalone',
                    'triggers': [],
                }
            e = summary[resource]
            e['trigger_count'] += 1
            if trigger.has_reward_logic and not trigger.is_honeypot:
                e['exploitable'] += 1
            if trigger.is_honeypot:
                e['honeypots'] += 1
            if trigger.risk_score > e['max_risk']:
                e['max_risk'] = trigger.risk_score
            e['triggers'].append(trigger.event_name)
        return summary

    def match_known_triggers(self) -> List[Dict]:
        results = []
        detected_names = set(self.triggers.keys())

        for known in self.KNOWN_TRIGGERS_DB:
            name = known['name']
            if name in detected_names:
                t = self.triggers[name]
                results.append({
                    **known,
                    'found_in_dump': True, 'partial_match': False,
                    'file': t.file, 'line': t.line,
                    'has_validation': t.has_validation,
                    'has_ban_logic': t.has_ban_logic,
                    'is_honeypot': t.is_honeypot,
                    'dump_risk_score': t.risk_score,
                    'ready_to_use': not t.is_honeypot and not t.has_validation,
                })
            else:
                suffix = name.split(':')[-1].lower()
                if len(suffix) <= 4:
                    continue
                for pname in detected_names:
                    if suffix in pname.lower():
                        t = self.triggers[pname]
                        results.append({
                            **known,
                            'name': pname, 'known_name': name,
                            'found_in_dump': True, 'partial_match': True,
                            'file': t.file, 'line': t.line,
                            'has_validation': t.has_validation,
                            'has_ban_logic': t.has_ban_logic,
                            'is_honeypot': t.is_honeypot,
                            'dump_risk_score': t.risk_score,
                            'ready_to_use': not t.is_honeypot and not t.has_validation,
                        })
                        break

        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        results.sort(key=lambda x: (
            0 if x.get('ready_to_use') else 1,
            risk_order.get(x.get('risk', 'LOW'), 9)
        ))
        return results



    # -------------------------------------------------------------------------
    # RP LOCATION DETECTION
    # -------------------------------------------------------------------------

    def _extract_vector3_coords(self, code: str, file_path: str) -> List[Dict]:
        if not code:
            return []
        matches = []
        for match in self.vector3_pattern.finditer(code):
            try:
                x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
                if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)):
                    continue
                if any(abs(v) > 100000 for v in (x, y, z)):
                    continue
                line_num = code[:match.start()].count('\n') + 1
                matches.append({'coords': (x, y, z), 'position': match.start(),
                                 'line_number': line_num, 'pattern_type': 'vector3', 'metadata': {}})
            except (ValueError, IndexError):
                continue
        return matches

    def _extract_vector2_coords(self, code: str, file_path: str) -> List[Dict]:
        if not code:
            return []
        matches = []
        for match in self.vector2_pattern.finditer(code):
            try:
                x, y = float(match.group(1)), float(match.group(2))
                if any(math.isnan(v) or math.isinf(v) for v in (x, y)):
                    continue
                if any(abs(v) > 100000 for v in (x, y)):
                    continue
                line_num = code[:match.start()].count('\n') + 1
                matches.append({'coords': (x, y, 0.0), 'position': match.start(),
                                 'line_number': line_num, 'pattern_type': 'vector2', 'metadata': {}})
            except (ValueError, IndexError):
                continue
        return matches

    def _extract_table_coords(self, code: str, file_path: str) -> List[Dict]:
        if not code:
            return []
        matches = []
        for match in self.table_coords_pattern.finditer(code):
            try:
                x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
                if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)):
                    continue
                if any(abs(v) > 100000 for v in (x, y, z)):
                    continue
                line_num = code[:match.start()].count('\n') + 1
                matches.append({'coords': (x, y, z), 'position': match.start(),
                                 'line_number': line_num, 'pattern_type': 'table', 'metadata': {}})
            except (ValueError, IndexError):
                continue
        return matches

    def _extract_config_locations(self, code: str, file_path: str) -> List[Dict]:
        matches = []
        for match in self.config_locations_pattern.finditer(code):
            try:
                line_num = code[:match.start()].count('\n') + 1
                lines = code.split('\n')
                start_line = max(0, line_num - 1)
                end_line = min(len(lines), line_num + 10)
                context = '\n'.join(lines[start_line:end_line])
                for ctx_match in (self._extract_vector3_coords(context, file_path) +
                                   self._extract_vector2_coords(context, file_path) +
                                   self._extract_table_coords(context, file_path)):
                    ctx_match['metadata']['config_block'] = True
                    ctx_match['line_number'] += start_line
                    matches.append(ctx_match)
            except Exception:
                continue
        return matches

    def _detect_drug_type(self, context: str) -> str:
        ctx = context.lower()
        priority = ['weed', 'meth', 'cocaine', 'heroin', 'mdma', 'lsd', 'mush', 'generic']
        for dtype in priority:
            keywords = self.drug_type_keywords.get(dtype, [])
            if any(kw in ctx for kw in keywords):
                return dtype
        return 'generic'

    def _classify_activity(self, context: str) -> Tuple[str, float]:
        try:
            if not context:
                return ('unknown', 0.0)
            context_lower = context.lower()

            for operation, keywords in self.drug_keywords.items():
                keyword_count = sum(1 for kw in keywords if kw in context_lower)
                if keyword_count > 0:
                    confidence = min(0.6 + (keyword_count * 0.15), 1.0)
                    drug_type = self._detect_drug_type(context)
                    return (f"drug_{drug_type}_{operation}", confidence)

            for dtype, kws in self.drug_type_keywords.items():
                if dtype == 'generic':
                    continue
                if any(kw in context_lower for kw in kws):
                    return (f"drug_{dtype}_generic", 0.65)

            for illegal_type, keywords in self.illegal_activity_keywords.items():
                keyword_count = sum(1 for kw in keywords if kw in context_lower)
                if keyword_count > 0:
                    confidence = min(0.55 + (keyword_count * 0.15), 0.95)
                    return (f"illegal_{illegal_type}", confidence)

            for job_type, keywords in self.job_keywords.items():
                keyword_count = sum(1 for kw in keywords if kw in context_lower)
                if keyword_count > 0:
                    return (f"job_{job_type}", min(0.5 + (keyword_count * 0.15), 0.95))

            for shop_type, keywords in self.shop_keywords.items():
                keyword_count = sum(1 for kw in keywords if kw in context_lower)
                if keyword_count > 0:
                    return (f"shop_{shop_type}", min(0.5 + (keyword_count * 0.15), 0.95))

            for service_type, keywords in self.service_keywords.items():
                keyword_count = sum(1 for kw in keywords if kw in context_lower)
                if keyword_count > 0:
                    return (f"service_{service_type}", min(0.5 + (keyword_count * 0.15), 0.95))

            return ("unknown", 0.3)
        except Exception:
            return ('unknown', 0.0)

    def _parse_location_metadata(self, context: str) -> dict:
        if not context:
            return {}
        metadata = {}
        try:
            m = re.search(r'(?:radius|distance|DrawDistance)\s*=\s*(-?\d+\.?\d*)', context, re.IGNORECASE)
            if m:
                try: metadata['radius'] = float(m.group(1))
                except: pass
            m = re.search(r'(?:blip\.)?sprite\s*=\s*(\d+)', context, re.IGNORECASE)
            if m:
                try: metadata['blip_sprite'] = int(m.group(1))
                except: pass
            m = re.search(r'(?:blip\.)?color\s*=\s*(\d+)', context, re.IGNORECASE)
            if m:
                try: metadata['blip_color'] = int(m.group(1))
                except: pass
            m = re.search(r'(?:blip\.)?(?:name|label)\s*=\s*["\']([^"\']+)["\']', context, re.IGNORECASE)
            if m:
                try: metadata['blip_name'] = m.group(1)
                except: pass
            m = re.search(r'zone\s*=\s*["\']([^"\']+)["\']', context, re.IGNORECASE)
            if m:
                try: metadata['zone_name'] = m.group(1)
                except: pass
        except Exception:
            pass
        return metadata

    def _calculate_location_risk(self, activity_type: str, category: str,
                                   metadata: dict, context: str) -> float:
        risk_score = 0.0
        category_risk = {'illegal': 50.0, 'legal_job': 20.0, 'shop': 15.0, 'service': 10.0, 'unknown': 5.0}
        risk_score += category_risk.get(category, 5.0)
        al = activity_type.lower()
        if 'drug' in al:                                    risk_score += 30.0
        if 'robbery' in al or 'heist' in al:               risk_score += 25.0
        if 'chop_shop' in al:                              risk_score += 20.0
        if 'arms_dealing' in al:                           risk_score += 25.0
        if 'illegal_trade' in al or 'illegal_mining' in al: risk_score += 15.0
        if 'weapon' in al:                                 risk_score += 20.0
        ctx = context.lower()
        risk_score -= sum(5.0 for i in ['permission', 'check', 'validate', 'auth', 'admin'] if i in ctx)
        risk_score += sum(10.0 for p in ['TriggerServerEvent', 'RegisterNetEvent', 'AddEventHandler'] if p in context)
        if metadata.get('radius', 0) > 50.0:               risk_score += 5.0
        if metadata.get('blip_sprite') is not None:        risk_score += 5.0
        risk_score = max(0.0, min(100.0, risk_score))
        if 'drug' in al:                                   risk_score = max(50.0, risk_score)
        return risk_score

    def _categorize_location(self, activity_type: str) -> str:
        al = activity_type.lower()
        if al.startswith('drug_'):    return 'illegal'
        if al.startswith('illegal_'): return 'illegal'
        if al.startswith('job_'):     return 'legal_job'
        if al.startswith('shop_'):    return 'shop'
        if al.startswith('service_'): return 'service'
        return 'unknown'

    def _extract_location_name(self, context: str, coords: tuple, activity_type: str) -> str:
        for pattern in [r'name\s*=\s*["\']([^"\']+)["\']',
                         r'label\s*=\s*["\']([^"\']+)["\']',
                         r'(?:blip\.)?name\s*=\s*["\']([^"\']+)["\']']:
            m = re.search(pattern, context, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                if name and len(name) > 1:
                    return name
        parts = activity_type.split('_')
        if len(parts) >= 2:
            return f"{parts[0].title()} {parts[1].title()} ({coords[0]:.0f},{coords[1]:.0f})"
        return f"Location ({coords[0]:.0f},{coords[1]:.0f})"

    def _deduplicate_locations(self, locations: list) -> list:
        if not locations:
            return []
        unique = []
        for loc in locations:
            is_dup = False
            for u in unique:
                dx = loc.coords[0] - u.coords[0]
                dy = loc.coords[1] - u.coords[1]
                dz = loc.coords[2] - u.coords[2]
                if (dx*dx + dy*dy + dz*dz) ** 0.5 < 5.0:
                    is_dup = True
                    break
            if not is_dup:
                unique.append(loc)
        return unique

    def _sanitize_string(self, s: str, max_len: int = 500) -> str:
        if not s:
            return ''
        s = str(s)
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
        return s[:max_len]

    def _is_false_positive_location(self, activity_type: str, file_path: str, context: str) -> bool:
        fp = file_path.lower().replace('\\', '/') if file_path else ''
        ctx = context.lower() if context else ''
        false_positive_scripts = [
            'casino', 'rcore_casino', 'horse', 'racing', 'race',
            'lottery', 'poker', 'blackjack', 'slots', 'roulette', 'bingo',
            'minigame', 'mini_game', 'arcade', 'bowling', 'golf',
            'cinema', 'theater', 'nightclub', 'strip_club', 'stripclub',
        ]
        for fp_script in false_positive_scripts:
            if fp_script in fp:
                if 'generic' in activity_type or activity_type.endswith('_generic'):
                    return True
                if 'casino' in fp or 'horse' in fp or 'racing' in fp:
                    return True
        casino_context_patterns = [
            'horsechairs', 'horse_chairs', 'horsedisplay', 'horse_display',
            'horseheading', 'casinochips', 'casino_chips', 'slotmachine',
            'dealercoords', 'racingcoords', 'laptime', 'vehiclereplacementcoords',
        ]
        for pattern in casino_context_patterns:
            if pattern in ctx:
                return True
        return False

    def _get_script_name(self, file_path: str) -> str:
        if not file_path:
            return 'unknown'
        parts = file_path.replace('\\', '/').split('/')
        if len(parts) >= 2:
            return parts[-2]
        return parts[-1] if parts else 'unknown'

    def detect_all_locations(self):
        print("\n[*] Phase 17: Detecting Illegal Locations...")
        if not self.lua_files:
            print("[!] No Lua files loaded.")
            return

        locations = []
        for lua_file in self.lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                file_path = str(lua_file)

                coord_matches = []
                coord_matches.extend(self._extract_vector3_coords(code, file_path))
                coord_matches.extend(self._extract_vector2_coords(code, file_path))
                coord_matches.extend(self._extract_table_coords(code, file_path))
                coord_matches.extend(self._extract_config_locations(code, file_path))

                for match in coord_matches:
                    try:
                        coords = match['coords']
                        line_number = match['line_number']
                        lines = code.split('\n')
                        start_line = max(0, line_number - 6)
                        end_line = min(len(lines), line_number + 5)
                        context = '\n'.join(lines[start_line:end_line])

                        activity_type, confidence = self._classify_activity(context)
                        activity_type = self._sanitize_string(activity_type, max_len=100)

                        if not (activity_type.startswith('drug_') or activity_type.startswith('illegal_')):
                            continue
                        if self._is_false_positive_location(activity_type, file_path, context):
                            continue

                        metadata = self._parse_location_metadata(context)
                        location_name = self._extract_location_name(context, coords, activity_type)
                        location_name = self._sanitize_string(location_name, max_len=200)
                        category = self._categorize_location(activity_type)
                        risk_score = self._calculate_location_risk(activity_type, category, metadata, context)
                        context_code = self._sanitize_string(context[:500], max_len=500)

                        locations.append(RPLocation(
                            coords=coords, activity_type=activity_type,
                            location_name=location_name, file_path=file_path,
                            line_number=line_number, confidence=confidence,
                            metadata=metadata, risk_score=risk_score,
                            category=category, context_code=context_code))
                    except Exception:
                        continue
            except Exception as e:
                print(f"[!] Warning: Error reading {lua_file}: {e}")
                continue

        locations = self._deduplicate_locations(locations)
        locations.sort(key=lambda loc: loc.risk_score, reverse=True)
        self.rp_locations = locations
        print(f"[+] Detected {len(self.rp_locations)} illegal locations")



    # -------------------------------------------------------------------------
    # FULL ANALYSIS + EXPORT
    # -------------------------------------------------------------------------

    def run_full_analysis(self):
        print("\n[*] Iniciando análisis completo...")
        self.extract_functions()
        self.detect_triggers()
        self.detect_obfuscation()
        self.detect_string_obfuscation()
        self.analyze_natives()
        self.analyze_callbacks()
        self.detect_security_issues()
        self.analyze_manifests()
        self.fingerprint_anticheats()
        self.analyze_trigger_chains()
        self.detect_code_clones()
        self.analyze_code_complexity()
        self.detect_backdoors()
        self.detect_behavioral_anomalies()
        self.detect_webhooks()
        self.build_call_graph()
        self.detect_all_locations()
        print("\n[+] Análisis completo finalizado.")

    def _generate_recommendations(self) -> List[str]:
        recs = []
        triggers_list = list(self.triggers.values())

        no_val = sum(1 for t in triggers_list if not t.has_validation)
        if no_val > 0:
            recs.append(f"{no_val} triggers SIN validación server-side — ejecutar directamente desde Ambani executor")

        with_reward = sum(1 for t in triggers_list if t.has_reward_logic and not t.is_honeypot)
        if with_reward > 0:
            recs.append(f"{with_reward} triggers con lógica de recompensa detectados — ver sección Explotables")

        honeypots = sum(1 for t in triggers_list if t.is_honeypot)
        if honeypots > 0:
            recs.append(f"{honeypots} HONEYPOTS detectados — NO ejecutar, ban inmediato. Ver sección Honeypots")

        known_ready = len([k for k in self.match_known_triggers() if k.get('ready_to_use')])
        if known_ready > 0:
            recs.append(f"{known_ready} triggers de Known DB listos para usar — ver sección Known DB")

        high_risk_safe = sum(1 for t in triggers_list if t.risk_score >= 70 and not t.is_honeypot)
        if high_risk_safe > 0:
            recs.append(f"{high_risk_safe} triggers de alto riesgo sin honeypot — revisar en sección Triggers")

        if self.anticheat_detected:
            names = ', '.join(self.anticheat_detected.keys())
            recs.append(f"Anticheats activos: {names} — ver sección Anticheats para instrucciones")

        if not recs:
            recs.append("Análisis completado — revisar sección Triggers para oportunidades manuales")

        return recs

    def export_json(self, output_path: str):
        data = {
            'tool': 'RED-SHADOW Destroyer v4.0',
            'dump_path': str(self.dump_path),
            'triggers': {k: asdict(v) for k, v in self.triggers.items()},
            'callbacks': [asdict(c) for c in self.callbacks],
            'natives': [asdict(n) for n in self.natives],
            'obfuscations': [asdict(o) for o in self.obfuscations],
            'security_issues': [asdict(s) for s in self.security_issues],
            'manifests': [asdict(m) for m in self.manifests],
            'anticheat_detected': self.anticheat_detected,
            'trigger_chains': self.trigger_chains,
            'backdoors': [asdict(b) for b in self.backdoors],
            'anomalies': [asdict(a) for a in self.anomalies],
            'rp_locations': [loc.to_dict() for loc in self.rp_locations],
            'webhooks': self.webhooks,
            'known_triggers': self.match_known_triggers(),
            'recommendations': self._generate_recommendations(),
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"[+] JSON exportado: {output_path}")

    # Legacy stubs for web_gui compatibility
    def interactive_menu(self):
        print("[!] Modo interactivo no disponible en esta versión. Usar web dashboard.")

    def _view_summary(self):
        print(f"\n[RESUMEN] Triggers: {len(self.triggers)} | Anticheats: {len(self.anticheat_detected)} | Spots: {len(self.rp_locations)}")

    def _export_json(self):
        self.export_json('red_shadow_output.json')

    def _export_html(self):
        print("[!] Export HTML no disponible. Usar web dashboard.")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    no_gui = '--no-gui' in sys.argv
    cmd_gui = '--cmd-gui' in sys.argv

    if len(sys.argv) < 2 or sys.argv[1].startswith('--'):
        if no_gui or cmd_gui:
            print(BANNER)
            print(f"{C.R}  Uso: python red_shadow_destroyer_v4.py <ruta_dump> [opciones]{C.X}")
            sys.exit(1)
        try:
            from web_gui import launch_web_gui
            launch_web_gui(None, auto_open=True)
        except ImportError:
            print(f"{C.R}[!] web_gui.py no encontrado.{C.X}")
            sys.exit(1)
        return

    dump_path = sys.argv[1]

    if not os.path.exists(dump_path):
        print(f"{C.R}[!] Ruta no encontrada: {dump_path}{C.X}")
        sys.exit(1)

    engine = RedShadowV4(dump_path)
    engine.print_banner()

    file_count = engine.load_files()
    if file_count == 0:
        print(f"{C.R}[!] No se encontraron archivos Lua en el dump{C.X}")
        sys.exit(1)

    engine.run_full_analysis()

    if no_gui:
        engine._view_summary()
        engine._export_json()
    elif cmd_gui:
        engine.interactive_menu()
    else:
        try:
            from web_gui import launch_web_gui
            launch_web_gui(engine, auto_open=True)
        except ImportError:
            print(f"{C.R}[!] web_gui.py no encontrado.{C.X}")
            engine._view_summary()


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
