# Auto Stop Engine - Professional Strategies Integration

## Overview

The Auto Stop Engine is an intelligent resource stopping system that uses ML-based confidence scoring and professional knowledge to make safe decisions about stopping FiveM resources. It integrates expert knowledge about what professionals actually stop with each anticheat to maximize exploitation while minimizing detection risk.

## Key Features

### 1. Professional Strategies Database
- **7 Anticheats Covered**: FiveGuard, Phoenix AC, WaveShield, FireAC, BadgerAC, Qprotect, No Anticheat
- **Expert Knowledge**: Real strategies used by professionals in HvH and bypass scenarios
- **Risk Levels**: Detection risk scores for each resource type with each anticheat
- **Timing Guidance**: When to stop resources for maximum stealth
- **Alternative Techniques**: Memory hooks, network blocking, crash simulation

### 2. Intelligent Decision Making
- **Multi-Factor Scoring**: Combines resource classification, trigger risk, stop detection, anticheat risk, and ML predictions
- **Professional Approval**: Requires professional recommendation before stopping
- **Confidence Thresholds**: Adjustable confidence levels (default 0.7)
- **Grace Periods**: 5-minute grace period for newly started resources
- **Rate Limiting**: Maximum 3 stops per minute

### 3. Resource Classification
- **CRITICAL**: Never stop (frameworks, databases, anticheats)
- **RISKY**: High risk to stop (economy, admin, weapons)
- **SAFE**: Safe to stop (cosmetic, UI)
- **VULNERABLE**: Should be stopped (exploitable resources)

### 4. Learning System
- **Admin Feedback**: Record correct/incorrect decisions
- **Threshold Adjustment**: Automatically adjust confidence threshold based on precision
- **Statistics Tracking**: TP, FP, TN, FN, precision, recall, F1 score
- **Continuous Improvement**: Learn from mistakes to improve future decisions

### 5. Operation Modes
- **MANUAL**: Require admin approval for each stop
- **NOTIFY**: Stop automatically but notify admin
- **AUTO**: Fully automatic stopping

## Professional Strategies by Anticheat

### FiveGuard (EXTREME Difficulty)
**Detection Level**: VERY_HIGH (0.95)

**Priority Stops**:
- Screenshot resources (0.95 risk) - Stop only 2-3 seconds during visual exploits
- Webhook resources (0.85 risk) - Block notifications to admins

**Never Stop**:
- FiveGuard itself
- Any anticheat resource
- Economy resources (banking, inventory)
- Admin resources

**Professional Workflow**:
1. Block webhooks in firewall
2. Identify screenshot resources
3. Stop screenshot for 2-3 seconds
4. Execute visual exploit quickly
5. Restart screenshot resource
6. NO other resource stops
7. Use 5+ minute delays between actions

**Expert Notes**:
- FiveGuard logs ALL resource stops with timestamp and player ID
- Correlates stops with player actions (stop screenshot + teleport = ban)
- Professionals prefer memory hooks over resource stops
- MAX 1 stop every 10 minutes

### WaveShield (LOW Difficulty)
**Detection Level**: MINIMAL (0.30)

**Safe Stops**:
- Almost everything except core/framework
- Economy resources
- Job resources
- Vehicle resources
- Weapon resources

**Professional Workflow**:
1. Stop banking/economy resources
2. Stop inventory resources
3. Execute exploits freely
4. Stop vehicle spawner for unlimited spawns
5. No need to restart - WaveShield doesn't detect
6. Rate limit: 3-4 stops per minute is safe

**Expert Notes**:
- WaveShield is the WEAKEST for resource stops
- Professionals treat it as "no anticheat"
- Only risk: txAdmin logs if active
- Can stop 10 resources in a row without issue

### Phoenix AC (HIGH Difficulty)
**Detection Level**: MODERATE (0.70)

**Priority Stops**:
- Screenshot resources (0.70 risk)
- Event logger resources (0.60 risk)
- Webhook resources (0.55 risk)

