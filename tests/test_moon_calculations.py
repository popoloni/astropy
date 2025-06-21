#!/usr/bin/env python3
"""
Unit tests for moon calculations using astropy library for verification.

This test suite compares our custom moon calculations against the astropy library
to ensure accuracy and identify any calculation errors.
"""

import unittest
import math
from datetime import datetime, timedelta
import pytz

# Import astropy for reference calculations
try:
    from astropy.time import Time
    from astropy.coordinates import get_moon, get_sun, EarthLocation, AltAz
    from astropy import units as u
    import astropy.coordinates as coord
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    print("Warning: astropy not available. Installing...")

# Import our moon calculation functions
from astronomy.celestial import calculate_moon_phase, calculate_moon_position, get_moon_phase_icon
from astronomy.time_utils import calculate_julian_date


class TestMoonCalculations(unittest.TestCase):
    """Test suite for moon calculation accuracy."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not ASTROPY_AVAILABLE:
            self.skipTest("astropy library not available")
        
        # Test dates - including various moon phases
        self.test_dates = [
            datetime(2024, 1, 11, 12, 0, 0, tzinfo=pytz.UTC),  # New Moon
            datetime(2024, 1, 18, 12, 0, 0, tzinfo=pytz.UTC),  # First Quarter  
            datetime(2024, 1, 25, 12, 0, 0, tzinfo=pytz.UTC),  # Full Moon
            datetime(2024, 2, 2, 12, 0, 0, tzinfo=pytz.UTC),   # Last Quarter
            datetime(2024, 6, 21, 12, 0, 0, tzinfo=pytz.UTC),  # Summer solstice
            datetime(2024, 12, 21, 12, 0, 0, tzinfo=pytz.UTC), # Winter solstice
        ]
        
        # Observer location (Milan, Italy - same as application)
        self.observer_location = EarthLocation(
            lat=45.4642 * u.deg,
            lon=9.1900 * u.deg,
            height=122 * u.m
        )
    
    def test_moon_phase_accuracy(self):
        """Test moon phase calculation accuracy against astropy."""
        print("\n🌙 Testing Moon Phase Calculations")
        print("=" * 50)
        
        for test_date in self.test_dates:
            with self.subTest(date=test_date):
                # Our calculation
                our_phase = calculate_moon_phase(test_date)
                
                # Astropy reference calculation
                time_astropy = Time(test_date)
                moon_astropy = get_moon(time_astropy)
                sun_astropy = get_sun(time_astropy)
                
                # Calculate phase angle using astropy
                separation = moon_astropy.separation(sun_astropy)
                # Phase angle is supplementary to separation
                phase_angle = 180 * u.deg - separation
                
                # Convert to illuminated fraction (0 = new, 0.5 = full, 1 = new)
                astropy_phase = (1 + math.cos(phase_angle.to(u.rad).value)) / 2
                
                # Convert our phase to match astropy's convention if needed
                # Our phase: 0=new, 0.5=full, 1=new
                # Astropy phase: 0=new, 0.5=full, 1=new
                
                phase_diff = abs(our_phase - astropy_phase)
                
                print(f"  Date: {test_date.strftime('%Y-%m-%d')}")
                print(f"    Our phase: {our_phase:.4f}")
                print(f"    Astropy:   {astropy_phase:.4f}")
                print(f"    Difference: {phase_diff:.4f}")
                
                # Get phase names
                our_icon, our_name = get_moon_phase_icon(our_phase)
                astropy_icon, astropy_name = get_moon_phase_icon(astropy_phase)
                
                print(f"    Our name: {our_name} {our_icon}")
                print(f"    Expected: {astropy_name} {astropy_icon}")
                
                # Assert accuracy within 5% (0.05)
                self.assertLess(phase_diff, 0.05, 
                    f"Moon phase calculation error too large on {test_date}: "
                    f"our={our_phase:.4f}, astropy={astropy_phase:.4f}, "
                    f"diff={phase_diff:.4f}")
                
                print("    ✅ Passed\n")
    
    def test_moon_position_accuracy(self):
        """Test moon position calculation accuracy against astropy."""
        print("\n🌙 Testing Moon Position Calculations")
        print("=" * 50)
        
        for test_date in self.test_dates:
            with self.subTest(date=test_date):
                # Our calculation
                our_alt, our_az = calculate_moon_position(test_date)
                
                # Astropy reference calculation
                time_astropy = Time(test_date)
                moon_astropy = get_moon(time_astropy)
                
                # Transform to horizontal coordinates for our location
                altaz_frame = AltAz(obstime=time_astropy, location=self.observer_location)
                moon_altaz = moon_astropy.transform_to(altaz_frame)
                
                astropy_alt = moon_altaz.alt.deg
                astropy_az = moon_altaz.az.deg
                
                alt_diff = abs(our_alt - astropy_alt)
                az_diff = abs(our_az - astropy_az)
                
                # Handle azimuth wraparound
                if az_diff > 180:
                    az_diff = 360 - az_diff
                
                print(f"  Date: {test_date.strftime('%Y-%m-%d %H:%M UTC')}")
                print(f"    Our position: Alt={our_alt:.2f}°, Az={our_az:.2f}°")
                print(f"    Astropy:      Alt={astropy_alt:.2f}°, Az={astropy_az:.2f}°")
                print(f"    Differences:  Alt={alt_diff:.2f}°, Az={az_diff:.2f}°")
                
                # Assert accuracy within 2 degrees for altitude, 5 degrees for azimuth
                self.assertLess(alt_diff, 2.0,
                    f"Moon altitude error too large on {test_date}: "
                    f"our={our_alt:.2f}°, astropy={astropy_alt:.2f}°, "
                    f"diff={alt_diff:.2f}°")
                
                self.assertLess(az_diff, 5.0,
                    f"Moon azimuth error too large on {test_date}: "
                    f"our={our_az:.2f}°, astropy={astropy_az:.2f}°, "
                    f"diff={az_diff:.2f}°")
                
                print("    ✅ Passed\n")
    
    def test_known_moon_phases(self):
        """Test against known moon phase dates."""
        print("\n🌙 Testing Known Moon Phase Dates")
        print("=" * 50)
        
        # Known moon phase dates for 2024 (approximate)
        known_phases = [
            (datetime(2024, 1, 11, 11, 57, tzinfo=pytz.UTC), "New Moon"),
            (datetime(2024, 1, 17, 22, 53, tzinfo=pytz.UTC), "First Quarter"),
            (datetime(2024, 1, 25, 17, 54, tzinfo=pytz.UTC), "Full Moon"),
            (datetime(2024, 2, 2, 23, 18, tzinfo=pytz.UTC), "Last Quarter"),
        ]
        
        for test_date, expected_phase_name in known_phases:
            with self.subTest(date=test_date, expected=expected_phase_name):
                our_phase = calculate_moon_phase(test_date)
                our_icon, our_name = get_moon_phase_icon(our_phase)
                
                print(f"  Date: {test_date.strftime('%Y-%m-%d %H:%M UTC')}")
                print(f"    Expected: {expected_phase_name}")
                print(f"    Our result: {our_name} {our_icon} (phase={our_phase:.3f})")
                
                # Check if the phase name matches (allowing for some tolerance)
                phase_matches = (
                    (expected_phase_name == "New Moon" and our_name == "New Moon") or
                    (expected_phase_name == "First Quarter" and our_name == "First Quarter") or
                    (expected_phase_name == "Full Moon" and our_name == "Full Moon") or
                    (expected_phase_name == "Last Quarter" and our_name == "Last Quarter")
                )
                
                self.assertTrue(phase_matches,
                    f"Moon phase name mismatch on {test_date}: "
                    f"expected={expected_phase_name}, our={our_name}")
                
                print("    ✅ Passed\n")
    
    def test_phase_consistency(self):
        """Test that moon phases progress consistently over time."""
        print("\n🌙 Testing Moon Phase Consistency")
        print("=" * 50)
        
        # Test over one lunar month (~29.5 days)
        start_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        phases = []
        
        for day in range(30):
            test_date = start_date + timedelta(days=day)
            phase = calculate_moon_phase(test_date)
            phases.append((test_date, phase))
        
        print("  Checking phase progression over 30 days:")
        
        # Check that phases change gradually (no sudden jumps)
        for i in range(1, len(phases)):
            prev_date, prev_phase = phases[i-1]
            curr_date, curr_phase = phases[i]
            
            # Calculate phase difference, handling wraparound
            phase_diff = curr_phase - prev_phase
            if phase_diff < -0.5:  # Wraparound from 1.0 to 0.0
                phase_diff += 1.0
            elif phase_diff > 0.5:  # Wraparound from 0.0 to 1.0
                phase_diff -= 1.0
            
            # Phase should change by approximately 1/29.5 ≈ 0.034 per day
            expected_change = 1.0 / 29.5
            
            print(f"    Day {i:2d}: {curr_date.strftime('%m-%d')} "
                  f"Phase={curr_phase:.3f}, Change={phase_diff:.3f}")
            
            # Allow for some variation in daily change
            self.assertLess(abs(abs(phase_diff) - expected_change), 0.02,
                f"Unexpected phase change on day {i}: "
                f"change={phase_diff:.3f}, expected≈{expected_change:.3f}")
        
        print("    ✅ Phase progression is consistent\n")
    
    def test_current_moon_phase(self):
        """Test the current moon phase to verify today's calculation."""
        print("\n🌙 Testing Current Moon Phase")
        print("=" * 50)
        
        now = datetime.now(pytz.UTC)
        our_phase = calculate_moon_phase(now)
        our_icon, our_name = get_moon_phase_icon(our_phase)
        
        # Astropy reference
        time_astropy = Time(now)
        moon_astropy = get_moon(time_astropy)
        sun_astropy = get_sun(time_astropy)
        
        separation = moon_astropy.separation(sun_astropy)
        phase_angle = 180 * u.deg - separation
        astropy_phase = (1 + math.cos(phase_angle.to(u.rad).value)) / 2
        astropy_icon, astropy_name = get_moon_phase_icon(astropy_phase)
        
        print(f"  Current time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Our calculation: {our_name} {our_icon} (phase={our_phase:.3f})")
        print(f"  Astropy reference: {astropy_name} {astropy_icon} (phase={astropy_phase:.3f})")
        
        phase_diff = abs(our_phase - astropy_phase)
        print(f"  Phase difference: {phase_diff:.3f}")
        
        if phase_diff < 0.05:
            print("  ✅ Current moon phase calculation is accurate!")
        else:
            print(f"  ⚠️ Current moon phase may be inaccurate (diff={phase_diff:.3f})")
        
        # This is informational, not a hard assertion since we don't know the exact current phase
        return our_name, astropy_name


def install_astropy():
    """Install astropy if not available."""
    try:
        import subprocess
        import sys
        print("Installing astropy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "astropy"])
        print("Astropy installed successfully!")
        return True
    except Exception as e:
        print(f"Failed to install astropy: {e}")
        return False


if __name__ == '__main__':
    # Try to install astropy if not available
    if not ASTROPY_AVAILABLE:
        if install_astropy():
            try:
                from astropy.time import Time
                from astropy.coordinates import get_moon, get_sun, EarthLocation, AltAz
                from astropy import units as u
                import astropy.coordinates as coord
                ASTROPY_AVAILABLE = True
                print("Astropy successfully imported after installation!")
            except ImportError:
                print("Failed to import astropy after installation.")
    
    if ASTROPY_AVAILABLE:
        # Run the tests
        unittest.main(verbosity=2)
    else:
        print("Cannot run tests without astropy library.")
        print("Please install astropy manually: pip install astropy") 