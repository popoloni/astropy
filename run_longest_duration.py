#!/usr/bin/env python3
"""
Longest Duration Strategy
========================
Optimizes for objects with the longest visibility windows.
Perfect for deep sky imaging when you want extended time on targets.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--schedule', 'longest_duration']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - LONGEST DURATION STRATEGY")
    print("=" * 60)
    print()
    print("This will generate:")
    print("- Complete text report")
    print("- Optimized schedule for longest visibility windows")
    print("- Single trajectory plot with all objects")
    print("- Visibility chart with moon interference")
    print()
    print("Strategy: Prioritize objects with the longest observation")
    print("windows for extended imaging sessions.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 