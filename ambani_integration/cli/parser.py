"""
CLI Argument Parser
Handles command-line arguments for different operation modes
"""

import argparse
import sys
from typing import Optional


# Legal disclaimer text
LEGAL_DISCLAIMER = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          ⚠️  LEGAL DISCLAIMER ⚠️                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  RED-SHADOW Ambani Integration is a SECURITY RESEARCH TOOL designed for   ║
║  authorized penetration testing and vulnerability assessment.             ║
║                                                                            ║
║  ⚠️  WARNING: Unauthorized use of this tool may be ILLEGAL                 ║
║                                                                            ║
║  By using --ambani-mode, you acknowledge that:                            ║
║                                                                            ║
║  1. You have EXPLICIT WRITTEN AUTHORIZATION from the server owner         ║
║  2. You will use this tool ONLY for legitimate security testing           ║
║  3. You understand that unauthorized access is a CRIMINAL OFFENSE         ║
║  4. You accept FULL RESPONSIBILITY for your actions                       ║
║  5. The developers are NOT LIABLE for misuse of this tool                 ║
║                                                                            ║
║  Unauthorized access to computer systems is prohibited by:                ║
║  - Computer Fraud and Abuse Act (CFAA) - USA                              ║
║  - Computer Misuse Act - UK                                               ║
║  - EU Cybercrime Directive                                                ║
║  - And similar laws in most jurisdictions worldwide                       ║
║                                                                            ║
║  USE AT YOUR OWN RISK. ALWAYS OBTAIN PROPER AUTHORIZATION.                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Do you have explicit authorization to test this server? (yes/no): """


def show_legal_disclaimer() -> bool:
    """
    Display legal disclaimer and get user confirmation
    
    Returns:
        True if user accepts, False otherwise
    """
    try:
        response = input(LEGAL_DISCLAIMER).strip().lower()
        if response in ('yes', 'y'):
            print("\n✓ Authorization confirmed. Proceeding with Ambani mode...\n")
            return True
        else:
            print("\n✗ Authorization not confirmed. Exiting.\n")
            return False
    except (EOFError, KeyboardInterrupt):
        print("\n\n✗ Interrupted. Exiting.\n")
        return False


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='red-shadow-ambani',
        description='RED-SHADOW v4.0 with Ambani Integration - Advanced FiveM Security Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard analysis without Ambani features
  python main.py /path/to/dump
  
  # Enable Ambani mode with safe mode (default)
  python main.py /path/to/dump --ambani-mode
  
  # Ambani mode with dry-run (simulate operations)
  python main.py /path/to/dump --ambani-mode --dry-run
  
  # Ambani mode with auto-stop engine
  python main.py /path/to/dump --ambani-mode --auto-stop-mode auto
  
  # Disable safe mode (NOT RECOMMENDED)
  python main.py /path/to/dump --ambani-mode --no-safe-mode
  
  # Full analysis with all features
  python main.py /path/to/dump --ambani-mode --auto-stop-mode auto --verbose

For more information, visit: https://github.com/FardosESP/red-shadow
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'dump_path',
        nargs='?',
        help='Path to FiveM server dump directory'
    )
    
    # Core mode flags
    mode_group = parser.add_argument_group('Operation Modes')
    
    mode_group.add_argument(
        '--ambani-mode',
        action='store_true',
        dest='ambani_mode',
        help='Enable Ambani-specific analysis and exploitation testing (requires authorization)'
    )
    
    mode_group.add_argument(
        '--safe-mode',
        action='store_true',
        dest='safe_mode',
        default=True,
        help='Enable safe mode with automatic rollback (default: enabled)'
    )
    
    mode_group.add_argument(
        '--no-safe-mode',
        action='store_false',
        dest='safe_mode',
        help='Disable safe mode (NOT RECOMMENDED - operations cannot be rolled back)'
    )
    
    mode_group.add_argument(
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Simulate operations without executing them (useful for testing)'
    )
    
    # Auto-stop engine configuration
    autostop_group = parser.add_argument_group('Auto-Stop Engine')
    
    autostop_group.add_argument(
        '--auto-stop-mode',
        choices=['manual', 'notify', 'auto'],
        dest='auto_stop_mode',
        default='manual',
        help='''Auto-stop mode for vulnerable resources:
                manual = no automatic stopping (default),
                notify = notify but don't stop,
                auto = automatically stop vulnerable resources'''
    )
    
    autostop_group.add_argument(
        '--auto-stop-threshold',
        type=int,
        dest='auto_stop_threshold',
        default=85,
        metavar='SCORE',
        help='Risk score threshold for auto-stop (0-100, default: 85)'
    )
    
    autostop_group.add_argument(
        '--learning-mode',
        action='store_true',
        dest='learning_mode',
        help='Enable learning mode to adjust thresholds based on admin feedback'
    )
    
    # Analysis configuration
    analysis_group = parser.add_argument_group('Analysis Options')
    
    analysis_group.add_argument(
        '--skip-ml',
        action='store_true',
        dest='skip_ml',
        help='Skip machine learning analysis (faster but less accurate)'
    )
    
    analysis_group.add_argument(
        '--skip-network',
        action='store_true',
        dest='skip_network',
        help='Skip network monitoring and packet analysis'
    )
    
    analysis_group.add_argument(
        '--skip-memory',
        action='store_true',
        dest='skip_memory',
        help='Skip memory forensics analysis'
    )
    
    analysis_group.add_argument(
        '--skip-bytecode',
        action='store_true',
        dest='skip_bytecode',
        help='Skip bytecode decompilation'
    )
    
    # Output configuration
    output_group = parser.add_argument_group('Output Options')
    
    output_group.add_argument(
        '-o', '--output',
        dest='output_dir',
        metavar='DIR',
        help='Output directory for reports (default: ./output)'
    )
    
    output_group.add_argument(
        '--format',
        dest='report_formats',
        nargs='+',
        choices=['json', 'html', 'pdf'],
        default=['json', 'html'],
        help='Report output formats (default: json html)'
    )
    
    output_group.add_argument(
        '--no-gui',
        action='store_true',
        dest='no_gui',
        help='Disable GUI and run in headless mode'
    )
    
    output_group.add_argument(
        '--cmd-gui',
        action='store_true',
        dest='cmd_gui',
        help='Use terminal-based GUI instead of web dashboard'
    )
    
    # Configuration
    config_group = parser.add_argument_group('Configuration')
    
    config_group.add_argument(
        '-c', '--config',
        dest='config_file',
        metavar='FILE',
        help='Path to configuration file (default: config.json)'
    )
    
    config_group.add_argument(
        '--create-config',
        action='store_true',
        dest='create_config',
        help='Create default configuration file and exit'
    )
    
    # Resource management
    resource_group = parser.add_argument_group('Resource Management')
    
    resource_group.add_argument(
        '--whitelist',
        dest='resource_whitelist',
        nargs='+',
        metavar='RESOURCE',
        help='Additional resources to whitelist (never auto-stop)'
    )
    
    resource_group.add_argument(
        '--blacklist',
        dest='resource_blacklist',
        nargs='+',
        metavar='RESOURCE',
        help='Resources to always analyze (override whitelist)'
    )
    
    # Logging and debugging
    debug_group = parser.add_argument_group('Logging and Debugging')
    
    debug_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Enable verbose output (DEBUG level logging)'
    )
    
    debug_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        dest='quiet',
        help='Suppress non-essential output'
    )
    
    debug_group.add_argument(
        '--log-file',
        dest='log_file',
        metavar='FILE',
        help='Log file path (default: logs/ambani_integration.log)'
    )
    
    debug_group.add_argument(
        '--no-color',
        action='store_true',
        dest='no_color',
        help='Disable colored output'
    )
    
    # Version and help
    parser.add_argument(
        '--version',
        action='version',
        version='RED-SHADOW v4.0 with Ambani Integration'
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> bool:
    """
    Validate parsed arguments
    
    Args:
        args: Parsed arguments namespace
        
    Returns:
        True if valid, False otherwise
    """
    errors = []
    
    # Validate auto-stop threshold
    if args.auto_stop_threshold < 0 or args.auto_stop_threshold > 100:
        errors.append(f"Auto-stop threshold must be between 0 and 100, got: {args.auto_stop_threshold}")
    
    # Validate mode combinations
    if args.dry_run and not args.ambani_mode:
        print("Warning: --dry-run is only meaningful with --ambani-mode")
    
    if args.auto_stop_mode != 'manual' and not args.ambani_mode:
        print("Warning: --auto-stop-mode is only meaningful with --ambani-mode")
    
    if args.learning_mode and args.auto_stop_mode == 'manual':
        print("Warning: --learning-mode is only meaningful with --auto-stop-mode notify or auto")
    
    # Validate conflicting options
    if args.verbose and args.quiet:
        errors.append("Cannot use --verbose and --quiet together")
    
    if args.no_gui and args.cmd_gui:
        errors.append("Cannot use --no-gui and --cmd-gui together")
    
    # Validate dump path (unless creating config)
    if not args.create_config and not args.dump_path:
        errors.append("Dump path is required (unless using --create-config)")
    
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"  ✗ {error}")
        print()
        return False
    
    return True


def parse_args(argv: Optional[list] = None) -> Optional[argparse.Namespace]:
    """
    Parse command-line arguments with validation
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments namespace, or None if validation fails
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Show legal disclaimer if Ambani mode is enabled
    if args.ambani_mode:
        if not show_legal_disclaimer():
            sys.exit(1)
    
    # Validate arguments
    if not validate_args(args):
        parser.print_help()
        return None
    
    return args


