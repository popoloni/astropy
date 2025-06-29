#!/usr/bin/env python3
"""
Catalog Comparison Tool
Compares JSON and CSV catalogs to validate the JSON implementation.
"""

import math
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def compare_coordinates(ra1, dec1, ra2, dec2, threshold=0.1):
    """Compare two coordinate pairs and return angular separation in degrees"""
    # Convert all to radians for calculation
    ra1_rad = math.radians(ra1 * 15) if ra1 < 24 else math.radians(ra1)  # Handle hours vs degrees
    dec1_rad = math.radians(dec1)
    ra2_rad = math.radians(ra2 * 15) if ra2 < 24 else math.radians(ra2)
    dec2_rad = math.radians(dec2)
    
    # Angular separation using spherical law of cosines
    cos_sep = (math.sin(dec1_rad) * math.sin(dec2_rad) + 
               math.cos(dec1_rad) * math.cos(dec2_rad) * math.cos(ra1_rad - ra2_rad))
    
    # Clamp to valid range to avoid numerical errors
    cos_sep = max(-1, min(1, cos_sep))
    separation = math.degrees(math.acos(cos_sep))
    
    return separation < threshold, separation


def normalize_name_for_matching(name):
    """Normalize object name for fuzzy matching"""
    if not name:
        return ""
    
    # Convert to lowercase and remove extra spaces
    normalized = name.lower().strip()
    
    # Remove common prefixes/suffixes
    normalized = normalized.replace('ngc ', 'ngc')
    normalized = normalized.replace('ic ', 'ic') 
    normalized = normalized.replace('messier ', 'm')
    normalized = normalized.replace('m ', 'm')
    
    # Remove special characters except numbers and letters
    import re
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    
    return normalized


def extract_catalog_numbers(name):
    """Extract catalog numbers (NGC, IC, M) from object name"""
    import re
    numbers = []
    
    # NGC numbers
    ngc_matches = re.findall(r'ngc\s*(\d+)', name.lower())
    for match in ngc_matches:
        numbers.append(f"ngc{match}")
    
    # IC numbers
    ic_matches = re.findall(r'ic\s*(\d+)', name.lower())
    for match in ic_matches:
        numbers.append(f"ic{match}")
    
    # Messier numbers
    m_matches = re.findall(r'm\s*(\d+)', name.lower())
    for match in m_matches:
        numbers.append(f"m{match}")
    
    return numbers


def find_matching_objects(csv_objects, json_objects):
    """Find matching objects between CSV and JSON catalogs"""
    matches = []
    csv_unmatched = []
    json_unmatched = list(json_objects)  # Start with all JSON objects
    
    for csv_obj in csv_objects:
        best_match = None
        best_score = float('inf')
        
        # Try exact name matching first
        csv_norm = normalize_name_for_matching(csv_obj.name)
        csv_catalogs = extract_catalog_numbers(csv_obj.name)
        
        for i, json_obj in enumerate(json_unmatched):
            json_norm = normalize_name_for_matching(json_obj.name)
            json_catalogs = extract_catalog_numbers(json_obj.name)
            
            # Check for name similarity
            name_match = False
            if csv_norm == json_norm:
                name_match = True
            elif any(cat in json_catalogs for cat in csv_catalogs):
                name_match = True
            elif any(cat in csv_catalogs for cat in json_catalogs):
                name_match = True
            
            # Check coordinate proximity
            coord_match, separation = compare_coordinates(
                csv_obj.ra_degrees / 15,  # Convert back to hours
                csv_obj.dec_degrees,
                json_obj.ra_degrees / 15,  # Convert back to hours  
                json_obj.dec_degrees,
                threshold=1.0  # 1 degree threshold for coordinate matching
            )
            
            # Calculate matching score
            score = separation
            if name_match:
                score -= 10  # Strong bonus for name match
                
            if score < best_score:
                best_match = (json_obj, i)
                best_score = score
        
        if best_match and best_score < 5.0:  # Accept matches within 5 degrees
            json_obj, json_index = best_match
            matches.append((csv_obj, json_obj))
            json_unmatched.pop(json_index)
        else:
            csv_unmatched.append(csv_obj)
    
    return matches, csv_unmatched, json_unmatched


