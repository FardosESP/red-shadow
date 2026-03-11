"""
Configuration Manager
Handles loading and managing application configuration
"""

import json
import os
from typing import Dict, Any, Optional
from .settings import DEFAULT_CONFIG


class ConfigManager:
    """
    Configuration management
    
    Responsibilities:
    - Load configuration from JSON files
    - Merge with environment variables
    - Provide configuration access
    - Validate configuration
    """
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        'AMBANI_ENABLED': 'ambani.enabled',
        'AMBANI_API_PATH': 'ambani.api_path',
        'AMBANI_SAFE_MODE': 'ambani.safe_mode',
        'AMBANI_RATE_LIMIT': 'ambani.rate_limit',
        'AMBANI_DRY_RUN': 'ambani.dry_run',
        'AUTO_STOP_MODE': 'auto_stop.mode',
        'AUTO_STOP_THRESHOLD': 'auto_stop.critical_threshold',
        'AUTO_STOP_LEARNING': 'auto_stop.learning_mode',
        'ML_ENABLED': 'ml.enabled',
        'ML_TRAINING_PATH': 'ml.training_data_path',
        'NETWORK_MONITOR_ENABLED': 'network_monitor.enabled',
        'NETWORK_INTERFACE': 'network_monitor.interface',
        'MEMORY_FORENSICS_ENABLED': 'memory_forensics.enabled',
        'REPORT_OUTPUT_DIR': 'reporting.output_dir',
        'REPORT_WEBHOOK_URL': 'reporting.webhook_url',
        'LOG_LEVEL': 'logging.level',
        'LOG_FILE': 'logging.file',
        'DATABASE_PATH': 'database.path',
        'DATABASE_CONNECTION_STRING': 'database.connection_string',
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Configuration Manager
        
        Args:
            config_path: Path to config.json file
        """
        self.config_path = config_path or os.getenv('AMBANI_CONFIG_PATH', 'config.json')
        self.config = self._deep_copy(DEFAULT_CONFIG)
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            self.load_config()
        
        # Override with environment variables
        self._load_env_variables()
    
    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a dictionary"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def load_config(self) -> None:
        """Load configuration from file and merge with defaults"""
        try:
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(self.config, file_config)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def _merge_config(self, base: Dict, override: Dict) -> None:
        """Recursively merge override config into base config"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_env_variables(self) -> None:
        """Load configuration from environment variables"""
        for env_var, config_key in self.ENV_MAPPINGS.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)
                self.set(config_key, converted_value)
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON conversion (for lists/dicts)
        if value.startswith('[') or value.startswith('{'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Return as string
        return value
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        errors = []
        
        # Required keys validation
        required_keys = [
            "ambani.enabled",
            "auto_stop.mode",
            "reporting.formats"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                errors.append(f"Missing required configuration: {key}")
        
        # Type validation
        if not isinstance(self.get("ambani.enabled"), bool):
            errors.append("ambani.enabled must be a boolean")
        
        if not isinstance(self.get("ambani.safe_mode", True), bool):
            errors.append("ambani.safe_mode must be a boolean")
        
        if not isinstance(self.get("ambani.rate_limit", 5), (int, float)):
            errors.append("ambani.rate_limit must be a number")
        
        # Value range validation
        auto_stop_mode = self.get("auto_stop.mode")
        if auto_stop_mode not in ["manual", "notify", "auto"]:
            errors.append(f"auto_stop.mode must be 'manual', 'notify', or 'auto', got: {auto_stop_mode}")
        
        critical_threshold = self.get("auto_stop.critical_threshold", 85)
        if not (0 <= critical_threshold <= 100):
            errors.append(f"auto_stop.critical_threshold must be between 0 and 100, got: {critical_threshold}")
        
        confidence_high = self.get("auto_stop.confidence_threshold_high", 0.80)
        if not (0.0 <= confidence_high <= 1.0):
            errors.append(f"auto_stop.confidence_threshold_high must be between 0.0 and 1.0, got: {confidence_high}")
        
        confidence_low = self.get("auto_stop.confidence_threshold_low", 0.60)
        if not (0.0 <= confidence_low <= 1.0):
            errors.append(f"auto_stop.confidence_threshold_low must be between 0.0 and 1.0, got: {confidence_low}")
        
        if confidence_low >= confidence_high:
            errors.append("auto_stop.confidence_threshold_low must be less than confidence_threshold_high")
        
        # Report formats validation
        report_formats = self.get("reporting.formats", [])
        if not isinstance(report_formats, list):
            errors.append("reporting.formats must be a list")
        else:
            valid_formats = ["json", "html", "pdf"]
            for fmt in report_formats:
                if fmt not in valid_formats:
                    errors.append(f"Invalid report format: {fmt}. Valid formats: {valid_formats}")
        
        # Logging level validation
        log_level = self.get("logging.level", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            errors.append(f"logging.level must be one of {valid_levels}, got: {log_level}")
        
        # Resource whitelist validation
        whitelist = self.get("resource_whitelist", [])
        if not isinstance(whitelist, list):
            errors.append("resource_whitelist must be a list")
        
        # ML models validation
        ml_models = self.get("ml.models", [])
        if not isinstance(ml_models, list):
            errors.append("ml.models must be a list")
        else:
            valid_models = ["isolation_forest", "one_class_svm", "autoencoder"]
            for model in ml_models:
                if model not in valid_models:
                    errors.append(f"Invalid ML model: {model}. Valid models: {valid_models}")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors))
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self._deep_copy(self.config)
    
    def reload(self) -> None:
        """Reload configuration from file and environment variables"""
        self.config = self._deep_copy(DEFAULT_CONFIG)
        if os.path.exists(self.config_path):
            self.load_config()
        self._load_env_variables()
    
    def create_default_config(self, path: Optional[str] = None) -> None:
        """
        Create a default configuration file
        
        Args:
            path: Path where to create the config file (defaults to self.config_path)
        """
        target_path = path or self.config_path
        try:
            with open(target_path, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to create default config: {e}")
