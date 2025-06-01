"""
Tests for Phase 2 High-Precision Functions

This module tests the coordinate transformation, twilight calculation,
and parallax correction functions implemented in Phase 2.
"""

import unittest
import math
from datetime import datetime, timedelta
import pytz
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from astronomy.precision.high_precision import (
    calculate_precise_altaz,
    find_precise_astronomical_twilight,
    calculate_precise_parallax_correction,
    calculate_precise_coordinate_transformation
)
from astronomy.precision.config import set_precision_mode, precision_context
from astronomy.celestial import calculate_altaz, calculate_altaz_precise, find_twilight, transform_coordinates


class TestPreciseAltAz(unittest.TestCase):
    """Test precise altitude/azimuth calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)  # Summer solstice
        self.observer_lat = math.radians(40.0)  # 40°N
        self.observer_lon = math.radians(-74.0)  # 74°W (New York area)
        self.ra = math.radians(180.0)  # 12h RA
        self.dec = math.radians(23.4)  # ~23.4° Dec (near solstice declination)
    
    def test_basic_altaz_calculation(self):
        """Test basic altitude/azimuth calculation"""
        result = calculate_precise_altaz(
            self.dt, self.observer_lat, self.observer_lon, self.ra, self.dec
        )
        
        # Check that result contains expected keys
        expected_keys = ['altitude', 'azimuth', 'altitude_geometric', 'hour_angle', 'air_mass']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that values are reasonable
        self.assertIsInstance(result['altitude'], float)
        self.assertIsInstance(result['azimuth'], float)
        self.assertGreaterEqual(result['altitude'], math.radians(-90))
        self.assertLessEqual(result['altitude'], math.radians(90))
        self.assertGreaterEqual(result['azimuth'], 0)
        self.assertLessEqual(result['azimuth'], 2 * math.pi)
    
    def test_refraction_correction(self):
        """Test atmospheric refraction correction"""
        # Test with refraction
        result_with_refraction = calculate_precise_altaz(
            self.dt, self.observer_lat, self.observer_lon, self.ra, self.dec, 
            include_refraction=True
        )
        
        # Test without refraction
        result_without_refraction = calculate_precise_altaz(
            self.dt, self.observer_lat, self.observer_lon, self.ra, self.dec, 
            include_refraction=False
        )
        
        # Refraction should increase altitude (for positive altitudes)
        if result_with_refraction['altitude_geometric'] > 0:
            self.assertGreater(
                result_with_refraction['altitude'], 
                result_without_refraction['altitude']
            )
    
    def test_air_mass_calculation(self):
        """Test air mass calculation"""
        # Test for object above horizon
        high_dec = math.radians(60.0)  # High declination
        result = calculate_precise_altaz(
            self.dt, self.observer_lat, self.observer_lon, self.ra, high_dec
        )
        
        if result['altitude'] > 0:
            self.assertIsNotNone(result['air_mass'])
            self.assertGreater(result['air_mass'], 1.0)  # Air mass should be > 1
        
        # Test for object below horizon
        low_dec = math.radians(-60.0)  # Low declination
        result = calculate_precise_altaz(
            self.dt, self.observer_lat, self.observer_lon, self.ra, low_dec
        )
        
        if result['altitude'] <= 0:
            self.assertIsNone(result['air_mass'])


class TestPreciseTwilight(unittest.TestCase):
    """Test precise twilight calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dt = datetime(2023, 6, 21, tzinfo=pytz.UTC)  # Summer solstice
        self.observer_lat = math.radians(40.0)  # 40°N
        self.observer_lon = math.radians(-74.0)  # 74°W
    
    def test_civil_twilight(self):
        """Test civil twilight calculation"""
        sunset = find_precise_astronomical_twilight(
            self.dt, self.observer_lat, self.observer_lon, 'civil', 'sunset'
        )
        
        sunrise = find_precise_astronomical_twilight(
            self.dt, self.observer_lat, self.observer_lon, 'civil', 'sunrise'
        )
        
        # Check that results are datetime objects
        self.assertIsInstance(sunset, datetime)
        self.assertIsInstance(sunrise, datetime)
        
        # Check that sunset is after sunrise
        self.assertGreater(sunset, sunrise)
        
        # Check that times are reasonable (within the same day)
        self.assertEqual(sunset.date(), self.dt.date())
        self.assertEqual(sunrise.date(), self.dt.date())
    
    def test_twilight_types(self):
        """Test different twilight types"""
        twilight_types = ['civil', 'nautical', 'astronomical']
        sunset_times = []
        
        for twilight_type in twilight_types:
            sunset = find_precise_astronomical_twilight(
                self.dt, self.observer_lat, self.observer_lon, twilight_type, 'sunset'
            )
            sunset_times.append(sunset)
        
        # For sunset: civil happens first (earliest), then nautical, then astronomical (latest)
        self.assertLess(sunset_times[0], sunset_times[1])  # civil < nautical (earlier)
        self.assertLess(sunset_times[1], sunset_times[2])  # nautical < astronomical (earlier)
    
    def test_invalid_twilight_type(self):
        """Test invalid twilight type"""
        with self.assertRaises(ValueError):
            find_precise_astronomical_twilight(
                self.dt, self.observer_lat, self.observer_lon, 'invalid', 'sunset'
            )
    
    def test_invalid_event_type(self):
        """Test invalid event type"""
        with self.assertRaises(ValueError):
            find_precise_astronomical_twilight(
                self.dt, self.observer_lat, self.observer_lon, 'civil', 'invalid'
            )


