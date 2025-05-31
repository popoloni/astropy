"""
Catalog management for the astropy application.
"""

from .messier import get_messier_catalog
from .dso import get_additional_dso
from .catalog_manager import get_combined_catalog, merge_catalogs
from .csv_catalog import get_objects_from_csv, get_object_type
from .object_utils import (
    enrich_object_name, 
    normalize_object_name, 
    are_same_object,
    get_object_by_name,
    get_objects_by_type,
    sort_objects_by_size,
    sort_objects_by_altitude
)

__all__ = [
    'get_messier_catalog',
    'get_additional_dso',
    'get_combined_catalog',
    'merge_catalogs',
    'get_objects_from_csv',
    'get_object_type',
    'enrich_object_name',
    'normalize_object_name',
    'are_same_object',
    'get_object_by_name',
    'get_objects_by_type',
    'sort_objects_by_size',
    'sort_objects_by_altitude'
] 