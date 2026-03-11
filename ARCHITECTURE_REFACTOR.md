# Architecture Refactoring: Event Farming System

## Problem Identified
Duplicate functionality between Python and Lua modules causing confusion and maintenance issues.

## Solution: Clear Separation of Responsibilities

### Before (Problematic)
- `event_monitor.py` - Had capture, analysis, and script generation (too much)
- `event_capture.lua` - Had capture AND analysis logic (duplicate)
- Unclear boundaries between components

### After (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT FARMING PIPELINE                    │
└─────────────────────────────────────────────────────────────┘

1. CAPTURE (Lua Client-Side)
   ├─ event_capture.lua
   ├─ Lightweight real-time capture
   ├─ Minimal processing for performance
   └─ Output: captured_events.json

2. ANALYZE (Python Server-Side)
   ├─ event_analyzer.py (NEW)
   ├─ Statistical analysis
   ├─ ML pattern detection
   ├─ Risk assessment with anticheat_analyzer
   ├─ Strategy optimization
   └─ Output: farming_strategies.json

3. COORDINATE (Python)
   ├─ event_monitor.py (REFACTORED)
   ├─ Workflow coordinator
   ├─ Simplified interface
   └─ Automates pipeline

4. EXECUTE (Lua Client-Side)
   ├─ auto_farmer.lua (NEW)
   ├─ Reads farming_strategies.json
   ├─ Executes with Ambani API
   ├─ Rate limiting & stealth
   └─ Real-time statistics
```

## New Files Created

### `ambani_integration/intelligence/event_analyzer.py`
- **Purpose**: Advanced event data analysis
- **Input**: captured_events.json (from Lua)
- **Output**: farming_strategies.json (for Lua)
- **Features**:
  - Statistical confidence calculation
  - Detection risk assessment
  - Profit per hour optimization
  - Anticheat integration
  - ML-ready architecture

### `ambani_integration/lua_scripts/auto_farmer.lua`
- **Purpose**: Automated farming execution
- **Input**: farming_strategies.json (from Python)
- **Features**:
  - Strategy loading and filtering
  - Cooldown management
  - Rate limiting (max exec/hour)
  - Random timing for stealth
  - Real-time statistics
  - Enable/disable individual strategies
  - Safe mode protection

### `tests/intelligence/test_event_analyzer.py`
- **Purpose**: Comprehensive test suite
- **Coverage**:
  - Data loading
  - Strategy analysis
  - Filtering logic
  - Risk calculation
  - Export functionality
  - Edge cases

### `examples/event_monitor_usage.py`
- **Purpose**: Real functional example
- **Shows**: Complete workflow automation

## Modified Files

### `ambani_integration/intelligence/event_monitor.py`
- **Before**: Monolithic class with all logic
- **After**: Lightweight coordinator
- **Removed**: Duplicate analysis logic, script generation
- **Added**: Simple workflow automation

### `ambani_integration/lua_modules/event_capture.lua`
- **Simplified**: Removed complex analysis
- **Focus**: Pure capture functionality
- **Kept**: Basic reward detection for real-time feedback

## Benefits

### 1. Clear Separation of Concerns
- Lua does real-time capture (what it's good at)
- Python does complex analysis (what it's good at)
- Each component has single responsibility

### 2. Better Performance
- Lua capture is lightweight (no heavy processing)
- Python analysis can use full ML capabilities
- No performance impact on FiveM client

### 3. Easier Maintenance
- Each file has clear purpose
- No duplicate code
- Changes isolated to specific components

### 4. Better Testing
- Each component testable independently
- Mock data easy to create
- Clear input/output contracts

### 5. Scalability
- Can add more analyzers without touching capture
- Can improve farming logic without touching analysis
- Can swap components independently

## Data Flow

```
FiveM Client (Lua)
    ↓
event_capture.lua
    ↓ (captures events)
captured_events.json
    ↓
Python Analysis
    ↓
event_analyzer.py
    ↓ (analyzes patterns)
farming_strategies.json
    ↓
FiveM Client (Lua)
    ↓
auto_farmer.lua
    ↓ (executes farming)
Profit!
```

## Language Choice Rationale

### Why Lua for Capture & Execution?
- Runs client-side in FiveM (required)
- Real-time event hooks (AddEventHandler)
- Direct access to Ambani API
- Minimal latency

### Why Python for Analysis?
- Complex statistical analysis
- Machine learning libraries
- Anticheat integration
- Database operations
- Better for heavy computation

### Why JSON for Communication?
- Language-agnostic
- Human-readable
- Easy to debug
- Standard format

## Usage Pattern

### Automated Workflow
```python
from ambani_integration.intelligence.event_monitor import EventMonitor

monitor = EventMonitor(anticheat_analyzer=ac_analyzer)

# Analyze captured data
strategies = monitor.analyze_captured_events("captured_events.json")

# Export for Lua
monitor.export_strategies_for_lua("farming_strategies.json")

# Done - auto_farmer.lua can now load and execute
```

### Manual Steps (if needed)
1. FiveM: `/capture start` → play → `/capture save`
2. Python: Run event_monitor_usage.py
3. FiveM: `/farmer load` → `/farmer start`

## Future Enhancements

### Potential Additions
- Real-time streaming (Lua → Python via WebSocket)
- ML model training on captured data
- Adaptive strategy adjustment
- Multi-server analysis
- Pattern anomaly detection

### Easy to Add Because
- Clean interfaces
- Modular design
- Clear data contracts
- Independent components

## Conclusion

This refactoring transforms a monolithic, confusing system into a clean, maintainable pipeline where each component does exactly what it should do, in the language best suited for the task.
