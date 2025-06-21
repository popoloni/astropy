"""
Catalog management for the astropy application.
Supports both CSV and JSON catalogs with unified interface.
"""

# Core catalog functions (old interface for backward compatibility)
from .messier import get_messier_catalog
from .dso import get_additional_dso

# New unified catalog manager (recommended interface)
from .catalog_manager import (
    get_objects_from_catalog,
    get_catalog_info,
    get_catalog_type,
    switch_catalog_type,
    compare_catalogs,
    get_objects_by_type,
    get_enhanced_object_data
)

# Backward compatibility - redirect to unified interface
from .catalog_manager import get_objects_from_csv

# Object utilities
from .object_utils import (
    enrich_object_name, 
    normalize_object_name, 
    are_same_object,
    get_object_by_name,
    sort_objects_by_size,
    sort_objects_by_altitude
)

# Legacy functions (preserved for old code)
try:
    from .csv_catalog import get_object_type
except ImportError:
    def get_object_type(obj_type_str):
        """Fallback object type function"""
        return obj_type_str

# Try to import combined catalog functions (may not exist in new structure)
try:
    from .combined_catalog import get_combined_catalog, merge_catalogs
except ImportError:
    # Create fallback functions
    def get_combined_catalog():
        """Fallback to unified catalog"""
        return get_objects_from_catalog()
    
    def merge_catalogs(csv_objects, builtin_objects):
        """Fallback merge function"""
        return csv_objects + builtin_objects

__all__ = [
    # Primary interface (recommended)
    'get_objects_from_catalog',
    'get_catalog_info', 
    'get_catalog_type',
    'switch_catalog_type',
    'compare_catalogs',
    'get_enhanced_object_data',
    
    # Backward compatibility
    'get_objects_from_csv',
    'get_objects_by_type',
    
    # Legacy functions
    'get_messier_catalog',
    'get_additional_dso',
    'get_combined_catalog',
    'merge_catalogs',
    'get_object_type',
    
    # Utilities
    'enrich_object_name',
    'normalize_object_name',
    'are_same_object',
    'get_object_by_name',
    'sort_objects_by_size',
    'sort_objects_by_altitude'
] 