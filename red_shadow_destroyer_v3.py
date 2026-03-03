#!/usr/bin/env python3
"""
RED-SHADOW "Destroyer" v3.0 - Terminal Hacker Edition
Herramienta profesional de análisis forense de volcados redENGINE
"""

import os
import re
import json
import sys
import time
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import colorama
from colorama import Fore, Back, Style, init

# Inicializar colorama para Windows
init(autoreset=True)

# ============================================================================
# COLORES Y ESTILOS
# ============================================================================

class Colors:
    """Paleta de colores para terminal"""
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    GRAY = Fore.LIGHTBLACK_EX
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_RED = Fore.LIGHTRED_EX
    BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    BRIGHT_CYAN = Fore.LIGHTCYAN_EX
    
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    DIM = Style.DIM

# ============================================================================
# ASCII ART Y BANNERS
# ============================================================================

BANNER = f"""{Colors.BRIGHT_RED}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         ██████╗ ███████╗██████╗      ███████╗██╗  ██╗        ║
║         ██╔══██╗██╔════╝██╔══██╗     ██╔════╝██║  ██║        ║
║         ██████╔╝█████╗  ██║  ██║     ███████╗███████║        ║
║         ██╔══██╗██╔══╝  ██║  ██║     ╚════██║██╔══██║        ║
║         ██║  ██║███████╗██████╔╝     ███████║██║  ██║        ║
║         ╚═╝  ╚═╝╚══════╝╚═════╝      ╚══════╝╚═╝  ╚═╝        ║
║                                                               ║
║              RED-SHADOW "Destroyer" v3.0                     ║
║         Advanced FiveM Dump Analysis Engine                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}"""

SEPARATOR = f"{Colors.CYAN}{'═' * 65}{Colors.RESET}"
SUBSEPARATOR = f"{Colors.GRAY}{'─' * 65}{Colors.RESET}"

# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class TriggerEvent:
    event_name: str
    file: str
    line: int
    handler_function: str
    has_validation: bool
    has_reward_logic: bool
    has_ban_logic: bool
    reward_type: str
    risk_score: float
    is_honeypot: bool

# ============================================================================
# ANALIZADOR AVANZADO
# ============================================================================

