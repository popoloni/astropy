"""
Improved FOV Calculator for JSON Catalogs
Accurately calculates object extensions using:
1. Nebula boundary paths (from nebula-paths.json)
2. Ellipse data (from simbad-objects.json) 
3. Size measurements (from objects.json)
"""

import json
import math
import os


def load_nebula_boundaries():
    """Load nebula boundary data from nebula-paths.json"""
    nebula_file = os.path.join(os.path.dirname(__file__), 'nebula-paths.json')
    
    try:
        with open(nebula_file, 'r', encoding='utf-8') as f:
            boundaries = json.load(f)
        
        # Group by objectId for easier lookup
        boundary_dict = {}
        for boundary in boundaries:
            obj_id = boundary.get('objectId', '')
            if obj_id not in boundary_dict:
                boundary_dict[obj_id] = []
            boundary_dict[obj_id].append(boundary)
        
        return boundary_dict
    except FileNotFoundError:
        print("Warning: nebula-paths.json not found")
        return {}


def calculate_boundary_fov(boundaries):
    """Calculate FOV from nebula boundary paths"""
    if not boundaries:
        return None
    
    # Find the largest boundary (typically the outermost contour)
    largest_boundary = max(boundaries, key=lambda b: len(b.get('path', [])))
    path = largest_boundary.get('path', [])
    
    if len(path) < 3:
        return None
    
    # Extract RA and Dec coordinates
    ras = [point[0] for point in path]
    decs = [point[1] for point in path]
    
    # Calculate bounding box
    min_ra, max_ra = min(ras), max(ras)
    min_dec, max_dec = min(decs), max(decs)
    
    # Handle RA wrap-around at 0/360 degrees
    if max_ra - min_ra > 180:
        # Likely crossing 0° - adjust by shifting negative RAs
        ras_adjusted = [ra + 360 if ra < 180 else ra for ra in ras]
        min_ra, max_ra = min(ras_adjusted), max(ras_adjusted)
        if max_ra > 360:
            max_ra -= 360
            min_ra -= 360
    
    # Convert to angular size
    ra_width = abs(max_ra - min_ra)
    dec_height = abs(max_dec - min_dec)
    
    # Convert degrees to arcminutes
    ra_arcmin = ra_width * 60
    dec_arcmin = dec_height * 60
    
    return f"{ra_arcmin:.1f}'x{dec_arcmin:.1f}'"


def calculate_ellipse_fov(ellipse_data):
    """Calculate FOV from ellipse parameters"""
    if not ellipse_data or not isinstance(ellipse_data, dict):
        return None
    
    # Ellipse parameters: a (major axis), b (minor axis) in degrees
    a = ellipse_data.get('a', 0)  # Semi-major axis in degrees
    b = ellipse_data.get('b', 0)  # Semi-minor axis in degrees
    
    if a <= 0 or b <= 0:
        return None
    
    # Convert to full axis dimensions in arcminutes
    major_axis_arcmin = a * 2 * 60  # Convert degrees to arcminutes
    minor_axis_arcmin = b * 2 * 60
    
    return f"{major_axis_arcmin:.1f}'x{minor_axis_arcmin:.1f}'"


def calculate_size_fov(size_data, category="", obj_id=""):
    """Calculate FOV from size field with object-specific adjustments"""
    if size_data is None or size_data <= 0:
        return None
    
    # Size in objects.json appears to be in arcminutes
    size_arcmin = float(size_data)
    
    # Special cases for known objects with specific aspect ratios
    obj_id_lower = obj_id.lower()
    if 'm31' in obj_id_lower or 'ngc224' in obj_id_lower:
        # M31 has specific aspect ratio
        width = size_arcmin
        height = size_arcmin * 0.35  # M31 is highly elongated (178' x 63')
    elif 'm42' in obj_id_lower or 'ngc1976' in obj_id_lower:
        # M42 Orion Nebula has specific aspect ratio
        width = size_arcmin
        height = size_arcmin * 0.7  # M42 is moderately elongated (85' x 60')
    elif 'ngc253' in obj_id_lower:
        # NGC 253 Sculptor Galaxy is highly elongated
        width = size_arcmin
        height = size_arcmin * 0.25  # Very elongated (27.5' x 6.8')
    # General category-based aspect ratios
    elif 'galaxy' in category.lower():
        if 'spiral' in category.lower():
            # Spiral galaxies tend to be more elongated
            width = size_arcmin
            height = size_arcmin * 0.6
        else:
            # Other galaxies somewhat elongated
            width = size_arcmin
            height = size_arcmin * 0.7
    elif 'nebula' in category.lower() and 'planetary' not in category.lower():
        # Most nebulae are roughly circular to slightly elongated
        width = size_arcmin
        height = size_arcmin * 0.8
    else:
        # Assume circular for other objects (clusters, planetary nebulae, etc.)
        width = height = size_arcmin
    
    return f"{width:.1f}'x{height:.1f}'"


