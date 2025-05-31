"""
Observation scheduling and object combination functions.
"""

import math
from datetime import timedelta
from models import SchedulingStrategy
from astronomy import find_visibility_window, calculate_visibility_duration, calculate_required_exposure


def generate_observation_schedule(objects, start_time, end_time, 
                                strategy=SchedulingStrategy.LONGEST_DURATION,
                                min_duration=None,
                                max_overlap=None):
    """Generate optimal observation schedule based on selected strategy"""
    from config.settings import SCHEDULING_STRATEGY, MIN_VISIBILITY_HOURS, MAX_OVERLAP_MINUTES, EXCLUDE_INSUFFICIENT_TIME, BORTLE_INDEX
    from .object_selection import calculate_object_score
    
    # Use config defaults if not provided
    if strategy is None:
        strategy = SCHEDULING_STRATEGY
    if min_duration is None:
        min_duration = MIN_VISIBILITY_HOURS
    if max_overlap is None:
        max_overlap = MAX_OVERLAP_MINUTES
    
    schedule = []

    # Filter out objects affected by the moon, but only if we have alternatives
    objects_no_moon = [obj for obj in objects if not getattr(obj, 'near_moon', False)]
    
    # If we have no objects clear from the moon, use all objects
    if not objects_no_moon:
        objects_no_moon = objects

    # Filter objects based on sufficient time if needed (applied after moon filter)
    if EXCLUDE_INSUFFICIENT_TIME:
        objects_filtered = [obj for obj in objects_no_moon if getattr(obj, 'sufficient_time', True)]
    else:
        objects_filtered = objects_no_moon

    # Calculate scores and periods for all remaining objects
    object_data = []
    for obj in objects_filtered:
        # *** IMPORTANT: Skip objects without magnitude EARLY to prevent errors ***
        if obj.magnitude is None:
            print(f"Skipping {obj.name} for scheduling due to missing magnitude.")
            continue # Skip objects without magnitude for scheduling

        periods = find_visibility_window(obj, start_time, end_time, use_margins=True)
        if periods:
            duration = calculate_visibility_duration(periods)
            if duration >= min_duration:
                exposure_time, frames, panels = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)

                # Check if we need to exclude based on insufficient time again,
                # even if EXCLUDE_INSUFFICIENT_TIME is False, MAX_OBJECTS needs this check.
                has_enough_time_for_exposure = (duration >= exposure_time)

                # Only add if it meets basic duration and potentially exposure time criteria
                if not EXCLUDE_INSUFFICIENT_TIME or has_enough_time_for_exposure:
                    # Now it's safe to calculate the score
                    score = calculate_object_score(obj, periods, strategy)
                    # Store exposure_time needed, especially for MAX_OBJECTS strategy
                    object_data.append((obj, periods, duration, score, exposure_time))

    # Sort by score according to strategy
    object_data.sort(key=lambda x: x[3], reverse=True)

    # Schedule observations based on strategy
    scheduled_times = [] # This will store tuples of (start_time, end_time, object)

    if strategy == SchedulingStrategy.MAX_OBJECTS:
        # --- Greedy Algorithm for MAX_OBJECTS with Multiple Potential Slots --- 
        
        # Configure sampling interval for potential slots (minutes)
        sampling_interval_minutes = 15
        sampling_interval = timedelta(minutes=sampling_interval_minutes)
        
        # Max allowable idle time between observations
        max_idle_time = timedelta(minutes=15)

        # 1. Generate Multiple Potential Slots throughout visibility periods
        potential_slots = []
        for obj, periods, duration, score, exposure_time in object_data:
            # Basic validity checks
            if duration < exposure_time or exposure_time <= 0:
                continue
            if not isinstance(exposure_time, (int, float)) or math.isinf(exposure_time) or math.isnan(exposure_time):
                continue
                
            try:
                needed_duration = timedelta(hours=exposure_time)
            except OverflowError:
                continue
                
            # For each visibility period, generate multiple potential start times
            for period_start, period_end in periods:
                # Calculate the latest possible start time that allows full observation
                latest_start = period_end - needed_duration
                
                # If the period isn't long enough for the needed duration, skip it
                if latest_start < period_start:
                    continue
                    
                # Generate potential slots at regular intervals throughout the period
                current_start = period_start
                while current_start <= latest_start:
                    potential_end = current_start + needed_duration
                    
                    # Add this potential slot
                    potential_slots.append({
                        'start': current_start,
                        'end': potential_end,
                        'obj': obj,
                        'duration': needed_duration,
                        'score': score  # Keep track of the original score
                    })
                    
                    # Move to the next potential start time
                    current_start += sampling_interval

        # 2. Sort Potential Slots 
        # First by finish time (primary), then by score (secondary)
        potential_slots.sort(key=lambda x: (x['end'], -x['score']))
        
        # 3. Modified Greedy Selection with ZERO tolerance for overlaps
        scheduled_times = []
        scheduled_objects = set()
        
        for slot in potential_slots:
            s_start = slot['start']
            s_end = slot['end']
            s_obj = slot['obj']
            
            # Skip if object already scheduled
            if s_obj in scheduled_objects:
                continue
                
            # Check for ANY conflicts with existing schedule
            is_conflicting = False
            for sched_start, sched_end, _ in scheduled_times:
                # Check if there's any overlap at all (strict check)
                if (s_start < sched_end and s_end > sched_start):
                    is_conflicting = True
                    break
            
            # If no conflict, add this slot
            if not is_conflicting:
                scheduled_times.append((s_start, s_end, s_obj))
                scheduled_objects.add(s_obj)
        
        # 4. Sort the schedule by start time
        scheduled_times.sort(key=lambda x: x[0])
        
        # 5. Try to minimize gaps by adjusting start times (post-processing)
        if len(scheduled_times) > 1:
            optimized_schedule = [scheduled_times[0]]  # Keep the first item as is
            
            for i in range(1, len(scheduled_times)):
                prev_end = optimized_schedule[-1][1]
                curr_start, curr_end, curr_obj = scheduled_times[i]
                curr_duration = curr_end - curr_start
                
                # Calculate the gap
                gap = curr_start - prev_end
                
                # If gap is larger than max_idle_time, try to move the current observation earlier
                if gap > max_idle_time:
                    # The earliest we can start is immediately after the previous observation ends
                    earliest_possible_start = prev_end
                    
                    # Calculate how much we can shift this observation earlier
                    shift_amount = min(gap, curr_start - earliest_possible_start)
                    
                    if shift_amount > timedelta(0):
                        # Adjust the start and end times
                        adjusted_start = curr_start - shift_amount
                        adjusted_end = adjusted_start + curr_duration  # Preserve duration
                        
                        # Verify no conflicts with any earlier observations
                        has_conflict = False
                        for idx in range(len(optimized_schedule)):
                            prev_start, prev_end, _ = optimized_schedule[idx]
                            # Check for any overlap (strict check)
                            if (adjusted_start < prev_end and adjusted_end > prev_start):
                                has_conflict = True
                                break
                        
                        if not has_conflict:
                            # Add the adjusted observation to the schedule
                            optimized_schedule.append((adjusted_start, adjusted_end, curr_obj))
                        else:
                            # Conflict found, use original times
                            optimized_schedule.append((curr_start, curr_end, curr_obj))
                    else:
                        # Can't shift, use original times
                        optimized_schedule.append((curr_start, curr_end, curr_obj))
                else:
                    # Gap is acceptable, use original times
                    optimized_schedule.append((curr_start, curr_end, curr_obj))
            
            # Replace the original schedule with the optimized one
            scheduled_times = optimized_schedule
            
        # 6. Final validation to ensure NO overlaps in the final schedule
        if len(scheduled_times) > 1:
            # Sort again to ensure proper ordering
            scheduled_times.sort(key=lambda x: x[0])
            
            # Check for any remaining overlaps and fix if needed
            validated_schedule = [scheduled_times[0]]
            
            for i in range(1, len(scheduled_times)):
                curr_slot = scheduled_times[i]
                curr_start, curr_end, curr_obj = curr_slot
                
                # Check for conflict with all previous validated slots
                has_conflict = False
                for prev_start, prev_end, _ in validated_schedule:
                    # If there's ANY overlap, it's a conflict
                    if (curr_start < prev_end and curr_end > prev_start):
                        has_conflict = True
                        break
                
                # Only add if no conflict
                if not has_conflict:
                    validated_schedule.append(curr_slot)
            
            # Use the final validated schedule
            scheduled_times = validated_schedule
    
    # For strategies other than MAX_OBJECTS, implement similar but simpler logic
    else:
        # Sort objects by score for this strategy
        object_data.sort(key=lambda x: x[3], reverse=True)
        
        # Greedily schedule objects without overlap
        for obj, periods, duration, score, exposure_time in object_data:
            # Skip invalid exposure times
            if not isinstance(exposure_time, (int, float)) or math.isinf(exposure_time) or math.isnan(exposure_time):
                continue
                
            try:
                needed_duration = timedelta(hours=exposure_time)
            except OverflowError:
                continue
                
            # Find best visibility period
            best_period = None
            for period_start, period_end in periods:
                period_duration = period_end - period_start
                if period_duration >= needed_duration:
                    # This period can fit the object
                    best_period = (period_start, period_end)
                    break
            
            if not best_period:
                continue
                
            # Check if object overlaps with existing schedule
            start_time = best_period[0]
            end_time = start_time + needed_duration
            
            # Check for overlap
            has_overlap = False
            for sched_start, sched_end, _ in scheduled_times:
                if end_time > sched_start and start_time < sched_end:
                    has_overlap = True
                    break
            
            if not has_overlap:
                scheduled_times.append((start_time, end_time, obj))
    
    # Return the final schedule
    return scheduled_times


def combine_objects_and_groups(individual_objects, mosaic_groups, strategy=SchedulingStrategy.LONGEST_DURATION, no_duplicates=False):
    """Combine individual objects and mosaic groups based on strategy"""
    # Find objects that are in mosaic groups
    grouped_object_names = set()
    for group in mosaic_groups:
        for obj in group.objects:
            grouped_object_names.add(obj.name)
    
    if strategy == SchedulingStrategy.MOSAIC_GROUPS or no_duplicates:
        # Prioritize mosaic groups, add individual objects only if they don't conflict
        combined = list(mosaic_groups)
        
        # Add ungrouped individual objects only
        filtered_objects = []
        for obj in individual_objects:
            if obj.name not in grouped_object_names:
                filtered_objects.append(obj)
        
        combined.extend(filtered_objects)
        
        return combined
    else:
        # For other strategies without no_duplicates, include all objects and groups
        return individual_objects + mosaic_groups 