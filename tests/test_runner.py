#!/usr/bin/env python3
"""
Comprehensive Test Runner for Astropy
=====================================

Runs all test categories with proper organization and reporting.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def run_python_test(test_path, description):
    """Run a Python test file and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"📁 {test_path}")
    print('='*60)
    
    try:
        # Get absolute path to astropy root
        script_dir = Path(__file__).parent
        astropy_root = script_dir.parent
        
        # Change to astropy root directory
        original_cwd = os.getcwd()
        os.chdir(astropy_root)
        
        # Run the test
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Restore directory
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout.strip():
                print("📋 Output:")
                print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
        else:
            print("❌ FAILED")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print("🚨 Error output:")
                print(result.stderr[:500] + ("..." if len(result.stderr) > 500 else ""))
            if result.stdout:
                print("📋 Standard output:")
                print(result.stdout[:500] + ("..." if len(result.stdout) > 500 else ""))
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Test took too long")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def run_test_suite():
    """Run the complete test suite"""
    print("🚀 ASTROPY COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Define test categories and their files
    test_categories = {
        "Unit Tests": [
            test_dir / "unit" / "test_phase3_simple.py",
            test_dir / "unit" / "test_yellow_labels.py",
        ],
        "Precision Tests": [
            test_dir / "precision" / "test_high_precision.py",
            test_dir / "precision" / "test_config.py",
            test_dir / "precision" / "test_phase2_functions.py",
            test_dir / "precision" / "test_phase3_functions.py",
        ],
        "Integration Tests": [
            test_dir / "integration" / "test_astropy_params.py",
            test_dir / "integration" / "test_high_precision_verification.py",
            test_dir / "integration" / "test_precision_integration.py",
            test_dir / "integration" / "comprehensive_test.py",
        ],
        "Legacy Tests": [
            test_dir / "legacy" / "test_mosaic_integration.py",
        ]
    }
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    # Run each category
    for category, test_files in test_categories.items():
        print(f"\n🏷️  {category.upper()}")
        print("-" * 60)
        
        category_passed = 0
        category_total = 0
        
        for test_file in test_files:
            if test_file.exists():
                total_tests += 1
                category_total += 1
                
                success = run_python_test(test_file, f"{category}: {test_file.name}")
                if success:
                    passed_tests += 1
                    category_passed += 1
            else:
                print(f"⚠️  Test file not found: {test_file}")
        
        results[category] = (category_passed, category_total)
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print('='*80)
    
    for category, (passed, total) in results.items():
        status = "✅" if passed == total else "❌"
        print(f"{status} {category}: {passed}/{total} passed")
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"💥 {total_tests - passed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_test_suite())