"""
High-Precision Astronomical Constants

This module contains enhanced precision constants for astronomical calculations,
including constants for VSOP87, ELP2000, and atmospheric refraction models.
"""

import math

class HighPrecisionConstants:
    """Enhanced precision astronomical constants"""
    
    # Time constants
    JULIAN_CENTURY = 36525.0  # Days in a Julian century
    J2000_EPOCH = 2451545.0   # Julian date of J2000.0 epoch
    
    # Earth constants (enhanced precision)
    EARTH_RADIUS_KM = 6378.137  # Earth equatorial radius in km
    EARTH_FLATTENING = 1.0 / 298.257223563  # Earth flattening
    EARTH_ROTATION_RATE = 7.2921159e-5  # Earth rotation rate (rad/s)
    
    # Astronomical unit and light speed
    AU_KM = 149597870.7  # Astronomical unit in km
    LIGHT_SPEED_KM_S = 299792458.0 / 1000.0  # Speed of light in km/s
    
    # Angular conversions (high precision)
    ARCSEC_TO_RAD = math.pi / (180.0 * 3600.0)
    ARCMIN_TO_RAD = math.pi / (180.0 * 60.0)
    DEG_TO_RAD = math.pi / 180.0
    RAD_TO_DEG = 180.0 / math.pi
    RAD_TO_ARCSEC = 180.0 * 3600.0 / math.pi
    
    # Sidereal time constants (enhanced precision)
    GMST_COEFFICIENTS = {
        'T0': 24110.54841,      # seconds
        'T1': 8640184.812866,   # seconds/century
        'T2': 0.093104,         # seconds/century²
        'T3': -6.2e-6           # seconds/century³
    }
    
    # Enhanced GMST coefficients with higher-order terms
    GMST_HIGH_PRECISION = {
        'T0': 24110.54841,      # seconds
        'T1': 8640184.812866,   # seconds/century
        'T2': 0.093104,         # seconds/century²
        'T3': -6.2e-6,          # seconds/century³
        'T4': 2.6e-10,          # seconds/century⁴
        'T5': -1.1e-14          # seconds/century⁵
    }

# Solar theory constants (VSOP87 simplified)
SOLAR_THEORY_TERMS = {
    # Earth's heliocentric longitude terms (simplified VSOP87)
    'longitude_terms': [
        # [amplitude (arcsec), period (years), phase (degrees)]
        [628331966747.0, 1.0, 0.0],           # Main term
        [206059.0, 0.5, 177.0],               # Semi-annual
        [4303.0, 0.33, 222.0],                # 4-month period
        [425.0, 0.25, 324.0],                 # 3-month period
        [119.0, 0.2, 70.0],                   # 2.4-month period
        [109.0, 0.167, 117.0],                # 2-month period
        [93.0, 0.143, 142.0],                 # 1.7-month period
        [72.0, 0.125, 158.0],                 # 1.5-month period
        [68.0, 0.111, 161.0],                 # 1.3-month period
        [67.0, 0.1, 157.0]                    # 1.2-month period
    ],
    
    # Earth's heliocentric latitude terms
    'latitude_terms': [
        [280.0, 1.0, 90.0],                   # Annual term
        [102.0, 0.5, 267.0],                  # Semi-annual
        [80.0, 0.33, 42.0],                   # 4-month period
        [44.0, 0.25, 144.0],                  # 3-month period
        [32.0, 0.2, 250.0]                    # 2.4-month period
    ],
    
    # Earth's distance from Sun terms
    'radius_terms': [
        [100013989.0, 1.0, 0.0],              # Main term (AU * 1e8)
        [1670700.0, 0.5, 177.0],              # Semi-annual
        [13956.0, 0.33, 222.0],               # 4-month period
        [3084.0, 0.25, 324.0],                # 3-month period
        [1628.0, 0.2, 70.0]                   # 2.4-month period
    ]
}

