import math
import numpy as np
from datetime import datetime, timedelta, timezone

import pytz
import re

import csv

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

from enum import Enum

class SchedulingStrategy(Enum):
    LONGEST_DURATION = "longest_duration"  # Current strategy: prioritize longest visibility
    MAX_OBJECTS = "max_objects"           # Maximum number of objects
    OPTIMAL_SNR = "optimal_snr"           # Best imaging conditions
    #MINIMAL_MOSAIC = "minimal_mosaic"     # Fewer panels needed
    #DIFFICULTY_BALANCED = "difficulty_balanced"  # Mix of easy and challenging

# ============= GLOBAL CONFIGURATION =============

# Location Configuration
LATITUDE = 45.516667  # Milan latitude
LONGITUDE = 9.216667  # Milan longitude
TIMEZONE = 'Europe/Rome'

# Visibility Constraints
MIN_ALT = 20  # Minimum altitude in degrees
MAX_ALT = 75  # Maximum altitude in degrees
MIN_AZ = 75   # Minimum azimuth in degrees
MAX_AZ = 160  # Maximum azimuth in degrees

# Catalog selection
USE_CSV_CATALOG = True  # Use custom CSV catalog
CATALOGNAME="objects.csv" #catalog_fixed.csv

# Time & Visibility Configuration
MIN_VISIBILITY_HOURS = 2   # Minimum visibility window in hours
MIN_TOTAL_AREA = 15 * 15     # Minimum area in square arcminutes
TRAJECTORY_INTERVAL_MINUTES = 15  # Interval minutes for trajectory calculations
SEARCH_INTERVAL_MINUTES = 1  # Interval minutes for searching rise/set times

# Scheduling Configuration
SCHEDULING_STRATEGY = SchedulingStrategy.MAX_OBJECTS
MAX_OVERLAP_MINUTES = 15  # Maximum allowed overlap between observations

# Visibility Filtering
EXCLUDE_INSUFFICIENT_TIME = False  # Whether to exclude objects with insufficient visibility time

# Imaging Configuration
BORTLE_INDEX = 9      # Milan sky condition (1-9 scale)
# Vespera Passenger Specifications
SCOPE_FOV_WIDTH = 2.4  # degrees
SCOPE_FOV_HEIGHT = 1.8  # degrees
SCOPE_FOV_AREA = SCOPE_FOV_WIDTH * SCOPE_FOV_HEIGHT  # square degrees
SINGLE_EXPOSURE = 10  # Vespera typically uses 10-30s exposures
MIN_SNR = 20          # Good balance for Vespera's capabilities
GAIN = 800            # Sony IMX585 optimal gain setting
READ_NOISE = 0.8      # Sony IMX585 typical read noise
PIXEL_SIZE = 2.9      # Sony IMX585 pixel size in microns
FOCAL_LENGTH = 200    # Vespera's focal length
APERTURE = 50         # Vespera's aperture

# Plot Configuration
MAX_OBJECTS_OPTIMAL = 5  # Maximum number of objects to show in optimal plot
FIGURE_SIZE = (12, 10)   # Default figure size for plots
COLOR_MAP = 'tab20'      # Color map for trajectory plots
GRID_ALPHA = 0.3         # Grid transparency
VISIBLE_REGION_ALPHA = 0.1  # Visibility region transparency

# Moon Configuration
MOON_PROXIMITY_RADIUS = 10  # Radius in degrees to check for moon proximity
MOON_TRAJECTORY_COLOR = 'yellow'  # Color for moon's trajectory
MOON_MARKER_COLOR = 'yellow'  # Color for moon's hour markers
MOON_LINE_WIDTH = 2  # Width of moon's trajectory line
MOON_MARKER_SIZE = 6  # Size of moon's hour markers
MOON_INTERFERENCE_COLOR = 'lightblue'  # Color for object trajectories near moon

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
    current_time = datetime.now(get_milan_timezone())
    
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
        time = datetime.now(get_milan_timezone())
    
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
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    # Flatten the dictionary into a single list while maintaining type information
    all_objects = []
    for obj_type, objects in objects_by_type.items():
        for obj in objects:
            obj.type = obj_type  # Add type information to object
            all_objects.append(obj)
    
    return all_objects

