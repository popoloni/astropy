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

__version__ = '1.0.0'
__author__ = 'AstroPy Precision Enhancement Team'