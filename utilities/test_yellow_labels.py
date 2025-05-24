#!/usr/bin/env python3
"""
Yellow Labels Test Wrapper for Pythonista
==========================================
Tests the yellow label feature for scheduled objects.
Shows clear examples of yellow vs white labels.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Test the yellow labels feature."""
    print("⭐ YELLOW LABELS TEST")
    print("=" * 25)
    print("Testing yellow label feature for scheduled objects...")
    print("Yellow labels = scheduled objects")
    print("White labels = visible but not scheduled")
    print()
    
    try:
        # Import astropy after setting up path
        import astropy
        
        # Set up arguments for full mode to show yellow labels
        original_argv = sys.argv.copy()
        sys.argv = ['astropy.py', '--quarters']
        
        # Run the main astropy function
        astropy.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Yellow labels test completed successfully!")
        print("Look for yellow vs white label backgrounds in the plots!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 