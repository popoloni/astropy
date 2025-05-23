#!/usr/bin/env python3
"""
Quick Report - Text Only
========================
Generates a comprehensive text report without any plots.
Perfect for quick checks and when you just need the information.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--report-only']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - TEXT REPORT ONLY")
    print("=" * 60)
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 