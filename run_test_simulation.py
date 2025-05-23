#!/usr/bin/env python3
"""
Test Simulation - Nighttime Preview
===================================
Simulates running the program at 1:30 AM to test nighttime observations
during daytime. Perfect for testing and planning ahead.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py
sys.argv = ['astropy.py', '--simulate-time', '01:30', '--report-only']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("ASTROPY OBSERVATION PLANNER - NIGHTTIME SIMULATION TEST")
    print("=" * 60)
    print()
    print("This simulates running the program at 1:30 AM")
    print("Perfect for testing during daytime!")
    print()
    print("Will generate a text report as if it were the middle of the night.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 
