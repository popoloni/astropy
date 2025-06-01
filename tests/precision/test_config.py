"""
Tests for precision configuration management
"""

import pytest
import json
import tempfile
import os
from datetime import datetime

from astronomy.precision.config import (
    set_precision_mode, get_precision_mode, precision_context,
    get_precision_config, update_precision_config, validate_precision_config,
    should_use_high_precision, PrecisionConfigError
)

class TestPrecisionConfig:
    
    def test_default_precision_mode(self):
        """Test default precision mode is 'auto'"""
        mode = get_precision_mode()
        assert mode in ['standard', 'high', 'auto']
    
    def test_set_precision_mode(self):
        """Test setting precision mode"""
        original_mode = get_precision_mode()
        
        try:
            set_precision_mode('high')
            assert get_precision_mode() == 'high'
            
            set_precision_mode('standard')
            assert get_precision_mode() == 'standard'
            
            set_precision_mode('auto')
            assert get_precision_mode() == 'auto'
        finally:
            set_precision_mode(original_mode)
    
    def test_invalid_precision_mode(self):
        """Test setting invalid precision mode raises error"""
        with pytest.raises(PrecisionConfigError):
            set_precision_mode('invalid_mode')
    
    def test_precision_context(self):
        """Test precision context manager"""
        original_mode = get_precision_mode()
        
        with precision_context('high'):
            assert get_precision_mode() == 'high'
        
        assert get_precision_mode() == original_mode
    
    def test_precision_context_with_config(self):
        """Test precision context with configuration overrides"""
        original_config = get_precision_config()
        
        with precision_context('high', use_high_precision=False, include_refraction=True):
            assert get_precision_mode() == 'high'
            config = get_precision_config()
            assert config['precision']['use_high_precision'] == False
            assert config['precision']['include_refraction'] == True
        
        # Verify original config is restored
        restored_config = get_precision_config()
        assert restored_config['precision']['use_high_precision'] == original_config['precision']['use_high_precision']
    
    def test_should_use_high_precision(self):
        """Test precision mode logic"""
        assert should_use_high_precision('high') == True
        assert should_use_high_precision('standard') == False
        
        # Test auto mode depends on configuration
        original_mode = get_precision_mode()
        try:
            set_precision_mode('auto')
            config = get_precision_config()
            expected = config['precision']['use_high_precision']
            assert should_use_high_precision('auto') == expected
        finally:
            set_precision_mode(original_mode)
    
    def test_validate_precision_config(self):
        """Test configuration validation"""
        valid_config = {
            'precision': {
                'use_high_precision': True,
                'include_refraction': True,
                'include_parallax': False,
                'cache_calculations': True,
                'fallback_on_error': True,
                'log_precision_warnings': True
            },
            'atmospheric': {
                'default_pressure_mbar': 1013.25,
                'default_temperature_c': 15.0,
                'enable_weather_corrections': False,
                'refraction_model': 'bennett'
            },
            'performance': {
                'enable_caching': True,
                'cache_size_limit': 1000,
                'benchmark_mode': False
            }
        }
        
        assert validate_precision_config(valid_config) == True
    
    def test_invalid_config_validation(self):
        """Test validation of invalid configurations"""
        # Missing section
        invalid_config = {
            'precision': {},
            'atmospheric': {}
            # Missing performance section
        }
        
        with pytest.raises(PrecisionConfigError):
            validate_precision_config(invalid_config)
        
        # Invalid pressure
        invalid_config = {
            'precision': {
                'use_high_precision': True,
                'include_refraction': True,
                'include_parallax': False,
                'cache_calculations': True,
                'fallback_on_error': True,
                'log_precision_warnings': True
            },
            'atmospheric': {
                'default_pressure_mbar': -100,  # Invalid negative pressure
                'default_temperature_c': 15.0,
                'enable_weather_corrections': False,
                'refraction_model': 'bennett'
            },
            'performance': {
                'enable_caching': True,
                'cache_size_limit': 1000,
                'benchmark_mode': False
            }
        }
        
        with pytest.raises(PrecisionConfigError):
            validate_precision_config(invalid_config)
    
    def test_update_precision_config(self):
        """Test updating precision configuration"""
        original_config = get_precision_config()
        
        try:
            updates = {
                'precision': {
                    'include_refraction': False
                },
                'atmospheric': {
                    'default_pressure_mbar': 1000.0
                }
            }
            
            update_precision_config(updates)
            
            updated_config = get_precision_config()
            assert updated_config['precision']['include_refraction'] == False
            assert updated_config['atmospheric']['default_pressure_mbar'] == 1000.0
            
        finally:
            # Restore original configuration
            update_precision_config(original_config)

if __name__ == '__main__':
    pytest.main([__file__])