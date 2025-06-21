#!/usr/bin/env python3
"""
Test script for JSON catalog functionality.
Demonstrates the new JSON catalog system and compares it with CSV.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_json_catalog_basic():
    """Basic test of JSON catalog loading"""
    print("=== JSON Catalog Basic Test ===\n")
    
    try:
        from catalogs.json_catalog import (
            load_json_catalogs, 
            get_objects_from_json,
            calculate_fov_from_json,
            map_json_category_to_csv_type,
            build_enhanced_name
        )
        print("✓ Successfully imported JSON catalog functions")
    except ImportError as e:
        print(f"✗ Failed to import JSON catalog functions: {e}")
        return
    
    # Test catalog loading
    print("\n1. Testing catalog loading...")
    try:
        catalogs = load_json_catalogs()
        print(f"✓ Loaded {len(catalogs)} catalog files")
        for name, data in catalogs.items():
            print(f"  {name}: {len(data)} entries")
    except Exception as e:
        print(f"✗ Failed to load catalogs: {e}")
        return
    
    # Test object conversion
    print("\n2. Testing object conversion...")
    try:
        json_objects = get_objects_from_json()
        print(f"✓ Converted {len(json_objects)} objects to CelestialObject format")
        
        # Show sample objects
        print("\nSample objects:")
        for obj in json_objects[:5]:
            print(f"  {obj.name}")
            print(f"    RA: {obj.ra_degrees/15:.3f}h, Dec: {obj.dec_degrees:.3f}°")
            print(f"    FOV: {obj.fov}, Magnitude: {obj.magnitude}")
            if hasattr(obj, 'csv_type'):
                print(f"    Type: {obj.csv_type}")
            if hasattr(obj, 'comments'):
                print(f"    Comments: {obj.comments[:100]}..." if len(obj.comments) > 100 else f"    Comments: {obj.comments}")
            print()
            
    except Exception as e:
        print(f"✗ Failed to convert objects: {e}")
        return
    
    print("✓ JSON catalog basic test completed successfully")


def test_coordinate_conversion():
    """Test coordinate conversion accuracy"""
    print("\n=== Coordinate Conversion Test ===\n")
    
    try:
        from catalogs.json_catalog import convert_json_coordinates
        
        # Test known coordinates
        test_coords = [
            (10.6847, 41.2694),    # M31 Andromeda (RA degrees, Dec degrees)
            (83.8221, -5.3911),    # M42 Orion (RA degrees, Dec degrees)  
            (250.4217, 36.4581),   # M13 Hercules (RA degrees, Dec degrees)
        ]
        
        print("Testing coordinate conversion:")
        for ra_deg, dec_deg in test_coords:
            ra_hours, dec_deg_out = convert_json_coordinates(ra_deg, dec_deg)
            print(f"  RA: {ra_deg:.3f}° → {ra_hours:.3f}h, Dec: {dec_deg:.3f}° → {dec_deg_out:.3f}°")
            
            # Verify conversion
            expected_hours = ra_deg / 15.0
            if abs(ra_hours - expected_hours) < 0.001:
                print("    ✓ Conversion correct")
            else:
                print(f"    ✗ Conversion error: expected {expected_hours:.3f}h")
        
    except Exception as e:
        print(f"✗ Coordinate conversion test failed: {e}")


def test_fov_calculation():
    """Test FOV calculation from different data sources"""
    print("\n=== FOV Calculation Test ===\n")
    
    try:
        from catalogs.json_catalog import calculate_fov_from_json
        
        # Test different FOV data formats
        test_objects = [
            {'size': 30.0, 'category': 'nebula-emission'},
            {'ellipse': {'a': 0.5, 'b': 0.3}, 'category': 'galaxy'},
            {'magnitude': 6.5, 'category': 'cluster-open'},
            {'magnitude': 11.0, 'category': 'galaxy-spiral'},
        ]
        
        print("Testing FOV calculation:")
        for i, obj in enumerate(test_objects):
            fov = calculate_fov_from_json(obj)
            print(f"  Object {i+1}: {obj} → FOV: {fov}")
            
    except Exception as e:
        print(f"✗ FOV calculation test failed: {e}")


def test_category_mapping():
    """Test category to CSV type mapping"""
    print("\n=== Category Mapping Test ===\n")
    
    try:
        from catalogs.json_catalog import map_json_category_to_csv_type
        
        # Test different categories
        test_categories = [
            'nebula-planetary',
            'nebula-emission', 
            'galaxy-spiral',
            'cluster-globular',
            'cluster-open',
            'star-single',
            'supernova-remnant'
        ]
        
        print("Testing category mapping:")
        for category in test_categories:
            csv_type = map_json_category_to_csv_type(category)
            print(f"  '{category}' → '{csv_type}'")
            
    except Exception as e:
        print(f"✗ Category mapping test failed: {e}")


def compare_sample_objects():
    """Compare a few objects between CSV and JSON catalogs"""
    print("\n=== Sample Object Comparison ===\n")
    
    try:
        from catalogs.csv_catalog import get_objects_from_csv  
        from catalogs.json_catalog import get_objects_from_json
        
        print("Loading catalogs...")
        csv_objects = get_objects_from_csv()
        json_objects = get_objects_from_json()
        
        print(f"CSV: {len(csv_objects)} objects")
        print(f"JSON: {len(json_objects)} objects")
        
        # Find some common objects
        search_terms = ['M31', 'M42', 'NGC 253', 'M13']
        
        for term in search_terms:
            print(f"\nSearching for {term}:")
            
            # Find in CSV
            csv_match = None
            for obj in csv_objects:
                if term.lower() in obj.name.lower():
                    csv_match = obj
                    break
            
            # Find in JSON  
            json_match = None
            for obj in json_objects:
                if term.lower() in obj.name.lower():
                    json_match = obj
                    break
            
            if csv_match:
                print(f"  CSV: {csv_match.name}")
                print(f"       RA={csv_match.ra_degrees/15:.3f}h, Dec={csv_match.dec_degrees:.3f}°")
                print(f"       FOV={csv_match.fov}, Mag={csv_match.magnitude}")
            else:
                print(f"  CSV: Not found")
                
            if json_match:
                print(f"  JSON: {json_match.name}")
                print(f"        RA={json_match.ra_degrees/15:.3f}h, Dec={json_match.dec_degrees:.3f}°")
                print(f"        FOV={json_match.fov}, Mag={json_match.magnitude}")
                if hasattr(json_match, 'comments'):
                    print(f"        Comments: {json_match.comments[:60]}...")
            else:
                print(f"  JSON: Not found")
        
    except Exception as e:
        print(f"✗ Sample comparison failed: {e}")


def main():
    """Run all tests"""
    print("JSON Catalog Test Suite")
    print("=" * 50)
    
    # Run individual tests
    test_json_catalog_basic()
    test_coordinate_conversion() 
    test_fov_calculation()
    test_category_mapping()
    compare_sample_objects()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("\nTo run the full catalog comparison:")
    print("  python utilities/catalog_comparison.py")


if __name__ == "__main__":
    main() 