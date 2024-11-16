import csv
import re

# Supplementary magnitude data
# Supplementary magnitude data
SUPPLEMENTARY_MAG = {
    'B33': '6.8',
    'GUM 16': '12.0',
    'IC 4604': '5.0',
    'NGC 1333': '5.6',
    'NGC 2024': '10.5',
    'NGC 2170': '10.65',
    'NGC 6188': '5.2',
    'NGC 6357': '10.0',
    'NGC 7822': '8.0',
    'SH2-236': '7.5',     # Using 7.5 as it's brighter than previously listed 7.52
    'SH2-237': '10.0',
    'SH2-234': '10.0',
    'SH2-252': '6.8',     # Using 6.8 as it's brighter than previously listed 6.83
    'SH2-279': '7.0',
    'SH2-292': '15.234'
}
def normalize_name(name):
    name = name.lower()
    # Handle Sharpless catalog variations
    name = re.sub(r'sh2[- ]|sharpless[- ]|sh[- ]2[- ]', 'sh2-', name)
    # Handle Gum catalog
    name = re.sub(r'gum[- ]', 'gum-', name)
    name = re.sub(r'nebula|cluster|galaxy|region|area', '', name)
    name = re.sub(r'-|–|_|\s+', ' ', name)
    name = re.split(r' - ', name)[0]  # Split only on " - " to preserve catalog numbers
    if not name.startswith(('m', 'ngc', 'ic', 'sh2', 'b', 'gum')):
        name = re.sub(r'^the\s+|^great\s+', '', name)
    return name.strip()

def extract_catalog_number(name):
    matches = []
    
    # Match M, NGC, IC with exact numbers
    basic_matches = re.findall(r'(m|ngc|ic)\s*(\d+)', name.lower())
    matches.extend([(prefix.upper(), number.zfill(4)) for prefix, number in basic_matches])
    
    # Match Sharpless catalog numbers
    sh2_matches = re.findall(r'sh2[- ]*(\d+)', name.lower())
    if sh2_matches:
        matches.extend([('Sh2-', num.zfill(3)) for num in sh2_matches])
        
    # Match Barnard (B) catalog numbers
    b_matches = re.findall(r'b[- ]*(\d+)', name.lower())
    if b_matches:
        matches.extend([('B', num.zfill(3)) for num in b_matches])
        
    # Match Gum catalog numbers
    gum_matches = re.findall(r'gum[- ]*(\d+)', name.lower())
    if gum_matches:
        matches.extend([('Gum-', num.zfill(3)) for num in gum_matches])
    
    return matches

def clean_magnitude(mag):
    if not mag: return ''
    return mag.rstrip('p')

def convert_ra(ra):
    if not ra: return ''
    try:
        parts = ra.split()
        if len(parts) == 2:
            hours = parts[0].zfill(2)
            mins = str(int(float(parts[1])))
            return f"{hours}h {mins}m"
    except:
        pass
    return ra

def convert_dec(dec):
    if not dec: return ''
    try:
        parts = dec.split()
        if len(parts) == 2:
            degs = parts[0]
            if not degs.startswith('+') and not degs.startswith('-'):
                degs = '+' + degs
            mins = parts[1].zfill(2)
            return f"{degs}° {mins}'"
    except:
        pass
    return dec

def convert_size_to_fov(size_max, size_min):
    if not size_max or not size_min: return ''
    try:
        max_match = re.match(r'([\d.]+)\s*([msd])', size_max)
        min_match = re.match(r'([\d.]+)\s*([msd])', size_min)
        
        if max_match and min_match:
            max_val = float(max_match.group(1))
            min_val = float(min_match.group(1))
            max_unit = max_match.group(2)
            min_unit = min_match.group(2)
            
            if max_unit == 'm':
                max_val = max_val/60
            elif max_unit == 's':
                max_val = max_val/3600
                
            if min_unit == 'm':
                min_val = min_val/60
            elif min_unit == 's':
                min_val = min_val/3600
                
            return f"{max_val:.1f}°x{min_val:.1f}°"
    except:
        pass
    return ''

