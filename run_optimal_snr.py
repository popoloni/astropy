#!/usr/bin/env python3
"""
Optimal Signal-to-Noise Strategy
===============================
Optimizes for the best imaging conditions by balancing object brightness and altitude.
Perfect for astrophotography sessions when image quality is paramount.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--schedule', 'optimal_snr']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - OPTIMAL SNR STRATEGY")
    print("=" * 60)
    print()
    print("This will generate:")
    print("- Complete text report")
    print("- Optimized schedule for best signal-to-noise ratio")
    print("- Single trajectory plot with all objects")
    print("- Visibility chart with moon interference")
    print()
    print("Strategy: Prioritize objects when they're at optimal altitude")
    print("and brightness for the best possible image quality.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 