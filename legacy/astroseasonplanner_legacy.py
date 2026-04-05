#!/usr/bin/env python3
"""
Trajectory Analysis and Weekly Astrophotography Planning
Analyzes trajectory density, moon conditions, and mosaic opportunities throughout the year
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict, Counter
import math
from typing import List, Dict, Tuple, Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the main astronightplanner module (now in same directory)
from astronightplanner import (
    get_objects_from_csv, get_combined_catalog, filter_visible_objects,
    find_astronomical_twilight, setup_altaz_plot, plot_object_trajectory,
    get_local_timezone, USE_CSV_CATALOG, DEFAULT_LOCATION, CONFIG,
    MIN_VISIBILITY_HOURS, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, is_visible,
    find_visibility_window, calculate_visibility_duration
)

# Import high precision functions
try:
    from astronomy.precision import (
        set_precision_mode, get_precision_mode, precision_context,
        calculate_high_precision_moon_position, calculate_high_precision_moon_phase,
        find_precise_astronomical_twilight, calculate_precise_altaz,
        get_phase3_status, list_available_features
    )
    HIGH_PRECISION_AVAILABLE = True
    print("High precision astronomical calculations available")
except ImportError as e:
    HIGH_PRECISION_AVAILABLE = False
    print(f"High precision features not available: {e}")
    print("Using standard precision calculations")

# Time period definitions
HALF_YEAR_RANGES = {
    'H1': (1, 26),   # First half: weeks 1-26
    'H2': (27, 52)   # Second half: weeks 27-52
}

QUARTER_RANGES = {
    'Q1': (1, 13),   # Q1: weeks 1-13
    'Q2': (14, 26),  # Q2: weeks 14-26
    'Q3': (27, 39),  # Q3: weeks 27-39
    'Q4': (40, 52)   # Q4: weeks 40-52
}

MONTH_TO_WEEKS = {
    1: (1, 4),    # January: weeks 1-4
    2: (5, 8),    # February: weeks 5-8
    3: (9, 13),   # March: weeks 9-13
    4: (14, 17),  # April: weeks 14-17
    5: (18, 22),  # May: weeks 18-22
    6: (23, 26),  # June: weeks 23-26
    7: (27, 30),  # July: weeks 27-30
    8: (31, 35),  # August: weeks 31-35
    9: (36, 39),  # September: weeks 36-39
    10: (40, 43), # October: weeks 40-43
    11: (44, 47), # November: weeks 44-47
    12: (48, 52)  # December: weeks 48-52
}

def get_moon_phase(date):
    """Calculate moon phase (0 = new moon, 1 = full moon)"""
    if HIGH_PRECISION_AVAILABLE:
        try:
            # Use high precision moon phase calculation
            phase_data = calculate_high_precision_moon_phase(date)
            # Handle different possible return structures
            if isinstance(phase_data, dict):
                # Try different possible keys
                if 'phase' in phase_data:
                    return phase_data['phase']
                elif 'illumination' in phase_data:
                    return phase_data['illumination']
                elif 'phase_fraction' in phase_data:
                    return phase_data['phase_fraction']
                else:
                    # If it's a dict but no recognized keys, use first numeric value
                    for value in phase_data.values():
                        if isinstance(value, (int, float)):
                            return float(value)
            elif isinstance(phase_data, (int, float)):
                # Direct numeric return
                return float(phase_data)
            else:
                raise ValueError(f"Unexpected moon phase data type: {type(phase_data)}")
        except Exception as e:
            print(f"High precision moon phase failed, using standard: {e}")
    
    # Fallback to simple moon phase calculation (approximate)
    # Based on the fact that lunar cycle is approximately 29.53 days
    # Known new moon: January 13, 2025 (updated to current year)
    known_new_moon = datetime(2025, 1, 13)
    days_since_new_moon = (date - known_new_moon).days
    lunar_cycle = 29.53
    phase = (days_since_new_moon % lunar_cycle) / lunar_cycle
    return phase

def get_moon_illumination(phase):
    """Calculate moon illumination percentage from phase"""
    # 0 = new moon (0% illumination), 0.5 = full moon (100% illumination)
    if phase <= 0.5:
        return phase * 2  # 0 to 1
    else:
        return (1 - phase) * 2  # 1 to 0

def calculate_moon_position(date, hour_offset=0):
    """Calculate moon position using high precision when available"""
    if HIGH_PRECISION_AVAILABLE:
        try:
            # Use high precision moon position calculation
            adjusted_date = date + timedelta(hours=hour_offset)
            moon_data = calculate_high_precision_moon_position(adjusted_date)
            # Handle different possible return structures
            if isinstance(moon_data, dict):
                if 'ra' in moon_data and 'dec' in moon_data:
                    return moon_data['ra'], moon_data['dec']
                elif 'right_ascension' in moon_data and 'declination' in moon_data:
                    return moon_data['right_ascension'], moon_data['declination']
            raise ValueError(f"Unexpected moon position data structure: {moon_data}")
        except Exception as e:
            print(f"High precision moon position failed, using standard: {e}")
    
    # Fallback to simplified calculation
    total_hours = (date - datetime(2024, 1, 1)).total_seconds() / 3600 + hour_offset
    
    # Moon moves approximately 13.2 degrees per day in RA
    moon_ra = (total_hours * 13.2 / 24) % 360
    
    # Simplified declination calculation
    moon_dec = 23.5 * math.sin(math.radians(moon_ra * 0.98))  # Slight offset from sun
    
    return moon_ra, moon_dec

def is_moon_interference(obj_ra, obj_dec, moon_ra, moon_dec, moon_illumination, separation_threshold=60):
    """Check if moon causes interference for an object"""
    # Calculate angular separation
    ra_diff = abs(obj_ra - moon_ra)
    if ra_diff > 180:
        ra_diff = 360 - ra_diff
    
    dec_diff = abs(obj_dec - moon_dec)
    separation = math.sqrt(ra_diff**2 + dec_diff**2)
    
    # Moon interference depends on illumination and separation
    # For astrophotography, moon affects wider areas than visual observation
    # BUT we need to be more realistic about when objects are actually usable
    
    if moon_illumination < 0.05:  # Very new moon (dark)
        interference_threshold = 5
        sky_brightness_penalty = False
    elif moon_illumination < 0.15:  # Thin crescent
        interference_threshold = 10
        sky_brightness_penalty = False
    elif moon_illumination < 0.3:  # Quarter moon
        interference_threshold = 20
        sky_brightness_penalty = False
    elif moon_illumination < 0.5:  # Half to gibbous
        interference_threshold = 30
        sky_brightness_penalty = False
    elif moon_illumination < 0.75:  # Gibbous moon
        interference_threshold = 45
        # Only apply sky brightness penalty if moon is very close
        sky_brightness_penalty = (separation < 15)
    elif moon_illumination < 0.9:  # Nearly full
        interference_threshold = 60
        # Apply sky brightness penalty for closer objects
        sky_brightness_penalty = (separation < 30)
    else:  # Full moon - affects most of sky but some distant objects still usable
        interference_threshold = 90
        # Apply broader penalty for full moon
        sky_brightness_penalty = (separation < 45)
    
    is_interfered = separation < interference_threshold or sky_brightness_penalty
    
    return is_interfered, separation

def get_weeks_for_period(period_type, period_value, year=None):
    """Get week numbers for a specified time period"""
    if year is None:
        year = datetime.now().year  # Use current year by default
    
    if period_type == 'year':
        return list(range(1, 53))
    elif period_type == 'half':
        if period_value.upper() in HALF_YEAR_RANGES:
            start_week, end_week = HALF_YEAR_RANGES[period_value.upper()]
            return list(range(start_week, end_week + 1))
    elif period_type == 'quarter':
        if period_value.upper() in QUARTER_RANGES:
            start_week, end_week = QUARTER_RANGES[period_value.upper()]
            return list(range(start_week, end_week + 1))
    elif period_type == 'month':
        if isinstance(period_value, int) and 1 <= period_value <= 12:
            start_week, end_week = MONTH_TO_WEEKS[period_value]
            return list(range(start_week, end_week + 1))
        elif isinstance(period_value, str):
            try:
                month_num = int(period_value)
                if 1 <= month_num <= 12:
                    start_week, end_week = MONTH_TO_WEEKS[month_num]
                    return list(range(start_week, end_week + 1))
            except ValueError:
                pass
    
    # Default to current week ± 4 weeks if invalid input
    current_week = datetime.now().isocalendar()[1]
    return list(range(max(1, current_week - 4), min(53, current_week + 4)))

def get_weekly_dates(weeks_to_analyze, year=None):
    """Get dates for specified weeks"""
    if year is None:
        year = datetime.now().year  # Use current year by default
    
    weekly_dates = {}
    
    for week_num in weeks_to_analyze:
        # Get first day of the week
        jan_1 = datetime(year, 1, 1)
        week_start = jan_1 + timedelta(weeks=week_num-1)
        # Adjust to Monday
        week_start = week_start - timedelta(days=week_start.weekday())
        
        # Sample middle of the week for analysis
        week_sample = week_start + timedelta(days=3)  # Thursday
        
        if week_sample.year == year:  # Ensure we're still in the target year
            weekly_dates[week_num] = week_sample
    
    return weekly_dates

def detect_mosaic_clusters(objects, config_fov=None, bortle_index=6):
    """Detect groups of objects and individual objects that require mosaics based on telescope FOV"""
    if len(objects) == 0:
        return []
    
    # Get FOV from config if not provided
    if config_fov is None:
        # Default values from config.json for Vaonis Vespera Passenger
        single_fov_width = 2.4  # degrees
        single_fov_height = 1.8  # degrees
        mosaic_fov_width = 4.7   # degrees
        mosaic_fov_height = 3.5  # degrees
    else:
        single_fov_width = config_fov['single_width']
        single_fov_height = config_fov['single_height'] 
        mosaic_fov_width = config_fov['mosaic_width']
        mosaic_fov_height = config_fov['mosaic_height']
    
    print(f"FOV Configuration:")
    print(f"  Single frame: {single_fov_width}° × {single_fov_height}°")
    print(f"  Mosaic frame: {mosaic_fov_width}° × {mosaic_fov_height}°")
    
    clusters = []
    used_objects = set()
    
    # First pass: Handle objects that individually require mosaics
    individual_mosaic_objects = []
    single_frame_candidates = []
    
    for i, obj in enumerate(objects):
        if i in used_objects:
            continue
            
        # Get imaging requirements for this object
        imaging_req = get_object_imaging_requirements(obj, bortle_index)
        panels_info = imaging_req['panels_info']
        
        if panels_info['requires_mosaic']:
            # This object alone requires a mosaic
            individual_mosaic_objects.append(obj)
            clusters.append([obj])  # Single-object mosaic
            used_objects.add(i)
            print(f"    {obj.name}: {panels_info['obj_width']:.2f}° × {panels_info['obj_height']:.2f}° → {panels_info['panels_needed']} panels (individual mosaic)")
        else:
            single_frame_candidates.append((i, obj))
    
    print(f"  Individual mosaic objects: {len(individual_mosaic_objects)}")
    
    # Second pass: Group remaining objects that can fit together in mosaic frame
    effective_mosaic_width = mosaic_fov_width * 0.8
    effective_mosaic_height = mosaic_fov_height * 0.8
    
    # Sort candidates by RA for consistent processing
    single_frame_candidates.sort(key=lambda x: x[1].ra)
    
    for idx, (i, seed_obj) in enumerate(single_frame_candidates):
        if i in used_objects:
            continue
        
        # Start new cluster with this seed object
        cluster_objects = [seed_obj]
        cluster_indices = [i]
        used_objects.add(i)
        
        # Find nearby objects that can form a compact group
        candidates = []
        
        for _, (j, obj2) in enumerate(single_frame_candidates):
            if j in used_objects:
                continue
            
            # Calculate angular separation from seed object
            ra_diff = abs(seed_obj.ra - obj2.ra)
            if ra_diff > 180:
                ra_diff = 360 - ra_diff
            dec_diff = abs(seed_obj.dec - obj2.dec)
            
            # Use a more restrictive distance - objects should be relatively close
            max_separation = min(effective_mosaic_width, effective_mosaic_height) / 2
            
            if ra_diff <= effective_mosaic_width and dec_diff <= effective_mosaic_height:
                candidates.append((j, obj2, ra_diff, dec_diff))
        
        # Sort candidates by distance and add closest ones first
        candidates.sort(key=lambda x: math.sqrt(x[2]**2 + x[3]**2))
        
        # Add candidates while cluster remains compact
        for j, obj2, ra_diff, dec_diff in candidates[:8]:  # Limit to 8 closest candidates
            if j in used_objects:
                continue
                
            # Test adding this object to the cluster
            temp_cluster = cluster_objects + [obj2]
            
            # Calculate bounding box of the enlarged cluster
            ra_coords = [obj.ra for obj in temp_cluster]
            dec_coords = [obj.dec for obj in temp_cluster]
            
            ra_span = calculate_ra_span(ra_coords)
            dec_span = max(dec_coords) - min(dec_coords)
            
            # Check if enlarged cluster still fits comfortably within mosaic FOV
            if (ra_span <= effective_mosaic_width and 
                dec_span <= effective_mosaic_height and 
                len(temp_cluster) <= 6):  # Practical limit for mosaic complexity
                
                cluster_objects.append(obj2)
                cluster_indices.append(j)
                used_objects.add(j)
        
        # Add the final cluster
        clusters.append(cluster_objects)
    
    return clusters

def calculate_ra_span(ra_coords):
    """Calculate RA span handling wrap-around at 0/360 degrees"""
    if not ra_coords:
        return 0
    
    if len(ra_coords) == 1:
        return 0
    
    # Sort coordinates
    sorted_ra = sorted(ra_coords)
    
    # Calculate span without wrap-around
    normal_span = sorted_ra[-1] - sorted_ra[0]
    
    # Calculate span with wrap-around
    wrap_span = (sorted_ra[0] + 360) - sorted_ra[-1]
    
    # Return the smaller span
    return min(normal_span, wrap_span)

def get_fov_config():
    """Get FOV configuration from config file"""
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        scope_config = config.get('imaging', {}).get('scope', {})
        return {
            'single_width': scope_config.get('fov_width', 2.4),
            'single_height': scope_config.get('fov_height', 1.8),
            'mosaic_width': scope_config.get('mosaic_fov_width', 4.7),
            'mosaic_height': scope_config.get('mosaic_fov_height', 3.5)
        }
    except Exception as e:
        print(f"Warning: Could not read FOV config: {e}")
        return None

def analyze_mosaic_statistics(clusters):
    """Analyze mosaic clustering statistics for debugging"""
    single_count = len([c for c in clusters if len(c) == 1])
    mosaic_count = len([c for c in clusters if len(c) > 1])
    total_in_mosaics = sum(len(c) for c in clusters if len(c) > 1)
    
    cluster_sizes = [len(c) for c in clusters if len(c) > 1]
    
    # Calculate mosaic type distribution
    small_mosaics = len([c for c in clusters if 2 <= len(c) <= 3])  # 2-3 objects
    medium_mosaics = len([c for c in clusters if 4 <= len(c) <= 6])  # 4-6 objects  
    large_mosaics = len([c for c in clusters if len(c) > 6])  # 7+ objects
    
    return {
        'total_clusters': len(clusters),
        'single_frame_targets': single_count,
        'mosaic_groups': mosaic_count,
        'objects_in_mosaics': total_in_mosaics,
        'cluster_sizes': cluster_sizes,
        'largest_cluster': max(cluster_sizes) if cluster_sizes else 0,
        'avg_cluster_size': sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0,
        'small_mosaics': small_mosaics,  # 2-3 objects
        'medium_mosaics': medium_mosaics,  # 4-6 objects
        'large_mosaics': large_mosaics  # 7+ objects
    }

def check_object_visibility_in_config_window(obj, twilight_evening, twilight_morning):
    """Check if object is visible within the configured visibility window"""
    from astronightplanner import calculate_altaz
    
    # Find visibility periods within the config-defined window
    visibility_periods = find_visibility_window(obj, twilight_evening, twilight_morning, use_margins=True)
    
    if not visibility_periods:
        return False, 0.0
    
    # Calculate total visibility duration
    total_duration = calculate_visibility_duration(visibility_periods)
    
    # Check if it meets minimum visibility requirement
    meets_min_duration = total_duration >= MIN_VISIBILITY_HOURS
    
    return meets_min_duration, total_duration

def safe_find_precise_twilight(date, observer_lat_rad, observer_lon_rad, twilight_type, event_type):
    """
    Safe wrapper for find_precise_astronomical_twilight that handles timezone issues.
    """
    try:
        # Ensure input date is timezone-naive (as expected by the function)
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)
        
        # Call the high precision function
        result = find_precise_astronomical_twilight(date, observer_lat_rad, observer_lon_rad, twilight_type, event_type)
        
        # Ensure result is timezone-naive to match our workflow
        if hasattr(result, 'tzinfo') and result.tzinfo is not None:
            result = result.replace(tzinfo=None)
            
        return result
        
    except Exception as e:
        # If high precision fails, fall back to standard calculation
        raise Exception(f"High precision twilight failed: {e}")

def analyze_weekly_conditions(objects, week_date):
    """Analyze conditions for a specific week"""
    # Get Bortle index from config
    try:
        from astronightplanner import DEFAULT_LOCATION
        bortle_index = DEFAULT_LOCATION.get('bortle_index', 6)
    except:
        bortle_index = 6  # Default moderate sky
    
    # Ensure week_date is timezone-naive
    if week_date.tzinfo is not None:
        week_date = week_date.replace(tzinfo=None)
    
    # Calculate twilight times using high precision when available
    if HIGH_PRECISION_AVAILABLE:
        try:
            # Get location from config
            observer_lat_deg = DEFAULT_LOCATION.get('latitude', 40.7128)
            observer_lon_deg = DEFAULT_LOCATION.get('longitude', -74.0060)
            
            # Convert to radians for high precision functions
            observer_lat_rad = math.radians(observer_lat_deg)
            observer_lon_rad = math.radians(observer_lon_deg)
            
            # Calculate evening and morning twilight separately using safe wrapper
            twilight_evening = safe_find_precise_twilight(week_date, observer_lat_rad, observer_lon_rad, 'astronomical', 'sunset')
            # For morning twilight, use next day and 'sunrise' event type
            next_day = week_date + timedelta(days=1)
            twilight_morning = safe_find_precise_twilight(next_day, observer_lat_rad, observer_lon_rad, 'astronomical', 'sunrise')
            
            # Results should already be timezone-naive from the wrapper
            
        except Exception as e:
            print(f"High precision twilight failed, using standard: {e}")
            twilight_evening, twilight_morning = find_astronomical_twilight(week_date)
            # Ensure standard twilight times are also timezone-naive
            if hasattr(twilight_evening, 'tzinfo') and twilight_evening.tzinfo is not None:
                twilight_evening = twilight_evening.replace(tzinfo=None)
            if hasattr(twilight_morning, 'tzinfo') and twilight_morning.tzinfo is not None:
                twilight_morning = twilight_morning.replace(tzinfo=None)
    else:
        twilight_evening, twilight_morning = find_astronomical_twilight(week_date)
        # Ensure standard twilight times are timezone-naive
        if hasattr(twilight_evening, 'tzinfo') and twilight_evening.tzinfo is not None:
            twilight_evening = twilight_evening.replace(tzinfo=None)
        if hasattr(twilight_morning, 'tzinfo') and twilight_morning.tzinfo is not None:
            twilight_morning = twilight_morning.replace(tzinfo=None)
    
    print(f"  Analyzing visibility for {week_date.strftime('%Y-%m-%d')} night...")
    print(f"  Twilight: {twilight_evening.strftime('%H:%M')} - {twilight_morning.strftime('%H:%M')}")
    print(f"  Bortle index: {bortle_index}")
    
    # Step 1: Filter objects that are visible within the config-defined visibility window
    # and meet minimum time requirements, considering imaging requirements
    observable_objects = []
    insufficient_time_objects = []
    exposure_limited_objects = []
    
    for obj in objects:
        meets_requirements, duration = check_object_visibility_in_config_window(
            obj, twilight_evening, twilight_morning
        )
        
        if meets_requirements:
            # Check if visibility duration is sufficient for required exposure
            imaging_req = get_object_imaging_requirements(obj, bortle_index)
            required_exposure = imaging_req['exposure_time_hours']
            
            if duration >= required_exposure:
                observable_objects.append(obj)
            else:
                exposure_limited_objects.append((obj, duration, required_exposure))
        else:
            insufficient_time_objects.append(obj)
    
    print(f"  Objects in visibility window with sufficient time: {len(observable_objects)}")
    print(f"  Objects with insufficient time: {len(insufficient_time_objects)}")
    print(f"  Objects limited by exposure requirements: {len(exposure_limited_objects)}")
    
    # Calculate moon conditions for this specific night
    moon_phase = get_moon_phase(week_date)
    moon_illumination = get_moon_illumination(moon_phase)
    
    # Calculate moon position for middle of the night - ensure timezone-naive arithmetic
    night_middle = twilight_evening + (twilight_morning - twilight_evening) / 2
    # Ensure all datetime objects are timezone-naive for calculations
    week_date_naive = week_date.replace(tzinfo=None) if week_date.tzinfo else week_date
    night_middle_naive = night_middle.replace(tzinfo=None) if hasattr(night_middle, 'tzinfo') and night_middle.tzinfo else night_middle
    
    moon_ra, moon_dec = calculate_moon_position(week_date_naive, 
                                              (night_middle_naive - week_date_naive).total_seconds() / 3600)
    
    print(f"  Moon illumination: {moon_illumination*100:.1f}%")
    
    # Step 2: Among observable objects, separate those affected by moon
    moon_free_objects = []
    moon_affected_objects = []
    
    for obj in observable_objects:
        is_interference, separation = is_moon_interference(
            obj.ra, obj.dec, moon_ra, moon_dec, moon_illumination
        )
        
        if is_interference:
            moon_affected_objects.append((obj, separation))
        else:
            moon_free_objects.append((obj, separation))
    
    print(f"  Moon-free objects: {len(moon_free_objects)}")
    print(f"  Moon-affected objects: {len(moon_affected_objects)}")
    
    # Step 3: Perform mosaic clustering ONLY on actually observable objects
    all_observable = [obj for obj, _ in moon_free_objects] + [obj for obj, _ in moon_affected_objects]
    
    if len(all_observable) > 0:
        print(f"  Performing mosaic analysis on {len(all_observable)} observable objects...")
        fov_config = get_fov_config()
        clusters = detect_mosaic_clusters(all_observable, fov_config, bortle_index)
        single_objects = [cluster for cluster in clusters if len(cluster) == 1]
        mosaic_groups = [cluster for cluster in clusters if len(cluster) > 1]
        
        # Analyze mosaic statistics
        mosaic_stats = analyze_mosaic_statistics(clusters)
        
        print(f"  Result: {len(single_objects)} single targets, {len(mosaic_groups)} mosaic groups")
    else:
        print(f"  No observable objects - skipping mosaic analysis")
        clusters = []
        single_objects = []
        mosaic_groups = []
        mosaic_stats = {
            'total_clusters': 0, 'single_frame_targets': 0, 'mosaic_groups': 0,
            'objects_in_mosaics': 0, 'cluster_sizes': [], 'largest_cluster': 0,
            'avg_cluster_size': 0, 'small_mosaics': 0, 'medium_mosaics': 0, 'large_mosaics': 0
        }
    
    # Step 4: Categorize mosaic clusters by moon interference
    moon_free_clusters = []
    moon_affected_clusters = []
    
    moon_free_obj_names = set(obj.name for obj, _ in moon_free_objects)
    
    for cluster in mosaic_groups:
        # Check if any object in cluster is moon-affected
        cluster_moon_free = all(obj.name in moon_free_obj_names for obj in cluster)
        
        if cluster_moon_free:
            moon_free_clusters.append(cluster)
        else:
            moon_affected_clusters.append(cluster)
    
    return {
        'week_date': week_date,
        'total_objects': len(objects),  # Total in catalog
        'observable_objects': len(all_observable),  # Actually observable this night
        'sufficient_time_objects': len(observable_objects),  # Meet time requirements
        'insufficient_time_objects': len(insufficient_time_objects),
        'exposure_limited_objects': len(exposure_limited_objects),
        'bortle_index': bortle_index,
        'moon_phase': moon_phase,
        'moon_illumination': moon_illumination,
        'moon_free_objects': moon_free_objects,
        'moon_affected_objects': moon_affected_objects,
        'single_objects': single_objects,
        'mosaic_groups': mosaic_groups,
        'moon_free_clusters': moon_free_clusters,
        'moon_affected_clusters': moon_affected_clusters,
        'mosaic_stats': mosaic_stats,
        'night_duration': (twilight_morning - twilight_evening).total_seconds() / 3600,
        'twilight_evening': twilight_evening,
        'twilight_morning': twilight_morning,
        'config_window_stats': {
            'min_altitude': MIN_ALT,
            'max_altitude': MAX_ALT,
            'min_azimuth': MIN_AZ,
            'max_azimuth': MAX_AZ,
            'min_visibility_hours': MIN_VISIBILITY_HOURS
        }
    }

def score_week_for_astrophotography(week_data):
    """Score a week for astrophotography potential"""
    score = 0
    
    # Base score from observable objects (not total catalog)
    score += week_data['observable_objects'] * 2
    
    # Bonus for moon-free objects (heavily weighted)
    score += len(week_data['moon_free_objects']) * 10
    
    # Bonus for mosaic opportunities
    score += len(week_data['mosaic_groups']) * 15
    score += len(week_data['moon_free_clusters']) * 25
    
    # Penalty for high moon illumination
    moon_penalty = week_data['moon_illumination'] * 50
    score -= moon_penalty
    
    # Bonus for sufficient observation time objects (config window compliant)
    score += week_data['sufficient_time_objects'] * 5
    
    # Bonus for longer nights
    score += week_data['night_duration'] * 5
    
    return max(0, score)  # Ensure non-negative score

def get_top_objects_for_week(week_data, top_n=5):
    """Get top recommended objects/groups for a week"""
    recommendations = []
    
    # Score individual objects
    for obj, moon_separation in week_data['moon_free_objects']:
        obj_score = 100 - week_data['moon_illumination'] * 30 + moon_separation
        recommendations.append({
            'type': 'single',
            'objects': [obj],
            'score': obj_score,
            'moon_free': True,
            'description': f"{obj.name} (single target)"
        })
    
    # Add moon-affected objects with lower scores
    for obj, moon_separation in week_data['moon_affected_objects'][:3]:  # Limit to top 3
        obj_score = 30 + moon_separation - week_data['moon_illumination'] * 40
        recommendations.append({
            'type': 'single',
            'objects': [obj],
            'score': obj_score,
            'moon_free': False,
            'description': f"{obj.name} (moon-affected)"
        })
    
    # Score mosaic groups (heavily favor these)
    for cluster in week_data['moon_free_clusters']:
        cluster_score = 150 + len(cluster) * 20 - week_data['moon_illumination'] * 20
        cluster_names = [obj.name for obj in cluster]
        recommendations.append({
            'type': 'mosaic',
            'objects': cluster,
            'score': cluster_score,
            'moon_free': True,
            'description': f"Mosaic group: {', '.join(cluster_names[:3])}{'...' if len(cluster) > 3 else ''}"
        })
    
    for cluster in week_data['moon_affected_clusters']:
        cluster_score = 80 + len(cluster) * 10 - week_data['moon_illumination'] * 50
        cluster_names = [obj.name for obj in cluster]
        recommendations.append({
            'type': 'mosaic',
            'objects': cluster,
            'score': cluster_score,
            'moon_free': False,
            'description': f"Mosaic group (moon-affected): {', '.join(cluster_names[:3])}{'...' if len(cluster) > 3 else ''}"
        })
    
    # Sort by score and return top N
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:top_n]

def analyze_yearly_object_conditions(weeks_to_analyze, year=None):
    """Analyze when each object is best photographed throughout the specified period"""
    if year is None:
        year = datetime.now().year
    
    print(f"Analyzing optimal conditions for each object for weeks {min(weeks_to_analyze)}-{max(weeks_to_analyze)} in year {year}...")
    
    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
    else:
        all_objects = get_combined_catalog()
    
    # Get weekly dates for specified weeks
    weekly_dates = get_weekly_dates(weeks_to_analyze, year)
    
    object_analysis = {}
    
    for obj in all_objects:
        object_analysis[obj.name] = {
            'best_weeks': [],
            'visibility_score_by_week': {},
            'moon_free_weeks': [],
            'config_compliant_weeks': [],
            'object': obj
        }
    
    # Analyze each week
    for week_num, week_date in weekly_dates.items():
        week_data = analyze_weekly_conditions(all_objects, week_date)
        
        # Update object analysis
        for obj, moon_separation in week_data['moon_free_objects']:
            score = 100 + moon_separation - week_data['moon_illumination'] * 30
            object_analysis[obj.name]['visibility_score_by_week'][week_num] = score
            object_analysis[obj.name]['moon_free_weeks'].append(week_num)
            
            # Check if object meets config requirements
            if obj in [o for o, _ in week_data['moon_free_objects']] and week_num not in object_analysis[obj.name]['config_compliant_weeks']:
                meets_requirements, _ = check_object_visibility_in_config_window(
                    obj, week_data['twilight_evening'], week_data['twilight_morning']
                )
                if meets_requirements:
                    object_analysis[obj.name]['config_compliant_weeks'].append(week_num)
        
        for obj, moon_separation in week_data['moon_affected_objects']:
            score = 30 + moon_separation - week_data['moon_illumination'] * 50
            object_analysis[obj.name]['visibility_score_by_week'][week_num] = score
    
    # Find best weeks for each object
    for obj_name, data in object_analysis.items():
        if data['visibility_score_by_week']:
            # Sort weeks by score
            sorted_weeks = sorted(data['visibility_score_by_week'].items(), 
                                key=lambda x: x[1], reverse=True)
            data['best_weeks'] = sorted_weeks[:5]  # Top 5 weeks
    
    return object_analysis

def analyze_weekly_astrophotography(period_type='year', period_value=None, year=None):
    """Main weekly analysis function with configurable time periods"""
    if year is None:
        year = datetime.now().year
    
    period_desc = get_period_description(period_type, period_value)
    print(f"Starting weekly astrophotography analysis for {period_desc} {year}...")
    
    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
    else:
        all_objects = get_combined_catalog()
    
    # Get weeks to analyze based on period selection
    weeks_to_analyze = get_weeks_for_period(period_type, period_value, year)
    weekly_dates = get_weekly_dates(weeks_to_analyze, year)
    
    print(f"Analyzing {len(weeks_to_analyze)} weeks (weeks {min(weeks_to_analyze)}-{max(weeks_to_analyze)}) for year {year}")
    
    weekly_results = {}
    
    # Analyze each week
    for week_num, week_date in weekly_dates.items():
        print(f"\nAnalyzing week {week_num} ({week_date.strftime('%Y-%m-%d')})...")
        
        week_data = analyze_weekly_conditions(all_objects, week_date)
        week_data['score'] = score_week_for_astrophotography(week_data)
        week_data['top_objects'] = get_top_objects_for_week(week_data)
        
        weekly_results[week_num] = week_data
        
        print(f"  Total catalog objects: {week_data['total_objects']}")
        print(f"  Observable tonight: {week_data['observable_objects']}")
        print(f"  Config-compliant: {week_data['sufficient_time_objects']}")
        print(f"  Exposure-limited: {week_data['exposure_limited_objects']}")
        print(f"  Moon illumination: {week_data['moon_illumination']*100:.1f}%")
        print(f"  Moon-free objects: {len(week_data['moon_free_objects'])}")
        print(f"  Single-frame targets: {week_data['mosaic_stats']['single_frame_targets']}")
        print(f"  Mosaic groups: {len(week_data['mosaic_groups'])} (Small: {week_data['mosaic_stats']['small_mosaics']}, Medium: {week_data['mosaic_stats']['medium_mosaics']}, Large: {week_data['mosaic_stats']['large_mosaics']})")
        if week_data['mosaic_stats']['cluster_sizes']:
            print(f"  Mosaic sizes: {week_data['mosaic_stats']['cluster_sizes']}")
        print(f"  Week score: {week_data['score']:.1f}")
    
    return weekly_results, weeks_to_analyze

def get_period_description(period_type, period_value):
    """Get human-readable description of the analysis period"""
    if period_type == 'year':
        return "entire year"
    elif period_type == 'half':
        return f"half-year {period_value.upper()}"
    elif period_type == 'quarter':
        return f"quarter {period_value.upper()}"
    elif period_type == 'month':
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        if isinstance(period_value, int) and 1 <= period_value <= 12:
            return f"month {month_names[period_value]}"
        else:
            return f"month {period_value}"
    else:
        return "selected period"

def plot_weekly_analysis(weekly_results, period_desc="analysis period"):
    """Create comprehensive plots for weekly analysis"""
    weeks = sorted(weekly_results.keys())
    
    # Extract data for plotting
    observable_objects = [weekly_results[w]['observable_objects'] for w in weeks]
    config_compliant = [weekly_results[w]['sufficient_time_objects'] for w in weeks]
    moon_illuminations = [weekly_results[w]['moon_illumination'] * 100 for w in weeks]
    moon_free_counts = [len(weekly_results[w]['moon_free_objects']) for w in weeks]
    mosaic_counts = [len(weekly_results[w]['mosaic_groups']) for w in weeks]
    scores = [weekly_results[w]['score'] for w in weeks]
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Weekly Astrophotography Analysis - {period_desc.title()}', fontsize=16)
    
    # Plot 1: Observable objects by week
    ax1 = axes[0, 0]
    scatter = ax1.scatter(weeks, observable_objects, c=scores, cmap='viridis', s=100, alpha=0.7)
    ax1.set_xlabel('Week Number')
    ax1.set_ylabel('Observable Objects')
    ax1.set_title('Observable Objects by Week')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Week Score')
    
    # Plot 2: Moon-free objects by week
    ax2 = axes[0, 1]
    bars = ax2.bar(weeks, moon_free_counts, alpha=0.7, color='green')
    ax2.set_xlabel('Week Number')
    ax2.set_ylabel('Moon-Free Objects')
    ax2.set_title('Moon-Free Objects by Week')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Mosaic opportunities
    ax3 = axes[0, 2]
    ax3.bar(weeks, mosaic_counts, alpha=0.7, color='orange')
    ax3.set_xlabel('Week Number')
    ax3.set_ylabel('Mosaic Groups')
    ax3.set_title('Mosaic Opportunities by Week')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Week scores
    ax4 = axes[1, 0]
    score_bars = ax4.bar(weeks, scores, alpha=0.7, color='purple')
    ax4.set_xlabel('Week Number')
    ax4.set_ylabel('Astrophotography Score')
    ax4.set_title('Weekly Astrophotography Scores')
    ax4.grid(True, alpha=0.3)
    
    # Highlight best week
    if weeks:
        best_week = max(weeks, key=lambda w: weekly_results[w]['score'])
        best_week_idx = weeks.index(best_week)
        score_bars[best_week_idx].set_color('gold')
    
    # Plot 5: Moon phase throughout weeks
    ax5 = axes[1, 1]
    moon_phases = [weekly_results[w]['moon_phase'] * 100 for w in weeks]
    ax5.plot(weeks, moon_phases, 'o-', color='blue', linewidth=2, markersize=8)
    ax5.set_xlabel('Week Number')
    ax5.set_ylabel('Moon Phase (%)')
    ax5.set_title('Moon Phase by Week')
    ax5.grid(True, alpha=0.3)
    ax5.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Full Moon')
    ax5.axhline(y=0, color='black', linestyle='--', alpha=0.5, label='New Moon')
    ax5.legend()
    
    # Plot 6: Objects distribution with config compliance
    ax6 = axes[1, 2]
    moon_affected_counts = [len(weekly_results[w]['moon_affected_objects']) for w in weeks]
    
    width = 0.25
    x = np.arange(len(weeks))
    ax6.bar(x - width, config_compliant, width, label='Config-Compliant', alpha=0.7, color='blue')
    ax6.bar(x, moon_free_counts, width, label='Moon-Free', alpha=0.7, color='green')
    ax6.bar(x + width, moon_affected_counts, width, label='Moon-Affected', alpha=0.7, color='red')
    
    ax6.set_xlabel('Week Number')
    ax6.set_ylabel('Object Count')
    ax6.set_title('Object Distribution by Week')
    ax6.set_xticks(x)
    ax6.set_xticklabels([str(w) for w in weeks])
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def print_weekly_summary(weekly_results, period_desc="analysis period"):
    """Print comprehensive weekly analysis summary"""
    print("\n" + "="*80)
    print(f"WEEKLY ASTROPHOTOGRAPHY ANALYSIS SUMMARY - {period_desc.upper()}")
    print("="*80)
    
    weeks = sorted(weekly_results.keys())
    if not weeks:
        print("No weeks analyzed.")
        return
    
    best_week = max(weeks, key=lambda w: weekly_results[w]['score'])
    best_week_data = weekly_results[best_week]
    
    print(f"\nAnalyzed {len(weeks)} weeks (weeks {min(weeks)}-{max(weeks)})")
    print(f"Best week for astrophotography: Week {best_week} ({best_week_data['week_date'].strftime('%Y-%m-%d')})")
    print(f"Best week score: {best_week_data['score']:.1f}")
    
    # Display config window information
    config_stats = best_week_data['config_window_stats']
    print(f"\nVisibility Window Configuration:")
    print(f"  Altitude range: {config_stats['min_altitude']}° - {config_stats['max_altitude']}°")
    print(f"  Azimuth range: {config_stats['min_azimuth']}° - {config_stats['max_azimuth']}°")
    print(f"  Minimum visibility: {config_stats['min_visibility_hours']} hours")
    
    # Best week details
    print(f"\nBest Week Details (Week {best_week}):")
    print(f"  Date: {best_week_data['week_date'].strftime('%Y-%m-%d (%A)')}")
    print(f"  Total catalog objects: {best_week_data['total_objects']}")
    print(f"  Observable objects: {best_week_data['observable_objects']}")
    print(f"  Config-compliant objects: {best_week_data['sufficient_time_objects']}")
    print(f"  Exposure-limited objects: {best_week_data['exposure_limited_objects']}")
    print(f"  Insufficient time objects: {best_week_data['insufficient_time_objects']}")
    print(f"  Bortle index: {best_week_data['bortle_index']}")
    print(f"  Moon illumination: {best_week_data['moon_illumination']*100:.1f}%")
    print(f"  Moon-free objects: {len(best_week_data['moon_free_objects'])}")
    print(f"  Moon-affected objects: {len(best_week_data['moon_affected_objects'])}")
    print(f"  Single objects: {len(best_week_data['single_objects'])}")
    print(f"  Mosaic groups: {len(best_week_data['mosaic_groups'])}")
    print(f"  Moon-free mosaics: {len(best_week_data['moon_free_clusters'])}")
    print(f"  Night duration: {best_week_data['night_duration']:.1f} hours")
    
    # Top recommendations for best week
    print(f"\nTop 5 Recommendations for Week {best_week}:")
    for i, rec in enumerate(best_week_data['top_objects'], 1):
        moon_status = "🌑 Moon-free" if rec['moon_free'] else "🌕 Moon-affected"
        print(f"  {i}. {rec['description']} - Score: {rec['score']:.1f} ({moon_status})")
    
    # Week comparison
    print(f"\nWeek Comparison:")
    print(f"{'Week':<6} {'Date':<12} {'Score':<8} {'Observable':<10} {'Config':<7} {'Exp-Lim':<8} {'Moon%':<6} {'M-Free':<7} {'Mosaics':<8}")
    print("-" * 88)
    
    for week in weeks:
        data = weekly_results[week]
        marker = "★ " if week == best_week else "  "
        print(f"{marker}{week:<4} {data['week_date'].strftime('%m-%d'):<12} "
              f"{data['score']:<8.1f} {data['observable_objects']:<10} "
              f"{data['sufficient_time_objects']:<7} {data['exposure_limited_objects']:<8} "
              f"{data['moon_illumination']*100:<6.1f} "
              f"{len(data['moon_free_objects']):<7} {len(data['mosaic_groups']):<8}")
    
    # Statistics summary
    avg_score = np.mean([weekly_results[w]['score'] for w in weeks])
    avg_observable = np.mean([weekly_results[w]['observable_objects'] for w in weeks])
    avg_config_compliant = np.mean([weekly_results[w]['sufficient_time_objects'] for w in weeks])
    avg_exposure_limited = np.mean([weekly_results[w]['exposure_limited_objects'] for w in weeks])
    
    print(f"\nStatistics Summary:")
    print(f"  Average week score: {avg_score:.1f}")
    print(f"  Average observable objects: {avg_observable:.1f}")
    print(f"  Average config-compliant objects: {avg_config_compliant:.1f}")
    print(f"  Average exposure-limited objects: {avg_exposure_limited:.1f}")

def get_best_month_for_object(best_weeks_list):
    """Determine the best month for an object based on its best weeks"""
    if not best_weeks_list:
        return "None"
    
    # Count weeks per month
    month_counts = {}
    for week_num, score in best_weeks_list:
        # Map week to month
        for month, (start_week, end_week) in MONTH_TO_WEEKS.items():
            if start_week <= week_num <= end_week:
                month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month_name = month_names[month]
                month_counts[month_name] = month_counts.get(month_name, 0) + 1
                break
    
    if not month_counts:
        return "None"
    
    # Return month with most weeks, or first month if tied
    max_count = max(month_counts.values())
    best_months = [month for month, count in month_counts.items() if count == max_count]
    return min(best_months)  # Return earliest month if tied

def print_yearly_object_analysis(object_analysis, period_desc="analysis period"):
    """Print analysis of best times for each object throughout the specified period"""
    print("\n" + "="*100)
    print(f"OBJECT OPTIMIZATION ANALYSIS - {period_desc.upper()}")
    print("="*100)
    
    # Prepare object data with best month information
    all_objects_data = []
    for obj_name, data in object_analysis.items():
        if data['best_weeks'] and len(data['moon_free_weeks']) > 0:
            best_score = data['best_weeks'][0][1] if data['best_weeks'] else 0
            first_best_week = data['best_weeks'][0][0] if data['best_weeks'] else 999
            best_month = get_best_month_for_object(data['best_weeks'])
            moon_free_count = len(data['moon_free_weeks'])
            config_count = len(data['config_compliant_weeks'])
            
            all_objects_data.append({
                'name': obj_name,
                'best_score': best_score,
                'first_best_week': first_best_week,
                'best_month': best_month,
                'moon_free_count': moon_free_count,
                'config_count': config_count,
                'best_weeks': data['best_weeks'],
                'data': data
            })
    
    # Sort by first best week
    all_objects_data.sort(key=lambda x: x['first_best_week'])
    
    # Filter for different categories
    top_objects = [obj for obj in all_objects_data if obj['moon_free_count'] >= 4]
    limited_objects = [obj for obj in all_objects_data if obj['moon_free_count'] < 4]
    
    # Top Objects (≥4 opportunities)
    if top_objects:
        print(f"\nTop Objects with Excellent Opportunities (≥4 moon-free weeks):")
        print(f"{'Object':<30} {'Best Score':<11} {'Moon-Free':<10} {'Config-OK':<10} {'Best Month':<11} {'Best Weeks'}")
        print("-" * 105)
        
        for obj in top_objects:  # Show all top objects, no arbitrary limit
            # Sort best weeks by week number for display
            sorted_weeks = sorted([week for week, _ in obj['best_weeks'][:5]])
            best_weeks_str = ", ".join([str(week) for week in sorted_weeks])
            print(f"{obj['name']:<30} {obj['best_score']:<11.1f} {obj['moon_free_count']:<10} "
                  f"{obj['config_count']:<10} {obj['best_month']:<11} {best_weeks_str}")
    
    # Limited Opportunities (<4 weeks)
    if limited_objects:
        print(f"\nObjects with Limited Opportunities (<4 moon-free weeks):")
        print(f"{'Object':<30} {'Moon-Free':<10} {'Config-OK':<10} {'Best Month':<11} {'Best Weeks'}")
        print("-" * 85)
        
        for obj in limited_objects:  # Show all limited objects, no arbitrary limit
            # Sort best weeks by week number for display
            sorted_weeks = sorted([week for week, _ in obj['best_weeks'][:5]])
            best_weeks_str = ", ".join([str(week) for week in sorted_weeks])
            print(f"{obj['name']:<30} {obj['moon_free_count']:<10} {obj['config_count']:<10} "
                  f"{obj['best_month']:<11} {best_weeks_str}")
    
    # All Objects Summary
    print(f"\nAll Objects Summary (ordered by first best week):")
    print(f"{'Object':<30} {'1st Week':<9} {'Best Score':<11} {'Moon-Free':<10} {'Best Month':<11} {'Best Weeks'}")
    print("-" * 105)
    
    for obj in all_objects_data:  # Show all objects, no arbitrary limit
        # Sort best weeks by week number for display
        sorted_weeks = sorted([week for week, _ in obj['best_weeks'][:4]])
        best_weeks_str = ", ".join([str(week) for week in sorted_weeks])
        print(f"{obj['name']:<30} {obj['first_best_week']:<9} {obj['best_score']:<11.1f} "
              f"{obj['moon_free_count']:<10} {obj['best_month']:<11} {best_weeks_str}")
    
    # Mosaic Analysis
    print(f"\nMosaic Groups Analysis:")
    print("(Objects that require individual mosaics or appear frequently in group mosaics)")
    
    # Identify objects that commonly appear in mosaics
    mosaic_candidates = []
    for obj in all_objects_data:
        obj_name = obj['name']
        
        # Check if object requires individual mosaic based on common large objects
        large_objects = ['M31', 'M42', 'M45', 'NGC 7000', 'IC 1396', 'NGC 6960', 'M27', 'IC 4592', 'SH2-106']
        is_large = any(large_name in obj_name for large_name in large_objects)
        
        # Include if it's a large object or has good opportunities
        if is_large or obj['moon_free_count'] >= 3:
            mosaic_type = "Individual" if is_large else "Group"
            mosaic_candidates.append({
                'name': obj_name,
                'type': mosaic_type,
                'first_best_week': obj['first_best_week'],
                'best_month': obj['best_month'],
                'moon_free_count': obj['moon_free_count'],
                'best_weeks': obj['best_weeks']
            })
    
    # Sort mosaic candidates by first best week
    mosaic_candidates.sort(key=lambda x: x['first_best_week'])
    
    if mosaic_candidates:
        print(f"{'Object':<30} {'Type':<10} {'1st Week':<9} {'Moon-Free':<10} {'Best Month':<11} {'Best Weeks'}")
        print("-" * 105)
        
        for mosaic in mosaic_candidates:  # Show all mosaic candidates, no arbitrary limit
            # Sort best weeks by week number for display
            sorted_weeks = sorted([week for week, _ in mosaic['best_weeks'][:4]])
            best_weeks_str = ", ".join([str(week) for week in sorted_weeks])
            print(f"{mosaic['name']:<30} {mosaic['type']:<10} {mosaic['first_best_week']:<9} "
                  f"{mosaic['moon_free_count']:<10} {mosaic['best_month']:<11} {best_weeks_str}")
    
    # Monthly statistics
    print(f"\nMonthly Best Opportunities Summary:")
    month_stats = {}
    for obj in all_objects_data:
        month = obj['best_month']
        if month != "None":
            month_stats[month] = month_stats.get(month, 0) + 1
    
    if month_stats:
        sorted_months = sorted(month_stats.items(), key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x[0]))
        print(f"{'Month':<8} {'Objects with Best Opportunities'}")
        print("-" * 40)
        for month, count in sorted_months:
            print(f"{month:<8} {count}")

def calculate_required_exposure_time(magnitude, bortle_index, base_exposure_hours=1.0):
    """
    Calculate required total exposure time based on object magnitude and sky conditions.
    
    Parameters:
    - magnitude: Object magnitude (brighter = lower number)
    - bortle_index: Sky darkness (1=darkest, 9=brightest)
    - base_exposure_hours: Base exposure for magnitude 10 in Bortle 4 sky
    
    Returns:
    - Required exposure time in hours
    """
    if magnitude is None:
        return base_exposure_hours
    
    # Magnitude factor: Each magnitude step requires ~2.5x more exposure
    # Mag 5 object needs much less time than mag 15 object
    magnitude_factor = 2.5 ** (magnitude - 10)
    
    # Bortle factor: Light pollution requires longer exposures
    # Bortle 1 (darkest): factor 0.5
    # Bortle 4 (moderate): factor 1.0  
    # Bortle 9 (city): factor 4.0
    bortle_factor = (bortle_index / 4.0) ** 1.5
    
    required_hours = base_exposure_hours * magnitude_factor * bortle_factor
    
    # Practical limits: minimum 0.5h, maximum 20h
    return max(0.5, min(20.0, required_hours))

def calculate_object_panels_required(obj_fov_str, telescope_fov_width=2.4, telescope_fov_height=1.8):
    """
    Calculate how many panels are needed to capture an object based on its size.
    
    Parameters:
    - obj_fov_str: Object FOV string (e.g. "3.0°x3.0°", "45'x45'")
    - telescope_fov_width: Telescope FOV width in degrees
    - telescope_fov_height: Telescope FOV height in degrees
    
    Returns:
    - Dictionary with panels_needed, can_single_frame, requires_mosaic
    """
    if not obj_fov_str:
        return {'panels_needed': 1, 'can_single_frame': True, 'requires_mosaic': False, 'obj_width': 0, 'obj_height': 0}
    
    try:
        # Parse FOV string (handle both degrees and arcminutes)
        fov_str = obj_fov_str.replace('°', '').replace("'", '').replace('x', 'x')
        if 'x' in fov_str:
            width_str, height_str = fov_str.split('x')
        else:
            width_str = height_str = fov_str
        
        # Convert to degrees
        obj_width = float(width_str)
        obj_height = float(height_str)
        
        # If values are large (>10), assume they're in arcminutes
        if obj_width > 10:
            obj_width /= 60.0
        if obj_height > 10:
            obj_height /= 60.0
        
        # Calculate panels needed in each dimension
        panels_x = max(1, math.ceil(obj_width / telescope_fov_width))
        panels_y = max(1, math.ceil(obj_height / telescope_fov_height))
        total_panels = panels_x * panels_y
        
        # Determine capture strategy
        can_single_frame = (obj_width <= telescope_fov_width * 1.1 and 
                           obj_height <= telescope_fov_height * 1.1)  # 10% margin
        requires_mosaic = total_panels > 1
        
        return {
            'panels_needed': total_panels,
            'can_single_frame': can_single_frame,
            'requires_mosaic': requires_mosaic,
            'obj_width': obj_width,
            'obj_height': obj_height,
            'panels_x': panels_x,
            'panels_y': panels_y
        }
        
    except (ValueError, AttributeError):
        # Default fallback for unparseable FOV
        return {'panels_needed': 1, 'can_single_frame': True, 'requires_mosaic': False, 'obj_width': 0, 'obj_height': 0}

def get_object_imaging_requirements(obj, bortle_index):
    """
    Get complete imaging requirements for an object.
    
    Returns:
    - Dictionary with exposure_time, panels_info, imaging_feasibility
    """
    # Calculate required exposure time
    exposure_time = calculate_required_exposure_time(
        getattr(obj, 'magnitude', None), bortle_index
    )
    
    # Calculate panel requirements  
    panels_info = calculate_object_panels_required(
        getattr(obj, 'fov', None)
    )
    
    # Determine imaging category
    if panels_info['requires_mosaic']:
        imaging_category = "mosaic_required"
        difficulty = "high" if panels_info['panels_needed'] > 4 else "medium"
    elif exposure_time > 8:
        imaging_category = "long_exposure"
        difficulty = "high"
    elif exposure_time > 3:
        imaging_category = "standard"
        difficulty = "medium"
    else:
        imaging_category = "easy"
        difficulty = "low"
    
    return {
        'exposure_time_hours': exposure_time,
        'panels_info': panels_info,
        'imaging_category': imaging_category,
        'difficulty': difficulty,
        'magnitude': getattr(obj, 'magnitude', None),
        'fov': getattr(obj, 'fov', None)
    }

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Trajectory Analysis and Weekly Astrophotography Planning')
    
    period_group = parser.add_mutually_exclusive_group(required=False)
    period_group.add_argument('--half', choices=['H1', 'H2'], 
                            help='Analyze first (H1) or second (H2) half of year')
    period_group.add_argument('--quarter', choices=['Q1', 'Q2', 'Q3', 'Q4'],
                            help='Analyze specific quarter')
    period_group.add_argument('--month', type=int, choices=range(1, 13),
                            help='Analyze specific month (1-12)')
    period_group.add_argument('--year', action='store_true', default=True,
                            help='Analyze entire year (default)')
    
    parser.add_argument('--no-plots', action='store_true',
                      help='Skip generating plots')
    parser.add_argument('--high-precision', action='store_true',
                      help='Enable high precision astronomical calculations')
    parser.add_argument('--precision-info', action='store_true',
                      help='Display precision capabilities and exit')
    
    return parser.parse_args()

def display_precision_info():
    """Display information about precision capabilities"""
    print("=" * 60)
    print("ASTRONOMICAL PRECISION CAPABILITIES")
    print("=" * 60)
    
    if HIGH_PRECISION_AVAILABLE:
        print("✓ High precision calculations: AVAILABLE")
        print(f"✓ Phase 3 advanced features: {'AVAILABLE' if get_phase3_status() else 'NOT AVAILABLE'}")
        print()
        
        features = list_available_features()
        for phase, feature_list in features.items():
            print(f"{phase}:")
            for feature in feature_list:
                print(f"  • {feature}")
            print()
        
        print("High precision improvements:")
        print("  • Moon position accuracy: ~5-10x better")
        print("  • Sun position accuracy: ~60x better") 
        print("  • Twilight calculations: Enhanced precision")
        print("  • Atmospheric refraction: Advanced modeling")
        
    else:
        print("✗ High precision calculations: NOT AVAILABLE")
        print("  Using standard precision astronomical calculations")
        print("  To enable high precision:")
        print("    1. Ensure astronomy/precision module is properly installed")
        print("    2. Check for missing dependencies")
        print("    3. Verify module imports")
    
    print("=" * 60)

def main():
    """Main analysis function"""
    args = parse_arguments()
    
    # Handle precision info request
    if args.precision_info:
        display_precision_info()
        return
    
    # Configure precision mode if requested
    if args.high_precision and HIGH_PRECISION_AVAILABLE:
        try:
            set_precision_mode('high')
            print("✓ High precision mode enabled")
        except Exception as e:
            print(f"Warning: Could not enable high precision mode: {e}")
    elif args.high_precision and not HIGH_PRECISION_AVAILABLE:
        print("Warning: High precision requested but not available")
    
    # Use current year
    current_year = datetime.now().year
    
    # Determine analysis period
    if args.half:
        period_type, period_value = 'half', args.half
    elif args.quarter:
        period_type, period_value = 'quarter', args.quarter
    elif args.month:
        period_type, period_value = 'month', args.month
    else:
        period_type, period_value = 'year', None
    
    period_desc = get_period_description(period_type, period_value)
    
    print("=" * 80)
    print("MULTI-NIGHT ASTROPHOTOGRAPHY PLANNER")
    print("Optimal Celestial Object Photography Timing Analysis")
    print("=" * 80)
    print(f"Analysis period: {period_desc} {current_year}")
    print(f"Using visibility window: Alt {MIN_ALT}°-{MAX_ALT}°, Az {MIN_AZ}°-{MAX_AZ}°")
    print(f"Minimum visibility requirement: {MIN_VISIBILITY_HOURS} hours")
    
    if HIGH_PRECISION_AVAILABLE:
        precision_mode = get_precision_mode() if HIGH_PRECISION_AVAILABLE else 'standard'
        print(f"Precision mode: {precision_mode.upper()}")
    else:
        print("Precision mode: STANDARD (high precision not available)")
    print("=" * 80)
    
    # Run weekly analysis
    weekly_results, weeks_analyzed = analyze_weekly_astrophotography(period_type, period_value, current_year)
    
    # Run object analysis for the specified period
    object_analysis = analyze_yearly_object_conditions(weeks_analyzed, current_year)
    
    # Create analysis plots
    if not args.no_plots:
        print("\nCreating analysis plots...")
        weekly_fig = plot_weekly_analysis(weekly_results, period_desc)
    
    # Print summaries
    print_weekly_summary(weekly_results, period_desc)
    print_yearly_object_analysis(object_analysis, period_desc)
    
    # Show plots
    if not args.no_plots:
        plt.show()
    
    return weekly_results, object_analysis

if __name__ == "__main__":
    main() 
