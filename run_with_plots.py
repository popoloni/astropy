#!/usr/bin/env python3
"""
Full Observation Report with Plots
==================================
Generates complete report with trajectory plots and visibility charts.
Shows single-plot trajectory view with all objects.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py (default mode - no special flags)
sys.argv = ['astropy.py']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - FULL REPORT WITH PLOTS")
    print("=" * 60)
    print()
    print("This will generate:")
    print("- Complete text report")
    print("- Single trajectory plot with all objects")
    print("- Visibility chart with moon interference")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 