#!/usr/bin/env python3
"""
Mosaic Trajectory Plot Wrapper for Pythonista
==============================================
Simple wrapper to run mosaic trajectory plotting with your Vespera Passenger.
Shows only objects that can be photographed together in mosaic groups.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run the mosaic trajectory plotter."""
    print("🔭 MOSAIC TRAJECTORY PLOTTER")
    print("=" * 40)
    print("Creating trajectory plots for mosaic groups...")
    
    try:
        # Import configuration and plot_mosaic_trajectories after setting up path
        from astropy import CONFIG
        import plot_mosaic_trajectories
        
        scope_name = CONFIG['imaging']['scope']['name']
        mosaic_fov_w = CONFIG['imaging']['scope']['mosaic_fov_width']
        mosaic_fov_h = CONFIG['imaging']['scope']['mosaic_fov_height']
        print(f"{scope_name} Mosaic FOV: {mosaic_fov_w}° × {mosaic_fov_h}°")
        print()
        
        # Run the main mosaic plotting function
        plot_mosaic_trajectories.main()
        
        print("\n✅ Mosaic plots completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 