"""
Application Settings
Default configuration and settings
"""

from typing import Dict, Any, List, Optional


# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "ambani": {
        "enabled": True,
        "api_path": "/path/to/ambani/api",
        "safe_mode": True,
        "dry_run": False,
        "rate_limit": 5
    },
    "auto_stop": {
        "mode": "notify",  # manual, notify, auto
        "critical_threshold": 85,
        "confidence_threshold_high": 0.80,
        "confidence_threshold_low": 0.60,
        "grace_period": 300,  # seconds
        "max_stops_per_minute": 3,
        "learning_mode": True
    },
    "ml": {
        "enabled": True,
        "models": ["isolation_forest", "one_class_svm", "autoencoder"],
        "contamination": 0.1,
        "training_data_path": "./data/training"
    },
    "network_monitor": {
        "enabled": True,
        "interface": "eth0",
        "capture_filter": "port 30120",
        "sampling_mode": False,
        "sampling_rate": 10
    },
    "memory_forensics": {
        "enabled": True,
        "snapshot_interval": 60,  # seconds
        "yara_rules_path": "./rules/yara"
    },
    "resource_whitelist": [
        "es_extended",
        "qb-core",
        "ox_core",
        "vrp",
        "vRP",
        "oxmysql",
        "mysql-async",
        "ghmattimysql",
        "txAdmin",
        "txAdminClient",
        "monitor",
        "sessionmanager",
        "mapmanager",
        "spawnmanager",
        "baseevents",
        "chat",
        "hardcap",
        "rconlog",
        "playernames"
    ],
    "reporting": {
        "formats": ["json", "html"],
        "output_dir": "./reports",
        "include_poc": True,
        "webhook_url": None
    },
    "logging": {
        "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        "file": "./logs/ambani_integration.log",
        "console": True,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "database": {
        "path": "./data/ambani_integration.db",
        "connection_string": None,  # Optional: for external databases
        "pool_size": 5,
        "timeout": 30
    },
    "api_endpoints": {
        "vulnerability_db": "https://api.ambani-integration.dev/vulnerabilities",
        "signature_updates": "https://api.ambani-integration.dev/signatures",
        "telemetry": None  # Optional: for usage statistics
    },
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


class Settings:
    """
    Application settings wrapper
    
    Provides easy access to configuration values
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize settings
        
        Args:
            config: Configuration dictionary
        """
        self._config = config
    
    # Ambani settings
    @property
    def ambani_enabled(self) -> bool:
        """Check if Ambani integration is enabled"""
        return self._config.get("ambani", {}).get("enabled", True)
    
    @property
    def ambani_api_path(self) -> str:
        """Get Ambani API path"""
        return self._config.get("ambani", {}).get("api_path", "/path/to/ambani/api")
    
    @property
    def safe_mode(self) -> bool:
        """Check if safe mode is enabled"""
        return self._config.get("ambani", {}).get("safe_mode", True)
    
    @property
    def dry_run(self) -> bool:
        """Check if dry-run mode is enabled"""
        return self._config.get("ambani", {}).get("dry_run", False)
    
    @property
    def rate_limit(self) -> int:
        """Get rate limit for Ambani operations"""
        return self._config.get("ambani", {}).get("rate_limit", 5)
    
    # Auto-stop settings
    @property
    def auto_stop_mode(self) -> str:
        """Get auto-stop mode (manual, notify, auto)"""
        return self._config.get("auto_stop", {}).get("mode", "notify")
    
    @property
    def critical_threshold(self) -> int:
        """Get critical threshold for auto-stop"""
        return self._config.get("auto_stop", {}).get("critical_threshold", 85)
    
    @property
    def confidence_threshold_high(self) -> float:
        """Get high confidence threshold"""
        return self._config.get("auto_stop", {}).get("confidence_threshold_high", 0.80)
    
    @property
    def confidence_threshold_low(self) -> float:
        """Get low confidence threshold"""
        return self._config.get("auto_stop", {}).get("confidence_threshold_low", 0.60)
    
    @property
    def grace_period(self) -> int:
        """Get grace period in seconds"""
        return self._config.get("auto_stop", {}).get("grace_period", 300)
    
    @property
    def max_stops_per_minute(self) -> int:
        """Get maximum stops per minute"""
        return self._config.get("auto_stop", {}).get("max_stops_per_minute", 3)
    
    @property
    def learning_mode(self) -> bool:
        """Check if learning mode is enabled"""
        return self._config.get("auto_stop", {}).get("learning_mode", True)
    
    # ML settings
    @property
    def ml_enabled(self) -> bool:
        """Check if ML is enabled"""
        return self._config.get("ml", {}).get("enabled", True)
    
    @property
    def ml_models(self) -> List[str]:
        """Get list of ML models to use"""
        return self._config.get("ml", {}).get("models", ["isolation_forest", "one_class_svm", "autoencoder"])
    
    @property
    def ml_contamination(self) -> float:
        """Get ML contamination parameter"""
        return self._config.get("ml", {}).get("contamination", 0.1)
    
    @property
    def ml_training_data_path(self) -> str:
        """Get ML training data path"""
        return self._config.get("ml", {}).get("training_data_path", "./data/training")
    
    # Network monitor settings
    @property
    def network_monitor_enabled(self) -> bool:
        """Check if network monitoring is enabled"""
        return self._config.get("network_monitor", {}).get("enabled", True)
    
    @property
    def network_interface(self) -> str:
        """Get network interface for monitoring"""
        return self._config.get("network_monitor", {}).get("interface", "eth0")
    
    @property
    def capture_filter(self) -> str:
        """Get packet capture filter"""
        return self._config.get("network_monitor", {}).get("capture_filter", "port 30120")
    
    @property
    def sampling_mode(self) -> bool:
        """Check if sampling mode is enabled"""
        return self._config.get("network_monitor", {}).get("sampling_mode", False)
    
    @property
    def sampling_rate(self) -> int:
        """Get sampling rate"""
        return self._config.get("network_monitor", {}).get("sampling_rate", 10)
    
    # Memory forensics settings
    @property
    def memory_forensics_enabled(self) -> bool:
        """Check if memory forensics is enabled"""
        return self._config.get("memory_forensics", {}).get("enabled", True)
    
    @property
    def snapshot_interval(self) -> int:
        """Get memory snapshot interval in seconds"""
        return self._config.get("memory_forensics", {}).get("snapshot_interval", 60)
    
    @property
    def yara_rules_path(self) -> str:
        """Get YARA rules path"""
        return self._config.get("memory_forensics", {}).get("yara_rules_path", "./rules/yara")
    
    # Resource whitelist
    @property
    def resource_whitelist(self) -> List[str]:
        """Get resource whitelist"""
        return self._config.get("resource_whitelist", [])
    
    # Reporting settings
    @property
    def report_formats(self) -> List[str]:
        """Get report formats"""
        return self._config.get("reporting", {}).get("formats", ["json", "html"])
    
    @property
    def output_dir(self) -> str:
        """Get output directory"""
        return self._config.get("reporting", {}).get("output_dir", "./reports")
    
    @property
    def include_poc(self) -> bool:
        """Check if PoC should be included in reports"""
        return self._config.get("reporting", {}).get("include_poc", True)
    
    @property
    def webhook_url(self) -> Optional[str]:
        """Get webhook URL for notifications"""
        return self._config.get("reporting", {}).get("webhook_url")
    
    # Logging settings
    @property
    def log_level(self) -> str:
        """Get logging level"""
        return self._config.get("logging", {}).get("level", "INFO")
    
    @property
    def log_file(self) -> str:
        """Get log file path"""
        return self._config.get("logging", {}).get("file", "./logs/ambani_integration.log")
    
    @property
    def log_console(self) -> bool:
        """Check if console logging is enabled"""
        return self._config.get("logging", {}).get("console", True)
    
    @property
    def log_format(self) -> str:
        """Get log format string"""
        return self._config.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Database settings
    @property
    def database_path(self) -> str:
        """Get database path"""
        return self._config.get("database", {}).get("path", "./data/ambani_integration.db")
    
    @property
    def database_connection_string(self) -> Optional[str]:
        """Get database connection string"""
        return self._config.get("database", {}).get("connection_string")
    
    @property
    def database_pool_size(self) -> int:
        """Get database connection pool size"""
        return self._config.get("database", {}).get("pool_size", 5)
    
    @property
    def database_timeout(self) -> int:
        """Get database timeout in seconds"""
        return self._config.get("database", {}).get("timeout", 30)
    
    # API endpoints
    @property
    def vulnerability_db_endpoint(self) -> str:
        """Get vulnerability database API endpoint"""
        return self._config.get("api_endpoints", {}).get("vulnerability_db", "https://api.ambani-integration.dev/vulnerabilities")
    
    @property
    def signature_updates_endpoint(self) -> str:
        """Get signature updates API endpoint"""
        return self._config.get("api_endpoints", {}).get("signature_updates", "https://api.ambani-integration.dev/signatures")
    
    @property
    def telemetry_endpoint(self) -> Optional[str]:
        """Get telemetry API endpoint"""
        return self._config.get("api_endpoints", {}).get("telemetry")
    
    # Thresholds
    @property
    def risk_thresholds(self) -> Dict[str, int]:
        """Get risk score thresholds"""
        return self._config.get("thresholds", {}).get("risk_score", {
            "critical": 70,
            "high": 50,
            "medium": 30,
            "low": 0
        })
    
    @property
    def anomaly_thresholds(self) -> Dict[str, float]:
        """Get anomaly score thresholds"""
        return self._config.get("thresholds", {}).get("anomaly_score", {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3
        })
    
    @property
    def honeypot_confidence_threshold(self) -> float:
        """Get honeypot confidence threshold"""
        return self._config.get("thresholds", {}).get("honeypot_confidence", 0.7)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
