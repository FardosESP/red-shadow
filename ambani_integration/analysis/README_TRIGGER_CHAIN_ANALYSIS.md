# Trigger Chain Analysis

## Overview

The Trigger Chain Analysis feature detects multi-stage attack chains where one trigger calls another trigger across multiple files. This advanced analysis uses Depth-First Search (DFS) graph traversal to identify complex attack vectors that span multiple resources.

## What is a Trigger Chain?

A trigger chain occurs when:
1. Trigger A is called (entry point)
2. Trigger A calls Trigger B (via TriggerEvent, TriggerServerEvent, etc.)
3. Trigger B may call Trigger C, and so on...

This creates a chain of execution that can be exploited by attackers to achieve complex attacks that wouldn't be possible with a single trigger.

## Key Features

### 1. Dependency Graph Building

The analyzer builds a directed graph of trigger dependencies:
- **Nodes**: Individual triggers (RegisterNetEvent, AddEventHandler, etc.)
- **Edges**: Calls between triggers (TriggerEvent, TriggerServerEvent, TriggerClientEvent)

Example:
```
bank:requestWithdraw -> bank:processWithdraw -> economy:addMoney -> logger:logTransaction
```

### 2. DFS Traversal

Uses Depth-First Search to explore all possible paths through the trigger graph:
- Starts from entry points (externally callable triggers)
- Explores all reachable triggers
- Detects cycles and prevents infinite loops
- Identifies all unique chains

### 3. Combined Risk Scoring

Calculates a combined risk score for the entire chain:
- **Formula**: `70% * max_risk + 30% * avg_risk`
- Takes into account the highest risk trigger in the chain
- Also considers the average risk across all triggers
- Results in a more accurate assessment of chain danger

### 4. Multi-Stage Attack Detection

Identifies chains that represent multi-stage attacks:
- **Criteria**: Chain length >= 2 AND combined risk >= MEDIUM threshold (30)
- These chains are particularly dangerous as they:
  - Span multiple files/resources
  - May bypass individual trigger validations
  - Create complex attack paths

### 5. Entry and Exit Point Identification

- **Entry Points**: Triggers that can be called externally (RegisterNetEvent, AddEventHandler, RegisterCommand)
- **Exit Points**: Triggers that don't call other triggers in the chain (dead ends)

## Data Structures

### TriggerChain

```python
@dataclass
class TriggerChain:
    triggers: List[Trigger]              # All triggers in the chain
    chain_length: int                    # Number of triggers
    combined_risk_score: int             # 0-100 risk score
    is_multi_stage_attack: bool          # True if dangerous chain
    description: str                     # Human-readable description
    entry_point: Trigger                 # First trigger (entry)
    exit_points: List[Trigger]           # Last triggers (exits)
```

## Usage

### Basic Analysis

```python
from ambani_integration.analysis.trigger_analyzer import TriggerAnalyzer

# Create analyzer
analyzer = TriggerAnalyzer()

# Analyze server dump
result = analyzer.analyze_dump('/path/to/server/dump')

# Access trigger chains
chains = result['trigger_chains']

for chain in chains:
    print(f"Chain: {chain.entry_point.name}")
    print(f"Length: {chain.chain_length}")
    print(f"Risk: {chain.combined_risk_score}/100")
    print(f"Multi-stage: {chain.is_multi_stage_attack}")
```

### Accessing the Dependency Graph

```python
# After analysis, access the trigger graph
trigger_graph = analyzer.trigger_graph

# Example: See what triggers are called by 'bank:withdraw'
called_triggers = trigger_graph.get('bank:withdraw', [])
print(f"bank:withdraw calls: {called_triggers}")
```

### Filtering High-Risk Chains

```python
# Get only high-risk chains
high_risk_chains = [
    chain for chain in result['trigger_chains']
    if chain.combined_risk_score >= 70
]

# Get only multi-stage attacks
multi_stage = [
    chain for chain in result['trigger_chains']
    if chain.is_multi_stage_attack
]
```

## Analysis Summary

The analysis result includes chain statistics:

```python
result = analyzer.analyze_dump('/path/to/dump')

summary = result['summary']
print(f"Total triggers: {summary['total_triggers']}")
print(f"Trigger chains: {summary['trigger_chains']}")
print(f"Multi-stage attacks: {summary['multi_stage_attacks']}")
```

## Example Attack Scenarios

### Scenario 1: Economy Manipulation Chain

```lua
-- File 1: client.lua
RegisterNetEvent('bank:withdraw')
AddEventHandler('bank:withdraw', function(amount)
    -- No validation!
    TriggerServerEvent('bank:process', amount)
end)

-- File 2: server.lua
RegisterNetEvent('bank:process')
AddEventHandler('bank:process', function(amount)
    -- Calls economy system
    TriggerEvent('economy:addMoney', source, amount)
end)

-- File 3: economy.lua
RegisterNetEvent('economy:addMoney')
AddEventHandler('economy:addMoney', function(player, amount)
    -- No validation!
    xPlayer.addMoney(amount)
end)
```

