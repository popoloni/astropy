import math
import numpy as np
from datetime import datetime, timedelta, timezone
import os

import pytz
import re
import json

import csv

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

from enum import Enum
import argparse

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import time simulation module
from models import SchedulingStrategy, CelestialObject, Observer, MosaicGroup
from config.settings import load_config, get_default_location, _import_mosaic_functions
from catalogs import (
    get_messier_catalog, get_additional_dso, get_combined_catalog,
    normalize_object_name, are_same_object, enrich_object_name,
    get_object_by_name, get_objects_by_type, sort_objects_by_size,
    sort_objects_by_altitude, get_object_type, merge_catalogs,
    get_objects_from_csv
)
from astronomy import (
    get_local_timezone, local_to_utc, utc_to_local, calculate_julian_date,
    format_time, dms_dd, dd_dh, dh_dd, hms_dh, dh_hour, dh_min, dh_sec,
    parse_ra, parse_dec, parse_fov, calculate_total_area,
    calculate_lst, calculate_sun_position, calculate_altaz,
    calculate_moon_phase, calculate_moon_position,
    calculate_moon_interference_radius, is_near_moon, get_moon_phase_icon,
    is_visible, find_visibility_window, calculate_visibility_duration,
    find_sunset_sunrise, find_astronomical_twilight,
    calculate_required_panels, calculate_required_exposure, is_object_imageable,
    filter_visible_objects
)
from analysis import (
    calculate_object_score, calculate_max_altitude, find_best_objects,
    filter_objects_by_criteria, generate_observation_schedule, 
    combine_objects_and_groups, create_mosaic_groups, analyze_mosaic_compatibility,
    print_schedule_strategy_report, generate_schedule_section_content,
    print_combined_report, print_objects_by_type, ReportGenerator
)
from utilities.time_sim import get_current_datetime, get_simulated_datetime
from utilities import time_sim

# Configuration loading
CONFIG = load_config()
DEFAULT_LOCATION = get_default_location(CONFIG)

# Import constants from config
if CONFIG:
    # Import all constants from config
    from config.settings import *
    LATITUDE = DEFAULT_LOCATION['latitude']
    LONGITUDE = DEFAULT_LOCATION['longitude']
    OBSERVER = Observer(LATITUDE, LONGITUDE)
    
    # Import mosaic functions if enabled
    if MOSAIC_ENABLED:
        _import_mosaic_functions()
else:
    raise RuntimeError("Could not load configuration file")

# ============= OBJECT FILTERING FUNCTIONS =============
# Object filtering functions have been moved to analysis.filtering module

# ============= REPORTING =============

def plot_moon_trajectory(ax, start_time, end_time):
    """Plot moon trajectory and add it to the legend"""
    times = []
    alts = []
    azs = []
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_moon_position(current_time)
        if is_visible(alt, az):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if azs:
        # Plot moon trajectory
        ax.plot(azs, alts, '-', color=MOON_TRAJECTORY_COLOR, 
               linewidth=MOON_LINE_WIDTH, label='Moon', zorder=2)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=MOON_MARKER_COLOR, 
                   markersize=MOON_MARKER_SIZE, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=MOON_MARKER_COLOR,
                       zorder=3)
                       
def setup_altaz_plot():
    """Setup basic altitude-azimuth plot"""
    # Create figure with appropriate size
    fig = plt.figure(figsize=FIGURE_SIZE)  # Wider figure
    
    # Use GridSpec for better control over spacing
    gs = fig.add_gridspec(1, 1)
    # Adjust margins to accommodate axis labels and legend
    gs.update(left=0.1, right=0.85, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])
    
    # Set axis limits and labels
    ax.set_xlim(MIN_AZ-10, MAX_AZ+10)
    ax.set_ylim(MIN_ALT-10, MAX_ALT+10)
    ax.set_xlabel('Azimuth (degrees)')
    ax.set_ylabel('Altitude (degrees)')
    ax.grid(True, alpha=GRID_ALPHA)
    
    # Add visible region rectangle
    visible_region = Rectangle((MIN_AZ, MIN_ALT), 
                             MAX_AZ - MIN_AZ, 
                             MAX_ALT - MIN_ALT,
                             facecolor='green', 
                             alpha=VISIBLE_REGION_ALPHA,
                             label='Visible Region')
    ax.add_patch(visible_region)
    
    # Configure grid with major and minor ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    
    return fig, ax

