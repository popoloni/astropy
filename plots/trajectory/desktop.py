"""
Desktop trajectory plotting functions for AstroScope application.
This module provides trajectory plotting functions optimized for desktop display.
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
import pytz
import re
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
from typing import List, Tuple, Optional, Any
import logging

from ..base import setup_altaz_plot, PlotConfig, get_color_cycle

# Import astronomy functions
from astronomy import (
    calculate_altaz, calculate_moon_position, is_visible, is_near_moon,
    utc_to_local, get_local_timezone
)

# Import configuration constants
from config.settings import COLOR_MAP, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants (these would normally be imported from config)
MOON_TRAJECTORY_COLOR = 'yellow'
MOON_LINE_WIDTH = 2
MOON_MARKER_COLOR = 'orange'
MOON_MARKER_SIZE = 8
MOON_INTERFERENCE_COLOR = 'red'
FIGURE_SIZE = (12, 8)
GRID_ALPHA = 0.3
VISIBLE_REGION_ALPHA = 0.1

def plot_object_trajectory(ax, obj, start_time, end_time, color, existing_positions=None, schedule=None):
    """
    Plot trajectory with moon proximity checking and legend.
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
    # Initialize legend handling - we'll add it later if needed
    
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
        # These functions would need to be imported from the main application
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
            # Update the legend now that we have a labeled item
            ax.legend()
        
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
        
        # Update the legend now that we have a labeled item
        ax.legend()
        
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

def plot_quarterly_trajectories(objects, start_time, end_time, schedule=None):
    """Create 4-quarter trajectory plots for better visualization"""
    # Calculate quarter duration
    total_duration = end_time - start_time
    quarter_duration = total_duration / 4
    
    # Create 2x2 subplot grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    all_quarter_objects = set()
    has_moon_trajectory = False
    
    for quarter in range(4):
        ax = axes[quarter]
        
        # Calculate quarter time range
        q_start = start_time + quarter * quarter_duration
        q_end = q_start + quarter_duration
        
        # Set up Alt-Az plot for this quarter
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
        
        # Find objects visible in this quarter
        quarter_visible_objects = []
        for obj in objects:
            # Check if object is visible during this quarter
            check_time = q_start
            while check_time <= q_end:
                alt, az = calculate_altaz(obj, check_time)
                if is_visible(alt, az, use_margins=True):
                    quarter_visible_objects.append(obj)
                    break
                check_time += timedelta(minutes=30)
        
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
            _plot_moon_trajectory_no_legend(ax, q_start, q_end)
        
        # Generate colors for this quarter's objects
        if quarter_visible_objects:
            # Use the same color distribution as legacy version
            colormap = plt.get_cmap(COLOR_MAP)
            colors = colormap(np.linspace(0, 1, len(quarter_visible_objects)))
            
            # Plot trajectories for this quarter only (no legend)
            existing_positions = []
            for obj, color in zip(quarter_visible_objects, colors):
                _plot_object_trajectory_no_legend(ax, obj, q_start, q_end, color, existing_positions, schedule)
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
    
    # Add overall title
    night_date = start_time.date()
    fig.suptitle(f'Quarterly Object Trajectories - {night_date}', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    return fig

# All helper functions are now properly imported from astronomy module

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

def plot_moon_trajectory_no_legend(ax, start_time, end_time):
    """Plot moon trajectory without adding to legend"""
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

def _plot_moon_trajectory_no_legend(ax, start_time, end_time):
    """Plot moon trajectory without adding to legend"""
    times = []
    alts = []
    azs = []
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_moon_position(current_time)
        if is_visible(alt, az):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
        current_time += timedelta(minutes=1)
    
    if azs:
        ax.plot(azs, alts, '-', color=MOON_TRAJECTORY_COLOR, 
               linewidth=MOON_LINE_WIDTH, zorder=2)

def _plot_object_trajectory_no_legend(ax, obj, start_time, end_time, color, existing_positions=None, schedule=None):
    """Plot object trajectory without adding to legend"""
    times = []
    alts = []
    azs = []
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        if is_visible(alt, az, use_margins=True):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
        current_time += timedelta(minutes=1)
    
    if azs:
        line_style = '-' if getattr(obj, 'sufficient_time', True) else '--'
        ax.plot(azs, alts, line_style, color=color, linewidth=1.5, zorder=1) 