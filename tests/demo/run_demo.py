#!/usr/bin/env python3
"""
Feature Demo Wrapper
===================

Simple wrapper to run feature demonstration from the root directory.
Supports both standard subprocess version and Pythonista-compatible version.
"""

import sys
import os
import subprocess

def main():
    """Run the appropriate demo based on environment"""
    
    print("🚀 ASTROPY FEATURE DEMONSTRATION")
    print("=" * 50)
    
    # Check if we can use subprocess (not in Pythonista)
    try:
        # Try to run a simple subprocess command
        subprocess.run(['echo', 'test'], capture_output=True, check=True)
        subprocess_available = True
    except:
        subprocess_available = False
    
    if subprocess_available:
        print("📍 Running standard feature demonstration...")
        try:
            # Change to root directory to run the demo
            original_dir = os.getcwd()
            root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
            os.chdir(root_dir)
            
            result = subprocess.run([
                sys.executable, 
                'utilities/feature_demonstration.py'
            ], check=False)
            
            os.chdir(original_dir)
            return result.returncode
        except Exception as e:
            print(f"❌ Error running standard demo: {e}")
            return 1
    else:
        print("📱 Running Pythonista-compatible demonstration...")
        try:
            # Add root directory to path for imports
            root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
            sys.path.insert(0, os.path.join(root_dir, 'utilities'))
            import feature_demonstration_pythonista
            return feature_demonstration_pythonista.main()
        except Exception as e:
            print(f"❌ Error running Pythonista demo: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 