def finalize_plot_legend(ax):
    """Finalize plot legend with sorted entries, keeping Visible Region and Moon first"""
    # Get current handles and labels
    handles, labels = ax.get_legend_handles_labels()
    
    # Find indices of special entries
    try:
        visible_idx = labels.index('Visible Region')
        visible_handle = handles.pop(visible_idx)
        visible_label = labels.pop(visible_idx)
    except ValueError:
        visible_handle, visible_label = None, None
        
    try:
        moon_idx = labels.index('Moon')
        moon_handle = handles.pop(moon_idx)
        moon_label = labels.pop(moon_idx)
    except ValueError:
        moon_handle, moon_label = None, None
    
    # Sort remaining entries
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: x[1].lower())
    handles, labels = zip(*sorted_pairs) if sorted_pairs else ([], [])
    
    # Reconstruct list with special entries first
    final_handles = []
    final_labels = []
    
    if visible_handle is not None:
        final_handles.append(visible_handle)
        final_labels.append(visible_label)
    if moon_handle is not None:
        final_handles.append(moon_handle)
        final_labels.append(moon_label)
        
    final_handles.extend(handles)
    final_labels.extend(labels)
    
    # Update legend
    ax.legend(final_handles, final_labels,
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Objects and Conditions')

def get_abbreviated_name(full_name):
    """Get abbreviated name (catalog designation) from full name"""
    # First try to find Messier number
    m_match = re.match(r'M(\d+)', full_name)
    if m_match:
        return f"M{m_match.group(1)}"
    
    # Then try NGC number
    ngc_match = re.match(r'NGC\s*(\d+)', full_name)
    if ngc_match:
        return f"NGC{ngc_match.group(1)}"
    
    # Then try IC number
    ic_match = re.match(r'IC\s*(\d+)', full_name)
    if ic_match:
        return f"IC{ic_match.group(1)}"
    
    # Then try SH2 number
    sh2_match = re.match(r'SH2-(\d+)', full_name)
    if sh2_match:
        return f"SH2-{sh2_match.group(1)}"  # Return complete SH2-nnn format
    
    # Then try SH number
    sh_match = re.match(r'SH\s*(\d+)', full_name)
    if sh_match:
        return f"SH{sh_match.group(1)}"  # Return complete SH-nnn format
        
    # Then try Barnard number
    b_match = re.match(r'B\s*(\d+)', full_name)
    if b_match:
        return f"B{b_match.group(1)}"
    
    # Then try Gum number
    gum_match = re.match(r'Gum\s*(\d+)', full_name)
    if gum_match:
        return f"GUM{gum_match.group(1)}"    

    # If no catalog number found, return first word
    return full_name.split()[0]

def find_optimal_label_position(azimuths, altitudes, hour_positions, existing_positions, 
                               existing_labels, margin=8):
    """
    Find optimal position for label that avoids overlapping with:
    - Other object labels
    - Hourly tick markers and their labels
    - Trajectory endpoints
    
    Parameters:
    - azimuths, altitudes: trajectory coordinates
    - hour_positions: list of (az, alt) tuples for hourly markers
    - existing_positions: list of (az, alt) tuples for other object labels
    - existing_labels: list of existing label texts to avoid duplication
    - margin: minimum distance in degrees for avoiding overlaps
    
    Returns:
    - (az, alt) tuple for label position, with fallback if no optimal position found
    """
    if len(azimuths) < 3:
        return None
    
    # Create list of forbidden zones (hourly ticks + existing labels)
    forbidden_zones = []
    
    # Add hourly tick positions with larger margin
    for pos in hour_positions:
        forbidden_zones.append((pos[0], pos[1], margin * 1.5))  # Larger margin for ticks
    
    # Add existing label positions
    for pos in existing_positions:
        forbidden_zones.append((pos[0], pos[1], margin))
    
    # Find potential label positions along trajectory
    # Avoid first and last 20% of trajectory (near endpoints)
    start_idx = max(1, len(azimuths) // 5)
    end_idx = min(len(azimuths) - 1, len(azimuths) * 4 // 5)
    
    candidate_positions = []
    
    for i in range(start_idx, end_idx):
        az, alt = azimuths[i], altitudes[i]
        
        # Check if this position conflicts with forbidden zones
        conflicts = False
        for fz_az, fz_alt, fz_margin in forbidden_zones:
            distance = ((az - fz_az)**2 + (alt - fz_alt)**2)**0.5
            if distance < fz_margin:
                conflicts = True
                break
        
        if not conflicts:
            # Calculate trajectory curvature at this point for better placement
            curvature_score = 0
            if i > 0 and i < len(azimuths) - 1:
                # Simple curvature estimation
                prev_az, prev_alt = azimuths[i-1], altitudes[i-1]
                next_az, next_alt = azimuths[i+1], altitudes[i+1]
                
                # Prefer straighter segments for labels
                angle1 = np.arctan2(alt - prev_alt, az - prev_az)
                angle2 = np.arctan2(next_alt - alt, next_az - az)
                angle_diff = abs(angle1 - angle2)
                curvature_score = 1 / (1 + angle_diff)  # Higher score for straighter segments
            
            # Distance from center of trajectory (prefer middle)
            center_preference = 1 - abs(i - len(azimuths) // 2) / (len(azimuths) // 2)
            
            # Combined score
            total_score = curvature_score * 0.7 + center_preference * 0.3
            
            candidate_positions.append((az, alt, total_score, i))
    
    if candidate_positions:
        # Sort by score and return best position
        candidate_positions.sort(key=lambda x: x[2], reverse=True)
        best_az, best_alt, _, _ = candidate_positions[0]
        return (best_az, best_alt)
    
    # FALLBACK: If no optimal position found, use middle of trajectory with reduced margin check
    fallback_candidates = []
    reduced_margin = margin * 0.5  # Use smaller margin for fallback
    
    for i in range(start_idx, end_idx):
        az, alt = azimuths[i], altitudes[i]
        
        # Check conflicts with reduced margin
        conflicts = False
        for fz_az, fz_alt, fz_margin in forbidden_zones:
            distance = ((az - fz_az)**2 + (alt - fz_alt)**2)**0.5
            if distance < reduced_margin:  # Use reduced margin
                conflicts = True
                break
        
        if not conflicts:
            # Distance from center of trajectory (prefer middle)
            center_preference = 1 - abs(i - len(azimuths) // 2) / (len(azimuths) // 2)
            fallback_candidates.append((az, alt, center_preference, i))
    
    if fallback_candidates:
        # Sort by center preference and return best fallback position
        fallback_candidates.sort(key=lambda x: x[2], reverse=True)
        best_az, best_alt, _, _ = fallback_candidates[0]
        return (best_az, best_alt)
    
    # FINAL FALLBACK: Just use trajectory middle point if all else fails
    mid_idx = len(azimuths) // 2
    return (azimuths[mid_idx], altitudes[mid_idx])

def calculate_label_offset(trajectory_az, trajectory_alt, trajectory_idx, azimuths, altitudes):
    """
    Calculate smart offset for label based on trajectory direction and position
    to avoid overlapping with the trajectory line itself.
    """
    # Default offset
    offset_x, offset_y = 8, 8
    
    if trajectory_idx > 0 and trajectory_idx < len(azimuths) - 1:
        # Calculate trajectory direction
        prev_az, prev_alt = azimuths[trajectory_idx - 1], altitudes[trajectory_idx - 1]
        next_az, next_alt = azimuths[trajectory_idx + 1], altitudes[trajectory_idx + 1]
        
        # Direction vector
        dir_az = next_az - prev_az
        dir_alt = next_alt - prev_alt
        
        # Perpendicular offset (rotated 90 degrees)
        if abs(dir_az) > abs(dir_alt):
            # More horizontal trajectory - offset vertically
            offset_x = 8 if dir_az > 0 else -8
            offset_y = 12 if dir_alt >= 0 else -12
        else:
            # More vertical trajectory - offset horizontally
            offset_x = 12 if dir_az >= 0 else -12
            offset_y = 8 if dir_alt > 0 else -8
    
    return offset_x, offset_y

def plot_object_trajectory(ax, obj, start_time, end_time, color, existing_positions=None, schedule=None):
    """Plot trajectory with moon proximity checking and legend.
    Elements are plotted in specific z-order:
    1. Base trajectory (z=1)
    2. Moon interference segments (z=2)
    3. Hour markers (z=3)
    4. Hour labels (z=4)
    5. Object name (z=5)
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    obj : CelestialObject
        Object to plot trajectory for
    start_time : datetime
        Start time for trajectory
    end_time : datetime
        End time for trajectory
    color : str
        Color for trajectory and markers
    existing_positions : list, optional
        List of existing label positions to avoid overlap
    schedule : list, optional
        List of scheduled observations [(start, end, obj), ...] for label styling
    """
    # Ensure there's a legend (even if empty) to avoid NoneType errors
    if ax.get_legend() is None:
        ax.legend()
    times = []
    alts = []
    azs = []
    near_moon = []  # Track moon proximity
    moon_alts = []  # Track moon altitude for each point
    obj.near_moon = False  # Initialize moon proximity flag
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Check if this object is scheduled
    is_scheduled = False
    if schedule:
        scheduled_objects = [sched_obj for _, _, sched_obj in schedule]
        is_scheduled = obj in scheduled_objects
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    # Use smaller interval for smoother trajectory
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        moon_alt, moon_az = calculate_moon_position(current_time)
        
        # Extended visibility check for trajectory plotting (±5 degrees)
        if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
            MIN_AZ - 5 <= az <= MAX_AZ + 5):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Check moon proximity - only consider when moon is risen
            is_near = False
            if moon_alt >= 0:  # Only check interference if moon is above horizon
                is_near = is_near_moon(alt, az, moon_alt, moon_az, obj.magnitude, current_time)
            near_moon.append(is_near)
            moon_alts.append(moon_alt)  # Store moon altitude for each point
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)  # Use 1-minute intervals for accuracy
    
    # Set moon influence flag only if object is affected for a significant period
    if near_moon:
        moon_influence_periods = []
        start_idx = None
        
        # Find continuous periods of moon influence
        for i, is_near in enumerate(near_moon):
            if is_near and start_idx is None:
                start_idx = i
            elif not is_near and start_idx is not None:
                moon_influence_periods.append((start_idx, i))
                start_idx = None
        
        # Don't forget the last period if it ends with moon influence
        if start_idx is not None:
            moon_influence_periods.append((start_idx, len(near_moon)))
        
        # Calculate total influence time
        total_influence_minutes = sum(end - start for start, end in moon_influence_periods)
        
        # Set flag if moon influence is significant (more than 15 minutes)
        obj.near_moon = total_influence_minutes >= 15
        obj.moon_influence_periods = moon_influence_periods  # Store periods for later use
    
    if azs:
        # Determine line style based on sufficient time
        line_style = '-' if getattr(obj, 'sufficient_time', True) else '--'
        
        # Plot base trajectory (lowest z-order)
        ax.plot(azs, alts, line_style, color=color, linewidth=1.5, alpha=0.3, zorder=1)
        
        # Plot moon-affected segments if any
        if hasattr(obj, 'moon_influence_periods'):
            for start_idx, end_idx in obj.moon_influence_periods:
                # Validate that moon is actually above horizon during this segment
                valid_segment = True
                for i in range(start_idx, min(end_idx+1, len(moon_alts))):
                    if moon_alts[i] < 0:  # Moon below horizon
                        valid_segment = False
                        break
                
                if valid_segment:
                    # Plot the moon-affected segment
                    ax.plot(azs[start_idx:end_idx+1], 
                           alts[start_idx:end_idx+1], 
                           line_style,
                           color=MOON_INTERFERENCE_COLOR,
                           linewidth=2,
                           zorder=2)
        
        # Add label only once
        legend = ax.get_legend()
        obj_name = obj.name.split('/')[0]
        existing_labels = [t.get_text() for t in legend.get_texts()] if legend else []
        
        if obj_name not in existing_labels:
            # Add a dummy line for the legend
            ax.plot([], [], line_style, color=color, 
                   linewidth=2, label=obj_name)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=color, markersize=6, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=color,
                       zorder=3)
        
        # Add abbreviated name near trajectory
        if existing_positions is None:
            existing_positions = []
            
        # Collect hour positions for avoiding overlap
        hour_positions = [(az, alt) for az, alt in zip(hour_azs, hour_alts)]
        
        # Get existing labels from legend to avoid duplicates
        legend = ax.get_legend()
        existing_labels = [t.get_text() for t in legend.get_texts()] if legend else []
            
        label_pos = find_optimal_label_position(azs, alts, hour_positions, existing_positions, existing_labels, margin=6)
        if label_pos:
            abbreviated_name = get_abbreviated_name(obj.name)
            
            # Calculate smart offset based on trajectory direction
            trajectory_idx = len(azs) // 2  # Use middle point for direction calculation
            offset_x, offset_y = calculate_label_offset(label_pos[0], label_pos[1], trajectory_idx, azs, alts)
            
            # Choose label background color based on scheduling status
            if is_scheduled:
                # Yellow transparent background for scheduled objects
                label_bg_color = "yellow"
                label_alpha = 0.6  # Slightly more opaque for better visibility of yellow
            else:
                # White transparent background for non-scheduled objects
                label_bg_color = "white"
                label_alpha = 0.4
            
            ax.annotate(abbreviated_name, 
                       label_pos,
                       xytext=(offset_x, offset_y),
                       textcoords='offset points',
                       color=color,
                       fontweight='bold',
                       fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.2", facecolor=label_bg_color, alpha=label_alpha),
                       zorder=15)
            existing_positions.append(label_pos)

def plot_visibility_chart(objects, start_time, end_time, schedule=None, title="Object Visibility", use_margins=True):
    """Create visibility chart showing moon interference periods and scheduled intervals.
    - Base bars show full visibility with colors indicating status/moon interference.
    - Scheduled intervals are overlaid with hatching.

    Parameters:
    -----------
    objects : list
        List of celestial objects to plot
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    schedule : list, optional
        List of scheduled observations [(start, end, obj), ...]
    title : str, optional
        Chart title
    use_margins : bool, optional
        Whether to use extended margins (±5°) for visibility boundaries
    """

    # Ensure times are in local timezone
    milan_tz = get_local_timezone()
    if start_time.tzinfo != milan_tz:
        start_time = start_time.astimezone(milan_tz)
    if end_time.tzinfo != milan_tz:
        end_time = end_time.astimezone(milan_tz)

    # Get current time in local timezone for the vertical line
    current_time = datetime.now(milan_tz)

    # Create figure with settings - creating a brand new figure each time
    # to avoid any remnant elements from previous plots
    plt.close('all')  # Close any existing figures
    fig = plt.figure(figsize=(15, max(10, len(objects)*0.3 + 4)))
    
    # Full-width subplot - no need to reserve space for legend
    ax = fig.add_subplot(111)
    
    # Get visibility periods and sort objects
    sorted_objects = _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins)

    # Setup plot
    _setup_visibility_chart_axes(ax, title, start_time, end_time, milan_tz)

    # Create mapping for recommended objects and scheduled intervals (in local time)
    recommended_objects = [obj for _, _, obj in schedule] if schedule else []
    scheduled_intervals = {obj: (start.astimezone(milan_tz), end.astimezone(milan_tz))
                           for start, end, obj in schedule} if schedule else {}

    # Plot BASE visibility periods
    for i, obj in enumerate(sorted_objects):
        # Skip returning handles/labels since we don't need them for a legend
        _plot_object_visibility_bars_no_legend(ax, i, obj, start_time, end_time,
                                         recommended_objects, use_margins)

    # OVERLAY the scheduled intervals with hatching
    for i, obj in enumerate(sorted_objects):
        if obj in scheduled_intervals:
            sched_start_local, sched_end_local = scheduled_intervals[obj]
            
            # Get the object's actual visibility periods
            periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
            if not periods:
                continue  # Skip if no visibility periods
                
            # Find the actual period that contains this scheduled time
            containing_period = None
            for p_start, p_end in periods:
                local_p_start = p_start.astimezone(milan_tz)
                local_p_end = p_end.astimezone(milan_tz)
                
                # Check if this period contains the scheduled interval
                if (local_p_start <= sched_end_local and 
                    local_p_end >= sched_start_local):
                    # Found a containing period
                    containing_period = (local_p_start, local_p_end)
                    break
                    
            if not containing_period:
                print(f"Warning: No visibility period found containing scheduled interval for {obj.name}")
                continue
                
            # Ensure the scheduled interval is within the plot's time range and valid
            # AND within the containing visibility period
            plot_start = max(sched_start_local, start_time, containing_period[0])
            plot_end = min(sched_end_local, end_time, containing_period[1])
            
            if plot_start < plot_end:  # Only plot if there's a non-zero duration within bounds
                ax.barh(i, plot_end - plot_start, 
                        left=plot_start, 
                        height=0.35,  # Slightly taller than visibility bars
                        color='none',  # Make base transparent
                        edgecolor='red',  # Changed from black to RED as requested
                        hatch='///',  # Hashing pattern
                        linewidth=1.0,  # Slightly thicker for better visibility
                        alpha=0.9,  # Higher alpha for better contrast
                        zorder=9)  # Set to 9 so it's BELOW the labels but still above the bars

    # Add vertical line for current time if it's within the plot range
    if start_time <= current_time <= end_time:
        ax.plot([current_time, current_time], [-0.5, len(sorted_objects)-0.5],
                color='red', linestyle='-', linewidth=2)

    # Customize plot axes
    ax.set_yticks(range(len(sorted_objects)))
    # Use custom display names that handle mosaic groups specially
    display_names = []
    for obj in sorted_objects:
        if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
            # For mosaic groups, show abbreviated names of individual objects
            abbreviated_names = [get_abbreviated_name(individual_obj.name) for individual_obj in obj.objects]
            if len(abbreviated_names) <= 3:
                display_names.append(', '.join(abbreviated_names))
            else:
                display_names.append(f"{', '.join(abbreviated_names[:2])} +{len(abbreviated_names)-2}")
        else:
            # For individual objects, use the standard abbreviated name
            display_names.append(get_abbreviated_name(obj.name))
    
    ax.set_yticklabels(display_names)
    ax.grid(True, axis='x', alpha=GRID_ALPHA)
    
    # Add a simple legend for moon interference, scheduled observations, and insufficient time
    legend_handles = []
    
    # Moon interference legend entry
    moon_handle = Patch(facecolor=MOON_INTERFERENCE_COLOR, alpha=0.8, 
                        label='Moon Interference')
    legend_handles.append(moon_handle)
    
    # Scheduled observations legend entry
    if schedule:
        sched_handle = Patch(facecolor='none', edgecolor='red', hatch='///', 
                             alpha=0.9, label='Scheduled Observation')
        legend_handles.append(sched_handle)
    
    # Insufficient time legend entry (optional)
    if any(not getattr(obj, 'sufficient_time', True) for obj in sorted_objects):
        insuf_handle = Patch(facecolor='pink', alpha=0.4, label='Insufficient Time')
        legend_handles.append(insuf_handle)
    
    # Add the legend
    if legend_handles:
        ax.legend(handles=legend_handles, loc='lower left')
    
    # Use full figure width
    fig.tight_layout()
    
    return fig, ax

def _plot_object_visibility_bars_no_legend(ax, index, obj, start_time, end_time, recommended_objects, use_margins):
    """Plot visibility bars for a single object (BASE LAYER) without returning legend handles."""
    milan_tz = get_local_timezone()
    periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)

    is_recommended = obj in recommended_objects
    has_sufficient_time = getattr(obj, 'sufficient_time', True)
    
    # Always use the regular color as the base color regardless of moon interference
    if not has_sufficient_time:
        color = 'darkmagenta' if is_recommended else 'pink'
    else:
        color = 'green' if is_recommended else 'gray'
    alpha = 0.8 if is_recommended else 0.4
    
    base_zorder = 5

    # Ensure periods is not None before iterating
    if periods is None:
        periods = []

    for period_start, period_end in periods:
        local_start = period_start.astimezone(milan_tz)
        local_end = period_end.astimezone(milan_tz)

        plot_start = max(local_start, start_time)
        plot_end = min(local_end, end_time)

        if plot_start >= plot_end: continue

        # If object has moon influence periods, draw the base bar in normal color
        # and overlay moon-affected segments separately
        if hasattr(obj, 'moon_influence_periods') and obj.moon_influence_periods:
            # First, draw the entire bar in normal color
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)
                   
            # Then overlay the moon interference segments
            for start_idx, end_idx in obj.moon_influence_periods:
                # Handle both integer indices and datetime objects
                if isinstance(start_idx, datetime) and isinstance(end_idx, datetime):
                    # Direct datetime objects - use them as-is
                    moon_start = start_idx
                    moon_end = end_idx
                elif isinstance(start_idx, int) and isinstance(end_idx, int):
                    # Integer indices - convert to datetime
                    moon_start = period_start + timedelta(minutes=start_idx)
                    moon_end = period_start + timedelta(minutes=end_idx)
                else:
                    # Skip mixed or invalid types
                    continue
                
                # Convert to local timezone
                moon_start_local = moon_start.astimezone(milan_tz)
                moon_end_local = moon_end.astimezone(milan_tz)
                
                # Check if this segment overlaps with the current visibility period
                if moon_end_local > plot_start and moon_start_local < plot_end:
                    # Calculate the overlapping segment
                    segment_start = max(moon_start_local, plot_start)
                    segment_end = min(moon_end_local, plot_end)
                    
                    # Draw the moon interference segment
                    moon_color = '#DAA520' if is_recommended else '#F0E68C'  # Goldenrod/Khaki
                    ax.barh(index, 
                           segment_end - segment_start, 
                           left=segment_start, 
                           height=0.3,
                           alpha=alpha,
                           color=moon_color,
                           zorder=base_zorder+1)  # Slightly higher zorder
        else:
            # Plot normal visibility bar
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)

        # Add abbreviated name text annotation near the bar start (once per object ideally)
        # Position text AT the bar start, aligned left
        # Plot text label only for the first segment
        if period_start == periods[0][0] and plot_start < plot_end:
             # Use custom display name that handles mosaic groups specially
             if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                 # For mosaic groups, show abbreviated names of individual objects
                 abbreviated_names = [get_abbreviated_name(individual_obj.name) for individual_obj in obj.objects]
                 if len(abbreviated_names) <= 3:
                     abbreviated_name = ', '.join(abbreviated_names)
                 else:
                     abbreviated_name = f"{', '.join(abbreviated_names[:2])} +{len(abbreviated_names)-2}"
             else:
                 # For individual objects, use the standard abbreviated name
                 abbreviated_name = get_abbreviated_name(obj.name)
             
             text_pos_x = plot_start # Align with the actual start of the plotted bar segment
             ax.text(text_pos_x + timedelta(minutes=1), index, # Small offset from the exact start
                     f" {abbreviated_name}", # Add space for padding
                     va='center', ha='left', # Align left
                     fontsize=7, # Smaller font size for text on chart
                     color='black', # Ensure visibility
                     zorder=base_zorder+1) # Above the bar

    # *** Ensure the function always returns a tuple ***
    return [], []

