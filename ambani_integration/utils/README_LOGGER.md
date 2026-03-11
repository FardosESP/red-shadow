# Logging System

Comprehensive logging system with multiple levels and configuration integration.

## Features

- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Dual Output**: Log to both console and file (configurable)
- **Configuration Integration**: Seamlessly integrates with ConfigManager
- **Structured Logging**: Timestamps, module names, and log levels
- **Module-Specific Loggers**: Different loggers for different modules
- **Singleton Pattern**: Centralized logging management
- **Dynamic Reconfiguration**: Update logging settings at runtime

## Quick Start

### Basic Usage

```python
from ambani_integration.utils.logger import get_logger

# Get a logger for your module
logger = get_logger("my_module")

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error message")
```

### With Configuration

```python
from ambani_integration.config.config_manager import ConfigManager
from ambani_integration.utils.logger import configure_logging, get_logger

# Load configuration
config_manager = ConfigManager("config.json")

# Configure logging system
configure_logging(config_manager)

# Use logger
logger = get_logger("my_module")
logger.info("Logging configured from config file")
```

## Configuration

The logging system reads configuration from ConfigManager:

```json
{
  "logging": {
    "level": "INFO",
    "file": "./logs/ambani_integration.log",
    "console": true,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Configuration Options

- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **file**: Path to log file (creates directory if needed)
- **console**: Enable/disable console output (true/false)
- **format**: Log message format string

### Environment Variables

You can also configure logging via environment variables:

```bash
export LOG_LEVEL=DEBUG
export LOG_FILE=./logs/app.log
```

## Advanced Usage

### Module-Specific Loggers

```python
# Create loggers for different modules
trigger_logger = get_logger("ambani_integration.analysis.trigger_analyzer")
resource_logger = get_logger("ambani_integration.execution.resource_controller")
ml_logger = get_logger("ambani_integration.ml.behavioral_analyzer")

# Each logger can have its own level
error_only_logger = get_logger("critical_module", level="ERROR")
```

### Dynamic Level Changes

```python
from ambani_integration.utils.logger import set_log_level

# Change level for all loggers
set_log_level("DEBUG")

# Change level for specific logger
set_log_level("ERROR", "my_module")
```

### Additional File Handlers

```python
from ambani_integration.utils.logger import add_file_handler

# Add additional log file for specific logger
add_file_handler("./logs/errors.log", "my_module")

# Add file handler to all loggers
add_file_handler("./logs/all.log")
```

### Shutdown

```python
from ambani_integration.utils.logger import shutdown_logging

# Properly close all handlers and cleanup
shutdown_logging()
```

## Log Levels

| Level    | Numeric Value | When to Use |
|----------|---------------|-------------|
| DEBUG    | 10            | Detailed diagnostic information |
| INFO     | 20            | General informational messages |
| WARNING  | 30            | Warning messages for potentially harmful situations |
| ERROR    | 40            | Error messages for serious problems |
| CRITICAL | 50            | Critical errors that may cause program failure |

## Log Format

Default format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

Example output:
```
2026-03-11 19:45:13,092 - ambani_integration.main - INFO - Configuration loaded successfully
2026-03-11 19:45:13,093 - ambani_integration.main - WARNING - Safe mode is enabled
2026-03-11 19:45:13,094 - ambani_integration.analysis.trigger_analyzer - ERROR - Critical vulnerability detected
```

### Custom Format

You can customize the format in configuration:

```json
{
  "logging": {
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  }
}
```

Available format variables:
- `%(asctime)s`: Timestamp
- `%(name)s`: Logger name
- `%(levelname)s`: Log level (DEBUG, INFO, etc.)
- `%(message)s`: Log message
- `%(filename)s`: Source filename
- `%(lineno)d`: Line number
- `%(funcName)s`: Function name
- `%(process)d`: Process ID
- `%(thread)d`: Thread ID

## Best Practices

### 1. Use Module-Specific Loggers

```python
# Good: Use module name
logger = get_logger(__name__)

# Better: Use full module path
logger = get_logger("ambani_integration.analysis.trigger_analyzer")
```

### 2. Choose Appropriate Log Levels

```python
# DEBUG: Detailed diagnostic info
logger.debug(f"Processing trigger: {trigger_name}")

# INFO: General progress
logger.info("Analysis completed successfully")

# WARNING: Potentially harmful situations
logger.warning(f"Resource {name} has high risk score: {score}")

