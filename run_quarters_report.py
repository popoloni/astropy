#!/usr/bin/env python3
"""
Quarters Report Wrapper for Pythonista
=======================================
Text report optimized for 4-quarter night analysis.
Mobile-friendly without plots.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run quarters text report analysis."""
    print("📊 4-QUARTER TEXT REPORT")
    print("=" * 30)
    print("Generating quarterly analysis without plots...")
    print()
    
    try:
        # Import astropy after setting up path
        import astropy
        
        # Set up arguments for quarters report mode
        original_argv = sys.argv.copy()
        sys.argv = ['astropy.py', '--quarters', '--report-only']
        
        # Run the main astropy function
        astropy.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Quarters report completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 