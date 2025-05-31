"""
Object selection and scoring functions for astronomical observation planning.
"""

import math
from datetime import timedelta
from models import SchedulingStrategy
from astronomy import calculate_altaz, calculate_required_exposure


def calculate_object_score(obj, periods, strategy=SchedulingStrategy.LONGEST_DURATION):
    """Calculate object score based on scheduling strategy"""
    from astronomy import calculate_visibility_duration
    
    duration = calculate_visibility_duration(periods)
    
    # Handle mosaic groups differently
    if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
        if strategy == SchedulingStrategy.MOSAIC_GROUPS:
            # For mosaic groups, prioritize by number of objects and total duration
            return obj.object_count * duration * 10  # High multiplier for mosaic groups
        else:
            # For other strategies, treat as composite object
            exposure_time = duration / 2  # Estimate based on group complexity
            panels = 1  # Mosaic groups are already pre-paneled
    else:
        # Import config constants
        from config.settings import BORTLE_INDEX
        exposure_time, frames, panels = calculate_required_exposure(
            obj.magnitude, BORTLE_INDEX, obj.fov)
    
    if strategy == SchedulingStrategy.LONGEST_DURATION:
        return duration
    
    elif strategy == SchedulingStrategy.MAX_OBJECTS:
        # Prefer objects that need just enough time
        if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
            return obj.object_count * duration  # Favor mosaic groups with more objects
        return 1.0 / abs(duration - exposure_time)
    
    elif strategy == SchedulingStrategy.OPTIMAL_SNR:
        # Consider magnitude and sky position
        alt_score = max(calculate_max_altitude(obj, periods[0][0], periods[-1][1]), 30) / 90
        mag_score = (20 - obj.magnitude) / 20  # Brighter objects score higher
        return alt_score * mag_score
    
    elif strategy == SchedulingStrategy.MINIMAL_MOSAIC:
        # Prefer objects requiring fewer panels
        return 1.0 / panels
    
    elif strategy == SchedulingStrategy.DIFFICULTY_BALANCED:
        # Balance between difficulty and feasibility
        difficulty = obj.magnitude / 20 + panels / 10
        feasibility = duration / exposure_time
        return feasibility / difficulty
    
    elif strategy == SchedulingStrategy.MOSAIC_GROUPS:
        # Prioritize mosaic groups over individual objects
        if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
            return obj.object_count * duration * 10  # High score for mosaic groups
        else:
            return duration * 0.1  # Lower score for individual objects
    
    return duration


def calculate_max_altitude(obj, start_time, end_time):
    """Calculate maximum altitude during visibility period"""
    from config.settings import TRAJECTORY_INTERVAL_MINUTES
    
    max_alt = 0
    current_time = start_time
    while current_time <= end_time:
        alt, _ = calculate_altaz(obj, current_time)
        max_alt = max(max_alt, alt)
        current_time += timedelta(minutes=TRAJECTORY_INTERVAL_MINUTES)
    return max_alt


def find_best_objects(visibility_periods, max_overlapping=None):
    """Select objects with longest visibility periods and minimal overlap"""
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