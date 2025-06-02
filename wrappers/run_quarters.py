#!/usr/bin/env python3
"""
Quarters Plot Wrapper for Pythonista
=====================================
4-quarter trajectory plots for cleaner visualization.
Perfect for nights with many visible objects.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run quarters analysis with 4-quarter plots."""
    print("📊 4-QUARTER TRAJECTORY PLOTS")
    print("=" * 35)
    print("Generating 4-quarter plots for cleaner visualization...")
    print("⭐ Includes yellow labels for scheduled objects")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Set up arguments for quarters mode
        original_argv = sys.argv.copy()
        sys.argv = ['astronightplanner.py', '--quarters']
        
        # Run the main astropy function
        astronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ 4-quarter analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 