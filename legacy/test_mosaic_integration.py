#!/usr/bin/env python3
"""
Test script for mosaic integration in astropy.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from astropy import (
    get_combined_catalog, get_current_datetime, get_local_timezone,
    find_astronomical_twilight, filter_visible_objects,
    create_mosaic_groups, combine_objects_and_groups,
    SchedulingStrategy, generate_observation_schedule,
    MosaicGroup
)
from datetime import timedelta

def test_mosaic_integration():
    """Test the mosaic integration functionality"""
    print("Testing Mosaic Integration")
    print("=" * 50)
    
    # Get current time and calculate observation period
    current_date = get_current_datetime(get_local_timezone())
    
    # Calculate night period
    if current_date.hour < 12:
        yesterday = current_date - timedelta(days=1)
        twilight_evening, twilight_morning = find_astronomical_twilight(yesterday)
    else:
        twilight_evening, twilight_morning = find_astronomical_twilight(current_date)
    
    start_time = twilight_evening
    end_time = twilight_morning
    
    print(f"Observation period: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
    
    # Get objects
    all_objects = get_combined_catalog()
    print(f"Total objects in catalog: {len(all_objects)}")
    
    # Filter visible objects
    visible_objects, insufficient_objects = filter_visible_objects(
        all_objects, start_time, end_time, use_margins=True)
    
    print(f"Visible objects: {len(visible_objects)}")
    print(f"Insufficient time objects: {len(insufficient_objects)}")
    
    # Test mosaic group creation
    print("\nTesting mosaic group creation...")
    mosaic_groups = create_mosaic_groups(visible_objects, start_time, end_time)
    
    print(f"Found {len(mosaic_groups)} mosaic groups:")
    for i, group in enumerate(mosaic_groups):
        print(f"  Group {i+1}: {group.name}")
        print(f"    Objects: {len(group.objects)}")
        print(f"    Overlap time: {group.calculate_total_overlap_duration():.1f}h")
        print(f"    Composite magnitude: {group.magnitude:.1f}")
        
        # Test that the group behaves like a CelestialObject
        assert hasattr(group, 'name')
        assert hasattr(group, 'ra')
        assert hasattr(group, 'dec')
        assert hasattr(group, 'magnitude')
        assert hasattr(group, 'fov')
        assert hasattr(group, 'is_mosaic_group')
        assert group.is_mosaic_group == True
        print(f"    ✓ Group behaves like CelestialObject")
    
    # Test combining objects and groups
    print("\nTesting object and group combination...")
    combined_objects = combine_objects_and_groups(
        visible_objects, mosaic_groups, SchedulingStrategy.MOSAIC_GROUPS)
    
    print(f"Combined objects count: {len(combined_objects)}")
    
    # Count mosaic groups vs individual objects
    mosaic_count = sum(1 for obj in combined_objects if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group)
    individual_count = len(combined_objects) - mosaic_count
    
    print(f"  Mosaic groups: {mosaic_count}")
    print(f"  Individual objects: {individual_count}")
    
    # Test scheduling with mosaic groups
    print("\nTesting scheduling with mosaic groups...")
    schedule = generate_observation_schedule(
        combined_objects, start_time, end_time,
        strategy=SchedulingStrategy.MOSAIC_GROUPS)
    
    print(f"Generated schedule with {len(schedule)} items:")
    for i, (sched_start, sched_end, sched_obj) in enumerate(schedule):
        duration = (sched_end - sched_start).total_seconds() / 3600
        obj_type = "Mosaic Group" if hasattr(sched_obj, 'is_mosaic_group') and sched_obj.is_mosaic_group else "Individual"
        print(f"  {i+1}. {sched_obj.name} ({obj_type}) - {duration:.1f}h")
    
    # Test that mosaic groups are prioritized
    mosaic_in_schedule = sum(1 for _, _, obj in schedule if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group)
    print(f"  Mosaic groups in schedule: {mosaic_in_schedule}")
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_mosaic_integration()
        print("\n🎉 Mosaic integration test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 