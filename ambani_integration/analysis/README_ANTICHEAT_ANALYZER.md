# Anticheat Analyzer

Comprehensive anticheat detection and profiling system with bypass strategy recommendations.

## Overview

The Anticheat Analyzer detects and profiles anticheat systems using signature fingerprinting and behavioral analysis. It provides detailed information about anticheat capabilities, limitations, and suggests bypass techniques based on the detected profile.

## Features

### 1. Anticheat Detection (Task 3.1)
- Signature-based fingerprinting for 23+ known anticheats
- Pattern matching using regex
- Version extraction
- Confidence scoring

### 2. Signature Database (Task 3.2)
Supports detection of:
- **Premium Anticheats**: FiveGuard, Phoenix AC, Sentinel Pro, Omega Protection
- **Commercial Anticheats**: FireAC, WaveShield, Qprotect, BadgerAC
- **Advanced Systems**: Vanguard, Titan Shield, Nexus AC, Warden
- **Standard Protection**: Guardian, Aegis, Fortress, Bastion, Citadel
- **Basic Systems**: Paladin, Rampart, Bulwark, Defender
- **Custom/Silent**: Behavioral detection for unknown anticheats

### 3. Profile Creation (Task 3.3)
Each detected anticheat gets a detailed profile with:
- Name and version
- Capabilities (memory scanning, event monitoring, rate limiting, etc.)
- Limitations (false positives, resource usage, etc.)
- Bypass difficulty score (0.0 to 1.0)
- Recommended bypass techniques
- Detection patterns found

### 4. Detection Risk Calculation (Task 3.4)
Calculates risk scores based on:
- Anticheat bypass difficulty
- Planned actions (stop resource, trigger event, modify money, etc.)
- Action multipliers for high-risk operations
- Combined risk from multiple anticheats

### 5. Bypass Technique Suggestions (Task 3.5)
Provides tailored bypass suggestions:
- Base techniques from anticheat profile
- Capability-specific bypasses (memory evasion, event spoofing, etc.)
- Limitation-based opportunities (false positive exploitation, resource exhaustion)
- Success probability estimates
- Required resources and skills

### 6. Silent Anticheat Detection (Task 3.6)
Detects hidden/custom anticheats using behavioral indicators:
- Silent ban patterns
- Hidden logging
- Obfuscated checks
- Encrypted communication

### 7. Update Detection (Task 3.7)
Monitors for anticheat updates:
- Pattern change analysis
- Version tracking
- Update alerts
- Pattern diff reporting

## Usage

### Basic Detection

```python
from ambani_integration.analysis.anticheat_analyzer import AnticheatAnalyzer

# Initialize analyzer
analyzer = AnticheatAnalyzer()

# Prepare code base
code_base = {
    "server.lua": "-- FiveGuard v2.5.0\nlocal FiveGuard = {}",
    "config.lua": "Config.FiveGuard = { enabled = true }"
}

# Detect anticheats
profiles = analyzer.detect_anticheats(code_base)

for profile in profiles:
    print(f"Detected: {profile.name} v{profile.version}")
    print(f"Confidence: {profile.confidence:.2f}")
    print(f"Bypass Difficulty: {profile.bypass_difficulty:.2f}")
```

### Risk Assessment

```python
# Calculate detection risk
planned_actions = ["stop_resource", "trigger_event", "modify_money"]
risk_score = analyzer.calculate_detection_risk(profiles, planned_actions)

print(f"Detection Risk: {risk_score:.2f}")
```

### Bypass Suggestions

```python
# Get bypass technique suggestions
for profile in profiles:
    suggestions = analyzer.suggest_bypass_techniques(profile)
    
    print(f"\nBypass suggestions for {profile.name}:")
    for suggestion in suggestions:
        print(f"  - {suggestion['technique']}")
        print(f"    Difficulty: {suggestion['difficulty']:.2f}")
        print(f"    Success Rate: {suggestion['success_probability']:.2f}")
        print(f"    Description: {suggestion['description']}")
```

### Strategy Recommendation

```python
# Get recommended overall strategy
strategy = analyzer.get_recommended_strategy(profiles)

print(f"Recommended Strategy: {strategy['strategy']}")
print(f"Max Stops Per Minute: {strategy['max_stops_per_minute']}")
print(f"Grace Period: {strategy['grace_period']} seconds")
```

### Component Stop Risk

```python
# Check risk of stopping specific anticheat component
risk = analyzer.get_component_stop_risk("FiveGuard", "screen_capture")

print(f"Component: {risk['component']}")
print(f"Detection Risk: {risk['detection_risk']:.2f}")
print(f"Stop Safety: {risk['stop_safety']}")
print(f"Bypass Benefit: {risk['bypass_benefit']}")
```

### Main Anticheat Stop Risk

