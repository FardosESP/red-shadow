"""
Trigger Analyzer
Analyzes triggers and events for Ambani-exploitable vulnerabilities
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from ..utils.constants import (
    DANGEROUS_NATIVES,
    RISK_THRESHOLD_CRITICAL,
    RISK_THRESHOLD_HIGH,
    RISK_THRESHOLD_MEDIUM
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Trigger:
    """Represents a trigger/event in the code"""
    name: str
    event_type: str
    file_path: str
    line_number: int
    code: str
    parameters: List[str]
    has_validation: bool
    has_rate_limiting: bool
    dangerous_natives: List[str]
    risk_score: int
    category: str


@dataclass
class ExploitVector:
    """Exploitable attack vector"""
    trigger: Trigger
    exploit_type: str
    severity: str
    description: str
    proof_of_concept: str
    impact: str
    mitigation: str
    ambani_compatible: bool


@dataclass
class Honeypot:
    """Detected honeypot/trap"""
    trigger: Trigger
    confidence: float
    detection_mechanism: str
    ban_function: str
    is_silent: bool


@dataclass
class ObfuscationAnalysis:
    """Obfuscation analysis results"""
    has_obfuscation: bool
    techniques: List[str]
    difficulty_score: int  # 0-100
    deobfuscation_possible: bool
    obfuscated_strings: List[str]


@dataclass
class TriggerChain:
    """Represents a chain of triggers that call each other"""
    triggers: List[Trigger]
    chain_length: int
    combined_risk_score: int
    is_multi_stage_attack: bool
    description: str
    entry_point: Trigger
    exit_points: List[Trigger]

    @dataclass
    class TriggerChain:
        """Represents a chain of triggers that call each other"""
        triggers: List[Trigger]
        chain_length: int
        combined_risk_score: int
        is_multi_stage_attack: bool
        description: str
        entry_point: Trigger
        exit_points: List[Trigger]


class TriggerAnalyzer:
    """
    Analyzes triggers and events for Ambani exploits
    
    Responsibilities:
    - Detect RegisterNetEvent, AddEventHandler, callbacks without validation
    - Calculate Risk_Score based on multiple factors
    - Identify Ambani-exploitable patterns
    - Detect honeypots and traps
    - Categorize vulnerabilities by severity
    """
    
    # Patterns for detecting different event types
    EVENT_PATTERNS = {
        'RegisterNetEvent': r'RegisterNetEvent\s*\(\s*["\']([^"\']+)["\']',
        'AddEventHandler': r'AddEventHandler\s*\(\s*["\']([^"\']+)["\']',
        'RegisterServerCallback': r'(?:ESX|QBCore)\.(?:RegisterServerCallback|Functions\.CreateCallback)\s*\(\s*["\']([^"\']+)["\']',
        'RegisterCommand': r'RegisterCommand\s*\(\s*["\']([^"\']+)["\']',
    }
    
    # Patterns for validation detection
    VALIDATION_PATTERNS = [
        r'if\s+not\s+source',
        r'if\s+source\s*==\s*["\']',
        r'IsPlayerAceAllowed',
        r'xPlayer\.getGroup',
        r'QBCore\.Functions\.HasPermission',
        r'Player\.PlayerData\.job',
        r'CheckPlayerPermission',
        r'IsAdmin',
        r'HasPermission',
    ]
    
    # Patterns for rate limiting detection
    RATE_LIMIT_PATTERNS = [
        r'cooldown',
        r'lastUsed',
        r'rateLimiter',
        r'throttle',
        r'debounce',
        r'os\.time\(\)\s*-\s*last',
    ]
    
    # Patterns for reward logic (money, items)
    REWARD_PATTERNS = [
        r'addMoney',
        r'addAccountMoney',
        r'AddMoney',
        r'giveMoney',
        r'addItem',
        r'giveItem',
        r'AddItem',
        r'setMoney',
        r'setAccountMoney',
        r'addInventoryItem',
    ]
    
    # Patterns for honeypot detection
    HONEYPOT_PATTERNS = {
        'ban_functions': [
            r'BanPlayer',
            r'DropPlayer.*["\']cheat',
            r'DropPlayer.*["\']hack',
            r'DropPlayer.*["\']exploit',
            r'TriggerEvent.*ban',
            r'webhook.*banned',
            r'log.*cheat',
        ],
        'attractive_names': [
            r'giveMoney',
            r'addCash',
            r'spawnVehicle',
            r'giveWeapon',
            r'setGodMode',
            r'adminMenu',
            r'freeItems',
        ]
    }
    
    # Obfuscation patterns
    OBFUSCATION_PATTERNS = {
        'loadstring': r'loadstring\s*\(',
        'string_char': r'string\.char\s*\(',
        'base64': r'base64',
        'xor_cipher': r'bit\.bxor',
        'bytecode': r'\\x[0-9a-fA-F]{2}',
        'hex_strings': r'\\[0-9]{3}',
    }
    
    def __init__(self):
        """Initialize the Trigger Analyzer"""
        self.triggers: List[Trigger] = []
        self.exploit_vectors: List[ExploitVector] = []
        self.honeypots: List[Honeypot] = []
        self.trigger_chains: List[TriggerChain] = []
        self.trigger_graph: Dict[str, List[str]] = {}  # trigger_name -> [called_triggers]
        logger.info("TriggerAnalyzer initialized")
    
    def analyze_dump(self, dump_path: str) -> Dict:
        """
        Analyze a server dump and return detected vulnerabilities
        
        Args:
            dump_path: Path to the server dump
            
        Returns:
            Analysis results with detected triggers and vulnerabilities
        """
        logger.info(f"Starting analysis of dump: {dump_path}")
        
        if not os.path.exists(dump_path):
            logger.error(f"Dump path does not exist: {dump_path}")
            return {
                'success': False,
                'error': 'Dump path does not exist',
                'triggers': [],
                'exploit_vectors': [],
                'honeypots': []
            }
        
        # Reset state
        self.triggers = []
        self.exploit_vectors = []
        self.honeypots = []
        self.trigger_chains = []
        self.trigger_graph = {}
        
        # Parse all Lua files in dump
        lua_files = self._find_lua_files(dump_path)
        logger.info(f"Found {len(lua_files)} Lua files to analyze")
        
        for lua_file in lua_files:
            self._analyze_file(lua_file)
        
        # Calculate risk scores for all triggers
        for trigger in self.triggers:
            trigger.risk_score = self.calculate_risk_score(trigger)
            trigger.category = self._categorize_severity(trigger.risk_score)
        
        # Detect exploit vectors
        self.exploit_vectors = self.detect_exploit_vectors(self.triggers)
        
        # Detect honeypots
        self.honeypots = self.detect_honeypots(self.triggers)
        
        # Build trigger dependency graph and detect chains
        self._build_trigger_graph()
        self.trigger_chains = self._detect_trigger_chains()
        
        logger.info(f"Analysis complete: {len(self.triggers)} triggers, "
                   f"{len(self.exploit_vectors)} exploit vectors, "
                   f"{len(self.honeypots)} honeypots, "
                   f"{len(self.trigger_chains)} trigger chains")
        
        return {
            'success': True,
            'triggers': self.triggers,
            'exploit_vectors': self.exploit_vectors,
            'honeypots': self.honeypots,
            'trigger_chains': self.trigger_chains,
            'summary': {
                'total_triggers': len(self.triggers),
                'critical': len([t for t in self.triggers if t.category == 'CRITICAL']),
                'high': len([t for t in self.triggers if t.category == 'HIGH']),
                'medium': len([t for t in self.triggers if t.category == 'MEDIUM']),
                'low': len([t for t in self.triggers if t.category == 'LOW']),
                'trigger_chains': len(self.trigger_chains),
                'multi_stage_attacks': len([c for c in self.trigger_chains if c.is_multi_stage_attack]),
            }
        }
    
    def _find_lua_files(self, path: str) -> List[str]:
        """Find all Lua files in the given path"""
        lua_files = []
        path_obj = Path(path)
        
        if path_obj.is_file() and path_obj.suffix == '.lua':
            return [str(path_obj)]
        
        if path_obj.is_dir():
            for lua_file in path_obj.rglob('*.lua'):
                lua_files.append(str(lua_file))
        
        return lua_files
    
    def _analyze_file(self, file_path: str) -> None:
        """Analyze a single Lua file for triggers"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Detect triggers using patterns
            for event_type, pattern in self.EVENT_PATTERNS.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    event_name = match.group(1)
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Extract code block (next 20 lines)
                    start_line = line_number - 1
                    end_line = min(start_line + 20, len(lines))
                    code_block = '\n'.join(lines[start_line:end_line])
                    
                    # Analyze the trigger
                    trigger = self._create_trigger(
                        name=event_name,
                        event_type=event_type,
                        file_path=file_path,
                        line_number=line_number,
                        code=code_block
                    )
                    
                    self.triggers.append(trigger)
                    
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
    
    def _create_trigger(self, name: str, event_type: str, file_path: str, 
                       line_number: int, code: str) -> Trigger:
        """Create a Trigger object with analysis"""
        # Detect validation
        has_validation = self._has_validation(code)
        
        # Detect rate limiting
        has_rate_limiting = self._has_rate_limiting(code)
        
        # Detect dangerous natives
        dangerous_natives = self._detect_dangerous_natives(code)
        
        # Extract parameters
        parameters = self._extract_parameters(code)
        
        return Trigger(
            name=name,
            event_type=event_type,
            file_path=file_path,
            line_number=line_number,
            code=code,
            parameters=parameters,
            has_validation=has_validation,
            has_rate_limiting=has_rate_limiting,
            dangerous_natives=dangerous_natives,
            risk_score=0,  # Will be calculated later
            category='UNKNOWN'
        )
    
    def _has_validation(self, code: str) -> bool:
        """Check if code has validation logic"""
        for pattern in self.VALIDATION_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False
    
    def _has_rate_limiting(self, code: str) -> bool:
        """Check if code has rate limiting"""
        for pattern in self.RATE_LIMIT_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False
    
    def _detect_dangerous_natives(self, code: str) -> List[str]:
        """Detect dangerous natives in code"""
        found_natives = []
        for native in DANGEROUS_NATIVES:
            if native in code:
                found_natives.append(native)
        return found_natives
    
    def _extract_parameters(self, code: str) -> List[str]:
        """Extract function parameters from code"""
        # Look for function definition
        func_match = re.search(r'function\s*\([^)]*\)', code)
        if func_match:
            params_str = func_match.group(0)
            # Extract parameter names
            params = re.findall(r'\b\w+\b', params_str)
            return [p for p in params if p != 'function']
        return []
    
    def _categorize_severity(self, risk_score: int) -> str:
        """Categorize severity based on risk score"""
        if risk_score >= RISK_THRESHOLD_CRITICAL:
            return 'CRITICAL'
        elif risk_score >= RISK_THRESHOLD_HIGH:
            return 'HIGH'
        elif risk_score >= RISK_THRESHOLD_MEDIUM:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_risk_score(self, trigger: Trigger) -> int:
        """
        Calculate Risk_Score (0-100) based on multiple factors
        
        Formula:
        Risk_Score = (
            validation_score * 0.30 +
            reward_logic_score * 0.25 +
            dangerous_natives_score * 0.25 +
            rate_limiting_score * 0.20
        )
        
        Args:
            trigger: Trigger to analyze
            
        Returns:
            Risk score from 0-100
        """
        # Validation score (0-100): 100 if no validation, 0 if has validation
        validation_score = 0 if trigger.has_validation else 100
        
        # Reward logic score (0-100): based on presence of money/item functions
        reward_score = 0
        for pattern in self.REWARD_PATTERNS:
            if re.search(pattern, trigger.code, re.IGNORECASE):
                reward_score = 100
                break
        
        # Dangerous natives score (0-100): based on number of dangerous natives
        natives_score = min(len(trigger.dangerous_natives) * 33, 100)
        
        # Rate limiting score (0-100): 100 if no rate limiting, 0 if has rate limiting
        rate_limit_score = 0 if trigger.has_rate_limiting else 100
        
        # Calculate weighted risk score
        risk_score = (
            validation_score * 0.30 +
            reward_score * 0.25 +
            natives_score * 0.25 +
            rate_limit_score * 0.20
        )
        
        return int(risk_score)
    
    def detect_exploit_vectors(self, triggers: List[Trigger]) -> List[ExploitVector]:
        """
        Identify Ambani-specific attack vectors
        
        Args:
            triggers: List of triggers to analyze
            
        Returns:
            List of exploitable vectors
        """
        exploit_vectors = []
        
        for trigger in triggers:
            # Skip low-risk triggers
            if trigger.risk_score < RISK_THRESHOLD_MEDIUM:
                continue
            
            # Determine exploit type
            exploit_type = self._determine_exploit_type(trigger)
            
            # Generate proof of concept
            poc = self._generate_poc(trigger)
            
            # Determine impact
            impact = self._determine_impact(trigger)
            
            # Generate mitigation
            mitigation = self._generate_mitigation(trigger)
            
            # Create exploit vector
            exploit = ExploitVector(
                trigger=trigger,
                exploit_type=exploit_type,
                severity=trigger.category,
                description=f"Exploitable {trigger.event_type} '{trigger.name}' without proper validation",
                proof_of_concept=poc,
                impact=impact,
                mitigation=mitigation,
                ambani_compatible=True
            )
            
            exploit_vectors.append(exploit)
        
        logger.info(f"Detected {len(exploit_vectors)} exploit vectors")
        return exploit_vectors
    
    def _determine_exploit_type(self, trigger: Trigger) -> str:
        """Determine the type of exploit"""
        if trigger.event_type in ['RegisterNetEvent', 'AddEventHandler']:
            return 'Event Injection'
        elif trigger.event_type == 'RegisterServerCallback':
            return 'Callback Exploitation'
        elif trigger.dangerous_natives:
            return 'Native Spoofing'
        else:
            return 'Generic Exploit'
    
    def _generate_poc(self, trigger: Trigger) -> str:
        """Generate proof of concept Lua code"""
        if trigger.event_type in ['RegisterNetEvent', 'AddEventHandler']:
            # Generate event injection PoC
            params = ', '.join([f'"{p}"' if i == 0 else 'nil' 
                              for i, p in enumerate(trigger.parameters[:3])])
            return f'TriggerServerEvent("{trigger.name}", {params})'
        
        elif trigger.event_type == 'RegisterServerCallback':
            # Generate callback exploitation PoC
            return f'TriggerServerCallback("{trigger.name}", function(result) print(result) end)'
        
        else:
            return f'-- Exploit {trigger.name} via Ambani API'
    
    def _determine_impact(self, trigger: Trigger) -> str:
        """Determine the impact of exploiting this trigger"""
        impacts = []
        
        # Check for money/economy impact
        for pattern in self.REWARD_PATTERNS:
            if re.search(pattern, trigger.code, re.IGNORECASE):
                impacts.append("Economy manipulation (money/items)")
                break
        
        # Check for dangerous natives
        if trigger.dangerous_natives:
            if any('Weapon' in n for n in trigger.dangerous_natives):
                impacts.append("Weapon spawning")
            if any('Coords' in n or 'Position' in n for n in trigger.dangerous_natives):
                impacts.append("Teleportation")
            if any('Invincible' in n or 'Health' in n for n in trigger.dangerous_natives):
                impacts.append("God mode / invincibility")
        
        # Check for admin functions
        if re.search(r'admin|kick|ban|permission', trigger.code, re.IGNORECASE):
            impacts.append("Administrative privilege escalation")
        
        if not impacts:
            impacts.append("Information disclosure or minor gameplay advantage")
        
        return ", ".join(impacts)
    
    def _generate_mitigation(self, trigger: Trigger) -> str:
        """Generate mitigation recommendations"""
        mitigations = []
        
        if not trigger.has_validation:
            mitigations.append("Add source validation: if not source then return end")
            mitigations.append("Add permission checks: if not IsPlayerAceAllowed(source, 'admin') then return end")
        
        if not trigger.has_rate_limiting:
            mitigations.append("Implement rate limiting to prevent spam")
        
        if trigger.dangerous_natives:
            mitigations.append("Add server-side validation before executing natives")
        
        if re.search(r'addMoney|giveMoney|addItem', trigger.code, re.IGNORECASE):
            mitigations.append("Validate transaction amounts and implement anti-cheat logging")
        
        return " | ".join(mitigations)
    
    def detect_honeypots(self, triggers: List[Trigger]) -> List[Honeypot]:
        """
        Detect traps and honeypots using pattern analysis
        
        Args:
            triggers: List of triggers to analyze
            
        Returns:
            List of detected honeypots
        """
        honeypots = []
        
        for trigger in triggers:
            # Check for attractive names
            is_attractive = False
            for pattern in self.HONEYPOT_PATTERNS['attractive_names']:
                if re.search(pattern, trigger.name, re.IGNORECASE):
                    is_attractive = True
                    break
            
            if not is_attractive:
                continue
            
            # Check for ban functions
            ban_function = None
            for pattern in self.HONEYPOT_PATTERNS['ban_functions']:
                match = re.search(pattern, trigger.code, re.IGNORECASE)
                if match:
                    ban_function = match.group(0)
                    break
            
            if ban_function:
                # Calculate confidence score
                confidence = self._calculate_honeypot_confidence(trigger, ban_function)
                
                # Determine if silent honeypot
                is_silent = 'webhook' in trigger.code.lower() or 'log' in trigger.code.lower()
                
                honeypot = Honeypot(
                    trigger=trigger,
                    confidence=confidence,
                    detection_mechanism=f"Attractive name '{trigger.name}' with ban logic",
                    ban_function=ban_function,
                    is_silent=is_silent
                )
                
                honeypots.append(honeypot)
        
        logger.info(f"Detected {len(honeypots)} potential honeypots")
        return honeypots
    
    def _calculate_honeypot_confidence(self, trigger: Trigger, ban_function: str) -> float:
        """Calculate confidence that this is a honeypot"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if name is very attractive
        attractive_keywords = ['free', 'give', 'admin', 'god', 'unlimited']
        for keyword in attractive_keywords:
            if keyword in trigger.name.lower():
                confidence += 0.1
        
        # Increase confidence if ban logic is prominent
        code_lines = trigger.code.split('\n')
        ban_lines = sum(1 for line in code_lines if 'ban' in line.lower() or 'drop' in line.lower())
        functional_lines = len([l for l in code_lines if l.strip() and not l.strip().startswith('--')])
        
        if functional_lines > 0:
            ban_ratio = ban_lines / functional_lines
            confidence += min(ban_ratio, 0.3)
        
        # Increase confidence if there's minimal functional code
        if functional_lines < 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def analyze_obfuscation(self, code: str) -> ObfuscationAnalysis:
        """
        Analyze obfuscation techniques and calculate deobfuscation difficulty
        
        Args:
            code: Code to analyze
            
        Returns:
            Obfuscation analysis results
        """
        techniques = []
        obfuscated_strings = []
        
        # Detect obfuscation techniques
        for technique, pattern in self.OBFUSCATION_PATTERNS.items():
            if re.search(pattern, code, re.IGNORECASE):
                techniques.append(technique)
        
        # Extract obfuscated strings
        if 'string_char' in techniques:
            # Find string.char patterns
            char_matches = re.findall(r'string\.char\([^)]+\)', code)
            obfuscated_strings.extend(char_matches[:5])  # Limit to 5 examples
        
        # Calculate difficulty score
        difficulty_score = self._calculate_obfuscation_difficulty(techniques, code)
        
        # Determine if deobfuscation is possible
        deobfuscation_possible = difficulty_score < 70
        
        return ObfuscationAnalysis(
            has_obfuscation=len(techniques) > 0,
            techniques=techniques,
            difficulty_score=difficulty_score,
            deobfuscation_possible=deobfuscation_possible,
            obfuscated_strings=obfuscated_strings
        )
    
    def _calculate_obfuscation_difficulty(self, techniques: List[str], code: str) -> int:
        """Calculate obfuscation difficulty score (0-100)"""
        if not techniques:
            return 0
        
        # Base score from number of techniques
        base_score = min(len(techniques) * 20, 60)
        
        # Add complexity factors
        complexity = 0
        
        # Check for multiple layers
        if 'loadstring' in techniques and len(techniques) > 1:
            complexity += 15
        
        # Check for bytecode
        if 'bytecode' in techniques:
            complexity += 20
        
        # Check for XOR cipher
        if 'xor_cipher' in techniques:
            complexity += 15
        
        # Check code length (longer = more complex)
        if len(code) > 10000:
            complexity += 10
        
        difficulty = min(base_score + complexity, 100)
        return difficulty
    
    def _build_trigger_graph(self) -> None:
        """
        Build a dependency graph of triggers
        Maps trigger names to the triggers they call
        """
        logger.info("Building trigger dependency graph")
        
        # Initialize graph with all trigger names
        for trigger in self.triggers:
            if trigger.name not in self.trigger_graph:
                self.trigger_graph[trigger.name] = []
        
        # Patterns for detecting trigger calls
        trigger_call_patterns = [
            r'TriggerEvent\s*\(\s*["\']([^"\']+)["\']',
            r'TriggerServerEvent\s*\(\s*["\']([^"\']+)["\']',
            r'TriggerClientEvent\s*\(\s*[^,]+,\s*["\']([^"\']+)["\']',
        ]
        
        # Analyze each trigger's code to find calls to other triggers
        for trigger in self.triggers:
            called_triggers = set()
            
            for pattern in trigger_call_patterns:
                matches = re.finditer(pattern, trigger.code, re.IGNORECASE)
                for match in matches:
                    called_trigger_name = match.group(1)
                    # Only add if the called trigger exists in our trigger list
                    if any(t.name == called_trigger_name for t in self.triggers):
                        called_triggers.add(called_trigger_name)
            
            self.trigger_graph[trigger.name] = list(called_triggers)
        
        # Log graph statistics
        total_edges = sum(len(calls) for calls in self.trigger_graph.values())
        logger.info(f"Trigger graph built: {len(self.trigger_graph)} nodes, {total_edges} edges")
    
    def _detect_trigger_chains(self) -> List[TriggerChain]:
        """
        Detect trigger chains using DFS graph traversal
        Identifies multi-stage attack chains where triggers call other triggers
        
        Returns:
            List of detected trigger chains
        """
        logger.info("Detecting trigger chains using DFS traversal")
        
        chains = []
        visited_paths = set()  # To avoid duplicate chains
        
        # Start DFS from each trigger
        for trigger in self.triggers:
            # Only start from triggers that could be entry points (externally callable)
            if self._is_entry_point(trigger):
                # Perform DFS to find all chains starting from this trigger
                self._dfs_find_chains(
                    trigger.name,
                    path=[trigger.name],
                    visited=set(),
                    chains=chains,
                    visited_paths=visited_paths
                )
        
        logger.info(f"Detected {len(chains)} trigger chains")
        return chains
    
    def _is_entry_point(self, trigger: Trigger) -> bool:
        """
        Determine if a trigger is an entry point (can be called externally)
        Entry points are triggers that can be invoked by clients
        """
        # RegisterNetEvent and AddEventHandler are typically client-callable
        if trigger.event_type in ['RegisterNetEvent', 'AddEventHandler']:
            return True
        
        # RegisterCommand is also an entry point
        if trigger.event_type == 'RegisterCommand':
            return True
        
        return False
    
    def _dfs_find_chains(
        self,
        current_trigger: str,
        path: List[str],
        visited: set,
        chains: List[TriggerChain],
        visited_paths: set
    ) -> None:
        """
        DFS traversal to find trigger chains
        
        Args:
            current_trigger: Current trigger name in the traversal
            path: Current path of trigger names
            visited: Set of visited triggers in current path (for cycle detection)
            chains: List to accumulate found chains
            visited_paths: Set of already processed paths (to avoid duplicates)
        """
        # If we've found a chain (length > 1), record it
        if len(path) > 1:
            # Create a unique key for this path
            path_key = tuple(sorted(path))
            
            if path_key not in visited_paths:
                visited_paths.add(path_key)
                
                # Get trigger objects for the path
                trigger_objects = []
                for trigger_name in path:
                    trigger_obj = next((t for t in self.triggers if t.name == trigger_name), None)
                    if trigger_obj:
                        trigger_objects.append(trigger_obj)
                
                if trigger_objects:
                    # Create the chain
                    chain = self._create_trigger_chain(trigger_objects, path)
                    chains.append(chain)
        
        # Mark current trigger as visited in this path
        visited.add(current_trigger)
        
        # Explore neighbors (triggers called by current trigger)
        if current_trigger in self.trigger_graph:
            for next_trigger in self.trigger_graph[current_trigger]:
                # Avoid cycles
                if next_trigger not in visited:
                    # Continue DFS
                    self._dfs_find_chains(
                        next_trigger,
                        path + [next_trigger],
                        visited.copy(),  # Copy to allow different paths
                        chains,
                        visited_paths
                    )
    
    def _create_trigger_chain(self, triggers: List[Trigger], path: List[str]) -> TriggerChain:
        """
        Create a TriggerChain object from a list of triggers
        
        Args:
            triggers: List of Trigger objects in the chain
            path: List of trigger names in order
            
        Returns:
            TriggerChain object
        """
        # Calculate combined risk score (weighted average with emphasis on highest risk)
        if triggers:
            risk_scores = [t.risk_score for t in triggers]
            max_risk = max(risk_scores)
            avg_risk = sum(risk_scores) / len(risk_scores)
            # Combined score: 70% max risk + 30% average risk
            combined_risk = int(max_risk * 0.7 + avg_risk * 0.3)
        else:
            combined_risk = 0
        
        # Determine if this is a multi-stage attack
        # Criteria: chain length >= 2 AND combined risk >= MEDIUM threshold
        is_multi_stage = len(triggers) >= 2 and combined_risk >= RISK_THRESHOLD_MEDIUM
        
        # Identify entry point (first trigger in chain)
        entry_point = triggers[0] if triggers else None
        
        # Identify exit points (triggers that don't call other triggers in the chain)
        exit_points = []
        for i, trigger in enumerate(triggers):
            trigger_name = path[i]
            # Check if this trigger calls any other trigger in the chain
            calls_in_chain = False
            if trigger_name in self.trigger_graph:
                for called in self.trigger_graph[trigger_name]:
                    if called in path[i+1:]:  # Check if it calls triggers later in the chain
                        calls_in_chain = True
                        break
            
            if not calls_in_chain and i < len(triggers) - 1:
                # This is a branch point or dead end
                exit_points.append(trigger)
        
        # If no exit points found, the last trigger is the exit point
        if not exit_points and triggers:
            exit_points = [triggers[-1]]
        
        # Generate description
        description = self._generate_chain_description(triggers, path, combined_risk)
        
        return TriggerChain(
            triggers=triggers,
            chain_length=len(triggers),
            combined_risk_score=combined_risk,
            is_multi_stage_attack=is_multi_stage,
            description=description,
            entry_point=entry_point,
            exit_points=exit_points
        )
    
    def _generate_chain_description(self, triggers: List[Trigger], path: List[str], combined_risk: int) -> str:
        """
        Generate a human-readable description of the trigger chain
        
        Args:
            triggers: List of triggers in the chain
            path: List of trigger names in order
            combined_risk: Combined risk score
            
        Returns:
            Description string
        """
        if not triggers:
            return "Empty trigger chain"
        
        # Build the chain path
        chain_path = " -> ".join(path)
        
        # Determine severity
        if combined_risk >= RISK_THRESHOLD_CRITICAL:
            severity = "CRITICAL"
        elif combined_risk >= RISK_THRESHOLD_HIGH:
            severity = "HIGH"
        elif combined_risk >= RISK_THRESHOLD_MEDIUM:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        # Check for dangerous patterns
        has_money = any(re.search(r'money|cash|bank', t.name, re.IGNORECASE) for t in triggers)
        has_admin = any(re.search(r'admin|permission|ban|kick', t.name, re.IGNORECASE) for t in triggers)
        has_items = any(re.search(r'item|inventory|weapon', t.name, re.IGNORECASE) for t in triggers)
        
        impact_parts = []
        if has_money:
            impact_parts.append("economy manipulation")
        if has_admin:
            impact_parts.append("privilege escalation")
        if has_items:
            impact_parts.append("item duplication")
        
        impact_desc = ", ".join(impact_parts) if impact_parts else "gameplay manipulation"
        
        description = (
            f"{severity} multi-stage attack chain: {chain_path}. "
            f"Chain length: {len(triggers)}, Combined risk: {combined_risk}/100. "
            f"Potential impact: {impact_desc}."
        )
        
        return description
