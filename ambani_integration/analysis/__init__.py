"""
Analysis Layer
Provides static and dynamic analysis capabilities for FiveM server code

Components:
- TriggerAnalyzer: Analyzes triggers and events for Ambani exploits
- AnticheatAnalyzer: Detects and profiles anticheat systems
- BehavioralAnalyzer: ML-based anomaly detection and behavior analysis
"""

from .trigger_analyzer import TriggerAnalyzer
from .anticheat_analyzer import AnticheatAnalyzer
from .behavioral_analyzer import BehavioralAnalyzer

__all__ = [
    "TriggerAnalyzer",
    "AnticheatAnalyzer",
    "BehavioralAnalyzer",
]
