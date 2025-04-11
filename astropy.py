import math
import numpy as np
from datetime import datetime, timedelta, timezone

import pytz
import re
import json

import csv

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

from enum import Enum
import argparse

class SchedulingStrategy(Enum):
    LONGEST_DURATION = "longest_duration"  # Current strategy: prioritize longest visibility
    MAX_OBJECTS = "max_objects"           # Maximum number of objects
    OPTIMAL_SNR = "optimal_snr"           # Best imaging conditions
    #MINIMAL_MOSAIC = "minimal_mosaic"     # Fewer panels needed
    #DIFFICULTY_BALANCED = "difficulty_balanced"  # Mix of easy and challenging

# Load configuration from file
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_default_location(config):
    """Get the default location from config"""
    for loc_id, loc_data in config['locations'].items():
        if loc_data.get('default', False):
            return loc_id, loc_data
    # If no default is set, use the first location
    first_loc = next(iter(config['locations'].items()))
    return first_loc

CONFIG = load_config()
DEFAULT_LOCATION_ID, DEFAULT_LOCATION = get_default_location(CONFIG)

# ============= GLOBAL CONFIGURATION =============

# Location Configuration
LATITUDE = DEFAULT_LOCATION['latitude']
LONGITUDE = DEFAULT_LOCATION['longitude']
TIMEZONE = DEFAULT_LOCATION['timezone']

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

# ============ DEEP SKY CATALOG FUNCTIONS =============

def get_messier_catalog():
    """Complete Messier Catalog with coordinates, FOV, and magnitudes"""
    return [
        # Nebulae
        CelestialObject("M1/NGC 1952 Crab Nebula", 5.575, 22.017, "6'x4'", 8.4),
        CelestialObject("M8/NGC 6523 Lagoon Nebula", 18.063, -24.383, "90'x40'", 6.0),
        CelestialObject("M16/NGC 6611 Eagle Nebula", 18.313, -13.783, "35'x28'", 6.4),
        CelestialObject("M17/NGC 6618 Omega - Swan Nebula", 18.346, -16.183, "46'x37'", 6.0),
        CelestialObject("M20/NGC 6514 Trifid Nebula", 18.033, -23.033, "28'x28'", 6.3),
        CelestialObject("M27/NGC 6853 Dumbbell Nebula", 19.994, 22.717, "8.0'x5.7'", 7.5),
        CelestialObject("M42/NGC 1976 Great Orion Nebula", 5.588, -5.391, "85'x60'", 4.0),
        CelestialObject("M43/NGC 1982 De Mairan's Nebula", 5.593, -5.267, "20'x15'", 9.0),
        CelestialObject("M57/NGC 6720 Ring Nebula", 18.884, 33.033, "1.4'x1'", 8.8),
        CelestialObject("M76/NGC 650/651 Little Dumbbell Nebula", 1.702, 51.567, "2.7'x1.8'", 10.1),
        CelestialObject("M97/NGC 3587 Owl Nebula", 11.248, 55.017, "3.4'x3.3'", 9.9),

        # Galaxies
        CelestialObject("M31/NGC 224 Andromeda Galaxy", 0.712, 41.269, "178'x63'", 3.4),
        CelestialObject("M32/NGC 221 Andromeda Companion", 0.712, 40.867, "8'x6'", 8.1),
        CelestialObject("M33/NGC 598 Triangulum Galaxy", 1.564, 30.660, "73'x45'", 5.7),
        CelestialObject("M51/NGC 5194 Whirlpool Galaxy", 13.497, 47.195, "11'x7'", 8.4),
        CelestialObject("M63/NGC 5055 Sunflower Galaxy", 13.158, 42.033, "12.6'x7.2'", 8.6),
        CelestialObject("M64/NGC 4826 Black Eye Galaxy", 12.944, 21.683, "10'x5'", 8.5),
        CelestialObject("M81/NGC 3031 Bode's Galaxy", 9.926, 69.067, "26.9'x14.1'", 6.9),
        CelestialObject("M82/NGC 3034 Cigar Galaxy", 9.928, 69.683, "11.2'x4.3'", 8.4),
        CelestialObject("M101/NGC 5457 Pinwheel Galaxy", 14.053, 54.349, "28.8'x26.9'", 7.9),
        CelestialObject("M104/NGC 4594 Sombrero Galaxy", 12.667, -11.617, "8.7'x3.5'", 8.0),
        CelestialObject("M106/NGC 4258", 12.317, 47.300, "18.6'x7.2'", 8.4),
        CelestialObject("M110/NGC 205", 0.683, 41.683, "17'x10'", 8.0),

        # Globular Clusters
        CelestialObject("M2/NGC 7089", 21.558, -0.817, "12.9'x12.9'", 6.5),
        CelestialObject("M3/NGC 5272", 13.703, 28.383, "16.2'x16.2'", 6.2),
        CelestialObject("M4/NGC 6121", 16.392, -26.533, "26.3'x26.3'", 5.6),
        CelestialObject("M5/NGC 5904", 15.310, 2.083, "17.4'x17.4'", 5.6),
        CelestialObject("M10/NGC 6254", 16.950, -4.100, "15.1'x15.1'", 6.6),
        CelestialObject("M13/NGC 6205 Great Hercules Cluster", 16.695, 36.459, "20'x20'", 5.8),
        CelestialObject("M15/NGC 7078", 21.500, 12.167, "12.3'x12.3'", 6.2),
        CelestialObject("M22/NGC 6656", 18.608, -23.900, "24'x24'", 5.1),
        CelestialObject("M55/NGC 6809", 19.667, -30.967, "19'x19'", 7.0),
        CelestialObject("M92/NGC 6341", 17.171, 43.133, "11.2'x11.2'", 6.4),

        # Open Clusters
        CelestialObject("M6/NGC 6405 Butterfly Cluster", 17.667, -32.217, "25'x15'", 4.2),
        CelestialObject("M7/NGC 6475 Ptolemy Cluster", 17.897, -34.817, "80'x80'", 3.3),
        CelestialObject("M23/NGC 6494", 17.950, -19.017, "27'x27'", 5.5),
        CelestialObject("M24/NGC 6603", 18.283, -18.517, "90'x90'", 4.6),
        CelestialObject("M25/IC 4725", 18.528, -19.233, "32'x32'", 4.6),
        CelestialObject("M34/NGC 1039", 2.702, 42.783, "35'x35'", 5.2),
        CelestialObject("M35/NGC 2168", 6.148, 24.333, "28'x28'", 5.1),
        CelestialObject("M36/NGC 1960 Pinwheel Cluster", 5.536, 34.133, "12'x12'", 6.0),
        CelestialObject("M37/NGC 2099 Salt and Pepper Cluster", 5.873, 32.550, "24'x24'", 5.6),
        CelestialObject("M38/NGC 1912 Starfish Cluster", 5.478, 35.833, "21'x21'", 6.4),
        CelestialObject("M39/NGC 7092", 21.535, 48.433, "32'x32'", 4.6),
        CelestialObject("M41/NGC 2287", 6.783, -20.733, "38'x38'", 4.5),
        CelestialObject("M44/NGC 2632 Beehive Cluster/Praesepe", 8.667, 19.983, "95'x95'", 3.1),
        CelestialObject("M45 Pleiades - Seven Sisters", 3.790, 24.117, "110'x110'", 1.6),
        CelestialObject("M46/NGC 2437", 7.697, -14.817, "27'x27'", 6.1),
        CelestialObject("M47/NGC 2422", 7.615, -14.483, "30'x30'", 4.4),
        CelestialObject("M48/NGC 2548", 8.233, -5.800, "54'x54'", 5.8),
        CelestialObject("M50/NGC 2323 Heart-Shaped Cluster", 7.033, -8.333, "16'x16'", 5.9),
        CelestialObject("M67/NGC 2682", 8.850, 11.817, "30'x30'", 6.9),
        CelestialObject("M93/NGC 2447", 7.742, -23.867, "22'x22'", 6.2),
    ]

