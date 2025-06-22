"""
Desktop mosaic plotting functions.

This module provides advanced mosaic plotting optimized for desktop displays
with detailed field of view indicators, group trajectory visualization, and
comprehensive mosaic analysis charts.
"""

import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse
import numpy as np
import pytz
from datetime import datetime, timedelta

# Import required functions and constants
from plots.base import setup_altaz_plot
from plots.trajectory.desktop import plot_moon_trajectory, plot_moon_trajectory_no_legend
from astronomy import (
    calculate_altaz, calculate_sun_position, is_visible, utc_to_local
)
from config.settings import (
    MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, GRID_ALPHA
)
from config.settings import MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT, SCOPE_NAME

# Desktop mosaic plotting constants
DESKTOP_FIGURE_SIZE = (15, 10)
DESKTOP_GRID_FIGURE_SIZE = (16, 6)
FOV_ALPHA = 0.3
FOV_SMALL_ALPHA = 0.15
LABEL_FONT_SIZE = 8
TITLE_FONT_SIZE = 14
GRID_TITLE_FONT_SIZE = 16

def plot_mosaic_fov_indicator(ax, center_alt, center_az, fov_width, fov_height, color='red', alpha=0.3):
    """
    Plot a field of view indicator on the trajectory plot.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    center_alt : float
        Center altitude in degrees
    center_az : float
        Center azimuth in degrees
    fov_width : float
        Field of view width in degrees
    fov_height : float
        Field of view height in degrees
    color : str, optional
        Color for the FOV indicator
    alpha : float, optional
        Transparency level
    """
    # Create an ellipse to represent the FOV
    fov_patch = Ellipse((center_az, center_alt), fov_width, fov_height,
                       facecolor=color, edgecolor=color, alpha=alpha,
                       linestyle='--', linewidth=2)
    ax.add_patch(fov_patch)
    
    # Add FOV label
    ax.text(center_az, center_alt, f'Mosaic\nFOV\n{fov_width:.1f}°×{fov_height:.1f}°',
           ha='center', va='center', fontsize=LABEL_FONT_SIZE, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

def calculate_group_center_position(group, time):
    """
    Calculate the center position of a group at a given time.
    
    Parameters:
    -----------
    group : MosaicGroup or list
        The mosaic group or list of objects
    time : datetime
        Time for position calculation
        
    Returns:
    --------
    tuple
        (center_altitude, center_azimuth) or (None, None) if no visible objects
    """
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
    """
    Plot trajectory for a mosaic group with special visual indicators.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    group : MosaicGroup or list
        The mosaic group or list of objects
    start_time : datetime
        Start time for trajectory
    end_time : datetime
        End time for trajectory
    group_color : str
        Color for the group
    group_number : int
        Group number for labeling
    show_labels : bool, optional
        Whether to show detailed labels
        
    Returns:
    --------
    list
        List of existing label positions
    """
    from plots.utils.common import get_abbreviated_name, calculate_label_offset
    
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
            
            # Check sun position for twilight-aware plotting
            sun_alt, _ = calculate_sun_position(current_time)
            from astronomy.visibility import get_twilight_angle
            is_dark_enough = sun_alt < get_twilight_angle()
            
            # Extended visibility check for trajectory plotting (±5 degrees)
            if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
                MIN_AZ - 5 <= az <= MAX_AZ + 5 and is_dark_enough):
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
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    group : MosaicGroup or list
        The mosaic group or list of objects
    overlap_periods : list
        List of (start_time, end_time) tuples for overlap periods
    group_color : str
        Color for the group
    small_plot : bool, optional
        Whether this is a small plot (simplified FOV indicator)
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
                               facecolor=group_color, edgecolor=group_color, alpha=FOV_SMALL_ALPHA,
                               linestyle='--', linewidth=1)
            ax.add_patch(fov_patch)
        else:
            plot_mosaic_fov_indicator(ax, center_alt, center_az, 
                                    MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT, 
                                    color=group_color, alpha=FOV_ALPHA)

def create_mosaic_trajectory_plot(groups, start_time, end_time):
    """
    Create a trajectory plot specifically for mosaic groups.
    
    This is the main desktop mosaic trajectory function with advanced features:
    - Individual object trajectories within each group
    - Field of view indicators at optimal observation times
    - Group-specific colors and styling
    - Comprehensive legend with sorted entries
    - Moon trajectory overlay
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups to plot
    start_time : datetime
        Start time for trajectory window
    end_time : datetime
        End time for trajectory window
        
    Returns:
    --------
    tuple
        (fig, ax) matplotlib figure and axes objects
    """
    # Setup the plot
    fig, ax = setup_altaz_plot()
    fig.set_size_inches(DESKTOP_FIGURE_SIZE)
    
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
              fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
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
    
    plt.tight_layout()
    return fig, ax

