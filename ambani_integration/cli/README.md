# CLI Module

Command-line interface for RED-SHADOW Ambani Integration.

## Overview

The CLI module provides a comprehensive argument parser for controlling all aspects of the Ambani Integration analysis system. It supports multiple operation modes, configuration options, and safety features.

## Features

- **Operation Modes**: Control analysis behavior with flags like `--ambani-mode`, `--safe-mode`, `--dry-run`
- **Auto-Stop Engine**: Configure automatic resource stopping with `--auto-stop-mode`
- **Analysis Control**: Skip specific analysis phases with `--skip-ml`, `--skip-network`, etc.
- **Output Configuration**: Control report formats and output directories
- **Resource Management**: Whitelist/blacklist resources for analysis
- **Logging**: Verbose, quiet, and custom log file options
- **Legal Compliance**: Automatic disclaimer for Ambani mode

## Usage

### Basic Usage

```python
from ambani_integration.cli import parse_args, args_to_config

# Parse command-line arguments
args = parse_args()

if args:
    # Convert to configuration dictionary
    config = args_to_config(args)
    
    # Use configuration in your application
    print(f"Ambani mode: {config['ambani']['enabled']}")
    print(f"Safe mode: {config['ambani']['safe_mode']}")
```

### Command-Line Examples

#### Standard Analysis
```bash
python main.py /path/to/dump
```

#### Ambani Mode with Safe Mode (Default)
```bash
python main.py /path/to/dump --ambani-mode
```

#### Dry-Run Mode (Simulate Operations)
```bash
python main.py /path/to/dump --ambani-mode --dry-run
```

#### Auto-Stop Engine
```bash
# Notify mode (alert but don't stop)
python main.py /path/to/dump --ambani-mode --auto-stop-mode notify

# Auto mode (automatically stop vulnerable resources)
python main.py /path/to/dump --ambani-mode --auto-stop-mode auto --auto-stop-threshold 90
```

#### Skip Specific Analysis Phases
```bash
python main.py /path/to/dump --ambani-mode --skip-ml --skip-network
```

#### Custom Output
```bash
python main.py /path/to/dump --ambani-mode --output /custom/output --format json html pdf
```

#### Verbose Logging
```bash
python main.py /path/to/dump --ambani-mode --verbose --log-file /custom/log.txt
```

#### Resource Management
```bash
python main.py /path/to/dump --ambani-mode --whitelist my_resource1 my_resource2
```

## Available Flags

### Operation Modes

- `--ambani-mode`: Enable Ambani-specific analysis (requires authorization)
- `--safe-mode`: Enable safe mode with automatic rollback (default: enabled)
- `--no-safe-mode`: Disable safe mode (NOT RECOMMENDED)
- `--dry-run`: Simulate operations without executing them

### Auto-Stop Engine

- `--auto-stop-mode {manual,notify,auto}`: Set auto-stop mode
  - `manual`: No automatic stopping (default)
  - `notify`: Notify but don't stop
  - `auto`: Automatically stop vulnerable resources
- `--auto-stop-threshold SCORE`: Risk score threshold (0-100, default: 85)
- `--learning-mode`: Enable learning mode for threshold adjustment

### Analysis Options

- `--skip-ml`: Skip machine learning analysis
- `--skip-network`: Skip network monitoring
- `--skip-memory`: Skip memory forensics
- `--skip-bytecode`: Skip bytecode decompilation

### Output Options

- `-o, --output DIR`: Output directory for reports
- `--format {json,html,pdf}`: Report output formats (default: json html)
- `--no-gui`: Disable GUI and run in headless mode
- `--cmd-gui`: Use terminal-based GUI

### Configuration

- `-c, --config FILE`: Path to configuration file
- `--create-config`: Create default configuration file and exit

### Resource Management

- `--whitelist RESOURCE [RESOURCE ...]`: Resources to never auto-stop
- `--blacklist RESOURCE [RESOURCE ...]`: Resources to always analyze

### Logging and Debugging

- `-v, --verbose`: Enable verbose output (DEBUG level)
- `-q, --quiet`: Suppress non-essential output
- `--log-file FILE`: Custom log file path
- `--no-color`: Disable colored output

## Legal Disclaimer

When `--ambani-mode` is enabled, the system displays a legal disclaimer that must be accepted before proceeding. This ensures users understand the legal implications of using penetration testing tools.

The disclaimer covers:
- Authorization requirements
- Legal responsibilities
- Criminal offense warnings
- Liability disclaimers

## API Reference

### `create_parser()`

Creates and configures the argument parser.

**Returns**: `argparse.ArgumentParser`

### `parse_args(argv=None)`

Parses command-line arguments with validation.

**Parameters**:
- `argv` (list, optional): Command-line arguments (defaults to sys.argv[1:])

**Returns**: `argparse.Namespace` or `None` if validation fails

### `validate_args(args)`

Validates parsed arguments.

**Parameters**:
- `args` (argparse.Namespace): Parsed arguments

**Returns**: `bool` - True if valid, False otherwise

### `args_to_config(args)`

Converts parsed arguments to configuration dictionary.

**Parameters**:
- `args` (argparse.Namespace): Parsed arguments

**Returns**: `dict` - Configuration dictionary

### `show_legal_disclaimer()`

Displays legal disclaimer and gets user confirmation.

**Returns**: `bool` - True if user accepts, False otherwise

## Integration with ConfigManager

The CLI module integrates seamlessly with the ConfigManager:

```python
from ambani_integration.cli import parse_args, args_to_config
from ambani_integration.config import ConfigManager

# Parse CLI arguments
args = parse_args()

if args:
    # Create config manager
    config_manager = ConfigManager(args.config_file)
    
    # Override with CLI arguments
    cli_config = args_to_config(args)
    for key, value in cli_config.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                config_manager.set(f"{key}.{subkey}", subvalue)
        else:
            config_manager.set(key, value)
    
    # Validate configuration
    config_manager.validate()
```

## Testing

The CLI module includes comprehensive unit tests:

```bash
# Run all CLI tests
python -m pytest tests/cli/test_parser.py -v

# Run specific test class
python -m pytest tests/cli/test_parser.py::TestParseArgs -v

# Run with coverage
python -m pytest tests/cli/test_parser.py --cov=ambani_integration.cli
```

## Error Handling

The parser includes validation for:
- Invalid threshold values (must be 0-100)
- Conflicting flags (e.g., --verbose and --quiet)
- Missing required arguments
- Invalid mode combinations

When validation fails, the parser:
1. Prints error messages
2. Shows help text
3. Returns `None` from `parse_args()`

## Best Practices

1. **Always use safe mode** unless you have a specific reason not to
2. **Test with dry-run first** before running destructive operations
3. **Start with notify mode** before enabling auto-stop
4. **Use verbose logging** when debugging issues
5. **Whitelist critical resources** to prevent accidental stops
6. **Obtain authorization** before using Ambani mode

## Examples

See `examples/cli_usage.py` for complete usage examples.
