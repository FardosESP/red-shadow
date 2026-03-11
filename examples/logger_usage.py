"""
Example usage of the logging system
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ambani_integration.config.config_manager import ConfigManager
from ambani_integration.utils.logger import configure_logging, get_logger


def main():
    """Demonstrate logging system usage"""
    
    print("=" * 60)
    print("Logging System Example")
    print("=" * 60)
    
    # Example 1: Basic logging without configuration
    print("\n1. Basic logging (default configuration):")
    logger1 = get_logger("module1")
    logger1.debug("This is a DEBUG message (won't show with default INFO level)")
    logger1.info("This is an INFO message")
    logger1.warning("This is a WARNING message")
    logger1.error("This is an ERROR message")
    logger1.critical("This is a CRITICAL message")
    
    # Example 2: Configure logging from ConfigManager
    print("\n2. Configured logging (DEBUG level, file output):")
    config_manager = ConfigManager()
    config_manager.set("logging.level", "DEBUG")
    config_manager.set("logging.file", "./logs/example.log")
    config_manager.set("logging.console", True)
    
    configure_logging(config_manager)
    
    logger2 = get_logger("module2")
    logger2.debug("This DEBUG message will now show")
    logger2.info("This INFO message will show")
    logger2.warning("This WARNING message will show")
    
    print(f"\nLogs are also written to: {config_manager.get('logging.file')}")
    
    # Example 3: Multiple loggers for different modules
    print("\n3. Multiple loggers for different modules:")
    trigger_logger = get_logger("ambani_integration.analysis.trigger_analyzer")
    trigger_logger.info("Analyzing triggers...")
    trigger_logger.warning("Found suspicious trigger without validation")
    
    resource_logger = get_logger("ambani_integration.execution.resource_controller")
    resource_logger.info("Stopping resource: vulnerable_shop")
    resource_logger.error("Failed to stop resource: permission denied")
    
    # Example 4: Custom log level for specific logger
    print("\n4. Custom log level for specific logger:")
    error_only_logger = get_logger("error_module", level="ERROR")
    error_only_logger.debug("This won't show")
    error_only_logger.info("This won't show")
    error_only_logger.warning("This won't show")
    error_only_logger.error("This ERROR will show")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
