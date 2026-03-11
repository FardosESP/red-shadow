"""
Validation utilities
Input validation and sanitization
"""

import os
import re
from typing import Optional


def validate_file_path(path: str) -> bool:
    """
    Validate file path exists and is readable
    
    Args:
        path: File path to validate
        
    Returns:
        True if valid
    """
    return os.path.isfile(path) and os.access(path, os.R_OK)


def validate_directory_path(path: str) -> bool:
    """
    Validate directory path exists and is accessible
    
    Args:
        path: Directory path to validate
        
    Returns:
        True if valid
    """
    return os.path.isdir(path) and os.access(path, os.R_OK)


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address format
    
    Args:
        ip: IP address string
        
    Returns:
        True if valid IPv4 address
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    octets = ip.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def validate_resource_name(name: str) -> bool:
    """
    Validate FiveM resource name format
    
    Args:
        name: Resource name
        
    Returns:
        True if valid
    """
    # Resource names should be alphanumeric with hyphens/underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', text)
    return sanitized.strip()
