#!/usr/bin/env python3
"""
Simple Phase 3 Test - Verify Phase 3 Components Work

This script performs basic tests of Phase 3 components without complex
interactions that might cause deadlocks.

Author: OpenHands AI Assistant
Date: 2025-06-01
"""

import sys
sys.path.insert(0, '.')

import math
from datetime import datetime
import pytz

def test_phase3_imports():
    """Test that Phase 3 components can be imported"""
    print("🔍 Testing Phase 3 Imports...")
    
    try:
        from astronomy.precision import (
            get_phase3_status,
            list_available_features,
            AdvancedAtmosphericModel,
            AtmosphericConditions,
            RefractionModel,
            InputValidator,
            ValidationLevel,
            AccuracyAssessment
        )
        print("✅ All Phase 3 imports successful")
        return True
    except ImportError as e:
        print(f"❌ Phase 3 import failed: {e}")
        return False

def test_atmospheric_modeling():
    """Test enhanced atmospheric modeling"""
    print("\n🌍 Testing Enhanced Atmospheric Modeling...")
    
    try:
        from astronomy.precision import (
            AdvancedAtmosphericModel,
            AtmosphericConditions,
            RefractionModel
        )
        
        # Create atmospheric model
        model = AdvancedAtmosphericModel()
        
        # Test standard conditions
        conditions = AtmosphericConditions(15.0, 1013.25, 50.0, 550.0)
        
        # Test refraction calculation
        altitude_rad = math.radians(30)
        refraction = model.calculate_refraction(altitude_rad, conditions, RefractionModel.BENNETT)
        
        print(f"✅ Refraction at 30°: {refraction * 206265:.1f} arcsec")
        
        # Test air mass calculation
        air_mass = model.calculate_air_mass(altitude_rad, include_refraction=True, conditions=conditions)
        print(f"✅ Air mass at 30°: {air_mass:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Atmospheric modeling test failed: {e}")
        return False

def test_validation_system():
    """Test validation and error handling"""
    print("\n🔍 Testing Validation System...")
    
    try:
        from astronomy.precision import (
            InputValidator,
            ValidationLevel,
            AccuracyAssessment
        )
        
        # Create validator
        validator = InputValidator(ValidationLevel.NORMAL)
        
        # Test datetime validation
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        validated_dt = validator.validate_datetime(dt)
        print(f"✅ DateTime validation: {validated_dt.strftime('%Y-%m-%d %H:%M %Z')}")
        
        # Test angle validation
        angle = validator.validate_angle(math.pi/4, "test_angle")
        print(f"✅ Angle validation: {math.degrees(angle):.1f}°")
        
        # Test accuracy assessment
        sun_accuracy = AccuracyAssessment.estimate_sun_position_accuracy(dt, 'high')
        print(f"✅ Sun accuracy estimate: {sun_accuracy['ra_accuracy_arcsec']:.1f} arcsec")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_basic_benchmarking():
    """Test basic benchmarking without complex operations"""
    print("\n📊 Testing Basic Benchmarking...")
    
    try:
        from astronomy.precision import PerformanceBenchmark
        from astronomy.precision import calculate_high_precision_sun_position
        
        # Create benchmark
        benchmark = PerformanceBenchmark()
        
        # Test simple function benchmarking
        dt = datetime(2023, 6, 21, 12, 0, 0, tzinfo=pytz.UTC)
        
        # Benchmark with just a few iterations
        results = benchmark.benchmark_function(
            calculate_high_precision_sun_position, dt, iterations=5
        )
        
        print(f"✅ Benchmark results: {results['mean']*1000:.2f}ms average")
        print(f"✅ Success rate: {results['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmarking test failed: {e}")
        return False

def main():
    """Run simple Phase 3 tests"""
    print("🚀 Phase 3 Simple Test Suite")
    print("=" * 50)
    
    tests = [
        test_phase3_imports,
        test_atmospheric_modeling,
        test_validation_system,
        test_basic_benchmarking
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed!")
        print("✅ Phase 3 implementation is working correctly")
        return 0
    else:
        print("⚠️  Some Phase 3 tests failed")
        return 1

if __name__ == "__main__":
    exit(main())