```python
# Check risk of stopping main anticheat resource
risk = analyzer.get_main_anticheat_stop_risk("FiveGuard")

print(f"Can Stop: {risk['can_stop']}")
print(f"Detection Risk: {risk['detection_risk']:.2f}")
print(f"Consequences: {risk['consequences']}")
print(f"Recommended: {risk['recommended']}")

for strategy in risk['bypass_strategies']:
    print(f"\nStrategy: {strategy['name']}")
    print(f"  Difficulty: {strategy['difficulty']:.2f}")
    print(f"  Success Rate: {strategy['success_rate']:.2f}")
```

## Bypass Strategy Categories

### 1. Resource Stop Bypass
- Stop screen capture components
- Stop process scanners
- Stop event monitors
- Stop webhook loggers
- Stop main anticheat (EXTREME RISK)

### 2. Memory Manipulation
- DLL injection
- Function hooking
- Memory patching
- Thread suspension

### 3. Network-Level Blocking
- Webhook URL blocking
- API endpoint blocking
- DNS poisoning
- Firewall rules

### 4. File System Manipulation
- File rename/move
- Permission changes
- File corruption

### 5. Timing-Based Bypass
- Server restart windows
- Low player count periods
- Admin offline timing
- Maintenance mode exploitation

### 6. Obfuscation Techniques
- Gradual stops
- Legitimate cover
- Admin impersonation
- False positive generation

### 7. Combination Strategies
- Network + Resource stops
- Timing + Obfuscation
- Memory + Network
- Full spectrum attacks

## Risk Levels

### Detection Risk Scores
- **0.0 - 0.3**: Low risk - Basic anticheats, minimal monitoring
- **0.3 - 0.5**: Moderate risk - Standard protection, some monitoring
- **0.5 - 0.7**: High risk - Strong anticheats, active monitoring
- **0.7 - 0.85**: Very high risk - Advanced systems, ML detection
- **0.85 - 1.0**: Extreme risk - Premium anticheats, aggressive protection

### Recommended Strategies
- **Aggressive** (0.0-0.5): Fast exploitation, minimal delays
- **Standard** (0.5-0.7): Moderate caution, some evasion
- **Stealth** (0.7-0.85): High caution, advanced evasion
- **Ultra Stealth** (0.85-1.0): Maximum caution, all techniques

## Data Files

### anticheat_resource_matrix.json
Defines which resources can be safely stopped with each anticheat:
- Safe to stop resources
- Risky to stop resources
- Never stop resources
- Detection methods
- Bypass difficulty scores

### anticheat_bypass_strategies.json
Comprehensive bypass strategy database:
- Bypass categories and techniques
- Anticheat component information
- Main anticheat stop strategies
- Advanced techniques (DLL injection, hooking, etc.)
- Combination strategies
- Risk matrices

## Integration

The Anticheat Analyzer integrates with:
- **Auto Stop Engine**: Provides risk scores for stop decisions
- **AI Decision Engine**: Informs strategy selection
- **Security Reporter**: Includes anticheat analysis in reports
- **Behavioral Analyzer**: Combines with ML-based detection

## Legal Notice

**FOR SECURITY RESEARCH AND AUTHORIZED PENETRATION TESTING ONLY**

This tool is designed for:
- Security researchers analyzing anticheat systems
- Server administrators testing their own security
- Authorized penetration testing with explicit permission

Unauthorized use against production servers is illegal and unethical.

## Example Output

```
Detected Anticheats:
  1. FiveGuard v2.5.1 (Confidence: 0.90)
     - Capabilities: memory_scanning, event_injection_detection, aggressive_rate_limiting
     - Limitations: high_false_positive_rate, resource_intensive
     - Bypass Difficulty: 0.85
     - Recommended Strategy: ultra_stealth

Detection Risk: 0.92 (EXTREME)
Recommended Strategy: ultra_stealth
Max Stops Per Minute: 1
Grace Period: 300 seconds

Bypass Suggestions:
  1. ultra_stealth_mode (Difficulty: 0.85, Success: 0.15)
  2. timing_randomization (Difficulty: 0.85, Success: 0.15)
  3. memory_evasion (Difficulty: 0.75, Success: 0.40)
  4. event_spoofing (Difficulty: 0.70, Success: 0.45)
```

## Testing

Run tests with:
```bash
python -m pytest tests/analysis/test_anticheat_analyzer.py -v
```

## See Also

- [Trigger Analyzer](README_TRIGGER_ANALYZER.md)
- [Trigger Chain Analysis](README_TRIGGER_CHAIN_ANALYSIS.md)
- [Behavioral Analyzer](../intelligence/README_BEHAVIORAL_ANALYZER.md)
- [Auto Stop Engine](../execution/README_AUTO_STOP_ENGINE.md)
