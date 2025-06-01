#!/usr/bin/env python3
"""
Phase 3 High-Precision Functions Test Suite

This module contains comprehensive tests for Phase 3 advanced features including:
- Performance benchmarking system
- Advanced caching mechanisms
- Enhanced atmospheric modeling
- Validation and error handling
- Diagnostic tools

Author: OpenHands AI Assistant
Date: 2025-06-01
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
import math
import time
from datetime import datetime, timedelta
import pytz

# Import Phase 3 components
try:
    from astronomy.precision import (
        # Benchmarking
        PerformanceBenchmark,
        AstronomicalBenchmarkSuite,
        performance_profiler,
        
        # Advanced caching
        AdvancedLRUCache,
        MultiLevelCache,
        advanced_cache,
        
        # Enhanced atmospheric modeling
        AdvancedAtmosphericModel,
        AtmosphericConditions,
        RefractionModel,
        WeatherDataProvider,
        
        # Validation and error handling
        InputValidator,
        ValidationLevel,
        ValidationError,
        ErrorRecoveryManager,
        AccuracyAssessment,
        validate_inputs,
        with_diagnostics,
        
        # Core functions for testing
        calculate_high_precision_sun_position,
        precision_context,
        get_phase3_status
    )
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False


@unittest.skipUnless(PHASE3_AVAILABLE, "Phase 3 components not available")
class TestPerformanceBenchmarking(unittest.TestCase):
    """Test performance benchmarking system"""
    
    def setUp(self):
        self.benchmark = PerformanceBenchmark()
        self.test_dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
    
    def test_benchmark_function(self):
        """Test basic function benchmarking"""
        def simple_function(x, y):
            time.sleep(0.001)  # Small delay
            return x + y
        
        results = self.benchmark.benchmark_function(
            simple_function, 1, 2, iterations=5
        )
        
        self.assertIn('mean', results)
        self.assertIn('median', results)
        self.assertIn('success_rate', results)
        self.assertEqual(results['success_rate'], 1.0)
        self.assertGreater(results['mean'], 0)
    
    def test_benchmark_memory(self):
        """Test memory usage benchmarking"""
        def memory_function():
            data = [i for i in range(1000)]
            return sum(data)
        
        results = self.benchmark.benchmark_memory(memory_function)
        
        self.assertIn('current_memory', results)
        self.assertIn('peak_memory', results)
        self.assertIn('success', results)
        self.assertTrue(results['success'])
        self.assertGreater(results['peak_memory'], 0)
    
    def test_accuracy_comparison(self):
        """Test accuracy comparison between functions"""
        def func1():
            return {'value': 1.0}
        
        def func2():
            return {'value': 1.001}
        
        results = self.benchmark.compare_accuracy(func1, func2)
        
        self.assertIn('success', results)
        self.assertTrue(results['success'])
        if 'differences' in results:
            self.assertIn('value', results['differences'])
    
    def test_astronomical_benchmark_suite(self):
        """Test astronomical benchmark suite (quick version)"""
        suite = AstronomicalBenchmarkSuite()
        
        # Test with minimal iterations for speed
        results = suite.benchmark_sun_position(iterations=2)
        
        self.assertIn('high_precision', results)
        self.assertIn('memory_usage', results)
        self.assertIn('accuracy_comparison', results)


@unittest.skipUnless(PHASE3_AVAILABLE, "Phase 3 components not available")
class TestAdvancedCaching(unittest.TestCase):
    """Test advanced caching system"""
    
    def test_advanced_lru_cache(self):
        """Test advanced LRU cache"""
        cache = AdvancedLRUCache(max_size=10, max_memory_mb=1.0)
        
        # Test cache operations
        found, value = cache.get('test_func', (1, 2), {})
        self.assertFalse(found)
        
        cache.put('test_func', (1, 2), {}, 'result')
        found, value = cache.get('test_func', (1, 2), {})
        self.assertTrue(found)
        self.assertEqual(value, 'result')
        
        # Test cache stats
        stats = cache.get_stats()
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('hit_rate', stats)
    
    def test_multi_level_cache(self):
        """Test multi-level cache"""
        cache = MultiLevelCache(
            memory_cache_size=10,
            memory_cache_mb=1.0,
            enable_persistent=False  # Disable for testing
        )
        
        # Test cache operations
        found, value = cache.get('test_func', (1, 2), {})
        self.assertFalse(found)
        
        cache.put('test_func', (1, 2), {}, 'result')
        found, value = cache.get('test_func', (1, 2), {})
        self.assertTrue(found)
        self.assertEqual(value, 'result')
    
    def test_advanced_cache_decorator(self):
        """Test advanced cache decorator"""
        call_count = 0
        
        @advanced_cache(ttl=60.0, use_persistent=False)
        def cached_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = cached_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Second call (should be cached)
        result2 = cached_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Different parameters
        result3 = cached_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)  # Should increment


@unittest.skipUnless(PHASE3_AVAILABLE, "Phase 3 components not available")
class TestEnhancedAtmosphericModeling(unittest.TestCase):
    """Test enhanced atmospheric modeling"""
    
    def setUp(self):
        self.model = AdvancedAtmosphericModel()
        self.standard_conditions = AtmosphericConditions()
    
    def test_atmospheric_conditions(self):
        """Test atmospheric conditions class"""
        conditions = AtmosphericConditions(
            temperature_c=20.0,
            pressure_hpa=1020.0,
            humidity_percent=60.0,
            wavelength_nm=550.0
        )
        
        self.assertEqual(conditions.temperature_c, 20.0)
        self.assertEqual(conditions.pressure_hpa, 1020.0)
        self.assertEqual(conditions.humidity_percent, 60.0)
        self.assertEqual(conditions.wavelength_nm, 550.0)
        
        # Test refractivity calculation
        refractivity = conditions.get_refractivity()
        self.assertIsInstance(refractivity, float)
        self.assertGreater(refractivity, 0)
    
    def test_refraction_models(self):
        """Test different refraction models"""
        altitude_rad = math.radians(30)
        
        models = [
            RefractionModel.BENNETT,
            RefractionModel.AUER_STANDISH,
            RefractionModel.HOHENKERK_SINCLAIR,
            RefractionModel.SAEMUNDSSON,
            RefractionModel.SIMPLE
        ]
        
        for model in models:
            refraction = self.model.calculate_refraction(
                altitude_rad, self.standard_conditions, model
            )
            self.assertIsInstance(refraction, float)
            self.assertGreater(refraction, 0)
            self.assertLess(refraction, math.radians(1))  # Should be less than 1 degree
    
    def test_chromatic_refraction(self):
        """Test wavelength-dependent refraction"""
        altitude_rad = math.radians(30)
        wavelengths = [400, 500, 600, 700, 800]
        
        results = self.model.calculate_wavelength_dependent_refraction(
            altitude_rad, wavelengths, self.standard_conditions
        )
        
        self.assertEqual(len(results), len(wavelengths))
        for wavelength in wavelengths:
            self.assertIn(wavelength, results)
            self.assertIsInstance(results[wavelength], float)
            self.assertGreater(results[wavelength], 0)
    
    def test_air_mass_calculation(self):
        """Test air mass calculation"""
        altitudes = [10, 30, 60, 85]
        
        for alt_deg in altitudes:
            alt_rad = math.radians(alt_deg)
            air_mass = self.model.calculate_air_mass(
                alt_rad, include_refraction=True, conditions=self.standard_conditions
            )
            
            self.assertIsInstance(air_mass, float)
            self.assertGreater(air_mass, 1.0)  # Should be > 1
            if alt_deg > 60:
                self.assertLess(air_mass, 2.0)  # Should be reasonable for high altitudes
    
    def test_gravitational_deflection(self):
        """Test gravitational light deflection"""
        # Test object far from Sun
        ra_obj = math.radians(0)
        dec_obj = math.radians(0)
        ra_sun = math.radians(180)  # Opposite side
        dec_sun = math.radians(0)
        
        delta_ra, delta_dec = self.model.calculate_gravitational_deflection(
            ra_obj, dec_obj, ra_sun, dec_sun
        )
        
        # Should be very small for objects far from Sun
        self.assertIsInstance(delta_ra, float)
        self.assertIsInstance(delta_dec, float)
        self.assertLess(abs(delta_ra), math.radians(0.1))
        self.assertLess(abs(delta_dec), math.radians(0.1))
    
    def test_stellar_aberration(self):
        """Test stellar aberration calculation"""
        ra = math.radians(90)
        dec = math.radians(23.4)
        earth_velocity = (29.8, 0, 0)  # km/s, roughly Earth's orbital velocity
        
        delta_ra, delta_dec = self.model.calculate_stellar_aberration(
            ra, dec, earth_velocity
        )
        
        self.assertIsInstance(delta_ra, float)
        self.assertIsInstance(delta_dec, float)
        # Aberration should be small but measurable
        self.assertLess(abs(delta_ra), math.radians(0.01))  # < 0.01 degrees
        self.assertLess(abs(delta_dec), math.radians(0.01))


@unittest.skipUnless(PHASE3_AVAILABLE, "Phase 3 components not available")
class TestValidationAndErrorHandling(unittest.TestCase):
    """Test validation and error handling system"""
    
    def setUp(self):
        self.validator = InputValidator(ValidationLevel.NORMAL)
    
    def test_datetime_validation(self):
        """Test datetime validation"""
        # Valid datetime
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        validated_dt = self.validator.validate_datetime(dt)
        self.assertEqual(validated_dt, dt)
        
        # Invalid datetime (None)
        with self.assertRaises(ValidationError):
            self.validator.validate_datetime(None)
        
        # Invalid type
        with self.assertRaises(ValidationError):
            self.validator.validate_datetime("not a datetime")
    
    def test_angle_validation(self):
        """Test angle validation"""
        # Valid angle
        angle = math.pi / 4
        validated_angle = self.validator.validate_angle(angle)
        self.assertEqual(validated_angle, angle)
        
        # Invalid angle (None)
        with self.assertRaises(ValidationError):
            self.validator.validate_angle(None)
        
        # Invalid type
        with self.assertRaises(ValidationError):
            self.validator.validate_angle("not a number")
        
        # Out of range
        with self.assertRaises(ValidationError):
            self.validator.validate_angle(10, min_value=0, max_value=5)
    
    def test_latitude_validation(self):
        """Test latitude validation"""
        # Valid latitude
        lat = math.radians(40.0)
        validated_lat = self.validator.validate_latitude(lat)
        self.assertEqual(validated_lat, lat)
        
        # Invalid latitude (too large)
        with self.assertRaises(ValidationError):
            self.validator.validate_latitude(math.radians(95.0))
        
        # Invalid latitude (too small)
        with self.assertRaises(ValidationError):
            self.validator.validate_latitude(math.radians(-95.0))
    
    def test_longitude_validation(self):
        """Test longitude validation"""
        # Valid longitude
        lon = math.radians(-74.0)
        validated_lon = self.validator.validate_longitude(lon)
        self.assertEqual(validated_lon, lon)
        
        # Invalid longitude (too large)
        with self.assertRaises(ValidationError):
            self.validator.validate_longitude(math.radians(185.0))
    
    def test_precision_mode_validation(self):
        """Test precision mode validation"""
        # Valid modes
        for mode in ['standard', 'high', 'auto']:
            validated_mode = self.validator.validate_precision_mode(mode)
            self.assertEqual(validated_mode, mode)
        
        # None should be allowed
        validated_none = self.validator.validate_precision_mode(None)
        self.assertIsNone(validated_none)
        
        # Invalid mode
        with self.assertRaises(ValidationError):
            self.validator.validate_precision_mode('invalid')
    
    def test_accuracy_assessment(self):
        """Test accuracy assessment tools"""
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        # Sun position accuracy
        sun_accuracy = AccuracyAssessment.estimate_sun_position_accuracy(dt, 'high')
        self.assertIn('ra_accuracy_arcsec', sun_accuracy)
        self.assertIn('dec_accuracy_arcsec', sun_accuracy)
        self.assertIsInstance(sun_accuracy['ra_accuracy_arcsec'], float)
        self.assertGreater(sun_accuracy['ra_accuracy_arcsec'], 0)
        
        # Moon position accuracy
        moon_accuracy = AccuracyAssessment.estimate_moon_position_accuracy(dt, 'high')
        self.assertIn('ra_accuracy_arcsec', moon_accuracy)
        self.assertIn('dec_accuracy_arcsec', moon_accuracy)
        self.assertIsInstance(moon_accuracy['ra_accuracy_arcsec'], float)
        self.assertGreater(moon_accuracy['ra_accuracy_arcsec'], 0)
        
        # Refraction accuracy
        refraction_accuracy = AccuracyAssessment.estimate_refraction_accuracy(
            math.radians(30)
        )
        self.assertIn('refraction_accuracy_arcsec', refraction_accuracy)
        self.assertIsInstance(refraction_accuracy['refraction_accuracy_arcsec'], float)
        self.assertGreater(refraction_accuracy['refraction_accuracy_arcsec'], 0)
    
    def test_validation_decorator(self):
        """Test validation decorator"""
        @validate_inputs(ValidationLevel.NORMAL)
        def test_function(dt, observer_lat=None, precision_mode=None):
            return {'dt': dt, 'lat': observer_lat, 'mode': precision_mode}
        
        # Valid inputs
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        result = test_function(dt=dt, observer_lat=math.radians(40.0), precision_mode='high')
        self.assertEqual(result['dt'], dt)
        self.assertEqual(result['lat'], math.radians(40.0))
        self.assertEqual(result['mode'], 'high')
    
    def test_error_recovery_manager(self):
        """Test error recovery manager"""
        recovery_manager = ErrorRecoveryManager()
        
        # Test recovery stats
        stats = recovery_manager.get_recovery_stats()
        self.assertIn('total_attempts', stats)
        self.assertIn('successful_recoveries', stats)
        self.assertIn('success_rate', stats)
        
        # Test fallback registration
        def fallback_func(*args, **kwargs):
            return "fallback_result"
        
        recovery_manager.register_fallback('test_function', fallback_func)
        self.assertIn('test_function', recovery_manager.fallback_strategies)


@unittest.skipUnless(PHASE3_AVAILABLE, "Phase 3 components not available")
class TestPhase3Integration(unittest.TestCase):
    """Test Phase 3 integration with existing functions"""
    
    def test_phase3_status(self):
        """Test Phase 3 status reporting"""
        status = get_phase3_status()
        self.assertTrue(status)  # Should be True if we're running these tests
    
    def test_performance_profiler_decorator(self):
        """Test performance profiler decorator"""
        @performance_profiler
        def test_function(x, y):
            time.sleep(0.001)
            return x + y
        
        result = test_function(1, 2)
        self.assertEqual(result, 3)
        
        # Check if performance data was added (if result is dict)
        if isinstance(result, dict):
            self.assertIn('_performance', result)
    
    def test_with_diagnostics_decorator(self):
        """Test diagnostics decorator"""
        @with_diagnostics(enable_tracing=True)
        def test_function(x, y):
            return {'result': x + y}
        
        result = test_function(1, 2)
        self.assertEqual(result['result'], 3)
        
        # Check if diagnostics were added
        if '_diagnostics' in result:
            self.assertIn('function', result['_diagnostics'])
            self.assertIn('execution_time', result['_diagnostics'])


def run_phase3_tests():
    """Run all Phase 3 tests"""
    if not PHASE3_AVAILABLE:
        print("❌ Phase 3 components not available - skipping tests")
        return False
    
    # Create test suite
    test_classes = [
        TestPerformanceBenchmarking,
        TestAdvancedCaching,
        TestEnhancedAtmosphericModeling,
        TestValidationAndErrorHandling,
        TestPhase3Integration
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🚀 Phase 3 High-Precision Functions Test Suite")
    print("=" * 60)
    
    success = run_phase3_tests()
    
    if success:
        print("\n🎉 All Phase 3 tests passed!")
        exit(0)
    else:
        print("\n❌ Some Phase 3 tests failed")
        exit(1)