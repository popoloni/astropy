"""
Desktop visibility chart plotting functions.

This module provides advanced visibility chart plotting optimized for desktop displays
with detailed scheduling information, moon interference visualization, and comprehensive
object analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle, Patch
from matplotlib.dates import DateFormatter
import numpy as np
import pytz
from datetime import datetime, timedelta

# Import astronomy functions
from astronomy import (
    find_visibility_window, calculate_visibility_duration, 
    get_local_timezone
)

# Import utility functions
from ..utils.common import get_abbreviated_name

# Import configuration constants
from config.settings import (
    MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, GRID_ALPHA, VISIBLE_REGION_ALPHA
)

# Constants for visibility plotting
FIGURE_SIZE = (15, 10)
MOON_INTERFERENCE_COLOR_RECOMMENDED = '#DAA520'  # Goldenrod for recommended objects
MOON_INTERFERENCE_COLOR_NON_RECOMMENDED = '#F0E68C'  # Khaki for non-recommended objects
SCHEDULED_COLOR = 'red'
INSUFFICIENT_TIME_COLOR = 'pink'
RECOMMENDED_COLOR = 'green'
NON_RECOMMENDED_COLOR = 'gray'

def plot_visibility_chart(objects, start_time, end_time, schedule=None, title="Object Visibility", use_margins=True):
    """
    Create comprehensive visibility chart showing moon interference and scheduled intervals.
    
    This is the main desktop visibility chart function with advanced features:
    - Base bars show full visibility with colors indicating status/moon interference
    - Scheduled intervals are overlaid with hatching
    - Moon interference periods are highlighted
    - Objects are sorted by visibility start time
    - Current time indicator
    - Comprehensive legend
    
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
        
    Returns:
    --------
    tuple
        (fig, ax) matplotlib figure and axes objects
    """
    # Ensure times are in local timezone
    local_tz = get_local_timezone()
    if start_time.tzinfo != local_tz:
        start_time = start_time.astimezone(local_tz)
    if end_time.tzinfo != local_tz:
        end_time = end_time.astimezone(local_tz)

    # Get current time in local timezone for the vertical line
    current_time = datetime.now(local_tz)

    # Create figure with settings - creating a brand new figure each time
    # to avoid any remnant elements from previous plots
    plt.close('all')  # Close any existing figures
    fig = plt.figure(figsize=FIGURE_SIZE)
    
    # Calculate dynamic height based on number of objects
    dynamic_height = max(10, len(objects) * 0.3 + 4)
    fig.set_size_inches(15, dynamic_height)
    
    # Full-width subplot - no need to reserve space for legend
    ax = fig.add_subplot(111)
    
    # Get visibility periods and sort objects
    sorted_objects = _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins)

    # Setup plot
    _setup_visibility_chart_axes(ax, title, start_time, end_time, local_tz)

    # Create mapping for recommended objects and scheduled intervals (in local time)
    recommended_objects = [obj for _, _, obj in schedule] if schedule else []
    scheduled_intervals = {obj: (start.astimezone(local_tz), end.astimezone(local_tz))
                           for start, end, obj in schedule} if schedule else {}

    # Plot BASE visibility periods
    for i, obj in enumerate(sorted_objects):
        _plot_object_visibility_bars(ax, i, obj, start_time, end_time,
                                   recommended_objects, use_margins)

    # OVERLAY the scheduled intervals with hatching
    for i, obj in enumerate(sorted_objects):
        if obj in scheduled_intervals:
            _plot_scheduled_interval(ax, i, obj, scheduled_intervals[obj], 
                                   start_time, end_time, use_margins)

    # Add vertical line for current time if it's within the plot range
    if start_time <= current_time <= end_time:
        ax.plot([current_time, current_time], [-0.5, len(sorted_objects)-0.5],
                color='red', linestyle='-', linewidth=2, label='Current Time')

    # Customize plot axes
    _setup_object_labels(ax, sorted_objects)
    ax.grid(True, axis='x', alpha=GRID_ALPHA)
    
    # Add comprehensive legend
    _add_visibility_chart_legend(ax, schedule, sorted_objects)
    
    # Use full figure width
    fig.tight_layout()
    
    return fig, ax

def create_mosaic_visibility_chart(groups, start_time, end_time):
    """
    Create a visibility chart specifically for mosaic groups.
    
    Parameters:
    -----------
    groups : list
        List of (group, overlap_periods) tuples
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
        
    Returns:
    --------
    tuple
        (fig, ax) matplotlib figure and axes objects
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
        color = colors[i % len(colors)]
        
        # Create group label
        if hasattr(group, 'objects') and group.objects:
            # Get abbreviated names of first few objects
            obj_names = [get_abbreviated_name(obj.name) for obj in group.objects[:3]]
            if len(group.objects) > 3:
                group_label = f"{', '.join(obj_names)} +{len(group.objects)-3}"
            else:
                group_label = ', '.join(obj_names)
        else:
            group_label = f"Group {len(groups)-i}"
        
        group_labels.append(group_label)
        
        # Plot overlap periods as horizontal bars
        for period_start, period_end in overlap_periods:
            # Convert to hours from start
            start_hours = (period_start - start_time).total_seconds() / 3600
            duration_hours = (period_end - period_start).total_seconds() / 3600
            
            # Only plot if within time range
            if start_hours < len(time_hours) and start_hours + duration_hours > 0:
                ax.barh(y_position, duration_hours, left=start_hours, 
                       height=0.6, color=color, alpha=0.7, 
                       edgecolor='black', linewidth=0.5)
        
        y_position += 1
    
    # Setup axes
    ax.set_xlim(0, time_hours[-1] if time_hours else 8)
    ax.set_ylim(-0.5, len(groups) - 0.5)
    
    # X axis - time labels
    hour_ticks = list(range(0, int(time_hours[-1]) + 1, 1)) if time_hours else [0]
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
                f'{total_groups} groups, {total_overlap_time:.1f}h total observation time', 
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax

