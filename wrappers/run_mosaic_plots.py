#!/usr/bin/env python3
"""
Mosaic Trajectory Plot Wrapper for Pythonista
==============================================
Simple wrapper to run mosaic trajectory plotting with your Vespera Passenger.
Shows only objects that can be photographed together in mosaic groups.
Uses the integrated mosaic functionality in astroastronightplanner.py.

The --no-duplicates flag can be used to exclude individual objects that are
already part of mosaic groups from standalone display.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run the mosaic trajectory plotter using integrated astropy functionality."""
    print("🔭 MOSAIC TRAJECTORY PLOTTER")
    print("=" * 40)
    print("Creating trajectory plots for mosaic groups...")
    print("Using integrated astropy mosaic functionality...")
    print("📄 Note: Use --no-duplicates to hide individual objects that are part of mosaic groups")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Get scope configuration from settings
        from config.settings import SCOPE_NAME, MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT
        print(f"🔭 {SCOPE_NAME}")
        print(f"📐 Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°")
        print()
        
        # Set up arguments for mosaic plotting with no duplicates
        original_argv = sys.argv.copy()
        sys.argv = ['astroastronightplanner.py', '--mosaic', '--no-duplicates']
        
        # Run the main astropy function with mosaic plotting
        astroastronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Mosaic plots completed successfully!")
        print("📊 Check the generated plots for mosaic group trajectories!")
        print("🎯 Individual objects in mosaic groups were filtered out to avoid duplicates!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