# ======== TIME CONVERSION FUNCTIONS =============

def get_milan_timezone():
    """Get configured timezone"""
    return pytz.timezone('Europe/Rome')

def local_to_utc(local_time):
    """Convert local time to UTC"""
    milan_tz = get_milan_timezone()
    if local_time.tzinfo is None:
        local_time = milan_tz.localize(local_time)
    return local_time.astimezone(pytz.UTC)

def utc_to_local(utc_time):
    """Convert UTC time to local time"""
    milan_tz = get_milan_timezone()
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

def calculate_moon_position(dt):
    """Calculate moon's position using simplified model"""
    # Ensure we're working with UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    
    # Calculate number of days since J2000.0
    d = jd - 2451545.0
    
    # Lunar orbital elements (simplified)
    L = 218.316 + 13.176396 * d  # mean longitude
    M = 134.963 + 13.064993 * d  # mean anomaly
    F = 93.272 + 13.229350 * d   # argument of latitude
    
    # Convert to radians
    L = math.radians(L)
    M = math.radians(M)
    F = math.radians(F)
    
    # Calculate simplified lunar coordinates
    lambda_moon = L + math.radians(6.289) * math.sin(M)  # longitude
    beta_moon = math.radians(5.128) * math.sin(F)        # latitude
    
    # Calculate altitude and azimuth
    ha = calculate_lst(dt) - lambda_moon
    
    # Calculate altitude
    alt = math.asin(math.sin(OBSERVER.lat) * math.sin(beta_moon) + 
                    math.cos(OBSERVER.lat) * math.cos(beta_moon) * math.cos(ha))
    
    # Calculate azimuth
    az = math.atan2(math.sin(ha), 
                    math.cos(ha) * math.sin(OBSERVER.lat) - 
                    math.tan(beta_moon) * math.cos(OBSERVER.lat))
    
    return math.degrees(alt), (math.degrees(az) + 360) % 360

def is_near_moon(obj_alt, obj_az, moon_alt, moon_az, radius=MOON_PROXIMITY_RADIUS):
    """Check if object is within radius degrees of the moon"""
    # Convert to radians
    obj_alt = math.radians(obj_alt)
    obj_az = math.radians(obj_az)
    moon_alt = math.radians(moon_alt)
    moon_az = math.radians(moon_az)
    
    # Calculate angular separation using spherical law of cosines
    separation = math.acos(math.sin(obj_alt) * math.sin(moon_alt) + 
                          math.cos(obj_alt) * math.cos(moon_alt) * 
                          math.cos(obj_az - moon_az))
    
    return math.degrees(separation) <= radius


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

# Create global observer
OBSERVER = Observer(LATITUDE, LONGITUDE)

# ============= VISIBILITY FUNCTIONS =============

def is_visible(alt, az):
    """Check if object is within visibility limits"""
    return (MIN_AZ <= az <= MAX_AZ) and (MIN_ALT <= alt <= MAX_ALT)

def find_visibility_window(obj, start_time, end_time):
    """Find visibility window for an object"""
    current_time = start_time
    visibility_periods = []
    start_visible = None
    
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        
        if is_visible(alt, az):
            if start_visible is None:
                start_visible = current_time
        elif start_visible is not None:
            visibility_periods.append((start_visible, current_time))
            start_visible = None
            
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
    
    if start_visible is not None:
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
    milan_tz = get_milan_timezone()
    
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
    milan_tz = get_milan_timezone()
    
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
                       
