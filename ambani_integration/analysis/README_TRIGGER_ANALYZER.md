# Trigger Analyzer

## Overview

The Trigger Analyzer is a core component of the Ambani Integration that analyzes FiveM server code to identify triggers and events that are exploitable by the Ambani cheat platform. It performs static code analysis on Lua files to detect vulnerabilities, calculate risk scores, and generate proof-of-concept exploits.

## Features

- **Event Detection**: Identifies RegisterNetEvent, AddEventHandler, RegisterServerCallback, and RegisterCommand patterns
- **Validation Analysis**: Detects presence or absence of source validation and permission checks
- **Rate Limiting Detection**: Identifies rate limiting and cooldown mechanisms
- **Dangerous Natives**: Detects usage of dangerous FiveM natives (GiveWeaponToPed, SetEntityCoords, etc.)
- **Risk Scoring**: Calculates weighted risk scores (0-100) based on multiple factors
- **Exploit Vector Generation**: Creates detailed exploit vectors with proof-of-concept code
- **Honeypot Detection**: Identifies traps and honeypots designed to catch cheaters
- **Obfuscation Analysis**: Analyzes code obfuscation techniques and difficulty
- **Trigger Chain Analysis**: Detects multi-stage attack chains across multiple files using DFS graph traversal (NEW)

## Usage

### Basic Usage

```python
from ambani_integration.analysis.trigger_analyzer import TriggerAnalyzer

# Initialize analyzer
analyzer = TriggerAnalyzer()

# Analyze a server dump (file or directory)
result = analyzer.analyze_dump('/path/to/server/dump')

if result['success']:
    print(f"Total triggers: {result['summary']['total_triggers']}")
    print(f"Critical: {result['summary']['critical']}")
    print(f"Exploit vectors: {len(result['exploit_vectors'])}")
    print(f"Honeypots: {len(result['honeypots'])}")
    print(f"Trigger chains: {result['summary']['trigger_chains']}")
    print(f"Multi-stage attacks: {result['summary']['multi_stage_attacks']}")
```

### Analyzing Trigger Chains

```python
# Access detected trigger chains
chains = result['trigger_chains']

for chain in chains:
    print(f"Chain: {chain.entry_point.name}")
    print(f"Length: {chain.chain_length} triggers")
    print(f"Combined Risk: {chain.combined_risk_score}/100")
    print(f"Multi-stage Attack: {chain.is_multi_stage_attack}")
    print(f"Path: {' -> '.join([t.name for t in chain.triggers])}")

# Filter high-risk chains
high_risk_chains = [c for c in chains if c.combined_risk_score >= 70]
```

For detailed information about trigger chain analysis, see [README_TRIGGER_CHAIN_ANALYSIS.md](./README_TRIGGER_CHAIN_ANALYSIS.md).

### Analyzing Individual Triggers

```python
from ambani_integration.analysis.trigger_analyzer import Trigger

trigger = Trigger(
    name='esx:giveMoney',
    event_type='RegisterNetEvent',
    file_path='server.lua',
    line_number=10,
    code='xPlayer.addMoney(amount)',
    parameters=['source', 'amount'],
    has_validation=False,
    has_rate_limiting=False,
    dangerous_natives=[],
    risk_score=0,
    category='UNKNOWN'
)

# Calculate risk score
risk_score = analyzer.calculate_risk_score(trigger)
print(f"Risk Score: {risk_score}")

# Detect exploit vectors
exploits = analyzer.detect_exploit_vectors([trigger])
for exploit in exploits:
    print(f"Exploit: {exploit.exploit_type}")
    print(f"PoC: {exploit.proof_of_concept}")
```

### Obfuscation Analysis

```python
code = """
local obfuscated = loadstring(string.char(112, 114, 105, 110, 116))
"""

analysis = analyzer.analyze_obfuscation(code)
print(f"Has obfuscation: {analysis.has_obfuscation}")
print(f"Techniques: {analysis.techniques}")
print(f"Difficulty: {analysis.difficulty_score}")
```

## Risk Score Algorithm

The risk score is calculated using a weighted formula:

```
Risk_Score = (
    validation_score * 0.30 +      # Absence of source validation
    reward_logic_score * 0.25 +    # Presence of money/item rewards
    dangerous_natives_score * 0.25 + # Usage of dangerous natives
    rate_limiting_score * 0.20     # Absence of rate limiting
)
```

### Severity Categories

- **CRITICAL** (≥70): Money/items, admin access, god mode
- **HIGH** (≥50): Teleport, weapons, vehicles
- **MEDIUM** (≥30): Information disclosure, position
- **LOW** (<30): Cosmetic, UI changes

## Exploit Vector Types