def _get_object_visibility_color(near_moon, is_recommended, has_sufficient_time):
    """Determine color and alpha for object visibility bars"""
    if near_moon:
        # Dark yellow for selected objects near moon, pale yellow for others
        if is_recommended:
            color = '#DAA520'  # Goldenrod
            alpha = 0.8
        else:
            color = '#F0E68C'  # Khaki
            alpha = 0.6
    else:
        if not has_sufficient_time:
            color = 'darkmagenta' if is_recommended else 'pink'
        else:
            color = 'green' if is_recommended else 'gray'
        alpha = 0.8 if is_recommended else 0.4
    
    return color, alpha

def _plot_visibility_with_moon_interference(ax, index, obj, period_start, period_end, 
                                         local_start, local_end, color, alpha, is_recommended, base_zorder):
    """Plot visibility bars with moon interference segments"""
    milan_tz = get_local_timezone()
    period_minutes = int((period_end - period_start).total_seconds() / 60)
    
    # Convert moon influence periods to actual times
    moon_times = []
    for start_idx, end_idx in obj.moon_influence_periods:
        # Handle both integer indices and datetime objects
        if isinstance(start_idx, datetime) and isinstance(end_idx, datetime):
            # Direct datetime objects - use them as-is
            moon_start = start_idx
            moon_end = end_idx
        elif isinstance(start_idx, int) and isinstance(end_idx, int):
            # Integer indices - convert to datetime
            moon_start = period_start + timedelta(minutes=start_idx)
            moon_end = period_start + timedelta(minutes=end_idx)
        else:
            # Skip mixed or invalid types
            continue
        
        # Only consider this period if it was properly checked for moon visibility earlier
        # If it's in moon_influence_periods, we trust that it was properly filtered
        if moon_start < period_end and moon_end > period_start:
            moon_times.append((
                max(moon_start, period_start),
                min(moon_end, period_end)
            ))
    
    # Plot non-moon-affected parts in normal color
    last_end = period_start
    for moon_start, moon_end in moon_times:
        if moon_start > last_end:
            # Plot normal visibility segment
            ax.barh(index, 
                   moon_start.astimezone(milan_tz) - last_end.astimezone(milan_tz),
                   left=last_end.astimezone(milan_tz),
                   height=0.3,
                   alpha=alpha,
                   color=color,
                   zorder=base_zorder)
        # Plot moon-affected segment
        ax.barh(index,
               moon_end.astimezone(milan_tz) - moon_start.astimezone(milan_tz),
               left=moon_start.astimezone(milan_tz),
               height=0.3,
               alpha=alpha,
               color='#DAA520' if is_recommended else '#F0E68C',
               zorder=base_zorder)  # Goldenrod/Khaki
        last_end = moon_end
    
    # Plot remaining normal visibility if any
    if last_end < period_end:
        ax.barh(index,
               period_end.astimezone(milan_tz) - last_end.astimezone(milan_tz),
               left=last_end.astimezone(milan_tz),
               height=0.3,
               alpha=alpha,
               color=color,
               zorder=base_zorder)

