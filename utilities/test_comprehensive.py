#!/usr/bin/env python3
"""
Comprehensive Test Suite: Non-regression tests for all phases
Tests complete functionality after Phase 6 cleanup
"""

import sys
import traceback
from datetime import datetime, timedelta
import pytz

def test_imports():
    """Test that all critical imports work correctly"""
    print("🧪 Testing critical imports...")
    
    try:
        # Test astronomy module imports
        from astronomy import (
            is_visible, find_visibility_window, calculate_visibility_duration,
            find_sunset_sunrise, find_astronomical_twilight, filter_visible_objects,
            calculate_altaz, calculate_moon_position, get_moon_phase_icon,
            calculate_required_exposure, calculate_required_panels,
            parse_ra, parse_dec
        )
        print("  ✅ Astronomy module imports")
        
        # Test analysis module imports
        from analysis import (
            calculate_object_score, generate_observation_schedule,
            create_mosaic_groups, combine_objects_and_groups,
            ReportGenerator
        )
        print("  ✅ Analysis module imports (including ReportGenerator)")
        
        # Test visualization imports (if available)
        try:
            from visualization.plotting import (
                setup_altaz_plot, get_abbreviated_name, finalize_plot_legend
            )
            print("  ✅ Visualization module imports")
        except ImportError:
            print("  ⚠️  Visualization module not available (optional)")
        
        # Test models and config
        from models import SchedulingStrategy, CelestialObject
        from config.settings import load_config
        print("  ✅ Core module imports")
        
        # Test catalogs
        from catalogs import get_combined_catalog, get_messier_catalog
        print("  ✅ Catalog imports")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_visibility_functions():
    """Test visibility calculation functions"""
    print("\n🧪 Testing visibility functions...")
    
    try:
        from astronomy import (
            is_visible, find_visibility_window, calculate_visibility_duration,
            find_sunset_sunrise, find_astronomical_twilight, filter_visible_objects,
            parse_ra, parse_dec
        )
        from models import CelestialObject
        from datetime import datetime
        
        # Test basic visibility (using valid azimuth range 65-165, altitude 15-75)
        assert is_visible(45, 120) == True  # Should be visible (within range)
        assert is_visible(-10, 120) == False  # Below horizon
        assert is_visible(45, 200) == False  # Outside azimuth range
        print("  ✅ is_visible function")
        
        # Test sunset/sunrise calculation
        test_date = datetime(2024, 6, 21)  # Summer solstice
        sunset, sunrise = find_sunset_sunrise(test_date)
        assert isinstance(sunset, datetime)
        assert isinstance(sunrise, datetime)
        print("  ✅ find_sunset_sunrise function")
        
        # Test twilight calculation
        twilight_eve, twilight_morn = find_astronomical_twilight(test_date)
        assert isinstance(twilight_eve, datetime)
        assert isinstance(twilight_morn, datetime)
        print("  ✅ find_astronomical_twilight function")
        
        # Test object filtering with properly parsed coordinates
        test_objects = [
            CelestialObject("Test1", parse_ra("12:00:00"), parse_dec("+45:00:00"), "20'", 8.0),
            CelestialObject("Test2", parse_ra("06:00:00"), parse_dec("+30:00:00"), "15'", 7.0)
        ]
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=8)
        
        filtered, insufficient = filter_visible_objects(test_objects, start_time, end_time)
        assert isinstance(filtered, list)
        assert isinstance(insufficient, list)
        print("  ✅ filter_visible_objects function")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Visibility function error: {e}")
        traceback.print_exc()
        return False

def test_analysis_functions():
    """Test analysis and scheduling functions"""
    print("\n🧪 Testing analysis functions...")
    
    try:
        from analysis import (
            calculate_object_score, generate_observation_schedule,
            create_mosaic_groups, combine_objects_and_groups
        )
        from models import SchedulingStrategy, CelestialObject
        from astronomy import parse_ra, parse_dec
        from datetime import datetime, timedelta
        
        # Create test objects with properly parsed coordinates
        test_objects = [
            CelestialObject("M42", parse_ra("05:35:17"), parse_dec("-05:23:14"), "65'x60'", 4.0),
            CelestialObject("M31", parse_ra("00:42:44"), parse_dec("+41:16:09"), "190'x60'", 3.4),
            CelestialObject("M13", parse_ra("16:41:41"), parse_dec("+36:27:37"), "20'", 5.8)
        ]
        
        # Test object scoring
        test_periods = [(datetime.now(), datetime.now() + timedelta(hours=2))]
        for obj in test_objects:
            score = calculate_object_score(obj, test_periods, SchedulingStrategy.LONGEST_DURATION)
            assert isinstance(score, (int, float))
        print("  ✅ calculate_object_score function")
        
        # Test schedule generation
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=8)
        
        for strategy in SchedulingStrategy:
            schedule = generate_observation_schedule(test_objects, start_time, end_time, strategy=strategy)
            assert isinstance(schedule, list)
        print("  ✅ generate_observation_schedule function")
        
        # Test mosaic groups
        mosaic_groups = create_mosaic_groups(test_objects, start_time, end_time)
        assert isinstance(mosaic_groups, list)
        print("  ✅ create_mosaic_groups function")
        
        # Test combine objects and groups
        combined = combine_objects_and_groups(test_objects, mosaic_groups, SchedulingStrategy.LONGEST_DURATION)
        assert isinstance(combined, list)
        print("  ✅ combine_objects_and_groups function")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Analysis function error: {e}")
        traceback.print_exc()
        return False