def get_additional_dso():
    """Additional major deep sky objects beyond Messier catalog with magnitudes"""
    return [
        # Large/Emission Nebulae
        CelestialObject("NGC 7000/C20 North America Nebula", 20.968, 44.533, "120'x100'", 4.0),
        CelestialObject("NGC 6960/C34 Western Veil - Witch's Broom Nebula", 20.764, 30.711, "70'x6'", 7.0),
        CelestialObject("NGC 6992/C33 Eastern Veil - Network Nebula", 20.917, 31.717, "75'x12'", 7.0),
        CelestialObject("NGC 1499/C31 California Nebula", 4.033, 36.417, "145'x40'", 5.0),
        CelestialObject("IC 5070/C19 Pelican Nebula", 20.785, 44.357, "60'x50'", 8.0),
        CelestialObject("NGC 2237/C49 Rosette Nebula", 6.533, 4.950, "80'x80'", 6.0),
        CelestialObject("IC 1396 Elephant's Trunk Nebula", 21.619, 57.500, "170'x140'", 7.5),
        CelestialObject("IC 1805/C31 Heart Nebula", 2.567, 61.833, "100'x100'", 6.5),
        CelestialObject("NGC 2264/C41 Cone Nebula - Christmas Tree Cluster", 6.691, 9.890, "20'x10'", 7.2),
        CelestialObject("IC 2118 Witch Head Nebula", 5.417, -7.233, "180'x60'", 13.0),
        CelestialObject("NGC 7293/C63 Helix Nebula", 22.493, -20.837, "28'x23'", 7.6),
        CelestialObject("IC 434/B33 Horsehead Nebula", 5.683, -2.450, "60'x10'", 6.8),
        CelestialObject("NGC 6888/C27 Crescent Nebula", 20.192, 38.356, "25'x18'", 7.4),
        CelestialObject("NGC 2359/C46 Thor's Helmet", 7.250, -13.200, "22'x15'", 11.5),
        CelestialObject("NGC 6302/C69 Bug Nebula", 17.139, -37.097, "12.9'x6.2'", 12.8),
        CelestialObject("IC 1318 Butterfly - Gamma Cygni Nebula", 20.183, 40.250, "180'x180'", 7.0),
        CelestialObject("IC 2177 Seagull Nebula", 7.067, -10.700, "120'x30'", None),
        CelestialObject("IC 4628 Prawn Nebula", 16.567, -40.333, "60'x35'", None),
        CelestialObject("NGC 2024 Flame Nebula", 5.417, -1.850, "30'x30'", None),
        CelestialObject("NGC 2070 Tarantula Nebula", 5.642, -69.100, "40'x25'", 8.0),
        CelestialObject("NGC 2467 Skull and Crossbones Nebula", 7.583, -26.433, "15'x15'", None),
        CelestialObject("NGC 3576 Statue of Liberty Nebula", 11.167, -61.317, "4'x4'", None),
        CelestialObject("NGC 6357 Lobster - War and Peace Nebula", 17.475, -34.200, "40'x30'", None),
        CelestialObject("NGC 2736 Pencil Nebula", 9.050, -45.950, "20'x0.5'", None),

        # Reflection Nebulae
        CelestialObject("IC 405 Flaming Star Nebula", 5.167, 34.250, "30'x19'", 6.0),
        CelestialObject("IC 4592 Blue Horsehead Nebula", 16.117, -19.617, "50'x30'", None),
        CelestialObject("NGC 1977 Running Man Nebula", 5.583, -4.867, "20'x10'", None),
        
        # Notable Galaxies
        CelestialObject("NGC 253/C65 Sculptor Galaxy - Silver Dollar Galaxy", 0.793, -25.288, "27'x7'", 7.1),
        CelestialObject("NGC 891/C23 Silver Sliver Galaxy", 2.375, 42.349, "13.5'x2.8'", 10.0),
        CelestialObject("NGC 4565/C38 Needle Galaxy", 12.536, 25.988, "15.8'x2.1'", 10.4),
        CelestialObject("NGC 4631/C32 Whale Galaxy", 12.717, 32.542, "15.5'x2.7'", 9.2),
        CelestialObject("NGC 5907 Splinter Galaxy - Knife Edge Galaxy", 15.268, 56.329, "12.8'x1.4'", 10.3),
        CelestialObject("NGC 6946/C12 Fireworks Galaxy", 20.578, 60.154, "11.5'x9.8'", 9.6),
        CelestialObject("NGC 5128/C77 Centaurus A", 13.425, -43.017, "25.7'x20'", 6.8),
        CelestialObject("NGC 4656 Hockey Stick Galaxy", 12.733, 32.167, "15'x3'", 10.5),
        CelestialObject("IC 342 Hidden Galaxy", 3.467, 68.100, "21.4'x20.9'", 9.1),
        CelestialObject("NGC 1316 Fornax A", 3.378, -37.208, "12'x8.5'", 8.2),
        CelestialObject("NGC 292 Small Magellanic Cloud", 0.867, -72.833, "280'x160'", 2.7),
        CelestialObject("NGC 4244 Silver Needle Galaxy", 12.317, 37.817, "16.6'x1.9'", 10.6),
        
        # Notable Star Clusters
        CelestialObject("NGC 869/C14 Perseus Double Cluster h", 2.327, 57.133, "30'x30'", 4.3),
        CelestialObject("NGC 884/C14 Perseus Double Cluster χ", 2.351, 57.133, "30'x30'", 4.4),
        CelestialObject("NGC 663/C10", 1.766, 61.233, "16'x16'", 7.1),
        CelestialObject("IC 4665 Summer Beehive Cluster", 17.725, 5.633, "70'x70'", 4.2),
        CelestialObject("NGC 752/C28 Butterfly Cluster", 1.958, 37.667, "50'x50'", 5.7),
        CelestialObject("Melotte25 Hyades Cluster", 4.283, 15.867, "330'x330'", 0.5),
        CelestialObject("NGC 2281 Broken Heart Cluster", 6.817, 41.083, "14'x14'", 5.4),
        CelestialObject("NGC 1502/C13 Jolly Roger Cluster", 4.078, 62.333, "8'x8'", 6.9),
        CelestialObject("Stock2 Muscle Man Cluster", 2.150, 59.483, "60'x60'", 4.4),
        CelestialObject("Melotte111 Coma Star Cluster", 12.367, 26.000, "275'x275'", 1.8),
        CelestialObject("Collinder399 Coathanger/Brocchi's Cluster", 19.433, 20.183, "60'x60'", 3.6),
        CelestialObject("IC 2391 Omicron Velorum Cluster", 8.667, -53.067, "50'x50'", 2.5),
        CelestialObject("NGC 104 47 Tucanae", 0.400, -72.067, "30.9'x30.9'", 4.0),
        CelestialObject("NGC 2516 Southern Beehive", 7.967, -60.867, "30'x30'", 3.8),
        CelestialObject("NGC 3766 Pearl Cluster", 11.600, -61.617, "12'x12'", 5.3),
        CelestialObject("NGC 457 Owl/ET Cluster", 1.317, 58.283, "13'x13'", 6.4),
        CelestialObject("NGC 5139 Omega Centauri", 13.447, -47.483, "36.3'x36.3'", 3.7),
        CelestialObject("NGC 7789 White Rose - Caroline's Rose", 23.957, 56.717, "25'x25'", 6.7),
        
        # Additional Notable Objects
        CelestialObject("NGC 7635/C11 Bubble Nebula", 23.333, 61.200, "15'x8'", 11.0),
        CelestialObject("IC 5146/C19 Cocoon Nebula", 21.883, 47.267, "10'x10'", 7.2),
        CelestialObject("NGC 7023/C4 Iris Nebula", 21.017, 68.167, "18'x18'", 6.8),
        CelestialObject("IC 1848 Soul Nebula", 2.983, 60.433, "80'x80'", 6.5),
        CelestialObject("NGC 281/C11 Pacman Nebula", 0.785, 56.633, "35'x30'", 7.4),
        CelestialObject("NGC 6334/C6 Cat's Paw Nebula", 17.292, -35.683, "40'x20'", 5.5),
        CelestialObject("IC 443 Jellyfish Nebula", 6.175, 22.567, "50'x50'", None),
        CelestialObject("NGC 3372/C92 Eta Carinae Nebula", 10.733, -59.867, "120'x120'", 3.0),
        CelestialObject("NGC 3532/C91 Wishing Well Cluster", 11.100, -58.733, "55'x55'", 3.0),
        CelestialObject("IC 2602/C102 Southern Pleiades", 10.717, -64.400, "100'x100'", 1.9),
        CelestialObject("NGC 6231/C76 Northern Jewel Box", 16.900, -41.833, "15'x15'", 2.6),
        
        # Sharpless Catalog Objects
        CelestialObject("SH2-101", 19.920, 40.517, "15'x15'", None),
        CelestialObject("SH2-106", 20.333, 37.433, "4'x3'", None),
        CelestialObject("SH2-140", 22.317, 63.183, "5'x5'", None),
        CelestialObject("SH2-155", 22.583, 62.467, "50'x10'", None),
        CelestialObject("SH2-170", 0.100, 65.783, "20'x15'", None),
        CelestialObject("SH2-302", 7.167, -18.517, "40'x40'", None),
    ]
    
def get_combined_catalog():
    """Get combined catalog of all objects"""
    messier = get_messier_catalog()
    additional = get_additional_dso()
    return messier + additional

def enrich_object_name(name):
    """Add common names and cross-references to object names"""    
    common_names = {}
    
    # Process Messier catalog
    for obj in get_messier_catalog():
        designations = obj.name.split('/')
        # Get the common name by taking everything after the last catalog designation
        full_name = designations[-1]
        parts = full_name.split(' ')
        # Skip the catalog designation (like 'NGC 1976') to get only the common name
        if parts[0] in ['NGC', 'IC']:
            common_name = ' '.join(parts[2:])  # Skip both NGC/IC and the number
        else:
            common_name = ' '.join(parts[1:])  # Skip just the first part
            
        # Add entry for each designation
        for designation in designations:
            designation = designation.split()[0]  # Get just the catalog number
            if common_name:
                common_names[designation] = common_name

    # Process additional DSO catalog
    for obj in get_additional_dso():
        designations = obj.name.split('/')
        full_name = designations[-1]
        parts = full_name.split(' ')
        # Skip the catalog designation to get only the common name
        if parts[0] in ['NGC', 'IC', 'C']:
            common_name = ' '.join(parts[2:])  # Skip both NGC/IC/C and the number
        elif parts[0].startswith('SH2-'):  # Handle SH2 format
            common_name = ' '.join(parts[1:])  # Skip the SH2-nnn part
        else:
            common_name = ' '.join(parts[1:])  # Skip just the first part
            
        # Add entry for each designation
        for designation in designations:
            if designation.strip().startswith(('NGC', 'IC')):
                designation = ' '.join(designation.split()[:2])
            elif designation.strip().startswith('SH2-'):  # Keep full SH2-nnn format
                designation = designation.strip()
            else:
                designation = designation.split()[0]
            if common_name:
                common_names[designation] = common_name

    # Try all possible designations from the input name
    input_designations = name.split('/')
    common_name = ''
    
    for designation in input_designations:
        designation = designation.strip()
        if ' or ' in designation:
            designation = designation.split(' or ')[0].strip()
            
        # Try exact match first
        if designation in common_names:
            common_name = common_names[designation]
            break
            
        # Try with just the catalog number for NGC/IC objects
        if designation.startswith(('NGC', 'IC')):
            catalog_id = ' '.join(designation.split()[:2])
            if catalog_id in common_names:
                common_name = common_names[catalog_id]
                break

    if common_name and common_name not in name:
        return f"{name} ({common_name})"
    
    return name
    
def filter_visible_objects(objects, min_alt=MIN_ALT, max_alt=MAX_ALT, min_az=MIN_AZ, max_az=MAX_AZ):
    """Filter objects based on visibility constraints"""
    visible_objects = []
    current_time = datetime.now(get_local_timezone())
    
    for obj in objects:
        alt, az = calculate_altaz(obj, current_time)
        if min_alt <= alt <= max_alt and min_az <= az <= max_az:
            visible_objects.append(obj)
    
    return visible_objects

def get_object_by_name(name, catalog=None):
    """Find object in catalog by name"""
    if catalog is None:
        catalog = get_combined_catalog()
    
    for obj in catalog:
        if obj.name.lower().startswith(name.lower()):
            return obj
    return None

def get_objects_by_type(obj_type, catalog=None):
    """Get objects of specific type from catalog"""
    if catalog is None:
        catalog = get_combined_catalog()
    
    type_keywords = {
        'galaxy': ['galaxy', 'galaxies'],
        'nebula': ['nebula', 'nebulae'],
        'cluster': ['cluster'],
        'globular': ['globular'],
        'open': ['open cluster'],
        'planetary': ['planetary']
    }
    
    keywords = type_keywords.get(obj_type.lower(), [])
    return [obj for obj in catalog 
            if any(keyword.lower() in obj.name.lower() 
                  for keyword in keywords)]

def sort_objects_by_size(objects):
    """Sort objects by apparent size (FOV area)"""
    return sorted(objects, key=lambda x: x.total_area, reverse=True)

def sort_objects_by_altitude(objects, time=None):
    """Sort objects by current altitude"""
    if time is None:
        time = datetime.now(get_local_timezone())
    
    def get_altitude(obj):
        alt, _ = calculate_altaz(obj, time)
        return alt
    
    return sorted(objects, key=get_altitude, reverse=True)

# ============= CSV MANAGEMENT FUNCTIONS =============

def get_object_type(type_str):
    """Categorize object type from CSV string"""
    type_str = type_str.lower()
    
    if 'neb' in type_str:
        if 'em neb' in type_str:
            return 'emission_nebula'
        elif 'ref neb' in type_str:
            return 'reflection_nebula'
        elif 'pl neb' in type_str or 'pi neb' in type_str:
            return 'planetary_nebula'
        else:
            return 'nebula'
    elif 'galaxy' in type_str:
        return 'galaxy'
    elif 'glob' in type_str:
        return 'globular_cluster'
    elif 'open' in type_str or 'cl' in type_str:
        return 'open_cluster'
    elif 'dark' in type_str:
        return 'dark_nebula'
    else:
        return 'other'

