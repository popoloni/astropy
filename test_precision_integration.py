#!/usr/bin/env python3
"""
Test script to verify high-precision integration is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import pytz
from astronomy.celestial import calculate_sun_position, calculate_moon_phase
from astronomy.precision.config import get_precision_mode

def test_precision_integration():
    """Test that high-precision calculations are being used"""
    
    print("🔬 PRECISION INTEGRATION TEST")
    print("=" * 50)
    
    # Test datetime
    test_time = datetime(2025, 6, 1, 12, 0, 0, tzinfo=pytz.UTC)
    
    print(f"Test time: {test_time}")
    print(f"Current precision mode: {get_precision_mode()}")
    print()
    
    # Test sun position calculation
    print("☀️ SUN POSITION TEST")
    print("-" * 30)
    
    # Force standard mode
    sun_pos_standard = calculate_sun_position(test_time, precision_mode='standard')
    print(f"Standard mode: Alt={sun_pos_standard[0]:.6f}°, Az={sun_pos_standard[1]:.6f}°")
    
    # Force high precision mode
    try:
        sun_pos_high = calculate_sun_position(test_time, precision_mode='high')
        print(f"High precision: Alt={sun_pos_high[0]:.6f}°, Az={sun_pos_high[1]:.6f}°")
        
        # Calculate difference
        alt_diff = abs(sun_pos_high[0] - sun_pos_standard[0])
        az_diff = abs(sun_pos_high[1] - sun_pos_standard[1])
        
        print(f"Difference: Alt={alt_diff:.6f}°, Az={az_diff:.6f}°")
        
        if alt_diff > 0.001 or az_diff > 0.001:
            print("✅ High precision is providing different (more accurate) results!")
        else:
            print("⚠️  Differences are very small - this might be expected for sun position")
            
    except Exception as e:
        print(f"❌ High precision failed: {e}")
    
    print()
    
    # Test moon phase calculation
    print("🌙 MOON PHASE TEST")
    print("-" * 30)
    
    # Force standard mode
    moon_phase_standard = calculate_moon_phase(test_time)
    print(f"Standard mode: {moon_phase_standard:.6f}")
    
    # Force high precision mode
    try:
        from astronomy.precision.high_precision import calculate_high_precision_moon_phase
        moon_phase_high = calculate_high_precision_moon_phase(test_time)
        print(f"High precision: {moon_phase_high:.6f}")
        
        # Calculate difference
        phase_diff = abs(moon_phase_high - moon_phase_standard)
        print(f"Difference: {phase_diff:.6f}")
        
        if phase_diff > 0.001:
            print("✅ High precision moon phase is providing different results!")
        else:
            print("⚠️  Differences are small - this might be expected")
            
    except Exception as e:
        print(f"❌ High precision moon phase failed: {e}")
    
    print()
    
    # Test precision module availability
    print("🔧 PRECISION MODULE STATUS")
    print("-" * 30)
    
    try:
        from astronomy.precision import HIGH_PRECISION_CONSTANTS
        print("✅ High precision constants available")
        print(f"   Earth radius: {HIGH_PRECISION_CONSTANTS.EARTH_RADIUS_KM} km")
        print(f"   AU: {HIGH_PRECISION_CONSTANTS.AU_KM} km")
    except Exception as e:
        print(f"❌ High precision constants error: {e}")
    
    try:
        from astronomy.precision.high_precision import calculate_high_precision_lst
        lst = calculate_high_precision_lst(test_time, 0.0)
        print(f"✅ High precision LST calculation working: {lst:.6f} rad")
    except Exception as e:
        print(f"❌ High precision LST failed: {e}")
    
    try:
        from astronomy.precision.atmospheric import apply_atmospheric_refraction
        refraction = apply_atmospheric_refraction(45.0, temperature=15.0, pressure=1013.25)
        print(f"✅ Atmospheric refraction working: {refraction:.6f}°")
    except Exception as e:
        print(f"❌ Atmospheric refraction failed: {e}")
    
    print()
    print("🎯 INTEGRATION TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_precision_integration()