def args_to_config(args: argparse.Namespace) -> dict:
    """
    Convert parsed arguments to configuration dictionary
    
    Args:
        args: Parsed arguments namespace
        
    Returns:
        Configuration dictionary
    """
    config = {
        'ambani': {
            'enabled': args.ambani_mode,
            'safe_mode': args.safe_mode,
            'dry_run': args.dry_run,
        },
        'auto_stop': {
            'mode': args.auto_stop_mode,
            'critical_threshold': args.auto_stop_threshold,
            'learning_mode': args.learning_mode,
        },
        'ml': {
            'enabled': not args.skip_ml,
        },
        'network_monitor': {
            'enabled': not args.skip_network,
        },
        'memory_forensics': {
            'enabled': not args.skip_memory,
        },
        'bytecode_decompiler': {
            'enabled': not args.skip_bytecode,
        },
        'reporting': {
            'output_dir': args.output_dir or './output',
            'formats': args.report_formats,
        },
        'logging': {
            'level': 'DEBUG' if args.verbose else ('ERROR' if args.quiet else 'INFO'),
            'file': args.log_file or 'logs/ambani_integration.log',
            'colored': not args.no_color,
        },
    }
    
    # Add resource whitelist/blacklist if provided
    if args.resource_whitelist:
        config['resource_whitelist_extra'] = args.resource_whitelist
    
    if args.resource_blacklist:
        config['resource_blacklist'] = args.resource_blacklist
    
    return config
