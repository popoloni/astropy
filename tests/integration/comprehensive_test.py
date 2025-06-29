#!/usr/bin/env python3
"""
Comprehensive test script for the integrated astropy system.
This validates that all functionalities work correctly after the mosaic integration.
"""

import subprocess
import sys
import json
from datetime import datetime

def run_command(cmd, description):
    """Run a command and capture its output"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    
    try:
        # Change to astropy root directory to run astronightplanner.py commands
        import os
        original_cwd = os.getcwd()
        
        # If we're in tests/integration/, go to astropy root (two levels up)
        if original_cwd.endswith('/tests/integration'):
            astropy_root = os.path.dirname(os.path.dirname(original_cwd))
            os.chdir(astropy_root)
        elif original_cwd.endswith('/utilities'):
            astropy_root = os.path.dirname(original_cwd)
            os.chdir(astropy_root)
        
        # Fix the command path - remove ../ since we're in astropy root
        if '../astronightplanner.py' in cmd:
            cmd = cmd.replace('../astronightplanner.py', 'astronightplanner.py')
        
        print(f"Command: {cmd}")
        print('='*60)
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        # Restore original directory
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            print(f"Output length: {len(result.stdout)} characters")
            return True, result.stdout, result.stderr
        else:
            print("❌ FAILED")
            print(f"Return code: {result.returncode}")
            print(f"Stderr: {result.stderr}")
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        print("❌ TIMEOUT - Command took too long")
        return False, "", "Timeout"
    except Exception as e:
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        print(f"❌ EXCEPTION: {e}")
        return False, "", str(e)

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

def main():
    """Run comprehensive tests"""
    print("🧪 COMPREHENSIVE ASTROPY INTEGRATION TEST")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic functionality (report-only)
    tests_total += 1
    success, output, stderr = run_command(
        "python3 ../astronightplanner.py --report-only",
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
            tests_passed += 1
            print("✅ Basic functionality test PASSED")
        else:
            print("❌ Basic functionality test FAILED")
    
    # Test 2: Mosaic analysis integration
    tests_total += 1
    success, output, stderr = run_command(
        "python3 ../astronightplanner.py --mosaic --report-only",
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
            tests_passed += 1
            print("✅ Mosaic analysis test PASSED")
        else:
            print("❌ Mosaic analysis test FAILED")
    
    # Test 3: Mosaic-only mode
    tests_total += 1
    success, output, stderr = run_command(
        "python3 ../astronightplanner.py --mosaic-only --report-only",
        "Mosaic-only mode"
    )
    
    if success:
        mosaic_only_patterns = [
            "Strategy: longest_duration",
            "Mosaic:",
            "Duration:",
            "Required exposure:"
        ]
        
        # Should NOT contain individual objects in schedules when mosaic-only
        forbidden_patterns = []
        
        if validate_output(output, mosaic_only_patterns, "Mosaic-Only Mode"):
            tests_passed += 1
            print("✅ Mosaic-only test PASSED")
        else:
            print("❌ Mosaic-only test FAILED")
    
    # Test 4: Specific mosaic_groups strategy
    tests_total += 1
    success, output, stderr = run_command(
        "python3 ../astronightplanner.py --schedule mosaic_groups --report-only",
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
            tests_passed += 1
            print("✅ Mosaic groups strategy test PASSED")
        else:
            print("❌ Mosaic groups strategy test FAILED")
    
    # Test 5: Backwards compatibility - all existing strategies should work
    strategies = ['longest_duration', 'max_objects', 'optimal_snr', 'minimal_mosaic', 'difficulty_balanced']
    
    for strategy in strategies:
        tests_total += 1
        success, output, stderr = run_command(
                         f"python3 ../astronightplanner.py --schedule {strategy} --report-only",
            f"Backwards compatibility - {strategy} strategy"
        )
        
        if success and f"Strategy: {strategy}" in output:
            tests_passed += 1
            print(f"✅ {strategy} strategy test PASSED")
        else:
            print(f"❌ {strategy} strategy test FAILED")
    
    # Test 6: Check for essential components and classes
    tests_total += 1
    success, output, stderr = run_command(
        "python3 -c \"import sys; sys.path.insert(0, '.'); import astronightplanner; print('MosaicGroup available:', hasattr(astronightplanner, 'MosaicGroup')); print('SchedulingStrategy.MOSAIC_GROUPS available:', hasattr(astronightplanner.SchedulingStrategy, 'MOSAIC_GROUPS'))\"",
        "Essential classes and enums availability"
    )
    
    if success and "MosaicGroup available: True" in output and "MOSAIC_GROUPS available: True" in output:
        tests_passed += 1
        print("✅ Essential components test PASSED")
    else:
        print("❌ Essential components test FAILED")
    
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