def _add_moon_interference_legend(ax):
    """Add legend entries for moon interference"""
    # Add dummy patches for legend
    ax.barh([-1], [0], height=0.3, color='#DAA520', alpha=0.8, 
            label='Selected Object (Moon Interference)')
    ax.barh([-1], [0], height=0.3, color='#F0E68C', alpha=0.4,
            label='Non-selected Object (Moon Interference)')

def _add_moon_interference_legend_items(handles, labels):
    """Add moon interference legend items"""
    # Add dummy patches for legend
    moon_line = plt.Line2D([0], [0], color=MOON_INTERFERENCE_COLOR, linestyle='-', label='Moon Interference')
    handles.append(moon_line)
    labels.append('Moon Interference')
    return handles, labels

# ============= SCHEDULE GENERATION =============

def _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins):
    """Get objects sorted by visibility start time for chart display"""
    milan_tz = get_local_timezone()
    object_periods = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            # Convert periods to local time
            local_periods = [(p[0].astimezone(milan_tz), p[1].astimezone(milan_tz)) 
                           for p in periods]
            duration = calculate_visibility_duration(periods)
            object_periods.append((obj, local_periods[0][0], duration))
    
    # Sort by start time
    object_periods.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in object_periods]

def _setup_visibility_chart_axes(ax, title, start_time, end_time, tz):
    """Setup axes for visibility chart"""
    ax.set_title(title)
    ax.set_xlabel('Local Time')
    ax.set_ylabel('Objects')
    ax.set_xlim(start_time, end_time)
    
    # Use local time formatter
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=tz))

