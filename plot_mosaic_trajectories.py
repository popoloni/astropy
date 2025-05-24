#!/usr/bin/env python3
"""
Mosaic Trajectory Plotter for Vaonis Vespera Passenger
======================================================
Creates dedicated trajectory plots showing only objects that can be photographed
together in mosaic groups, with field of view indicators.
"""

import math
import sys
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import astropy functions
from astropy import (
    get_combined_catalog, get_objects_from_csv, USE_CSV_CATALOG,
    calculate_altaz, get_local_timezone, get_current_datetime,
    find_astronomical_twilight, find_visibility_window,
    calculate_visibility_duration, MIN_VISIBILITY_HOURS,
    setup_altaz_plot, plot_moon_trajectory, utc_to_local,
    is_visible, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, GRID_ALPHA,
    get_abbreviated_name, find_optimal_label_position,
    calculate_label_offset, pytz, CONFIG
)

# Import mosaic analysis functions
from utilities.analyze_mosaic_groups import (
    analyze_object_groups, calculate_angular_separation, can_fit_in_mosaic, objects_visible_simultaneously
)

# Get mosaic FOV from configuration
MOSAIC_FOV_WIDTH = CONFIG['imaging']['scope']['mosaic_fov_width']
MOSAIC_FOV_HEIGHT = CONFIG['imaging']['scope']['mosaic_fov_height']
SCOPE_NAME = CONFIG['imaging']['scope']['name']

def plot_mosaic_fov_indicator(ax, center_alt, center_az, fov_width, fov_height, color='red', alpha=0.3):
    """
    Plot a field of view indicator on the trajectory plot.
    """
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
    """
    Calculate the center position of a group at a given time.
    """
    altitudes = []
    azimuths = []
    
    for obj in group:
        alt, az = calculate_altaz(obj, time)
        if is_visible(alt, az, use_margins=True):
            altitudes.append(alt)
            azimuths.append(az)
    
    if altitudes and azimuths:
        return sum(altitudes) / len(altitudes), sum(azimuths) / len(azimuths)
    return None, None

def plot_mosaic_group_trajectory(ax, group, start_time, end_time, group_color, group_number, show_labels=True):
    """
    Plot trajectory for a mosaic group with special visual indicators.
    """
    # Plot individual object trajectories
    existing_positions = []
    
    for i, obj in enumerate(group):
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
    """
    Plot the mosaic field of view at the optimal observation time.
    """
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

def sort_groups_by_timing(groups):
    """
    Sort groups by start time (ascending), then by end time (ascending) as tiebreaker.
    
    Args:
        groups: List of tuples (group, overlap_periods)
        
    Returns:
        Sorted list of groups
    """
    def get_group_timing(group_tuple):
        group, overlap_periods = group_tuple
        if not overlap_periods:
            return (float('inf'), float('inf'))  # Put groups with no overlap at the end
        
        # Find earliest start time across all overlap periods
        earliest_start = min(period[0] for period in overlap_periods)
        # Find earliest end time across all overlap periods
        earliest_end = min(period[1] for period in overlap_periods)
        
        return (earliest_start, earliest_end)
    
    return sorted(groups, key=get_group_timing)

def create_mosaic_trajectory_plot(groups, start_time, end_time):
    """
    Create a trajectory plot specifically for mosaic groups.
    """
    # Setup the plot
    fig, ax = setup_altaz_plot()
    
    # Plot moon trajectory
    plot_moon_trajectory(ax, start_time, end_time)
    
    # Define colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Plot each mosaic group
    for i, (group, overlap_periods) in enumerate(groups):
        group_color = colors[i % len(colors)]
        group_number = i + 1
        
        print(f"Plotting Mosaic Group {group_number} ({len(group)} objects)...")
        
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
    """
    Create a grid of individual mosaic plots without legends to maximize space.
    """
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
    
    for i, (group, overlap_periods) in enumerate(groups):
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
        plot_moon_trajectory(ax, start_time, end_time)
        
        # Plot this group
        plot_mosaic_group_trajectory(ax, group, start_time, end_time, 
                                    group_color, group_number, show_labels=False)
        
        # Plot FOV indicator
        plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=True)
        
        # Add group title and info
        group_names = [get_abbreviated_name(obj.name) for obj in group]
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