class AdvancedLuaAnalyzer:
    """Motor de análisis avanzado con interfaz terminal"""
    
    def __init__(self, dump_path: str):
        self.dump_path = Path(dump_path)
        self.files: Dict[str, str] = {}
        self.triggers: Dict[str, TriggerEvent] = {}
        self.total_lines = 0
        self.current_progress = 0
        
    def print_banner(self):
        """Mostrar banner inicial"""
        print(BANNER)
        print(f"{Colors.CYAN}[*] Iniciando análisis forense de volcado redENGINE...{Colors.RESET}\n")
    
    def print_status(self, message: str, status: str = "INFO"):
        """Imprimir mensaje de estado"""
        status_colors = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "SCAN": Colors.MAGENTA,
        }
        
        color = status_colors.get(status, Colors.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status == "SCAN":
            print(f"{color}[{timestamp}] ▶ {message}{Colors.RESET}", end='\r')
        else:
            print(f"{color}[{timestamp}] [{status:7}] {message}{Colors.RESET}")
    
    def print_progress_bar(self, current: int, total: int, label: str = ""):
        """Mostrar barra de progreso"""
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"{Colors.CYAN}[{bar}] {percent:5.1f}% {label}{Colors.RESET}", end='\r')
    
    def load_files(self):
        """Cargar archivos Lua"""
        self.print_status("Buscando archivos Lua...", "SCAN")
        
        lua_files = list(self.dump_path.rglob("*.lua"))
        total_files = len(lua_files)
        
        print(f"\n{Colors.GREEN}[+] Encontrados {total_files} archivos Lua{Colors.RESET}")
        
        for idx, lua_file in enumerate(lua_files, 1):
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self.files[str(lua_file)] = content
                    self.total_lines += len(content.split('\n'))
                
                self.print_progress_bar(idx, total_files, f"Cargando: {lua_file.name}")
            except Exception as e:
                self.print_status(f"Error leyendo {lua_file.name}", "ERROR")
        
        print(f"\n{Colors.GREEN}[+] {len(self.files)} archivos cargados ({self.total_lines} líneas){Colors.RESET}\n")
    
    def analyze_triggers(self):
        """Analizar triggers"""
        self.print_status("Analizando triggers...", "INFO")
        
        trigger_patterns = {
            'RegisterNetEvent': r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\']',
            'AddEventHandler': r'AddEventHandler\s*\(\s*["\']([^"\']+)["\']',
        }
        
        total_files = len(self.files)
        
        for file_idx, (file_path, content) in enumerate(self.files.items(), 1):
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern_type, pattern in trigger_patterns.items():
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        event_name = match.group(1)
                        
                        # Extraer contexto
                        context_start = max(0, match.start() - 500)
                        context_end = min(len(content), match.end() + 500)
                        context = content[context_start:context_end]
                        
                        # Analizar
                        has_validation = self.has_validation_logic(context)
                        has_reward = self.detect_reward_logic(context)
                        has_ban = self.has_ban_logic(context)
                        reward_type = self.classify_reward(context)
                        risk_score = self.calculate_risk(event_name, has_validation, has_reward, has_ban)
                        is_honeypot = has_ban and not has_reward
                        
                        self.triggers[event_name] = TriggerEvent(
                            event_name=event_name,
                            file=file_path,
                            line=line_num,
                            handler_function="unknown",
                            has_validation=has_validation,
                            has_reward_logic=has_reward,
                            has_ban_logic=has_ban,
                            reward_type=reward_type,
                            risk_score=risk_score,
                            is_honeypot=is_honeypot
                        )
            
            self.print_progress_bar(file_idx, total_files, f"Analizando: {Path(file_path).name}")
        
        print(f"\n{Colors.GREEN}[+] {len(self.triggers)} triggers detectados{Colors.RESET}\n")
    
    def has_ban_logic(self, code: str) -> bool:
        ban_keywords = ['DropPlayer', 'Ban', 'kick', 'banear', 'TriggerClientEvent']
        return any(keyword in code for keyword in ban_keywords)
    
    def has_validation_logic(self, code: str) -> bool:
        validation_keywords = ['if', 'check', 'verify', 'validate', 'assert']
        return any(keyword in code for keyword in validation_keywords)
    
    def detect_reward_logic(self, code: str) -> bool:
        reward_keywords = ['addMoney', 'addItem', 'giveWeapon', 'addInventory']
        return any(keyword in code for keyword in reward_keywords)
    
    def classify_reward(self, code: str) -> str:
        if 'addMoney' in code or 'money' in code.lower():
            return 'MONEY'
        elif 'addItem' in code or 'inventory' in code.lower():
            return 'ITEMS'
        elif 'giveWeapon' in code or 'weapon' in code.lower():
            return 'WEAPONS'
        return 'UNKNOWN'
    
    def calculate_risk(self, event_name: str, has_validation: bool, 
                      has_reward: bool, has_ban: bool) -> float:
        risk = 50.0
        
        if has_validation:
            risk -= 20
        if has_reward:
            risk += 15
        if has_ban:
            risk += 30
        
        suspicious = ['admin', 'ban', 'kick', 'trap', 'check']
        if any(s in event_name.lower() for s in suspicious):
            risk += 25
        
        return max(0, min(100, risk))
    
    def print_results(self):
        """Imprimir resultados"""
        print(SEPARATOR)
        print(f"{Colors.BRIGHT_CYAN}RESULTADOS DEL ANÁLISIS{Colors.RESET}")
        print(SEPARATOR)
        
        # Clasificar triggers
        safe = [t for t in self.triggers.values() if t.risk_score < 40]
        caution = [t for t in self.triggers.values() if 40 <= t.risk_score < 70]
        dangerous = [t for t in self.triggers.values() if t.risk_score >= 70]
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]
        
        # Estadísticas
        print(f"\n{Colors.BRIGHT_CYAN}[ESTADÍSTICAS]{Colors.RESET}")
        print(f"  Total de triggers: {Colors.CYAN}{len(self.triggers)}{Colors.RESET}")
        print(f"  Seguros: {Colors.GREEN}{len(safe)}{Colors.RESET}")
        print(f"  Advertencia: {Colors.YELLOW}{len(caution)}{Colors.RESET}")
        print(f"  Peligrosos: {Colors.RED}{len(dangerous)}{Colors.RESET}")
        print(f"  Honeypots: {Colors.BRIGHT_RED}{len(honeypots)}{Colors.RESET}")
        
        # Triggers seguros
        if safe:
            print(f"\n{SUBSEPARATOR}")
            print(f"{Colors.GREEN}✓ TRIGGERS SEGUROS ({len(safe)}){Colors.RESET}")
            print(SUBSEPARATOR)
            
            for trigger in sorted(safe, key=lambda t: t.risk_score)[:15]:
                reward_color = Colors.CYAN
                print(f"  {Colors.GREEN}✓{Colors.RESET} {trigger.event_name:<30} | {reward_color}{trigger.reward_type:<8}{Colors.RESET} | Riesgo: {Colors.GREEN}{trigger.risk_score:5.0f}%{Colors.RESET}")
        
        # Triggers con advertencia
        if caution:
            print(f"\n{SUBSEPARATOR}")
            print(f"{Colors.YELLOW}⚠ TRIGGERS CON ADVERTENCIA ({len(caution)}){Colors.RESET}")
            print(SUBSEPARATOR)
            
            for trigger in sorted(caution, key=lambda t: t.risk_score)[:10]:
                print(f"  {Colors.YELLOW}⚠{Colors.RESET} {trigger.event_name:<30} | {trigger.reward_type:<8} | Riesgo: {Colors.YELLOW}{trigger.risk_score:5.0f}%{Colors.RESET}")
        
        # Honeypots
        if honeypots:
            print(f"\n{SUBSEPARATOR}")
            print(f"{Colors.BRIGHT_RED}✗ HONEYPOTS DETECTADOS ({len(honeypots)}){Colors.RESET}")
            print(SUBSEPARATOR)
            
            for trigger in honeypots:
                print(f"  {Colors.BRIGHT_RED}✗{Colors.RESET} {trigger.event_name:<30} | {Colors.RED}TRAMPA{Colors.RESET:<8} | Riesgo: {Colors.BRIGHT_RED}{trigger.risk_score:5.0f}%{Colors.RESET}")
        
        # Recomendaciones
        print(f"\n{SUBSEPARATOR}")
        print(f"{Colors.BRIGHT_CYAN}[RECOMENDACIONES]{Colors.RESET}")
        print(SUBSEPARATOR)
        
        if safe:
            top_safe = sorted(safe, key=lambda t: t.risk_score)[:3]
            print(f"  {Colors.GREEN}→{Colors.RESET} Triggers recomendados: {', '.join(t.event_name for t in top_safe)}")
        
        if honeypots:
            print(f"  {Colors.RED}→{Colors.RESET} EVITAR estos triggers: {', '.join(t.event_name for t in honeypots[:3])}")
        
        if caution:
            print(f"  {Colors.YELLOW}→{Colors.RESET} Verificar validaciones en: {', '.join(t.event_name for t in caution[:3])}")
        
        print(f"\n{SEPARATOR}\n")
    
    def save_report(self):
        """Guardar reporte JSON"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_triggers': len(self.triggers),
            'triggers': [asdict(t) for t in self.triggers.values()]
        }
        
        report_file = f"red_shadow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"{Colors.GREEN}[+] Reporte guardado: {report_file}{Colors.RESET}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.RED}[!] Uso: red_shadow_destroyer.exe <ruta_dump>{Colors.RESET}")
        sys.exit(1)
    
    dump_path = sys.argv[1]
    
    if not os.path.exists(dump_path):
        print(f"{Colors.RED}[!] Ruta no encontrada: {dump_path}{Colors.RESET}")
        sys.exit(1)
    
    analyzer = AdvancedLuaAnalyzer(dump_path)
    analyzer.print_banner()
    
    try:
        analyzer.load_files()
        analyzer.analyze_triggers()
        analyzer.print_results()
        analyzer.save_report()
        
        print(f"{Colors.GREEN}[+] Análisis completado exitosamente{Colors.RESET}\n")
    
    except Exception as e:
        print(f"{Colors.RED}[!] Error durante el análisis: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