def compare_catalogs():
    """Main comparison function"""
    print("=== Catalog Comparison Tool ===\n")
    
    # Import catalog functions
    try:
        from catalogs.csv_catalog import get_objects_from_csv
        from catalogs.json_catalog import get_objects_from_json
        print("✓ Successfully imported catalog functions")
    except ImportError as e:
        print(f"✗ Error importing catalog functions: {e}")
        return
    
    # Load CSV catalog
    print("\nLoading CSV catalog...")
    try:
        csv_objects = get_objects_from_csv()
        print(f"✓ CSV catalog: {len(csv_objects)} objects loaded")
    except Exception as e:
        print(f"✗ Error loading CSV catalog: {e}")
        return
    
    # Load JSON catalog  
    print("\nLoading JSON catalog...")
    try:
        json_objects = get_objects_from_json()
        print(f"✓ JSON catalog: {len(json_objects)} objects loaded")
    except Exception as e:
        print(f"✗ Error loading JSON catalog: {e}")
        return
    
    # Find matching objects
    print("\nMatching objects between catalogs...")
    matches, csv_unmatched, json_unmatched = find_matching_objects(csv_objects, json_objects)
    
    print(f"✓ Found {len(matches)} matching objects")
    print(f"  CSV unmatched: {len(csv_unmatched)}")
    print(f"  JSON unmatched: {len(json_unmatched)}")
    
    # Analyze matches
    print("\n=== COORDINATE ACCURACY ANALYSIS ===")
    coord_errors = []
    magnitude_errors = []
    
    for csv_obj, json_obj in matches:
        # Check coordinate accuracy
        coord_match, separation = compare_coordinates(
            csv_obj.ra_degrees / 15,
            csv_obj.dec_degrees, 
            json_obj.ra_degrees / 15,
            json_obj.dec_degrees,
            threshold=0.01  # Very tight threshold for analysis
        )
        
        if not coord_match:
            coord_errors.append((csv_obj.name, json_obj.name, separation))
        
        # Check magnitude differences
        if csv_obj.magnitude and json_obj.magnitude:
            mag_diff = abs(csv_obj.magnitude - json_obj.magnitude)
            if mag_diff > 1.0:  # More than 1 magnitude difference
                magnitude_errors.append((csv_obj.name, json_obj.name, csv_obj.magnitude, json_obj.magnitude, mag_diff))
    
    print(f"Coordinate accuracy: {len(matches) - len(coord_errors)}/{len(matches)} objects within 0.01°")
    if coord_errors:
        print(f"  {len(coord_errors)} objects with coordinate discrepancies:")
        for csv_name, json_name, sep in coord_errors[:5]:  # Show first 5
            print(f"    {csv_name} vs {json_name}: {sep:.4f}° separation")
        if len(coord_errors) > 5:
            print(f"    ... and {len(coord_errors) - 5} more")
    
    print(f"Magnitude accuracy: {len(matches) - len(magnitude_errors)}/{len(matches)} objects within 1.0 mag")
    if magnitude_errors:
        print(f"  {len(magnitude_errors)} objects with magnitude discrepancies:")
        for csv_name, json_name, csv_mag, json_mag, diff in magnitude_errors[:5]:
            print(f"    {csv_name} vs {json_name}: CSV={csv_mag:.1f}, JSON={json_mag:.1f} (Δ{diff:.1f})")
        if len(magnitude_errors) > 5:
            print(f"    ... and {len(magnitude_errors) - 5} more")
    
    # Object type analysis
    print("\n=== OBJECT TYPE ANALYSIS ===")
    type_mismatches = []
    
    for csv_obj, json_obj in matches:
        # Get CSV type if available
        csv_type = getattr(csv_obj, 'csv_type', 'Unknown')
        json_type = getattr(json_obj, 'csv_type', 'Unknown')
        
        if csv_type != json_type and csv_type != 'Unknown' and json_type != 'Unknown':
            type_mismatches.append((csv_obj.name, csv_type, json_type))
    
    print(f"Type consistency: {len(matches) - len(type_mismatches)}/{len(matches)} objects with matching types")
    if type_mismatches:
        print(f"  {len(type_mismatches)} objects with type discrepancies:")
        for name, csv_type, json_type in type_mismatches[:5]:
            print(f"    {name}: CSV='{csv_type}', JSON='{json_type}'")
        if len(type_mismatches) > 5:
            print(f"    ... and {len(type_mismatches) - 5} more")
    
    # Coverage analysis
    print("\n=== COVERAGE ANALYSIS ===")
    print(f"CSV objects: {len(csv_objects)}")
    print(f"JSON objects: {len(json_objects)}")
    print(f"Matched objects: {len(matches)} ({100*len(matches)/len(csv_objects):.1f}% of CSV)")
    print(f"CSV-only objects: {len(csv_unmatched)} ({100*len(csv_unmatched)/len(csv_objects):.1f}% of CSV)")
    if len(json_objects) > 0:
        print(f"JSON-only objects: {len(json_unmatched)} ({100*len(json_unmatched)/len(json_objects):.1f}% of JSON)")
    else:
        print(f"JSON-only objects: {len(json_unmatched)} (N/A% - no JSON objects loaded)")
    
    if csv_unmatched:
        print(f"\nSample CSV-only objects:")
        for obj in csv_unmatched[:10]:
            print(f"  {obj.name} (RA={obj.ra_degrees/15:.2f}h, Dec={obj.dec_degrees:.2f}°)")
        if len(csv_unmatched) > 10:
            print(f"  ... and {len(csv_unmatched) - 10} more")
    
    if json_unmatched:
        print(f"\nSample JSON-only objects:")
        for obj in json_unmatched[:10]:
            print(f"  {obj.name} (RA={obj.ra_degrees/15:.2f}h, Dec={obj.dec_degrees:.2f}°)")
        if len(json_unmatched) > 10:
            print(f"  ... and {len(json_unmatched) - 10} more")
    
    # Quality metrics
    print("\n=== QUALITY METRICS ===")
    
    # Enhanced data in JSON
    enhanced_count = 0
    for json_obj in json_objects:
        if hasattr(json_obj, 'comments') and json_obj.comments:
            enhanced_count += 1
    
    print(f"Objects with enhanced metadata: {enhanced_count}/{len(json_objects)} ({100*enhanced_count/len(json_objects):.1f}%)")
    
    # FOV data comparison
    csv_with_fov = sum(1 for obj in csv_objects if obj.fov and obj.fov.strip())
    json_with_fov = sum(1 for obj in json_objects if obj.fov and obj.fov.strip())
    
    print(f"Objects with FOV data: CSV={csv_with_fov}/{len(csv_objects)} ({100*csv_with_fov/len(csv_objects):.1f}%), JSON={json_with_fov}/{len(json_objects)} ({100*json_with_fov/len(json_objects):.1f}%)")
    
    return {
        'csv_count': len(csv_objects),
        'json_count': len(json_objects),
        'matches': len(matches),
        'csv_unmatched': len(csv_unmatched),
        'json_unmatched': len(json_unmatched),
        'coord_errors': len(coord_errors),
        'magnitude_errors': len(magnitude_errors),
        'type_mismatches': len(type_mismatches)
    }


