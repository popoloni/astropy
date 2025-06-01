"""
Precision Configuration Management

This module handles configuration for high-precision astronomical calculations,
including precision mode switching, validation, and context management.
"""

import json
import os
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Union
from threading import local

# Thread-local storage for precision configuration
_thread_local = local()

logger = logging.getLogger(__name__)

# Default precision configuration
DEFAULT_PRECISION_CONFIG = {
    "precision": {
        "use_high_precision": True,
        "include_refraction": True,
        "include_parallax": False,
        "cache_calculations": True,
        "fallback_on_error": True,
        "log_precision_warnings": True
    },
    "atmospheric": {
        "default_pressure_mbar": 1013.25,
        "default_temperature_c": 15.0,
        "enable_weather_corrections": False,
        "refraction_model": "bennett"
    },
    "performance": {
        "enable_caching": True,
        "cache_size_limit": 1000,
        "benchmark_mode": False
    }
}

# Valid precision modes
PRECISION_MODES = ['standard', 'high', 'auto']

class PrecisionConfigError(Exception):
    """Exception raised for precision configuration errors"""
    pass

def _get_thread_config():
    """Get thread-local configuration, initializing if needed"""
    if not hasattr(_thread_local, 'config'):
        _thread_local.config = load_precision_config()
    if not hasattr(_thread_local, 'precision_mode'):
        _thread_local.precision_mode = 'auto'
    return _thread_local

