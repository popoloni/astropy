"""
Configuration settings and loading functions for the astropy application.
"""

import os
import json
from models import SchedulingStrategy, Observer


def load_config():
    """Load configuration from JSON file"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def get_default_location(config):
    """Get the default location from config with validation"""
    for loc_id, loc_data in config['locations'].items():
        if loc_data.get('default', False):
            # Validate location data
            if 'latitude' not in loc_data or 'longitude' not in loc_data:
                raise ValueError(f"Location {loc_id} missing latitude or longitude")
            if not -90 <= loc_data['latitude'] <= 90:
                raise ValueError(f"Invalid latitude for {loc_id}: {loc_data['latitude']}")
            if not -180 <= loc_data['longitude'] <= 180:
                raise ValueError(f"Invalid longitude for {loc_id}: {loc_data['longitude']}")
            return loc_id, loc_data
    
    # If no default is set, use the first location
    first_loc = next(iter(config['locations'].items()))
    loc_id, loc_data = first_loc
    
    # Validate first location too
    if 'latitude' not in loc_data or 'longitude' not in loc_data:
        raise ValueError(f"Location {loc_id} missing latitude or longitude")
    if not -90 <= loc_data['latitude'] <= 90:
        raise ValueError(f"Invalid latitude for {loc_id}: {loc_data['latitude']}")
    if not -180 <= loc_data['longitude'] <= 180:
        raise ValueError(f"Invalid longitude for {loc_id}: {loc_data['longitude']}")
    
    return first_loc


# Load configuration
CONFIG = load_config()
DEFAULT_LOCATION_ID, DEFAULT_LOCATION = get_default_location(CONFIG)

# ============= GLOBAL CONFIGURATION =============

# Location Configuration
LATITUDE = DEFAULT_LOCATION['latitude']
LONGITUDE = DEFAULT_LOCATION['longitude']
TIMEZONE = DEFAULT_LOCATION['timezone']

# Get elevation if available, default to 0
ELEVATION = DEFAULT_LOCATION.get('elevation', 0.0)

# Create observer object with elevation support
OBSERVER = Observer(LATITUDE, LONGITUDE, ELEVATION)

# Visibility Constraints
MIN_ALT = DEFAULT_LOCATION['min_altitude']
MAX_ALT = DEFAULT_LOCATION['max_altitude']
MIN_AZ = DEFAULT_LOCATION['min_azimuth']
MAX_AZ = DEFAULT_LOCATION['max_azimuth']

# Location-specific settings
BORTLE_INDEX = DEFAULT_LOCATION['bortle_index']

# Catalog selection
USE_CSV_CATALOG = CONFIG['catalog']['use_csv_catalog']
CATALOGNAME = CONFIG['catalog']['catalog_name']
MERGING_CATALOGS = CONFIG['catalog']['merge']

# Time & Visibility Configuration
MIN_VISIBILITY_HOURS = CONFIG['visibility']['min_visibility_hours']
MIN_TOTAL_AREA = CONFIG['visibility']['min_total_area']
TRAJECTORY_INTERVAL_MINUTES = CONFIG['visibility']['trajectory_interval_minutes']
SEARCH_INTERVAL_MINUTES = CONFIG['visibility']['search_interval_minutes']

# Scheduling Configuration
SCHEDULING_STRATEGY = SchedulingStrategy[CONFIG['scheduling']['strategy'].upper()]
MAX_OVERLAP_MINUTES = CONFIG['scheduling']['max_overlap_minutes']

# Visibility Filtering
EXCLUDE_INSUFFICIENT_TIME = CONFIG['scheduling']['exclude_insufficient_time']

# Imaging Configuration - Load from default scope in scope_data.json
def _get_default_scope_config():
    """Get default scope configuration from scope_data.json"""
    try:
        # Load scope_data.json directly to avoid circular imports
        import json
        import os
        
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scope_data_path = os.path.join(current_dir, 'scope_data.json')
        
        with open(scope_data_path, 'r') as f:
            scope_data = json.load(f)
        
        # Find the default scope
        for scope_id, data in scope_data.items():
            if data.get('default', False):
                return {
                    'name': data['name'],
                    'fov_width': data['native_fov_deg'][0],
                    'fov_height': data['native_fov_deg'][1],
                    'mosaic_fov_width': data['mosaic_fov_deg'][0],
                    'mosaic_fov_height': data['mosaic_fov_deg'][1],
                    'pixel_size': data['pixel_size_um'],
                    'focal_length': data['focal_length_mm'],
                    'aperture': data['aperture_mm'],
                    'sensor_model': data['sensor_model'],
                    'resolution_mp': data['resolution_mp']
                }
        
        # If no default found, use first scope
        if scope_data:
            first_scope = next(iter(scope_data.values()))
            return {
                'name': first_scope['name'],
                'fov_width': first_scope['native_fov_deg'][0],
                'fov_height': first_scope['native_fov_deg'][1],
                'mosaic_fov_width': first_scope['mosaic_fov_deg'][0],
                'mosaic_fov_height': first_scope['mosaic_fov_deg'][1],
                'pixel_size': first_scope['pixel_size_um'],
                'focal_length': first_scope['focal_length_mm'],
                'aperture': first_scope['aperture_mm'],
                'sensor_model': first_scope['sensor_model'],
                'resolution_mp': first_scope['resolution_mp']
            }
            
    except Exception as e:
        print(f"Warning: Could not load default scope configuration: {e}")
    
    # Fallback configuration if scope loading fails
    return {
        'name': 'Vespera Passenger',
        'fov_width': 1.6,
        'fov_height': 1.6,
        'mosaic_fov_width': 4.18,
        'mosaic_fov_height': 2.45,
        'pixel_size': 2.0,
        'focal_length': 200,
        'aperture': 50,
        'sensor_model': 'Sony IMX678',
        'resolution_mp': 12.5
    }

# Load default scope configuration
DEFAULT_SCOPE_CONFIG = _get_default_scope_config()

# Scope specifications from default scope
SCOPE_FOV_WIDTH = DEFAULT_SCOPE_CONFIG['fov_width']
SCOPE_FOV_HEIGHT = DEFAULT_SCOPE_CONFIG['fov_height']
SCOPE_FOV_AREA = SCOPE_FOV_WIDTH * SCOPE_FOV_HEIGHT  # square degrees
PIXEL_SIZE = DEFAULT_SCOPE_CONFIG['pixel_size']
FOCAL_LENGTH = DEFAULT_SCOPE_CONFIG['focal_length']
APERTURE = DEFAULT_SCOPE_CONFIG['aperture']
SCOPE_NAME = DEFAULT_SCOPE_CONFIG['name']

# Default imaging parameters (these could be moved to a separate config section)
SINGLE_EXPOSURE = 10  # seconds
MIN_SNR = 20
GAIN = 800
READ_NOISE = 0.8

# Plot Configuration
MAX_OBJECTS_OPTIMAL = CONFIG['plotting']['max_objects_optimal']
FIGURE_SIZE = tuple(CONFIG['plotting']['figure_size'])
COLOR_MAP = CONFIG['plotting']['color_map']
GRID_ALPHA = CONFIG['plotting']['grid_alpha']
VISIBLE_REGION_ALPHA = CONFIG['plotting']['visible_region_alpha']

# Moon Configuration
MOON_PROXIMITY_RADIUS = CONFIG['moon']['proximity_radius']
MOON_TRAJECTORY_COLOR = CONFIG['moon']['trajectory_color']
MOON_MARKER_COLOR = CONFIG['moon']['marker_color']
MOON_LINE_WIDTH = CONFIG['moon']['line_width']
MOON_MARKER_SIZE = CONFIG['moon']['marker_size']
MOON_INTERFERENCE_COLOR = CONFIG['moon']['interference_color']

# Mosaic Configuration
MOSAIC_FOV_WIDTH = DEFAULT_SCOPE_CONFIG['mosaic_fov_width']
MOSAIC_FOV_HEIGHT = DEFAULT_SCOPE_CONFIG['mosaic_fov_height']

# Mosaic analysis functions will be imported dynamically to avoid circular imports
MOSAIC_ANALYSIS_AVAILABLE = True
MOSAIC_ENABLED = True  # Enable mosaic functionality


def _import_mosaic_functions():
    """Dynamically import mosaic analysis functions to avoid circular imports"""
    try:
        from utilities.analyze_mosaic_groups import (
            analyze_object_groups, calculate_angular_separation, 
            can_fit_in_mosaic, objects_visible_simultaneously
        )
        return analyze_object_groups, calculate_angular_separation, can_fit_in_mosaic, objects_visible_simultaneously
    except ImportError as e:
        print(f"Warning: Mosaic analysis module not available: {e}")
        return None, None, None, None 
