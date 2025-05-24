#!/usr/bin/env python3
"""
Longest Duration Strategy Wrapper for Pythonista
=================================================
Prioritizes objects with longest visibility windows.
Perfect for deep sky imaging and extended exposures.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run longest duration scheduling strategy."""
    print("🎯 LONGEST DURATION STRATEGY")
    print("=" * 35)
    print("Prioritizing objects with longest visibility...")
    print("Perfect for deep sky imaging and long exposures!")
    print()
    
    try:
        # Import astropy after setting up path
        import astropy
        
        # Set up arguments for longest duration mode
        original_argv = sys.argv.copy()
        sys.argv = ['astropy.py', '--schedule', 'longest']
        
        # Run the main astropy function
        astropy.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Longest duration analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 