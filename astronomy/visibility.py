"""
Object visibility and imaging calculations for astronomical observations.
"""

import math
import re
from datetime import timedelta
from .celestial import calculate_altaz, calculate_sun_position
from .time_utils import utc_to_local


def is_visible(alt, az, use_margins=True):
    """Check if object is within visibility limits"""
    # Import here to avoid circular imports during refactoring
    from config.settings import MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ
    
    if use_margins:
        # Use 5-degree margins as in trajectory plotting
        return ((MIN_ALT - 5 <= alt <= MAX_ALT + 5) and 
                (MIN_AZ - 5 <= az <= MAX_AZ + 5))
    else:
        return (MIN_AZ <= az <= MAX_AZ) and (MIN_ALT <= alt <= MAX_ALT)


def find_visibility_window(obj, start_time, end_time, use_margins=True):
    """Find visibility window for an object, considering sun position"""
    current_time = start_time
    visibility_periods = []
    start_visible = None
    last_visible = False
    
    # Use 1-minute intervals for better precision, matching trajectory plotting
    interval = timedelta(minutes=1)
    
    while current_time <= end_time:
        # Check object's position
        alt, az = calculate_altaz(obj, current_time)
        
        # Check sun's position
        sun_alt, _ = calculate_sun_position(current_time)
        
        # Object is visible if:
        # 1. It's within visibility limits
        # 2. The sun is below the horizon (altitude < -5)
        is_currently_visible = is_visible(alt, az, use_margins) and sun_alt < -5
        
        # Object becomes visible
        if is_currently_visible and not last_visible:
            start_visible = current_time
        # Object becomes invisible
        elif not is_currently_visible and last_visible and start_visible is not None:
            visibility_periods.append((start_visible, current_time))
            start_visible = None
            
        last_visible = is_currently_visible
        current_time += interval
    
    # If object is still visible at the end, add the final period
    if start_visible is not None and last_visible:
        visibility_periods.append((start_visible, end_time))
    
    return visibility_periods


def calculate_visibility_duration(visibility_periods):
    """Calculate total visibility duration in hours"""
    total_seconds = sum(
        (end - start).total_seconds() 
        for start, end in visibility_periods
    )
    return total_seconds / 3600


def find_sunset_sunrise(date):
    """Find sunset and sunrise times"""
    # Import here to avoid circular imports during refactoring
    from astronomy.time_utils import get_local_timezone, local_to_utc
    from config.settings import SEARCH_INTERVAL_MINUTES
    
    milan_tz = get_local_timezone()
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon = milan_tz.localize(noon)
    noon_utc = local_to_utc(noon)
    
    current_time = noon_utc
    alt, _ = calculate_sun_position(current_time)
    
    while alt > 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunset = current_time
    
    while alt <= 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunrise = current_time
    
    return utc_to_local(sunset), utc_to_local(sunrise)


def find_astronomical_twilight(date):
    """Find astronomical twilight times"""
    # Import here to avoid circular imports during refactoring
    from astronomy.time_utils import get_local_timezone, local_to_utc
    from config.settings import SEARCH_INTERVAL_MINUTES
    
    milan_tz = get_local_timezone()
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon = milan_tz.localize(noon)
    noon_utc = local_to_utc(noon)
    
    current_time = noon_utc
    alt, _ = calculate_sun_position(current_time)
    
    while alt > -18:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    twilight_evening = current_time
    
    while alt <= -18:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    twilight_morning = current_time
    
    return utc_to_local(twilight_evening), utc_to_local(twilight_morning)


