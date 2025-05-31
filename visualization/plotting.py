"""
Core plotting functions for trajectory and visibility charts.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
import pytz
from datetime import datetime, timedelta

from astronomy import (
    calculate_altaz, calculate_moon_position, utc_to_local, is_visible,
    find_visibility_window, calculate_visibility_duration, is_near_moon
)
from config.settings import *


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
    import re
    
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