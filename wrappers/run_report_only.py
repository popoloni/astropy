#!/usr/bin/env python3
"""
Report Only Wrapper for Pythonista
===================================
Generates text-only observation reports without plots.
Perfect for quick checks on mobile devices.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run report-only analysis."""
    print("📊 OBSERVATION REPORT ONLY")
    print("=" * 30)
    print("Generating text report without plots...")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Set up arguments for report-only mode
        original_argv = sys.argv.copy()
        sys.argv = ['astroastronightplanner.py', '--report-only']
        
        # Run the main astropy function
        astroastronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Report completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 