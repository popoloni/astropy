"""
Common utility functions for plotting modules.

This module provides shared utility functions used across different plotting
modules for consistent behavior and code reuse.
"""

import re
import math
from typing import List, Tuple, Optional, Any

def get_abbreviated_name(full_name, max_length=12):
    """
    Get abbreviated name (catalog designation) from full name.
    
    Parameters:
    -----------
    full_name : str
        Full object name
    max_length : int, optional
        Maximum length for abbreviation
        
    Returns:
    --------
    str
        Abbreviated name
    """
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
        return f"SH2-{sh2_match.group(1)}"
    
    # Then try SH number
    sh_match = re.match(r'SH\s*(\d+)', full_name)
    if sh_match:
        return f"SH{sh_match.group(1)}"
        
    # Then try Barnard number
    b_match = re.match(r'B\s*(\d+)', full_name)
    if b_match:
        return f"B{b_match.group(1)}"
    
    # Then try Gum number
    gum_match = re.match(r'Gum\s*(\d+)', full_name)
    if gum_match:
        return f"GUM{gum_match.group(1)}"
    
    # If no catalog number found, return first word (truncated if needed)
    first_word = full_name.split()[0]
    return first_word[:max_length] if len(first_word) > max_length else first_word

def calculate_label_offset(trajectory_az, trajectory_alt, trajectory_idx, azimuths, altitudes):
    """
    Calculate smart offset for label based on trajectory direction.
    
    Parameters:
    -----------
    trajectory_az : float
        Azimuth at label position
    trajectory_alt : float
        Altitude at label position
    trajectory_idx : int
        Index in trajectory arrays
    azimuths : list
        List of azimuth values
    altitudes : list
        List of altitude values
        
    Returns:
    --------
    tuple
        (offset_x, offset_y) in points
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
            
            # Ensure minimum offset
            if abs(offset_x) < 8:
                offset_x = 8 if offset_x >= 0 else -8
            if abs(offset_y) < 8:
                offset_y = 8 if offset_y >= 0 else -8
    
    return offset_x, offset_y

def find_optimal_label_position(azimuths, altitudes, hour_positions, existing_positions, 
                               existing_labels, margin=8):
    """
    Find optimal position for object label to avoid overlaps.
    
    Parameters:
    -----------
    azimuths : list
        List of azimuth values for trajectory
    altitudes : list
        List of altitude values for trajectory
    hour_positions : list
        List of (az, alt) tuples for hour markers
    existing_positions : list
        List of existing label positions
    existing_labels : list
        List of existing label texts
    margin : int, optional
        Minimum margin between labels
        
    Returns:
    --------
    tuple
        (best_az, best_alt, best_idx) for label position
    """
    if not azimuths or not altitudes:
        return None, None, None
    
    # Try positions along the trajectory
    best_position = None
    best_score = -1
    best_idx = None
    
    # Sample positions along trajectory
    step = max(1, len(azimuths) // 10)  # Sample ~10 positions
    
    for i in range(0, len(azimuths), step):
        az, alt = azimuths[i], altitudes[i]
        
        # Calculate score based on distance from existing positions
        score = 0
        
        # Check distance from existing labels
        for existing_az, existing_alt in existing_positions:
            distance = math.sqrt((az - existing_az)**2 + (alt - existing_alt)**2)
            if distance < margin:
                score -= 100  # Heavy penalty for overlap
            else:
                score += min(distance, 20)  # Bonus for distance, capped
        
        # Check distance from hour markers
        for hour_az, hour_alt in hour_positions:
            distance = math.sqrt((az - hour_az)**2 + (alt - hour_alt)**2)
            if distance < margin:
                score -= 50  # Penalty for being too close to hour markers
        
        # Prefer positions in the middle of the trajectory
        middle_idx = len(azimuths) // 2
        trajectory_position_score = 10 - abs(i - middle_idx) / len(azimuths) * 10
        score += trajectory_position_score
        
        if score > best_score:
            best_score = score
            best_position = (az, alt)
            best_idx = i
    
    if best_position:
        return best_position[0], best_position[1], best_idx
    else:
        # Fallback to middle position
        mid_idx = len(azimuths) // 2
        return azimuths[mid_idx], altitudes[mid_idx], mid_idx

def format_time_range(start_time, end_time, format_type='short'):
    """
    Format time range for display.
    
    Parameters:
    -----------
    start_time : datetime
        Start time
    end_time : datetime
        End time
    format_type : str, optional
        Format type ('short', 'long', 'mobile')
        
    Returns:
    --------
    str
        Formatted time range string
    """
    if format_type == 'mobile':
        return f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
    elif format_type == 'short':
        return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    else:  # long
        return f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"

def calculate_overlap_duration(periods):
    """
    Calculate total duration from overlap periods.
    
    Parameters:
    -----------
    periods : list
        List of (start_time, end_time) tuples
        
    Returns:
    --------
    float
        Total duration in hours
    """
    total_seconds = sum((end - start).total_seconds() for start, end in periods)
    return total_seconds / 3600

def validate_groups_for_plotting(groups, max_groups=None):
    """
    Validate and limit groups for plotting.
    
    Parameters:
    -----------
    groups : list
        List of groups to validate
    max_groups : int, optional
        Maximum number of groups to allow
        
    Returns:
    --------
    tuple
        (valid_groups, warnings) where warnings is a list of warning messages
    """
    warnings = []
    valid_groups = []
    
    if not groups:
        warnings.append("No groups provided")
        return valid_groups, warnings
    
    for i, group in enumerate(groups):
        # Check if group has objects
        objects = group.objects if hasattr(group, 'objects') else group
        if not objects:
            warnings.append(f"Group {i+1} has no objects")
            continue
        
        # Check if group has valid overlap periods
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        if not overlap_periods:
            warnings.append(f"Group {i+1} has no overlap periods")
        
        valid_groups.append(group)
        
        # Check group limit
        if max_groups and len(valid_groups) >= max_groups:
            remaining = len(groups) - i - 1
            if remaining > 0:
                warnings.append(f"Limited to {max_groups} groups ({remaining} groups excluded)")
            break
    
    return valid_groups, warnings

def create_color_palette(n_colors, palette_type='default'):
    """
    Create color palette for plotting.
    
    Parameters:
    -----------
    n_colors : int
        Number of colors needed
    palette_type : str, optional
        Type of palette ('default', 'mobile', 'high_contrast')
        
    Returns:
    --------
    list
        List of color strings
    """
    if palette_type == 'mobile':
        base_colors = ['#FF4444', '#4444FF', '#44FF44', '#FF44FF', '#FFAA44', '#44FFFF']
    elif palette_type == 'high_contrast':
        base_colors = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFFF00', '#00FFFF', '#FFA500', '#800080']
    else:  # default
        base_colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Extend palette if needed
    colors = []
    for i in range(n_colors):
        colors.append(base_colors[i % len(base_colors)])
    
    return colors

def finalize_plot_legend(ax):
    """
    Finalize plot legend with sorted entries, keeping special entries first.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes object to update legend for
    """
    # Get current handles and labels
    handles, labels = ax.get_legend_handles_labels()
    
    if not handles:
        return  # No legend items to process
    
    # Find indices of special entries
    special_entries = []
    regular_entries = []
    
    for i, label in enumerate(labels):
        if label in ['Visible Region', 'Moon']:
            special_entries.append((handles[i], label))
        else:
            regular_entries.append((handles[i], label))
    
    # Sort regular entries alphabetically
    regular_entries.sort(key=lambda x: x[1].lower())
    
    # Reconstruct lists with special entries first
    final_handles = []
    final_labels = []
    
    # Add special entries first (in specific order)
    for handle, label in special_entries:
        if label == 'Visible Region':
            final_handles.append(handle)
            final_labels.append(label)
    
    for handle, label in special_entries:
        if label == 'Moon':
            final_handles.append(handle)
            final_labels.append(label)
    
    # Add regular entries
    for handle, label in regular_entries:
        final_handles.append(handle)
        final_labels.append(label)
    
    # Update legend
    if final_handles:
        ax.legend(final_handles, final_labels,
                 bbox_to_anchor=(1.02, 1),
                 loc='upper left',
                 borderaxespad=0,
                 title='Objects and Conditions')
