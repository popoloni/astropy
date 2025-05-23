#!/usr/bin/env python3
"""
4-Quarter Analysis - Text Only
=============================
Generates text report optimized for 4-quarter night analysis.
Perfect for planning without plots on mobile devices.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--quarters', '--report-only']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - 4-QUARTER TEXT ANALYSIS")
    print("=" * 60)
    print()
    print("This will generate a comprehensive text report")
    print("optimized for 4-quarter night planning.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 