def filter_visible_objects(objects, start_time, end_time, exclude_insufficient=EXCLUDE_INSUFFICIENT_TIME):
    """Filter objects based on visibility and exposure requirements"""
    filtered_objects = []
    insufficient_objects = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            duration = calculate_visibility_duration(periods)
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                exposure_time, frames, panels = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)
                
                if duration >= MIN_VISIBILITY_HOURS:
                    obj.sufficient_time = duration >= exposure_time
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
    # Increase figure size to accommodate legend
    fig = plt.figure(figsize=(15, 10))  # Wider figure
    
    # Use gridspec to create better layout
    gs = fig.add_gridspec(1, 1)
    gs.update(left=0.1, right=0.8)  # Leave more space for legend
    
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
    
    # Then try Sh2 number - Fixed this part
    sh2_match = re.match(r'SH2-(\d+)', full_name)
    if sh2_match:
        return f"SH2-{sh2_match.group(1)}"  # Return complete SH2-nnn format
        
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
    """Plot trajectory with moon proximity checking and legend"""
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
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        moon_alt, moon_az = calculate_moon_position(current_time)
        
        if is_visible(alt, az):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            is_near = is_near_moon(alt, az, moon_alt, moon_az)
            near_moon.append(is_near)
            if is_near:
                obj.near_moon = True  # Set flag if object is ever near moon
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if azs:
        # Plot trajectory segments based on moon proximity
        for i in range(len(azs)-1):
            segment_color = MOON_INTERFERENCE_COLOR if near_moon[i] or near_moon[i+1] else color
            line_style = '--' if not getattr(obj, 'sufficient_time', True) else '-'
            # Only add label for the first segment to avoid duplicates in legend
            if i == 0:
                ax.plot(azs[i:i+2], alts[i:i+2], line_style, color=segment_color, 
                       linewidth=2, label=obj.name.split('/')[0])
        
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

def plot_visibility_chart(objects, start_time, end_time, schedule=None, title="Object Visibility"):
    """Create visibility chart for multiple objects, sorted by start time and highlighting recommended objects"""
    
    # Ensure times are in local timezone
    milan_tz = get_milan_timezone()
    if start_time.tzinfo != milan_tz:
        start_time = start_time.astimezone(milan_tz)
    if end_time.tzinfo != milan_tz:
        end_time = end_time.astimezone(milan_tz)
    
    # Increase figure size
    fig = plt.figure(figsize=(15, max(10, len(objects)*0.3 + 4)))
    
    # Use gridspec for better layout
    gs = fig.add_gridspec(1, 1)
    gs.update(left=0.15, right=0.95, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])

    # Get visibility periods and sort objects by start time
    object_periods = []
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            # Convert periods to local time
            local_periods = [(p[0].astimezone(milan_tz), p[1].astimezone(milan_tz)) 
                           for p in periods]
            duration = calculate_visibility_duration(periods)
            object_periods.append((obj, local_periods[0][0], duration))
    
    # Sort by start time
    object_periods.sort(key=lambda x: x[1], reverse=True)
    sorted_objects = [item[0] for item in object_periods]
    
    # Setup plot
    ax.set_title(title)
    ax.set_xlabel('Local Time')
    ax.set_ylabel('Objects')
    ax.set_xlim(start_time, end_time)
    
    # Use local time formatter
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=milan_tz))
    
     # Create color map for recommended vs non-recommended objects
    recommended_objects = [obj for _, _, obj in schedule] if schedule else []
    
    # Plot visibility periods
    for i, obj in enumerate(sorted_objects):
        periods = find_visibility_window(obj, start_time, end_time)
        is_recommended = obj in recommended_objects
        has_sufficient_time = getattr(obj, 'sufficient_time', True)
        
        # Determine color based on status
        if not has_sufficient_time:
            color = 'darkmagenta' if is_recommended else 'pink'
        else:
            color = 'green' if is_recommended else 'gray'
        
        for period_start, period_end in periods:
            local_start = period_start.astimezone(milan_tz)
            local_end = period_end.astimezone(milan_tz)
            
            ax.barh(i, local_end - local_start, left=local_start, height=0.3,
                   alpha=0.8 if is_recommended else 0.4,
                   color=color,
                   label=obj.name if period_start == periods[0][0] else "")
                               
            # Add abbreviated name at the start of the bar
            if period_start == periods[0][0]:
                abbreviated_name = get_abbreviated_name(obj.name)
                ax.text(local_start, i, f" {abbreviated_name}", 
                       va='center', ha='left', 
                       fontsize=8,
                       fontweight='bold' if is_recommended else 'normal')
    
    # Customize plot
    ax.set_yticks(range(len(sorted_objects)))
    ax.set_yticklabels([obj.name for obj in sorted_objects])
    ax.grid(True, alpha=GRID_ALPHA)
    
    plt.tight_layout()
    return fig, ax

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
        periods = find_visibility_window(obj, start_time, end_time)
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
    return time.strftime("%H:%M")

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

