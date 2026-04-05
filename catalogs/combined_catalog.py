"""
Combined catalog functions for merging different catalog sources.
Provides legacy functions for backward compatibility.
"""

from .messier import get_messier_catalog
from .dso import get_additional_dso
from .object_utils import are_same_object


def get_combined_catalog():
    """Get combined catalog of all objects"""
    messier = get_messier_catalog()
    additional = get_additional_dso()
    return messier + additional


def merge_catalogs(csv_objects, builtin_objects):
    """Merge CSV and built-in catalogs, preferring CSV entries for duplicates"""
    merged = []
    used_builtin = set()
    
    # First add all CSV objects
    merged.extend(csv_objects)
    
    # Add non-duplicate built-in objects
    for builtin_obj in builtin_objects:
        is_duplicate = False
        for csv_obj in csv_objects:
            if are_same_object(builtin_obj.name, csv_obj.name):
                is_duplicate = True
                break
        if not is_duplicate:
            merged.append(builtin_obj)
    
    return merged 