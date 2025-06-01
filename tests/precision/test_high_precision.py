"""
Tests for high-precision astronomical calculations
"""

import pytest
import math
import sys
import os
from datetime import datetime
import pytz

# Add the astropy root directory to path (two levels up from tests/precision/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from astronomy.precision.high_precision import (
    calculate_high_precision_lst,
    calculate_high_precision_sun_position,
    calculate_high_precision_moon_position,
    calculate_high_precision_moon_phase
)
from astronomy.precision.utils import calculate_julian_date

class TestHighPrecisionCalculations:
    
    def test_high_precision_lst(self):
        """Test high-precision LST calculation"""
        # Test with known date
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)  # Summer solstice
        observer_lon = 0.0  # Greenwich
        
        lst_hours = calculate_high_precision_lst(dt, observer_lon)
        
        # LST should be between 0 and 24 hours
        assert 0.0 <= lst_hours < 24.0
        
        # For Greenwich at noon on summer solstice, LST should be around 6 hours
        # (rough check - exact value depends on year and precision)
        assert 5.0 <= lst_hours <= 7.0
    
    def test_high_precision_lst_longitude_effect(self):
        """Test LST changes with longitude"""
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        lst_greenwich = calculate_high_precision_lst(dt, 0.0)
        lst_east = calculate_high_precision_lst(dt, 15.0)  # 15 degrees east
        
        # 15 degrees east should add 1 hour to LST
        expected_diff = 1.0
        actual_diff = (lst_east - lst_greenwich) % 24.0
        
        assert abs(actual_diff - expected_diff) < 0.01  # Within 0.01 hours
    
    def test_high_precision_sun_position(self):
        """Test high-precision sun position calculation"""
        # Test with known date
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)  # Summer solstice noon
        
        sun_pos = calculate_high_precision_sun_position(dt)
        
        # Check return format
        assert isinstance(sun_pos, dict)
        assert 'ra' in sun_pos
        assert 'dec' in sun_pos
        assert 'distance' in sun_pos
        
        # Check value ranges
        assert 0.0 <= sun_pos['ra'] < 360.0
        assert -90.0 <= sun_pos['dec'] <= 90.0
        assert 0.9 <= sun_pos['distance'] <= 1.1  # Earth-Sun distance in AU
        
        # On summer solstice, sun should be at maximum declination (~23.4°)
        assert sun_pos['dec'] > 23.0
    
    def test_high_precision_moon_position(self):
        """Test high-precision moon position calculation"""
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        moon_pos = calculate_high_precision_moon_position(dt)
        
        # Check return format
        assert isinstance(moon_pos, dict)
        assert 'ra' in moon_pos
        assert 'dec' in moon_pos
        assert 'distance' in moon_pos
        
        # Check value ranges
        assert 0.0 <= moon_pos['ra'] < 360.0
        assert -90.0 <= moon_pos['dec'] <= 90.0
        assert 350000.0 <= moon_pos['distance'] <= 410000.0  # Moon distance in km
    
    def test_high_precision_moon_phase(self):
        """Test high-precision moon phase calculation"""
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        moon_phase = calculate_high_precision_moon_phase(dt)
        
        # Check return format
        assert isinstance(moon_phase, dict)
        assert 'phase_angle' in moon_phase
        assert 'illumination' in moon_phase
        assert 'phase_name' in moon_phase
        
        # Check value ranges
        assert 0.0 <= moon_phase['phase_angle'] <= 360.0
        assert 0.0 <= moon_phase['illumination'] <= 1.0
        assert isinstance(moon_phase['phase_name'], str)
        
        # Phase name should be one of the expected values
        valid_phases = [
            "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
            "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
        ]
        assert moon_phase['phase_name'] in valid_phases
    
    def test_precision_consistency(self):
        """Test that calculations are consistent across multiple calls"""
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        # Calculate multiple times
        lst1 = calculate_high_precision_lst(dt, 0.0)
        lst2 = calculate_high_precision_lst(dt, 0.0)
        assert abs(lst1 - lst2) < 1e-10
        
        sun1 = calculate_high_precision_sun_position(dt)
        sun2 = calculate_high_precision_sun_position(dt)
        assert abs(sun1['ra'] - sun2['ra']) < 1e-10
        assert abs(sun1['dec'] - sun2['dec']) < 1e-10
    
    def test_timezone_handling(self):
        """Test that timezone conversion works correctly"""
        # Same instant in different timezones
        dt_utc = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        dt_est = dt_utc.astimezone(pytz.timezone('US/Eastern'))
        
        lst_utc = calculate_high_precision_lst(dt_utc, 0.0)
        lst_est = calculate_high_precision_lst(dt_est, 0.0)
        
        # Should give same result regardless of input timezone
        assert abs(lst_utc - lst_est) < 1e-10
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with very old date
        dt_old = datetime(1900, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        lst_old = calculate_high_precision_lst(dt_old, 0.0)
        assert 0.0 <= lst_old < 24.0
        
        # Test with future date
        dt_future = datetime(2100, 12, 31, 23, 59, 59, tzinfo=pytz.UTC)
        lst_future = calculate_high_precision_lst(dt_future, 0.0)
        assert 0.0 <= lst_future < 24.0
        
        # Test with extreme longitudes
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        lst_west = calculate_high_precision_lst(dt, -180.0)
        lst_east = calculate_high_precision_lst(dt, 180.0)
        assert 0.0 <= lst_west < 24.0
        assert 0.0 <= lst_east < 24.0

if __name__ == '__main__':
    pytest.main([__file__])