def normalize_object_name(name):
    """
    Normalize object name for comparison by extracting catalog prefix and number.
    Example: 'NGC 6888 (Crescent Nebula)' -> ('ngc', '6888')
    """
    # Remove spaces, parentheses, and dashes, convert to lowercase
    name = name.lower()
    name = re.sub(r'[\s\(\)\-]', '', name)
    
    # Match catalog prefix and number
    # Handle special cases like 'M31', 'IC1318', 'NGC6888', 'SH101', etc.
    patterns = [
        r'^(ngc)(\d+)',    # NGC cases
        r'^(ic)(\d+)',     # IC cases
        r'^(m)(\d+)',      # Messier cases
        r'^(sh)(\d+)',     # SH cases
        r'^(collinder)(\d+)',  # Collinder cases
        r'^(melotte)(\d+)',    # Melotte cases
        r'^(barnard)(\d+)',    # Barnard cases
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            prefix, number = match.groups()
            return (prefix, number)
    
    # If no standard pattern matches, return the whole string
    return (name, '')

def are_same_object(name1, name2):
    """Compare two object names to determine if they refer to the same object"""
    # Split names by '/' to handle multiple designations
    names1 = name1.split('/')
    names2 = name2.split('/')
    
    # Normalize each name part
    norm_names1 = [normalize_object_name(n.strip()) for n in names1]
    norm_names2 = [normalize_object_name(n.strip()) for n in names2]
    
    # Check if any normalized names match (just prefix and number)
    return any(n1 == n2 and n1[0] != '' and n1[1] != '' 
              for n1 in norm_names1 for n2 in norm_names2)

def merge_catalogs(csv_objects, builtin_objects):
    """Merge CSV and built-in catalogs, preferring CSV entries for duplicates"""
    merged = []
    used_builtin = set()
    
    # First add all CSV objects
    merged.extend(csv_objects)
    
    # Add non-duplicate built-in objects
    for builtin_obj in builtin_objects:
        is_duplicate = False
        for csv_obj in csv_objects:
            if are_same_object(builtin_obj.name, csv_obj.name):
                is_duplicate = True
                break
        if not is_duplicate:
            merged.append(builtin_obj)
    
    return merged

def get_objects_from_csv():
    """Read objects from CSV file and organize by type"""
    objects_by_type = {
        'emission_nebula': [],
        'reflection_nebula': [],
        'planetary_nebula': [],
        'nebula': [],
        'galaxy': [],
        'globular_cluster': [],
        'open_cluster': [],
        'dark_nebula': [],
        'other': []
    }
    
    print(f"Catalog config: {CONFIG['catalog']}")  # Debug print
    print(f"Merge flag value: {CONFIG['catalog'].get('merge', False)}")  # Debug print
    
    csv_objects = []
    try:
        with open(CATALOGNAME, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Extract primary name before any dash
                full_name = row['Object'].strip()
                original_name = full_name.split('-')[0].strip()
                enriched_name = enrich_object_name(original_name)
                
                # Parse coordinates
                ra_str = row['RA'].strip()
                dec_str = row['Dec'].strip()
                ra_deg = parse_ra(ra_str)
                dec_deg = parse_dec(dec_str)
                
                # Parse FOV and calculate area
                fov = row.get('FOV', '').strip()

                # Parse magnitude if available
                magnitude = row.get('Magnitude', '').strip()
                if magnitude == '-':
                    magnitude = 10.0
                else:
                    magnitude = float(magnitude)
                
                # Create object
                obj = CelestialObject(enriched_name, ra_deg/15, dec_deg, fov, magnitude)
                
                # Add comments if available
                if 'Comments' in row and row['Comments'].strip():
                    obj.comments = row['Comments'].strip()
                
                # Only add objects that meet the area threshold
                if obj.total_area >= MIN_TOTAL_AREA or not fov:
                    # Categorize object by type
                    obj_type = get_object_type(row['Type'])
                    objects_by_type[obj_type].append(obj)
                    csv_objects.append(obj)  # Keep track of successfully parsed objects
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        # Don't return immediately, continue with merging if enabled
    
    print(f"CSV objects found: {len(csv_objects)}")  # Debug print
    
    # If merge is enabled or CSV read failed, get built-in catalog
    merge_enabled = MERGING_CATALOGS
    print(f"Merge enabled: {merge_enabled}")  # Debug print
    
    if merge_enabled or not csv_objects:
        print("Getting built-in catalog")
        builtin_objects = get_combined_catalog()
        
        if merge_enabled and csv_objects:
            print(f"Merging {len(csv_objects)} CSV objects with {len(builtin_objects)} built-in objects")
            return merge_catalogs(csv_objects, builtin_objects)
        else:
            print("Using built-in catalog only")
            return builtin_objects
    
    # If we have CSV objects and merge is not enabled, return just those
    print(f"Using {len(csv_objects)} CSV objects only")
    return csv_objects

# ======== TIME CONVERSION FUNCTIONS =============

def get_local_timezone():
    """Get configured timezone"""
    return pytz.timezone('Europe/Rome')

def local_to_utc(local_time):
    """Convert local time to UTC"""
    milan_tz = get_local_timezone()
    if local_time.tzinfo is None:
        local_time = milan_tz.localize(local_time)
    return local_time.astimezone(pytz.UTC)

def utc_to_local(utc_time):
    """Convert UTC time to local time"""
    milan_tz = get_local_timezone()
    if utc_time.tzinfo is None:
        utc_time = pytz.UTC.localize(utc_time)
    return utc_time.astimezone(milan_tz)

def calculate_julian_date(dt):
    """Calculate Julian Date from datetime (UTC)"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    year, month, day = dt.year, dt.month, dt.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + (a // 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    jd += (dt.hour + dt.minute/60 + dt.second/3600)/24.0
    return jd

# ============= COORDINATE CONVERSION FUNCTIONS =============

def dms_dd(degrees, minutes, seconds):
    """Convert Degrees Minutes Seconds to Decimal Degrees"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(degrees) + B
    return -C if degrees < 0 or minutes < 0 or seconds < 0 else C

def dd_dh(decimal_degrees):
    """Convert Decimal Degrees to Degree-Hours"""
    return decimal_degrees / 15

def dh_dd(degree_hours):
    """Convert Degree-Hours to Decimal Degrees"""
    return degree_hours * 15

def hms_dh(hours, minutes, seconds):
    """Convert Hours Minutes Seconds to Decimal Hours"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(hours) + B
    return -C if hours < 0 or minutes < 0 or seconds < 0 else C

def dh_hour(decimal_hours):
    """Return hour part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return -(math.floor(E / 3600)) if decimal_hours < 0 else math.floor(E / 3600)

def dh_min(decimal_hours):
    """Return minutes part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return math.floor(E / 60) % 60

def dh_sec(decimal_hours):
    """Return seconds part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    return 0 if C == 60 else C

# ============= ASTRONOMICAL CALCULATIONS =============

def calculate_lst(dt):
    """Calculate Local Sidereal Time in radians"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    jd = calculate_julian_date(dt)
    t = (jd - 2451545.0) / 36525
    
    gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3/38710000
    gst = math.radians(gst % 360)
    
    lst = gst + OBSERVER.lon
    return lst % (2 * math.pi)

def calculate_sun_position(dt):
    """Calculate Sun's position (altitude, azimuth)"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    n = jd - 2451545.0
    
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    
    lambda_sun = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    
    epsilon = math.radians(23.439 - 0.0000004 * n)
    
    ra = math.atan2(math.cos(epsilon) * math.sin(lambda_sun), math.cos(lambda_sun))
    dec = math.asin(math.sin(epsilon) * math.sin(lambda_sun))
    
    ha = calculate_lst(dt) - ra
    
    sin_alt = (math.sin(dec) * math.sin(OBSERVER.lat) + 
               math.cos(dec) * math.cos(OBSERVER.lat) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    cos_az = (math.sin(dec) - math.sin(alt) * math.sin(OBSERVER.lat)) / (
              math.cos(alt) * math.cos(OBSERVER.lat))
    cos_az = min(1, max(-1, cos_az))
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
        
    return math.degrees(alt), math.degrees(az)

def calculate_altaz(obj, dt):
    """Calculate altitude and azimuth for an object"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    lst = calculate_lst(dt)
    ha = lst - obj.ra
    
    sin_alt = (math.sin(obj.dec) * math.sin(OBSERVER.lat) + 
               math.cos(obj.dec) * math.cos(OBSERVER.lat) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    cos_az = (math.sin(obj.dec) - math.sin(alt) * math.sin(OBSERVER.lat)) / (
              math.cos(alt) * math.cos(OBSERVER.lat))
    cos_az = min(1, max(-1, cos_az))
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
        
    return math.degrees(alt), math.degrees(az)

def calculate_moon_phase(dt):
    """
    Calculate moon phase (0-1) where 0=new moon, 0.5=full moon, 1=new moon again
    Using a more accurate algorithm based on astronomical calculations
    """
    # Ensure we're working with UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    
    # Meeus first approximation
    T = (jd - 2451545.0) / 36525  # Time in Julian centuries since J2000.0
    
    # Sun's mean elongation
    D = 297.8502042 + 445267.1115168 * T - 0.0016300 * T**2 + T**3 / 545868 - T**4 / 113065000
    
    # Sun's mean anomaly
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000
    
    # Moon's mean anomaly
    Mm = 134.9634114 + 477198.8676313 * T - 0.0089970 * T**2 + T**3 / 69699 - T**4 / 14712000
    
    # Moon's argument of latitude
    F = 93.2720993 + 483202.0175273 * T - 0.0034029 * T**2 - T**3 / 3526000 + T**4 / 863310000
    
    # Corrections for perturbations
    dE = 1.0 - 0.002516 * T - 0.0000074 * T**2  # Correction for eccentricity
    
    # Convert to radians for calculations
    D = math.radians(D % 360)
    M = math.radians(M % 360)
    Mm = math.radians(Mm % 360)
    F = math.radians(F % 360)
    
    # Calculate phase angle
    phase_angle = 180 - D * 180/math.pi - 6.289 * math.sin(Mm) + 2.100 * math.sin(M) - 1.274 * math.sin(2*D - Mm) - 0.658 * math.sin(2*D) - 0.214 * math.sin(2*Mm) - 0.110 * math.sin(D)
    
    # Convert phase angle to illuminated fraction
    phase = (1 + math.cos(math.radians(phase_angle))) / 2
    
    return phase

def calculate_moon_position(dt):
    """Calculate moon's position using a more accurate model based on Jean Meeus' algorithms"""
    # Ensure we're working with UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    
    # Time in Julian centuries since J2000.0
    T = (jd - 2451545.0) / 36525.0
    
    # Meeus' Astronomical Algorithms - Chapter 47
    # Lunar mean elements
    Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T**2 + T**3 / 538841.0 - T**4 / 65194000.0  # Mean longitude
    D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T**2 + T**3 / 545868.0 - T**4 / 113065000.0   # Mean elongation
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000.0                        # Sun's mean anomaly
    Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T**2 + T**3 / 69699.0 - T**4 / 14712000.0     # Moon's mean anomaly
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T**2 - T**3 / 3526000.0 + T**4 / 863310000.0    # Argument of latitude

    # Reduce angles to range 0-360 degrees
    Lp = Lp % 360
    D = D % 360
    M = M % 360
    Mp = Mp % 360
    F = F % 360

    # Convert to radians for calculations
    Lp_rad = math.radians(Lp)
    D_rad = math.radians(D)
    M_rad = math.radians(M)
    Mp_rad = math.radians(Mp)
    F_rad = math.radians(F)

    # Periodic perturbations
    # Longitude perturbations
    dL = 6288.0160 * math.sin(Mp_rad)
    dL += 1274.0198 * math.sin(2*D_rad - Mp_rad)
    dL += 658.7141 * math.sin(2*D_rad)
    dL += 214.2591 * math.sin(2*Mp_rad)
    dL += 186.4060 * math.sin(M_rad)
    dL /= 1000000.0  # Convert to degrees

    # Latitude perturbations
    dB = 5128.0 * math.sin(F_rad)
    dB += 280.0 * math.sin(Mp_rad + F_rad)
    dB += 277.0 * math.sin(Mp_rad - F_rad)
    dB += 176.0 * math.sin(2*D_rad - F_rad)
    dB += 115.0 * math.sin(2*D_rad + F_rad)
    dB /= 1000000.0  # Convert to degrees

    # Calculate ecliptic coordinates
    lambda_moon = Lp + dL
    beta_moon = dB

    # Convert to equatorial coordinates
    epsilon = math.radians(23.43929111 - 0.013004167*T)  # Obliquity of ecliptic
    
    lambda_moon = math.radians(lambda_moon)
    beta_moon = math.radians(beta_moon)
    
    # Calculate right ascension and declination
    alpha = math.atan2(
        math.sin(lambda_moon) * math.cos(epsilon) - math.tan(beta_moon) * math.sin(epsilon),
        math.cos(lambda_moon)
    )
    delta = math.asin(
        math.sin(beta_moon) * math.cos(epsilon) + 
        math.cos(beta_moon) * math.sin(epsilon) * math.sin(lambda_moon)
    )

    # Get local sidereal time
    lst = calculate_lst(dt)
    
    # Calculate hour angle
    ha = lst - alpha
    
    # Convert to local horizontal coordinates
    lat_rad = math.radians(LATITUDE)
    
    # Calculate altitude
    sin_alt = (math.sin(lat_rad) * math.sin(delta) + 
               math.cos(lat_rad) * math.cos(delta) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    # Calculate azimuth
    az = math.atan2(
        math.sin(ha),
        math.cos(ha) * math.sin(lat_rad) - math.tan(delta) * math.cos(lat_rad)
    )
    az = (math.degrees(az) + 180) % 360
    
    # Convert altitude to degrees and apply refraction correction
    alt_deg = math.degrees(alt)
    if alt_deg > -0.575:
        R = 1.02 / math.tan(math.radians(alt_deg + 10.3/(alt_deg + 5.11)))
        alt_deg += R/60.0  # R is in arc-minutes, convert to degrees
    
    return alt_deg, az

def calculate_moon_interference_radius(moon_phase, obj_magnitude, sky_brightness):
    """
    Calculate the radius of moon interference based on multiple factors.
    
    Parameters:
    - moon_phase: 0-1 where 0=new moon, 0.5=full moon
    - obj_magnitude: Visual magnitude of the object
    - sky_brightness: Bortle scale (1-9)
    
    Returns:
    - Interference radius in degrees
    """
    # Base radius calculation based on moon phase
    if moon_phase >= 0.875 or moon_phase <= 0.125:  # New Moon ±0.125
        base_radius = 20
    elif 0.375 <= moon_phase <= 0.625:  # Full Moon ±0.125
        base_radius = 60
    elif 0.25 <= moon_phase < 0.375 or 0.625 < moon_phase <= 0.75:  # Quarter Moons
        base_radius = 40
    else:  # Crescent Moons
        base_radius = 30
    
    # Magnitude factor (fainter objects are more affected)
    # Normalize magnitude to a factor between 1.0 and 2.0
    mag_factor = min(2.0, max(1.0, obj_magnitude / 8.0))
    
    # Sky brightness factor (light pollution makes moon interference worse)
    # In Bortle 9 skies, interference is much more significant
    sky_factor = (sky_brightness / 5.0) ** 1.5  # Exponential effect for high Bortle
    
    # Calculate final radius
    radius = base_radius * mag_factor * sky_factor
    
    # Ensure minimum and maximum reasonable values
    # Maximum increased for very bright moon in light-polluted skies
    radius = min(90.0, max(15.0, radius))
    
    return radius

def is_near_moon(obj_alt, obj_az, moon_alt, moon_az, obj_magnitude, dt):
    """
    Enhanced moon proximity check taking into account moon phase and object brightness.
    """
    # Skip check if moon is below horizon
    if moon_alt < 0:
        return False
        
    # Calculate moon phase
    moon_phase = calculate_moon_phase(dt)
    
    # Calculate interference radius based on conditions
    radius = calculate_moon_interference_radius(
        moon_phase=moon_phase,
        obj_magnitude=obj_magnitude,
        sky_brightness=BORTLE_INDEX
    )
    
    # Convert coordinates to radians
    obj_alt = math.radians(90 - obj_alt)    # Convert to co-latitude
    obj_az = math.radians(obj_az)
    moon_alt = math.radians(90 - moon_alt)  # Convert to co-latitude
    moon_az = math.radians(moon_az)
    
    # Calculate angular separation using spherical trig
    dlon = moon_az - obj_az
    cos_d = (math.cos(moon_alt) * math.cos(obj_alt) +
             math.sin(moon_alt) * math.sin(obj_alt) * math.cos(dlon))
    cos_d = min(1.0, max(-1.0, cos_d))  # Ensure value is in valid range
    
    # Convert to degrees
    separation = math.degrees(math.acos(cos_d))
    
    return separation < radius

# ============= UTILITY FUNCTIONS =============

def parse_ra(ra_str):
    """Convert RA from HH:MM format to decimal degrees"""
    match = re.match(r'(\d+)h\s*(\d+)m', ra_str)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2))
        return (hours + minutes/60) * 15
    return 0

def parse_dec(dec_str):
    """Convert Dec from DD:MM format to decimal degrees"""
    match = re.match(r'([+-]?\d+)°?\s*(\d+)?\'?', dec_str)
    if match:
        degrees = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        return degrees + minutes/60 * (1 if degrees >= 0 else -1)
    match = re.match(r'([+-]?\d+)°?', dec_str)
    if match:
        return float(match.group(1))
    return 0

def parse_fov(fov_str):
    """Parse FOV string and return list of areas in square arcminutes"""
    if not fov_str:
        return []
    
    fov_list = fov_str.split(',')
    areas = []
    
    for fov in fov_list:
        fov = fov.strip()
        match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', fov)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
            
            if '°' in fov:
                width *= 60
                height *= 60
                
            areas.append(width * height)
    
    return areas

def calculate_total_area(fov_str):
    """Calculate total area from FOV string"""
    areas = parse_fov(fov_str)
    return sum(areas) if areas else 0

def calculate_required_panels(obj_fov):
    """Calculate number of panels needed to cover object"""
    if not obj_fov:
        return 1
        
    # Parse object FOV
    match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', obj_fov)
    if not match:
        return 1
        
    width = float(match.group(1))
    height = float(match.group(2))
    
    # Convert to degrees if in arcminutes
    if "'" in obj_fov:
        width = width / 60
        height = height / 60
    
    # Calculate panels needed in each dimension (with 10% overlap)
    panels_width = math.ceil(width / (SCOPE_FOV_WIDTH * 0.9))
    panels_height = math.ceil(height / (SCOPE_FOV_HEIGHT * 0.9))
    
    return panels_width * panels_height

def calculate_required_exposure(magnitude, bortle_index, obj_fov, single_exposure=SINGLE_EXPOSURE):
    """
    Calculate required total exposure time based on magnitude, sky conditions, and object size.
    Returns total exposure time in hours and number of frames needed.
    """
    # Base exposure time (in hours) for mag 10 object in Bortle 4
    base_exposure = 1.0
    
    # Adjust for magnitude (exponential relationship)
    magnitude_factor = 2 ** ((magnitude - 10) / 2.5)
    
    # Adjust for Bortle index (linear relationship)
    bortle_factor = (bortle_index / 4) ** 2
    
    # Calculate base total exposure time in hours
    base_total_exposure = base_exposure * magnitude_factor * bortle_factor
    
    # Calculate number of panels needed
    panels = calculate_required_panels(obj_fov)
    
    # Adjust total exposure time for panels
    total_exposure = base_total_exposure * panels
    
    # Calculate number of subframes needed
    subframes = math.ceil((total_exposure * 3600) / single_exposure)
    
    return total_exposure, subframes, panels

def is_object_imageable(obj, visibility_duration, bortle_index):
    """
    Determine if object can be imaged successfully given conditions.
    """
    if not hasattr(obj, 'magnitude') or obj.magnitude is None:
        return False
        
    required_exposure = calculate_required_exposure(obj.magnitude, bortle_index)
    return visibility_duration >= required_exposure

# ============= CLASS DEFINITIONS =============

class Observer:
    """Class to represent the observer's location"""
    def __init__(self, lat, lon):
        self.lat = math.radians(lat)
        self.lon = math.radians(lon)

class CelestialObject:
    """Class to represent a celestial object"""
    def __init__(self, name, ra_hours, dec_deg, fov=None, magnitude=None):
        self.name = name
        self.ra = math.radians(ra_hours * 15)  # Convert hours to degrees then to radians
        self.dec = math.radians(dec_deg)
        self.fov = fov
        self.magnitude = magnitude
        self.total_area = calculate_total_area(fov) if fov else 0
        self.required_exposure = None  # Will be calculated later

class ReportGenerator:
    """Class to handle report generation and formatting"""
    def __init__(self, date, location_data):
        self.date = date
        self.location = location_data
        self.sections = []
        
    def add_section(self, title, content):
        """Add a section to the report"""
        self.sections.append({
            'title': title,
            'content': content
        })
    
    def format_section(self, section):
        """Format a single section"""
        output = f"\n{section['title']}\n"
        output += "=" * len(section['title']) + "\n"
        output += section['content']
        return output
    
    def generate_quick_summary(self, visible_objects, moon_affected_objects, twilight_evening, twilight_morning, moon_phase):
        """Generate quick summary section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        content = (
            f"Date: {self.date.date()}\n"
            f"Location: {self.location['name']} ({LATITUDE:.2f}°N, {LONGITUDE:.2f}°E)\n\n"
            f"Observable Objects: {len(visible_objects)} total ({len(moon_affected_objects)} affected by moon)\n"
            f"Best Observation Window: {format_time(twilight_evening)} - {format_time(twilight_morning)}\n"
            f"Moon Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Seeing Conditions: Bortle {BORTLE_INDEX}\n"
        )
        self.add_section("QUICK SUMMARY", content)
    
    def generate_timing_section(self, sunset, sunrise, twilight_evening, twilight_morning, moon_rise, moon_set):
        """Generate timing information section"""
        content = (
            f"Sunset: {format_time(sunset)}\n"
            f"Astronomical Twilight Begins: {format_time(twilight_evening)}\n"
        )
        if moon_rise:
            content += f"Moon Rise: {format_time(moon_rise)}\n"
        if moon_set:
            content += f"Moon Set: {format_time(moon_set)}\n"
        content += (
            f"Astronomical Twilight Ends: {format_time(twilight_morning)}\n"
            f"Sunrise: {format_time(sunrise)}\n"
        )
        self.add_section("TIMING INFORMATION", content)
    
    def generate_moon_conditions(self, moon_phase, moon_affected_objects):
        """Generate moon conditions section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        content = (
            f"Current Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Objects affected by moon: {len(moon_affected_objects)}\n\n"
        )
        if moon_affected_objects:
            content += "Affected objects:\n"
            for obj in moon_affected_objects:
                periods = getattr(obj, 'moon_influence_periods', [])
                # Calculate total minutes properly from timedelta objects
                total_minutes = sum(
                    int((end - start).total_seconds() / 60)
                    for start, end in periods
                )
                content += f"- {obj.name} ({total_minutes} minutes of interference)\n"
        else:
            content += "No objects are significantly affected by moon proximity.\n"
        self.add_section("MOON CONDITIONS", content)
    
    def generate_object_sections(self, visible_objects, insufficient_objects):
        """Generate sections for different object categories"""
        # Prime targets (sufficient time & good conditions)
        prime_targets = [obj for obj in visible_objects 
                        if not getattr(obj, 'near_moon', False)]
        if prime_targets:
            content = self._format_object_list("Prime observation targets:", prime_targets)
            self.add_section("PRIME TARGETS", content)
        
        # Moon-affected targets
        moon_affected = [obj for obj in visible_objects 
                        if getattr(obj, 'near_moon', False)]
        if moon_affected:
            content = self._format_object_list("Objects affected by moon:", moon_affected)
            self.add_section("MOON-AFFECTED TARGETS", content)
        
        # Time-limited targets
        if insufficient_objects:
            content = self._format_object_list("Objects with insufficient visibility time:", insufficient_objects)
            self.add_section("TIME-LIMITED TARGETS", content)
    
    def _format_object_list(self, header, objects):
        """Format a list of objects with their details"""
        # Sort objects by visibility start time
        sorted_objects = sorted(objects, 
                              key=lambda obj: find_visibility_window(obj, self.date, self.date + timedelta(days=1))[0][0])
        
        content = f"{header}\n\n"
        for obj in sorted_objects:
            # Get visibility periods
            periods = find_visibility_window(obj, self.date, self.date + timedelta(days=1))
            if not periods:
                continue
                
            start_time = periods[0][0]
            #end_time = periods[-1][1]
            duration = calculate_visibility_duration(periods)
            end_time = start_time + timedelta(hours=duration)
            
            # Get moon status
            moon_status = ""
            if hasattr(obj, 'near_moon') and obj.near_moon:
                moon_phase = calculate_moon_phase(start_time)
                moon_icon, _ = get_moon_phase_icon(moon_phase)
                moon_status = f"{moon_icon} Moon interference"
            else:
                moon_status = "✨ Clear from moon"
            
            # Format the line
            content += f"{obj.name}\n"
            content += f"{moon_status}\n"
            content += f"Visibility: {format_time(start_time)} - {format_time(end_time)} ({duration:.1f} hours)\n"
            
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                content += f"Magnitude: {obj.magnitude}\n"
            
            if obj.fov:
                content += f"Field of view: {obj.fov}\n"
                # Calculate panels needed
                panels = calculate_required_panels(obj.fov)
                if panels > 1:
                    mosaic_size = math.ceil(math.sqrt(panels))
                    content += f"Mosaic: {mosaic_size}x{mosaic_size} panels\n"
            
            if hasattr(obj, 'required_exposure') and obj.required_exposure is not None:
                exposure_time, frames, _ = obj.required_exposure
                content += f"Required exposure: {exposure_time:.2f} hours ({frames} frames of {SINGLE_EXPOSURE}s)\n"
                
                # Add clear indication of sufficient/insufficient time
                if duration >= exposure_time:
                    content += "✓ Sufficient visibility time for imaging\n"
                else:
                    content += f"✗ NOT ENOUGH visibility time (needs {exposure_time:.1f}h, have {duration:.1f}h)\n"
            
            content += "\n"
        return content
    
    def generate_schedule_section(self, schedule, strategy):
        """Generate schedule section"""
        content = (
            f"Strategy: {strategy.value}\n"
            f"Total objects: {len(schedule)}\n"
            f"Total observation time: {sum((end - start).total_seconds() / 3600 for start, end, _ in schedule):.1f} hours\n\n"
        )
        
        for start, end, obj in schedule:
            duration = (end - start).total_seconds() / 3600
            exposure_time, frames, panels = calculate_required_exposure(
                obj.magnitude, BORTLE_INDEX, obj.fov)
            
            content += (
                f"{obj.name}\n"
                f"  Start: {format_time(start)}\n"
                f"  End: {format_time(end)}\n"
                f"  Duration: {duration:.1f} hours\n"
                f"  Required exposure: {exposure_time:.1f} hours\n"
            )
            if panels > 1:
                content += f"  Mosaic: {math.ceil(math.sqrt(panels))}x{math.ceil(math.sqrt(panels))}\n"
            content += "\n"
        
        self.add_section("RECOMMENDED SCHEDULE", content)
    
    def generate_report(self):
        """Generate the complete report"""
        output = "NIGHT OBSERVATION REPORT\n"
        output += "=" * 23 + "\n"
        
        for section in self.sections:
            output += self.format_section(section)
            
        return output

# Create global observer
OBSERVER = Observer(LATITUDE, LONGITUDE)

# ============= VISIBILITY FUNCTIONS =============

def is_visible(alt, az, use_margins=True):
    """Check if object is within visibility limits"""
    if use_margins:
        # Use 5-degree margins as in trajectory plotting
        return ((MIN_ALT - 5 <= alt <= MAX_ALT + 5) and 
                (MIN_AZ - 5 <= az <= MAX_AZ + 5))
    else:
        return (MIN_AZ <= az <= MAX_AZ) and (MIN_ALT <= alt <= MAX_ALT)

def find_visibility_window(obj, start_time, end_time, use_margins=True):
    """Find visibility window for an object, considering sun position"""
    current_time = start_time
    visibility_periods = []
    start_visible = None
    last_visible = False
    
    # Use 1-minute intervals for better precision, matching trajectory plotting
    interval = timedelta(minutes=1)
    
    while current_time <= end_time:
        # Check object's position
        alt, az = calculate_altaz(obj, current_time)
        
        # Check sun's position
        sun_alt, _ = calculate_sun_position(current_time)
        
        # Object is visible if:
        # 1. It's within visibility limits
        # 2. The sun is below the horizon (altitude < -5)
        is_currently_visible = is_visible(alt, az, use_margins) and sun_alt < -5
        
        # Object becomes visible
        if is_currently_visible and not last_visible:
            start_visible = current_time
        # Object becomes invisible
        elif not is_currently_visible and last_visible and start_visible is not None:
            visibility_periods.append((start_visible, current_time))
            start_visible = None
            
        last_visible = is_currently_visible
        current_time += interval
    
    # If object is still visible at the end, add the final period
    if start_visible is not None and last_visible:
        visibility_periods.append((start_visible, end_time))
    
    return visibility_periods

def calculate_visibility_duration(visibility_periods):
    """Calculate total visibility duration in hours"""
    total_seconds = sum(
        (end - start).total_seconds() 
        for start, end in visibility_periods
    )
    return total_seconds / 3600

# ============= TWILIGHT AND NIGHT FUNCTIONS =============

def find_sunset_sunrise(date):
    """Find sunset and sunrise times"""
    milan_tz = get_local_timezone()
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon = milan_tz.localize(noon)
    noon_utc = local_to_utc(noon)
    
    current_time = noon_utc
    alt, _ = calculate_sun_position(current_time)
    
    while alt > 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunset = current_time
    
    while alt <= 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunrise = current_time
    
    return utc_to_local(sunset), utc_to_local(sunrise)

def find_astronomical_twilight(date):
    """Find astronomical twilight times"""
    milan_tz = get_local_timezone()
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon = milan_tz.localize(noon)
    noon_utc = local_to_utc(noon)
    
    current_time = noon_utc
    alt, _ = calculate_sun_position(current_time)
    
    while alt > -18:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    twilight_evening = current_time
    
    while alt <= -18:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    twilight_morning = current_time
    
    return utc_to_local(twilight_evening), utc_to_local(twilight_morning)

# ============= OBJECT SELECTION FUNCTIONS =============

def find_best_objects(visibility_periods, max_overlapping=MAX_OBJECTS_OPTIMAL):
    """Select objects with longest visibility periods and minimal overlap"""
    sorted_periods = []
    for obj_name, period in visibility_periods.items():
        duration = period['duration']
        sorted_periods.append((obj_name, period['start'], period['end'], duration))
    
    sorted_periods.sort(key=lambda x: x[3], reverse=True)
    
    selected_objects = []
    for obj_data in sorted_periods:
        overlap = False
        for selected in selected_objects:
            if not (obj_data[2] <= selected[1] or obj_data[1] >= selected[2]):
                overlap = True
                break
        if not overlap and len(selected_objects) < max_overlapping:
            selected_objects.append(obj_data)
    
    return selected_objects

# ============= PLOTTING FUNCTIONS =============

def plot_moon_trajectory(ax, start_time, end_time):
    """Plot moon trajectory and add it to the legend"""
    times = []
    alts = []
    azs = []
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_moon_position(current_time)
        if is_visible(alt, az):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if azs:
        # Plot moon trajectory
        ax.plot(azs, alts, '-', color=MOON_TRAJECTORY_COLOR, 
               linewidth=MOON_LINE_WIDTH, label='Moon', zorder=2)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=MOON_MARKER_COLOR, 
                   markersize=MOON_MARKER_SIZE, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=MOON_MARKER_COLOR,
                       zorder=3)
                       
def filter_visible_objects(objects, start_time, end_time, exclude_insufficient=EXCLUDE_INSUFFICIENT_TIME, use_margins=True):
    """Filter objects based on visibility and exposure requirements"""
    filtered_objects = []
    insufficient_objects = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins) # Added use_margins=True
        if periods:
            duration = calculate_visibility_duration(periods)
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                # Calculate required exposure time and store it in the object
                obj.required_exposure = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)
                
                if duration >= MIN_VISIBILITY_HOURS:
                    obj.sufficient_time = duration >= obj.required_exposure[0]
                    if exclude_insufficient:
                        if obj.sufficient_time:
                            filtered_objects.append(obj)
                        else:
                            insufficient_objects.append(obj)
                    else:
                        filtered_objects.append(obj)
    
    return filtered_objects, insufficient_objects


