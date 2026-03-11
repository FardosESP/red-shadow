"""
Tests for Configuration Manager
"""

import os
import json
import tempfile
import pytest
from ambani_integration.config import ConfigManager, Settings, DEFAULT_CONFIG


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(DEFAULT_CONFIG, f)
            config_path = f.name
        
        try:
            manager = ConfigManager(config_path)
            assert manager.get('ambani.enabled') == True
            assert manager.get('auto_stop.mode') == 'notify'
            assert manager.get('ambani.rate_limit') == 5
        finally:
            os.unlink(config_path)
    
    def test_get_with_dot_notation(self):
        """Test getting values with dot notation"""
        manager = ConfigManager()
        manager.config = {'ambani': {'enabled': True, 'safe_mode': False}}
        
        assert manager.get('ambani.enabled') == True
        assert manager.get('ambani.safe_mode') == False
        assert manager.get('ambani.nonexistent', 'default') == 'default'
    
    def test_set_with_dot_notation(self):
        """Test setting values with dot notation"""
        manager = ConfigManager()
        manager.config = {}
        
        manager.set('ambani.enabled', True)
        manager.set('ambani.rate_limit', 10)
        
        assert manager.get('ambani.enabled') == True
        assert manager.get('ambani.rate_limit') == 10
    
    def test_environment_variable_override(self):
        """Test environment variable override"""
        os.environ['AMBANI_ENABLED'] = 'false'
        os.environ['AMBANI_RATE_LIMIT'] = '10'
        os.environ['AUTO_STOP_MODE'] = 'auto'
        
        try:
            manager = ConfigManager()
            assert manager.get('ambani.enabled') == False
            assert manager.get('ambani.rate_limit') == 10
            assert manager.get('auto_stop.mode') == 'auto'
        finally:
            del os.environ['AMBANI_ENABLED']
            del os.environ['AMBANI_RATE_LIMIT']
            del os.environ['AUTO_STOP_MODE']
    
    def test_validate_valid_config(self):
        """Test validation with valid configuration"""
        manager = ConfigManager()
        assert manager.validate() == True
    
    def test_validate_invalid_mode(self):
        """Test validation with invalid auto_stop mode"""
        manager = ConfigManager()
        manager.set('auto_stop.mode', 'invalid')
        
        with pytest.raises(ValueError) as exc_info:
            manager.validate()
        
        assert 'auto_stop.mode' in str(exc_info.value)
    
    def test_validate_invalid_threshold(self):
        """Test validation with invalid threshold"""
        manager = ConfigManager()
        manager.set('auto_stop.critical_threshold', 150)
        
        with pytest.raises(ValueError) as exc_info:
            manager.validate()
        
        assert 'critical_threshold' in str(exc_info.value)
    
    def test_validate_invalid_confidence(self):
        """Test validation with invalid confidence thresholds"""
        manager = ConfigManager()
        manager.set('auto_stop.confidence_threshold_low', 0.9)
        manager.set('auto_stop.confidence_threshold_high', 0.8)
        
        with pytest.raises(ValueError) as exc_info:
            manager.validate()
        
        assert 'confidence_threshold_low' in str(exc_info.value)
    
    def test_create_default_config(self):
        """Test creating default config file"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            os.unlink(config_path)  # Remove the temp file
            manager = ConfigManager()
            manager.create_default_config(config_path)
            
            assert os.path.exists(config_path)
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert config['ambani']['enabled'] == True
            assert config['auto_stop']['mode'] == 'notify'
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_reload_config(self):
        """Test reloading configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'ambani': {'enabled': False}}, f)
            config_path = f.name
        
        try:
            manager = ConfigManager(config_path)
            assert manager.get('ambani.enabled') == False
            
            # Modify file
            with open(config_path, 'w') as f:
                json.dump({'ambani': {'enabled': True}}, f)
            
            manager.reload()
            assert manager.get('ambani.enabled') == True
        finally:
            os.unlink(config_path)


class TestSettings:
    """Test Settings wrapper"""
    
    def test_settings_properties(self):
        """Test Settings property access"""
        settings = Settings(DEFAULT_CONFIG)
        
        assert settings.ambani_enabled == True
        assert settings.safe_mode == True
        assert settings.auto_stop_mode == 'notify'
        assert settings.ml_enabled == True
        assert settings.network_monitor_enabled == True
        assert settings.memory_forensics_enabled == True
    
    def test_settings_thresholds(self):
        """Test Settings threshold access"""
        settings = Settings(DEFAULT_CONFIG)
        
        risk_thresholds = settings.risk_thresholds
        assert risk_thresholds['critical'] == 70
        assert risk_thresholds['high'] == 50
        
        anomaly_thresholds = settings.anomaly_thresholds
        assert anomaly_thresholds['high'] == 0.8
        assert anomaly_thresholds['medium'] == 0.5
    
    def test_settings_get_method(self):
        """Test Settings get method"""
        settings = Settings(DEFAULT_CONFIG)
        
        assert settings.get('ambani.enabled') == True
        assert settings.get('nonexistent.key', 'default') == 'default'
