#!/usr/bin/env python3
"""
Mosaic Analysis and Plotting Wrapper for Pythonista
===================================================
Comprehensive mosaic analysis tool that:
- Analyzes objects for mosaic grouping opportunities
- Shows detailed mosaic group information
- Generates trajectory plots for mosaic groups
- Provides scheduling focused on mosaic opportunities

This replaces the functionality of the old plot_mosaic_trajectories.py script
using the integrated astropy mosaic capabilities.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run comprehensive mosaic analysis and plotting."""
    print("🔬 COMPREHENSIVE MOSAIC ANALYSIS")
    print("=" * 45)
    print("Analyzing objects for mosaic opportunities...")
    print("Generating detailed reports and trajectory plots...")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Get scope configuration from settings
        from config.settings import SCOPE_NAME, MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT
        print(f"🔭 {SCOPE_NAME}")
        print(f"📐 Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°")
        print()
        
        # Set up arguments for comprehensive mosaic analysis
        original_argv = sys.argv.copy()
        sys.argv = ['astronightplanner.py', '--mosaic', '--schedule', 'mosaic_groups']
        
        print("📊 PHASE 1: Mosaic Group Analysis")
        print("=" * 35)
        
        # Run the main astropy function with mosaic analysis and plotting
        astronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n" + "=" * 50)
        print("✅ MOSAIC ANALYSIS COMPLETE!")
        print("=" * 50)
        print("📈 Generated outputs:")
        print("  • Detailed mosaic group analysis")
        print("  • Individual group trajectory plots")
        print("  • Combined trajectory overview")
        print("  • Mosaic-optimized scheduling")
        print("  • Full observation report")
        print()
        print("📱 Perfect for:")
        print("  • Planning mosaic imaging sessions")
        print("  • Identifying optimal groupings")
        print("  • Maximizing telescope efficiency")
        print("  • Advanced astrophotography projects")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 