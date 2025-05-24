import json
import math
from datetime import datetime

def ra_to_hrs(ra):
    ra = ra * 24 / 360
    hours = int(ra)
    minutes = int((ra - hours) * 60)
    return f"{hours:02d}h {minutes:02d}m"

def dec_to_deg(dec):
    degrees = int(dec)
    minutes = int(abs((dec - degrees) * 60))
    sign = '-' if dec < 0 else '+'
    return f"{sign}{abs(degrees):02d}° {minutes:02d}'"

def calculate_ideal_date(ra):
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    days_in_year = 365
    
    days = (ra / 360) * days_in_year
    target_day = days + 80  # March 21 is day 80
    
    month = 1
    while target_day > month_days[month-1]:
        target_day -= month_days[month-1]
        month += 1
        if month > 12:
            month = 1
    
    return f"{int(target_day):02d}-{datetime.strptime(str(month), '%m').strftime('%b')}"

def get_object_type(category):
    type_mapping = {
        'nebula-planetary': 'Pl Neb',
        'nebula-emission': 'Em Neb',
        'nebula-reflexion': 'Ref Neb',
        'nebula-dark': 'Dark Neb',
        'nebula-emission-reflexion': 'Em+Ref Neb',
        'nebula-cluster-open': 'Neb+OCl',
        'nebula-remanent': 'SNR',
        'cluster-open': 'O Clus',
        'cluster-globular': 'Gl Clus',
        'galaxy-spiral': 'Gal',
        'galaxy-lenticular': 'Gal',
        'galaxy-eliptic': 'Gal',
        'galaxy-group': 'Gal Grp'
    }
    return type_mapping.get(category, 'Other')

def build_complete_name(obj):
    names = []
    
    # Add Messier number
    if 'idMessier' in obj:
        names.append(f"M{obj['idMessier']}")
    
    # Add NGC number
    if 'idNgc' in obj:
        names.append(f"NGC {obj['idNgc']}")
    
    # Add IC number
    if 'idIc' in obj:
        names.append(f"IC {obj['idIc']}")
    
    # Add common name or ID if different from catalog numbers
    if obj['id'] not in [f"M{obj.get('idMessier')}", f"NGC{obj.get('idNgc')}", f"IC{obj.get('idIc')}"]:
        if not any(cat_num in obj['id'] for cat_num in ['NGC', 'IC', 'M']):
            names.append(obj['id'])
    
    return ' / '.join(names) if names else obj['id']

def calculate_fov(obj):
    """Calculate FOV from object size"""
    if 'size' not in obj:
        return None
        
    size = obj['size']
    if isinstance(size, (int, float)):
        # Convert to degrees if size is large
        if size > 60:
            return f"{size/60:.1f}°x{size/60:.1f}°"
        else:
            return f"{size}'x{size}'"
            
    return None

def format_magnitude(magnitude):
    """Format magnitude ensuring a valid number"""
    if magnitude is None or magnitude == '':
        return '99.9'  # Standard value for unknown magnitude
    try:
        return f"{float(magnitude):.1f}"
    except (ValueError, TypeError):
        return '99.9'

def main():
    import os
    import shutil
    
    # Get the directory paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    catalogs_dir = os.path.join(parent_dir, 'catalogs')
    
    # Safety check: backup existing CSV if it exists
    csv_path = os.path.join(catalogs_dir, 'objects.csv')
    if os.path.exists(csv_path):
        backup_path = csv_path + '.backup'
        shutil.copy2(csv_path, backup_path)
        print(f"Created backup: {backup_path}")
    
    # Load JSON files
    json_path = os.path.join(catalogs_dir, 'objects.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        objects = json.load(f)

    # Create CSV header
    csv_lines = ['Object;Type;Ideal Date;RA;Dec;FOV;Magnitude;Comments']
    
    # Process each object
    for obj in objects:
        if 'category' not in obj:
            continue
            
        # Calculate FOV first - skip if no size
        fov = calculate_fov(obj)
        if fov is None:
            continue
            
        # Get basic object properties
        category = obj.get('category', '')
        ra = obj.get('ra', 0)
        dec = obj.get('de', 0)
        magnitude = format_magnitude(obj.get('magnitude'))
        
        # Build complete object name
        name = build_complete_name(obj)
            
        # Build comments
        comments = []
        if 'discoveredBy' in obj and obj['discoveredBy'] != 'N/A':
            comments.append(f"Discovered by {obj['discoveredBy']}")
        if 'discoveredIn' in obj and obj['discoveredIn'] != 'N/A':
            comments.append(f"in {obj['discoveredIn']}")
        if 'realSize' in obj and 'realSizeUnit' in obj:
            comments.append(f"Real size: {obj['realSize']} {obj['realSizeUnit']}")
        if 'distance' in obj and 'distanceUnit' in obj:
            comments.append(f"Distance: {obj['distance']} {obj['distanceUnit']}")
            
        # Format CSV line
        csv_line = [
            name,
            get_object_type(category),
            calculate_ideal_date(ra),
            ra_to_hrs(ra),
            dec_to_deg(dec),
            fov,
            magnitude,
            '. '.join(comments)
        ]
        
        csv_lines.append(';'.join(str(x) for x in csv_line))
    
    # Write CSV file
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines))
    
    print(f"Successfully converted {len(csv_lines)-1} objects to {csv_path}")

if __name__ == '__main__':
    main()