class TestParallaxCorrection(unittest.TestCase):
    """Test parallax correction calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        self.observer_lat = math.radians(40.0)
        self.observer_lon = math.radians(-74.0)
        self.ra = math.radians(180.0)
        self.dec = math.radians(0.0)  # On celestial equator
        self.distance_km = 384400.0  # Approximate moon distance
    
    def test_parallax_correction(self):
        """Test basic parallax correction"""
        result = calculate_precise_parallax_correction(
            self.dt, self.observer_lat, self.observer_lon, 
            self.ra, self.dec, self.distance_km
        )
        
        # Check that result contains expected keys
        expected_keys = ['ra_corrected', 'dec_corrected', 'ra_correction', 'dec_correction', 'parallax_angle']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that corrections are reasonable (small for moon distance)
        self.assertLess(abs(result['ra_correction']), math.radians(1.0))  # < 1 degree
        self.assertLess(abs(result['dec_correction']), math.radians(1.0))  # < 1 degree
        
        # Parallax angle should be positive
        self.assertGreater(result['parallax_angle'], 0)
    
    def test_distance_effect(self):
        """Test effect of distance on parallax"""
        # Close object (artificial satellite)
        close_distance = 1000.0  # 1000 km
        close_result = calculate_precise_parallax_correction(
            self.dt, self.observer_lat, self.observer_lon, 
            self.ra, self.dec, close_distance
        )
        
        # Distant object (moon)
        distant_result = calculate_precise_parallax_correction(
            self.dt, self.observer_lat, self.observer_lon, 
            self.ra, self.dec, self.distance_km
        )
        
        # Closer object should have larger parallax
        self.assertGreater(close_result['parallax_angle'], distant_result['parallax_angle'])


class TestCoordinateTransformation(unittest.TestCase):
    """Test coordinate system transformations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        self.observer_lat = math.radians(40.0)
        self.observer_lon = math.radians(-74.0)
    
    def test_equatorial_to_horizontal(self):
        """Test equatorial to horizontal transformation"""
        input_coords = {
            'ra': math.radians(180.0),
            'dec': math.radians(23.4)
        }
        
        result = calculate_precise_coordinate_transformation(
            self.dt, self.observer_lat, self.observer_lon,
            input_coords, 'equatorial', 'horizontal'
        )
        
        # Check that result contains expected keys
        expected_keys = ['altitude', 'azimuth', 'altitude_geometric', 'hour_angle']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that values are reasonable
        self.assertGreaterEqual(result['altitude'], math.radians(-90))
        self.assertLessEqual(result['altitude'], math.radians(90))
        self.assertGreaterEqual(result['azimuth'], 0)
        self.assertLessEqual(result['azimuth'], 2 * math.pi)
    
    def test_horizontal_to_equatorial(self):
        """Test horizontal to equatorial transformation"""
        input_coords = {
            'altitude': math.radians(45.0),
            'azimuth': math.radians(180.0)
        }
        
        result = calculate_precise_coordinate_transformation(
            self.dt, self.observer_lat, self.observer_lon,
            input_coords, 'horizontal', 'equatorial'
        )
        
        # Check that result contains expected keys
        expected_keys = ['ra', 'dec', 'hour_angle']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that values are reasonable
        self.assertGreaterEqual(result['ra'], 0)
        self.assertLessEqual(result['ra'], 2 * math.pi)
        self.assertGreaterEqual(result['dec'], math.radians(-90))
        self.assertLessEqual(result['dec'], math.radians(90))
    
    def test_round_trip_transformation(self):
        """Test round-trip coordinate transformation"""
        original_coords = {
            'ra': math.radians(180.0),
            'dec': math.radians(23.4)
        }
        
        # Transform to horizontal
        horizontal = calculate_precise_coordinate_transformation(
            self.dt, self.observer_lat, self.observer_lon,
            original_coords, 'equatorial', 'horizontal', include_corrections=False
        )
        
        # Transform back to equatorial
        equatorial = calculate_precise_coordinate_transformation(
            self.dt, self.observer_lat, self.observer_lon,
            horizontal, 'horizontal', 'equatorial', include_corrections=False
        )
        
        # Check that we get back close to original coordinates
        ra_diff = abs(equatorial['ra'] - original_coords['ra'])
        dec_diff = abs(equatorial['dec'] - original_coords['dec'])
        
        # Allow for small numerical errors
        self.assertLess(ra_diff, math.radians(0.01))  # < 0.01 degrees
        self.assertLess(dec_diff, math.radians(0.01))  # < 0.01 degrees
    
    def test_same_system_transformation(self):
        """Test transformation within same coordinate system"""
        input_coords = {
            'ra': math.radians(180.0),
            'dec': math.radians(23.4)
        }
        
        result = calculate_precise_coordinate_transformation(
            self.dt, self.observer_lat, self.observer_lon,
            input_coords, 'equatorial', 'equatorial'
        )
        
        # Should return identical coordinates
        self.assertEqual(result, input_coords)
    
    def test_unsupported_transformation(self):
        """Test unsupported coordinate transformation"""
        input_coords = {'ra': 0, 'dec': 0}
        
        with self.assertRaises(ValueError):
            calculate_precise_coordinate_transformation(
                self.dt, self.observer_lat, self.observer_lon,
                input_coords, 'equatorial', 'ecliptic'
            )


