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

# Import plotting functions from plots module
from plots import (
    setup_altaz_plot,
    plot_object_trajectory,
    plot_moon_trajectory,
    plot_visibility_chart,
    plot_quarterly_trajectories,
    get_abbreviated_name,
    calculate_label_offset,
    find_optimal_label_position,
    finalize_plot_legend
)

# Import mosaic functions from the plots.mosaic module
from plots.mosaic import (
    plot_mosaic_fov_indicator,
    calculate_group_center_position,
    plot_mosaic_group_trajectory,
    plot_mosaic_fov_at_optimal_time,
    create_mosaic_trajectory_plot,
    create_mosaic_grid_plot
)

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
# All plotting functions have been moved to plots module

# plot_object_trajectory has been moved to plots.trajectory module

# plot_visibility_chart has been moved to plots.visibility module

# All plotting functions have been moved to plots module

# calculate_object_score has been moved to analysis modules
# calculate_max_altitude has been moved to analysis modules
# create_mosaic_groups has been moved to analysis modules
# combine_objects_and_groups has been moved to analysis modules
# generate_observation_schedule has been moved to analysis modules
# print_combined_report has been moved to analysis modules
# print_schedule_strategy_report has been moved to analysis modules
# print_objects_by_type has been moved to analysis modules

# plot_quarterly_trajectories has been moved to plots.trajectory module
# plot_moon_trajectory_no_legend has been moved to plots.trajectory module  
# plot_object_trajectory_no_legend has been moved to plots.trajectory module

# ============= MOSAIC PLOTTING FUNCTIONS =============
# Mosaic plotting functions have been moved to plots.mosaic module

# Legacy function definition for backward compatibility
# All mosaic functions are now imported from plots.mosaic module above

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

