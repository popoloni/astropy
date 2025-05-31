"""
CSV catalog reading and management functions.
"""

import csv
from models import CelestialObject
from config import CATALOGNAME, MIN_TOTAL_AREA, MERGING_CATALOGS
from .object_utils import enrich_object_name
from .catalog_manager import get_combined_catalog, merge_catalogs


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
    
    # Import parsing functions here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from astropy import parse_ra, parse_dec
    
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
    
    # If merge is enabled or CSV read failed, get built-in catalog
    merge_enabled = MERGING_CATALOGS
    
    if merge_enabled or not csv_objects:
        builtin_objects = get_combined_catalog()
        
        if merge_enabled and csv_objects:
            return merge_catalogs(csv_objects, builtin_objects)
        else:
            return builtin_objects
    
    # If we have CSV objects and merge is not enabled, return just those
    return csv_objects 