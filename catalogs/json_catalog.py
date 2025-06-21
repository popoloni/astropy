"""
JSON catalog reading and management functions.
Provides JSON-based catalog functionality without modifying existing CSV catalog code.
"""

import json
import math
import os
from models import CelestialObject


def load_json_catalogs():
    """Load all JSON catalog files"""
    catalogs = {}
    catalog_dir = os.path.dirname(__file__)
    
    json_files = {
        'objects': 'objects.json',
        'simbad': 'simbad-objects.json', 
        'nebula_paths': 'nebula-paths.json',
        'constellations': 'constellations.json'
    }
    
    for key, filename in json_files.items():
        filepath = os.path.join(catalog_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                catalogs[key] = json.load(f)
                print(f"Loaded {len(catalogs[key])} entries from {filename}")
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            catalogs[key] = []
    
    return catalogs


def calculate_fov_from_json(obj, nebula_boundaries=None):
    """Calculate FOV string from JSON object data using improved accuracy"""
    
    # Use the improved FOV calculator
    try:
        from catalogs.improved_fov_calculator import calculate_accurate_fov, load_nebula_boundaries
        
        if nebula_boundaries is None:
            # Load nebula boundaries if not provided (cache for efficiency)
            nebula_boundaries = load_nebula_boundaries()
        
        fov, method = calculate_accurate_fov(obj, nebula_boundaries)
        return fov
    except ImportError:
        # Fallback to basic calculation if improved calculator not available
        return calculate_fov_basic(obj)


def calculate_fov_basic(obj):
    """Basic FOV calculation (fallback)"""
    # First try to get size from 'size' field (in arcminutes)
    if 'size' in obj and obj['size']:
        size = obj['size']
        category = obj.get('category', '').lower()
        
        # Apply aspect ratio based on category
        if 'galaxy' in category:
            width = size
            height = size * 0.6  # Galaxies often elongated
        elif 'nebula' in category and 'planetary' not in category:
            width = size
            height = size * 0.8  # Nebulae slightly elongated
        else:
            width = height = size  # Assume circular
            
        return f"{width:.1f}'x{height:.1f}'"
    
    # Then try ellipse data from SIMBAD
    if 'ellipse' in obj and obj['ellipse']:
        ellipse = obj['ellipse']
        if 'a' in ellipse and 'b' in ellipse:
            # Convert from degrees to arcminutes (full axis)
            a_arcmin = ellipse['a'] * 2 * 60
            b_arcmin = ellipse['b'] * 2 * 60
            return f"{a_arcmin:.1f}'x{b_arcmin:.1f}'"
    
    # Fallback: try to infer from object type and magnitude
    mag = obj.get('magnitude', 10)
    category = obj.get('category', '').lower()
    
    # Improved category-based estimation
    if 'star' in category:
        return "10.0'x10.0'"
    elif 'nebula-planetary' in category:
        if mag < 9:
            return "4.0'x4.0'"
        elif mag < 12:
            return "2.0'x2.0'"
        else:
            return "1.0'x1.0'"
    elif 'nebula' in category:
        if mag < 6:
            return "60.0'x50.0'"
        elif mag < 8:
            return "30.0'x25.0'"
        else:
            return "15.0'x12.0'"
    elif 'galaxy' in category:
        if 'group' in category:
            return "120.0'x90.0'"
        elif mag < 8:
            return "25.0'x15.0'"
        elif mag < 10:
            return "12.0'x8.0'"
        else:
            return "6.0'x4.0'"
    elif 'cluster-globular' in category:
        if mag < 6:
            return "25.0'x25.0'"
        elif mag < 8:
            return "15.0'x15.0'"
        else:
            return "8.0'x8.0'"
    elif 'cluster-open' in category:
        if mag < 4:
            return "60.0'x60.0'"
        elif mag < 6:
            return "30.0'x30.0'"
        else:
            return "20.0'x20.0'"
    
    # Default fallback
    return "10.0'x10.0'"


def map_json_category_to_csv_type(category):
    """Map JSON categories to CSV type strings"""
    if not category:
        return "Other"
    
    category = category.lower()
    
    # Nebula types
    if 'nebula-planetary' in category:
        return "Pl Neb"
    elif 'nebula-emission' in category:
        return "Em Neb"
    elif 'nebula-reflection' in category:
        return "Ref Neb"
    elif 'nebula-dark' in category:
        return "Dark Neb"
    elif 'nebula' in category:
        return "Em Neb"  # Default nebula type
    
    # Galaxy types
    elif 'galaxy' in category:
        if 'group' in category:
            return "Gal Grp"
        else:
            return "Gal"
    
    # Cluster types
    elif 'cluster-globular' in category:
        return "Gl Clus"
    elif 'cluster-open' in category:
        return "O Clus"
    elif 'cluster' in category:
        return "O Clus"  # Default cluster type
    
    # Special types
    elif 'star' in category:
        return "Star"
    elif 'supernova' in category:
        return "SNR"
    
    return "Other"


def calculate_ideal_date_from_ra(ra_deg):
    """Calculate optimal viewing date from RA (rough approximation)"""
    # RA 0° is best viewed around September 22 (day 265)
    # RA 180° is best viewed around March 21 (day 80)  
    # Linear interpolation for simplicity
    
    # Normalize RA to 0-360 range
    ra_norm = ra_deg % 360
    
    # Calculate day of year when object transits at midnight
    # RA advances ~1° per day, starting from Sept 22
    base_day = 265  # Sept 22
    day_offset = ra_norm  # Rough approximation
    
    optimal_day = (base_day + day_offset) % 365
    
    # Convert to month-day format
    months = [
        ("Jan", 31), ("Feb", 28), ("Mar", 31), ("Apr", 30),
        ("May", 31), ("Jun", 30), ("Jul", 31), ("Aug", 31),
        ("Sep", 30), ("Oct", 31), ("Nov", 30), ("Dec", 31)
    ]
    
    day_count = optimal_day
    for month, days in months:
        if day_count <= days:
            return f"{int(day_count):02d}-{month}"
        day_count -= days
    
    return "01-Jan"  # Fallback


def build_enhanced_name(obj, simbad_data=None):
    """Build complete name with common names and catalog IDs"""
    name_parts = []
    
    # Start with primary ID
    primary_id = obj.get('id', '')
    if primary_id:
        name_parts.append(primary_id)
    
    # Add NGC/IC number if available and not already in ID
    ngc_id = obj.get('idNgc', '')
    if ngc_id and ngc_id not in primary_id:
        if ngc_id.isdigit():
            name_parts.append(f"NGC {ngc_id}")
        else:
            name_parts.append(ngc_id)
    
    # Add common name from SIMBAD data if available
    if simbad_data:
        for simbad_obj in simbad_data:
            # Try to match by catalog ID or coordinates
            if ('catalogId' in simbad_obj and 
                simbad_obj.get('catalogId', '').lower() == primary_id.lower()):
                common_name = simbad_obj.get('commonName', '')
                if common_name and common_name not in ' / '.join(name_parts):
                    name_parts.append(common_name)
                break
    
    # Join with ' / ' separator (matching CSV format)
    if len(name_parts) > 1:
        return ' / '.join(name_parts)
    elif name_parts:
        return name_parts[0]
    else:
        return "Unknown Object"


def convert_json_coordinates(ra_deg, dec_deg):
    """Convert JSON decimal degrees to format expected by CelestialObject"""
    # CelestialObject expects RA in hours, Dec in degrees
    ra_hours = ra_deg / 15.0
    return ra_hours, dec_deg


def merge_object_data(objects_json, simbad_json):
    """Merge objects.json and simbad-objects.json for enhanced data"""
    merged_objects = []
    
    # Create lookup dict for SIMBAD data by various IDs
    simbad_lookup = {}
    for simbad_obj in simbad_json:
        # Index by common name, catalogId, and NGC ID
        if 'commonName' in simbad_obj:
            simbad_lookup[simbad_obj['commonName'].lower()] = simbad_obj
        if 'catalogId' in simbad_obj:
            simbad_lookup[simbad_obj['catalogId'].lower()] = simbad_obj
        if 'idNgc' in simbad_obj:
            simbad_lookup[f"ngc{simbad_obj['idNgc']}"] = simbad_obj
    
    # Process objects.json entries
    for obj in objects_json:
        # Try to find matching SIMBAD data
        obj_id = obj.get('id', '').lower()
        simbad_match = simbad_lookup.get(obj_id)
        
        if not simbad_match and 'idNgc' in obj:
            ngc_key = f"ngc{obj['idNgc']}"
            simbad_match = simbad_lookup.get(ngc_key)
        
        # Merge data, preferring objects.json for primary data
        merged_obj = obj.copy()
        if simbad_match:
            # Add ellipse data if not present
            if 'ellipse' in simbad_match and 'size' not in merged_obj:
                merged_obj['ellipse'] = simbad_match['ellipse']
            # Add common name if available
            if 'commonName' in simbad_match:
                merged_obj['commonName'] = simbad_match['commonName']
        
        merged_objects.append(merged_obj)
    
    # Add unique SIMBAD objects not in objects.json
    objects_ids = {obj.get('id', '').lower() for obj in objects_json}
    objects_ngc_ids = {f"ngc{obj.get('idNgc', '')}" for obj in objects_json if 'idNgc' in obj}
    
    for simbad_obj in simbad_json:
        # Skip if already included from objects.json
        simbad_id = simbad_obj.get('catalogId', '').lower()
        simbad_ngc = f"ngc{simbad_obj.get('idNgc', '')}" if 'idNgc' in simbad_obj else ''
        
        if (simbad_id not in objects_ids and 
            simbad_ngc not in objects_ngc_ids and
            'ra' in simbad_obj and 'de' in simbad_obj):
            
            # Convert SIMBAD object to objects.json format
            converted_obj = {
                'id': simbad_obj.get('catalogId', simbad_obj.get('commonName', 'Unknown')),
                'ra': simbad_obj['ra'],
                'de': simbad_obj['de'],
                'magnitude': simbad_obj.get('magnitude', 10.0),
                'category': simbad_obj.get('category', 'other'),
                'ellipse': simbad_obj.get('ellipse'),
                'commonName': simbad_obj.get('commonName')
            }
            
            if 'idNgc' in simbad_obj:
                converted_obj['idNgc'] = simbad_obj['idNgc']
            
            merged_objects.append(converted_obj)
    
    return merged_objects


def get_objects_from_json():
    """Get objects from JSON catalogs in same format as CSV catalog"""
    from config import MIN_TOTAL_AREA
    
    # Load all JSON catalogs
    catalogs = load_json_catalogs()
    
    objects_data = catalogs['objects']
    simbad_data = catalogs['simbad']
    
    # Merge data from multiple sources
    merged_objects = merge_object_data(objects_data, simbad_data)
    
    # Load nebula boundaries once for efficiency
    try:
        from catalogs.improved_fov_calculator import load_nebula_boundaries
        nebula_boundaries = load_nebula_boundaries()
    except ImportError:
        nebula_boundaries = None
    
    json_objects = []
    skipped_count = 0
    
    # Convert MIN_TOTAL_AREA from square arcminutes to square degrees
    # MIN_TOTAL_AREA appears to be in square arcminutes, convert to square degrees
    min_area_deg2 = MIN_TOTAL_AREA / 3600.0  # 1 degree = 60 arcmin, so 1 deg² = 3600 arcmin²
    
    for obj in merged_objects:
        try:
            # Get coordinates
            ra_deg = obj.get('ra', 0)
            dec_deg = obj.get('de', 0)
            
            if ra_deg == 0 and dec_deg == 0:
                skipped_count += 1
                continue
            
            # Convert coordinates 
            ra_hours, dec_deg = convert_json_coordinates(ra_deg, dec_deg)
            
            # Calculate FOV with improved accuracy
            fov = calculate_fov_from_json(obj, nebula_boundaries)
            
            # Get magnitude
            magnitude = obj.get('magnitude')
            if magnitude is None:
                magnitude = 10.0
            
            # Build enhanced name
            name = build_enhanced_name(obj, simbad_data)
            
            # Create CelestialObject
            celestial_obj = CelestialObject(name, ra_hours, dec_deg, fov, magnitude)
            
            # Add additional attributes for compatibility
            celestial_obj.json_category = obj.get('category', 'other')
            celestial_obj.csv_type = map_json_category_to_csv_type(obj.get('category', ''))
            celestial_obj.ideal_date = calculate_ideal_date_from_ra(ra_deg)
            
            # Add comments if discoverer info available
            comments = []
            if 'discoveredBy' in obj and obj['discoveredBy'] not in ['N/A', '']:
                comments.append(f"Discovered by {obj['discoveredBy']}")
            if 'discoveredIn' in obj and obj['discoveredIn'] not in ['N/A', '']:
                comments.append(f"in {obj['discoveredIn']}")
            if 'realSize' in obj and 'realSizeUnit' in obj:
                comments.append(f"Real size: {obj['realSize']} {obj['realSizeUnit']}")
            if 'distance' in obj and 'distanceUnit' in obj:
                comments.append(f"Distance: {obj['distance']} {obj['distanceUnit']}")
            
            if comments:
                celestial_obj.comments = '. '.join(comments)
            
            # Only add objects that meet the area threshold (converted to degrees²)
            # Also be more lenient for JSON catalog initially
            if celestial_obj.total_area >= min_area_deg2 or not fov or celestial_obj.total_area >= 0.01:  # 0.01 deg² = 36 arcmin²
                json_objects.append(celestial_obj)
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"Error processing object {obj.get('id', 'unknown')}: {e}")
            skipped_count += 1
            continue
    
    print(f"JSON catalog: {len(json_objects)} objects loaded, {skipped_count} skipped")
    print(f"Area threshold: {MIN_TOTAL_AREA} arcmin² = {min_area_deg2:.4f} deg²")
    return json_objects


def get_object_type_from_json(category):
    """Get object type category for compatibility with existing code"""
    if not category:
        return 'other'
    
    category = category.lower()
    
    if 'nebula' in category:
        if 'emission' in category:
            return 'emission_nebula'
        elif 'reflection' in category:
            return 'reflection_nebula' 
        elif 'planetary' in category:
            return 'planetary_nebula'
        elif 'dark' in category:
            return 'dark_nebula'
        else:
            return 'nebula'
    elif 'galaxy' in category:
        return 'galaxy'
    elif 'globular' in category:
        return 'globular_cluster'
    elif 'cluster' in category and 'open' in category:
        return 'open_cluster'
    elif 'cluster' in category:
        return 'open_cluster'  # Default cluster type
    else:
        return 'other'


def get_objects_from_json_by_type():
    """Get objects from JSON organized by type (matching CSV function interface)"""
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
    
    json_objects = get_objects_from_json()
    
    for obj in json_objects:
        obj_type = get_object_type_from_json(obj.json_category)
        objects_by_type[obj_type].append(obj)
    
    return objects_by_type 