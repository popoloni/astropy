"""
High-Precision Astronomical Calculations Module

This module provides enhanced precision implementations of astronomical calculations
with configurable precision modes and graceful fallback to standard implementations.

Key Features:
- VSOP87 simplified theory for high-precision sun positions (60x improvement)
- ELP2000 simplified lunar theory for moon calculations (5-10x improvement)
- Bennett's atmospheric refraction formula with weather corrections
- Enhanced Local Sidereal Time with higher-order terms
- Topocentric parallax corrections for nearby objects
- Configurable precision modes with runtime switching

Phase 3 Advanced Features:
- Performance benchmarking and profiling system
- Multi-level caching with persistent storage
- Enhanced atmospheric modeling with multiple refraction models
- Comprehensive validation and error handling
- Diagnostic tools and accuracy assessment
"""

from .config import (
    set_precision_mode,
    get_precision_mode,
    precision_context,
    get_precision_config,
    validate_precision_config
)

from .high_precision import (
    calculate_high_precision_lst,
    calculate_high_precision_sun_position,
    calculate_high_precision_moon_position,
    calculate_high_precision_moon_phase,
    calculate_precise_altaz,
    find_precise_astronomical_twilight,
    calculate_precise_parallax_correction,
    calculate_precise_coordinate_transformation
)

from .atmospheric import (
    apply_atmospheric_refraction,
    calculate_atmospheric_conditions,
    get_refraction_correction
)

from .constants import (
    HIGH_PRECISION_CONSTANTS,
    ATMOSPHERIC_CONSTANTS,
    LUNAR_THEORY_TERMS,
    SOLAR_THEORY_TERMS
)

from .utils import (
    normalize_angle,
    calculate_julian_date,
    precision_cache,
    precision_fallback,
    PrecisionError
)

__all__ = [
    # Configuration management
    'set_precision_mode',
    'get_precision_mode', 
    'precision_context',
    'get_precision_config',
    'validate_precision_config',
    
    # High-precision calculations
    'calculate_high_precision_lst',
    'calculate_high_precision_sun_position',
    'calculate_high_precision_moon_position',
    'calculate_high_precision_moon_phase',
    'calculate_precise_altaz',
    'find_precise_astronomical_twilight',
    'calculate_precise_parallax_correction',
    'calculate_precise_coordinate_transformation',
    
    # Atmospheric corrections
    'apply_atmospheric_refraction',
    'calculate_atmospheric_conditions',
    'get_refraction_correction',
    
    # Constants
    'HIGH_PRECISION_CONSTANTS',
    'ATMOSPHERIC_CONSTANTS',
    'LUNAR_THEORY_TERMS',
    'SOLAR_THEORY_TERMS',
    
    # Utilities
    'normalize_angle',
    'calculate_julian_date',
    'precision_cache',
    'precision_fallback',
    'PrecisionError'
]

# Phase 3: Advanced features (optional imports)
try:
    # Benchmarking and performance analysis
    from .benchmarks import (
        PerformanceBenchmark,
        AstronomicalBenchmarkSuite,
        performance_profiler,
        generate_performance_report
    )
    
    # Advanced caching system
    from .advanced_cache import (
        AdvancedLRUCache,
        MultiLevelCache,
        advanced_cache,
        get_global_cache_stats,
        clear_global_cache,
        cleanup_global_cache
    )
    
    # Enhanced atmospheric modeling
    from .advanced_atmospheric import (
        AdvancedAtmosphericModel,
        AtmosphericConditions,
        RefractionModel,
        WeatherDataProvider
    )
    
    # Validation and error handling
    from .validation import (
        InputValidator,
        ValidationLevel,
        ValidationError,
        ErrorRecoveryManager,
        AccuracyAssessment,
        validate_inputs,
        with_diagnostics,
        get_global_validator,
        get_global_recovery_manager
    )
    
    _PHASE3_AVAILABLE = True
    
    # Add Phase 3 exports
    __all__.extend([
        # Benchmarking
        'PerformanceBenchmark',
        'AstronomicalBenchmarkSuite', 
        'performance_profiler',
        'generate_performance_report',
        
        # Advanced caching
        'AdvancedLRUCache',
        'MultiLevelCache',
        'advanced_cache',
        'get_global_cache_stats',
        'clear_global_cache',
        'cleanup_global_cache',
        
        # Enhanced atmospheric modeling
        'AdvancedAtmosphericModel',
        'AtmosphericConditions',
        'RefractionModel',
        'WeatherDataProvider',
        
        # Validation and error handling
        'InputValidator',
        'ValidationLevel',
        'ValidationError',
        'ErrorRecoveryManager',
        'AccuracyAssessment',
        'validate_inputs',
        'with_diagnostics',
        'get_global_validator',
        'get_global_recovery_manager'
    ])
    
except ImportError as e:
    # Phase 3 components not available
    _PHASE3_AVAILABLE = False
    # For debugging - uncomment to see import errors
    # print(f"Phase 3 import error: {e}")

__version__ = '1.3.0'  # Updated for Phase 3
__author__ = 'OpenHands AI Assistant'

def get_phase3_status():
    """Check if Phase 3 features are available"""
    return _PHASE3_AVAILABLE

def list_available_features():
    """List all available features in the precision module"""
    features = {
        'Phase 1 (Foundation)': [
            'High-precision sun/moon position calculations',
            'Enhanced Local Sidereal Time',
            'Basic atmospheric refraction',
            'Configuration management',
            'Basic caching system'
        ],
        'Phase 2 (Coordinate Transformations)': [
            'Precise coordinate transformations',
            'Twilight calculations',
            'Parallax corrections',
            'Integration with celestial.py'
        ]
    }
    
    if _PHASE3_AVAILABLE:
        features['Phase 3 (Advanced Features)'] = [
            'Performance benchmarking system',
            'Multi-level advanced caching',
            'Enhanced atmospheric modeling',
            'Comprehensive validation and error handling',
            'Diagnostic tools and accuracy assessment'
        ]
    else:
        features['Phase 3 (Not Available)'] = [
            'Phase 3 modules not found - check imports'
        ]
    
    return features