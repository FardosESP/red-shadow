"""
Configuration Layer
Configuration management and settings

Components:
- config_manager: Configuration loading and management
- settings: Application settings and defaults
"""

from .config_manager import ConfigManager
from .settings import Settings, DEFAULT_CONFIG

__all__ = [
    "ConfigManager",
    "Settings",
    "DEFAULT_CONFIG",
]