def create_mosaic_grid_plot(groups, start_time, end_time):
    """
    Create a grid of individual mosaic plots without legends to maximize space.
    
    This function creates detailed individual plots for each mosaic group:
    - Each group gets its own subplot
    - Simplified moon trajectory (no legend)
    - FOV indicators at optimal times
    - Group timing information
    - Optimized layout for multiple groups
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups to plot
    start_time : datetime
        Start time for trajectory window
    end_time : datetime
        End time for trajectory window
        
    Returns:
    --------
    tuple
        (fig, axes) matplotlib figure and axes objects
    """
    from plots.utils.common import get_abbreviated_name
    
    n_groups = len(groups)
    if n_groups == 0:
        return None, None
    
    # Calculate grid dimensions
    cols = min(3, n_groups)  # Maximum 3 columns
    rows = math.ceil(n_groups / cols)
    
    # Create subplot grid
    fig, axes = plt.subplots(rows, cols, figsize=(DESKTOP_GRID_FIGURE_SIZE[0], DESKTOP_GRID_FIGURE_SIZE[1]*rows))
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
                fontsize=GRID_TITLE_FONT_SIZE, fontweight='bold')
    
    plt.tight_layout()
    return fig, axes

# Helper functions for advanced mosaic analysis
def analyze_group_visibility_overlap(groups, start_time, end_time):
    """
    Analyze visibility overlap periods for mosaic groups.
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups
    start_time : datetime
        Start time for analysis
    end_time : datetime
        End time for analysis
        
    Returns:
    --------
    dict
        Dictionary with group analysis results
    """
    analysis_results = {}
    
    for i, group in enumerate(groups):
        group_number = i + 1
        objects = group.objects if hasattr(group, 'objects') else group
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        
        # Calculate total overlap time
        total_overlap_hours = sum((p[1] - p[0]).total_seconds() / 3600 for p in overlap_periods)
        
        # Find optimal observation time (center of longest period)
        if overlap_periods:
            longest_period = max(overlap_periods, key=lambda p: (p[1] - p[0]).total_seconds())
            optimal_time = longest_period[0] + (longest_period[1] - longest_period[0]) / 2
            center_alt, center_az = calculate_group_center_position(group, optimal_time)
        else:
            optimal_time = None
            center_alt, center_az = None, None
        
        analysis_results[group_number] = {
            'objects': objects,
            'overlap_periods': overlap_periods,
            'total_overlap_hours': total_overlap_hours,
            'optimal_time': optimal_time,
            'center_position': (center_alt, center_az),
            'object_count': len(objects)
        }
    
    return analysis_results

def create_mosaic_summary_plot(groups, start_time, end_time, analysis_results=None):
    """
    Create a summary plot showing all mosaic groups with key statistics.
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups
    start_time : datetime
        Start time for analysis
    end_time : datetime
        End time for analysis
    analysis_results : dict, optional
        Pre-computed analysis results
        
    Returns:
    --------
    tuple
        (fig, ax) matplotlib figure and axes objects
    """
    if analysis_results is None:
        analysis_results = analyze_group_visibility_overlap(groups, start_time, end_time)
    
    # Create summary plot
    fig, ax = setup_altaz_plot()
    fig.set_size_inches(DESKTOP_FIGURE_SIZE)
    
    # Plot moon trajectory
    plot_moon_trajectory(ax, start_time, end_time)
    
    # Colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Plot FOV indicators for all groups at their optimal times
    for group_number, results in analysis_results.items():
        group_color = colors[(group_number - 1) % len(colors)]
        center_alt, center_az = results['center_position']
        
        if center_alt is not None and center_az is not None:
            # Plot FOV indicator
            fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                               facecolor=group_color, edgecolor=group_color, alpha=0.4,
                               linestyle='-', linewidth=2, 
                               label=f'Group {group_number} ({results["total_overlap_hours"]:.1f}h)')
            ax.add_patch(fov_patch)
            
            # Add group number label
            ax.text(center_az, center_alt, str(group_number),
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   color='white', zorder=20)
    
    # Customize the plot
    night_date = start_time.date()
    plt.title(f'Mosaic Groups Summary - {night_date}\n{SCOPE_NAME} (Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°)', 
              fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title='Mosaic Groups')
    
    plt.tight_layout()
    return fig, ax 