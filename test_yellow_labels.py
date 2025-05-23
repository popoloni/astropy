#!/usr/bin/env python3
"""
Test Yellow Labels for Scheduled Objects
========================================
Tests the new yellow label feature in trajectory plots.
This script runs a quick test to show scheduled objects with yellow labels.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up arguments for astropy.py with a specific scheduling strategy
sys.argv = ['astropy.py', '--schedule', 'max_objects']

# Import and run the main astropy program
try:
    from astropy import main
    print("=" * 60)
    print("TESTING YELLOW LABELS FOR SCHEDULED OBJECTS")
    print("=" * 60)
    print()
    print("This will generate trajectory plots where:")
    print("- ⭐ SCHEDULED objects have YELLOW transparent label backgrounds")
    print("- 🔘 Non-scheduled objects have WHITE transparent label backgrounds")
    print()
    print("Look for the yellow labels in the trajectory plots!")
    print("The same objects that have red hatching in the visibility chart")
    print("should have yellow labels in the trajectory plots.")
    print()
    
    main()
    
except Exception as e:
    print(f"Error running astropy: {e}")
    print("Make sure astropy.py is in the same directory as this script.") 