def setup_altaz_plot():
    """Setup basic altitude-azimuth plot"""
    # Create figure with appropriate size
    fig = plt.figure(figsize=FIGURE_SIZE)  # Wider figure
    
    # Use GridSpec for better control over spacing
    gs = fig.add_gridspec(1, 1)
    # Adjust margins to accommodate axis labels and legend
    gs.update(left=0.1, right=0.85, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])
    
    # Set axis limits and labels
    ax.set_xlim(MIN_AZ-10, MAX_AZ+10)
    ax.set_ylim(MIN_ALT-10, MAX_ALT+10)
    ax.set_xlabel('Azimuth (degrees)')
    ax.set_ylabel('Altitude (degrees)')
    ax.grid(True, alpha=GRID_ALPHA)
    
    # Add visible region rectangle
    visible_region = Rectangle((MIN_AZ, MIN_ALT), 
                             MAX_AZ - MIN_AZ, 
                             MAX_ALT - MIN_ALT,
                             facecolor='green', 
                             alpha=VISIBLE_REGION_ALPHA,
                             label='Visible Region')
    ax.add_patch(visible_region)
    
    # Configure grid with major and minor ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    
    return fig, ax

def finalize_plot_legend(ax):
    """Finalize plot legend with sorted entries, keeping Visible Region and Moon first"""
    # Get current handles and labels
    handles, labels = ax.get_legend_handles_labels()
    
    # Find indices of special entries
    try:
        visible_idx = labels.index('Visible Region')
        visible_handle = handles.pop(visible_idx)
        visible_label = labels.pop(visible_idx)
    except ValueError:
        visible_handle, visible_label = None, None
        
    try:
        moon_idx = labels.index('Moon')
        moon_handle = handles.pop(moon_idx)
        moon_label = labels.pop(moon_idx)
    except ValueError:
        moon_handle, moon_label = None, None
    
    # Sort remaining entries
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: x[1].lower())
    handles, labels = zip(*sorted_pairs) if sorted_pairs else ([], [])
    
    # Reconstruct list with special entries first
    final_handles = []
    final_labels = []
    
    if visible_handle is not None:
        final_handles.append(visible_handle)
        final_labels.append(visible_label)
    if moon_handle is not None:
        final_handles.append(moon_handle)
        final_labels.append(moon_label)
        
    final_handles.extend(handles)
    final_labels.extend(labels)
    
    # Update legend
    ax.legend(final_handles, final_labels,
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Objects and Conditions')

def get_abbreviated_name(full_name):
    """Get abbreviated name (catalog designation) from full name"""
    # First try to find Messier number
    m_match = re.match(r'M(\d+)', full_name)
    if m_match:
        return f"M{m_match.group(1)}"
    
    # Then try NGC number
    ngc_match = re.match(r'NGC\s*(\d+)', full_name)
    if ngc_match:
        return f"NGC{ngc_match.group(1)}"
    
    # Then try IC number
    ic_match = re.match(r'IC\s*(\d+)', full_name)
    if ic_match:
        return f"IC{ic_match.group(1)}"
    
    # Then try SH2 number
    sh2_match = re.match(r'SH2-(\d+)', full_name)
    if sh2_match:
        return f"SH2-{sh2_match.group(1)}"  # Return complete SH2-nnn format
    
    # Then try SH number
    sh_match = re.match(r'SH\s*(\d+)', full_name)
    if sh_match:
        return f"SH{sh_match.group(1)}"  # Return complete SH-nnn format
        
    # Then try Barnard number
    b_match = re.match(r'B\s*(\d+)', full_name)
    if b_match:
        return f"B{b_match.group(1)}"
    
    # Then try Gum number
    gum_match = re.match(r'Gum\s*(\d+)', full_name)
    if gum_match:
        return f"GUM{gum_match.group(1)}"    

    # If no catalog number found, return first word
    return full_name.split()[0]

def find_label_position(azimuths, altitudes, existing_positions, margin=3):
    """Find suitable position for label that doesn't overlap with others"""
    # Try middle position first
    mid_idx = len(azimuths) // 2
    mid_pos = (azimuths[mid_idx], altitudes[mid_idx])
    
    if not any(abs(mid_pos[0] - pos[0]) < margin and abs(mid_pos[1] - pos[1]) < margin 
              for pos in existing_positions):
        return mid_pos
    
    # Try other positions along the trajectory
    for i in range(len(azimuths)):
        pos = (azimuths[i], altitudes[i])
        if not any(abs(pos[0] - existing_pos[0]) < margin and abs(pos[1] - existing_pos[1]) < margin 
                  for existing_pos in existing_positions):
            return pos
    
    return None

def plot_object_trajectory(ax, obj, start_time, end_time, color, existing_positions=None):
    """Plot trajectory with moon proximity checking and legend.
    Elements are plotted in specific z-order:
    1. Base trajectory (z=1)
    2. Moon interference segments (z=2)
    3. Hour markers (z=3)
    4. Hour labels (z=4)
    5. Object name (z=5)
    """
    # Ensure there's a legend (even if empty) to avoid NoneType errors
    if ax.get_legend() is None:
        ax.legend()
    times = []
    alts = []
    azs = []
    near_moon = []  # Track moon proximity
    obj.near_moon = False  # Initialize moon proximity flag
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    # Use smaller interval for smoother trajectory
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        moon_alt, moon_az = calculate_moon_position(current_time)
        
        # Extended visibility check for trajectory plotting (±5 degrees)
        if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
            MIN_AZ - 5 <= az <= MAX_AZ + 5):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Check moon proximity
            is_near = is_near_moon(alt, az, moon_alt, moon_az, obj.magnitude, current_time)
            near_moon.append(is_near)
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)  # Use 1-minute intervals for accuracy
    
    # Set moon influence flag only if object is affected for a significant period
    if near_moon:
        moon_influence_periods = []
        start_idx = None
        
        # Find continuous periods of moon influence
        for i, is_near in enumerate(near_moon):
            if is_near and start_idx is None:
                start_idx = i
            elif not is_near and start_idx is not None:
                moon_influence_periods.append((start_idx, i))
                start_idx = None
        
        # Don't forget the last period if it ends with moon influence
        if start_idx is not None:
            moon_influence_periods.append((start_idx, len(near_moon)))
        
        # Calculate total influence time
        total_influence_minutes = sum(end - start for start, end in moon_influence_periods)
        
        # Set flag if moon influence is significant (more than 15 minutes)
        obj.near_moon = total_influence_minutes >= 15
        obj.moon_influence_periods = moon_influence_periods  # Store periods for later use
    
    if azs:
        # Determine line style based on sufficient time
        line_style = '-' if getattr(obj, 'sufficient_time', True) else '--'
        
        # Plot base trajectory (lowest z-order)
        ax.plot(azs, alts, line_style, color=color, linewidth=1.5, alpha=0.3, zorder=1)
        
        # Plot moon-affected segments if any
        if hasattr(obj, 'moon_influence_periods'):
            for start_idx, end_idx in obj.moon_influence_periods:
                # Plot the moon-affected segment
                ax.plot(azs[start_idx:end_idx+1], 
                       alts[start_idx:end_idx+1], 
                       line_style,
                       color=MOON_INTERFERENCE_COLOR,
                       linewidth=2,
                       zorder=2)
        
        # Add label only once
        legend = ax.get_legend()
        obj_name = obj.name.split('/')[0]
        existing_labels = [t.get_text() for t in legend.get_texts()] if legend else []
        
        if obj_name not in existing_labels:
            # Add a dummy line for the legend
            ax.plot([], [], line_style, color=color, 
                   linewidth=2, label=obj_name)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=color, markersize=6, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=color,
                       zorder=3)
        
        # Add abbreviated name near trajectory
        if existing_positions is None:
            existing_positions = []
            
        label_pos = find_label_position(azs, alts, existing_positions)
        if label_pos:
            abbreviated_name = get_abbreviated_name(obj.name)
            ax.annotate(abbreviated_name, 
                       label_pos,
                       xytext=(5, 5),
                       textcoords='offset points',
                       color=color,
                       fontweight='bold',
                       fontsize=10)
            existing_positions.append(label_pos)

