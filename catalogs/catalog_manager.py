"""
Unified Catalog Manager
Provides a single interface for loading objects from either CSV or JSON catalogs
Based on configuration settings.
"""

import os
import sys


def get_catalog_type():
    """Get the configured catalog type"""
    try:
        from config.settings import USE_CSV_CATALOG
        return "csv" if USE_CSV_CATALOG else "json"
    except ImportError:
        # Fallback to JSON if config is not available
        return "json"


def get_objects_from_catalog():
    """
    Get objects from the configured catalog (CSV or JSON)
    This is the main interface function that replaces get_objects_from_csv()
    """
    catalog_type = get_catalog_type()
    
    if catalog_type == "csv":
        try:
            from catalogs.csv_catalog import get_objects_from_csv
            return get_objects_from_csv()
        except ImportError as e:
            print(f"Warning: Could not load CSV catalog: {e}")
            print("Falling back to JSON catalog...")
            # Fall back to JSON
            from catalogs.json_catalog import get_objects_from_json
            return get_objects_from_json()
    else:
        try:
            from catalogs.json_catalog import get_objects_from_json
            return get_objects_from_json()
        except ImportError as e:
            print(f"Warning: Could not load JSON catalog: {e}")
            print("Falling back to CSV catalog...")
            # Fall back to CSV
            from catalogs.csv_catalog import get_objects_from_csv
            return get_objects_from_csv()


def get_catalog_info():
    """Get information about the current catalog configuration"""
    catalog_type = get_catalog_type()
    
    try:
        if catalog_type == "csv":
            from catalogs.csv_catalog import get_objects_from_csv
            objects = get_objects_from_csv()
            return {
                "type": "CSV",
                "source": "catalogs/objects.csv",
                "count": len(objects),
                "features": ["Basic object data", "Standard FOV calculations"]
            }
        else:
            from catalogs.json_catalog import get_objects_from_json
            objects = get_objects_from_json()
            return {
                "type": "JSON",
                "source": "catalogs/*.json (merged)",
                "count": len(objects),
                "features": [
                    "Enhanced object metadata",
                    "Accurate FOV calculations",
                    "Nebula boundary data",
                    "Ellipse measurements",
                    "Discovery information",
                    "Real size and distance data"
                ]
            }
    except Exception as e:
        return {
            "type": "Unknown",
            "source": "Error loading catalog",
            "count": 0,
            "error": str(e),
            "features": []
        }


def switch_catalog_type(use_csv=False):
    """
    Switch between catalog types
    NOTE: This changes the configuration in memory only.
    To persist, update config.json manually.
    """
    try:
        import config.settings as settings
        settings.USE_CSV_CATALOG = use_csv
        print(f"Switched to {'CSV' if use_csv else 'JSON'} catalog (in-memory only)")
        
        # Test the switch
        info = get_catalog_info()
        print(f"Current catalog: {info['type']} with {info['count']} objects")
        return True
    except Exception as e:
        print(f"Error switching catalog: {e}")
        return False


def compare_catalogs():
    """Compare CSV and JSON catalog capabilities"""
    print("=== Catalog Comparison ===\n")
    
    results = {}
    
    # Test CSV catalog
    print("Testing CSV catalog...")
    try:
        original_setting = get_catalog_type()
        switch_catalog_type(use_csv=True)
        csv_info = get_catalog_info()
        results["csv"] = csv_info
        print(f"✓ CSV: {csv_info['count']} objects")
    except Exception as e:
        results["csv"] = {"error": str(e), "count": 0}
        print(f"✗ CSV error: {e}")
    
    # Test JSON catalog
    print("Testing JSON catalog...")
    try:
        switch_catalog_type(use_csv=False)
        json_info = get_catalog_info()
        results["json"] = json_info
        print(f"✓ JSON: {json_info['count']} objects")
    except Exception as e:
        results["json"] = {"error": str(e), "count": 0}
        print(f"✗ JSON error: {e}")
    
    # Restore original setting
    try:
        switch_catalog_type(use_csv=(original_setting == "csv"))
    except:
        pass
    
    # Print comparison
    print("\n=== Comparison Summary ===")
    for catalog_type, info in results.items():
        print(f"\n{catalog_type.upper()} Catalog:")
        if "error" in info:
            print(f"  ❌ Error: {info['error']}")
        else:
            print(f"  📊 Objects: {info['count']}")
            print(f"  📁 Source: {info['source']}")
            print(f"  ✨ Features:")
            for feature in info.get('features', []):
                print(f"    • {feature}")
    
    return results


# Backward compatibility aliases
# These allow existing code to work without changes
def get_objects_from_csv():
    """Backward compatibility wrapper - now uses configured catalog"""
    return get_objects_from_catalog()


# Advanced catalog functions
def get_objects_by_type(object_type=None):
    """Get objects filtered by type from the configured catalog"""
    catalog_type = get_catalog_type()
    
    if catalog_type == "json":
        try:
            from catalogs.json_catalog import get_objects_from_json_by_type
            return get_objects_from_json_by_type(object_type)
        except ImportError:
            pass
    
    # Fallback to basic filtering for CSV catalog
    objects = get_objects_from_catalog()
    if object_type:
        return [obj for obj in objects if getattr(obj, 'obj_type', '').lower() == object_type.lower()]
    return objects


def get_enhanced_object_data():
    """Get enhanced object data (only available with JSON catalog)"""
    catalog_type = get_catalog_type()
    
    if catalog_type == "json":
        objects = get_objects_from_catalog()
        enhanced = []
        
        for obj in objects:
            if hasattr(obj, 'comments') and obj.comments:
                enhanced.append({
                    'name': obj.name,
                    'type': getattr(obj, 'obj_type', 'Unknown'),
                    'coordinates': f"RA={obj.ra_hours:.3f}h, Dec={obj.dec_deg:.3f}°",
                    'fov': obj.fov,
                    'magnitude': obj.magnitude,
                    'metadata': obj.comments
                })
        
        return enhanced
    else:
        print("Enhanced object data is only available with JSON catalog")
        print("Set use_csv_catalog=false in config.json to enable")
        return []


if __name__ == "__main__":
    # Test the catalog manager
    print("=== Catalog Manager Test ===\n")
    
    current_info = get_catalog_info()
    print(f"Current catalog: {current_info['type']}")
    print(f"Objects: {current_info['count']}")
    print(f"Source: {current_info['source']}")
    
    # Compare both catalogs
    print("\n" + "="*50)
    compare_catalogs()
    
    # Test enhanced data if JSON
    if get_catalog_type() == "json":
        print("\n=== Enhanced Metadata Sample ===")
        enhanced = get_enhanced_object_data()
        for obj in enhanced[:3]:  # Show first 3
            print(f"\n{obj['name']} ({obj['type']})")
            print(f"  {obj['coordinates']}")
            print(f"  FOV: {obj['fov']}, Mag: {obj['magnitude']}")
            print(f"  Info: {obj['metadata'][:100]}...") 