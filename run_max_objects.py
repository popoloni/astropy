#!/usr/bin/env python3
"""
Maximum Objects Strategy
========================
Optimizes for seeing the maximum number of different objects in one night.
Perfect for survey nights and visual observation sessions.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--schedule', 'max_objects']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - MAXIMUM OBJECTS STRATEGY")
    print("=" * 60)
    print()
    print("This will generate:")
    print("- Complete text report")
    print("- Optimized schedule for maximum number of objects")
    print("- Single trajectory plot with all objects")
    print("- Visibility chart with moon interference")
    print()
    print("Strategy: Fit as many different objects as possible into the night.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 