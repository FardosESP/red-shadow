"""
Example: Logging system integrated with ConfigManager
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ambani_integration.config.config_manager import ConfigManager
from ambani_integration.utils.logger import configure_logging, get_logger


def main():
    """Demonstrate logging with configuration file"""
    
    print("=" * 60)
    print("Logging with Configuration File")
    print("=" * 60)
    
    # Create a custom config file
    config_data = {
        "logging": {
            "level": "DEBUG",
            "file": "./logs/ambani_integration.log",
            "console": True,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "ambani": {
            "enabled": True,
            "safe_mode": True
        }
    }
    
    config_path = "./config_example.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"\n1. Created configuration file: {config_path}")
    print(f"   Log level: {config_data['logging']['level']}")
    print(f"   Log file: {config_data['logging']['file']}")
    
    # Load configuration
    config_manager = ConfigManager(config_path)
    
    # Configure logging from config file
    configure_logging(config_manager)
    
    print("\n2. Logging system configured from file")
    
    # Use loggers
    print("\n3. Testing different log levels:")
    
    logger = get_logger("ambani_integration.main")
    logger.debug("DEBUG: Starting Ambani integration analysis")
    logger.info("INFO: Configuration loaded successfully")
    logger.warning("WARNING: Safe mode is enabled")
    logger.error("ERROR: This is a test error message")
    logger.critical("CRITICAL: This is a test critical message")
    
    # Module-specific loggers
    print("\n4. Module-specific loggers:")
    
    trigger_logger = get_logger("ambani_integration.analysis.trigger_analyzer")
    trigger_logger.info("Analyzing server dump...")
    trigger_logger.warning("Found 5 triggers without validation")
    trigger_logger.error("Critical vulnerability detected in resource: bank_system")
    
    resource_logger = get_logger("ambani_integration.execution.resource_controller")
    resource_logger.info("Auto-stop mode: notify")
    resource_logger.warning("Resource 'bank_system' has risk score: 92")
    resource_logger.info("Sending notification to administrator")
    
    ml_logger = get_logger("ambani_integration.ml.behavioral_analyzer")
    ml_logger.debug("Loading ML models...")
    ml_logger.info("Isolation Forest model loaded")
    ml_logger.info("Anomaly score calculated: 0.87")
    
    print(f"\n5. All logs written to: {config_data['logging']['file']}")
    print(f"   Check the file to see all DEBUG messages")
    
    # Cleanup
    os.remove(config_path)
    print(f"\n6. Cleaned up configuration file: {config_path}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