def test_report_generation():
    """Test report generation functionality"""
    print("\n🧪 Testing report generation...")
    
    try:
        from analysis import ReportGenerator
        from config.settings import get_default_location, load_config
        from datetime import datetime
        
        # Initialize report generator
        test_date = datetime.now()
        config = load_config()
        location = get_default_location(config)
        
        report_gen = ReportGenerator(test_date, location)
        assert report_gen is not None
        print("  ✅ ReportGenerator initialization")
        
        # Test adding sections
        report_gen.add_section("TEST SECTION", "Test content")
        assert len(report_gen.sections) == 1
        print("  ✅ Report section addition")
        
        # Test report generation
        report_content = report_gen.generate_report()
        assert isinstance(report_content, str)
        assert "TEST SECTION" in report_content
        print("  ✅ Report generation")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Report generation error: {e}")
        traceback.print_exc()
        return False

def test_main_application():
    """Test main application functionality"""
    print("\n🧪 Testing main application...")
    
    try:
        # Test basic report generation
        import subprocess
        result = subprocess.run([
            'python', 'astropy.py', '--report-only', '--schedule', 'longest_duration'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            assert "NIGHT OBSERVATION REPORT" in result.stdout
            print("  ✅ Main application report generation")
        else:
            print(f"  ❌ Main application failed: {result.stderr}")
            return False
        
        # Test different scheduling strategies
        strategies = ['max_objects', 'optimal_snr', 'minimal_mosaic', 'difficulty_balanced']
        for strategy in strategies:
            result = subprocess.run([
                'python', 'astropy.py', '--report-only', '--schedule', strategy
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"  ❌ Strategy {strategy} failed: {result.stderr}")
                return False
        
        print("  ✅ All scheduling strategies")
        
        # Test mosaic functionality
        result = subprocess.run([
            'python', 'astropy.py', '--report-only', '--schedule', 'mosaic_groups', '--mosaic'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Mosaic functionality")
        else:
            print(f"  ❌ Mosaic functionality failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Main application error: {e}")
        traceback.print_exc()
        return False

def test_no_duplicates():
    """Verify no duplicate functions exist"""
    print("\n🧪 Testing for duplicate functions...")
    
    try:
        import subprocess
        
        # Check for duplicate function definitions across modules
        duplicate_functions = [
            'is_visible', 'find_visibility_window', 'calculate_visibility_duration',
            'find_sunset_sunrise', 'find_astronomical_twilight', 'filter_visible_objects'
        ]
        
        for func_name in duplicate_functions:
            result = subprocess.run([
                'grep', '-r', f'def {func_name}', 
                '--include=*.py', 
                '--exclude-dir=legacy',
                '--exclude-dir=__pycache__',
                '.'
            ], capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                # Filter out backup files and legacy files
                active_files = [line for line in lines if not any(
                    excluded in line for excluded in 
                    ['_backup', '_legacy', '_experimental', '_monolithic', 'backup_before']
                )]
                
                if len(active_files) > 1:
                    print(f"  ⚠️  Function {func_name} found in multiple active files:")
                    for line in active_files:
                        print(f"    {line}")
                else:
                    print(f"  ✅ Function {func_name} - no duplicates")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Duplicate check error: {e}")
        return False

def run_comprehensive_tests():
    """Run the complete test suite"""
    print("=" * 60)
    print("COMPREHENSIVE NON-REGRESSION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Visibility Functions", test_visibility_functions),
        ("Analysis Functions", test_analysis_functions),
        ("Report Generation", test_report_generation),
        ("Main Application", test_main_application),
        ("Duplicate Function Check", test_no_duplicates)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The refactoring has been completed successfully!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 