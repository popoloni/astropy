#!/usr/bin/env python3
"""
Max Objects Strategy Wrapper for Pythonista
============================================
Optimizes for maximum number of different objects.
Perfect for survey nights and visual observation.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run max objects scheduling strategy."""
    print("🎯 MAX OBJECTS STRATEGY")
    print("=" * 30)
    print("Optimizing for maximum number of objects...")
    print("Perfect for survey nights and star hopping!")
    print()
    
    try:
        # Import astropy after setting up path
        import astropy
        
        # Set up arguments for max objects mode
        original_argv = sys.argv.copy()
        sys.argv = ['astropy.py', '--schedule', 'max_objects']
        
        # Run the main astropy function
        astropy.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Max objects analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 