# calculate_object_score has been moved to analysis modules
# calculate_max_altitude has been moved to analysis modules
# create_mosaic_groups has been moved to analysis modules
# combine_objects_and_groups has been moved to analysis modules
# generate_observation_schedule has been moved to analysis modules
# print_combined_report has been moved to analysis modules
# print_schedule_strategy_report has been moved to analysis modules
# print_objects_by_type has been moved to analysis modules
def plot_quarterly_trajectories(objects, start_time, end_time, schedule=None):
    """Create 4-quarter trajectory plots to reduce visual clutter"""
    
    # Calculate quarter durations
    total_duration = end_time - start_time
    quarter_duration = total_duration / 4
    
    quarters = {
        'Q1': (start_time, start_time + quarter_duration),
        'Q2': (start_time + quarter_duration, start_time + 2 * quarter_duration),
        'Q3': (start_time + 2 * quarter_duration, start_time + 3 * quarter_duration),
        'Q4': (start_time + 3 * quarter_duration, end_time)
    }
    
    # Count objects visible in each quarter
    quarter_objects = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}
    
    for obj in objects:
        # Check visibility in each quarter
        for quarter_name, (q_start, q_end) in quarters.items():
            # Sample a few time points in the quarter to check visibility
            sample_times = [
                q_start + (q_end - q_start) * i / 4 
                for i in range(5)
            ]
            
            visible_in_quarter = False
            for sample_time in sample_times:
                alt, az = calculate_altaz(obj, sample_time)
                if is_visible(alt, az, use_margins=True):
                    visible_in_quarter = True
                    break
            
            if visible_in_quarter:
                quarter_objects[quarter_name].append(obj)
    
    # Create 2x2 subplot with more space for cleaner look
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2, hspace=0.25, wspace=0.15)
    
    # Use the same date as the original for consistency
    night_date = start_time.date()
    fig.suptitle(f'Object Trajectories by Night Quarter - {night_date}', fontsize=16, fontweight='bold')
    
    quarter_names = ['Q1', 'Q2', 'Q3', 'Q4']
    quarter_titles = [
        'First Quarter (Early Night)',
        'Second Quarter (Mid-Early Night)', 
        'Third Quarter (Mid-Late Night)',
        'Fourth Quarter (Late Night)'
    ]
    
    # Collect all unique objects across quarters for a single legend
    all_quarter_objects = set()
    has_moon_trajectory = False
    
    # Plot each quarter
    for i, (quarter_name, title) in enumerate(zip(quarter_names, quarter_titles)):
        row = i // 2
        col = i % 2
        ax = fig.add_subplot(gs[row, col])
        
        # Setup axis like the original plot
        ax.set_xlim(MIN_AZ-10, MAX_AZ+10)
        ax.set_ylim(MIN_ALT-10, MAX_ALT+10)
        ax.set_xlabel('Azimuth (degrees)')
        ax.set_ylabel('Altitude (degrees)')
        ax.grid(True, alpha=GRID_ALPHA)
        ax.set_title(title, fontweight='bold')
        
        # Add visible region (no label to avoid legend entry)
        visible_region = Rectangle((MIN_AZ, MIN_ALT), 
                                 MAX_AZ - MIN_AZ, 
                                 MAX_ALT - MIN_ALT,
                                 facecolor='green', 
                                 alpha=VISIBLE_REGION_ALPHA)
        ax.add_patch(visible_region)
        
        # Get quarter time range and objects
        q_start, q_end = quarters[quarter_name]
        quarter_visible_objects = quarter_objects[quarter_name]
        
        # Check if moon is visible in this quarter
        moon_visible_in_quarter = False
        check_time = q_start
        while check_time <= q_end and not moon_visible_in_quarter:
            moon_alt, moon_az = calculate_moon_position(check_time)
            if is_visible(moon_alt, moon_az, use_margins=True):
                moon_visible_in_quarter = True
                has_moon_trajectory = True
            check_time += timedelta(minutes=30)
        
        # Plot moon trajectory for this quarter (no legend)
        if moon_visible_in_quarter:
            plot_moon_trajectory_no_legend(ax, q_start, q_end)
        
        # Generate colors for this quarter's objects
        if quarter_visible_objects:
            # Use a better color distribution
            colormap = plt.get_cmap(COLOR_MAP)
            colors = colormap(np.linspace(0, 1, len(quarter_visible_objects)))
            
            # Plot trajectories for this quarter only (no legend)
            existing_positions = []
            for obj, color in zip(quarter_visible_objects, colors):
                plot_object_trajectory_no_legend(ax, obj, q_start, q_end, color, existing_positions, schedule)
                all_quarter_objects.add(obj.name)
        
        # Add quarter time info
        local_tz = get_local_timezone()
        q_start_local = q_start.astimezone(local_tz)
        q_end_local = q_end.astimezone(local_tz)
        time_text = f"{q_start_local.strftime('%H:%M')} - {q_end_local.strftime('%H:%M')}"
        ax.text(0.02, 0.98, time_text, transform=ax.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.4),
                verticalalignment='top', fontsize=10, fontweight='bold')
        
        # Add object count
        obj_count_text = f"Objects: {len(quarter_visible_objects)}"
        ax.text(0.02, 0.02, obj_count_text, transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.9),
                verticalalignment='bottom', fontsize=10, fontweight='bold')
        
        # Add scheduled objects indicator if schedule provided
        if schedule:
            scheduled_in_quarter = []
            for sched_start, sched_end, sched_obj in schedule:
                # Check if schedule overlaps with this quarter
                if (sched_start < q_end and sched_end > q_start and 
                    sched_obj in quarter_visible_objects):
                    scheduled_in_quarter.append(sched_obj.name)
            
            if scheduled_in_quarter:
                scheduled_text = f"Scheduled: {len(scheduled_in_quarter)}"
                ax.text(0.98, 0.02, scheduled_text, transform=ax.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9),
                        verticalalignment='bottom', horizontalalignment='right', 
                        fontsize=10, fontweight='bold')
        
        # Finalize legend for this subplot
        # finalize_plot_legend(ax)  # Commented out to avoid messy legends
    
    # Add a simple text summary instead of complex legends
    summary_text = (
        f"Total unique objects shown: {len(all_quarter_objects)}\n"
        f"Green area: Visible region"
    )
    if has_moon_trajectory:
        summary_text += " | Gold line: Moon trajectory"
    
    summary_text += "\nSolid lines: Sufficient time | Dashed lines: Insufficient time"
    
    # Add information about scheduled objects if any exist
    if schedule:
        summary_text += "\nYellow labels: Scheduled for observation"
    
    # Add summary as text in the figure (adjust position to avoid tight_layout issues)
    fig.text(0.02, 0.01, summary_text, fontsize=9, 
             bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgray", alpha=0.9),
             verticalalignment='bottom')
    
    # Adjust layout manually instead of tight_layout to avoid warnings
    plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.12)
    return fig

def plot_moon_trajectory_no_legend(ax, start_time, end_time):
    """Plot moon trajectory without adding legend entries"""
    times = []
    alts = []
    azs = []
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_moon_position(current_time)
        if is_visible(alt, az):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if azs:
        # Plot moon trajectory (no label for legend)
        ax.plot(azs, alts, '-', color=MOON_TRAJECTORY_COLOR, 
               linewidth=MOON_LINE_WIDTH, zorder=2)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=MOON_MARKER_COLOR, 
                   markersize=MOON_MARKER_SIZE, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=MOON_MARKER_COLOR,
                       zorder=3)

def plot_object_trajectory_no_legend(ax, obj, start_time, end_time, color, existing_positions=None, schedule=None):
    """Plot object trajectory without adding legend entries
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    obj : CelestialObject
        Object to plot trajectory for
    start_time : datetime
        Start time for trajectory
    end_time : datetime
        End time for trajectory
    color : str
        Color for trajectory and markers
    existing_positions : list, optional
        List of existing label positions to avoid overlap
    schedule : list, optional
        List of scheduled observations [(start, end, obj), ...] for label styling
    """
    times = []
    alts = []
    azs = []
    near_moon = []
    moon_alts = []
    obj.near_moon = False
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Check if this object is scheduled
    is_scheduled = False
    if schedule:
        scheduled_objects = [sched_obj for _, _, sched_obj in schedule]
        is_scheduled = obj in scheduled_objects
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        moon_alt, moon_az = calculate_moon_position(current_time)
        
        # Extended visibility check
        if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
            MIN_AZ - 5 <= az <= MAX_AZ + 5):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Check moon proximity
            is_near = False
            if moon_alt >= 0:
                is_near = is_near_moon(alt, az, moon_alt, moon_az, obj.magnitude, current_time)
            near_moon.append(is_near)
            moon_alts.append(moon_alt)
            
            # Hour markers
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if not azs:
        return
    
    # Determine line style
    line_style = '-' if getattr(obj, 'sufficient_time', True) else '--'
    
    # Plot base trajectory (no label for legend)
    ax.plot(azs, alts, line_style, color=color, linewidth=1.5, alpha=0.3, zorder=1)
    
    # Plot moon-affected segments if any
    if hasattr(obj, 'moon_influence_periods'):
        for start_idx, end_idx in obj.moon_influence_periods:
            # Handle both integer indices and datetime objects
            if isinstance(start_idx, datetime) and isinstance(end_idx, datetime):
                # Convert datetime objects to indices if needed
                # This is a simplified approach - for quarters view we skip detailed moon segments
                continue
            elif isinstance(start_idx, int) and isinstance(end_idx, int):
                # Original integer-based approach
                valid_segment = True
                for i in range(start_idx, min(end_idx+1, len(moon_alts))):
                    if moon_alts[i] < 0:
                        valid_segment = False
                        break
                
                if valid_segment:
                    ax.plot(azs[start_idx:end_idx+1], 
                           alts[start_idx:end_idx+1], 
                           line_style,
                           color=MOON_INTERFERENCE_COLOR,
                           linewidth=2,
                           zorder=2)
            # Skip mixed types or invalid data
    
    # Add hour markers
    for t, az, alt in zip(hour_times, hour_azs, hour_alts):
        ax.plot(az, alt, 'o', color=color, markersize=6, zorder=3)
        ax.annotate(f'{t.hour:02d}h', 
                   (az, alt),
                   xytext=(5, 5),
                   textcoords='offset points',
                   fontsize=8,
                   color=color,
                   zorder=3)
    
    # Add abbreviated name near trajectory
    if existing_positions is None:
        existing_positions = []
        
    # Collect hour positions for avoiding overlap
    hour_positions = [(az, alt) for az, alt in zip(hour_azs, hour_alts)]
    existing_labels = []  # No legend in this version
    
    label_pos = find_optimal_label_position(azs, alts, hour_positions, existing_positions, 
                                           existing_labels, margin=6)
    if label_pos:
        abbreviated_name = get_abbreviated_name(obj.name)
        # Calculate smart offset
        trajectory_idx = len(azs) // 2
        offset_x, offset_y = calculate_label_offset(label_pos[0], label_pos[1], trajectory_idx, azs, alts)
        
        # Choose label background color based on scheduling status
        if is_scheduled:
            # Yellow transparent background for scheduled objects
            label_bg_color = "yellow"
            label_alpha = 0.6  # Slightly more opaque for better visibility of yellow
        else:
            # White transparent background for non-scheduled objects
            label_bg_color = "white"
            label_alpha = 0.4
        
        ax.annotate(abbreviated_name, 
                   label_pos,
                   xytext=(offset_x, offset_y),
                   textcoords='offset points',
                   color=color,
                   fontweight='bold',
                   fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=label_bg_color, alpha=label_alpha),
                   zorder=15)
        existing_positions.append(label_pos)

