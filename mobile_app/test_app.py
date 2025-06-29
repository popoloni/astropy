#!/usr/bin/env python3
"""
Test script for AstroScope Planner mobile app
Verifies imports and basic functionality without running the full GUI
"""

import sys
import os
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test astropy modules
        print("  Testing astropy modules...")
        from astronightplanner import filter_visible_objects, generate_observation_schedule
        from astronomy import calculate_altaz, find_visibility_window
        from analysis import calculate_object_score, create_mosaic_groups
        print("  ✓ Astropy modules imported successfully")
        
        # Test app modules
        print("  Testing app modules...")
        from utils.app_state import AppState
        from utils.location_manager import LocationManager
        print("  ✓ App utility modules imported successfully")
        
        # Test screen modules (without Kivy)
        print("  Testing screen modules...")
        # Note: These will fail without Kivy, but we can test the imports
        try:
            from screens.home_screen import HomeScreen
            from screens.targets_screen import TargetsScreen
            from screens.target_detail_screen import TargetDetailScreen
            from screens.mosaic_screen import MosaicScreen
            from screens.settings_screen import SettingsScreen
            print("  ✓ Screen modules imported successfully")
        except ImportError as e:
            if "kivy" in str(e).lower():
                print("  ⚠ Screen modules require Kivy (expected in test environment)")
            else:
                raise
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_app_state():
    """Test app state functionality"""
    print("\nTesting app state...")
    
    try:
        from utils.app_state import AppState
        
        # Create app state
        app_state = AppState()
        
        # Test properties
        assert hasattr(app_state, 'tonights_targets')
        assert hasattr(app_state, 'current_location')
        assert hasattr(app_state, 'scheduling_strategy')
        
        # Test methods
        assert callable(app_state.get_strategy_display_name)
        assert callable(app_state.get_session_stats)
        
        # Test strategy display names
        strategies = ['max_objects', 'longest_duration', 'optimal_snr']
        for strategy in strategies:
            display_name = app_state.get_strategy_display_name(strategy)
            assert isinstance(display_name, str)
            assert len(display_name) > 0
        
        print("  ✓ App state functionality working")
        return True
        
    except Exception as e:
        print(f"  ✗ App state test failed: {e}")
        traceback.print_exc()
        return False

def test_location_manager():
    """Test location manager functionality"""
    print("\nTesting location manager...")
    
    try:
        from utils.location_manager import LocationManager
        
        # Create location manager
        location_manager = LocationManager()
        
        # Test methods
        assert callable(location_manager.get_location_names)
        assert callable(location_manager.validate_coordinates)
        assert callable(location_manager.get_default_location)
        
        # Test coordinate validation
        valid, message, lat, lon = location_manager.validate_coordinates("45.5", "9.2")
        assert valid == True
        assert lat == 45.5
        assert lon == 9.2
        
        # Test invalid coordinates
        valid, message, lat, lon = location_manager.validate_coordinates("invalid", "9.2")
        assert valid == False
        
        # Test location names
        names = location_manager.get_location_names()
        assert isinstance(names, list)
        assert len(names) > 0
        
        print("  ✓ Location manager functionality working")
        return True
        
    except Exception as e:
        print(f"  ✗ Location manager test failed: {e}")
        traceback.print_exc()
        return False

def test_astropy_integration():
    """Test integration with astropy modules"""
    print("\nTesting astropy integration...")
    
    try:
        from datetime import datetime, timedelta
        from astronightplanner import find_astronomical_twilight
        from astronomy import filter_visible_objects
        from catalogs import get_objects_from_catalog, get_catalog_info
        
        # Get catalog using new configurable system
        catalog_info = get_catalog_info()
        all_objects = get_objects_from_catalog()
        print(f"  ✓ Using {catalog_info['type']} catalog ({catalog_info['source']})")
        assert isinstance(all_objects, list)
        assert len(all_objects) > 0
        print(f"  ✓ Loaded {len(all_objects)} objects from catalog")
        
        # Test twilight calculation
        current_date = datetime.now()
        twilight_times = find_astronomical_twilight(current_date)
        
        if twilight_times:
            start_time, end_time = twilight_times
            
            # Test filtering with correct signature
            visible_objects, insufficient_objects = filter_visible_objects(
                all_objects, start_time, end_time
            )
            
            assert isinstance(visible_objects, list)
            assert isinstance(insufficient_objects, list)
            print(f"  ✓ Found {len(visible_objects)} visible objects, {len(insufficient_objects)} insufficient")
            
            # Test object scoring
            if visible_objects:
                from analysis import calculate_object_score
                from astronomy import find_visibility_window
                
                first_object = visible_objects[0]
                # Get visibility periods for scoring
                periods = find_visibility_window(first_object, start_time, end_time)
                if periods:
                    score = calculate_object_score(first_object, periods)
                    assert isinstance(score, (int, float))
                    print(f"  ✓ Object scoring working (sample score: {score:.1f})")
                else:
                    print("  ⚠ No visibility periods found for scoring test")
        else:
            print("  ⚠ No twilight times available (expected during polar day/night)")
        
        print("  ✓ Astropy integration working")
        return True
        
    except Exception as e:
        print(f"  ✗ Astropy integration test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'buildozer.spec',
        'README.md',
        'utils/__init__.py',
        'utils/app_state.py',
        'utils/location_manager.py',
        'screens/__init__.py',
        'screens/home_screen.py',
        'screens/targets_screen.py',
        'screens/target_detail_screen.py',
        'screens/mosaic_screen.py',
        'screens/settings_screen.py',
        'widgets/__init__.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"  ✗ Missing files: {missing_files}")
        return False
    else:
        print(f"  ✓ All {len(required_files)} required files present")
        return True

def main():
    """Run all tests"""
    print("AstroScope Planner Mobile App - Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_app_state,
        test_location_manager,
        test_astropy_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! App structure is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())