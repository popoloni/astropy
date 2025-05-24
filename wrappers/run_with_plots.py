#!/usr/bin/env python3
"""
Full Plots Wrapper for Pythonista
==================================
Complete observation planner with trajectory plots and visibility charts.
Includes yellow labels for scheduled objects.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run full analysis with plots."""
    print("📊 FULL OBSERVATION PLANNER")
    print("=" * 35)
    print("Generating complete report with plots...")
    print("⭐ Includes yellow labels for scheduled objects")
    print()
    
    try:
        # Import astropy after setting up path
        import astropy
        
        # Set up arguments for full mode (default behavior)
        original_argv = sys.argv.copy()
        sys.argv = ['astropy.py']
        
        # Run the main astropy function
        astropy.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Full analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 