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
    """Get the default location from config"""
    for loc_id, loc_data in config['locations'].items():
        if loc_data.get('default', False):
            return loc_id, loc_data
    # If no default is set, use the first location
    first_loc = next(iter(config['locations'].items()))
    return first_loc


# Load configuration
CONFIG = load_config()
DEFAULT_LOCATION_ID, DEFAULT_LOCATION = get_default_location(CONFIG)

# ============= GLOBAL CONFIGURATION =============

# Location Configuration
LATITUDE = DEFAULT_LOCATION['latitude']
LONGITUDE = DEFAULT_LOCATION['longitude']
TIMEZONE = DEFAULT_LOCATION['timezone']

# Create observer object
OBSERVER = Observer(LATITUDE, LONGITUDE)

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

# Imaging Configuration
# Vespera Passenger Specifications
SCOPE_FOV_WIDTH = CONFIG['imaging']['scope']['fov_width']
SCOPE_FOV_HEIGHT = CONFIG['imaging']['scope']['fov_height']
SCOPE_FOV_AREA = SCOPE_FOV_WIDTH * SCOPE_FOV_HEIGHT  # square degrees
SINGLE_EXPOSURE = CONFIG['imaging']['scope']['single_exposure']
MIN_SNR = CONFIG['imaging']['scope']['min_snr']
GAIN = CONFIG['imaging']['scope']['gain']
READ_NOISE = CONFIG['imaging']['scope']['read_noise']
PIXEL_SIZE = CONFIG['imaging']['scope']['pixel_size']
FOCAL_LENGTH = CONFIG['imaging']['scope']['focal_length']
APERTURE = CONFIG['imaging']['scope']['aperture']

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
MOSAIC_FOV_WIDTH = CONFIG['imaging']['scope']['mosaic_fov_width']
MOSAIC_FOV_HEIGHT = CONFIG['imaging']['scope']['mosaic_fov_height']
SCOPE_NAME = CONFIG['imaging']['scope']['name']

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