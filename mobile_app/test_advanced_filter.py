#!/usr/bin/env python3
"""
Test script for Advanced Filtering System
Validates the filtering functionality with sample data
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.advanced_filter import AdvancedFilter, FilterPresetManager, FilterOperator, FilterCriteria
    print("✓ Advanced filter imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def create_sample_targets():
    """Create sample target data for testing"""
    return [
        {
            'name': 'M31 Andromeda Galaxy',
            'magnitude': 3.4,
            'size': 190.0,
            'object_type': 'galaxy',
            'constellation': 'Andromeda',
            'max_altitude': 75.0,
            'visibility_hours': 6.0,
            'moon_separation_deg': 45.0,
            'recommended_focal_length': 600.0,
            'surface_brightness': 13.5,
            'recommended_exposure_time': 300.0,
            'required_pixel_scale': 2.5
        },
        {
            'name': 'M42 Orion Nebula',
            'magnitude': 4.0,
            'size': 85.0,
            'object_type': 'nebula',
            'constellation': 'Orion',
            'max_altitude': 65.0,
            'visibility_hours': 4.0,
            'moon_separation_deg': 60.0,
            'recommended_focal_length': 1000.0,
            'surface_brightness': 17.0,
            'recommended_exposure_time': 180.0,
            'required_pixel_scale': 1.8
        },
        {
            'name': 'NGC 7293 Helix Nebula',
            'magnitude': 7.3,
            'size': 16.0,
            'object_type': 'planetary_nebula',
            'constellation': 'Aquarius',
            'max_altitude': 45.0,
            'visibility_hours': 3.0,
            'moon_separation_deg': 25.0,
            'recommended_focal_length': 1500.0,
            'surface_brightness': 20.5,
            'recommended_exposure_time': 600.0,
            'required_pixel_scale': 1.2
        },
        {
            'name': 'M45 Pleiades',
            'magnitude': 1.6,
            'size': 110.0,
            'object_type': 'cluster',
            'constellation': 'Taurus',
            'max_altitude': 80.0,
            'visibility_hours': 5.0,
            'moon_separation_deg': 90.0,
            'recommended_focal_length': 400.0,
            'surface_brightness': 15.0,
            'recommended_exposure_time': 120.0,
            'required_pixel_scale': 3.0
        },
        {
            'name': 'NGC 2237 Rosette Nebula',
            'magnitude': 9.0,
            'size': 80.0,
            'object_type': 'nebula',
            'constellation': 'Monoceros',
            'max_altitude': 55.0,
            'visibility_hours': 4.5,
            'moon_separation_deg': 35.0,
            'recommended_focal_length': 800.0,
            'surface_brightness': 18.5,
            'recommended_exposure_time': 450.0,
            'required_pixel_scale': 2.0
        },
        {
            'name': 'M87 Virgo Galaxy',
            'magnitude': 8.6,
            'size': 8.3,
            'object_type': 'galaxy',
            'constellation': 'Virgo',
            'max_altitude': 70.0,
            'visibility_hours': 3.5,
            'moon_separation_deg': 50.0,
            'recommended_focal_length': 2000.0,
            'surface_brightness': 21.0,
            'recommended_exposure_time': 900.0,
            'required_pixel_scale': 1.0
        }
    ]


def test_basic_filtering():
    """Test basic filtering functionality"""
    print("\n=== Testing Basic Filtering ===")
    
    targets = create_sample_targets()
    filter_obj = AdvancedFilter()
    
    # Test magnitude filtering
    filter_obj.magnitude_range = (0.0, 5.0)
    filtered = filter_obj.apply_filters(targets)
    bright_targets = [t['name'] for t in filtered]
    print(f"Magnitude 0-5: {len(filtered)} targets - {bright_targets}")
    
    # Test object type filtering
    filter_obj.magnitude_range = (0.0, 15.0)  # Reset
    filter_obj.object_types = ['nebula']
    filtered = filter_obj.apply_filters(targets)
    nebula_targets = [t['name'] for t in filtered]
    print(f"Nebulae only: {len(filtered)} targets - {nebula_targets}")
    
    # Test size filtering
    filter_obj.object_types = ['galaxy', 'nebula', 'cluster']  # Reset
    filter_obj.size_range = (50.0, 200.0)
    filtered = filter_obj.apply_filters(targets)
    large_targets = [t['name'] for t in filtered]
    print(f"Size 50-200 arcmin: {len(filtered)} targets - {large_targets}")
    
    return True


def test_advanced_filtering():
    """Test advanced filtering functionality"""
    print("\n=== Testing Advanced Filtering ===")
    
    targets = create_sample_targets()
    filter_obj = AdvancedFilter()
    
    # Test altitude filtering
    filter_obj.altitude_range = (60.0, 90.0)
    filtered = filter_obj.apply_filters(targets)
    high_targets = [t['name'] for t in filtered]
    print(f"High altitude (60-90°): {len(filtered)} targets - {high_targets}")
    
    # Test visibility hours filtering
    filter_obj.altitude_range = (0.0, 90.0)  # Reset
    filter_obj.visibility_hours_min = 4.0
    filtered = filter_obj.apply_filters(targets)
    long_visible = [t['name'] for t in filtered]
    print(f"Visible >4 hours: {len(filtered)} targets - {long_visible}")
    
    # Test moon avoidance
    filter_obj.visibility_hours_min = 0.0  # Reset
    filter_obj.moon_avoidance = True
    filtered = filter_obj.apply_filters(targets)
    moon_safe = [t['name'] for t in filtered]
    print(f"Moon avoidance: {len(filtered)} targets - {moon_safe}")
    
    return True


def test_imaging_difficulty():
    """Test imaging difficulty assessment"""
    print("\n=== Testing Imaging Difficulty ===")
    
    targets = create_sample_targets()
    filter_obj = AdvancedFilter()
    
    # Test beginner difficulty
    filter_obj.imaging_difficulty = 'beginner'
    filtered = filter_obj.apply_filters(targets)
    beginner_targets = [t['name'] for t in filtered]
    print(f"Beginner difficulty: {len(filtered)} targets - {beginner_targets}")
    
    # Test advanced difficulty
    filter_obj.imaging_difficulty = 'advanced'
    filtered = filter_obj.apply_filters(targets)
    advanced_targets = [t['name'] for t in filtered]
    print(f"Advanced difficulty: {len(filtered)} targets - {advanced_targets}")
    
    # Show difficulty scores for all targets
    print("\nDifficulty scores:")
    for target in targets:
        score = filter_obj._calculate_imaging_difficulty_score(target)
        print(f"  {target['name']}: {score:.1f}")
    
    return True


def test_custom_criteria():
    """Test custom filter criteria"""
    print("\n=== Testing Custom Criteria ===")
    
    targets = create_sample_targets()
    filter_obj = AdvancedFilter()
    
    # Add custom criteria for constellation
    filter_obj.add_custom_criteria('constellation', FilterOperator.EQUALS, 'Orion')
    filtered = filter_obj.apply_filters(targets)
    orion_targets = [t['name'] for t in filtered]
    print(f"Orion constellation: {len(filtered)} targets - {orion_targets}")
    
    # Add custom criteria for exposure time
    filter_obj.remove_custom_criteria('constellation')
    filter_obj.add_custom_criteria('recommended_exposure_time', FilterOperator.LESS_THAN, 300)
    filtered = filter_obj.apply_filters(targets)
    short_exposure = [t['name'] for t in filtered]
    print(f"Exposure <300s: {len(filtered)} targets - {short_exposure}")
    
    # Test range criteria
    filter_obj.remove_custom_criteria('recommended_exposure_time')
    filter_obj.add_custom_criteria('magnitude', FilterOperator.BETWEEN, (3.0, 8.0))
    filtered = filter_obj.apply_filters(targets)
    mid_mag = [t['name'] for t in filtered]
    print(f"Magnitude 3-8: {len(filtered)} targets - {mid_mag}")
    
    return True


def test_presets():
    """Test filter presets"""
    print("\n=== Testing Filter Presets ===")
    
    targets = create_sample_targets()
    preset_manager = FilterPresetManager()
    
    # Test built-in presets
    presets = preset_manager.list_presets()
    print(f"Available presets: {presets}")
    
    # Test beginner preset
    beginner_preset = preset_manager.get_preset('beginner')
    if beginner_preset:
        filter_obj = AdvancedFilter()
        filter_obj.load_preset(beginner_preset)
        filtered = filter_obj.apply_filters(targets)
        beginner_targets = [t['name'] for t in filtered]
        print(f"Beginner preset: {len(filtered)} targets - {beginner_targets}")
    
    # Test deep sky preset
    deep_sky_preset = preset_manager.get_preset('deep_sky')
    if deep_sky_preset:
        filter_obj = AdvancedFilter()
        filter_obj.load_preset(deep_sky_preset)
        filtered = filter_obj.apply_filters(targets)
        deep_sky_targets = [t['name'] for t in filtered]
        print(f"Deep sky preset: {len(filtered)} targets - {deep_sky_targets}")
    
    # Test saving custom preset
    filter_obj = AdvancedFilter()
    filter_obj.magnitude_range = (1.0, 6.0)
    filter_obj.object_types = ['cluster', 'nebula']
    custom_preset = filter_obj.save_preset('custom_test')
    print(f"Saved custom preset: {custom_preset['name']}")
    
    return True


def test_filter_combinations():
    """Test complex filter combinations"""
    print("\n=== Testing Filter Combinations ===")
    
    targets = create_sample_targets()
    filter_obj = AdvancedFilter()
    
    # Complex filter: bright nebulae with good visibility
    filter_obj.magnitude_range = (0.0, 8.0)
    filter_obj.object_types = ['nebula']
    filter_obj.visibility_hours_min = 3.0
    filter_obj.moon_avoidance = True
    
    filtered = filter_obj.apply_filters(targets)
    complex_targets = [t['name'] for t in filtered]
    print(f"Bright nebulae, >3h visible, moon-safe: {len(filtered)} targets - {complex_targets}")
    
    # Test AND vs OR logic
    filter_obj.combine_with_and = False  # Use OR logic
    filter_obj.magnitude_range = (0.0, 2.0)  # Very bright
    filter_obj.size_range = (100.0, 200.0)  # Very large
    
    filtered = filter_obj.apply_filters(targets)
    or_targets = [t['name'] for t in filtered]
    print(f"Very bright OR very large (OR logic): {len(filtered)} targets - {or_targets}")
    
    filter_obj.combine_with_and = True  # Use AND logic
    filtered = filter_obj.apply_filters(targets)
    and_targets = [t['name'] for t in filtered]
    print(f"Very bright AND very large (AND logic): {len(filtered)} targets - {and_targets}")
    
    return True


def test_filter_summary():
    """Test filter summary and settings"""
    print("\n=== Testing Filter Summary ===")
    
    filter_obj = AdvancedFilter()
    filter_obj.magnitude_range = (5.0, 12.0)
    filter_obj.object_types = ['galaxy', 'nebula']
    filter_obj.imaging_difficulty = 'intermediate'
    filter_obj.add_custom_criteria('constellation', FilterOperator.IN, ['Orion', 'Andromeda'])
    
    summary = filter_obj.get_filter_summary()
    print("Filter summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return True


def run_all_tests():
    """Run all filter tests"""
    print("Advanced Filtering System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Filtering", test_basic_filtering),
        ("Advanced Filtering", test_advanced_filtering),
        ("Imaging Difficulty", test_imaging_difficulty),
        ("Custom Criteria", test_custom_criteria),
        ("Filter Presets", test_presets),
        ("Filter Combinations", test_filter_combinations),
        ("Filter Summary", test_filter_summary)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name} - PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} - FAILED")
        except Exception as e:
            print(f"✗ {test_name} - ERROR: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Advanced filtering system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)