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
from ..utils.common import (
    get_abbreviated_name, 
    calculate_label_offset, 
    find_optimal_label_position
)

# Import astronomy functions
from astronomy import (
    calculate_altaz, calculate_moon_position, is_visible, is_near_moon,
    utc_to_local, get_local_timezone
)

# Import configuration constants
from config.settings import (
    COLOR_MAP, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ,
    FIGURE_SIZE, GRID_ALPHA, VISIBLE_REGION_ALPHA,
    MOON_TRAJECTORY_COLOR, MOON_LINE_WIDTH, MOON_MARKER_COLOR, 
    MOON_MARKER_SIZE, MOON_INTERFERENCE_COLOR
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            
        label_pos_tuple = find_optimal_label_position(azs, alts, hour_positions, existing_positions, existing_labels, margin=6)
        if label_pos_tuple and len(label_pos_tuple) >= 2:
            label_pos = (label_pos_tuple[0], label_pos_tuple[1])
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
    """Plot object trajectory without adding legend entries"""
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
            if isinstance(start_idx, int) and isinstance(end_idx, int):
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
    
    label_pos_tuple = find_optimal_label_position(azs, alts, hour_positions, existing_positions, 
                                           existing_labels, margin=6)
    if label_pos_tuple and len(label_pos_tuple) >= 2:
        label_pos = (label_pos_tuple[0], label_pos_tuple[1])
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