#!/usr/bin/env python3
"""
Test Runner Wrapper
==================

Simple wrapper to run tests from the root directory.
Supports both standard subprocess version and Pythonista-compatible version.
"""

import sys
import os
import subprocess

def main():
    """Run the appropriate test based on environment"""
    
    print("🧪 ASTROPY TEST RUNNER")
    print("=" * 50)
    
    # Check if we can use subprocess (not in Pythonista)
    try:
        # Try to run a simple subprocess command
        subprocess.run(['echo', 'test'], capture_output=True, check=True)
        subprocess_available = True
    except:
        subprocess_available = False
    
    if subprocess_available:
        print("📍 Running standard test suite...")
        try:
            result = subprocess.run([
                sys.executable, 
                'utilities/comprehensive_test.py'
            ], check=False)
            return result.returncode
        except Exception as e:
            print(f"❌ Error running standard tests: {e}")
            return 1
    else:
        print("📱 Running Pythonista-compatible test suite...")
        try:
            # Import and run the Pythonista version
            sys.path.insert(0, 'utilities')
            import comprehensive_test_pythonista
            return comprehensive_test_pythonista.main()
        except Exception as e:
            print(f"❌ Error running Pythonista tests: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 