# Helper functions

def _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins):
    """Get objects sorted by visibility start time for chart display"""
    local_tz = get_local_timezone()
    object_periods = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            # Convert periods to local time
            local_periods = [(p[0].astimezone(local_tz), p[1].astimezone(local_tz)) 
                           for p in periods]
            duration = calculate_visibility_duration(periods)
            object_periods.append((obj, local_periods[0][0], duration))
    
    # Sort by start time (reverse order for chart display)
    object_periods.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in object_periods]

def _setup_visibility_chart_axes(ax, title, start_time, end_time, tz):
    """Setup axes for visibility chart"""
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Local Time', fontsize=12)
    ax.set_ylabel('Objects', fontsize=12)
    ax.set_xlim(start_time, end_time)
    
    # Use local time formatter
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=tz))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))

def _plot_object_visibility_bars(ax, index, obj, start_time, end_time, recommended_objects, use_margins):
    """Plot visibility bars for a single object (BASE LAYER)"""
    local_tz = get_local_timezone()
    periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)

    is_recommended = obj in recommended_objects
    has_sufficient_time = getattr(obj, 'sufficient_time', True)
    
    # Determine base color
    if not has_sufficient_time:
        color = 'darkmagenta' if is_recommended else INSUFFICIENT_TIME_COLOR
    else:
        color = RECOMMENDED_COLOR if is_recommended else NON_RECOMMENDED_COLOR
    alpha = 0.8 if is_recommended else 0.4
    
    base_zorder = 5

    # Ensure periods is not None before iterating
    if periods is None:
        periods = []

    for period_start, period_end in periods:
        local_start = period_start.astimezone(local_tz)
        local_end = period_end.astimezone(local_tz)

        plot_start = max(local_start, start_time)
        plot_end = min(local_end, end_time)

        if plot_start >= plot_end: 
            continue

        # If object has moon influence periods, handle moon interference visualization
        if hasattr(obj, 'moon_influence_periods') and obj.moon_influence_periods:
            # First, draw the entire bar in normal color
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)
                   
            # Then overlay the moon interference segments
            for start_idx, end_idx in obj.moon_influence_periods:
                # Handle both integer indices and datetime objects
                if isinstance(start_idx, datetime) and isinstance(end_idx, datetime):
                    moon_start = start_idx
                    moon_end = end_idx
                elif isinstance(start_idx, int) and isinstance(end_idx, int):
                    # Convert indices to datetime (assuming 1-minute intervals)
                    moon_start = period_start + timedelta(minutes=start_idx)
                    moon_end = period_start + timedelta(minutes=end_idx)
                else:
                    continue  # Skip invalid entries
                
                # Convert to local time
                moon_start_local = moon_start.astimezone(local_tz)
                moon_end_local = moon_end.astimezone(local_tz)
                
                # Clip to plot boundaries
                moon_plot_start = max(moon_start_local, plot_start)
                moon_plot_end = min(moon_end_local, plot_end)
                
                if moon_plot_start < moon_plot_end:
                    # Use different colors for moon interference based on recommendation status
                    moon_color = MOON_INTERFERENCE_COLOR_RECOMMENDED if is_recommended else MOON_INTERFERENCE_COLOR_NON_RECOMMENDED
                    ax.barh(index, moon_plot_end - moon_plot_start, 
                           left=moon_plot_start, height=0.3,
                           alpha=0.9, color=moon_color, 
                           zorder=base_zorder + 1)
        else:
            # No moon interference - draw normal bar
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)

