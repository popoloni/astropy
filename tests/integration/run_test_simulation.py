#!/usr/bin/env python3
"""
Test Simulation Wrapper for Pythonista
=======================================
Simulates nighttime conditions (1:30 AM) during daytime.
Perfect for testing the app during the day.
"""

import sys
import os

# Add root directory to path for imports
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, root_dir)

def main():
    """Run nighttime simulation for daytime testing."""
    print("🧪 NIGHTTIME SIMULATION TEST")
    print("=" * 35)
    print("Simulating 1:30 AM conditions during daytime...")
    print("Perfect for testing without waiting for night!")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Set up arguments for simulation mode
        original_argv = sys.argv.copy()
        sys.argv = ['astroastronightplanner.py', '--simulate-time', '01:30', '--report-only']
        
        # Run the main astropy function
        astroastronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Simulation test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
