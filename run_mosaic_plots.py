#!/usr/bin/env python3
"""
Mosaic Trajectory Plot Wrapper for Pythonista
==============================================
Simple wrapper to run mosaic trajectory plotting with your Vespera Passenger.
Shows only objects that can be photographed together in mosaic groups.
"""

import subprocess
import sys

def main():
    """Run the mosaic trajectory plotter."""
    print("🔭 MOSAIC TRAJECTORY PLOTTER")
    print("=" * 40)
    print("Creating trajectory plots for mosaic groups...")
    print("Vespera Passenger Mosaic FOV: 4.7° × 3.5°")
    print()
    
    try:
        # Run the mosaic trajectory plotter
        result = subprocess.run([sys.executable, "plot_mosaic_trajectories.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Mosaic plots completed successfully!")
        else:
            print(f"\n❌ Error running mosaic plotter (exit code: {result.returncode})")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 