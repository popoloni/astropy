#!/usr/bin/env python3
"""
4-Quarter Trajectory View
========================
Generates report with 4-quarter trajectory plots for cleaner visualization.
Splits the night into 4 time periods to reduce visual clutter.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--quarters']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - 4-QUARTER TRAJECTORY VIEW")
    print("=" * 60)
    print()
    print("This will generate:")
    print("- Complete text report")
    print("- 4-quarter trajectory plots (less cluttered)")
    print("- Visibility chart with moon interference")
    print()
    print("Each quarter shows objects visible during that time period.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 