# Read Saguaro database
saguaro_db = {}
with open('Sac72.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)
    for row in reader:
        if len(row) >= 12:
            obj_name = row[0].strip()
            other_name = row[1].strip() if len(row) > 1 else ""
            
            catalog_nums = extract_catalog_number(obj_name)
            if catalog_nums:
                for prefix, number in catalog_nums:
                    normalized_name = f"{prefix} {number}"
                    saguaro_db[normalized_name] = {
                        'ra': row[4].strip(),
                        'dec': row[5].strip(),
                        'mag': clean_magnitude(row[6].strip()),
                        'size_max': row[10].strip(),
                        'size_min': row[11].strip(),
                        'other_name': other_name,
                        'original_name': obj_name,
                        'normalized_name': normalize_name(obj_name)
                    }
            else:
                saguaro_db[obj_name] = {
                    'ra': row[4].strip(),
                    'dec': row[5].strip(),
                    'mag': clean_magnitude(row[6].strip()),
                    'size_max': row[10].strip(),
                    'size_min': row[11].strip(),
                    'other_name': other_name,
                    'original_name': obj_name,
                    'normalized_name': normalize_name(obj_name)
                }

# Track objects with missing magnitude
missing_magnitude = []

# Process target CSV
with open('catalog.csv', 'r', encoding='utf-8') as fin, open('catalog_fixed.csv', 'w', newline='', encoding='utf-8') as fout:
    reader = csv.reader(fin, delimiter=';')
    writer = csv.writer(fout, delimiter=';')
    
    header = next(reader)
    writer.writerow(header)
    
    for row in reader:
        obj_name = row[0].strip()
        original_values = {
            'ra': row[3],
            'dec': row[4],
            'fov': row[5],
            'mag': row[6]
        }
        
        normalized_target = normalize_name(obj_name)
        catalog_numbers = extract_catalog_number(obj_name)
        match_found = False
        
        # First try matching catalog numbers
        if catalog_numbers:
            for prefix, number in catalog_numbers:
                search_name = f"{prefix} {number}"
                if search_name in saguaro_db:
                    data = saguaro_db[search_name]
                    match_found = True
                    print(f"\nFound match for {obj_name} -> {data['original_name']} (catalog number match)")
                    
                    # Update values and show changes
                    if data['ra']:
                        new_ra = convert_ra(data['ra'])
                        if new_ra != original_values['ra']:
                            print(f"  RA: {original_values['ra']} -> {new_ra}")
                        row[3] = new_ra
                        
                    if data['dec']:
                        new_dec = convert_dec(data['dec'])
                        if new_dec != original_values['dec']:
                            print(f"  DEC: {original_values['dec']} -> {new_dec}")
                        row[4] = new_dec
                        
                    if data['mag'] and data['mag'] != '99.9':
                        if data['mag'] != original_values['mag']:
                            print(f"  MAG: {original_values['mag']} -> {data['mag']}")
                        row[6] = data['mag']
                        
                    fov = convert_size_to_fov(data['size_max'], data['size_min'])
                    if fov and fov != original_values['fov']:
                        print(f"  FOV: {original_values['fov']} -> {fov}")
                        row[5] = fov
                    break
        
        # If no match found, try normalized name matching
        if not match_found:
            for sag_name, data in saguaro_db.items():
                if (normalized_target in normalize_name(sag_name) or 
                    normalize_name(sag_name) in normalized_target):
                    match_found = True
                    print(f"\nFound match for {obj_name} -> {data['original_name']} (name match)")
                    
                    # Update values and show changes
                    if data['ra']:
                        new_ra = convert_ra(data['ra'])
                        if new_ra != original_values['ra']:
                            print(f"  RA: {original_values['ra']} -> {new_ra}")
                        row[3] = new_ra
                        
                    if data['dec']:
                        new_dec = convert_dec(data['dec'])
                        if new_dec != original_values['dec']:
                            print(f"  DEC: {original_values['dec']} -> {new_dec}")
                        row[4] = new_dec
                        
                    if data['mag'] and data['mag'] != '99.9':
                        if data['mag'] != original_values['mag']:
                            print(f"  MAG: {original_values['mag']} -> {data['mag']}")
                        row[6] = data['mag']
                        
                    fov = convert_size_to_fov(data['size_max'], data['size_min'])
                    if fov and fov != original_values['fov']:
                        print(f"  FOV: {original_values['fov']} -> {fov}")
                        row[5] = fov
                    break
        
        if not match_found:
            print(f"\nNo match found for: {obj_name}")
            
        # Check for supplementary magnitude if needed
        if row[6] == '-':
            # Try to find in supplementary data
            for supp_name, supp_mag in SUPPLEMENTARY_MAG.items():
                if supp_name.lower() in normalized_target:
                    print(f"  Using supplementary magnitude: {supp_mag}")
                    row[6] = supp_mag
                    break
            
            # If still no magnitude, add to missing list
            if row[6] == '-':
                missing_magnitude.append(obj_name)
                
        writer.writerow(row)

print("\nProcessing complete. Check catalog_fixed.csv for results.")
print("\nObjects with missing magnitude:")
for obj in missing_magnitude:
    print(f"- {obj}")
