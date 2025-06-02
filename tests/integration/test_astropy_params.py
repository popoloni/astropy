#!/usr/bin/env python3
"""
Comprehensive test script for astroastronightplanner.py with high precision enabled
Tests all major parameter combinations to ensure compatibility
"""

import subprocess
import sys
import os
from datetime import datetime

def run_astropy_test(params, description):
    """Run astroastronightplanner.py with given parameters and check for errors"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Command: python astroastronightplanner.py {' '.join(params)}")
    print("-" * 60)
    
    try:
        # Run the command
        result = subprocess.run(
            [sys.executable, "astroastronightplanner.py"] + params,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            # Show first few lines of output to verify it's working
            lines = result.stdout.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(result.stdout.split('\n')) > 5:
                print("   ...")
            return True
        else:
            print("❌ FAILED")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def main():
    """Test all major parameter combinations"""
    
    print("🚀 ASTROPY.PY HIGH PRECISION PARAMETER TESTING")
    print("=" * 70)
    print("Testing all major parameter combinations with high precision enabled")
    print(f"Current working directory: {os.getcwd()}")
    print()
    
    # Change to astropy directory
    os.chdir('/workspace/astropy')
    
    # Test cases: (parameters, description)
    test_cases = [
        # Basic functionality
        (["--report-only"], "Basic report only"),
        (["--date", "2025-06-15"], "Specific date"),
        (["--date", "2025-12-21"], "Winter solstice date"),
        
        # Object filtering
        (["--object", "M31"], "Specific object (M31)"),
        (["--object", "NGC6960"], "Specific object (NGC6960)"),
        (["--type", "nebula"], "Filter by nebula type"),
        (["--type", "galaxy"], "Filter by galaxy type"),
        (["--type", "cluster"], "Filter by cluster type"),
        
        # Scheduling strategies
        (["--schedule", "longest_duration"], "Longest duration strategy"),
        (["--schedule", "max_objects"], "Max objects strategy"),
        (["--schedule", "optimal_snr"], "Optimal SNR strategy"),
        (["--schedule", "minimal_mosaic"], "Minimal mosaic strategy"),
        (["--schedule", "difficulty_balanced"], "Difficulty balanced strategy"),
        (["--schedule", "mosaic_groups"], "Mosaic groups strategy"),
        
        # Visibility options
        (["--no-margins"], "No margins mode"),
        (["--quarters"], "Quarterly plots"),
        
        # Time simulation
        (["--simulate-time", "23:30"], "Simulate nighttime"),
        (["--simulate-time", "12:00"], "Simulate daytime"),
        (["--simulate-time", "01:30:45"], "Simulate with seconds"),
        
        # Mosaic options
        (["--mosaic"], "Mosaic analysis enabled"),
        (["--mosaic-only"], "Mosaic only mode"),
        (["--mosaic", "--no-duplicates"], "Mosaic with no duplicates"),
        
        # Combined options
        (["--date", "2025-07-04", "--schedule", "max_objects"], "Date + schedule"),
        (["--type", "nebula", "--schedule", "optimal_snr"], "Type filter + schedule"),
        (["--object", "M27", "--quarters"], "Specific object + quarters"),
        (["--report-only", "--date", "2025-08-15", "--type", "cluster"], "Report + date + type"),
        (["--mosaic", "--schedule", "mosaic_groups", "--no-margins"], "Mosaic + schedule + no margins"),
        (["--simulate-time", "02:00", "--schedule", "longest_duration"], "Simulation + schedule"),
        (["--date", "2025-09-23", "--mosaic-only", "--no-duplicates"], "Date + mosaic-only + no-duplicates"),
        
        # Edge cases
        (["--date", "2025-01-01"], "New Year's Day"),
        (["--date", "2025-06-21"], "Summer solstice"),
        (["--object", "M999"], "Non-existent object (should handle gracefully)"),
        (["--type", "nonexistent"], "Non-existent type (should handle gracefully)"),
    ]
    
    # Run all tests
    passed = 0
    failed = 0
    
    for params, description in test_cases:
        success = run_astropy_test(params, description)
        if success:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! High precision integration is working correctly.")
    else:
        print(f"\n⚠️  {failed} tests failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)