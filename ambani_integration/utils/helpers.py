"""
Helper utilities
Common helper functions used across the application
"""

from typing import Any, Dict, List, Optional
import re
import hashlib


def calculate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of data
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of hash
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize value to 0.0-1.0 range
    
    Args:
        value: Value to normalize
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Normalized value
    """
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def extract_event_name(code: str) -> Optional[str]:
    """
    Extract event name from RegisterNetEvent or AddEventHandler
    
    Args:
        code: Code snippet
        
    Returns:
        Event name if found
    """
    patterns = [
        r'RegisterNetEvent\(["\']([^"\']+)["\']',
        r'AddEventHandler\(["\']([^"\']+)["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            return match.group(1)
    
    return None


def is_dangerous_native(native_name: str) -> bool:
    """
    Check if native is considered dangerous
    
    Args:
        native_name: Native function name
        
    Returns:
        True if dangerous
    """
    dangerous_natives = [
        "GiveWeaponToPed",
        "SetEntityCoords",
        "SetPlayerInvincible",
        "NetworkResurrectLocalPlayer",
        "AddCash",
        "SetPedArmour",
        "SetEntityHealth",
    ]
    
    return any(dangerous in native_name for dangerous in dangerous_natives)


def matches_pattern(text: str, patterns: List[str]) -> bool:
    """
    Check if text matches any pattern (supports wildcards)
    
    Args:
        text: Text to check
        patterns: List of patterns (supports * wildcard)
        
    Returns:
        True if matches any pattern
    """
    for pattern in patterns:
        regex_pattern = pattern.replace("*", ".*")
        if re.search(regex_pattern, text, re.IGNORECASE):
            return True
    return False
