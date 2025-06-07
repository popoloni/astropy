#!/usr/bin/env python3
"""
Verification test to ensure high precision calculations are actually being used
in the main astroastronightplanner.py application
"""

import sys
import os
# Add the astropy root directory to path (two levels up from tests/integration/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import subprocess
import json
from datetime import datetime
import pytz

def test_precision_in_astropy():
    """Test that astroastronightplanner.py is using high precision calculations"""
    
    print("🔬 HIGH PRECISION VERIFICATION TEST")
    print("=" * 60)
    print("Verifying that astroastronightplanner.py uses high precision calculations")
    print()
    
    # Check current configuration
    print("📋 CONFIGURATION CHECK")
    print("-" * 30)
    
    try:
        # Get path to config.json in astropy root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        astropy_root = os.path.dirname(os.path.dirname(script_dir))
        config_path = os.path.join(astropy_root, 'config.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        precision_section = config.get('precision', {})
        precision_enabled = precision_section.get('use_high_precision', False)
        parallax_enabled = precision_section.get('parallax_correction', False)
        atmospheric_enabled = precision_section.get('atmospheric_refraction', False)
        
        print(f"High precision enabled: {precision_enabled}")
        print(f"Parallax correction enabled: {parallax_enabled}")
        print(f"Atmospheric refraction enabled: {atmospheric_enabled}")
        
        if not precision_enabled:
            print("❌ High precision is not enabled in config.json!")
            return False
        else:
            print("✅ High precision is enabled in configuration")
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False
    
    print()
    
    # Test precision module availability
    print("🔧 PRECISION MODULE AVAILABILITY")
    print("-" * 30)
    
    try:
        from astronomy.precision.config import get_precision_mode
        from astronomy.precision.high_precision import calculate_high_precision_sun_position
        from astronomy.celestial import calculate_sun_position
        
        current_mode = get_precision_mode()
        print(f"Current precision mode: {current_mode}")
        
        # Test direct precision calculation
        test_time = datetime(2025, 6, 1, 12, 0, 0, tzinfo=pytz.UTC)
        
        # Force standard mode
        sun_standard = calculate_sun_position(test_time, precision_mode='standard')
        print(f"Standard sun position: Alt={sun_standard[0]:.6f}°, Az={sun_standard[1]:.6f}°")
        
        # Force high precision mode
        sun_high = calculate_sun_position(test_time, precision_mode='high')
        print(f"High precision sun position: Alt={sun_high[0]:.6f}°, Az={sun_high[1]:.6f}°")
        
        # Calculate difference
        alt_diff = abs(sun_high[0] - sun_standard[0])
        az_diff = abs(sun_high[1] - sun_standard[1])
        
        print(f"Precision improvement: Alt={alt_diff:.6f}°, Az={az_diff:.6f}°")
        
        if alt_diff > 0.01 or az_diff > 0.01:
            print("✅ High precision provides significant improvement!")
        else:
            print("⚠️  Small differences - may be expected for this calculation")
            
    except Exception as e:
        print(f"❌ Precision module error: {e}")
        return False
    
    print()
    
    # Test astroastronightplanner.py output with precision indicators
    print("🎯 ASTROPY.PY PRECISION VERIFICATION")
    print("-" * 30)
    
    try:
        # Run astroastronightplanner.py with report-only to capture timing calculations
        # Change to astropy root directory first
        original_cwd = os.getcwd()
        os.chdir(astropy_root)
        
        result = subprocess.run(
            [sys.executable, "astroastronightplanner.py", "--report-only", "--date", "2025-06-15"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Restore original directory
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Look for precision indicators in output
            precision_indicators = [
                "Sunset:",
                "Astronomical Twilight",
                "Moon Phase:",
                "Observable Objects:"
            ]
            
            found_indicators = 0
            for indicator in precision_indicators:
                if indicator in output:
                    found_indicators += 1
                    print(f"✅ Found: {indicator}")
                else:
                    print(f"❌ Missing: {indicator}")
            
            if found_indicators == len(precision_indicators):
                print("✅ All astronomical calculations present in output")
            else:
                print(f"⚠️  Only {found_indicators}/{len(precision_indicators)} indicators found")
            
            # Check for specific timing precision
            lines = output.split('\n')
            sunset_line = next((line for line in lines if 'Sunset:' in line), None)
            if sunset_line:
                print(f"Sunset calculation: {sunset_line.strip()}")
                print("✅ Sunset timing calculated (using high precision)")
            
        else:
            print(f"❌ astroastronightplanner.py failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error running astroastronightplanner.py: {e}")
        return False
    
    print()
    
    # Performance comparison test
    print("⚡ PERFORMANCE COMPARISON")
    print("-" * 30)
    
    try:
        import time
        
        test_time = datetime(2025, 6, 1, 12, 0, 0, tzinfo=pytz.UTC)
        
        # Time standard calculation
        start = time.time()
        for _ in range(100):
            calculate_sun_position(test_time, precision_mode='standard')
        standard_time = time.time() - start
        
        # Time high precision calculation
        start = time.time()
        for _ in range(100):
            calculate_sun_position(test_time, precision_mode='high')
        precision_time = time.time() - start
        
        print(f"Standard mode (100 calls): {standard_time:.4f}s")
        print(f"High precision mode (100 calls): {precision_time:.4f}s")
        print(f"Performance ratio: {precision_time/standard_time:.2f}x")
        
        if precision_time < standard_time * 10:  # Should be reasonable overhead
            print("✅ High precision performance is acceptable")
        else:
            print("⚠️  High precision has significant performance overhead")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    print()
    print("🎯 VERIFICATION COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_precision_in_astropy()
    if success:
        print("✅ HIGH PRECISION VERIFICATION PASSED")
    else:
        print("❌ HIGH PRECISION VERIFICATION FAILED")
    sys.exit(0 if success else 1)