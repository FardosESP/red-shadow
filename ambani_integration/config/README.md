# Configuration System

The configuration system provides flexible configuration management for the Ambani Integration project, supporting both JSON configuration files and environment variables.

## Features

- **JSON Configuration**: Load settings from `config.json` files
- **Environment Variables**: Override settings via environment variables for deployment flexibility
- **Default Values**: Comprehensive default configuration included
- **Validation**: Automatic validation of configuration values
- **Type Conversion**: Automatic type conversion for environment variables
- **Dot Notation**: Access nested configuration using dot notation (e.g., `ambani.enabled`)

## Quick Start

### Using JSON Configuration

```python
from ambani_integration.config import ConfigManager, Settings

# Load configuration from config.json
config_manager = ConfigManager()

# Access configuration values
enabled = config_manager.get('ambani.enabled')
mode = config_manager.get('auto_stop.mode')

# Use Settings wrapper for typed access
settings = Settings(config_manager.get_all())
print(f"Safe mode: {settings.safe_mode}")
print(f"Auto-stop mode: {settings.auto_stop_mode}")
```

### Using Environment Variables

```bash
# Set environment variables
export AMBANI_ENABLED=true
export AUTO_STOP_MODE=auto
export LOG_LEVEL=DEBUG

# Run your application
python main.py
```

Environment variables automatically override JSON configuration values.

## Configuration Structure

### Ambani Settings

```json
{
  "ambani": {
    "enabled": true,           // Enable/disable Ambani integration
    "api_path": "/path/to/ambani/api",  // Path to Ambani API
    "safe_mode": true,         // Enable safe mode (prevents destructive operations)
    "dry_run": false,          // Simulate operations without executing
    "rate_limit": 5            // Events per second
  }
}
```

### Auto-Stop Engine Settings

```json
{
  "auto_stop": {
    "mode": "notify",                    // manual, notify, or auto
    "critical_threshold": 85,            // Risk score threshold (0-100)
    "confidence_threshold_high": 0.80,   // High confidence threshold
    "confidence_threshold_low": 0.60,    // Low confidence threshold
    "grace_period": 300,                 // Grace period in seconds
    "max_stops_per_minute": 3,           // Rate limiting
    "learning_mode": true                // Enable learning from feedback
  }
}
```

### Machine Learning Settings

```json
{
  "ml": {
    "enabled": true,
    "models": ["isolation_forest", "one_class_svm", "autoencoder"],
    "contamination": 0.1,
    "training_data_path": "./data/training"
  }
}
```

### Network Monitor Settings

```json
{
  "network_monitor": {
    "enabled": true,
    "interface": "eth0",
    "capture_filter": "port 30120",
    "sampling_mode": false,
    "sampling_rate": 10
  }
}
```

### Memory Forensics Settings

```json
{
  "memory_forensics": {
    "enabled": true,
    "snapshot_interval": 60,
    "yara_rules_path": "./rules/yara"
  }
}
```

### Resource Whitelist

```json
{
  "resource_whitelist": [
    "es_extended",
    "qb-core",
    "oxmysql",
    "txAdmin"
  ]
}
```

### Reporting Settings

```json
{
  "reporting": {
    "formats": ["json", "html"],
    "output_dir": "./reports",
    "include_poc": true,
    "webhook_url": null
  }
}
```

### Logging Settings

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

### Database Settings

```json
{
  "database": {
    "path": "./data/ambani_integration.db",
    "connection_string": null,
    "pool_size": 5,
    "timeout": 30
  }
}
```

### API Endpoints

```json
{
  "api_endpoints": {
    "vulnerability_db": "https://api.ambani-integration.dev/vulnerabilities",
    "signature_updates": "https://api.ambani-integration.dev/signatures",
    "telemetry": null
  }
}
```

### Thresholds

```json
{
  "thresholds": {
    "risk_score": {
      "critical": 70,
      "high": 50,
      "medium": 30,
      "low": 0
    },
    "anomaly_score": {
      "high": 0.8,
      "medium": 0.5,
      "low": 0.3
    },
    "honeypot_confidence": 0.7
  }
}
```

## Environment Variable Mappings

