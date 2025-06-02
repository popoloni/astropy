#!/usr/bin/env python3
"""
Mosaic Group Analysis for Vaonis Vespera Passenger
==================================================
Analyzes which celestial objects can be photographed together in the same mosaic field of view.
Mosaic FOV: 4.7° × 3.5°
"""

import math
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from specific modules to avoid circular imports
from astronomy import (
    calculate_altaz, get_local_timezone,
    find_astronomical_twilight, find_visibility_window,
    calculate_visibility_duration
)
from catalogs import get_combined_catalog, get_objects_from_csv
from config.settings import load_config, MIN_VISIBILITY_HOURS, USE_CSV_CATALOG
from utilities.time_sim import get_current_datetime

# Load configuration
CONFIG = load_config()

# Get mosaic FOV from settings (which loads from scope_data.json)
from config.settings import MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT

def calculate_angular_separation(obj1, obj2):
    """
    Calculate angular separation between two objects using spherical trigonometry.
    Returns separation in degrees.
    """
    # Convert coordinates from object format (radians) to RA/Dec
    ra1 = obj1.ra  # already in radians
    dec1 = obj1.dec  # already in radians
    ra2 = obj2.ra  # already in radians
    dec2 = obj2.dec  # already in radians
    
    # Calculate angular separation using spherical law of cosines
    cos_d = (math.sin(dec1) * math.sin(dec2) + 
             math.cos(dec1) * math.cos(dec2) * math.cos(ra2 - ra1))
    
    # Ensure value is in valid range to avoid math domain errors
    cos_d = min(1.0, max(-1.0, cos_d))
    
    # Convert to degrees
    separation = math.degrees(math.acos(cos_d))
    
    return separation

def can_fit_in_mosaic(objects_list):
    """
    Check if a list of objects can fit within the mosaic field of view.
    Returns True if all objects fit, False otherwise.
    """
    if len(objects_list) < 2:
        return True
        
    # Calculate the bounding box of all objects
    ra_coords = [obj.ra for obj in objects_list]
    dec_coords = [obj.dec for obj in objects_list]
    
    # Handle RA wraparound (0h/24h boundary)
    ra_min = min(ra_coords)
    ra_max = max(ra_coords)
    ra_span = ra_max - ra_min
    
    # Check for wraparound case
    if ra_span > math.pi:  # More than 180 degrees, likely wraparound
        ra_span = 2 * math.pi - ra_span
    
    # Convert RA span to degrees (considering declination)
    avg_dec = sum(dec_coords) / len(dec_coords)
    ra_span_deg = math.degrees(ra_span) * math.cos(avg_dec)
    
    # Calculate declination span
    dec_span_deg = math.degrees(max(dec_coords) - min(dec_coords))
    
    # Check if objects fit within mosaic FOV with 10% margin for positioning
    fits_ra = ra_span_deg <= MOSAIC_FOV_WIDTH * 0.9
    fits_dec = dec_span_deg <= MOSAIC_FOV_HEIGHT * 0.9
    
    return fits_ra and fits_dec

def objects_visible_simultaneously(objects_list, start_time, end_time):
    """
    Check if objects are visible simultaneously during the given time period.
    Returns the overlapping time period if they are, None otherwise.
    """
    if not objects_list:
        return None
        
    # Get visibility windows for all objects
    visibility_windows = []
    for obj in objects_list:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=True)
        if not periods:
            return None  # One object is not visible at all
        visibility_windows.append(periods)
    
    # Find overlapping time periods
    overlap_periods = []
    
    # For each combination of periods, find overlaps
    for periods in visibility_windows:
        if not overlap_periods:
            overlap_periods = periods
        else:
            new_overlaps = []
            for period in periods:
                for overlap in overlap_periods:
                    # Find intersection
                    start_overlap = max(period[0], overlap[0])
                    end_overlap = min(period[1], overlap[1])
                    
                    if start_overlap < end_overlap:
                        new_overlaps.append((start_overlap, end_overlap))
            
            overlap_periods = new_overlaps
            
            if not overlap_periods:
                return None  # No overlap found
    
    return overlap_periods

