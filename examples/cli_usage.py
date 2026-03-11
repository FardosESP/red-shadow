#!/usr/bin/env python3
"""
CLI Usage Examples
Demonstrates how to use the CLI argument parser
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambani_integration.cli import parse_args, args_to_config
from ambani_integration.config import ConfigManager


def example_basic_usage():
    """Example 1: Basic usage with minimal arguments"""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)
    
    # Simulate command-line arguments
    test_args = ['/path/to/dump']
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Dump path: {args.dump_path}")
        print(f"✓ Ambani mode: {args.ambani_mode}")
        print(f"✓ Safe mode: {args.safe_mode}")
        print(f"✓ Auto-stop mode: {args.auto_stop_mode}")
        
        # Convert to config
        config = args_to_config(args)
        print(f"\n✓ Configuration generated:")
        print(f"  - Ambani enabled: {config['ambani']['enabled']}")
        print(f"  - Safe mode: {config['ambani']['safe_mode']}")
        print(f"  - ML enabled: {config['ml']['enabled']}")
    
    print()


def example_ambani_mode():
    """Example 2: Ambani mode with auto-stop"""
    print("=" * 80)
    print("Example 2: Ambani Mode with Auto-Stop")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--ambani-mode',
        '--auto-stop-mode', 'auto',
        '--auto-stop-threshold', '90',
        '--learning-mode'
    ]
    
    # Note: In real usage, this would show the legal disclaimer
    # For this example, we'll mock it
    import unittest.mock as mock
    with mock.patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True):
        args = parse_args(test_args)
    
    if args:
        print(f"✓ Ambani mode: {args.ambani_mode}")
        print(f"✓ Auto-stop mode: {args.auto_stop_mode}")
        print(f"✓ Auto-stop threshold: {args.auto_stop_threshold}")
        print(f"✓ Learning mode: {args.learning_mode}")
        
        config = args_to_config(args)
        print(f"\n✓ Auto-stop configuration:")
        print(f"  - Mode: {config['auto_stop']['mode']}")
        print(f"  - Threshold: {config['auto_stop']['critical_threshold']}")
        print(f"  - Learning: {config['auto_stop']['learning_mode']}")
    
    print()


def example_dry_run():
    """Example 3: Dry-run mode for testing"""
    print("=" * 80)
    print("Example 3: Dry-Run Mode")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--ambani-mode',
        '--dry-run',
        '--auto-stop-mode', 'auto'
    ]
    
    import unittest.mock as mock
    with mock.patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True):
        args = parse_args(test_args)
    
    if args:
        print(f"✓ Dry-run mode: {args.dry_run}")
        print(f"✓ Safe mode: {args.safe_mode}")
        
        config = args_to_config(args)
        print(f"\n✓ Dry-run configuration:")
        print(f"  - Dry run: {config['ambani']['dry_run']}")
        print(f"  - Safe mode: {config['ambani']['safe_mode']}")
        print("\n  ℹ Operations will be simulated without execution")
    
    print()


def example_custom_output():
    """Example 4: Custom output configuration"""
    print("=" * 80)
    print("Example 4: Custom Output Configuration")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--output', '/custom/output/dir',
        '--format', 'json', 'html', 'pdf',
        '--no-gui'
    ]
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Output directory: {args.output_dir}")
        print(f"✓ Report formats: {args.report_formats}")
        print(f"✓ GUI disabled: {args.no_gui}")
        
        config = args_to_config(args)
        print(f"\n✓ Output configuration:")
        print(f"  - Directory: {config['reporting']['output_dir']}")
        print(f"  - Formats: {', '.join(config['reporting']['formats'])}")
    
    print()


def example_skip_analysis():
    """Example 5: Skip specific analysis phases"""
    print("=" * 80)
    print("Example 5: Skip Analysis Phases")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--skip-ml',
        '--skip-network',
        '--skip-memory'
    ]
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Skip ML: {args.skip_ml}")
        print(f"✓ Skip network: {args.skip_network}")
        print(f"✓ Skip memory: {args.skip_memory}")
        print(f"✓ Skip bytecode: {args.skip_bytecode}")
        
        config = args_to_config(args)
        print(f"\n✓ Analysis configuration:")
        print(f"  - ML enabled: {config['ml']['enabled']}")
        print(f"  - Network enabled: {config['network_monitor']['enabled']}")
        print(f"  - Memory enabled: {config['memory_forensics']['enabled']}")
        print(f"  - Bytecode enabled: {config['bytecode_decompiler']['enabled']}")
    
    print()


def example_resource_management():
    """Example 6: Resource whitelist/blacklist"""
    print("=" * 80)
    print("Example 6: Resource Management")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--whitelist', 'my_critical_resource', 'another_resource',
        '--blacklist', 'suspicious_resource'
    ]
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Whitelist: {args.resource_whitelist}")
        print(f"✓ Blacklist: {args.resource_blacklist}")
        
        config = args_to_config(args)
        print(f"\n✓ Resource configuration:")
        if 'resource_whitelist_extra' in config:
            print(f"  - Extra whitelist: {config['resource_whitelist_extra']}")
        if 'resource_blacklist' in config:
            print(f"  - Blacklist: {config['resource_blacklist']}")
    
    print()


def example_logging_options():
    """Example 7: Logging configuration"""
    print("=" * 80)
    print("Example 7: Logging Configuration")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--verbose',
        '--log-file', '/custom/logs/analysis.log',
        '--no-color'
    ]
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Verbose: {args.verbose}")
        print(f"✓ Log file: {args.log_file}")
        print(f"✓ No color: {args.no_color}")
        
        config = args_to_config(args)
        print(f"\n✓ Logging configuration:")
        print(f"  - Level: {config['logging']['level']}")
        print(f"  - File: {config['logging']['file']}")
        print(f"  - Colored: {config['logging']['colored']}")
    
    print()


def example_integration_with_config_manager():
    """Example 8: Integration with ConfigManager"""
    print("=" * 80)
    print("Example 8: Integration with ConfigManager")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--config', 'config.json',
        '--verbose'
    ]
    
    args = parse_args(test_args)
    
    if args:
        print(f"✓ Config file: {args.config_file}")
        
        # Create config manager
        config_manager = ConfigManager(args.config_file)
        
        # Override with CLI arguments
        cli_config = args_to_config(args)
        
        print(f"\n✓ Merging CLI config with file config...")
        
        for key, value in cli_config.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config_key = f"{key}.{subkey}"
                    config_manager.set(config_key, subvalue)
                    print(f"  - Set {config_key} = {subvalue}")
            else:
                config_manager.set(key, value)
                print(f"  - Set {key} = {value}")
        
        # Validate
        try:
            config_manager.validate()
            print(f"\n✓ Configuration validated successfully")
        except ValueError as e:
            print(f"\n✗ Configuration validation failed: {e}")
    
    print()


def example_full_workflow():
    """Example 9: Complete workflow"""
    print("=" * 80)
    print("Example 9: Complete Workflow")
    print("=" * 80)
    
    test_args = [
        '/path/to/dump',
        '--ambani-mode',
        '--safe-mode',
        '--dry-run',
        '--auto-stop-mode', 'auto',
        '--auto-stop-threshold', '85',
        '--learning-mode',
        '--output', './output',
        '--format', 'json', 'html',
        '--whitelist', 'es_extended', 'qb-core',
        '--verbose',
        '--log-file', './logs/analysis.log'
    ]
    
    import unittest.mock as mock
    with mock.patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True):
        args = parse_args(test_args)
    
    if args:
        print("✓ Arguments parsed successfully")
        
        # Convert to config
        config = args_to_config(args)
        
        print(f"\n✓ Complete configuration:")
        print(f"  Ambani Mode:")
        print(f"    - Enabled: {config['ambani']['enabled']}")
        print(f"    - Safe mode: {config['ambani']['safe_mode']}")
        print(f"    - Dry run: {config['ambani']['dry_run']}")
        
        print(f"\n  Auto-Stop Engine:")
        print(f"    - Mode: {config['auto_stop']['mode']}")
        print(f"    - Threshold: {config['auto_stop']['critical_threshold']}")
        print(f"    - Learning: {config['auto_stop']['learning_mode']}")
        
        print(f"\n  Analysis:")
        print(f"    - ML: {config['ml']['enabled']}")
        print(f"    - Network: {config['network_monitor']['enabled']}")
        print(f"    - Memory: {config['memory_forensics']['enabled']}")
        print(f"    - Bytecode: {config['bytecode_decompiler']['enabled']}")
        
        print(f"\n  Output:")
        print(f"    - Directory: {config['reporting']['output_dir']}")
        print(f"    - Formats: {', '.join(config['reporting']['formats'])}")
        
        print(f"\n  Logging:")
        print(f"    - Level: {config['logging']['level']}")
        print(f"    - File: {config['logging']['file']}")
        
        if 'resource_whitelist_extra' in config:
            print(f"\n  Resources:")
            print(f"    - Whitelist: {', '.join(config['resource_whitelist_extra'])}")
        
        print(f"\n✓ Ready to start analysis!")
    
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CLI USAGE EXAMPLES" + " " * 40 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    examples = [
        example_basic_usage,
        example_ambani_mode,
        example_dry_run,
        example_custom_output,
        example_skip_analysis,
        example_resource_management,
        example_logging_options,
        example_integration_with_config_manager,
        example_full_workflow
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"✗ Example failed: {e}\n")
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
