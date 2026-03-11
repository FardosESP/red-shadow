"""
System-wide constants
"""

# Version
VERSION = "1.0.0"

# Critical resources that should never be stopped automatically
CRITICAL_RESOURCES = [
    # FiveM Core
    "sessionmanager", "mapmanager", "spawnmanager", "baseevents",
    "chat", "hardcap", "rconlog", "playernames",
    
    # Frameworks
    "es_extended", "qb-core", "ox_core", "vrp", "vRP",
    
    # Database
    "oxmysql", "mysql-async", "ghmattimysql",
    
    # Admin Tools
    "txAdmin", "txAdminClient", "monitor",
    
    # Anticheats
    "FiveGuard", "WaveShield", "PhoenixAC", "FireAC", "BadgerAC"
]

# Risky resources that may trigger auto-ban if stopped
RISKY_RESOURCES = [
    "*anticheat*", "*ac_*", "*anti-cheat*", "*protection*",
    "*logger*", "*log*", "*audit*",
    "*admin*", "*moderator*", "*staff*"
]

# Safe resources to stop
SAFE_RESOURCES = [
    "*shop*", "*store*", "*garage*", "*clothing*", "*barber*",
    "*tattoo*", "*phone*", "*hud*", "*ui*", "*menu*",
    "*job_*", "*work_*", "*mechanic*", "*taxi*", "*delivery*",
    "*vehicle*", "*car*", "*weapon*", "*gun*"
]

# Vulnerable resource patterns (high priority for analysis)
VULNERABLE_RESOURCES = [
    "*bank*", "*atm*", "*money*", "*cash*", "*economy*",
    "*shop*", "*store*", "*buy*", "*sell*",
    "*inventory*", "*item*", "*loot*", "*drop*",
    "*admin*", "*mod*", "*staff*", "*manage*"
]

# Dangerous natives that can be exploited
DANGEROUS_NATIVES = [
    "GiveWeaponToPed",
    "SetEntityCoords",
    "SetPlayerInvincible",
    "NetworkResurrectLocalPlayer",
    "AddCash",
    "SetPedArmour",
    "SetEntityHealth",
    "SetVehicleEngineHealth",
    "SetVehicleBodyHealth",
    "NetworkExplodeVehicle",
]

# Anticheat signatures
ANTICHEAT_SIGNATURES = {
    "FiveGuard": {
        "patterns": ["FiveGuard", "fg_", "anticheat.fiveguard"],
        "capabilities": ["event_injection_detection", "native_spoofing_detection", "aggressive_rate_limiting"],
        "bypass_difficulty": 0.85
    },
    "Phoenix AC": {
        "patterns": ["PhoenixAC", "pac_", "phoenix.anticheat"],
        "capabilities": ["pattern_matching", "behavior_analysis", "moderate_rate_limiting"],
        "bypass_difficulty": 0.70
    },
    "WaveShield": {
        "patterns": ["WaveShield", "ws_", "waveshield.protection"],
        "capabilities": ["static_analysis", "signature_detection", "light_rate_limiting"],
        "bypass_difficulty": 0.50
    }
}

# Risk score thresholds
RISK_THRESHOLD_CRITICAL = 70
RISK_THRESHOLD_HIGH = 50
RISK_THRESHOLD_MEDIUM = 30

# Stop confidence thresholds
STOP_CONFIDENCE_HIGH = 0.80
STOP_CONFIDENCE_LOW = 0.60

# Default configuration values
DEFAULT_RATE_LIMIT = 5  # events per second
DEFAULT_GRACE_PERIOD = 300  # seconds
DEFAULT_MAX_STOPS_PER_MINUTE = 3
DEFAULT_CRITICAL_THRESHOLD = 85

# Sandbox restrictions
SANDBOX_BLOCKED_FUNCTIONS = [
    "os.execute", "os.exit", "io.popen",
    "loadfile", "dofile", "require",
    "debug.getinfo", "debug.setmetatable"
]

SANDBOX_BLOCKED_MODULES = ["io", "os", "debug", "package", "ffi"]

SANDBOX_MEMORY_LIMIT = 100 * 1024 * 1024  # 100 MB
SANDBOX_CPU_TIME_LIMIT = 5  # seconds
SANDBOX_INSTRUCTION_LIMIT = 1000000