def find_best_objects(visibility_periods, max_overlapping=None):
    """Select objects with longest visibility periods and minimal overlap"""
    # Import here to avoid circular imports during refactoring
    from config.settings import MAX_OBJECTS_OPTIMAL
    
    if max_overlapping is None:
        max_overlapping = MAX_OBJECTS_OPTIMAL
    
    sorted_periods = []
    for obj_name, period in visibility_periods.items():
        duration = period['duration']
        sorted_periods.append((obj_name, period['start'], period['end'], duration))
    
    sorted_periods.sort(key=lambda x: x[3], reverse=True)
    
    selected_objects = []
    for obj_data in sorted_periods:
        overlap = False
        for selected in selected_objects:
            if not (obj_data[2] <= selected[1] or obj_data[1] >= selected[2]):
                overlap = True
                break
        if not overlap and len(selected_objects) < max_overlapping:
            selected_objects.append(obj_data)
    
    return selected_objects


def calculate_required_panels(obj_fov):
    """Calculate number of panels needed to cover object"""
    # Import here to avoid circular imports during refactoring
    from config.settings import SCOPE_FOV_WIDTH, SCOPE_FOV_HEIGHT
    
    if not obj_fov:
        return 1
        
    # Parse object FOV
    match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', obj_fov)
    if not match:
        return 1
        
    width = float(match.group(1))
    height = float(match.group(2))
    
    # Convert to degrees if in arcminutes
    if "'" in obj_fov:
        width = width / 60
        height = height / 60
    
    # Calculate panels needed in each dimension (with 10% overlap)
    panels_width = math.ceil(width / (SCOPE_FOV_WIDTH * 0.9))
    panels_height = math.ceil(height / (SCOPE_FOV_HEIGHT * 0.9))
    
    return panels_width * panels_height


def calculate_required_exposure(magnitude, bortle_index, obj_fov, single_exposure=None):
    """
    Calculate required total exposure time based on magnitude, sky conditions, and object size.
    Returns total exposure time in hours and number of frames needed.
    """
    # Import here to avoid circular imports during refactoring
    from config.settings import SINGLE_EXPOSURE
    
    if single_exposure is None:
        single_exposure = SINGLE_EXPOSURE
    
    # Base exposure time (in hours) for mag 10 object in Bortle 4
    base_exposure = 1.0
    
    # Adjust for magnitude (exponential relationship)
    magnitude_factor = 2 ** ((magnitude - 10) / 2.5)
    
    # Adjust for Bortle index (linear relationship)
    bortle_factor = (bortle_index / 4) ** 2
    
    # Calculate base total exposure time in hours
    base_total_exposure = base_exposure * magnitude_factor * bortle_factor
    
    # Calculate number of panels needed
    panels = calculate_required_panels(obj_fov)
    
    # Adjust total exposure time for panels
    total_exposure = base_total_exposure * panels
    
    # Calculate number of subframes needed
    subframes = math.ceil((total_exposure * 3600) / single_exposure)
    
    return total_exposure, subframes, panels


def is_object_imageable(obj, visibility_duration, bortle_index):
    """
    Determine if object can be imaged successfully given conditions.
    """
    if not hasattr(obj, 'magnitude') or obj.magnitude is None:
        return False
        
    required_exposure = calculate_required_exposure(obj.magnitude, bortle_index, obj.fov)
    return visibility_duration >= required_exposure[0]


def filter_visible_objects(objects, start_time, end_time, exclude_insufficient=None, use_margins=True):
    """Filter objects based on visibility and exposure requirements"""
    # Import here to avoid circular imports during refactoring
    from config.settings import EXCLUDE_INSUFFICIENT_TIME, MIN_VISIBILITY_HOURS, BORTLE_INDEX
    
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
                    if obj.sufficient_time or not exclude_insufficient:
                        filtered_objects.append(obj)
                    else:
                        insufficient_objects.append(obj)
                else:
                    obj.sufficient_time = False
                    insufficient_objects.append(obj)
            else:
                # Object without magnitude - assume visible if duration meets minimum
                if duration >= MIN_VISIBILITY_HOURS:
                    obj.sufficient_time = True
                    filtered_objects.append(obj)
                else:
                    obj.sufficient_time = False
                    insufficient_objects.append(obj)
    
    return filtered_objects, insufficient_objects 