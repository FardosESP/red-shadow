"""
Unit tests for logging system
"""

import os
import tempfile
import logging
from pathlib import Path
import pytest

from ambani_integration.utils.logger import (
    LoggerManager,
    configure_logging,
    get_logger,
    set_log_level,
    add_file_handler,
    shutdown_logging
)
from ambani_integration.config.config_manager import ConfigManager


class TestLoggerManager:
    """Test LoggerManager class"""
    
    def setup_method(self):
        """Setup for each test"""
        # Reset singleton state
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Get all loggers and close their handlers
        manager = LoggerManager._instance
        if manager:
            for logger in list(manager._loggers.values()):
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
        
        shutdown_logging()
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def test_singleton_pattern(self):
        """Test that LoggerManager follows singleton pattern"""
        manager1 = LoggerManager()
        manager2 = LoggerManager()
        
        assert manager1 is manager2
    
    def test_get_logger_creates_new_logger(self):
        """Test that get_logger creates a new logger"""
        manager = LoggerManager()
        logger = manager.get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert "test_module" in manager._loggers
    
    def test_get_logger_returns_existing_logger(self):
        """Test that get_logger returns existing logger"""
        manager = LoggerManager()
        logger1 = manager.get_logger("test_module")
        logger2 = manager.get_logger("test_module")
        
        assert logger1 is logger2
    
    def test_parse_log_level(self):
        """Test log level parsing"""
        manager = LoggerManager()
        
        assert manager._parse_log_level("DEBUG") == logging.DEBUG
        assert manager._parse_log_level("INFO") == logging.INFO
        assert manager._parse_log_level("WARNING") == logging.WARNING
        assert manager._parse_log_level("WARN") == logging.WARNING
        assert manager._parse_log_level("ERROR") == logging.ERROR
        assert manager._parse_log_level("CRITICAL") == logging.CRITICAL
        assert manager._parse_log_level("INVALID") == logging.INFO  # Default
    
    def test_configure_with_config_manager(self):
        """Test configuration from ConfigManager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            # Create config
            config_path = os.path.join(tmpdir, "config.json")
            config_manager = ConfigManager(config_path)
            config_manager.set("logging.level", "DEBUG")
            config_manager.set("logging.file", log_file)
            config_manager.set("logging.console", True)
            
            # Configure logging
            manager = LoggerManager()
            manager.configure(config_manager)
            
            assert manager._log_level == logging.DEBUG
            assert manager._log_file == log_file
            assert manager._log_console is True
    
    def test_logger_with_custom_level(self):
        """Test creating logger with custom level"""
        manager = LoggerManager()
        logger = manager.get_logger("test_module", level="ERROR")
        
        assert logger.level == logging.ERROR
    
    def test_set_level_all_loggers(self):
        """Test setting level for all loggers"""
        manager = LoggerManager()
        logger1 = manager.get_logger("module1")
        logger2 = manager.get_logger("module2")
        
        manager.set_level("ERROR")
        
        assert logger1.level == logging.ERROR
        assert logger2.level == logging.ERROR
    
    def test_set_level_specific_logger(self):
        """Test setting level for specific logger"""
        manager = LoggerManager()
        logger1 = manager.get_logger("module1")
        logger2 = manager.get_logger("module2")
        
        manager.set_level("ERROR", "module1")
        
        assert logger1.level == logging.ERROR
        assert logger2.level == logging.INFO  # Default
    
    def test_add_file_handler(self):
        """Test adding file handler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            manager = LoggerManager()
            logger = manager.get_logger("test_module")
            
            initial_handlers = len(logger.handlers)
            manager.add_file_handler(log_file, "test_module")
            
            assert len(logger.handlers) == initial_handlers + 1
            assert os.path.exists(log_file)
    
    def test_logger_prevents_propagation(self):
        """Test that loggers don't propagate to root logger"""
        manager = LoggerManager()
        logger = manager.get_logger("test_module")
        
        assert logger.propagate is False
    
    def test_shutdown(self):
        """Test shutdown closes all handlers"""
        manager = LoggerManager()
        logger = manager.get_logger("test_module")
        
        manager.shutdown()
        
        assert len(manager._loggers) == 0
        assert len(logger.handlers) == 0