**Safe Stops**:
- Cosmetic resources (clothing, barber, tattoo)
- UI resources (hud, menu, notifications)
- Job resources (delivery, mechanic, taxi)

**Professional Workflow**:
1. Wait for 10+ players online (less suspicious)
2. Stop webhook resource
3. Wait 2 minutes
4. Stop event_logger if exists
5. Wait 3 minutes
6. Execute exploits
7. Reiniciar recursos after 5 minutes
8. Act normal for 10+ minutes

**Expert Notes**:
- Phoenix AC has health checks every 5 minutes
- Does NOT ban automatically, only alerts admins
- Optimal window: 3-5 AM when admins sleep
- MAX 2 stops every 5 minutes

### FireAC (VERY_HIGH Difficulty)
**Detection Level**: HIGH (0.88)

**ML Evasion Tactics**:
- Vary timing between stops (never same interval)
- Stop different resources each time
- Mix stops with legitimate activity
- Use gradual degradation for natural crashes

**Professional Workflow**:
1. Play normally for 30+ minutes (train ML)
2. Generate artificial lag (spawn 50+ props)
3. During lag, stop 1 resource
4. Wait 15+ minutes
5. Repeat with DIFFERENT resource
6. Never stop more than 2 resources in 1 hour
7. Vary days/times of activity

**Expert Notes**:
- FireAC uses ML to detect anomalies
- Professionals "train" the model first by playing legitimately
- Correlates stops with post-stop behavior
- Best strategy: NO stops, use memory manipulation

### BadgerAC (VERY_LOW Difficulty)
**Detection Level**: MINIMAL (0.25)

**Safe Stops**:
- Almost everything except core and BadgerAC itself

**Professional Workflow**:
1. Stop all vulnerable resources
2. Execute exploits freely
3. Rate limit: 4-5 stops per minute is safe

**Expert Notes**:
- BadgerAC is one of the WEAKEST anticheats
- Only basic client exploit detection
- Does NOT monitor resource stops effectively
- Professionals ignore it completely

### Qprotect (HIGH Difficulty)
**Detection Level**: HIGH (0.82)

**Priority Stops**:
- Webhook resources (0.82 risk) - FIRST priority
- Screenshot resources (0.65 risk) - After webhooks blocked
- Admin log resources (0.70 risk) - If using admin commands

**Professional Workflow**:
1. Identify ALL webhook URLs in configs
2. Block in firewall: discord.com, webhook.site, discordapp.com
3. Verify block with packet capture
4. Stop webhook resources
5. Wait 5 minutes
6. Stop screenshot resources
7. Execute exploits
8. Restart resources after 10 minutes

**Expert Notes**:
- Qprotect is "webhook-dependent" - blind without webhooks
- Professionals ALWAYS block network first
- Has admin review - human checks logs
- Optimal window: when admins offline (night/early morning)
- MAX 1 stop every 8 minutes

## Usage Examples

### Basic Usage
```python
from ambani_integration.execution.auto_stop_engine import AutoStopEngine, StopMode

# Initialize engine
engine = AutoStopEngine(
    mode=StopMode.NOTIFY,
    confidence_threshold=0.7
)

# Make stop decision
decision = engine.should_stop_resource(
    resource_name="banking_system",
    triggers=[{'risk_score': 0.8}],
    code_content="RegisterServerEvent('bank:deposit')",
    anticheat_name="FiveGuard"
)

print(f"Should stop: {decision.should_stop}")
print(f"Confidence: {decision.confidence_score:.2f}")
print(f"Detection risk: {decision.anticheat_risk:.2f}")
```

### Get Professional Recommendation
```python
# Get professional recommendation for a resource
rec = engine.get_professional_recommendation('screenshot_capture', 'FiveGuard')

print(f"Recommended: {rec['recommended']}")
print(f"Detection risk: {rec['detection_risk']:.2f}")
print(f"Timing: {rec['timing']}")
print(f"Pro tip: {rec['professional_tip']}")
```