| Environment Variable | Configuration Key | Type | Example |
|---------------------|-------------------|------|---------|
| `AMBANI_ENABLED` | `ambani.enabled` | bool | `true` |
| `AMBANI_API_PATH` | `ambani.api_path` | string | `/path/to/api` |
| `AMBANI_SAFE_MODE` | `ambani.safe_mode` | bool | `true` |
| `AMBANI_RATE_LIMIT` | `ambani.rate_limit` | int | `5` |
| `AMBANI_DRY_RUN` | `ambani.dry_run` | bool | `false` |
| `AUTO_STOP_MODE` | `auto_stop.mode` | string | `notify` |
| `AUTO_STOP_THRESHOLD` | `auto_stop.critical_threshold` | int | `85` |
| `AUTO_STOP_LEARNING` | `auto_stop.learning_mode` | bool | `true` |
| `ML_ENABLED` | `ml.enabled` | bool | `true` |
| `ML_TRAINING_PATH` | `ml.training_data_path` | string | `./data/training` |
| `NETWORK_MONITOR_ENABLED` | `network_monitor.enabled` | bool | `true` |
| `NETWORK_INTERFACE` | `network_monitor.interface` | string | `eth0` |
| `MEMORY_FORENSICS_ENABLED` | `memory_forensics.enabled` | bool | `true` |
| `REPORT_OUTPUT_DIR` | `reporting.output_dir` | string | `./reports` |
| `REPORT_WEBHOOK_URL` | `reporting.webhook_url` | string | `https://...` |
| `LOG_LEVEL` | `logging.level` | string | `INFO` |
| `LOG_FILE` | `logging.file` | string | `./logs/app.log` |
| `DATABASE_PATH` | `database.path` | string | `./data/db.sqlite` |
| `DATABASE_CONNECTION_STRING` | `database.connection_string` | string | `postgresql://...` |

## Usage Examples

### Example 1: Production Deployment

```bash
# Set production environment variables
export AMBANI_SAFE_MODE=true
export AUTO_STOP_MODE=auto
export LOG_LEVEL=WARNING
export REPORT_WEBHOOK_URL=https://your-webhook-url
export DATABASE_CONNECTION_STRING=postgresql://user:pass@localhost/dbname

# Run application
python main.py --ambani-mode
```

### Example 2: Development Environment

```bash
# Set development environment variables
export AMBANI_DRY_RUN=true
export AUTO_STOP_MODE=manual
export LOG_LEVEL=DEBUG

# Run application
python main.py --ambani-mode
```

### Example 3: High-Security Environment

```bash
# Set high-security environment variables
export AMBANI_SAFE_MODE=true
export AUTO_STOP_MODE=notify
export AUTO_STOP_THRESHOLD=70
export ML_ENABLED=true
export NETWORK_MONITOR_ENABLED=true
export MEMORY_FORENSICS_ENABLED=true

# Run application
python main.py --ambani-mode
```

### Example 4: Programmatic Configuration

```python
from ambani_integration.config import ConfigManager, Settings

# Create config manager
config = ConfigManager('custom_config.json')

# Modify configuration
config.set('ambani.enabled', True)
config.set('auto_stop.mode', 'auto')
config.set('logging.level', 'DEBUG')

# Validate configuration
try:
    config.validate()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")

# Save configuration
config.save_config()

# Use settings wrapper
settings = Settings(config.get_all())
print(f"Auto-stop mode: {settings.auto_stop_mode}")
print(f"Critical threshold: {settings.critical_threshold}")
```

## Configuration Validation

The configuration system automatically validates:

- **Required keys**: Ensures all required configuration keys are present
- **Type checking**: Validates that values are of the correct type
- **Value ranges**: Ensures numeric values are within valid ranges
- **Enum validation**: Validates that string values match allowed options
- **Logical consistency**: Ensures related values are logically consistent

Example validation errors:

```python
# Invalid auto_stop mode
config.set('auto_stop.mode', 'invalid')
config.validate()  # Raises ValueError

# Invalid threshold range
config.set('auto_stop.critical_threshold', 150)
config.validate()  # Raises ValueError

# Inconsistent confidence thresholds
config.set('auto_stop.confidence_threshold_low', 0.9)
config.set('auto_stop.confidence_threshold_high', 0.8)
config.validate()  # Raises ValueError
```

## Creating Default Configuration

```python
from ambani_integration.config import ConfigManager

# Create a new config manager
config = ConfigManager()

# Create default config.json file
config.create_default_config('./config.json')
```

## Best Practices

1. **Use environment variables for deployment**: Keep sensitive information and deployment-specific settings in environment variables
2. **Use JSON for defaults**: Store default configuration in `config.json`
3. **Validate early**: Call `validate()` at application startup to catch configuration errors early
4. **Use Settings wrapper**: Use the `Settings` class for typed access to configuration values
5. **Document custom settings**: If you add custom configuration, document it in this README

## Testing

Run configuration tests:

```bash
pytest tests/config/test_config_manager.py -v
```

## See Also

- `.env.example`: Example environment variables file
- `config.json`: Default configuration file
- `tests/config/test_config_manager.py`: Configuration tests