def print_combined_report(objects, start_time, end_time, bortle_index):
    """Print combined visibility and imaging report"""
    print("\nCombined Visibility and Imaging Report")
    print(f"Bortle Index: {bortle_index}")
    print("=" * 50)
    
    # Collect all object data
    object_data = []
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            duration = calculate_visibility_duration(periods)
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                exposure_time, frames, panels = calculate_required_exposure(
                    obj.magnitude, bortle_index, obj.fov)
                
                object_data.append({
                    'name': obj.name,
                    'start': periods[0][0],
                    'end': periods[-1][1],
                    'duration': duration,
                    'magnitude': obj.magnitude,
                    'exposure': exposure_time,
                    'frames': frames,
                    'panels': panels,
                    'fov': obj.fov
                })
    
    # Sort by visibility start time
    object_data.sort(key=lambda x: x['start'])
    
    # Print sorted report
    for data in object_data:
        print(f"\n{data['name']}")
        print(f"Visibility: {format_time(data['start'])} - {format_time(data['end'])} "
              f"({data['duration']:.1f} hours)")
        print(f"Magnitude: {data['magnitude']}")
        if data['fov']:
            print(f"Field of view: {data['fov']}")
            if data['panels'] > 1:
                print(f"Requires {data['panels']} panels for full coverage")
        print(f"Required exposure: {data['exposure']:.2f} hours "
              f"({data['frames']} frames of {SINGLE_EXPOSURE}s)")
        
        # Add imaging feasibility indication
        if data['exposure'] <= data['duration']:
            print("✓ Sufficient visibility time for imaging")
        else:
            print("✗ Insufficient visibility time for complete imaging "
                  f"(needs {data['exposure']:.1f}h, have {data['duration']:.1f}h)")

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
    # Initialize
    current_date = datetime.now(get_milan_timezone())
    
    # Get night period
    sunset, next_sunrise = find_sunset_sunrise(current_date)
    twilight_evening, twilight_morning = find_astronomical_twilight(current_date)
    
    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
            return
    else:
        all_objects = get_combined_catalog()
    
    #if all_objects:
    #    print_objects_by_type(all_objects, True)

    # Print reports
    print(f"\nNight of {current_date.date()}")
    print(f"Sunset: {format_time(sunset)}")
    print(f"Astronomical twilight begins: {format_time(twilight_evening)}")
    print(f"Astronomical twilight ends: {format_time(twilight_morning)}")
    print(f"Sunrise: {format_time(next_sunrise)}")

    # Filter objects based on imaging requirements
    visible_objects = []
    # Filter objects based on visibility and exposure requirements
    visible_objects, insufficient_objects = filter_visible_objects(
        all_objects, twilight_evening, twilight_morning)
    
    if not visible_objects and not insufficient_objects:
        print("No objects are visible under current conditions")
        return
    
    # Print combined report for all objects
    print_combined_report(visible_objects + insufficient_objects, 
                         twilight_evening, twilight_morning, 
                         BORTLE_INDEX)
    
    if not visible_objects:
        print("\nNo objects have sufficient visibility time for imaging")
        return
        
    # Generate schedules for different strategies
    schedules = {}
    for strategy in SchedulingStrategy:
        ischedule = generate_observation_schedule(
            visible_objects, twilight_evening, twilight_morning,
            strategy=strategy)
        schedules[strategy] = ischedule
        print_schedule_strategy_report(ischedule, strategy)
    
    # Use selected strategy for visualization
    schedule = schedules[SCHEDULING_STRATEGY]
    
    # Create plots
    fig, ax = setup_altaz_plot()
    colors = plt.cm.get_cmap(COLOR_MAP)(np.linspace(0, 1, len(visible_objects)))
    
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
    
    plt.title(f"Object Trajectories for {current_date.date()}")
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
    ax.legend(handles=handles, 
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Objects and Conditions')
    plt.show()
    plt.close(fig)  # Explicitly close the figure
    
    # Create visibility chart
    if not EXCLUDE_INSUFFICIENT_TIME:
        visible_objects.extend(insufficient_objects)
    fig, ax = plot_visibility_chart(visible_objects, twilight_evening, 
                                  twilight_morning, schedule)
    plt.show()
    plt.close(fig)  # Explicitly close the figure

if __name__ == "__main__":
    main()
