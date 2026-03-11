"""
Logging System
Comprehensive logging with multiple levels and configuration integration
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class LoggerManager:
    """
    Centralized logging manager
    
    Responsibilities:
    - Configure logging from ConfigManager
    - Support multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Log to both file and console (configurable)
    - Provide structured logging with timestamps, module names, and log levels
    - Support different loggers per module
    """
    
    _instance: Optional['LoggerManager'] = None
    _loggers: Dict[str, logging.Logger] = {}
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure single LoggerManager instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize LoggerManager (only once due to singleton)"""
        if not self._initialized:
            self._config = None
            self._log_level = logging.INFO
            self._log_file = None
            self._log_console = True
            self._log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            LoggerManager._initialized = True
    
    def configure(self, config_manager=None) -> None:
        """
        Configure logging system from ConfigManager
        
        Args:
            config_manager: ConfigManager instance (optional)
        """
        if config_manager:
            self._config = config_manager
            
            # Get logging configuration
            log_level_str = config_manager.get('logging.level', 'INFO')
            self._log_level = self._parse_log_level(log_level_str)
            
            self._log_file = config_manager.get('logging.file', './logs/ambani_integration.log')
            self._log_console = config_manager.get('logging.console', True)
            self._log_format = config_manager.get('logging.format', 
                                                   '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Ensure log directory exists
            if self._log_file:
                log_dir = os.path.dirname(self._log_file)
                if log_dir:
                    Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Reconfigure existing loggers
        for logger_name in list(self._loggers.keys()):
            self._reconfigure_logger(logger_name)
    
    def _parse_log_level(self, level_str: str) -> int:
        """
        Parse log level string to logging constant
        
        Args:
            level_str: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Logging level constant
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str.upper(), logging.INFO)
    
    def _reconfigure_logger(self, logger_name: str) -> None:
        """
        Reconfigure an existing logger with current settings
        
        Args:
            logger_name: Name of the logger to reconfigure
        """
        if logger_name in self._loggers:
            logger = self._loggers[logger_name]
            
            # Update logger level
            logger.setLevel(self._log_level)
            
            # Remove existing handlers
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            
            # Re-add handlers with new configuration
            self._add_handlers(logger)
    
    def _add_handlers(self, logger: logging.Logger) -> None:
        """
        Add console and file handlers to logger
        
        Args:
            logger: Logger instance to add handlers to
        """
        formatter = logging.Formatter(self._log_format)
        
        # Console handler
        if self._log_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self._log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self._log_file:
            try:
                file_handler = logging.FileHandler(self._log_file, encoding='utf-8')
                file_handler.setLevel(self._log_level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                # If file handler fails, log to console
                if self._log_console:
                    print(f"Warning: Failed to create file handler for {self._log_file}: {e}", 
                          file=sys.stderr)
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger for a specific module
        
        Args:
            name: Logger name (typically module name)
            level: Optional log level override for this logger
            
        Returns:
            Configured logger instance
        """
        # Return existing logger if already created
        if name in self._loggers:
            logger = self._loggers[name]
            
            # Update level if specified
            if level:
                logger.setLevel(self._parse_log_level(level))
            
            return logger
        
        # Create new logger
        logger = logging.getLogger(name)
        
        # Set log level
        if level:
            logger.setLevel(self._parse_log_level(level))
        else:
            logger.setLevel(self._log_level)
        
        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        
        # Add handlers
        self._add_handlers(logger)
        
        # Store logger
        self._loggers[name] = logger
        
        return logger
    
    def set_level(self, level: str, logger_name: Optional[str] = None) -> None:
        """
        Set log level for all loggers or a specific logger
        
        Args:
            level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            logger_name: Optional logger name (if None, applies to all loggers)
        """
        log_level = self._parse_log_level(level)
        
        if logger_name:
            # Set level for specific logger
            if logger_name in self._loggers:
                logger = self._loggers[logger_name]
                logger.setLevel(log_level)
                
                # Update handlers
                for handler in logger.handlers:
                    handler.setLevel(log_level)
        else:
            # Set level for all loggers
            self._log_level = log_level
            
            for logger in self._loggers.values():
                logger.setLevel(log_level)
                
                # Update handlers
                for handler in logger.handlers:
                    handler.setLevel(log_level)
    
    def add_file_handler(self, log_file: str, logger_name: Optional[str] = None) -> None:
        """
        Add an additional file handler to logger(s)
        
        Args:
            log_file: Path to log file
            logger_name: Optional logger name (if None, applies to all loggers)
        """
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        formatter = logging.Formatter(self._log_format)
        
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self._log_level)
            file_handler.setFormatter(formatter)
            
            if logger_name:
                # Add to specific logger
                if logger_name in self._loggers:
                    self._loggers[logger_name].addHandler(file_handler)
            else:
                # Add to all loggers
                for logger in self._loggers.values():
                    logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Failed to add file handler for {log_file}: {e}", file=sys.stderr)
    
    def shutdown(self) -> None:
        """Shutdown all loggers and close handlers"""
        for logger in self._loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        
        self._loggers.clear()
        logging.shutdown()


# Global logger manager instance
_logger_manager = LoggerManager()


def configure_logging(config_manager=None) -> None:
    """
    Configure the logging system
    
    Args:
        config_manager: ConfigManager instance (optional)
    """
    _logger_manager.configure(config_manager)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        name: Logger name (typically module name)
        level: Optional log level override for this logger
        
    Returns:
        Configured logger instance
    """
    return _logger_manager.get_logger(name, level)


def set_log_level(level: str, logger_name: Optional[str] = None) -> None:
    """
    Set log level for all loggers or a specific logger
    
    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional logger name (if None, applies to all loggers)
    """
    _logger_manager.set_level(level, logger_name)


def add_file_handler(log_file: str, logger_name: Optional[str] = None) -> None:
    """
    Add an additional file handler to logger(s)
    
    Args:
        log_file: Path to log file
        logger_name: Optional logger name (if None, applies to all loggers)
    """
    _logger_manager.add_file_handler(log_file, logger_name)


def shutdown_logging() -> None:
    """Shutdown all loggers and close handlers"""
    _logger_manager.shutdown()


# Legacy compatibility functions
def setup_logger(
    name: str = "ambani_integration",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Legacy function for backward compatibility
    Set up logger with console and optional file output
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    # Convert int level to string
    level_map = {
        logging.DEBUG: 'DEBUG',
        logging.INFO: 'INFO',
        logging.WARNING: 'WARNING',
        logging.ERROR: 'ERROR',
        logging.CRITICAL: 'CRITICAL'
    }
    level_str = level_map.get(level, 'INFO')
    
    logger = get_logger(name, level_str)
    
    if log_file:
        add_file_handler(log_file, name)
    
    return logger
