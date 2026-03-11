"""
RED-SHADOW Ambani Integration
Advanced security analysis platform for FiveM servers

This package provides comprehensive security analysis capabilities including:
- Trigger and event analysis for Ambani exploits
- Anticheat detection and profiling
- Machine learning-based behavioral analysis
- Memory forensics and bytecode decompilation
- AI-driven decision engine for exploit strategies
- Automated resource control with safe-stop capabilities
- Real-time network monitoring and deep packet inspection
"""

__version__ = "1.0.0"
__author__ = "RED-SHADOW Team"

# Core modules
from . import analysis
from . import intelligence
from . import execution
from . import monitoring
from . import forensics
from . import utils
from . import config

__all__ = [
    "analysis",
    "intelligence",
    "execution",
    "monitoring",
    "forensics",
    "utils",
    "config",
]
