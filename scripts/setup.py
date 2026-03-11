#!/usr/bin/env python3
"""
Setup script for Ambani Integration
"""

import os
import sys


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/training",
        "logs",
        "reports",
        "rules",
        "rules/yara",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def create_default_config():
    """Create default configuration file"""
    import json
    from ambani_integration.config.settings import DEFAULT_CONFIG
    
    config_path = "config.json"
    
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"Created default configuration: {config_path}")
    else:
        print(f"Configuration already exists: {config_path}")


def main():
    """Main setup function"""
    print("Setting up Ambani Integration...")
    
    create_directories()
    create_default_config()
    
    print("\nSetup complete!")
    print("Next steps:")
    print("1. Review and customize config.json")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application")


if __name__ == "__main__":
    main()
