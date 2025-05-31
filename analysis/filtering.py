"""
Object filtering functions for astronomical observation planning.
"""

from astronomy import find_visibility_window, calculate_visibility_duration, calculate_required_exposure


def filter_objects_by_altitude_azimuth(objects, min_alt=None, max_alt=None, min_az=None, max_az=None):
    """Filter objects based on altitude and azimuth limits (old version for compatibility)"""
    from config.settings import MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ
    
    if min_alt is None:
        min_alt = MIN_ALT
    if max_alt is None:
        max_alt = MAX_ALT
    if min_az is None:
        min_az = MIN_AZ
    if max_az is None:
        max_az = MAX_AZ
    
    filtered = []
    for obj in objects:
        if min_alt <= 90 <= max_alt and min_az <= 180 <= max_az:  # Simple placeholder check
            filtered.append(obj)
    return filtered


def filter_objects_by_criteria(objects, start_time, end_time, exclude_insufficient=True, use_margins=True):
    """Filter objects based on visibility and exposure requirements"""
    from config.settings import EXCLUDE_INSUFFICIENT_TIME, MIN_VISIBILITY_HOURS, BORTLE_INDEX
    
    # Use parameter if provided, otherwise use config default
    if exclude_insufficient is None:
        exclude_insufficient = EXCLUDE_INSUFFICIENT_TIME
    
    filtered_objects = []
    insufficient_objects = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            duration = calculate_visibility_duration(periods)
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                # Calculate required exposure time and store it in the object
                obj.required_exposure = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)
                
                if duration >= MIN_VISIBILITY_HOURS:
                    obj.sufficient_time = duration >= obj.required_exposure[0]
                    if exclude_insufficient:
                        if obj.sufficient_time:
                            filtered_objects.append(obj)
                        else:
                            insufficient_objects.append(obj)
                    else:
                        filtered_objects.append(obj)
    
    return filtered_objects, insufficient_objects 