### Learning from Feedback
```python
# Record admin feedback
engine.record_feedback(
    resource_name='test_resource',
    was_correct=True,
    admin_comment='Good stop'
)

# Get statistics
stats = engine.get_statistics()
print(f"Precision: {stats['precision']:.2f}")
print(f"F1 Score: {stats['f1_score']:.2f}")
```

## Configuration

### Confidence Threshold
- **Default**: 0.7
- **Range**: 0.0 to 1.0
- **Higher**: More conservative (fewer stops, fewer false positives)
- **Lower**: More aggressive (more stops, more false positives)

### Grace Period
- **Default**: 300 seconds (5 minutes)
- **Purpose**: Prevent stopping newly started resources
- **Adjustable**: Set `engine.grace_period_seconds`

### Rate Limiting
- **Default**: 3 stops per minute
- **Purpose**: Prevent detection through rapid stops
- **Adjustable**: Set `engine.max_stops_per_minute`

## Integration with Other Components

### Anticheat Analyzer
```python
from ambani_integration.analysis.anticheat_analyzer import AnticheatAnalyzer

anticheat_analyzer = AnticheatAnalyzer()
engine = AutoStopEngine(anticheat_analyzer=anticheat_analyzer)
```

### Behavioral Analyzer
```python
from ambani_integration.analysis.behavioral_analyzer import BehavioralAnalyzer

behavioral_analyzer = BehavioralAnalyzer()
engine = AutoStopEngine(behavioral_analyzer=behavioral_analyzer)
```

### Resource Controller
```python
from ambani_integration.execution.resource_controller import ResourceController

resource_controller = ResourceController()
success = engine.execute_stop(
    resource_name='test_resource',
    decision=decision,
    resource_controller=resource_controller
)
```

## Advanced Techniques

### Crash Simulation
Make stops appear as natural crashes by corrupting resource memory gradually.
- **Detection Risk**: 0.30
- **Effectiveness**: 0.85
- **Use With**: FiveGuard, FireAC

### Maintenance Window Exploit
Stop resources during server restart/maintenance windows.
- **Detection Risk**: 0.20
- **Effectiveness**: 0.90
- **Use With**: All anticheats

### Gradual Degradation
Degrade resource slowly instead of abrupt stop.
- **Detection Risk**: 0.35
- **Effectiveness**: 0.80
- **Use With**: FireAC, FiveGuard (evades ML detection)

## Red Flags to Avoid

### Instant Ban Triggers
- Stopping anticheat resource itself
- Stopping framework (ESX, QBCore)
- Stopping database resources
- Stopping txAdmin
- Multiple resources in <1 minute
- Stop + exploit in <30 seconds

### High Suspicion Actions
- Stopping same resource repeatedly
- Stopping during low player count
- Stopping immediately after join
- No legitimate activity before stops
- Predictable stop patterns

## Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/execution/test_auto_stop_engine.py -v
```

Run the example usage:
```bash
python examples/auto_stop_engine_usage.py
```

## Files

- `auto_stop_engine.py` - Main engine implementation
- `professional_stop_strategies.json` - Expert knowledge database
- `test_auto_stop_engine.py` - Comprehensive test suite (28 tests)
- `auto_stop_engine_usage.py` - Usage examples
- `README_AUTO_STOP_ENGINE.md` - This documentation

## Statistics

- **28 Tests**: All passing
- **7 Anticheats**: Full professional strategies
- **4 Classifications**: CRITICAL, RISKY, SAFE, VULNERABLE
- **3 Operation Modes**: MANUAL, NOTIFY, AUTO
- **10 Subtasks**: All completed (Task 8.1-8.10)

## Legal Notice

This tool is for authorized security research and penetration testing only. Unauthorized use against production servers is illegal and unethical. Always obtain proper authorization before testing.

## References

- Task 8.1-8.10 in `.kiro/specs/ambani-integration/tasks.md`
- Professional strategies in `ambani_integration/data/professional_stop_strategies.json`
- Anticheat resource matrix in `ambani_integration/data/anticheat_resource_matrix.json`
- Bypass strategies in `ambani_integration/data/anticheat_bypass_strategies.json`