# ============= MOSAIC PLOTTING FUNCTIONS =============

def plot_mosaic_fov_indicator(ax, center_alt, center_az, fov_width, fov_height, color='red', alpha=0.3):
    """Plot a field of view indicator on the trajectory plot."""
    from matplotlib.patches import Ellipse
    
    # Create an ellipse to represent the FOV
    fov_patch = Ellipse((center_az, center_alt), fov_width, fov_height,
                       facecolor=color, edgecolor=color, alpha=alpha,
                       linestyle='--', linewidth=2)
    ax.add_patch(fov_patch)
    
    # Add FOV label
    ax.text(center_az, center_alt, f'Mosaic\nFOV\n{fov_width:.1f}°×{fov_height:.1f}°',
           ha='center', va='center', fontsize=8, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

def calculate_group_center_position(group, time):
    """Calculate the center position of a group at a given time."""
    altitudes = []
    azimuths = []
    
    # Handle both MosaicGroup and list of objects
    objects = group.objects if hasattr(group, 'objects') else group
    
    for obj in objects:
        alt, az = calculate_altaz(obj, time)
        if is_visible(alt, az, use_margins=True):
            altitudes.append(alt)
            azimuths.append(az)
    
    if altitudes and azimuths:
        return sum(altitudes) / len(altitudes), sum(azimuths) / len(azimuths)
    return None, None

def plot_mosaic_group_trajectory(ax, group, start_time, end_time, group_color, group_number, show_labels=True):
    """Plot trajectory for a mosaic group with special visual indicators."""
    import matplotlib.pyplot as plt
    
    # Handle both MosaicGroup and list of objects
    objects = group.objects if hasattr(group, 'objects') else group
    overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
    
    # Plot individual object trajectories
    existing_positions = []
    
    for i, obj in enumerate(objects):
        times = []
        alts = []
        azs = []
        hour_times = []
        hour_alts = []
        hour_azs = []
        
        # Ensure times are in UTC for calculations
        if start_time.tzinfo != pytz.UTC:
            start_time = start_time.astimezone(pytz.UTC)
        if end_time.tzinfo != pytz.UTC:
            end_time = end_time.astimezone(pytz.UTC)
        
        current_time = start_time
        while current_time <= end_time:
            alt, az = calculate_altaz(obj, current_time)
            
            # Extended visibility check for trajectory plotting (±5 degrees)
            if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
                MIN_AZ - 5 <= az <= MAX_AZ + 5):
                times.append(current_time)
                alts.append(alt)
                azs.append(az)
                
                # Convert to local time for display
                local_time = utc_to_local(current_time)
                if local_time.minute == 0:
                    hour_times.append(local_time)
                    hour_alts.append(alt)
                    hour_azs.append(az)
                    
            current_time += timedelta(minutes=1)
        
        if azs:
            # Use different line styles for objects in the same group
            line_styles = ['-', '--', '-.', ':']
            line_style = line_styles[i % len(line_styles)]
            
            # Plot trajectory
            label = f'Group {group_number}: {get_abbreviated_name(obj.name)}' if show_labels else None
            ax.plot(azs, alts, line_style, color=group_color, linewidth=2, 
                   alpha=0.8, label=label)
            
            # Add hour markers (reduce frequency for smaller plots)
            marker_freq = 2 if not show_labels else 1  # Every 2 hours for small plots
            for j, (t, az, alt) in enumerate(zip(hour_times, hour_azs, hour_alts)):
                if j % marker_freq == 0:
                    ax.plot(az, alt, 'o', color=group_color, markersize=4 if not show_labels else 6, zorder=3)
                    if show_labels:
                        ax.annotate(f'{t.hour:02d}h', 
                                   (az, alt),
                                   xytext=(5, 5),
                                   textcoords='offset points',
                                   fontsize=8,
                                   color=group_color,
                                   zorder=3)
            
            # Add object label
            if len(azs) > 10 and show_labels:  # Only if we have enough points and showing labels
                mid_idx = len(azs) // 2
                label_pos = (azs[mid_idx], alts[mid_idx])
                
                abbreviated_name = get_abbreviated_name(obj.name)
                offset_x, offset_y = calculate_label_offset(label_pos[0], label_pos[1], mid_idx, azs, alts)
                
                # Use group-specific background color
                ax.annotate(abbreviated_name, 
                           label_pos,
                           xytext=(offset_x, offset_y),
                           textcoords='offset points',
                           color=group_color,
                           fontweight='bold',
                           fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor=group_color, alpha=0.3),
                           zorder=15)
                existing_positions.append(label_pos)
    
    return existing_positions

def plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=False):
    """Plot the mosaic field of view at the optimal observation time."""
    from matplotlib.patches import Ellipse
    
    if not overlap_periods:
        return
    
    # Find the middle of the longest overlap period
    longest_period = max(overlap_periods, key=lambda p: (p[1] - p[0]).total_seconds())
    mid_time = longest_period[0] + (longest_period[1] - longest_period[0]) / 2
    
    # Calculate the center position of the group at this time
    center_alt, center_az = calculate_group_center_position(group, mid_time)
    
    if center_alt is not None and center_az is not None:
        # Plot the mosaic FOV indicator
        if small_plot:
            # Simplified FOV indicator for small plots
            fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                               facecolor=group_color, edgecolor=group_color, alpha=0.15,
                               linestyle='--', linewidth=1)
            ax.add_patch(fov_patch)
        else:
            plot_mosaic_fov_indicator(ax, center_alt, center_az, 
                                    MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT, 
                                    color=group_color, alpha=0.2)

