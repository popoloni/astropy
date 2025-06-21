#!/usr/bin/env python3
"""Astronomy accuracy test using astropy as ground truth"""

import sys
import os
import math
import pytz
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our functions
from astronomy import calculate_julian_date, calculate_sun_position, calculate_moon_position

# Import astropy for comparison
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon
from astropy import units as u

def test_julian_date():
    """Test Julian Date calculation"""
    print("=== Testing Julian Date Calculation ===")
    
    test_dates = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2024, 7, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2025, 6, 17, 14, 30, 0, tzinfo=pytz.UTC),
    ]
    
    errors = []
    for test_date in test_dates:
        our_jd = calculate_julian_date(test_date)
        astropy_time = Time(test_date)
        astropy_jd = astropy_time.jd
        error = abs(our_jd - astropy_jd)
        errors.append(error)
        
        print(f"Date: {test_date}")
        print(f"  Our JD:     {our_jd:.6f}")
        print(f"  Astropy JD: {astropy_jd:.6f}")
        print(f"  Error:      {error:.8f} days ({error*24*3600:.3f} seconds)")
    
    max_error = max(errors)
    avg_error = sum(errors) / len(errors)
    
    print(f"\nJulian Date Summary:")
    print(f"  Max error: {max_error:.8f} days ({max_error*24*3600:.3f} seconds)")
    print(f"  Avg error: {avg_error:.8f} days ({avg_error*24*3600:.3f} seconds)")
    
    return max_error < 1e-6, max_error, avg_error

def test_sun_position():
    """Test Sun position calculation"""
    print("\n=== Testing Sun Position Calculation ===")
    
    # Milano location
    location = EarthLocation(lat=45.52*u.deg, lon=9.22*u.deg, height=122*u.m)
    
    test_dates = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2024, 7, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2025, 6, 17, 14, 30, 0, tzinfo=pytz.UTC),
    ]
    
    errors = []
    for test_date in test_dates:
        our_alt, our_az = calculate_sun_position(test_date)
        
        astropy_time = Time(test_date)
        astropy_sun = get_sun(astropy_time)
        astropy_altaz = astropy_sun.transform_to(AltAz(obstime=astropy_time, location=location))
        astropy_alt = astropy_altaz.alt.degree
        astropy_az = astropy_altaz.az.degree
        
        # Calculate angular separation
        error = angular_separation(our_alt, our_az, astropy_alt, astropy_az)
        errors.append(error)
        
        print(f"Date: {test_date}")
        print(f"  Our Sun:     Alt={our_alt:.3f}°, Az={our_az:.3f}°")
        print(f"  Astropy Sun: Alt={astropy_alt:.3f}°, Az={astropy_az:.3f}°")
        print(f"  Error:       {error:.3f}° ({error*60:.1f} arcmin)")
    
    max_error = max(errors)
    avg_error = sum(errors) / len(errors)
    
    print(f"\nSun Position Summary:")
    print(f"  Max error: {max_error:.3f}° ({max_error*60:.1f} arcmin)")
    print(f"  Avg error: {avg_error:.3f}° ({avg_error*60:.1f} arcmin)")
    
    return max_error < 2.0, max_error, avg_error

def test_moon_position():
    """Test Moon position calculation"""
    print("\n=== Testing Moon Position Calculation ===")
    
    # Milano location
    location = EarthLocation(lat=45.52*u.deg, lon=9.22*u.deg, height=122*u.m)
    
    test_dates = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2024, 7, 15, 12, 0, 0, tzinfo=pytz.UTC),
        datetime(2025, 6, 17, 14, 30, 0, tzinfo=pytz.UTC),
    ]
    
    errors = []
    for test_date in test_dates:
        our_alt, our_az = calculate_moon_position(test_date)
        
        astropy_time = Time(test_date)
        astropy_moon = get_moon(astropy_time)
        astropy_altaz = astropy_moon.transform_to(AltAz(obstime=astropy_time, location=location))
        astropy_alt = astropy_altaz.alt.degree
        astropy_az = astropy_altaz.az.degree
        
        # Calculate angular separation
        error = angular_separation(our_alt, our_az, astropy_alt, astropy_az)
        errors.append(error)
        
        print(f"Date: {test_date}")
        print(f"  Our Moon:     Alt={our_alt:.3f}°, Az={our_az:.3f}°")
        print(f"  Astropy Moon: Alt={astropy_alt:.3f}°, Az={astropy_az:.3f}°")
        print(f"  Error:        {error:.3f}° ({error*60:.1f} arcmin)")
    
    max_error = max(errors)
    avg_error = sum(errors) / len(errors)
    
    print(f"\nMoon Position Summary:")
    print(f"  Max error: {max_error:.3f}° ({max_error*60:.1f} arcmin)")
    print(f"  Avg error: {avg_error:.3f}° ({avg_error*60:.1f} arcmin)")
    
    return max_error < 5.0, max_error, avg_error