class TestModuleFunctions:
    """Test module-level functions"""
    
    def setup_method(self):
        """Setup for each test"""
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Get all loggers and close their handlers
        manager = LoggerManager._instance
        if manager:
            for logger in list(manager._loggers.values()):
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
        
        shutdown_logging()
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def test_configure_logging(self):
        """Test configure_logging function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config_manager = ConfigManager(config_path)
            config_manager.set("logging.level", "WARNING")
            
            configure_logging(config_manager)
            
            manager = LoggerManager()
            assert manager._log_level == logging.WARNING
    
    def test_get_logger_function(self):
        """Test get_logger function"""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_set_log_level_function(self):
        """Test set_log_level function"""
        logger = get_logger("test_module")
        
        set_log_level("ERROR")
        
        assert logger.level == logging.ERROR
    
    def test_add_file_handler_function(self):
        """Test add_file_handler function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            logger = get_logger("test_module")
            initial_handlers = len(logger.handlers)
            
            add_file_handler(log_file, "test_module")
            
            assert len(logger.handlers) == initial_handlers + 1


class TestLoggingIntegration:
    """Integration tests for logging system"""
    
    def setup_method(self):
        """Setup for each test"""
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Get all loggers and close their handlers
        manager = LoggerManager._instance
        if manager:
            for logger in list(manager._loggers.values()):
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
        
        shutdown_logging()
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def test_logging_to_file(self):
        """Test that logs are written to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            config_path = os.path.join(tmpdir, "config.json")
            config_manager = ConfigManager(config_path)
            config_manager.set("logging.file", log_file)
            config_manager.set("logging.level", "INFO")
            
            configure_logging(config_manager)
            
            logger = get_logger("test_module")
            logger.info("Test message")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Check file exists and contains message
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
                assert "INFO" in content
    
    def test_multiple_loggers_different_modules(self):
        """Test multiple loggers for different modules"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2
    
    def test_log_levels_filtering(self):
        """Test that log levels filter messages correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            config_path = os.path.join(tmpdir, "config.json")
            config_manager = ConfigManager(config_path)
            config_manager.set("logging.file", log_file)
            config_manager.set("logging.level", "WARNING")
            config_manager.set("logging.console", False)
            
            configure_logging(config_manager)
            
            logger = get_logger("test_module")
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Check file content
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Debug message" not in content
                assert "Info message" not in content
                assert "Warning message" in content
                assert "Error message" in content
    
    def test_reconfigure_existing_loggers(self):
        """Test that reconfiguring updates existing loggers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config_manager = ConfigManager(config_path)
            config_manager.set("logging.level", "INFO")
            
            configure_logging(config_manager)
            logger = get_logger("test_module")
            
            assert logger.level == logging.INFO
            
            # Reconfigure with different level
            config_manager.set("logging.level", "ERROR")
            configure_logging(config_manager)
            
            assert logger.level == logging.ERROR


class TestLegacyCompatibility:
    """Test backward compatibility with legacy setup_logger function"""
    
    def setup_method(self):
        """Setup for each test"""
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Get all loggers and close their handlers
        manager = LoggerManager._instance
        if manager:
            for logger in list(manager._loggers.values()):
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
        
        shutdown_logging()
        LoggerManager._instance = None
        LoggerManager._loggers = {}
        LoggerManager._initialized = False
    
    def test_setup_logger_legacy(self):
        """Test legacy setup_logger function"""
        from ambani_integration.utils.logger import setup_logger
        
        logger = setup_logger("test_module", logging.DEBUG)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_file(self):
        """Test legacy setup_logger with file"""
        from ambani_integration.utils.logger import setup_logger
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            logger = setup_logger("test_module", logging.INFO, log_file)
            logger.info("Test message")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            assert os.path.exists(log_file)