def create_mosaic_visibility_chart(groups, start_time, end_time):
    """
    Create a visibility chart specifically for mosaic groups.
    """
    if not groups:
        return None, None
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Time axis (every 15 minutes)
    time_points = []
    current = start_time
    while current <= end_time:
        time_points.append(current)
        current += timedelta(minutes=15)
    
    # Convert to hours from start for plotting
    time_hours = [(t - start_time).total_seconds() / 3600 for t in time_points]
    
    # Plot each mosaic group
    y_position = 0
    group_labels = []
    
    # Plot groups in reverse order so earliest starting group appears at top
    for i, (group, overlap_periods) in enumerate(reversed(groups)):
        group_color = colors[(len(groups) - 1 - i) % len(colors)]  # Keep original color assignment
        group_number = len(groups) - i  # Keep original group numbering
        
        # Create group label
        group_names = [get_abbreviated_name(obj.name) for obj in group]
        group_label = f"Group {group_number}: {', '.join(group_names)}"
        group_labels.append(group_label)
        
        # Plot visibility bars for overlap periods
        for period_start, period_end in overlap_periods:
            start_hour = (period_start - start_time).total_seconds() / 3600
            end_hour = (period_end - start_time).total_seconds() / 3600
            
            # Main visibility bar
            ax.barh(y_position, end_hour - start_hour, left=start_hour, height=0.6,
                   color=group_color, alpha=0.7, edgecolor='black', linewidth=1)
            
            # Add timing text
            duration = (period_end - period_start).total_seconds() / 3600
            mid_hour = start_hour + (end_hour - start_hour) / 2
            ax.text(mid_hour, y_position, f'{duration:.1f}h',
                   ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        y_position += 1
    
    # Customize the chart
    ax.set_xlim(0, (end_time - start_time).total_seconds() / 3600)
    ax.set_ylim(-0.5, len(groups) - 0.5)
    
    # Add vertical line for current time if it's within the plot range
    local_tz = get_local_timezone()
    current_time = get_current_datetime(local_tz)
    if start_time <= current_time <= end_time:
        current_hour = (current_time - start_time).total_seconds() / 3600
        ax.axvline(x=current_hour, color='red', linestyle='-', linewidth=2,
                   label='Current Time', alpha=0.8)
    
    # Time axis labels
    hour_ticks = list(range(0, int((end_time - start_time).total_seconds() / 3600) + 1))
    hour_labels = []
    for h in hour_ticks:
        time_label = start_time + timedelta(hours=h)
        hour_labels.append(time_label.strftime('%H:%M'))
    
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_labels)
    ax.set_xlabel('Time (Local)', fontsize=12)
    
    # Y axis
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels(group_labels)
    ax.set_ylabel('Mosaic Groups', fontsize=12)
    
    # Grid
    ax.grid(True, axis='x', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Title
    total_groups = len(groups)
    total_overlap_time = sum(
        sum((p[1] - p[0]).total_seconds() / 3600 for p in overlap_periods)
        for _, overlap_periods in groups
    )
    
    night_date = start_time.date()
    ax.set_title(f'Mosaic Groups Visibility Chart - {night_date}\n'
                f'{total_groups} groups, {total_overlap_time:.1f}h total observation time\n'
                f'{SCOPE_NAME} Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°', 
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax

def main():
    """Main function."""
    print("MOSAIC TRAJECTORY PLOTTER")
    print("=" * 50)
    
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
        start_time = twilight_evening #current_date # EP 24/05/2025 - reverted back
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
    
    print(f"Analyzing {len(visible_objects)} visible objects for mosaic groups...")
    
    # Analyze groups
    groups = analyze_object_groups(visible_objects, start_time, end_time)
    
    if not groups:
        print("No mosaic groups found!")
        return
    
    print(f"Found {len(groups)} mosaic groups. Creating trajectory plots...")
    
    # Sort groups by timing
    sorted_groups = sort_groups_by_timing(groups)
    
    # 1. Create combined plot with all groups and legend
    print("\n1. Creating combined mosaic trajectory plot...")
    fig_combined, ax_combined = create_mosaic_trajectory_plot(sorted_groups, start_time, end_time)
    plt.tight_layout()
    plt.show()
    
    # 2. Create grid of individual plots without legends
    print("\n2. Creating mosaic groups detail grid...")
    fig_grid, axes_grid = create_mosaic_grid_plot(sorted_groups, start_time, end_time)
    if fig_grid:
        plt.show()
    
    # 3. Create visibility chart for mosaic groups
    print("\n3. Creating mosaic groups visibility chart...")
    fig_visibility, ax_visibility = create_mosaic_visibility_chart(sorted_groups, start_time, end_time)
    if fig_visibility:
        plt.show()
    
    print(f"\nPlotting complete! Generated 3 specialized mosaic charts:")
    print("  • Combined trajectory plot with legend")
    print("  • Detail grid of individual groups")
    print("  • Mosaic groups visibility chart")

if __name__ == "__main__":
    main() 
