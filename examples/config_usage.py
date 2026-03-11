"""
Configuration System Usage Examples

This script demonstrates how to use the configuration system
in the Ambani Integration project.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ambani_integration.config import ConfigManager, Settings


def example_1_basic_usage():
    """Example 1: Basic configuration usage"""
    print("=" * 60)
    print("Example 1: Basic Configuration Usage")
    print("=" * 60)
    
    # Create config manager (loads from config.json if exists)
    config = ConfigManager()
    
    # Access configuration values using dot notation
    print(f"Ambani enabled: {config.get('ambani.enabled')}")
    print(f"Safe mode: {config.get('ambani.safe_mode')}")
    print(f"Auto-stop mode: {config.get('auto_stop.mode')}")
    print(f"Critical threshold: {config.get('auto_stop.critical_threshold')}")
    print()


def example_2_settings_wrapper():
    """Example 2: Using Settings wrapper for typed access"""
    print("=" * 60)
    print("Example 2: Using Settings Wrapper")
    print("=" * 60)
    
    config = ConfigManager()
    settings = Settings(config.get_all())
    
    # Access settings using properties
    print(f"Ambani enabled: {settings.ambani_enabled}")
    print(f"Safe mode: {settings.safe_mode}")
    print(f"Dry run: {settings.dry_run}")
    print(f"Rate limit: {settings.rate_limit}")
    print(f"Auto-stop mode: {settings.auto_stop_mode}")
    print(f"ML enabled: {settings.ml_enabled}")
    print(f"ML models: {settings.ml_models}")
    print(f"Network monitor enabled: {settings.network_monitor_enabled}")
    print(f"Memory forensics enabled: {settings.memory_forensics_enabled}")
    print()


def example_3_environment_variables():
    """Example 3: Environment variable override"""
    print("=" * 60)
    print("Example 3: Environment Variable Override")
    print("=" * 60)
    
    # Set environment variables
    os.environ['AMBANI_ENABLED'] = 'false'
    os.environ['AUTO_STOP_MODE'] = 'auto'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Create config manager (will load env vars)
    config = ConfigManager()
    
    print(f"Ambani enabled (from env): {config.get('ambani.enabled')}")
    print(f"Auto-stop mode (from env): {config.get('auto_stop.mode')}")
    print(f"Log level (from env): {config.get('logging.level')}")
    
    # Clean up
    del os.environ['AMBANI_ENABLED']
    del os.environ['AUTO_STOP_MODE']
    del os.environ['LOG_LEVEL']
    print()


def example_4_modify_and_save():
    """Example 4: Modify and save configuration"""
    print("=" * 60)
    print("Example 4: Modify and Save Configuration")
    print("=" * 60)
    
    config = ConfigManager()
    
    # Modify configuration
    print("Modifying configuration...")
    config.set('ambani.enabled', True)
    config.set('auto_stop.mode', 'notify')
    config.set('logging.level', 'INFO')
    
    print(f"New ambani.enabled: {config.get('ambani.enabled')}")
    print(f"New auto_stop.mode: {config.get('auto_stop.mode')}")
    print(f"New logging.level: {config.get('logging.level')}")
    
    # Note: Uncomment to actually save
    # config.save_config()
    # print("Configuration saved to config.json")
    print()


def example_5_validation():
    """Example 5: Configuration validation"""
    print("=" * 60)
    print("Example 5: Configuration Validation")
    print("=" * 60)
    
    config = ConfigManager()
    
    # Validate current configuration
    try:
        config.validate()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")
    
    # Try invalid configuration
    print("\nTesting invalid configuration...")
    config.set('auto_stop.mode', 'invalid_mode')
    
    try:
        config.validate()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration validation failed (expected):")
        print(f"  {e}")
    
    # Restore valid configuration
    config.set('auto_stop.mode', 'notify')
    print()


def example_6_thresholds():
    """Example 6: Working with thresholds"""
    print("=" * 60)
    print("Example 6: Working with Thresholds")
    print("=" * 60)
    
    config = ConfigManager()
    settings = Settings(config.get_all())
    
    # Access risk thresholds
    risk_thresholds = settings.risk_thresholds
    print("Risk Score Thresholds:")
    print(f"  Critical: {risk_thresholds['critical']}")
    print(f"  High: {risk_thresholds['high']}")
    print(f"  Medium: {risk_thresholds['medium']}")
    print(f"  Low: {risk_thresholds['low']}")
    
    # Access anomaly thresholds
    anomaly_thresholds = settings.anomaly_thresholds
    print("\nAnomaly Score Thresholds:")
    print(f"  High: {anomaly_thresholds['high']}")
    print(f"  Medium: {anomaly_thresholds['medium']}")
    print(f"  Low: {anomaly_thresholds['low']}")
    
    # Honeypot confidence threshold
    print(f"\nHoneypot Confidence Threshold: {settings.honeypot_confidence_threshold}")
    print()


def example_7_resource_whitelist():
    """Example 7: Working with resource whitelist"""
    print("=" * 60)
    print("Example 7: Resource Whitelist")
    print("=" * 60)
    
    config = ConfigManager()
    settings = Settings(config.get_all())
    
    whitelist = settings.resource_whitelist
    print(f"Resource Whitelist ({len(whitelist)} resources):")
    for resource in whitelist:
        print(f"  - {resource}")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AMBANI INTEGRATION CONFIG EXAMPLES" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        example_1_basic_usage()
        example_2_settings_wrapper()
        example_3_environment_variables()
        example_4_modify_and_save()
        example_5_validation()
        example_6_thresholds()
        example_7_resource_whitelist()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