# ERROR: Serious problems
logger.error(f"Failed to stop resource: {error}")

# CRITICAL: Program may fail
logger.critical("Database connection lost")
```

### 3. Include Context in Messages

```python
# Good: Include relevant context
logger.error(f"Failed to stop resource '{resource_name}': {error}")

# Bad: Vague message
logger.error("Operation failed")
```

### 4. Use Lazy Formatting

```python
# Good: Lazy evaluation (only formats if logged)
logger.debug("Processing %s with %d items", name, count)

# Also good: f-strings (Python 3.6+)
logger.debug(f"Processing {name} with {count} items")
```

### 5. Configure Early

```python
# Configure logging at application startup
def main():
    config_manager = ConfigManager()
    configure_logging(config_manager)
    
    # Now use loggers throughout the application
    logger = get_logger(__name__)
    logger.info("Application started")
```

## Integration with Other Components

### With ConfigManager

```python
from ambani_integration.config.config_manager import ConfigManager
from ambani_integration.utils.logger import configure_logging, get_logger

config = ConfigManager("config.json")
configure_logging(config)

logger = get_logger(__name__)
logger.info(f"Ambani mode: {config.get('ambani.enabled')}")
```

### With Auto Stop Engine

```python
from ambani_integration.utils.logger import get_logger

class AutoStopEngine:
    def __init__(self):
        self.logger = get_logger("ambani_integration.execution.auto_stop_engine")
    
    def evaluate_resource(self, resource):
        self.logger.info(f"Evaluating resource: {resource.name}")
        self.logger.debug(f"Risk score: {resource.risk_score}")
        
        if resource.risk_score >= 85:
            self.logger.warning(f"High risk resource detected: {resource.name}")
```

### With Trigger Analyzer

```python
from ambani_integration.utils.logger import get_logger

class TriggerAnalyzer:
    def __init__(self):
        self.logger = get_logger("ambani_integration.analysis.trigger_analyzer")
    
    def analyze_trigger(self, trigger):
        self.logger.debug(f"Analyzing trigger: {trigger.name}")
        
        if not trigger.has_validation:
            self.logger.warning(f"Trigger without validation: {trigger.name}")
```

## Troubleshooting

### Logs Not Appearing

1. Check log level configuration
2. Verify console output is enabled
3. Ensure logger is configured before use

```python
# Configure before using
configure_logging(config_manager)
logger = get_logger(__name__)  # Now it will work
```

### File Permission Errors

Ensure the log directory exists and is writable:

```python
import os
from pathlib import Path

log_file = "./logs/app.log"
Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)
```

### Duplicate Log Messages

This can happen if loggers propagate to root logger. The system prevents this by default:

```python
logger.propagate = False  # Already set by LoggerManager
```

## Examples

See the `examples/` directory for complete examples:

- `examples/logger_usage.py`: Basic logging examples
- `examples/logger_with_config.py`: Configuration integration example

## API Reference

### Functions

#### `configure_logging(config_manager=None)`
Configure the logging system from ConfigManager.

#### `get_logger(name, level=None)`
Get or create a logger for a specific module.

**Parameters:**
- `name` (str): Logger name (typically module name)
- `level` (str, optional): Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Returns:** `logging.Logger`

#### `set_log_level(level, logger_name=None)`
Set log level for all loggers or a specific logger.

**Parameters:**
- `level` (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger_name` (str, optional): Logger name (if None, applies to all)

#### `add_file_handler(log_file, logger_name=None)`
Add an additional file handler to logger(s).

**Parameters:**
- `log_file` (str): Path to log file
- `logger_name` (str, optional): Logger name (if None, applies to all)

#### `shutdown_logging()`
Shutdown all loggers and close handlers.

### LoggerManager Class

Singleton class that manages all loggers.

**Methods:**
- `configure(config_manager)`: Configure from ConfigManager
- `get_logger(name, level)`: Get or create logger
- `set_level(level, logger_name)`: Set log level
- `add_file_handler(log_file, logger_name)`: Add file handler
- `shutdown()`: Shutdown all loggers

## Legacy Compatibility

The system maintains backward compatibility with the old `setup_logger` function:

```python
from ambani_integration.utils.logger import setup_logger
import logging

logger = setup_logger("my_module", logging.DEBUG, "./logs/app.log")
```

However, it's recommended to use the new API for better features and configuration integration.