**Detected Chain**: `bank:withdraw -> bank:process -> economy:addMoney`
- **Length**: 3 triggers
- **Risk**: HIGH (spans 3 files, no validation)
- **Impact**: Unlimited money duplication

### Scenario 2: Privilege Escalation Chain

```lua
-- File 1: admin_client.lua
RegisterNetEvent('admin:request')
AddEventHandler('admin:request', function()
    TriggerServerEvent('admin:check')
end)

-- File 2: admin_server.lua
RegisterNetEvent('admin:check')
AddEventHandler('admin:check', function()
    -- Weak check
    TriggerEvent('admin:grant', source)
end)

-- File 3: permissions.lua
RegisterNetEvent('admin:grant')
AddEventHandler('admin:grant', function(player)
    -- No validation!
    SetPlayerAdmin(player, true)
end)
```

**Detected Chain**: `admin:request -> admin:check -> admin:grant`
- **Length**: 3 triggers
- **Risk**: CRITICAL (privilege escalation)
- **Impact**: Any player can become admin

## Detection Patterns

The analyzer detects trigger calls using these patterns:

```python
trigger_call_patterns = [
    r'TriggerEvent\s*\(\s*["\']([^"\']+)["\']',
    r'TriggerServerEvent\s*\(\s*["\']([^"\']+)["\']',
    r'TriggerClientEvent\s*\(\s*[^,]+,\s*["\']([^"\']+)["\']',
]
```

## Cycle Detection

The DFS algorithm prevents infinite loops by:
1. Tracking visited triggers in the current path
2. Not revisiting triggers already in the path
3. Allowing the same trigger in different paths

Example cycle:
```
A -> B -> A  (cycle detected, stops at second A)
```

## Performance Considerations

- **Time Complexity**: O(V + E) where V = triggers, E = trigger calls
- **Space Complexity**: O(V) for the graph + O(P) for paths
- **Typical Performance**: 
  - 100 triggers: < 0.1 seconds
  - 1000 triggers: < 1 second
  - 10000 triggers: < 10 seconds

## Limitations

1. **Dynamic Trigger Names**: Cannot detect triggers with dynamically generated names
   ```lua
   local eventName = "trigger_" .. math.random(1, 100)
   TriggerEvent(eventName)  -- Not detected
   ```

2. **Conditional Calls**: Doesn't analyze conditions, assumes all paths are possible
   ```lua
   if false then
       TriggerEvent('neverCalled')  -- Still detected as possible
   end
   ```

3. **Obfuscated Code**: May miss triggers in heavily obfuscated code

## Best Practices

### For Security Analysts

1. **Focus on High-Risk Chains**: Prioritize chains with risk >= 70
2. **Check Entry Points**: Verify entry points have proper validation
3. **Analyze Cross-File Chains**: Pay special attention to chains spanning multiple files
4. **Look for Economy Chains**: Chains involving money/items are high priority

### For Developers

1. **Add Validation at Entry Points**: Always validate source at the first trigger
2. **Implement Rate Limiting**: Prevent chain spam attacks
3. **Break Long Chains**: Refactor chains longer than 3-4 triggers
4. **Use Server-Side Validation**: Don't trust client-triggered chains

## Integration with Other Analysis

Trigger chain analysis works alongside:
- **Risk Scoring**: Each trigger has individual risk score
- **Exploit Vector Detection**: Chains become exploit vectors
- **Honeypot Detection**: Chains may lead to honeypots
- **Obfuscation Analysis**: Chains may contain obfuscated triggers

## Future Enhancements

Planned improvements:
1. **Conditional Path Analysis**: Analyze if conditions to determine likely paths
2. **Data Flow Tracking**: Track how data flows through chains
3. **Impact Prediction**: Predict the final impact of executing a chain
4. **Chain Visualization**: Generate visual graphs of trigger chains
5. **Chain Prioritization**: ML-based prioritization of dangerous chains

## References

- **DFS Algorithm**: [Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- **Graph Theory**: [Directed Graphs](https://en.wikipedia.org/wiki/Directed_graph)
- **FiveM Events**: [FiveM Event System](https://docs.fivem.net/docs/scripting-manual/working-with-events/)

## Support

For issues or questions about trigger chain analysis:
1. Check the test suite: `tests/analysis/test_trigger_chain_analysis.py`
2. Run the demo: `python examples/trigger_chain_analysis_demo.py`
3. Review the implementation: `ambani_integration/analysis/trigger_analyzer.py`