1. **Event Injection**: Exploitable RegisterNetEvent/AddEventHandler
2. **Callback Exploitation**: Vulnerable server callbacks
3. **Native Spoofing**: Dangerous natives without validation
4. **Generic Exploit**: Other exploitable patterns

## Honeypot Detection

The analyzer detects honeypots using multiple heuristics:

- **Attractive Names**: giveMoney, addCash, spawnVehicle, etc.
- **Ban Functions**: BanPlayer, DropPlayer with "cheat" reason
- **Silent Honeypots**: Webhook logging without immediate ban
- **Confidence Scoring**: Calculates probability (0.0-1.0) that trigger is a trap

## Data Structures

### Trigger

```python
@dataclass
class Trigger:
    name: str                      # Event name
    event_type: str                # RegisterNetEvent, AddEventHandler, etc.
    file_path: str                 # Source file path
    line_number: int               # Line number in file
    code: str                      # Code block (20 lines)
    parameters: List[str]          # Function parameters
    has_validation: bool           # Has source validation
    has_rate_limiting: bool        # Has rate limiting
    dangerous_natives: List[str]   # Dangerous natives used
    risk_score: int                # Risk score (0-100)
    category: str                  # CRITICAL, HIGH, MEDIUM, LOW
```

### TriggerChain (NEW)

```python
@dataclass
class TriggerChain:
    triggers: List[Trigger]        # All triggers in the chain
    chain_length: int              # Number of triggers
    combined_risk_score: int       # Combined risk (0-100)
    is_multi_stage_attack: bool    # True if dangerous chain
    description: str               # Human-readable description
    entry_point: Trigger           # First trigger (entry)
    exit_points: List[Trigger]     # Last triggers (exits)
```

### ExploitVector

```python
@dataclass
class ExploitVector:
    trigger: Trigger               # Associated trigger
    exploit_type: str              # Type of exploit
    severity: str                  # Severity level
    description: str               # Vulnerability description
    proof_of_concept: str          # PoC Lua code
    impact: str                    # Impact description
    mitigation: str                # Mitigation recommendations
    ambani_compatible: bool        # Compatible with Ambani API
```

### Honeypot

```python
@dataclass
class Honeypot:
    trigger: Trigger               # Associated trigger
    confidence: float              # Confidence score (0.0-1.0)
    detection_mechanism: str       # How it was detected
    ban_function: str              # Ban function used
    is_silent: bool                # Silent honeypot (logs only)
```

## Detection Patterns

### Validation Patterns
- `if not source`
- `IsPlayerAceAllowed`
- `xPlayer.getGroup`
- `QBCore.Functions.HasPermission`
- `CheckPlayerPermission`

### Rate Limiting Patterns
- `cooldown`
- `lastUsed`
- `rateLimiter`
- `throttle`
- `os.time() - last`

### Reward Patterns
- `addMoney`, `addAccountMoney`
- `giveMoney`, `setMoney`
- `addItem`, `giveItem`
- `addInventoryItem`

### Dangerous Natives
- `GiveWeaponToPed`
- `SetEntityCoords`
- `SetPlayerInvincible`
- `NetworkResurrectLocalPlayer`
- `AddCash`

## Example Output

```json
{
  "success": true,
  "triggers": [...],
  "exploit_vectors": [
    {
      "trigger": {
        "name": "esx:giveMoney",
        "risk_score": 75,
        "category": "CRITICAL"
      },
      "exploit_type": "Event Injection",
      "severity": "CRITICAL",
      "proof_of_concept": "TriggerServerEvent('esx:giveMoney', 999999)",
      "impact": "Economy manipulation (money/items)",
      "mitigation": "Add source validation | Implement rate limiting"
    }
  ],
  "honeypots": [
    {
      "trigger": {"name": "giveFreeMoneyNow"},
      "confidence": 0.85,
      "detection_mechanism": "Attractive name with ban logic",
      "is_silent": false
    }
  ],
  "summary": {
    "total_triggers": 10,
    "critical": 2,
    "high": 3,
    "medium": 4,
    "low": 1,
    "trigger_chains": 5,
    "multi_stage_attacks": 3
  },
  "trigger_chains": [
    {
      "chain_length": 3,
      "combined_risk_score": 69,
      "is_multi_stage_attack": true,
      "description": "HIGH multi-stage attack chain: bank:withdraw -> bank:process -> economy:addMoney",
      "entry_point": {"name": "bank:withdraw"},
      "exit_points": [{"name": "economy:addMoney"}]
    }
  ]
}
```

## Testing

Run the test suite:

```bash
pytest tests/analysis/test_trigger_analyzer.py -v
```

## See Also

- [Anticheat Analyzer](./anticheat_analyzer.py) - Detects and profiles anticheats
- [Behavioral Analyzer](./behavioral_analyzer.py) - ML-based anomaly detection
- [Security Reporter](../monitoring/security_reporter.py) - Report generation