def analyze_object_groups(objects, start_time, end_time):
    """
    Analyze which objects can be grouped together for mosaic photography.
    """
    print("MOSAIC GROUP ANALYSIS")
    print("=" * 50)
    print(f"Mosaic Field of View: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°")
    print(f"Analysis period: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
    print()
    
    groups_found = []
    used_objects = set()
    
    # Try to find groups of 2-4 objects that can fit together
    for group_size in range(4, 1, -1):  # Start with larger groups
        for i, obj1 in enumerate(objects):
            if obj1.name in used_objects:
                continue
                
            # Try to build a group starting with obj1
            current_group = [obj1]
            
            for j, obj2 in enumerate(objects):
                if j <= i or obj2.name in used_objects:
                    continue
                    
                # Test if we can add obj2 to the current group
                test_group = current_group + [obj2]
                
                if len(test_group) > group_size:
                    continue
                    
                # Check if objects fit spatially
                if can_fit_in_mosaic(test_group):
                    # Check if objects are visible simultaneously
                    overlap_periods = objects_visible_simultaneously(test_group, start_time, end_time)
                    if overlap_periods:
                        # Calculate total overlap duration
                        total_overlap = sum(
                            (period[1] - period[0]).total_seconds() / 3600
                            for period in overlap_periods
                        )
                        
                        if total_overlap >= MIN_VISIBILITY_HOURS:
                            current_group.append(obj2)
            
            # If we found a group of at least 2 objects
            if len(current_group) >= 2:
                # Check final validity
                if can_fit_in_mosaic(current_group):
                    overlap_periods = objects_visible_simultaneously(current_group, start_time, end_time)
                    if overlap_periods:
                        total_overlap = sum(
                            (period[1] - period[0]).total_seconds() / 3600
                            for period in overlap_periods
                        )
                        
                        if total_overlap >= MIN_VISIBILITY_HOURS:
                            groups_found.append((current_group, overlap_periods))
                            for obj in current_group:
                                used_objects.add(obj.name)
    
    return groups_found

def print_group_analysis(groups):
    """Print the analysis results."""
    if not groups:
        print("No suitable object groups found for mosaic photography.")
        return
    
    print(f"Found {len(groups)} suitable mosaic groups:")
    print()
    
    for i, (group, overlap_periods) in enumerate(groups, 1):
        print(f"MOSAIC GROUP {i}")
        print("-" * 30)
        
        # Calculate group spatial extent
        ra_coords = [obj.ra for obj in group]
        dec_coords = [obj.dec for obj in group]
        
        ra_span = math.degrees(max(ra_coords) - min(ra_coords))
        dec_span = math.degrees(max(dec_coords) - min(dec_coords))
        
        # Handle RA wraparound
        if ra_span > 180:
            ra_span = 360 - ra_span
            
        # Adjust RA span for declination
        avg_dec = sum(dec_coords) / len(dec_coords)
        ra_span *= math.cos(avg_dec)
        
        print(f"Spatial extent: {ra_span:.1f}° × {dec_span:.1f}°")
        print(f"Objects ({len(group)}):")
        
        for obj in group:
            ra_hours = math.degrees(obj.ra) / 15
            dec_deg = math.degrees(obj.dec)
            print(f"  • {obj.name}")
            print(f"    RA: {ra_hours:.2f}h, Dec: {dec_deg:.1f}°")
            if hasattr(obj, 'magnitude') and obj.magnitude:
                print(f"    Magnitude: {obj.magnitude}")
            if obj.fov:
                print(f"    FOV: {obj.fov}")
        
        print("\nSimultaneous visibility periods:")
        total_time = 0
        for period_start, period_end in overlap_periods:
            duration = (period_end - period_start).total_seconds() / 3600
            total_time += duration
            print(f"  {period_start.strftime('%H:%M')} - {period_end.strftime('%H:%M')} ({duration:.1f}h)")
        
        print(f"Total overlap time: {total_time:.1f} hours")
        
        # Calculate separations between objects
        print("\nObject separations:")
        for j, obj1 in enumerate(group):
            for k, obj2 in enumerate(group):
                if j < k:
                    sep = calculate_angular_separation(obj1, obj2)
                    obj1_short = obj1.name.split('/')[0]
                    obj2_short = obj2.name.split('/')[0]
                    print(f"  {obj1_short} - {obj2_short}: {sep:.1f}°")
        
        print()

def main():
    """Main function."""
    # Get current time and calculate observation period
    current_date = get_current_datetime(get_local_timezone())
    
    # Calculate night period
    if current_date.hour < 12:
        yesterday = current_date - timedelta(days=1)
        twilight_evening, twilight_morning = find_astronomical_twilight(yesterday)
    else:
        twilight_evening, twilight_morning = find_astronomical_twilight(current_date)
    
    # Check if we're currently in the night
    local_tz = get_local_timezone()
    if twilight_evening.tzinfo != local_tz:
        twilight_evening = twilight_evening.astimezone(local_tz)
    if twilight_morning.tzinfo != local_tz:
        twilight_morning = twilight_morning.astimezone(local_tz)
    
    is_night_time = (current_date >= twilight_evening and current_date <= twilight_morning)
    
    if is_night_time:
        start_time = twilight_evening #current_date  # EP 24/05/2025 - reverted back
        end_time = twilight_morning
    else:
        start_time = twilight_evening
        end_time = twilight_morning
    
    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
    else:
        all_objects = get_combined_catalog()
    
    if not all_objects:
        print("No objects found!")
        return
    
    # Filter for objects visible during the observation period
    visible_objects = []
    for obj in all_objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=True)
        if periods:
            duration = calculate_visibility_duration(periods)
            if duration >= MIN_VISIBILITY_HOURS:
                visible_objects.append(obj)
    
    if not visible_objects:
        print("No objects are visible during the observation period!")
        return
    
    print(f"Analyzing {len(visible_objects)} visible objects...")
    print()
    
    # Analyze groups
    groups = analyze_object_groups(visible_objects, start_time, end_time)
    
    # Print results
    print_group_analysis(groups)

if __name__ == "__main__":
    main() 
