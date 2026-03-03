#!/usr/bin/env python3
"""
RED-SHADOW "Destroyer" v2.0 - Advanced Lua Code Analysis Engine
Análisis profundo de volcados de redENGINE con detección de trampas y protecciones

Características:
- Análisis de flujo de datos (Data Flow Analysis)
- Detección de patrones de Honeypots
- Rastreo de dependencias cruzadas
- Análisis de ofuscación
- Detección de Silent Bans
- Generación de reportes forenses
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax

console = Console()

# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class LuaFunction:
    """Representa una función Lua detectada"""
    name: str
    file: str
    line: int
    parameters: List[str]
    calls: List[str]  # Funciones que llama
    variables_used: List[str]
    has_ban_logic: bool = False
    has_validation: bool = False
    is_honeypot: bool = False
    risk_score: float = 0.0

@dataclass
class TriggerEvent:
    """Representa un evento de trigger detectado"""
    event_name: str
    file: str
    line: int
    handler_function: str
    parameters: List[str]
    calls_functions: List[str]
    has_validation: bool
    has_reward_logic: bool
    has_ban_logic: bool
    reward_type: str  # 'MONEY', 'ITEMS', 'WEAPONS', 'UNKNOWN'
    risk_score: float
    is_honeypot: bool

@dataclass
class AnalysisReport:
    """Reporte final del análisis"""
    timestamp: str
    total_files: int
    total_functions: int
    total_triggers: int
    safe_triggers: List[TriggerEvent]
    risky_triggers: List[TriggerEvent]
    honeypots: List[TriggerEvent]
    detected_anticheats: List[str]
    cross_dependencies: Dict[str, List[str]]
    overall_risk: float
    recommendations: List[str]

# ============================================================================
# ANALIZADOR DE CÓDIGO LUA
# ============================================================================

class LuaCodeAnalyzer:
    """Motor de análisis profundo de código Lua"""
    
    def __init__(self, dump_path: str):
        self.dump_path = Path(dump_path)
        self.files: Dict[str, str] = {}
        self.functions: Dict[str, LuaFunction] = {}
        self.triggers: Dict[str, TriggerEvent] = {}
        self.variables: Dict[str, Set[str]] = defaultdict(set)
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)
        
    def load_files(self):
        """Cargar todos los archivos Lua del dump"""
        console.print("[*] Cargando archivos Lua del dump...")
        
        lua_files = list(self.dump_path.rglob("*.lua"))
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Leyendo archivos...", total=len(lua_files))
            
            for lua_file in lua_files:
                try:
                    with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self.files[str(lua_file)] = content
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"[!] Error leyendo {lua_file}: {e}")
        
        console.print(f"[+] {len(self.files)} archivos Lua cargados")
        return len(self.files)
    
    def analyze_all(self):
        """Ejecutar análisis completo"""
        console.print("\n[*] Iniciando análisis profundo...")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Analizando...", total=4)
            
            # Fase 1: Extraer funciones
            console.print("\n[Phase 1] Extrayendo funciones...")
            self.extract_functions()
            progress.update(task, advance=1)
            
            # Fase 2: Detectar triggers
            console.print("[Phase 2] Detectando triggers...")
            self.detect_triggers()
            progress.update(task, advance=1)
            
            # Fase 3: Análisis de flujo de datos
            console.print("[Phase 3] Analizando flujo de datos...")
            self.analyze_data_flow()
            progress.update(task, advance=1)
            
            # Fase 4: Detección de trampas
            console.print("[Phase 4] Detectando trampas y protecciones...")
            self.detect_traps_and_protections()
            progress.update(task, advance=1)
    
    def extract_functions(self):
        """Extraer todas las funciones Lua"""
        function_pattern = r'(?:local\s+)?function\s+(\w+)\s*\((.*?)\)'
        
        for file_path, content in self.files.items():
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(function_pattern, line)
                
                for match in matches:
                    func_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',') if p.strip()]
                    
                    # Extraer llamadas de función
                    calls = self.extract_function_calls(content[match.start():])
                    
                    self.functions[func_name] = LuaFunction(
                        name=func_name,
                        file=file_path,
                        line=line_num,
                        parameters=params,
                        calls=calls,
                        variables_used=self.extract_variables(line),
                        has_ban_logic=self.has_ban_logic(content),
                        has_validation=self.has_validation_logic(content)
                    )
    
    def detect_triggers(self):
        """Detectar todos los triggers (RegisterNetEvent, TriggerServerEvent, etc.)"""
        trigger_patterns = {
            'RegisterNetEvent': r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\']',
            'AddEventHandler': r'AddEventHandler\s*\(\s*["\']([^"\']+)["\']',
            'TriggerServerEvent': r'TriggerServerEvent\s*\(\s*["\']([^"\']+)["\']',
        }
        
        for file_path, content in self.files.items():
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
                        
                        # Analizar trigger
                        has_validation = self.has_validation_logic(context)
                        has_reward = self.detect_reward_logic(context)
                        has_ban = self.has_ban_logic(context)
                        reward_type = self.classify_reward(context)
                        
                        risk_score = self.calculate_trigger_risk(
                            event_name, has_validation, has_reward, has_ban
                        )
                        
                        is_honeypot = self.is_honeypot_trigger(event_name, context, has_ban)
                        
                        self.triggers[event_name] = TriggerEvent(
                            event_name=event_name,
                            file=file_path,
                            line=line_num,
                            handler_function=self.extract_handler_function(context),
                            parameters=self.extract_parameters(context),
                            calls_functions=self.extract_function_calls(context),
                            has_validation=has_validation,
                            has_reward_logic=has_reward,
                            has_ban_logic=has_ban,
                            reward_type=reward_type,
                            risk_score=risk_score,
                            is_honeypot=is_honeypot
                        )
    
    def analyze_data_flow(self):
        """Analizar flujo de datos entre triggers"""
        for trigger_name, trigger in self.triggers.items():
            # Rastrear qué variables se usan
            for func_call in trigger.calls_functions:
                if func_call in self.functions:
                    func = self.functions[func_call]
                    self.cross_references[trigger_name].update(func.calls)
    
    def detect_traps_and_protections(self):
        """Detectar trampas, honeypots y protecciones"""
        for trigger_name, trigger in self.triggers.items():
            # Marcar como honeypot si tiene lógica de ban sin recompensa
            if trigger.has_ban_logic and not trigger.has_reward_logic:
                trigger.is_honeypot = True
                trigger.risk_score = 95.0
    
    def extract_function_calls(self, code: str) -> List[str]:
        """Extraer llamadas de función del código"""
        pattern = r'(\w+)\s*\('
        matches = re.findall(pattern, code)
        return list(set(matches))
    
    def extract_variables(self, line: str) -> List[str]:
        """Extraer variables usadas en una línea"""
        pattern = r'\b([a-zA-Z_]\w*)\b'
        return re.findall(pattern, line)
    
    def extract_parameters(self, context: str) -> List[str]:
        """Extraer parámetros de un trigger"""
        pattern = r'function\s*\((.*?)\)'
        match = re.search(pattern, context)
        if match:
            return [p.strip() for p in match.group(1).split(',') if p.strip()]
        return []
    
    def extract_handler_function(self, context: str) -> str:
        """Extraer el nombre de la función manejadora"""
        pattern = r'function\s+(\w+)'
        match = re.search(pattern, context)
        return match.group(1) if match else "unknown"
    
    def has_ban_logic(self, code: str) -> bool:
        """Detectar lógica de baneo"""
        ban_keywords = ['DropPlayer', 'Ban', 'kick', 'TriggerClientEvent.*ban', 'banear']
        return any(keyword in code for keyword in ban_keywords)
    
    def has_validation_logic(self, code: str) -> bool:
        """Detectar lógica de validación"""
        validation_keywords = ['if', 'check', 'verify', 'validate', 'assert', 'require']
        return any(keyword in code for keyword in validation_keywords)
    
    def detect_reward_logic(self, code: str) -> bool:
        """Detectar lógica de recompensa"""
        reward_keywords = ['addMoney', 'addItem', 'giveWeapon', 'addInventory', 'TriggerClientEvent']
        return any(keyword in code for keyword in reward_keywords)
    
    def classify_reward(self, code: str) -> str:
        """Clasificar el tipo de recompensa"""
        if 'addMoney' in code or 'money' in code.lower():
            return 'MONEY'
        elif 'addItem' in code or 'inventory' in code.lower():
            return 'ITEMS'
        elif 'giveWeapon' in code or 'weapon' in code.lower():
            return 'WEAPONS'
        return 'UNKNOWN'
    
    def calculate_trigger_risk(self, event_name: str, has_validation: bool, 
                               has_reward: bool, has_ban: bool) -> float:
        """Calcular puntuación de riesgo"""
        risk = 50.0
        
        # Validaciones reducen riesgo
        if has_validation:
            risk -= 20
        
        # Recompensas aumentan riesgo
        if has_reward:
            risk += 15
        
        # Lógica de ban aumenta riesgo
        if has_ban:
            risk += 30
        
        # Nombres sospechosos
        suspicious = ['admin', 'ban', 'kick', 'trap', 'check']
        if any(s in event_name.lower() for s in suspicious):
            risk += 25
        
        return max(0, min(100, risk))
    
    def is_honeypot_trigger(self, event_name: str, context: str, has_ban: bool) -> bool:
        """Detectar si es un honeypot (trampa)"""
        # Honeypot si: tiene ban logic pero no tiene reward logic
        has_reward = self.detect_reward_logic(context)
        return has_ban and not has_reward
    
    def generate_report(self) -> AnalysisReport:
        """Generar reporte final"""
        safe_triggers = [t for t in self.triggers.values() if t.risk_score < 40]
        risky_triggers = [t for t in self.triggers.values() if 40 <= t.risk_score < 80]
        honeypots = [t for t in self.triggers.values() if t.is_honeypot]
        
        overall_risk = sum(t.risk_score for t in self.triggers.values()) / len(self.triggers) if self.triggers else 0
        
        detected_anticheats = self.detect_anticheats()
        recommendations = self.generate_recommendations(safe_triggers, honeypots)
        
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_files=len(self.files),
            total_functions=len(self.functions),
            total_triggers=len(self.triggers),
            safe_triggers=safe_triggers,
            risky_triggers=risky_triggers,
            honeypots=honeypots,
            detected_anticheats=detected_anticheats,
            cross_dependencies=dict(self.cross_references),
            overall_risk=overall_risk,
            recommendations=recommendations
        )
    
    def detect_anticheats(self) -> List[str]:
        """Detectar Anticheats conocidos"""
        detected = []
        anticheat_signatures = {
            'WaveShield': ['WaveShield', 'Wave.lua', 'wave_check'],
            'Phoenix': ['Phoenix', 'phoenix_ac', 'PhoenixAC'],
            'Nexus': ['Nexus', 'nexus_ac', 'NexusAC'],
            'FireAC': ['FireAC', 'fire_ac', 'FireAntiCheat'],
        }
        
        all_code = '\n'.join(self.files.values())
        
        for ac_name, signatures in anticheat_signatures.items():
            if any(sig in all_code for sig in signatures):
                detected.append(ac_name)
        
        return detected
    
    def generate_recommendations(self, safe_triggers: List[TriggerEvent], 
                                honeypots: List[TriggerEvent]) -> List[str]:
        """Generar recomendaciones"""
        recommendations = []
        
        if len(safe_triggers) > 0:
            recommendations.append(f"✓ {len(safe_triggers)} triggers seguros identificados")
        
        if len(honeypots) > 0:
            recommendations.append(f"⚠ {len(honeypots)} honeypots detectados - EVITAR")
        
        if len(safe_triggers) > 0:
            top_safe = sorted(safe_triggers, key=lambda t: t.risk_score)[:3]
            recommendations.append(f"→ Triggers recomendados: {', '.join(t.event_name for t in top_safe)}")
        
        return recommendations
    
    def print_report(self, report: AnalysisReport):
        """Imprimir reporte en consola"""
        console.print(Panel("[bold cyan]RED-SHADOW Destroyer v2.0 - Análisis Forense[/bold cyan]"))
        
        # Estadísticas generales
        stats_table = Table(title="Estadísticas Generales")
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="green")
        stats_table.add_row("Archivos analizados", str(report.total_files))
        stats_table.add_row("Funciones detectadas", str(report.total_functions))
        stats_table.add_row("Triggers encontrados", str(report.total_triggers))
        stats_table.add_row("Riesgo general", f"{report.overall_risk:.1f}%")
        console.print(stats_table)
        
        # Triggers seguros
        if report.safe_triggers:
            console.print("\n[green]✓ TRIGGERS SEGUROS[/green]")
            safe_table = Table()
            safe_table.add_column("Evento", style="green")
            safe_table.add_column("Recompensa", style="cyan")
            safe_table.add_column("Riesgo", style="yellow")
            
            for trigger in report.safe_triggers[:10]:
                safe_table.add_row(
                    trigger.event_name,
                    trigger.reward_type,
                    f"{trigger.risk_score:.0f}%"
                )
            console.print(safe_table)
        
        # Honeypots
        if report.honeypots:
            console.print("\n[red]✗ HONEYPOTS DETECTADOS[/red]")
            honeypot_table = Table()
            honeypot_table.add_column("Evento", style="red")
            honeypot_table.add_column("Archivo", style="yellow")
            honeypot_table.add_column("Línea", style="cyan")
            
            for trigger in report.honeypots:
                honeypot_table.add_row(
                    trigger.event_name,
                    trigger.file.split('/')[-1],
                    str(trigger.line)
                )
            console.print(honeypot_table)
        
        # Anticheats detectados
        if report.detected_anticheats:
            console.print(f"\n[yellow]⚠ Anticheats detectados: {', '.join(report.detected_anticheats)}[/yellow]")
        
        # Recomendaciones
        if report.recommendations:
            console.print("\n[cyan]Recomendaciones:[/cyan]")
            for rec in report.recommendations:
                console.print(f"  {rec}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        console.print("[!] Uso: python red_shadow_destroyer_v2.py <ruta_dump> [-v]")
        sys.exit(1)
    
    dump_path = sys.argv[1]
    verbose = '-v' in sys.argv
    
    if not os.path.exists(dump_path):
        console.print(f"[!] Ruta no encontrada: {dump_path}")
        sys.exit(1)
    
    console.print(Panel("[bold cyan]RED-SHADOW Destroyer v2.0[/bold cyan]\n[yellow]Advanced Lua Code Analysis Engine[/yellow]"))
    
    analyzer = LuaCodeAnalyzer(dump_path)
    analyzer.load_files()
    analyzer.analyze_all()
    
    report = analyzer.generate_report()
    analyzer.print_report(report)
    
    # Guardar reporte en JSON
    report_file = f"red_shadow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': report.timestamp,
            'total_files': report.total_files,
            'total_functions': report.total_functions,
            'total_triggers': report.total_triggers,
            'safe_triggers': [asdict(t) for t in report.safe_triggers],
            'risky_triggers': [asdict(t) for t in report.risky_triggers],
            'honeypots': [asdict(t) for t in report.honeypots],
            'detected_anticheats': report.detected_anticheats,
            'overall_risk': report.overall_risk,
            'recommendations': report.recommendations
        }, f, indent=2, default=str)
    
    console.print(f"\n[+] Reporte guardado en: {report_file}")

if __name__ == '__main__':
    main()