def _plot_scheduled_interval(ax, index, obj, scheduled_interval, start_time, end_time, use_margins):
    """Plot scheduled interval overlay with hatching"""
    local_tz = get_local_timezone()
    sched_start_local, sched_end_local = scheduled_interval
    
    # Get the object's actual visibility periods
    periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
    if not periods:
        return  # Skip if no visibility periods
        
    # Find the actual period that contains this scheduled time
    containing_period = None
    for p_start, p_end in periods:
        local_p_start = p_start.astimezone(local_tz)
        local_p_end = p_end.astimezone(local_tz)
        
        # Check if this period contains the scheduled interval
        if (local_p_start <= sched_end_local and 
            local_p_end >= sched_start_local):
            containing_period = (local_p_start, local_p_end)
            break
            
    if not containing_period:
        return  # No containing period found
        
    # Ensure the scheduled interval is within bounds
    plot_start = max(sched_start_local, start_time, containing_period[0])
    plot_end = min(sched_end_local, end_time, containing_period[1])
    
    if plot_start < plot_end:  # Only plot if there's a non-zero duration
        ax.barh(index, plot_end - plot_start, 
                left=plot_start, 
                height=0.35,  # Slightly taller than visibility bars
                color='none',  # Make base transparent
                edgecolor=SCHEDULED_COLOR,
                hatch='///',  # Hashing pattern
                linewidth=1.0,
                alpha=0.9,
                zorder=9)  # Above the base bars but below labels

def _setup_object_labels(ax, sorted_objects):
    """Setup Y-axis labels for objects"""
    ax.set_yticks(range(len(sorted_objects)))
    
    # Use custom display names that handle mosaic groups specially
    display_names = []
    for obj in sorted_objects:
        if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
            # For mosaic groups, show abbreviated names of individual objects
            abbreviated_names = [get_abbreviated_name(individual_obj.name)
                                 for individual_obj in obj.objects]
            if len(abbreviated_names) <= 3:
                display_names.append(', '.join(abbreviated_names))
            else:
                display_names.append(f"{', '.join(abbreviated_names[:2])} +{len(abbreviated_names)-2}")
        else:
            # For individual objects, use the standard abbreviated name
            display_names.append(get_abbreviated_name(obj.name))
    
    ax.set_yticklabels(display_names)

def _add_visibility_chart_legend(ax, schedule, sorted_objects):
    """Add comprehensive legend for visibility chart"""
    legend_handles = []
    
    # Moon interference legend entry
    moon_handle = Patch(facecolor=MOON_INTERFERENCE_COLOR_RECOMMENDED, alpha=0.8, 
                        label='Moon Interference')
    legend_handles.append(moon_handle)
    
    # Scheduled observations legend entry
    if schedule:
        sched_handle = Patch(facecolor='none', edgecolor=SCHEDULED_COLOR, 
                           hatch='///', alpha=0.9, label='Scheduled Observation')
        legend_handles.append(sched_handle)
    
    # Insufficient time legend entry
    if any(not getattr(obj, 'sufficient_time', True) for obj in sorted_objects):
        insuf_handle = Patch(facecolor=INSUFFICIENT_TIME_COLOR, alpha=0.4, 
                           label='Insufficient Time')
        legend_handles.append(insuf_handle)
    
    # Recommended vs non-recommended
    rec_handle = Patch(facecolor=RECOMMENDED_COLOR, alpha=0.8, label='Recommended')
    legend_handles.append(rec_handle)
    
    non_rec_handle = Patch(facecolor=NON_RECOMMENDED_COLOR, alpha=0.4, 
                          label='Non-Recommended')
    legend_handles.append(non_rec_handle)
    
    # Add the legend
    if legend_handles:
        ax.legend(handles=legend_handles, loc='lower left', fontsize=10)

# All astronomical calculation functions are now properly imported from astronomy module 