def plot_visibility_chart(objects, start_time, end_time, schedule=None, title="Object Visibility", use_margins=True):
    """Create visibility chart showing moon interference periods in yellow tones.
    - Goldenrod: Selected objects during moon interference
    - Khaki: Non-selected objects during moon interference
    - Green/Gray: Normal visibility periods
    
    Parameters:
    -----------
    objects : list
        List of celestial objects to plot
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    schedule : list, optional
        List of scheduled objects
    title : str, optional
        Chart title
    use_margins : bool, optional
        Whether to use extended margins (±5°) for visibility boundaries
    """
    
    # Ensure times are in local timezone
    milan_tz = get_local_timezone()
    if start_time.tzinfo != milan_tz:
        start_time = start_time.astimezone(milan_tz)
    if end_time.tzinfo != milan_tz:
        end_time = end_time.astimezone(milan_tz)
    
    # Get current time in local timezone for the vertical line
    current_time = datetime.now(milan_tz)
    
    # Create figure with settings
    fig, ax = _create_visibility_chart_figure(objects)
    
    # Get visibility periods and sort objects
    sorted_objects = _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins)
    
    # Setup plot
    _setup_visibility_chart_axes(ax, title, start_time, end_time, milan_tz)
     
    # Create color map for recommended vs non-recommended objects
    recommended_objects = [obj for _, _, obj in schedule] if schedule else []
    
    # Plot visibility periods
    for i, obj in enumerate(sorted_objects):
        _plot_object_visibility_bars(ax, i, obj, start_time, end_time, recommended_objects, use_margins)
    
    # Add vertical line for current time if it's within the plot range
    if start_time <= current_time <= end_time:
        ax.axvline(x=current_time, color='red', linestyle='-', linewidth=2, label='Current Time')
    
    # Customize plot
    ax.set_yticks(range(len(sorted_objects)))
    ax.set_yticklabels([obj.name for obj in sorted_objects])
    ax.grid(True, alpha=GRID_ALPHA)
    
    # Add legend entries for moon interference if needed
    if any(getattr(obj, 'near_moon', False) for obj in sorted_objects):
        _add_moon_interference_legend(ax)
    
    return fig, ax