# Lunar theory constants (ELP2000 simplified)
LUNAR_THEORY_TERMS = {
    # Moon's geocentric longitude terms (simplified ELP2000)
    'longitude_terms': [
        # [amplitude (arcsec), D, M, M', F] where D=elongation, M=sun mean anomaly, M'=moon mean anomaly, F=argument of latitude
        [22639.586, 0, 0, 1, 0],              # Main term (mean longitude)
        [4586.438, 2, 0, -1, 0],              # Evection
        [2369.912, 2, 0, 0, 0],               # Variation
        [769.016, 0, 1, 0, 0],                # Annual equation
        [666.593, 1, 0, 0, 0],                # Parallactic inequality
        [411.595, 0, 0, 2, 0],                # 
        [211.656, 2, 0, -2, 0],               #
        [205.435, 0, 2, 0, 0],                #
        [191.955, 2, -1, -1, 0],              #
        [164.727, 0, 0, 0, 2],                #
        [147.687, 2, 0, 1, 0],                #
        [124.988, 4, 0, -1, 0],               #
        [109.380, 2, 1, -1, 0],               #
        [55.173, 4, 0, -2, 0],                #
        [45.099, 2, -1, 0, 0],                #
        [39.528, 2, 1, 0, 0],                 #
        [38.430, 1, 0, -1, 0],                #
        [36.124, 2, 2, -1, 0],                #
        [30.773, 0, 1, 1, 0],                 #
        [28.460, 1, 0, 1, 0],                 #
        [24.208, 2, 0, 0, -2],                #
        [18.807, 0, 3, 0, 0],                 #
        [17.780, 4, 0, 0, 0],                 #
        [17.681, 2, -2, -1, 0],               #
        [16.827, 1, 1, -1, 0],                #
        [16.738, 2, 0, -1, 2],                #
        [15.898, 0, 0, 3, 0],                 #
        [14.187, 2, 1, 1, 0],                 #
        [13.992, 4, -1, -1, 0],               #
        [13.949, 0, 1, -2, 0]                 #
    ],
    
    # Moon's geocentric latitude terms
    'latitude_terms': [
        [18461.24, 0, 0, 0, 1],               # Main term
        [1010.167, 0, 0, 1, 1],               #
        [999.737, 0, 0, 1, -1],               #
        [623.655, 2, 0, 0, 1],                #
        [199.484, 2, 0, -1, 1],               #
        [166.677, 2, 0, -1, -1],              #
        [117.261, 2, 0, 0, -1],               #
        [61.911, 0, 1, 0, 1],                 #
        [33.715, 0, 1, 0, -1],                #
        [31.174, 4, 0, 0, 1],                 #
        [29.577, 2, 0, 1, 1],                 #
        [15.512, 2, -1, 0, 1],                #
        [15.335, 2, 0, 1, -1]                 #
    ],
    
    # Moon's distance terms
    'radius_terms': [
        [20905355.0, 0, 0, 1, 0],             # Main term (km)
        [3699111.0, 2, 0, -1, 0],             # Evection
        [2955968.0, 2, 0, 0, 0],              # Variation
        [569925.0, 0, 1, 0, 0],               # Annual equation
        [246158.0, 1, 0, 0, 0],               # Parallactic inequality
        [204586.0, 0, 0, 2, 0],               #
        [170733.0, 2, 0, -2, 0],              #
        [152138.0, 2, -1, -1, 0],             #
        [129620.0, 2, 0, 1, 0],               #
        [108743.0, 4, 0, -1, 0],              #
        [104755.0, 2, 1, -1, 0],              #
        [79661.0, 1, 0, -1, 0],               #
        [48888.0, 4, 0, -2, 0],               #
        [34734.0, 2, -1, 0, 0],               #
        [32405.0, 2, 1, 0, 0],                #
        [31245.0, 1, 0, 1, 0],                #
        [25731.0, 0, 1, 1, 0],                #
        [24608.0, 2, 2, -1, 0],               #
        [18739.0, 0, 3, 0, 0],                #
        [17901.0, 4, 0, 0, 0]                 #
    ]
}

# Atmospheric refraction constants
ATMOSPHERIC_CONSTANTS = {
    # Bennett's formula constants
    'bennett': {
        'A': 1.02,                            # Coefficient A
        'B': 10.3,                            # Coefficient B (arcmin)
        'C': 5.11,                            # Coefficient C (degrees)
        'standard_pressure': 1013.25,         # Standard pressure (mbar)
        'standard_temperature': 288.15,       # Standard temperature (K)
        'temperature_lapse': 0.0065           # Temperature lapse rate (K/m)
    },
    
    # Saemundsson's formula constants
    'saemundsson': {
        'A': 1.02,                            # Coefficient A
        'B': 10.3,                            # Coefficient B (arcmin)
        'C': 5.11,                            # Coefficient C (degrees)
        'D': 0.0019279,                       # Additional term
        'E': 1.1364                           # Additional term
    },
    
    # Simple refraction model
    'simple': {
        'coefficient': 0.00452,               # Simple refraction coefficient
        'min_altitude': 5.0                   # Minimum altitude for application (degrees)
    },
    
    # Physical constants for refraction
    'physical': {
        'dry_air_density_stp': 1.2929,       # kg/m³ at STP
        'water_vapor_density': 0.804,        # kg/m³ at STP
        'refractive_index_dry': 1.0002926,   # Refractive index of dry air
        'refractive_index_vapor': 1.000249   # Refractive index of water vapor
    }
}

# Nutation constants (simplified)
NUTATION_TERMS = [
    # [coefficient in longitude (arcsec), coefficient in obliquity (arcsec), period (years)]
    [-17.20, 9.20, 18.61],                   # Main term (18.6 year period)
    [-1.32, 0.57, 0.5],                      # Semi-annual
    [-0.23, 0.10, 0.25],                     # Quarterly
    [-0.21, 0.09, 1.0],                      # Annual
    [0.20, -0.09, 9.3],                      # 9.3 year period
    [0.16, -0.07, 0.33],                     # 4-month period
    [-0.16, 0.07, 13.7],                     # 13.7 year period
    [-0.15, 0.0, 0.17]                       # 2-month period
]

# Aberration constants
ABERRATION_CONSTANT = 20.49552  # arcseconds

# Parallax constants
PARALLAX_CONSTANTS = {
    'earth_radius_equatorial': 6378137.0,    # meters
    'earth_radius_polar': 6356752.314245,    # meters
    'moon_mean_distance': 384400.0,          # km
    'sun_mean_distance': 149597870.7,        # km
    'au_to_km': 149597870.7                  # km per AU
}

# Export main constants object
HIGH_PRECISION_CONSTANTS = HighPrecisionConstants()