def test_specific_objects():
    """Test specific well-known objects for accuracy"""
    print("\n=== SPECIFIC OBJECT TESTS ===")
    
    # Load catalogs
    try:
        from catalogs.csv_catalog import get_objects_from_csv
        from catalogs.json_catalog import get_objects_from_json
        
        csv_objects = get_objects_from_csv()
        json_objects = get_objects_from_json()
    except Exception as e:
        print(f"Error loading catalogs: {e}")
        return
    
    # Test objects (known coordinates for validation)
    test_objects = {
        'M31': (10.684, 41.269),     # Andromeda Galaxy (RA hours, Dec degrees)
        'M42': (5.588, -5.391),      # Orion Nebula
        'M13': (16.694, 36.460),     # Hercules Cluster
        'M57': (18.884, 33.033),     # Ring Nebula
        'NGC 253': (11.888, -25.288) # Sculptor Galaxy
    }
    
    for test_name, (expected_ra_h, expected_dec) in test_objects.items():
        print(f"\nTesting {test_name}:")
        
        # Find in CSV
        csv_match = None
        for obj in csv_objects:
            if any(cat in obj.name.lower() for cat in [test_name.lower(), test_name.lower().replace('m', 'messier '), test_name.lower().replace('ngc', 'ngc ')]):
                csv_match = obj
                break
        
        # Find in JSON
        json_match = None
        for obj in json_objects:
            if any(cat in obj.name.lower() for cat in [test_name.lower(), test_name.lower().replace('m', 'messier '), test_name.lower().replace('ngc', 'ngc ')]):
                json_match = obj
                break
        
        if csv_match:
            csv_ra_h = csv_match.ra_degrees / 15
            csv_dec = csv_match.dec_degrees
            csv_error = math.sqrt((csv_ra_h - expected_ra_h)**2 + (csv_dec - expected_dec)**2)
            print(f"  CSV: {csv_match.name} - RA={csv_ra_h:.3f}h, Dec={csv_dec:.3f}° (error={csv_error:.3f}°)")
        else:
            print(f"  CSV: Not found")
        
        if json_match:
            json_ra_h = json_match.ra_degrees / 15  
            json_dec = json_match.dec_degrees
            json_error = math.sqrt((json_ra_h - expected_ra_h)**2 + (json_dec - expected_dec)**2)
            print(f"  JSON: {json_match.name} - RA={json_ra_h:.3f}h, Dec={json_dec:.3f}° (error={json_error:.3f}°)")
        else:
            print(f"  JSON: Not found")


if __name__ == "__main__":
    # Set up environment
    import sys
    import os
    
    # Change to script directory for proper imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    
    # Run comparison
    try:
        results = compare_catalogs()
        test_specific_objects()
        
        print("\n=== SUMMARY ===")
        if results:
            print(f"✓ Comparison completed successfully")
            print(f"  Match rate: {100*results['matches']/(results['csv_count']):.1f}%")
            print(f"  Coordinate accuracy: {100*(results['matches']-results['coord_errors'])/results['matches']:.1f}%")
            print(f"  JSON catalog provides {results['json_count'] - results['csv_count']} additional objects")
            
            if results['coord_errors'] < results['matches'] * 0.05:  # Less than 5% errors
                print("✓ Coordinate accuracy is excellent")
            elif results['coord_errors'] < results['matches'] * 0.10:  # Less than 10% errors
                print("⚠ Coordinate accuracy is good but could be improved")
            else:
                print("✗ Coordinate accuracy needs improvement")
        
    except Exception as e:
        print(f"✗ Comparison failed: {e}")
        import traceback
        traceback.print_exc() 