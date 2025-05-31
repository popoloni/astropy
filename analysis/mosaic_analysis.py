"""
Mosaic analysis and group creation functions.
"""

from models import MosaicGroup


def create_mosaic_groups(objects, start_time, end_time):
    """Create MosaicGroup objects from visible objects using mosaic analysis"""
    from config.settings import MOSAIC_ANALYSIS_AVAILABLE, _import_mosaic_functions
    
    if not MOSAIC_ANALYSIS_AVAILABLE:
        print("Mosaic analysis not available. Returning empty list.")
        return []
    
    # Import mosaic functions dynamically
    analyze_object_groups, _, _, _ = _import_mosaic_functions()
    if analyze_object_groups is None:
        print("Mosaic analysis functions not available. Returning empty list.")
        return []
    
    # Find mosaic groups using the analysis function
    groups_data = analyze_object_groups(objects, start_time, end_time)
    
    # Convert to MosaicGroup objects
    mosaic_groups = []
    for i, (group_objects, overlap_periods) in enumerate(groups_data):
        group_id = f"Group_{i+1}"
        mosaic_group = MosaicGroup(group_objects, overlap_periods, group_id)
        mosaic_groups.append(mosaic_group)
    
    return mosaic_groups


def analyze_mosaic_compatibility(objects, fov_width=None, fov_height=None):
    """Analyze if objects can be combined in a mosaic based on field of view constraints"""
    from config.settings import MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT
    
    if fov_width is None:
        fov_width = MOSAIC_FOV_WIDTH
    if fov_height is None:
        fov_height = MOSAIC_FOV_HEIGHT
    
    compatible_groups = []
    
    # Simple spatial clustering based on coordinates
    # This is a placeholder implementation - the actual logic would be more complex
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects[i+1:], i+1):
            # Check if objects are close enough to be in the same mosaic
            # This would require actual coordinate analysis
            if can_objects_fit_in_mosaic([obj1, obj2], fov_width, fov_height):
                compatible_groups.append([obj1, obj2])
    
    return compatible_groups


def can_objects_fit_in_mosaic(objects, fov_width, fov_height):
    """Check if a group of objects can fit within the given field of view"""
    # Placeholder implementation - would need actual coordinate analysis
    # For now, assume small groups can fit together
    return len(objects) <= 3 