def _create_visibility_chart_figure(objects):
    """Create figure with appropriate size for visibility chart"""
    fig = plt.figure(figsize=(15, max(10, len(objects)*0.3 + 4)))
    
    # Use GridSpec for better control over spacing
    gs = fig.add_gridspec(1, 1)
    # Adjust margins to accommodate labels and legend
    gs.update(left=0.25, right=0.95, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])
    return fig, ax

def _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins):
    """Get objects sorted by visibility start time for chart display"""
    milan_tz = get_local_timezone()
    object_periods = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            # Convert periods to local time
            local_periods = [(p[0].astimezone(milan_tz), p[1].astimezone(milan_tz)) 
                           for p in periods]
            duration = calculate_visibility_duration(periods)
            object_periods.append((obj, local_periods[0][0], duration))
    
    # Sort by start time
    object_periods.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in object_periods]

def _setup_visibility_chart_axes(ax, title, start_time, end_time, tz):
    """Setup axes for visibility chart"""
    ax.set_title(title)
    ax.set_xlabel('Local Time')
    ax.set_ylabel('Objects')
    ax.set_xlim(start_time, end_time)
    
    # Use local time formatter
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=tz))

def _plot_object_visibility_bars(ax, index, obj, start_time, end_time, recommended_objects, use_margins):
    """Plot visibility bars for a single object"""
    milan_tz = get_local_timezone()
    periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
    
    is_recommended = obj in recommended_objects
    has_sufficient_time = getattr(obj, 'sufficient_time', True)
    near_moon = getattr(obj, 'near_moon', False)
    
    # Determine color based on status and moon proximity
    color, alpha = _get_object_visibility_color(near_moon, is_recommended, has_sufficient_time)
    
    for period_start, period_end in periods:
        local_start = period_start.astimezone(milan_tz)
        local_end = period_end.astimezone(milan_tz)
        
        # If object has moon influence periods, we need to split the visibility bar
        if hasattr(obj, 'moon_influence_periods') and obj.moon_influence_periods:
            _plot_visibility_with_moon_interference(ax, index, obj, period_start, period_end, 
                                                 local_start, local_end, color, alpha, is_recommended)
        else:
            # Plot normal visibility bar if no moon influence
            ax.barh(index, local_end - local_start, left=local_start, height=0.3,
                   alpha=alpha, color=color)
        
        # Add label only for the first period
        if period_start == periods[0][0]:
            # Add abbreviated name at the start of the bar
            abbreviated_name = get_abbreviated_name(obj.name)
            ax.text(local_start, index, f" {abbreviated_name}", 
                   va='center', ha='left', 
                   fontsize=8,
                   fontweight='bold' if is_recommended else 'normal')
            
            ax.barh(index, timedelta(minutes=1), left=local_start, height=0.3,
                   alpha=0,  # Transparent
                   label=obj.name)