def angular_separation(alt1, az1, alt2, az2):
    """Calculate angular separation between two positions"""
    alt1_rad = math.radians(alt1)
    az1_rad = math.radians(az1)
    alt2_rad = math.radians(alt2)
    az2_rad = math.radians(az2)
    
    cos_sep = (math.sin(alt1_rad) * math.sin(alt2_rad) + 
               math.cos(alt1_rad) * math.cos(alt2_rad) * math.cos(az2_rad - az1_rad))
    cos_sep = max(-1.0, min(1.0, cos_sep))
    
    return math.degrees(math.acos(cos_sep))

def main():
    print("🌟 ASTRONOMY FUNCTION ACCURACY TESTING")
    print("Using Astropy v6.0.1 as Ground Truth")
    print("="*60)
    
    results = []
    
    try:
        jd_passed, jd_max, jd_avg = test_julian_date()
        sun_passed, sun_max, sun_avg = test_sun_position()
        moon_passed, moon_max, moon_avg = test_moon_position()
        
        results = [
            ("Julian Date", jd_passed, jd_max, jd_avg),
            ("Sun Position", sun_passed, sun_max, sun_avg),
            ("Moon Position", moon_passed, moon_max, moon_avg)
        ]
        
        print("\n" + "="*60)
        print("COMPREHENSIVE ACCURACY REPORT")
        print("="*60)
        
        for test_name, passed, max_err, avg_err in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            if test_name == "Julian Date":
                print(f"{test_name}: {status}")
                print(f"  Max error: {max_err:.8f} days ({max_err*24*3600:.3f} seconds)")
                print(f"  Avg error: {avg_err:.8f} days ({avg_err*24*3600:.3f} seconds)")
            else:
                print(f"{test_name}: {status}")
                print(f"  Max error: {max_err:.3f}° ({max_err*60:.1f} arcmin)")
                print(f"  Avg error: {avg_err:.3f}° ({avg_err*60:.1f} arcmin)")
        
        all_passed = all(result[1] for result in results)
        print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        # Generate detailed assessment
        print("\n" + "="*60)
        print("ACCURACY ASSESSMENT & RECOMMENDATIONS")
        print("="*60)
        
        print("\n📊 ACCURACY LEVELS:")
        print(f"Julian Date: {'✅ EXCELLENT' if jd_max < 1e-6 else '⚠️ NEEDS IMPROVEMENT'}")
        print(f"  - Sub-second accuracy achieved: {jd_max*24*3600:.3f}s max error")
        
        if sun_max < 0.1:
            sun_status = "✅ EXCELLENT"
        elif sun_max < 0.5:
            sun_status = "✅ GOOD"
        elif sun_max < 2.0:
            sun_status = "⚠️ ACCEPTABLE"
        else:
            sun_status = "❌ POOR"
        
        print(f"Sun Position: {sun_status}")
        print(f"  - Angular accuracy: {sun_max*60:.1f} arcmin max error")
        
        if moon_max < 0.5:
            moon_status = "✅ EXCELLENT"
        elif moon_max < 2.0:
            moon_status = "✅ GOOD"
        elif moon_max < 5.0:
            moon_status = "⚠️ ACCEPTABLE"
        else:
            moon_status = "❌ POOR"
            
        print(f"Moon Position: {moon_status}")
        print(f"  - Angular accuracy: {moon_max*60:.1f} arcmin max error")
        
        print("\n🔧 IMPROVEMENT RECOMMENDATIONS:")
        if sun_max > 0.5:
            print("- Sun Position: Consider implementing VSOP87 theory for higher accuracy")
        if moon_max > 2.0:
            print("- Moon Position: Consider implementing ELP2000 lunar theory")
        if sun_max > 0.1 or moon_max > 1.0:
            print("- Consider adding atmospheric refraction corrections")
            print("- Consider adding nutation and aberration corrections")
        
        print("\n📈 FUNCTION COVERAGE:")
        tested_functions = [
            "calculate_julian_date", "calculate_sun_position", "calculate_moon_position"
        ]
        for func in tested_functions:
            print(f"  ✅ {func}")
        
        print(f"\nTotal functions tested: {len(tested_functions)}")
        print("Additional functions available for testing:")
        print("  - calculate_moon_phase, calculate_altaz, coordinate conversions")
        
        # Save results to JSON
        import json
        report_data = {
            "test_results": {
                "julian_date": {"max_error_days": float(jd_max), "avg_error_days": float(jd_avg), "passed": bool(jd_passed)},
                "sun_position": {"max_error_degrees": float(sun_max), "avg_error_degrees": float(sun_avg), "passed": bool(sun_passed)},
                "moon_position": {"max_error_degrees": float(moon_max), "avg_error_degrees": float(moon_avg), "passed": bool(moon_passed)}
            },
            "overall_passed": bool(all_passed),
            "test_date": str(datetime.now()),
            "astropy_version": "6.0.1"
        }
        
        with open('tests/astronomy_accuracy_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: tests/astronomy_accuracy_report.json")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
