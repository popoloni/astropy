"""
Utility functions for working with celestial objects.
"""

import re
from datetime import datetime


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


def enrich_object_name(name):
    """Add common names and cross-references to object names"""
    # Import here to avoid circular imports
    from .messier import get_messier_catalog
    from .dso import get_additional_dso
    
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


def get_object_by_name(name, catalog=None):
    """Find object in catalog by name"""
    if catalog is None:
        from .catalog_manager import get_combined_catalog
        catalog = get_combined_catalog()
    
    for obj in catalog:
        if obj.name.lower().startswith(name.lower()):
            return obj
    return None


def get_objects_by_type(obj_type, catalog=None):
    """Get objects of specific type from catalog"""
    if catalog is None:
        from .catalog_manager import get_combined_catalog
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
    # Import here to avoid circular imports
    from config import get_local_timezone
    from datetime import datetime
    
    if time is None:
        time = datetime.now(get_local_timezone())
    
    def get_altitude(obj):
        # Import here to avoid circular imports during refactoring
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from astronightplanner import calculate_altaz
        alt, _ = calculate_altaz(obj, time)
        return alt
    
    return sorted(objects, key=get_altitude, reverse=True) 