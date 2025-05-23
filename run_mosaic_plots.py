#!/usr/bin/env python3
"""
Mosaic Trajectory Plot Wrapper for Pythonista
==============================================
Simple wrapper to run mosaic trajectory plotting with your Vespera Passenger.
Shows only objects that can be photographed together in mosaic groups.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the mosaic trajectory plotter."""
    print("🔭 MOSAIC TRAJECTORY PLOTTER")
    print("=" * 40)
    print("Creating trajectory plots for mosaic groups...")
    print("Vespera Passenger Mosaic FOV: 4.7° × 3.5°")
    print()
    
    try:
        # Import plot_mosaic_trajectories after setting up path
        import plot_mosaic_trajectories
        
        # Run the main mosaic plotting function
        plot_mosaic_trajectories.main()
        
        print("\n✅ Mosaic plots completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 