class TestIntegrationFunctions(unittest.TestCase):
    """Test integration with main celestial module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        self.observer_lat = math.radians(40.0)
        self.observer_lon = math.radians(-74.0)
        self.ra = math.radians(180.0)
        self.dec = math.radians(23.4)
    
    def test_calculate_altaz_integration(self):
        """Test calculate_altaz function integration"""
        # Test high precision mode
        with precision_context('high'):
            result_high = calculate_altaz_precise(
                self.dt, self.observer_lat, self.observer_lon, self.ra, self.dec
            )
        
        # Test standard mode
        with precision_context('standard'):
            result_standard = calculate_altaz_precise(
                self.dt, self.observer_lat, self.observer_lon, self.ra, self.dec
            )
        
        # Both should return valid results
        self.assertIn('altitude', result_high)
        self.assertIn('altitude', result_standard)
        
        # Results should be different (high precision should be more accurate)
        self.assertNotEqual(result_high['altitude'], result_standard['altitude'])
    
    def test_find_twilight_integration(self):
        """Test find_twilight function integration"""
        # Test high precision mode
        with precision_context('high'):
            twilight_high = find_twilight(
                self.dt, self.observer_lat, self.observer_lon, 'civil', 'sunset'
            )
        
        # Test standard mode
        with precision_context('standard'):
            twilight_standard = find_twilight(
                self.dt, self.observer_lat, self.observer_lon, 'civil', 'sunset'
            )
        
        # Both should return datetime objects
        self.assertIsInstance(twilight_high, datetime)
        self.assertIsInstance(twilight_standard, datetime)
        
        # Results should be different
        self.assertNotEqual(twilight_high, twilight_standard)
    
    def test_transform_coordinates_integration(self):
        """Test transform_coordinates function integration"""
        input_coords = {
            'ra': self.ra,
            'dec': self.dec
        }
        
        # Test high precision mode
        with precision_context('high'):
            result_high = transform_coordinates(
                self.dt, self.observer_lat, self.observer_lon,
                input_coords, 'equatorial', 'horizontal'
            )
        
        # Test standard mode
        with precision_context('standard'):
            result_standard = transform_coordinates(
                self.dt, self.observer_lat, self.observer_lon,
                input_coords, 'equatorial', 'horizontal'
            )
        
        # Both should return valid results
        self.assertIn('altitude', result_high)
        self.assertIn('altitude', result_standard)
        
        # Results should be different
        self.assertNotEqual(result_high['altitude'], result_standard['altitude'])


if __name__ == '__main__':
    unittest.main()