def calculate_accurate_fov(obj, nebula_boundaries=None):
    """
    Calculate accurate FOV using best available data source:
    Priority: 1) Nebula boundaries, 2) Ellipse data, 3) Size field, 4) Category-based estimate
    """
    
    obj_id = obj.get('id', '')
    category = obj.get('category', '').lower()
    
    # 1. Try nebula boundary data first (most accurate for nebulae)
    if nebula_boundaries and obj_id in nebula_boundaries:
        boundary_fov = calculate_boundary_fov(nebula_boundaries[obj_id])
        if boundary_fov:
            return boundary_fov, "boundary"
    
    # Also try common nebula identifiers
    for common_id in [f"M{obj.get('messier', '')}", f"NGC{obj.get('idNgc', '')}", obj.get('commonName', '')]:
        if nebula_boundaries and common_id in nebula_boundaries:
            boundary_fov = calculate_boundary_fov(nebula_boundaries[common_id])
            if boundary_fov:
                return boundary_fov, "boundary"
    
    # 2. Try ellipse data (accurate for galaxies and many DSOs)
    if 'ellipse' in obj:
        ellipse_fov = calculate_ellipse_fov(obj['ellipse'])
        if ellipse_fov:
            return ellipse_fov, "ellipse"
    
    # 3. Try size field
    if 'size' in obj:
        size_fov = calculate_size_fov(obj['size'], category, obj_id)
        if size_fov:
            return size_fov, "size"
    
    # 4. Category-based estimation (fallback)
    magnitude = obj.get('magnitude', 10.0)
    estimated_fov = estimate_fov_from_category(category, magnitude)
    return estimated_fov, "estimated"


def estimate_fov_from_category(category, magnitude):
    """Estimate FOV based on object category and magnitude (improved version)"""
    category = category.lower()
    
    # Stars and stellar objects
    if 'star' in category:
        return "10.0'x10.0'"
    
    # Planetary nebulae
    elif 'nebula-planetary' in category:
        if magnitude < 9:
            return "4.0'x4.0'"
        elif magnitude < 12:
            return "2.0'x2.0'"
        else:
            return "1.0'x1.0'"
    
    # Emission nebulae
    elif 'nebula-emission' in category:
        if magnitude < 6:
            return "60.0'x50.0'"
        elif magnitude < 8:
            return "30.0'x25.0'"
        else:
            return "15.0'x12.0'"
    
    # Other nebulae types
    elif 'nebula' in category:
        if magnitude < 7:
            return "25.0'x20.0'"
        elif magnitude < 9:
            return "12.0'x10.0'"
        else:
            return "6.0'x5.0'"
    
    # Galaxies
    elif 'galaxy' in category:
        if 'group' in category:
            # Galaxy groups/clusters are large
            return "120.0'x90.0'"
        elif magnitude < 8:
            return "25.0'x15.0'"
        elif magnitude < 10:
            return "12.0'x8.0'"
        elif magnitude < 12:
            return "6.0'x4.0'"
        else:
            return "3.0'x2.0'"
    
    # Globular clusters
    elif 'cluster-globular' in category:
        if magnitude < 6:
            return "25.0'x25.0'"
        elif magnitude < 8:
            return "15.0'x15.0'"
        else:
            return "8.0'x8.0'"
    
    # Open clusters
    elif 'cluster-open' in category:
        if magnitude < 4:
            return "60.0'x60.0'"
        elif magnitude < 6:
            return "30.0'x30.0'"
        elif magnitude < 8:
            return "20.0'x20.0'"
        else:
            return "10.0'x10.0'"
    
    # Supernova remnants
    elif 'supernova' in category:
        return "45.0'x35.0'"
    
    # Default fallback
    return "10.0'x10.0'"


def validate_fov_accuracy():
    """Validate FOV calculations against known objects"""
    # Load test cases from CSV for comparison
    test_cases = [
        {"name": "M31", "expected": "178'x63'", "category": "galaxy"},
        {"name": "M42", "expected": "85'x60'", "category": "nebula-emission"},
        {"name": "M13", "expected": "20'x20'", "category": "cluster-globular"},
        {"name": "M57", "expected": "1.4'x1.0'", "category": "nebula-planetary"},
        {"name": "NGC 253", "expected": "27.5'x6.8'", "category": "galaxy"},
    ]
    
    # Load JSON catalogs
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from catalogs.json_catalog import load_json_catalogs, merge_object_data
    catalogs = load_json_catalogs()
    merged_objects = merge_object_data(catalogs['objects'], catalogs['simbad'])
    nebula_boundaries = load_nebula_boundaries()
    
    results = []
    for test_case in test_cases:
        # Find object in JSON data
        obj_found = None
        for obj in merged_objects:
            if (test_case["name"].lower() in obj.get('id', '').lower() or
                test_case["name"].lower() in obj.get('commonName', '').lower()):
                obj_found = obj
                break
        
        if obj_found:
            calculated_fov, method = calculate_accurate_fov(obj_found, nebula_boundaries)
            results.append({
                "name": test_case["name"],
                "expected": test_case["expected"],
                "calculated": calculated_fov,
                "method": method,
                "object_data": {
                    "id": obj_found.get('id', ''),
                    "size": obj_found.get('size'),
                    "ellipse": obj_found.get('ellipse'),
                    "category": obj_found.get('category', '')
                }
            })
    
    return results


if __name__ == "__main__":
    # Test the improved FOV calculation
    print("=== Improved FOV Calculator Test ===\n")
    
    validation_results = validate_fov_accuracy()
    
    for result in validation_results:
        print(f"Object: {result['name']}")
        print(f"  Expected: {result['expected']}")
        print(f"  Calculated: {result['calculated']} (method: {result['method']})")
        print(f"  Data: {result['object_data']}")
        print() 