def create_mosaic_trajectory_plot(groups, start_time, end_time):
    """Create a trajectory plot specifically for mosaic groups."""
    import matplotlib.pyplot as plt
    
    # Setup the plot
    fig, ax = setup_altaz_plot()
    
    # Plot moon trajectory
    plot_moon_trajectory(ax, start_time, end_time)
    
    # Define colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Plot each mosaic group
    for i, group in enumerate(groups):
        group_color = colors[i % len(colors)]
        group_number = i + 1
        
        print(f"Plotting Mosaic Group {group_number} ({len(group.objects) if hasattr(group, 'objects') else len(group)} objects)...")
        
        # Get overlap periods
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        
        # Plot trajectories for this group
        plot_mosaic_group_trajectory(ax, group, start_time, end_time, 
                                    group_color, group_number, show_labels=True)
        
        # Plot FOV indicator at optimal time
        plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=False)
    
    # Customize the plot
    night_date = start_time.date()
    plt.title(f'Mosaic Group Trajectories - {night_date}\n{SCOPE_NAME} (Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°)', 
              fontsize=14, fontweight='bold')
    
    # Create custom legend
    handles, labels = ax.get_legend_handles_labels()
    
    # Sort legend by group number
    sorted_items = sorted(zip(handles, labels), key=lambda x: x[1])
    sorted_handles, sorted_labels = zip(*sorted_items) if sorted_items else ([], [])
    
    # Add legend
    ax.legend(sorted_handles, sorted_labels,
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Mosaic Groups')
    
    return fig, ax

def create_mosaic_grid_plot(groups, start_time, end_time):
    """Create a grid of individual mosaic plots without legends to maximize space."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    n_groups = len(groups)
    if n_groups == 0:
        return None, None
    
    # Calculate grid dimensions
    cols = min(3, n_groups)  # Maximum 3 columns
    rows = math.ceil(n_groups / cols)
    
    # Create subplot grid
    fig, axes = plt.subplots(rows, cols, figsize=(16, 6*rows))
    if n_groups == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
    else:
        axes = axes.flatten()
    
    # Colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    for i, group in enumerate(groups):
        ax = axes[i]
        group_color = colors[i % len(colors)]
        group_number = i + 1
        
        # Setup this subplot
        ax.set_xlim(MIN_AZ, MAX_AZ)
        ax.set_ylim(MIN_ALT, MAX_ALT)
        ax.set_xlabel('Azimuth (degrees)', fontsize=10)
        ax.set_ylabel('Altitude (degrees)', fontsize=10)
        ax.grid(True, alpha=GRID_ALPHA)
        ax.tick_params(labelsize=9)
        
        # Plot moon trajectory (simplified)
        plot_moon_trajectory_no_legend(ax, start_time, end_time)
        
        # Get overlap periods and objects
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        objects = group.objects if hasattr(group, 'objects') else group
        
        # Plot this group
        plot_mosaic_group_trajectory(ax, group, start_time, end_time, 
                                    group_color, group_number, show_labels=False)
        
        # Plot FOV indicator
        plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=True)
        
        # Add group title and info
        group_names = [get_abbreviated_name(obj.name) for obj in objects]
        total_time = sum((p[1] - p[0]).total_seconds() / 3600 for p in overlap_periods)
        
        title = f"Group {group_number}: {', '.join(group_names)}\n{total_time:.1f}h overlap"
        ax.set_title(title, fontsize=10, fontweight='bold', pad=10)
        
        # Add timing text in corner
        timing_text = ""
        for period_start, period_end in overlap_periods:
            timing_text += f"{period_start.strftime('%H:%M')}-{period_end.strftime('%H:%M')} "
        
        if timing_text:
            ax.text(0.02, 0.98, timing_text.strip(), transform=ax.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
                    verticalalignment='top', fontsize=8)
    
    # Hide unused subplots
    for i in range(n_groups, len(axes)):
        axes[i].set_visible(False)
    
    # Overall title
    fig.suptitle(f'Mosaic Groups Detail - {start_time.date()}\n{SCOPE_NAME} Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    return fig, axes

# ============= MAIN PROGRAM =============

def main():
    """Main program execution"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Astronomical visibility report and charts')
    parser.add_argument('--date', type=str, default=None, help='Date for calculations (YYYY-MM-DD)')
    parser.add_argument('--object', type=str, default=None, help='Specific object to display')
    parser.add_argument('--type', type=str, default=None, help='Filter by object type')
    parser.add_argument('--report-only', action='store_true', help='Show only the text report')
    parser.add_argument('--schedule', choices=['longest_duration', 'max_objects', 'optimal_snr', 'minimal_mosaic', 'difficulty_balanced', 'mosaic_groups'], 
                      default='longest_duration', help='Scheduling strategy')
    parser.add_argument('--no-margins', action='store_true', 
                      help='Do not use extended margins for visibility chart')
    parser.add_argument('--simulate-time', type=str, default=None, 
                      help='Simulate running at a specific time (format: HH:MM or HH:MM:SS)')
    parser.add_argument('--quarters', action='store_true',
                      help='Use 4-quarter trajectory plots instead of single plot')
    parser.add_argument('--mosaic', action='store_true',
                      help='Enable mosaic group analysis and specialized plots')
    parser.add_argument('--mosaic-only', action='store_true',
                      help='Show only mosaic groups (implies --mosaic)')
    parser.add_argument('--no-duplicates', action='store_true',
                      help='When used with --mosaic, exclude individual objects that are already part of mosaic groups from standalone display')
    
    args = parser.parse_args()
    
    # Map command line schedule argument to SchedulingStrategy
    strategy_mapping = {
        'longest_duration': SchedulingStrategy.LONGEST_DURATION,
        'max_objects': SchedulingStrategy.MAX_OBJECTS,
        'optimal_snr': SchedulingStrategy.OPTIMAL_SNR,
        'minimal_mosaic': SchedulingStrategy.MINIMAL_MOSAIC,
        'difficulty_balanced': SchedulingStrategy.DIFFICULTY_BALANCED,
        'mosaic_groups': SchedulingStrategy.MOSAIC_GROUPS
    }
    selected_strategy = strategy_mapping[args.schedule]
    
    # Set up time simulation if requested
    if args.simulate_time:
        local_tz = get_local_timezone()
        simulated_time = get_simulated_datetime(args.simulate_time, local_tz)
        if simulated_time:
            time_sim.SIMULATED_DATETIME = simulated_time
            print(f"Simulating time: {time_sim.SIMULATED_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get current time to determine which night we're in
    current_date = get_current_datetime(get_local_timezone())
    
    # If current time is after midnight but before noon, we're still in the "night"
    # of the previous day, so we need to adjust the date for calculations
    if current_date.hour < 12:
        yesterday = current_date - timedelta(days=1)
        sunset, next_sunrise = find_sunset_sunrise(yesterday)
        twilight_evening, twilight_morning = find_astronomical_twilight(yesterday)
    else:
        # We're in daytime (afternoon), calculate for upcoming night
        sunset, next_sunrise = find_sunset_sunrise(current_date)
        twilight_evening, twilight_morning = find_astronomical_twilight(current_date)

    # Ensure twilight times are in the correct timezone
    local_tz = get_local_timezone()
    if twilight_evening.tzinfo != local_tz:
        twilight_evening = twilight_evening.astimezone(local_tz)
    if twilight_morning.tzinfo != local_tz:
        twilight_morning = twilight_morning.astimezone(local_tz)

    # Check if we're currently between evening twilight and morning twilight
    # (i.e., during astronomical night)
    is_night_time = (current_date >= twilight_evening and current_date <= twilight_morning)

    # If we're already in the night, only show objects visible for the rest of the night - reverted back EP 24/05/2025
    if is_night_time:
        # Only calculate visibility from current time until morning twilight
        start_time = twilight_evening #current_date
        end_time = twilight_morning
    else:
        # We're in daytime, calculate for the entire upcoming night
        start_time = twilight_evening
        end_time = twilight_morning

    # Get objects
    if USE_CSV_CATALOG:
        all_objects = get_objects_from_csv()
        if not all_objects:
            all_objects = get_combined_catalog()
            return
    else:
        all_objects = get_combined_catalog()
    
    # Determine use_margins setting from args (invert the no-margins flag)
    use_margins = not args.no_margins
    
    # Filter objects based on visibility and exposure requirements for the calculated time period
    visible_objects, insufficient_objects = filter_visible_objects(
        all_objects, start_time, end_time, use_margins=use_margins)
    
    if not visible_objects and not insufficient_objects:
        print("No objects are visible under current conditions")
        return
    
    # Initialize report generator with the observation period
    report_gen = ReportGenerator(start_time, DEFAULT_LOCATION)
    
    # Find moon rise and set times and check moon interference
    moon_rise = None
    moon_set = None
    check_time = start_time
    prev_alt = None
    
    # First pass: find moon rise/set times for the observation period
    while check_time <= end_time:
        moon_alt, _ = calculate_moon_position(check_time)
        
        if prev_alt is not None:
            # Moon rise detected
            if prev_alt < 0 and moon_alt >= 0:
                moon_rise = check_time
            # Moon set detected
            elif prev_alt >= 0 and moon_alt < 0:
                moon_set = check_time
        
        prev_alt = moon_alt
        check_time += timedelta(minutes=1)
    
    # Calculate moon phase at the start of the observation period
    moon_phase = calculate_moon_phase(start_time)
    
    # Second pass: check moon interference for each object
    moon_affected = []
    all_objects_to_check = visible_objects + insufficient_objects
    
    for obj in all_objects_to_check:
        # Reset moon interference attributes
        obj.near_moon = False
        obj.moon_influence_periods = []
        
        # Check visibility periods for the observation period
        visibility_periods = find_visibility_window(obj, start_time, end_time, use_margins=True)
        
        for period_start, period_end in visibility_periods:
            check_time = period_start
            interference_start = None
            
            while check_time <= period_end:
                obj_alt, obj_az = calculate_altaz(obj, check_time)
                moon_alt, moon_az = calculate_moon_position(check_time)
                
                # Only consider interference if moon is above horizon (risen)
                if moon_alt >= 0 and is_near_moon(obj_alt, obj_az, moon_alt, moon_az, obj.magnitude, check_time):
                    if interference_start is None:
                        interference_start = check_time
                elif interference_start is not None:
                    obj.moon_influence_periods.append((interference_start, check_time))
                    interference_start = None
                
                check_time += timedelta(minutes=15)  # Check every 15 minutes
            
            if interference_start is not None:
                # For the last period, verify the moon is still above horizon
                # This handles the case where interference starts but then moon sets
                check_time = period_end
                _, moon_alt = calculate_moon_position(check_time)
                if moon_alt >= 0:
                    obj.moon_influence_periods.append((interference_start, period_end))
        
        # Only consider object affected if there are interference periods
        if obj.moon_influence_periods:
            obj.near_moon = True
            moon_affected.append(obj)
    
    # Generate initial report sections for the observation period
    report_gen.generate_quick_summary(visible_objects, moon_affected, 
                                    start_time, end_time, moon_phase)
    report_gen.generate_timing_section(sunset, next_sunrise, 
                                     twilight_evening, twilight_morning,
                                     moon_rise, moon_set)
    report_gen.generate_moon_conditions(moon_phase, moon_affected)
    
    # Mosaic group analysis and integration
    mosaic_groups = []
    combined_objects = visible_objects
    
    if args.mosaic or args.mosaic_only or args.schedule == 'mosaic_groups':
        print("\nAnalyzing mosaic groups...")
        mosaic_groups = create_mosaic_groups(visible_objects, start_time, end_time)
        
        if mosaic_groups:
            print(f"Found {len(mosaic_groups)} mosaic groups.")
            
            # Use the selected strategy for mosaic analysis
            scheduling_strategy = selected_strategy
            
            # Combine objects and groups based on strategy
            combined_objects = combine_objects_and_groups(visible_objects, mosaic_groups, scheduling_strategy, args.no_duplicates)
            
            # Add mosaic groups to report
            if mosaic_groups:
                mosaic_content = "Mosaic groups found:\n\n"
                for i, group in enumerate(mosaic_groups):
                    mosaic_content += f"Group {i+1}: {group.name}\n"
                    mosaic_content += f"  Objects: {', '.join([get_abbreviated_name(obj.name) for obj in group.objects])}\n"
                    mosaic_content += f"  Total overlap time: {group.calculate_total_overlap_duration():.1f} hours\n"
                    mosaic_content += f"  Composite magnitude: {group.magnitude:.1f}\n\n"
                
                report_gen.add_section("MOSAIC GROUPS", mosaic_content)
        else:
            print("No mosaic groups found with current criteria.")
            if args.mosaic_only:
                print("No plots will be generated as no mosaic groups were found.")
    
    # Filter objects if mosaic-only mode
    if args.mosaic_only:
        if mosaic_groups:
            combined_objects = mosaic_groups
        else:
            print("No mosaic groups found. Exiting.")
            return
    
    # Generate object sections using the filtered objects when --no-duplicates is used
    if args.no_duplicates and mosaic_groups:
        # Extract individual objects from combined_objects (excluding mosaic groups)
        individual_filtered_objects = [obj for obj in combined_objects if not hasattr(obj, 'is_mosaic_group')]
        report_gen.generate_object_sections(individual_filtered_objects, insufficient_objects)
    else:
        # Use original visible objects for report
        report_gen.generate_object_sections(visible_objects, insufficient_objects)
    
    # Generate schedules for different strategies for the observation period
    schedules = {}
    for strategy in SchedulingStrategy:
        schedule = generate_observation_schedule(
            combined_objects, start_time, end_time,
            strategy=strategy)
        schedules[strategy] = schedule
        report_gen.generate_schedule_section(schedule, strategy)
    
    # Print the complete report
    print(report_gen.generate_report())
    
    # Skip plots if report-only is specified
    if args.report_only:
        return
        
    # Use selected strategy for visualization
    schedule = schedules[selected_strategy]
    
    # Choose plotting method based on arguments
    if args.mosaic and mosaic_groups:
        # Create mosaic-specific plots
        print("\nGenerating mosaic trajectory plots...")
        
        # 1. Combined mosaic trajectory plot
        fig_combined, ax_combined = create_mosaic_trajectory_plot(mosaic_groups, start_time, end_time)
        plt.tight_layout()
        plt.show()
        plt.close(fig_combined)
        
        # 2. Grid of individual mosaic plots
        print("Generating mosaic groups detail grid...")
        fig_grid, axes_grid = create_mosaic_grid_plot(mosaic_groups, start_time, end_time)
        if fig_grid:
            plt.show()
            plt.close(fig_grid)
        
        # If not mosaic-only, also show regular plots with combined objects
        if not args.mosaic_only:
            print("Generating combined trajectory plot...")
            fig, ax = setup_altaz_plot()
            
            # Generate colors for combined objects
            colormap = plt.get_cmap(COLOR_MAP) 
            colors = colormap(np.linspace(0, 1, len(combined_objects)))
            
            # Plot moon trajectory first
            plot_moon_trajectory(ax, start_time, end_time)
            
            existing_positions = []
            # Plot trajectories for combined objects
            for obj, color in zip(combined_objects, colors):
                if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                    # Plot mosaic group differently
                    plot_mosaic_group_trajectory(ax, obj, start_time, end_time, 
                                                color, len(existing_positions)+1, show_labels=True)
                else:
                    plot_object_trajectory(ax, obj, start_time, end_time, 
                                         color, existing_positions, schedule)
            
            plt.title(f"Combined Objects and Mosaic Groups - {sunset.date()}")
            finalize_plot_legend(ax)
            plt.show()
            plt.close(fig)
            
    elif args.quarters:
        # Create 4-quarter trajectory plots
        if not EXCLUDE_INSUFFICIENT_TIME:
            all_visible = combined_objects + insufficient_objects
        else:
            all_visible = combined_objects
        
        fig = plot_quarterly_trajectories(all_visible, start_time, end_time, schedule)
        plt.show()
        plt.close(fig)
        
    else:
        # Create original plots for the observation period
        fig, ax = setup_altaz_plot()
        
        # Generate colors 
        colormap = plt.get_cmap(COLOR_MAP) 
        colors = colormap(np.linspace(0, 1, len(combined_objects)))
        
        # Initialize empty legend to avoid NoneType errors
        ax.legend()
        
        # Plot moon trajectory first
        plot_moon_trajectory(ax, start_time, end_time)
        
        existing_positions = []
        # Plot trajectories for combined objects
        for obj, color in zip(combined_objects, colors):
            if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                # Plot mosaic group
                plot_mosaic_group_trajectory(ax, obj, start_time, end_time, 
                                            color, len(existing_positions)+1, show_labels=True)
            else:
                plot_object_trajectory(ax, obj, start_time, end_time, 
                                     color, existing_positions, schedule)
        
        # Plot trajectories for insufficient time objects if not excluded
        if not EXCLUDE_INSUFFICIENT_TIME and not args.mosaic_only:
            for obj in insufficient_objects:
                plot_object_trajectory(ax, obj, start_time, end_time, 
                                     'pink', existing_positions, schedule)
        
        # Use sunset date for the title to maintain consistency in the display
        title = f"Object Trajectories for Night of {sunset.date()}"
        if mosaic_groups and not args.mosaic_only:
            title += f" (including {len(mosaic_groups)} mosaic groups)"
        plt.title(title)
        
        # Create custom legend
        handles, labels = ax.get_legend_handles_labels()
        
        # Add a legend entry for moon interference if any object was near moon
        all_check_objects = combined_objects + (insufficient_objects if not args.mosaic_only else [])
        if any(obj for obj in all_check_objects if hasattr(obj, 'near_moon')):
            moon_line = plt.Line2D([0], [0], color=MOON_INTERFERENCE_COLOR, linestyle='-', label='Moon Interference')
            handles.append(moon_line)
        
        # Add legend entry for insufficient time objects if any
        if insufficient_objects and not args.mosaic_only:
            insuf_line = plt.Line2D([0], [0], color='gray', linestyle='--', label='Insufficient Time')
            handles.append(insuf_line)
        
        # Create the legend with all handles
        finalize_plot_legend(ax)
        plt.show()
        plt.close(fig)  # Explicitly close the figure
    
    # Create visibility chart for the observation period
    chart_objects = combined_objects.copy()
    if not EXCLUDE_INSUFFICIENT_TIME and not args.mosaic_only:
        chart_objects.extend(insufficient_objects)
    
    chart_title = "Object Visibility"
    if mosaic_groups:
        chart_title += f" (including {len(mosaic_groups)} mosaic groups)"
    
    fig, ax = plot_visibility_chart(chart_objects, start_time, 
                                  end_time, schedule, title=chart_title, use_margins=False)
    plt.show()
    plt.close(fig)  # Explicitly close the figure

if __name__ == "__main__":
    main()

