#!/usr/bin/env python3
"""
Optimal SNR Strategy Wrapper for Pythonista
============================================
Optimizes for best imaging conditions (brightness + altitude).
Perfect for astrophotography when image quality is paramount.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run optimal SNR scheduling strategy."""
    print("🎯 OPTIMAL SNR STRATEGY")
    print("=" * 30)
    print("Optimizing for best imaging conditions...")
    print("Perfect for high-quality astrophotography!")
    print()
    
    try:
        # Import astropy after setting up path
        import astronightplanner
        
        # Set up arguments for optimal SNR mode
        original_argv = sys.argv.copy()
        sys.argv = ['astronightplanner.py', '--schedule', 'optimal_snr']
        
        # Run the main astropy function
        astronightplanner.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        print("\n✅ Optimal SNR analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 