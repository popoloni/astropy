#!/usr/bin/env python3
"""
Comprehensive test script for Pythonista (iOS)
==============================================

This validates that all functionalities work correctly after the mosaic integration.
This version is compatible with iOS Pythonista and doesn't use subprocess.
"""

import sys
import os
import argparse
from datetime import datetime
import io
import contextlib

# Add root directory to path to import astropy
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, root_dir)

try:
    import astropy
    from astropy import main as astropy_main
except ImportError as e:
    print(f"Error importing astropy: {e}")
    sys.exit(1)

def capture_output(func, *args, **kwargs):
    """Capture stdout from a function call"""
    old_stdout = sys.stdout
    old_argv = sys.argv.copy()
    
    try:
        # Redirect stdout to capture output
        sys.stdout = captured_output = io.StringIO()
        
        # Set up arguments
        if args:
            sys.argv = ['astropy.py'] + list(args)
        
        # Call the function
        try:
            result = func(**kwargs)
            success = True
            error_msg = ""
        except SystemExit as e:
            success = e.code == 0
            error_msg = f"SystemExit: {e.code}"
        except Exception as e:
            success = False
            error_msg = str(e)
        
        # Get the captured output
        output = captured_output.getvalue()
        
        return success, output, error_msg
        
    finally:
        # Restore stdout and argv
        sys.stdout = old_stdout
        sys.argv = old_argv

def run_astropy_test(test_args, description):
    """Run astropy with given arguments and capture output"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Arguments: {' '.join(test_args)}")
    print('='*60)
    
    success, output, error = capture_output(astropy_main, *test_args)
    
    if success:
        print("✅ SUCCESS")
        print(f"Output length: {len(output)} characters")
        return True, output, error
    else:
        print("❌ FAILED")
        print(f"Error: {error}")
        return False, output, error

def validate_output(output, expected_patterns, test_name):
    """Validate that output contains expected patterns"""
    print(f"\nValidating {test_name}:")
    
    all_found = True
    for pattern in expected_patterns:
        if pattern in output:
            print(f"  ✅ Found: '{pattern}'")
        else:
            print(f"  ❌ Missing: '{pattern}'")
            all_found = False
    
    return all_found

def test_basic_functionality():
    """Test basic functionality with all scheduling strategies"""
    success, output, error = run_astropy_test(
        ['--report-only'],
        "Basic functionality with all scheduling strategies"
    )
    
    if success:
        basic_patterns = [
            "NIGHT OBSERVATION REPORT",
            "QUICK SUMMARY",
            "TIMING INFORMATION",
            "MOON CONDITIONS",
            "PRIME TARGETS",
            "Strategy: longest_duration",
            "Strategy: max_objects", 
            "Strategy: optimal_snr",
            "Strategy: minimal_mosaic",
            "Strategy: difficulty_balanced",
            "Strategy: mosaic_groups"
        ]
        
        if validate_output(output, basic_patterns, "Basic Report"):
            print("✅ Basic functionality test PASSED")
            return True
        else:
            print("❌ Basic functionality test FAILED")
            return False
    return False

def test_mosaic_integration():
    """Test mosaic analysis integration"""
    success, output, error = run_astropy_test(
        ['--mosaic', '--report-only'],
        "Mosaic analysis integration"
    )
    
    if success:
        mosaic_patterns = [
            "Analyzing mosaic groups...",
            "MOSAIC GROUP ANALYSIS",
            "Found",
            "mosaic groups",
            "MOSAIC GROUPS",
            "Group 1:",
            "Total overlap time:",
            "Composite magnitude:",
            "Mosaic:"
        ]
        
        if validate_output(output, mosaic_patterns, "Mosaic Analysis"):
            print("✅ Mosaic analysis test PASSED")
            return True
        else:
            print("❌ Mosaic analysis test FAILED")
            return False
    return False

def test_mosaic_only():
    """Test mosaic-only mode"""
    success, output, error = run_astropy_test(
        ['--mosaic-only', '--report-only'],
        "Mosaic-only mode"
    )
    
    if success:
        mosaic_only_patterns = [
            "Strategy: longest_duration",
            "Mosaic:",
            "Duration:",
            "Required exposure:"
        ]
        
        if validate_output(output, mosaic_only_patterns, "Mosaic-Only Mode"):
            print("✅ Mosaic-only test PASSED")
            return True
        else:
            print("❌ Mosaic-only test FAILED")
            return False
    return False

def test_mosaic_strategy():
    """Test mosaic groups scheduling strategy"""
    success, output, error = run_astropy_test(
        ['--schedule', 'mosaic_groups', '--report-only'],
        "Mosaic groups scheduling strategy"
    )
    
    if success:
        strategy_patterns = [
            "Analyzing mosaic groups...",
            "Found",
            "mosaic groups",
            "Strategy: mosaic_groups",
            "Mosaic:"
        ]
        
        if validate_output(output, strategy_patterns, "Mosaic Groups Strategy"):
            print("✅ Mosaic groups strategy test PASSED")
            return True
        else:
            print("❌ Mosaic groups strategy test FAILED")
            return False
    return False

def test_strategy_compatibility():
    """Test backwards compatibility for all strategies"""
    strategies = ['longest_duration', 'max_objects', 'optimal_snr', 'minimal_mosaic', 'difficulty_balanced']
    
    passed = 0
    total = len(strategies)
    
    for strategy in strategies:
        success, output, error = run_astropy_test(
            ['--schedule', strategy, '--report-only'],
            f"Backwards compatibility - {strategy} strategy"
        )
        
        if success and f"Strategy: {strategy}" in output:
            print(f"✅ {strategy} strategy test PASSED")
            passed += 1
        else:
            print(f"❌ {strategy} strategy test FAILED")
    
    return passed, total

def test_essential_components():
    """Test essential classes and enums availability"""
    print(f"\n{'='*60}")
    print("Testing: Essential classes and enums availability")
    print('='*60)
    
    try:
        # Test MosaicGroup availability
        mosaic_group_available = hasattr(astropy, 'MosaicGroup')
        print(f"MosaicGroup available: {mosaic_group_available}")
        
        # Test SchedulingStrategy.MOSAIC_GROUPS availability
        mosaic_strategy_available = hasattr(astropy.SchedulingStrategy, 'MOSAIC_GROUPS')
        print(f"SchedulingStrategy.MOSAIC_GROUPS available: {mosaic_strategy_available}")
        
        if mosaic_group_available and mosaic_strategy_available:
            print("✅ Essential components test PASSED")
            return True
        else:
            print("❌ Essential components test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Essential components test FAILED: {e}")
        return False

def main():
    """Run comprehensive tests for Pythonista"""
    print("🧪 COMPREHENSIVE ASTROPY INTEGRATION TEST (Pythonista Compatible)")
    print("=" * 80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic functionality
    tests_total += 1
    if test_basic_functionality():
        tests_passed += 1
    
    # Test 2: Mosaic analysis integration
    tests_total += 1
    if test_mosaic_integration():
        tests_passed += 1
    
    # Test 3: Mosaic-only mode
    tests_total += 1
    if test_mosaic_only():
        tests_passed += 1
    
    # Test 4: Mosaic groups strategy
    tests_total += 1
    if test_mosaic_strategy():
        tests_passed += 1
    
    # Test 5: Strategy compatibility
    strategy_passed, strategy_total = test_strategy_compatibility()
    tests_passed += strategy_passed
    tests_total += strategy_total
    
    # Test 6: Essential components
    tests_total += 1
    if test_essential_components():
        tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print("🧪 TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED! Integration is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 