def _get_object_visibility_color(near_moon, is_recommended, has_sufficient_time):
    """Determine color and alpha for object visibility bars"""
    if near_moon:
        # Dark yellow for selected objects near moon, pale yellow for others
        if is_recommended:
            color = '#DAA520'  # Goldenrod
            alpha = 0.8
        else:
            color = '#F0E68C'  # Khaki
            alpha = 0.6
    else:
        if not has_sufficient_time:
            color = 'darkmagenta' if is_recommended else 'pink'
        else:
            color = 'green' if is_recommended else 'gray'
        alpha = 0.8 if is_recommended else 0.4
    
    return color, alpha

def _plot_visibility_with_moon_interference(ax, index, obj, period_start, period_end, 
                                         local_start, local_end, color, alpha, is_recommended):
    """Plot visibility bars with moon interference segments"""
    milan_tz = get_local_timezone()
    period_minutes = int((period_end - period_start).total_seconds() / 60)
    
    # Convert moon influence periods to actual times
    moon_times = []
    for start_idx, end_idx in obj.moon_influence_periods:
        moon_start = period_start + timedelta(minutes=start_idx)
        moon_end = period_start + timedelta(minutes=end_idx)
        if moon_start < period_end and moon_end > period_start:
            moon_times.append((
                max(moon_start, period_start),
                min(moon_end, period_end)
            ))
    
    # Plot non-moon-affected parts in normal color
    last_end = period_start
    for moon_start, moon_end in moon_times:
        if moon_start > last_end:
            # Plot normal visibility segment
            ax.barh(index, 
                   moon_start.astimezone(milan_tz) - last_end.astimezone(milan_tz),
                   left=last_end.astimezone(milan_tz),
                   height=0.3,
                   alpha=alpha,
                   color=color)
        # Plot moon-affected segment
        ax.barh(index,
               moon_end.astimezone(milan_tz) - moon_start.astimezone(milan_tz),
               left=moon_start.astimezone(milan_tz),
               height=0.3,
               alpha=alpha,
               color='#DAA520' if is_recommended else '#F0E68C')  # Goldenrod/Khaki
        last_end = moon_end
    
    # Plot remaining normal visibility if any
    if last_end < period_end:
        ax.barh(index,
               period_end.astimezone(milan_tz) - last_end.astimezone(milan_tz),
               left=last_end.astimezone(milan_tz),
               height=0.3,
               alpha=alpha,
               color=color)

def _add_moon_interference_legend(ax):
    """Add legend entries for moon interference"""
    # Add dummy patches for legend
    ax.barh([-1], [0], height=0.3, color='#DAA520', alpha=0.8, 
            label='Selected Object (Moon Interference)')
    ax.barh([-1], [0], height=0.3, color='#F0E68C', alpha=0.4,
            label='Non-selected Object (Moon Interference)')

# ============= SCHEDULE GENERATION =============

def calculate_object_score(obj, periods, strategy=SCHEDULING_STRATEGY):
    """Calculate object score based on scheduling strategy"""
    duration = calculate_visibility_duration(periods)
    exposure_time, frames, panels = calculate_required_exposure(
        obj.magnitude, BORTLE_INDEX, obj.fov)
    
    if strategy == SchedulingStrategy.LONGEST_DURATION:
        return duration
    
    elif strategy == SchedulingStrategy.MAX_OBJECTS:
        # Prefer objects that need just enough time
        return 1.0 / abs(duration - exposure_time)
    
    elif strategy == SchedulingStrategy.OPTIMAL_SNR:
        # Consider magnitude and sky position
        alt_score = max(calculate_max_altitude(obj, periods[0][0], periods[-1][1]), 30) / 90
        mag_score = (20 - obj.magnitude) / 20  # Brighter objects score higher
        return alt_score * mag_score
    
    elif strategy == SchedulingStrategy.MINIMAL_MOSAIC:
        # Prefer objects requiring fewer panels
        return 1.0 / panels
    
    elif strategy == SchedulingStrategy.DIFFICULTY_BALANCED:
        # Balance between difficulty and feasibility
        difficulty = obj.magnitude / 20 + panels / 10
        feasibility = duration / exposure_time
        return feasibility / difficulty
    
    return duration

def calculate_max_altitude(obj, start_time, end_time):
    """Calculate maximum altitude during visibility period"""
    max_alt = 0
    current_time = start_time
    while current_time <= end_time:
        alt, _ = calculate_altaz(obj, current_time)
        max_alt = max(max_alt, alt)
        current_time += timedelta(minutes=TRAJECTORY_INTERVAL_MINUTES)
    return max_alt

def generate_observation_schedule(objects, start_time, end_time, 
                                strategy=SCHEDULING_STRATEGY,
                                min_duration=MIN_VISIBILITY_HOURS,
                                max_overlap=MAX_OVERLAP_MINUTES):
    """Generate optimal observation schedule based on selected strategy"""
    schedule = []
    
    # Filter objects based on sufficient time if needed
    if EXCLUDE_INSUFFICIENT_TIME:
        objects = [obj for obj in objects if getattr(obj, 'sufficient_time', True)]
    
    # Calculate scores and periods for all objects
    object_data = []
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=True)  # Added use_margins=True
        if periods:
            duration = calculate_visibility_duration(periods)
            if duration >= min_duration:
                exposure_time, frames, panels = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)
                if not EXCLUDE_INSUFFICIENT_TIME or duration >= exposure_time:
                    score = calculate_object_score(obj, periods, strategy)
                    object_data.append((obj, periods, duration, score))
    
    # Sort by score according to strategy
    object_data.sort(key=lambda x: x[3], reverse=True)
    
    # Schedule observations based on strategy
    if strategy == SchedulingStrategy.MAX_OBJECTS:
        # Try to fit as many objects as possible
        scheduled_times = []
        for obj, periods, duration, score in object_data:
            exposure_time, frames, panels = calculate_required_exposure(
                obj.magnitude, BORTLE_INDEX, obj.fov)
            
            # Try each visibility period
            for period_start, period_end in periods:
                conflict = False
                for scheduled_start, scheduled_end, _ in scheduled_times:
                    overlap = min(period_end, scheduled_end) - max(period_start, scheduled_start)
                    if overlap.total_seconds() / 60 > max_overlap:
                        conflict = True
                        break
                
                if not conflict:
                    # Schedule only needed time, not entire visibility window
                    end_time = period_start + timedelta(hours=exposure_time)
                    if end_time <= period_end:
                        scheduled_times.append((period_start, end_time, obj))
                        break
    
    else:
        # Use standard scheduling with full visibility windows
        scheduled_times = []
        for obj, periods, duration, score in object_data:
            for period_start, period_end in periods:
                conflict = False
                for scheduled_start, scheduled_end, _ in scheduled_times:
                    overlap = min(period_end, scheduled_end) - max(period_start, scheduled_start)
                    if overlap.total_seconds() / 60 > max_overlap:
                        conflict = True
                        break
                
                if not conflict:
                    scheduled_times.append((period_start, period_end, obj))
                    break
    
    # Sort schedule by start time
    scheduled_times.sort(key=lambda x: x[0])
    return scheduled_times




# ============= OUTPUT FORMATTING =============

def format_time(time):
    """Format time for display"""
    local_tz = get_local_timezone()
    
    if time.tzinfo != local_tz:
        time = time.astimezone(local_tz)
    elif time.tzinfo is None:
        time = local_tz.localize(time)
    
    return time.strftime("%H:%M:%S")

def print_visibility_report(objects, start_time, end_time):
    """Print detailed visibility report"""
    print("\nVisibility Report")
    print("=" * 50)
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            duration = calculate_visibility_duration(periods)
            print(f"\n{obj.name}")
            print(f"Total visibility: {duration:.1f} hours")
            print("Visible periods:")
            for start, end in periods:
                print(f"  {format_time(start)} - {format_time(end)}")
            if obj.fov:
                print(f"Field of view: {obj.fov}")
                print(f"Total area: {obj.total_area:.1f} sq. arcmin")

def filter_imageable_objects(objects, start_time, end_time, bortle_index):
    """Filter objects based on required exposure time vs. visibility duration"""
    imageable_objects = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            duration = calculate_visibility_duration(periods)
            
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                required_exposure = calculate_required_exposure(obj.magnitude, bortle_index)
                obj.required_exposure = required_exposure
                
                if duration >= required_exposure:
                    imageable_objects.append(obj)
    
    return imageable_objects

def print_imaging_report(objects, bortle_index):
    """Print detailed imaging report"""
    print("\nImaging Conditions Report")
    print(f"Bortle Index: {bortle_index}")
    print("=" * 50)
    
    for obj in objects:
        if hasattr(obj, 'required_exposure') and obj.required_exposure is not None:
            print(f"\n{obj.name}")
            print(f"Magnitude: {obj.magnitude}")
            print(f"Required exposure: {obj.required_exposure:.2f} hours")
            print(f"Minimum subframes: {math.ceil((obj.required_exposure * 3600) / SINGLE_EXPOSURE)}")
            if obj.fov:
                print(f"Field of view: {obj.fov}")

def print_schedule(schedule):
    """Print observation schedule"""
    print("\nObservation Schedule")
    print("=" * 50)
    
    for start, end, obj in schedule:
        duration = (end - start).total_seconds() / 3600
        print(f"\n{obj.name}")
        print(f"Start: {format_time(start)}")
        print(f"End: {format_time(end)}")
        print(f"Duration: {duration:.1f} hours")
        if obj.fov:
            print(f"Field of view: {obj.fov}")

def get_moon_phase_icon(phase):
    """
    Get Unicode moon phase icon based on illumination percentage
    phase: 0-1 where 0=new moon, 1=full moon
    Returns appropriate moon phase emoji based on standard illumination percentages
    """
    if phase <= 0.01:  # New Moon (0%)
        return "🌑", "New Moon"
    elif phase <= 0.49:  # Waxing Crescent (0-50%)
        return "🌒", "Waxing Crescent"
    elif phase <= 0.51:  # First Quarter (50%)
        return "🌓", "First Quarter"
    elif phase <= 0.99:  # Waxing Gibbous (50-100%)
        return "🌔", "Waxing Gibbous"
    elif phase <= 1.0:  # Full Moon (100%)
        return "🌕", "Full Moon"
    elif phase <= 1.49:  # Waning Gibbous (100-50%)
        return "🌖", "Waning Gibbous"
    elif phase <= 1.51:  # Last Quarter (50%)
        return "🌗", "Last Quarter"
    else:  # Waning Crescent (50-0%)
        return "🌘", "Waning Crescent"

