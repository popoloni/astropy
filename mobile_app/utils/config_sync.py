"""
Configuration Synchronization Utility
Handles synchronization between mobile app and desktop configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional

Logger = logging.getLogger(__name__)

def get_main_config_path() -> str:
    """Get the path to the main config.json file"""
    # Mobile app is in mobile_app/ subdirectory, main config is in parent directory
    current_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(current_dir, 'config.json')

def load_main_config() -> Optional[Dict[str, Any]]:
    """Load the main configuration file"""
    try:
        config_path = get_main_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            Logger.info(f"Loaded main configuration from {config_path}")
            return config
        else:
            Logger.warning(f"Main configuration file not found at {config_path}")
            return None
    except Exception as e:
        Logger.error(f"Error loading main configuration: {e}")
        return None

def get_twilight_configuration() -> str:
    """Get the twilight type from main configuration"""
    try:
        config = load_main_config()
        if config and 'visibility' in config and 'twilight_type' in config['visibility']:
            twilight_type = config['visibility']['twilight_type']
            Logger.info(f"Retrieved twilight type from main config: {twilight_type}")
            return twilight_type
        else:
            Logger.warning("Twilight type not found in main config, using default")
            return 'astronomical'
    except Exception as e:
        Logger.error(f"Error getting twilight configuration: {e}")
        return 'astronomical'

def sync_twilight_to_main_config(twilight_type: str) -> bool:
    """Sync twilight type back to main configuration"""
    try:
        config_path = get_main_config_path()
        config = load_main_config()
        
        if config is None:
            # Create basic config structure if it doesn't exist
            config = {
                'visibility': {
                    'twilight_type': twilight_type
                }
            }
        else:
            # Update existing config
            if 'visibility' not in config:
                config['visibility'] = {}
            config['visibility']['twilight_type'] = twilight_type
        
        # Save updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        Logger.info(f"Synced twilight type '{twilight_type}' to main configuration")
        return True
        
    except Exception as e:
        Logger.error(f"Error syncing twilight configuration: {e}")
        return False

def get_scheduling_configuration() -> Dict[str, Any]:
    """Get scheduling configuration from main config"""
    try:
        config = load_main_config()
        if config and 'scheduling' in config:
            return config['scheduling']
        else:
            # Return default scheduling configuration
            return {
                'exclude_insufficient_time': False,
                'min_visibility_hours': 1.0
            }
    except Exception as e:
        Logger.error(f"Error getting scheduling configuration: {e}")
        return {
            'exclude_insufficient_time': False,
            'min_visibility_hours': 1.0
        }

def get_location_configuration() -> Optional[Dict[str, Any]]:
    """Get location configuration from main config"""
    try:
        config = load_main_config()
        if config and 'location' in config:
            return config['location']
        else:
            return None
    except Exception as e:
        Logger.error(f"Error getting location configuration: {e}")
        return None

def sync_mobile_settings_to_main(mobile_settings: Dict[str, Any]) -> bool:
    """Sync mobile app settings back to main configuration"""
    try:
        config = load_main_config()
        if config is None:
            config = {}
        
        # Sync twilight type
        if 'twilight_type' in mobile_settings:
            if 'visibility' not in config:
                config['visibility'] = {}
            config['visibility']['twilight_type'] = mobile_settings['twilight_type']
        
        # Sync scheduling preferences
        if 'scheduling' not in config:
            config['scheduling'] = {}
        
        if 'min_visibility' in mobile_settings:
            config['scheduling']['min_visibility_hours'] = mobile_settings['min_visibility']
        
        if 'exclude_insufficient' in mobile_settings:
            config['scheduling']['exclude_insufficient_time'] = mobile_settings['exclude_insufficient']
        
        # Save updated configuration
        config_path = get_main_config_path()
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        Logger.info("Successfully synced mobile settings to main configuration")
        return True
        
    except Exception as e:
        Logger.error(f"Error syncing mobile settings to main config: {e}")
        return False

def validate_configuration_consistency() -> Dict[str, Any]:
    """Validate consistency between mobile and desktop configurations"""
    try:
        main_config = load_main_config()
        
        issues = []
        recommendations = []
        
        if main_config is None:
            issues.append("Main configuration file not found")
            recommendations.append("Create main config.json file")
        else:
            # Check twilight configuration
            if 'visibility' not in main_config or 'twilight_type' not in main_config['visibility']:
                issues.append("Twilight type not configured in main config")
                recommendations.append("Set twilight_type in main config visibility section")
            
            # Check scheduling configuration
            if 'scheduling' not in main_config:
                issues.append("Scheduling configuration missing from main config")
                recommendations.append("Add scheduling section to main config")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations,
            'main_config_exists': main_config is not None
        }
        
    except Exception as e:
        Logger.error(f"Error validating configuration consistency: {e}")
        return {
            'valid': False,
            'issues': [f"Validation error: {e}"],
            'recommendations': ["Check configuration file permissions and format"],
            'main_config_exists': False
        } 