def load_precision_config() -> Dict[str, Any]:
    """
    Load precision configuration from file or return defaults
    
    Returns:
        Dict containing precision configuration
    """
    # Try to load from existing config.json
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(script_dir, 'config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Merge with defaults for any missing keys
            merged_config = DEFAULT_PRECISION_CONFIG.copy()
            for section, values in config.items():
                if section in merged_config:
                    merged_config[section].update(values)
                else:
                    merged_config[section] = values
                    
            return merged_config
            
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    return DEFAULT_PRECISION_CONFIG.copy()

def save_precision_config(config: Dict[str, Any]) -> None:
    """
    Save precision configuration to file
    
    Args:
        config: Configuration dictionary to save
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(script_dir, 'config.json')
    
    try:
        # Load existing config and update precision sections
        existing_config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        
        # Update precision-related sections
        for section in ['precision', 'atmospheric', 'performance']:
            if section in config:
                existing_config[section] = config[section]
        
        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
            
        logger.info(f"Precision configuration saved to {config_path}")
        
    except Exception as e:
        logger.error(f"Failed to save precision config: {e}")
        raise PrecisionConfigError(f"Could not save configuration: {e}")

def validate_precision_config(config: Dict[str, Any]) -> bool:
    """
    Validate precision configuration structure and values
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, raises PrecisionConfigError if invalid
    """
    required_sections = ['precision', 'atmospheric', 'performance']
    
    for section in required_sections:
        if section not in config:
            raise PrecisionConfigError(f"Missing required section: {section}")
    
    # Validate precision section
    precision = config['precision']
    required_precision_keys = [
        'use_high_precision', 'include_refraction', 'include_parallax',
        'cache_calculations', 'fallback_on_error', 'log_precision_warnings'
    ]
    
    for key in required_precision_keys:
        if key not in precision:
            raise PrecisionConfigError(f"Missing precision key: {key}")
        if not isinstance(precision[key], bool):
            raise PrecisionConfigError(f"Precision key {key} must be boolean")
    
    # Validate atmospheric section
    atmospheric = config['atmospheric']
    if atmospheric['default_pressure_mbar'] <= 0:
        raise PrecisionConfigError("Pressure must be positive")
    if atmospheric['default_temperature_c'] < -273.15:
        raise PrecisionConfigError("Temperature must be above absolute zero")
    if atmospheric['refraction_model'] not in ['bennett', 'saemundsson', 'simple']:
        raise PrecisionConfigError("Invalid refraction model")
    
    # Validate performance section
    performance = config['performance']
    if performance['cache_size_limit'] <= 0:
        raise PrecisionConfigError("Cache size limit must be positive")
    
    return True

def set_precision_mode(mode: str) -> None:
    """
    Set global precision mode
    
    Args:
        mode: Precision mode ('standard', 'high', 'auto')
    """
    if mode not in PRECISION_MODES:
        raise PrecisionConfigError(f"Invalid precision mode: {mode}. Must be one of {PRECISION_MODES}")
    
    thread_config = _get_thread_config()
    thread_config.precision_mode = mode
    
    logger.info(f"Precision mode set to: {mode}")

def get_precision_mode() -> str:
    """
    Get current precision mode
    
    Returns:
        Current precision mode string
    """
    thread_config = _get_thread_config()
    return thread_config.precision_mode

def get_precision_config() -> Dict[str, Any]:
    """
    Get current precision configuration
    
    Returns:
        Current precision configuration dictionary
    """
    thread_config = _get_thread_config()
    return thread_config.config.copy()

def update_precision_config(updates: Dict[str, Any]) -> None:
    """
    Update precision configuration
    
    Args:
        updates: Dictionary of configuration updates
    """
    thread_config = _get_thread_config()
    
    # Deep merge updates into current config
    for section, values in updates.items():
        if section in thread_config.config:
            thread_config.config[section].update(values)
        else:
            thread_config.config[section] = values
    
    # Validate updated configuration
    validate_precision_config(thread_config.config)
    
    logger.info(f"Precision configuration updated: {updates}")

@contextmanager
def precision_context(mode: str, **config_overrides):
    """
    Context manager for temporary precision mode and configuration changes
    
    Args:
        mode: Temporary precision mode
        **config_overrides: Temporary configuration overrides
        
    Example:
        with precision_context('high', include_refraction=True):
            lst = calculate_lst(dt)
            sun_pos = calculate_sun_position(dt)
    """
    thread_config = _get_thread_config()
    
    # Save current state
    old_mode = thread_config.precision_mode
    old_config = thread_config.config.copy()
    
    try:
        # Apply temporary changes
        set_precision_mode(mode)
        
        if config_overrides:
            # Apply config overrides
            temp_updates = {}
            for key, value in config_overrides.items():
                # Handle nested config keys like 'precision.use_high_precision'
                if '.' in key:
                    section, subkey = key.split('.', 1)
                    if section not in temp_updates:
                        temp_updates[section] = {}
                    temp_updates[section][subkey] = value
                else:
                    # Assume it's a precision setting if no section specified
                    if 'precision' not in temp_updates:
                        temp_updates['precision'] = {}
                    temp_updates['precision'][key] = value
            
            update_precision_config(temp_updates)
        
        yield
        
    finally:
        # Restore original state
        thread_config.precision_mode = old_mode
        thread_config.config = old_config

def should_use_high_precision(precision_mode: Optional[str] = None) -> bool:
    """
    Determine if high precision should be used based on mode and configuration
    
    Args:
        precision_mode: Override precision mode (optional)
        
    Returns:
        True if high precision should be used
    """
    if precision_mode is None:
        precision_mode = get_precision_mode()
    
    if precision_mode == 'high':
        return True
    elif precision_mode == 'standard':
        return False
    elif precision_mode == 'auto':
        config = get_precision_config()
        return config['precision']['use_high_precision']
    else:
        raise PrecisionConfigError(f"Unknown precision mode: {precision_mode}")

def log_precision_fallback(function_name: str, error: Exception) -> None:
    """
    Log precision fallback events
    
    Args:
        function_name: Name of function that failed in high precision
        error: Exception that caused the fallback
    """
    config = get_precision_config()
    if config['precision']['log_precision_warnings']:
        logger.warning(f"High-precision {function_name} failed, using standard: {error}")

def get_atmospheric_config() -> Dict[str, Any]:
    """
    Get atmospheric correction configuration
    
    Returns:
        Atmospheric configuration dictionary
    """
    config = get_precision_config()
    return config['atmospheric']

def get_performance_config() -> Dict[str, Any]:
    """
    Get performance configuration
    
    Returns:
        Performance configuration dictionary
    """
    config = get_precision_config()
    return config['performance']

# Initialize default configuration on module import
try:
    _get_thread_config()
except Exception as e:
    logger.warning(f"Failed to initialize precision configuration: {e}")