def print_combined_report(objects, start_time, end_time, bortle_index):
    """Print a combined report including visibility and imaging information."""
    print("\nNIGHT OBSERVATION REPORT")
    print(f"Date: {start_time.date()}")
    print(f"Location: Milano, Italy")
    print("-" * 50)
    
    # Sort objects by visibility duration for the entire night
    sorted_objects = []
    for obj in objects:
        visibility_periods = find_visibility_window(obj, start_time, end_time, use_margins=True)  # Added use_margins=True
        if visibility_periods:
            duration = calculate_visibility_duration(visibility_periods)
            # Store the visibility periods with the object for later use
            obj.visibility_periods = visibility_periods
            sorted_objects.append((obj, duration))
    
    # Sort by duration in descending order
    sorted_objects.sort(key=lambda x: x[1], reverse=True)
    
    # Print visibility information for each object
    for obj, duration in sorted_objects:
        # Get the first and last visibility periods
        first_period = obj.visibility_periods[0]
        last_period = obj.visibility_periods[-1]
        
        # Calculate total visibility duration in hours
        hours = duration.total_seconds() / 3600
        
        # Get imaging requirements
        required_panels = calculate_required_panels(obj.fov) if obj.fov else None
        required_exposure = calculate_required_exposure(obj.magnitude, bortle_index, obj.fov) if obj.magnitude and obj.fov else None
        
        print(f"\n{obj.name}:")
        print(f"Visibility: {format_time(first_period[0])} - {format_time(last_period[1])} ({hours:.1f} hours)")
        
        if required_panels is not None:
            print(f"Required panels: {required_panels}")
        if required_exposure is not None:
            print(f"Required exposure: {required_exposure[0]:.1f} hours")  # Fixed to use first element of tuple
        
        # Check if object is near moon during any visibility period
        if hasattr(obj, 'near_moon') and obj.near_moon:
            print("WARNING: Object will be near the moon during some visibility periods")
        
        # Check if object has sufficient time for imaging
        if required_exposure is not None:
            if hours >= required_exposure[0]:  # Fixed to use first element of tuple
                print("✓ Sufficient time for imaging")
            else:
                print("✗ Insufficient time for imaging")
    
    print("\n" + "-" * 50)

def print_schedule_strategy_report(schedule, strategy):
    """Print schedule details based on strategy"""
    print(f"\nObservation Schedule ({strategy.value})")
    print("=" * 50)
    
    total_objects = len(schedule)
    total_time = sum((end - start).total_seconds() / 3600 
                     for start, end, _ in schedule)
    
    print(f"Total objects: {total_objects}")
    print(f"Total observation time: {total_time:.1f} hours")
    
    for start, end, obj in schedule:
        duration = (end - start).total_seconds() / 3600
        exposure_time, frames, panels = calculate_required_exposure(
            obj.magnitude, BORTLE_INDEX, obj.fov)
        
        print(f"\n{obj.name}")
        print(f"Start: {format_time(start)}")
        print(f"End: {format_time(end)}")
        print(f"Duration: {duration:.1f} hours")
        print(f"Required exposure: {exposure_time:.1f} hours")
        print(f"Panels: {panels}")
        if panels > 1:
            print(f"Mosaic: {math.ceil(math.sqrt(panels))}x{math.ceil(math.sqrt(panels))}")

def print_objects_by_type(objects, abbreviate=False):
    """Print objects organized by type"""
    objects_by_type = {}
    for obj in objects:
        obj_type = getattr(obj, 'type', 'unknown')
        if obj_type not in objects_by_type:
            objects_by_type[obj_type] = []
        objects_by_type[obj_type].append(obj)
    
    print("\nObjects by type:")
    print("=" * 50)
    for obj_type, obj_list in objects_by_type.items():
        print(f"\n{obj_type.replace('_', ' ').title()} ({len(obj_list)}):")
        for obj in obj_list:
            print(f"  {obj.name}")
            if not abbreviate:
                if hasattr(obj, 'fov') and obj.fov:
                    print(f"    FOV: {obj.fov}")
                if hasattr(obj, 'comments') and obj.comments:
                    print(f"    Comments: {obj.comments}")


# ============= MAIN PROGRAM =============

def main():
    """Main program execution"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Astronomical visibility report and charts')
    parser.add_argument('--date', type=str, default=None, help='Date for calculations (YYYY-MM-DD)')
    parser.add_argument('--object', type=str, default=None, help='Specific object to display')
    parser.add_argument('--type', type=str, default=None, help='Filter by object type')
    parser.add_argument('--report-only', action='store_true', help='Show only the text report')
    parser.add_argument('--schedule', choices=['longest', 'max_objects', 'optimal_snr'], 
                      default='longest', help='Scheduling strategy')
    parser.add_argument('--no-margins', action='store_true', 
                      help='Do not use extended margins for visibility chart')
    
    args = parser.parse_args()
    
    # Get current time to determine which night we're in
    current_date = datetime.now(get_local_timezone())
    
    # Get night period
    sunset, next_sunrise = find_sunset_sunrise(current_date)
    twilight_evening, twilight_morning = find_astronomical_twilight(current_date)

     # Ensure twilight times are in the correct timezone
    local_tz = get_local_timezone()
    if twilight_evening.tzinfo != local_tz:
        twilight_evening = twilight_evening.astimezone(local_tz)
    if twilight_morning.tzinfo != local_tz:
        twilight_morning = twilight_morning.astimezone(local_tz)

    # If current time is after midnight, adjust to previous day's sunset
    if current_date.hour < 12:
        yesterday = current_date - timedelta(days=1)
        sunset, _ = find_sunset_sunrise(yesterday)
        twilight_evening, _ = find_astronomical_twilight(yesterday)
    # If we're in daytime, calculate for tonight
    elif sunset > current_date:
        # We're in daytime before sunset, use today's twilight times
        pass



    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
            return
    else:
        all_objects = get_combined_catalog()
    
    # Determine use_margins setting from args (invert the no-margins flag)
    use_margins = not args.no_margins
    
    # Filter objects based on visibility and exposure requirements for the entire night
    visible_objects, insufficient_objects = filter_visible_objects(
        all_objects, twilight_evening, twilight_morning, use_margins=use_margins)
    
    if not visible_objects and not insufficient_objects:
        print("No objects are visible under current conditions")
        return
    
    # Initialize report generator with the full night period
    report_gen = ReportGenerator(twilight_evening, DEFAULT_LOCATION)
    
    # Find moon rise and set times and check moon interference
    moon_rise = None
    moon_set = None
    check_time = twilight_evening
    prev_alt = None
    
    # First pass: find moon rise/set times for the entire night
    while check_time <= twilight_morning:
        moon_alt, _ = calculate_moon_position(check_time)
        
        if prev_alt is not None:
            # Moon rise detected
            if prev_alt < 0 and moon_alt >= 0:
                moon_rise = check_time
            # Moon set detected
            elif prev_alt >= 0 and moon_alt < 0:
                moon_set = check_time
        
        prev_alt = moon_alt
        check_time += timedelta(minutes=1)
    
    # Calculate moon phase at the start of astronomical twilight
    moon_phase = calculate_moon_phase(twilight_evening)
    
    # Second pass: check moon interference for each object
    moon_affected = []
    all_objects_to_check = visible_objects + insufficient_objects
    
    for obj in all_objects_to_check:
        # Reset moon interference attributes
        obj.near_moon = False
        obj.moon_influence_periods = []
        
        # Check visibility periods for the entire night
        visibility_periods = find_visibility_window(obj, twilight_evening, twilight_morning, use_margins=True)
        
        for period_start, period_end in visibility_periods:
            check_time = period_start
            interference_start = None
            
            while check_time <= period_end:
                obj_alt, obj_az = calculate_altaz(obj, check_time)
                moon_alt, moon_az = calculate_moon_position(check_time)
                
                if is_near_moon(obj_alt, obj_az, moon_alt, moon_az, obj.magnitude, check_time):
                    if interference_start is None:
                        interference_start = check_time
                elif interference_start is not None:
                    obj.moon_influence_periods.append((interference_start, check_time))
                    interference_start = None
                
                check_time += timedelta(minutes=15)  # Check every 15 minutes
            
            if interference_start is not None:
                obj.moon_influence_periods.append((interference_start, period_end))
        
        if obj.moon_influence_periods:
            obj.near_moon = True
            moon_affected.append(obj)
    
    # Generate report sections for the entire night
    report_gen.generate_quick_summary(visible_objects, moon_affected, 
                                    twilight_evening, twilight_morning, moon_phase)
    report_gen.generate_timing_section(sunset, next_sunrise, 
                                     twilight_evening, twilight_morning,
                                     moon_rise, moon_set)
    report_gen.generate_moon_conditions(moon_phase, moon_affected)
    report_gen.generate_object_sections(visible_objects, insufficient_objects)
    
    # Generate schedules for different strategies for the entire night
    schedules = {}
    for strategy in SchedulingStrategy:
        schedule = generate_observation_schedule(
            visible_objects, twilight_evening, twilight_morning,
            strategy=strategy)
        schedules[strategy] = schedule
        report_gen.generate_schedule_section(schedule, strategy)
    
    # Print the complete report
    print(report_gen.generate_report())
    
    # Use selected strategy for visualization
    schedule = schedules[SCHEDULING_STRATEGY]
    
    # Create plots for the entire night period
    fig, ax = setup_altaz_plot()
    
    # Generate colors 
    colormap = plt.get_cmap(COLOR_MAP) 
    colors = colormap(np.linspace(0, 1, len(visible_objects)))
    
    # Initialize empty legend to avoid NoneType errors
    ax.legend()
    
    # Plot moon trajectory first
    plot_moon_trajectory(ax, twilight_evening, twilight_morning)
    
    existing_positions = []
    # Plot trajectories for visible objects
    for obj, color in zip(visible_objects, colors):
        plot_object_trajectory(ax, obj, twilight_evening, twilight_morning, 
                             color, existing_positions)
    
    # Plot trajectories for insufficient time objects if not excluded
    if not EXCLUDE_INSUFFICIENT_TIME:
        for obj in insufficient_objects:
            plot_object_trajectory(ax, obj, twilight_evening, twilight_morning, 
                                 'pink', existing_positions)
    
    plt.title(f"Object Trajectories for Night of {sunset.date()}")
    # Create custom legend
    handles, labels = ax.get_legend_handles_labels()
    
    # Add a legend entry for moon interference if any object was near moon
    if any(obj for obj in visible_objects + insufficient_objects if hasattr(obj, 'near_moon')):
        moon_line = plt.Line2D([0], [0], color=MOON_INTERFERENCE_COLOR, linestyle='-', label='Moon Interference')
        handles.append(moon_line)
    
    # Add legend entry for insufficient time objects if any
    if insufficient_objects:
        insuf_line = plt.Line2D([0], [0], color='gray', linestyle='--', label='Insufficient Time')
        handles.append(insuf_line)
    
    # Create the legend with all handles
    finalize_plot_legend(ax)
    plt.show()
    plt.close(fig)  # Explicitly close the figure
    
    # Create visibility chart for the entire night
    if not EXCLUDE_INSUFFICIENT_TIME:
        visible_objects.extend(insufficient_objects)
    fig, ax = plot_visibility_chart(visible_objects, twilight_evening, 
                                  twilight_morning, schedule, use_margins=False)
    plt.show()
    plt.close(fig)  # Explicitly close the figure

if __name__ == "__main__":
    main()
