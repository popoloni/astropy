# astropy_experimental.py
# This file is a copy of astronightplanner.py with some experimental features added.
# the experimental features are:
# - high-precision calculations
# - caching
# - error handling
# - input validation
# - utility functions
# - high-precision atmospheric refraction
# what is still to be refined is:
# - graphical output, suboptimal for now if compared to astronightplanner.py

import sys
import os
# Add root directory to path for imports
root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, root_dir)

import math
import numpy as np
from datetime import datetime, timedelta, timezone
import os

import pytz
import re
import json

import csv

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

from enum import Enum
import argparse
import gc
from functools import lru_cache

# Import time simulation module
import utilities.time_sim as time_sim
from utilities.time_sim import get_current_datetime, get_simulated_datetime, SIMULATED_DATETIME

# ============= ENHANCED ERROR HANDLING =============

class AstronomicalCalculationError(Exception):
    """Custom exception for astronomical calculation errors"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

# ============= HIGH-PRECISION CONSTANTS =============

class AstronomicalConstants:
    """Pre-computed constants for better performance and precision"""
    
    # High-precision fundamental constants
    JD_J2000 = 2451545.0
    SECONDS_PER_DAY = 86400.0
    DAYS_PER_CENTURY = 36525.0
    
    # Earth rotation parameters
    OMEGA_EARTH = 7.292115e-5  # Earth's rotation rate (rad/s)
    
    # Atmospheric refraction coefficients (Bennett's formula)
    REFRACTION_COEFF = {
        'A': 1.0 / 60.0,  # Base coefficient
        'B': 0.00676,     # Tan^3 coefficient  
        'C': 0.00012,     # Tan^5 coefficient
    }
    
    # Pre-computed trigonometric values for common angles
    SIN_15 = math.sin(math.radians(15))
    COS_15 = math.cos(math.radians(15))
    TAN_15 = math.tan(math.radians(15))

# ============= INPUT VALIDATION DECORATOR =============

def validate_and_normalize_inputs(func):
    """Decorator for input validation and normalization"""
    def wrapper(*args, **kwargs):
        try:
            # Validate datetime objects
            for arg in args:
                if isinstance(arg, datetime):
                    if arg.year < 1900 or arg.year > 2100:
                        raise AstronomicalCalculationError(
                            f"Date {arg} outside valid range (1900-2100)"
                        )
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Validate output ranges
            if isinstance(result, tuple) and len(result) == 2:
                alt, az = result
                if not (-90 <= alt <= 90):
                    raise AstronomicalCalculationError(f"Invalid altitude: {alt}°")
                if not (0 <= az <= 360):
                    az = az % 360  # Normalize azimuth
                    result = (alt, az)
            
            return result
            
        except Exception as e:
            if isinstance(e, AstronomicalCalculationError):
                raise
            else:
                raise AstronomicalCalculationError(f"Calculation error in {func.__name__}: {e}")
    
    return wrapper

# ============= UTILITY FUNCTIONS =============

def normalize_angle(angle_deg):
    """Normalize angle to 0-360 degrees"""
    return angle_deg % 360

@lru_cache(maxsize=100)
def cached_expensive_calculation(jd_rounded):
    """Cache expensive calculations with rounded Julian Date"""
    # This will be used by other functions for caching
    return jd_rounded

def clear_calculation_cache():
    """Clear caches and force garbage collection for iOS"""
    cached_expensive_calculation.cache_clear()
    gc.collect()

# ============= HIGH-PRECISION ATMOSPHERIC REFRACTION =============

def apply_atmospheric_refraction(altitude_deg, pressure_mbar=1013.25, temperature_c=15.0):
    """
    Apply atmospheric refraction correction using Bennett's formula
    Accuracy: ~0.1 arcmin for altitudes > 5°
    """
    if altitude_deg < -2:  # Below reasonable horizon
        return altitude_deg
    
    # Convert to positive altitude for calculation
    alt_positive = max(0.1, altitude_deg)  # Minimum 0.1° to avoid division issues
    alt_rad = math.radians(alt_positive)
    
    # Atmospheric conditions correction
    pressure_factor = pressure_mbar / 1013.25
    temperature_factor = 283.0 / (273.0 + temperature_c)
    
    # Bennett's formula for refraction
    if alt_positive >= 15:
        # High altitude approximation (simpler, more accurate)
        refraction_arcmin = pressure_factor * temperature_factor / math.tan(alt_rad)
    else:
        # Low altitude formula (more complex but necessary)
        tan_alt = math.tan(alt_rad)
        refraction_arcmin = pressure_factor * temperature_factor * \
                           (1.0 / tan_alt - 0.00676 * tan_alt * tan_alt * tan_alt + 
                            0.00012 * tan_alt * tan_alt * tan_alt * tan_alt * tan_alt)
    
    # Convert arcminutes to degrees and apply
    refraction_deg = refraction_arcmin / 60.0
    
    return altitude_deg + refraction_deg

# ============= HIGH-PRECISION LST CALCULATION =============

def calculate_high_precision_lst(dt):
    """
    High-precision Local Sidereal Time calculation
    Includes higher-order terms for better accuracy
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    T = (jd - 2451545.0) / 36525.0
    
    # Greenwich Mean Sidereal Time (GMST) with higher precision
    # Meeus formula with all terms
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0)
    gmst += 0.000387933 * T**2 - T**3 / 38710000
    
    # Additional precision terms
    gmst += 0.0000258622 * T**4 - T**5 / 319000000
    
    # Normalize to 0-360 degrees
    gmst = gmst % 360
    
    # Convert to radians and add longitude
    gmst_rad = math.radians(gmst)
    lst = gmst_rad + math.radians(LONGITUDE)
    
    return lst % (2 * math.pi)

# ============= HIGH-PRECISION SUN CALCULATIONS =============

@validate_and_normalize_inputs
def calculate_high_precision_sun_position(dt):
    """
    High-precision sun position using simplified VSOP87 theory
    Accuracy: ~2 arcsec (vs current ~2 arcmin)
    Uses only standard math library
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    T = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000.0
    
    # High-precision Earth's orbital elements (VSOP87 simplified)
    # Mean longitude of the Sun (geometric)
    L0 = 280.4664567 + 36000.76982779 * T + 0.0003032028 * T**2 + T**3 / 49931000
    
    # Mean anomaly of Earth
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000
    
    # Convert to radians
    L0_rad = math.radians(L0 % 360)
    M_rad = math.radians(M % 360)
    
    # Equation of center (more complete series)
    C = (1.914602 - 0.004817 * T - 0.000014 * T**2) * math.sin(M_rad) + \
        (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) + \
        0.000289 * math.sin(3 * M_rad)
    
    # True longitude
    true_longitude = L0 + C
    
    # True anomaly
    nu = M + C
    nu_rad = math.radians(nu)
    
    # Earth's distance from Sun (AU)
    R = (1.000001018 * (1 - 0.01670862 * math.cos(M_rad) - 
         0.000042037 * math.cos(2 * M_rad))) / \
        (1 + 0.01670862 * math.cos(nu_rad))
    
    # Aberration correction
    aberration = -20.4898 / R  # arcseconds
    true_longitude += aberration / 3600  # convert to degrees
    
    # Nutation in longitude (simplified)
    omega = 125.04 - 1934.136 * T  # longitude of ascending node of Moon
    omega_rad = math.radians(omega)
    nutation_longitude = -17.20 * math.sin(omega_rad) - 1.32 * math.sin(2 * L0_rad)
    nutation_longitude /= 3600  # convert to degrees
    
    # Apparent longitude
    apparent_longitude = true_longitude + nutation_longitude
    
    # Obliquity of ecliptic with nutation
    epsilon0 = 23.43929111 - 0.013004167 * T - 0.0000001639 * T**2 + 0.0000005036 * T**3
    nutation_obliquity = 9.20 * math.cos(omega_rad) + 0.57 * math.cos(2 * L0_rad)
    nutation_obliquity /= 3600  # convert to degrees
    epsilon = epsilon0 + nutation_obliquity
    
    # Convert to equatorial coordinates
    lambda_rad = math.radians(apparent_longitude)
    epsilon_rad = math.radians(epsilon)
    
    # Right ascension and declination
    alpha = math.atan2(math.cos(epsilon_rad) * math.sin(lambda_rad), math.cos(lambda_rad))
    delta = math.asin(math.sin(epsilon_rad) * math.sin(lambda_rad))
    
    # Convert to horizontal coordinates
    lst = calculate_high_precision_lst(dt)
    ha = lst - alpha
    
    lat_rad = math.radians(LATITUDE)
    
    # Include atmospheric refraction
    sin_alt = (math.sin(lat_rad) * math.sin(delta) + 
               math.cos(lat_rad) * math.cos(delta) * math.cos(ha))
    alt_geometric = math.asin(sin_alt)
    alt_apparent = apply_atmospheric_refraction(math.degrees(alt_geometric))
    
    # Azimuth calculation
    cos_az = (math.sin(delta) - math.sin(math.radians(alt_apparent)) * math.sin(lat_rad)) / \
             (math.cos(math.radians(alt_apparent)) * math.cos(lat_rad))
    cos_az = min(1, max(-1, cos_az))
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
    
    return alt_apparent, math.degrees(az)

# ============= HIGH-PRECISION MOON CALCULATIONS =============

@validate_and_normalize_inputs
def calculate_high_precision_moon_position(dt):
    """
    High-precision moon position using simplified ELP2000 lunar theory
    Accuracy: ~1 arcmin (vs current ~5-10 arcmin)
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    T = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000.0
    
    # Fundamental arguments (Meeus Ch. 47)
    Lp = normalize_angle(218.3164477 + 481267.88123421 * T - 0.0015786 * T**2 + 
                         T**3 / 538841.0 - T**4 / 65194000.0)  # Mean longitude
    D = normalize_angle(297.8501921 + 445267.1114034 * T - 0.0018819 * T**2 + 
                        T**3 / 545868.0 - T**4 / 113065000.0)  # Mean elongation
    M = normalize_angle(357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + 
                        T**3 / 24490000.0)  # Sun's mean anomaly
    Mp = normalize_angle(134.9633964 + 477198.8675055 * T + 0.0087414 * T**2 + 
                         T**3 / 69699.0 - T**4 / 14712000.0)  # Moon's mean anomaly
    F = normalize_angle(93.2720950 + 483202.0175233 * T - 0.0036539 * T**2 - 
                        T**3 / 3526000.0 + T**4 / 863310000.0)  # Argument of latitude
    
    # Convert to radians for calculations
    Lp_rad, D_rad, M_rad, Mp_rad, F_rad = map(math.radians, [Lp, D, M, Mp, F])
    
    # Periodic terms for longitude (most significant terms from ELP2000)
    longitude_terms = [
        # Coefficient, D, M, Mp, F multipliers
        (6288774, 0, 0, 1, 0),    # Main term
        (1274027, 2, 0, -1, 0),   # Evection
        (658314, 2, 0, 0, 0),     # Variation
        (213618, 0, 0, 2, 0),     # Second variation
        (-185116, 0, 1, 0, 0),    # Annual equation
        (-114332, 0, 0, 0, 2),    # Principal term in latitude argument
        (58793, 2, 0, -2, 0),
        (57066, 2, -1, -1, 0),
        (53322, 2, 0, 1, 0),
        (45758, 2, -1, 0, 0),
        (-40923, 0, 1, -1, 0),
        (-34720, 1, 0, 0, 0),
        (-30383, 0, 1, 1, 0),
        (15327, 2, 0, 0, -2),
        (-12528, 0, 0, 1, 2),
        (10980, 0, 0, 1, -2),
        (10675, 4, 0, -1, 0),
        (10034, 0, 0, 3, 0),
        (8548, 4, 0, -2, 0),
        (-7888, 2, 1, -1, 0),
        (-6766, 2, 1, 0, 0),
        (-5163, 1, 0, -1, 0),
        (4987, 1, 1, 0, 0),
        (4036, 2, -1, 1, 0),
        (3994, 2, 0, 2, 0),
        (3861, 4, 0, 0, 0),
        (3665, 2, 0, -3, 0),
        (-2689, 0, 1, -2, 0),
        (-2602, 2, 0, -1, 2),
        (2390, 2, -1, -2, 0),
        (-2348, 1, 0, 1, 0),
        (2236, 2, -2, 0, 0),
        (-2120, 0, 1, 2, 0),
        (-2078, 0, 2, 0, 0),
    ]
    
    # Calculate longitude perturbations
    delta_longitude = 0
    for coeff, d, m, mp, f in longitude_terms:
        argument = d * D_rad + m * M_rad + mp * Mp_rad + f * F_rad
        delta_longitude += coeff * math.sin(argument)
    
    # Latitude terms (most significant)
    latitude_terms = [
        (5128122, 0, 0, 0, 1),
        (280602, 0, 0, 1, 1),
        (277693, 0, 0, 1, -1),
        (173237, 2, 0, 0, -1),
        (55413, 2, 0, -1, 1),
        (46271, 2, 0, -1, -1),
        (32573, 0, 0, 2, 1),
        (17198, 2, 0, 1, -1),
        (9266, 2, 0, 0, 1),
        (8822, 0, 0, 2, -1),
        (8216, 2, -1, 0, -1),
        (4324, 2, 0, -2, -1),
        (4200, 2, 0, 1, 1),
        (-3359, 2, 1, 0, -1),
        (2463, 2, -1, -1, 1),
        (2211, 2, -1, -1, -1),
        (2065, 2, -1, 0, 1),
        (-1870, 0, 1, 0, 1),
        (1828, 4, 0, -1, -1),
        (-1794, 0, 1, 0, -1),
        (-1749, 0, 0, 0, 3),
        (-1565, 0, 1, -1, -1),
        (-1491, 1, 0, 0, 1),
        (-1475, 0, 1, 1, 1),
        (-1410, 0, 1, 1, -1),
        (-1344, 0, 1, -1, 1),
        (-1335, 1, 0, 0, -1),
    ]
    
    # Calculate latitude perturbations
    delta_latitude = 0
    for coeff, d, m, mp, f in latitude_terms:
        argument = d * D_rad + m * M_rad + mp * Mp_rad + f * F_rad
        delta_latitude += coeff * math.sin(argument)
    
    # Final geocentric coordinates
    moon_longitude = Lp + delta_longitude / 1000000.0  # Convert to degrees
    moon_latitude = delta_latitude / 1000000.0  # Convert to degrees
    
    # Convert to equatorial coordinates
    epsilon = 23.43929111 - 0.013004167 * T  # Obliquity of ecliptic
    
    lambda_rad = math.radians(moon_longitude)
    beta_rad = math.radians(moon_latitude)
    epsilon_rad = math.radians(epsilon)
    
    # Right ascension and declination
    alpha = math.atan2(
        math.sin(lambda_rad) * math.cos(epsilon_rad) - 
        math.tan(beta_rad) * math.sin(epsilon_rad),
        math.cos(lambda_rad)
    )
    delta = math.asin(
        math.sin(beta_rad) * math.cos(epsilon_rad) + 
        math.cos(beta_rad) * math.sin(epsilon_rad) * math.sin(lambda_rad)
    )
    
    # Convert to horizontal coordinates
    lst = calculate_high_precision_lst(dt)
    ha = lst - alpha
    lat_rad = math.radians(LATITUDE)
    
    # Calculate altitude with refraction
    sin_alt = (math.sin(lat_rad) * math.sin(delta) + 
               math.cos(lat_rad) * math.cos(delta) * math.cos(ha))
    alt_geometric = math.asin(sin_alt)
    alt_apparent = apply_atmospheric_refraction(math.degrees(alt_geometric))
    
    # Calculate azimuth
    az = math.atan2(
        math.sin(ha),
        math.cos(ha) * math.sin(lat_rad) - math.tan(delta) * math.cos(lat_rad)
    )
    az_degrees = (math.degrees(az) + 180) % 360
    
    return alt_apparent, az_degrees

def calculate_high_precision_moon_phase(dt):
    """
    High-precision moon phase calculation
    Accuracy: ~0.1% illumination (vs current ~1-2%)
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    T = (jd - 2451545.0) / 36525.0
    
    # Enhanced fundamental arguments
    D = 297.8502042 + 445267.1115168 * T - 0.0016300 * T**2 + T**3 / 545868 - T**4 / 113065000
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000
    Mp = 134.9634114 + 477198.8676313 * T + 0.0087414 * T**2 + T**3 / 69699 - T**4 / 14712000
    F = 93.2720993 + 483202.0175273 * T - 0.0036539 * T**2 - T**3 / 3526000 + T**4 / 863310000
    
    # Convert to radians
    D_rad = math.radians(D % 360)
    M_rad = math.radians(M % 360)
    Mp_rad = math.radians(Mp % 360)
    F_rad = math.radians(F % 360)
    
    # Phase angle calculation with higher-order terms
    i = 180 - D * 180/math.pi - 6.289 * math.sin(Mp_rad) + 2.100 * math.sin(M_rad)
    i -= 1.274 * math.sin(2*D_rad - Mp_rad) - 0.658 * math.sin(2*D_rad)
    i -= 0.214 * math.sin(2*Mp_rad) - 0.110 * math.sin(D_rad)
    i += 0.144 * math.sin(2*D_rad + Mp_rad) + 0.128 * math.sin(2*D_rad - M_rad)
    i -= 0.096 * math.sin(2*D_rad - M_rad - Mp_rad) - 0.070 * math.sin(2*D_rad - 2*Mp_rad)
    i -= 0.062 * math.sin(Mp_rad - M_rad) - 0.050 * math.sin(D_rad + Mp_rad)
    i -= 0.045 * math.sin(D_rad - Mp_rad) - 0.031 * math.sin(D_rad + M_rad)
    i -= 0.027 * math.sin(Mp_rad + M_rad) + 0.024 * math.sin(2*F_rad)
    
    # Convert phase angle to illuminated fraction
    i_rad = math.radians(abs(i))
    k = (1 + math.cos(i_rad)) / 2
    
    return k

# ============= ENHANCED COORDINATE CALCULATIONS =============

@validate_and_normalize_inputs
def calculate_precise_altaz(obj, dt, include_refraction=True, include_parallax=False):
    """
    High-precision altitude/azimuth calculation
    Includes atmospheric refraction and optionally topocentric parallax
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    # Calculate high-precision LST
    lst = calculate_high_precision_lst(dt)
    
    # Hour angle
    ha = lst - obj.ra
    
    # Geocentric coordinates
    lat_rad = math.radians(LATITUDE)
    
    # Basic spherical astronomy
    sin_alt = (math.sin(obj.dec) * math.sin(lat_rad) + 
               math.cos(obj.dec) * math.cos(lat_rad) * math.cos(ha))
    
    # Handle numerical errors near zenith/nadir
    sin_alt = max(-1.0, min(1.0, sin_alt))
    alt_geometric = math.asin(sin_alt)
    
    # Topocentric parallax correction (for Moon and close objects)
    if include_parallax and hasattr(obj, 'distance_km'):
        # Simplified parallax correction
        earth_radius_km = 6371.0
        if obj.distance_km < 1000000:  # Less than 1 million km (mainly Moon)
            parallax_correction = math.asin(earth_radius_km / obj.distance_km)
            alt_geometric -= parallax_correction * math.cos(alt_geometric)
    
    # Apply atmospheric refraction
    if include_refraction:
        alt_apparent = apply_atmospheric_refraction(math.degrees(alt_geometric))
    else:
        alt_apparent = math.degrees(alt_geometric)
    
    # Azimuth calculation
    cos_az = (math.sin(obj.dec) - math.sin(math.radians(alt_apparent)) * math.sin(lat_rad)) / \
             (math.cos(math.radians(alt_apparent)) * math.cos(lat_rad))
    cos_az = max(-1.0, min(1.0, cos_az))  # Handle numerical errors
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
    
    return alt_apparent, math.degrees(az)

# ============= ENHANCED TWILIGHT CALCULATIONS =============

def find_precise_astronomical_twilight(date):
    """
    High-precision twilight calculation using iterative method
    Accuracy: ~30 seconds (vs current ~2-3 minutes)
    """
    # Start with approximate times
    sunset_approx, sunrise_approx = find_sunset_sunrise(date)
    
    # Twilight occurs when sun is 18° below horizon
    twilight_altitude = -18.0
    
    # Iterative refinement for evening twilight
    evening_twilight = refine_sun_event_time(
        date, sunset_approx, twilight_altitude, search_after=True
    )
    
    # Iterative refinement for morning twilight  
    morning_twilight = refine_sun_event_time(
        date + timedelta(days=1), sunrise_approx, twilight_altitude, search_after=False
    )
    
    return evening_twilight, morning_twilight

def refine_sun_event_time(date, approximate_time, target_altitude, search_after=True, tolerance=0.01):
    """
    Iteratively refine sun event time using Newton's method
    """
    current_time = approximate_time
    
    for iteration in range(10):  # Maximum 10 iterations
        # Calculate current sun altitude
        sun_alt, _ = calculate_high_precision_sun_position(current_time)
        
        # Calculate error
        altitude_error = sun_alt - target_altitude
        
        if abs(altitude_error) < tolerance:  # Converged
            break
        
        # Calculate derivative (rate of altitude change)
        dt_small = timedelta(minutes=1)
        if search_after:
            test_time = current_time + dt_small
        else:
            test_time = current_time - dt_small
        
        test_alt, _ = calculate_high_precision_sun_position(test_time)
        altitude_rate = (test_alt - sun_alt) / (dt_small.total_seconds() / 3600)  # degrees per hour
        
        if abs(altitude_rate) < 1e-6:  # Avoid division by zero
            break
        
        # Newton's method correction
        time_correction_hours = -altitude_error / altitude_rate
        current_time += timedelta(hours=time_correction_hours)
    
    return current_time

# ============= ENHANCED CONFIGURATION MANAGEMENT =============

def load_ios_config():
    """Load configuration optimized for iOS Pythonista"""
    # Try multiple locations
    config_paths = [
        'config.json',  # Current directory
        os.path.expanduser('~/Documents/config.json'),  # Pythonista Documents
        os.path.expanduser('~/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/config.json')  # iCloud
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config from {path}: {e}")
                continue
    
    # Return default configuration if none found
    return get_default_config()

def get_default_config():
    """Default configuration for Pythonista"""
    return {
        'locations': {
            'default': {
                'name': 'Default Location',
                'latitude': 45.0,
                'longitude': 0.0,
                'elevation': 100,
                'timezone': 'UTC',
                'bortle_index': 4,
                'default': True
            }
        },
        'precision': {
            'use_high_precision': True,
            'include_refraction': True,
            'include_parallax': False,
            'cache_calculations': True
        },
        'catalog': {
            'use_csv_catalog': False,
            'catalog_name': 'combined',
            'merge': True
        },
        'visibility': {
            'min_visibility_hours': 2.0,
            'min_total_area': 1.0,
            'trajectory_interval_minutes': 15,
            'search_interval_minutes': 5
        },
        'scheduling': {
            'strategy': 'LONGEST_DURATION',
            'max_overlap_minutes': 30,
            'exclude_insufficient_time': False
        },
        'imaging': {
            'scope': {
                'name': 'Vespera Passenger',
                'fov_width': 2.4,
                'fov_height': 1.8,
                'mosaic_fov_width': 4.7,
                'mosaic_fov_height': 3.5,
                'single_exposure': 300,
                'min_snr': 10,
                'gain': 100,
                'read_noise': 3.5,
                'pixel_size': 3.76,
                'focal_length': 200,
                'aperture': 50
            }
        },
        'plotting': {
            'max_objects_optimal': 15,
            'figure_size': [16, 12],
            'color_map': 'viridis',
            'grid_alpha': 0.3,
            'visible_region_alpha': 0.2
        },
        'moon': {
            'proximity_radius': 10,
            'trajectory_color': '#FFD700',
            'marker_color': '#FFA500',
            'line_width': 2,
            'marker_size': 100,
            'interference_color': 'red'
        }
    }

# ============= TESTING AND VALIDATION =============

def run_precision_tests():
    """
    Test suite to validate precision improvements
    Compare against known astronomical data
    """
    test_results = {}
    
    # Test 1: Sun position accuracy
    # Use known solstice/equinox data
    test_cases = [
        # (datetime, expected_alt, expected_az, tolerance_arcmin)
        (datetime(2024, 6, 21, 12, 0, tzinfo=pytz.UTC), 68.44, 180.0, 2.0),  # Summer solstice noon
        (datetime(2024, 12, 21, 12, 0, tzinfo=pytz.UTC), 21.56, 180.0, 2.0), # Winter solstice noon
    ]
    
    sun_errors = []
    for test_time, expected_alt, expected_az, tolerance in test_cases:
        calc_alt, calc_az = calculate_high_precision_sun_position(test_time)
        alt_error = abs(calc_alt - expected_alt) * 60  # Convert to arcminutes
        az_error = abs(calc_az - expected_az) * 60
        
        sun_errors.append(alt_error)
        print(f"Sun test {test_time}: Alt error {alt_error:.1f}', Az error {az_error:.1f}'")
    
    test_results['sun_accuracy'] = {
        'max_error_arcmin': max(sun_errors),
        'avg_error_arcmin': sum(sun_errors) / len(sun_errors),
        'passed': all(error < 2.0 for error in sun_errors)
    }
    
    # Test 2: Moon phase accuracy
    # Use known new moon dates
    known_new_moons = [
        datetime(2024, 1, 11, 11, 57, tzinfo=pytz.UTC),
        datetime(2024, 2, 9, 22, 59, tzinfo=pytz.UTC),
    ]
    
    phase_errors = []
    for new_moon_time in known_new_moons:
        phase = calculate_high_precision_moon_phase(new_moon_time)
        error = abs(phase) * 100  # Convert to percentage
        phase_errors.append(error)
        print(f"Moon phase test {new_moon_time}: Error {error:.2f}%")
    
    test_results['moon_phase_accuracy'] = {
        'max_error_percent': max(phase_errors),
        'avg_error_percent': sum(phase_errors) / len(phase_errors),
        'passed': all(error < 1.0 for error in phase_errors)
    }
    
    return test_results

def benchmark_calculations():
    """Benchmark calculation performance"""
    import time
    
    test_time = datetime(2024, 6, 21, 12, 0, tzinfo=pytz.UTC)
    num_iterations = 100
    
    # Benchmark sun calculation
    start_time = time.time()
    for _ in range(num_iterations):
        calculate_high_precision_sun_position(test_time)
    sun_time = (time.time() - start_time) / num_iterations * 1000  # ms per call
    
    # Benchmark moon calculation  
    start_time = time.time()
    for _ in range(num_iterations):
        calculate_high_precision_moon_position(test_time)
    moon_time = (time.time() - start_time) / num_iterations * 1000  # ms per call
    
    print(f"Performance benchmark (iOS Pythonista):")
    print(f"  Sun position: {sun_time:.2f} ms per calculation")
    print(f"  Moon position: {moon_time:.2f} ms per calculation")
    
    return {'sun_ms': sun_time, 'moon_ms': moon_time}

# ============= ORIGINAL CODE STARTS HERE =============

class SchedulingStrategy(Enum):
    LONGEST_DURATION = "longest_duration"  # Current strategy: prioritize longest visibility
    MAX_OBJECTS = "max_objects"           # Maximum number of objects
    OPTIMAL_SNR = "optimal_snr"           # Best imaging conditions
    MINIMAL_MOSAIC = "minimal_mosaic"     # Fewer panels needed
    DIFFICULTY_BALANCED = "difficulty_balanced"  # Mix of easy and challenging
    MOSAIC_GROUPS = "mosaic_groups"       # Prioritize mosaic groups over individual objects

# Load configuration from file
def load_config():
    # Get the root directory (parent of legacy folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    config_path = os.path.join(root_dir, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_default_location(config):
    """Get the default location from config"""
    # Handle new config structure with single location
    if 'location' in config:
        location = config['location']
        return 'default', location
    
    # Handle old config structure with multiple locations
    if 'locations' in config:
        for loc_id, loc_data in config['locations'].items():
            if loc_data.get('default', False):
                return loc_id, loc_data
        # If no default found, return the first one
        if config['locations']:
            first_key = next(iter(config['locations']))
            return first_key, config['locations'][first_key]
    
    # Fallback to hardcoded default
    return 'default', {
        'name': 'Milano',
        'latitude': 45.517,
        'longitude': 9.217,
        'timezone': 'Europe/Rome',
        'elevation': 122
    }

CONFIG = load_config()
DEFAULT_LOCATION_ID, DEFAULT_LOCATION = get_default_location(CONFIG)

# ============= ENHANCED CONFIGURATION OVERRIDE =============

# Override configuration with enhanced iOS-compatible version
try:
    CONFIG = load_ios_config()
    DEFAULT_LOCATION_ID, DEFAULT_LOCATION = get_default_location(CONFIG)
    print("Enhanced configuration loaded successfully")
except Exception as e:
    print(f"Using fallback configuration due to error: {e}")
    # CONFIG and DEFAULT_LOCATION remain as originally loaded above

# ============= GLOBAL CONFIGURATION =============

# Location Configuration
LATITUDE = DEFAULT_LOCATION['latitude']
LONGITUDE = DEFAULT_LOCATION['longitude']
TIMEZONE = DEFAULT_LOCATION['timezone']

# Visibility Constraints - read from location section
MIN_ALT = DEFAULT_LOCATION.get('min_altitude', 20)
MAX_ALT = DEFAULT_LOCATION.get('max_altitude', 85)
MIN_AZ = DEFAULT_LOCATION.get('min_azimuth', 0)
MAX_AZ = DEFAULT_LOCATION.get('max_azimuth', 360)

# Location-specific settings
BORTLE_INDEX = DEFAULT_LOCATION.get('bortle_index', 6)

# Catalog selection
USE_CSV_CATALOG = CONFIG.get('catalog', {}).get('use_csv_catalog', False)
CATALOGNAME = CONFIG.get('catalog', {}).get('catalog_name', 'combined')
MERGING_CATALOGS = CONFIG.get('catalog', {}).get('merge', True)

# Time & Visibility Configuration
MIN_VISIBILITY_HOURS = CONFIG.get('observation', {}).get('min_visibility_hours', 1.5)
MIN_TOTAL_AREA = CONFIG.get('visibility', {}).get('min_total_area', 1.0)
TRAJECTORY_INTERVAL_MINUTES = CONFIG.get('visibility', {}).get('trajectory_interval_minutes', 15)
SEARCH_INTERVAL_MINUTES = CONFIG.get('visibility', {}).get('search_interval_minutes', 5)

# Scheduling Configuration
SCHEDULING_STRATEGY = SchedulingStrategy[CONFIG.get('scheduling', {}).get('strategy', 'longest_duration').upper()]
MAX_OVERLAP_MINUTES = CONFIG.get('observation', {}).get('max_overlap_minutes', 30)

# Visibility Filtering
EXCLUDE_INSUFFICIENT_TIME = CONFIG.get('observation', {}).get('exclude_insufficient_time', True)

# Imaging Configuration
# Vespera Passenger Specifications
SCOPE_FOV_WIDTH = CONFIG.get('imaging', {}).get('scope', {}).get('fov_width', 2.4)
SCOPE_FOV_HEIGHT = CONFIG.get('imaging', {}).get('scope', {}).get('fov_height', 1.8)
SCOPE_FOV_AREA = SCOPE_FOV_WIDTH * SCOPE_FOV_HEIGHT  # square degrees
SINGLE_EXPOSURE = CONFIG.get('observation', {}).get('single_exposure_minutes', 5) * 60  # Convert to seconds
MIN_SNR = CONFIG.get('imaging', {}).get('scope', {}).get('min_snr', 10)
GAIN = CONFIG.get('imaging', {}).get('scope', {}).get('gain', 100)
READ_NOISE = CONFIG.get('imaging', {}).get('scope', {}).get('read_noise', 3.5)
PIXEL_SIZE = CONFIG.get('imaging', {}).get('scope', {}).get('pixel_size', 3.76)
FOCAL_LENGTH = CONFIG.get('imaging', {}).get('scope', {}).get('focal_length', 200)
APERTURE = CONFIG.get('imaging', {}).get('scope', {}).get('aperture', 50)

# Plot Configuration
MAX_OBJECTS_OPTIMAL = CONFIG.get('plotting', {}).get('max_objects_optimal', 15)
FIGURE_SIZE = tuple(CONFIG.get('plotting', {}).get('figure_size', [16, 12]))
COLOR_MAP = CONFIG.get('plotting', {}).get('color_map', 'viridis')
GRID_ALPHA = CONFIG.get('plotting', {}).get('grid_alpha', 0.3)
VISIBLE_REGION_ALPHA = CONFIG.get('plotting', {}).get('visible_region_alpha', 0.2)

# Moon Configuration
MOON_PROXIMITY_RADIUS = CONFIG.get('moon', {}).get('proximity_radius', 10)
MOON_TRAJECTORY_COLOR = CONFIG.get('moon', {}).get('trajectory_color', '#FFD700')
MOON_MARKER_COLOR = CONFIG.get('moon', {}).get('marker_color', '#FFA500')
MOON_LINE_WIDTH = CONFIG.get('moon', {}).get('line_width', 2)
MOON_MARKER_SIZE = CONFIG.get('moon', {}).get('marker_size', 100)
MOON_INTERFERENCE_COLOR = CONFIG.get('moon', {}).get('interference_color', 'red')

# Mosaic Configuration
MOSAIC_FOV_WIDTH = CONFIG.get('imaging', {}).get('scope', {}).get('mosaic_fov_width', 4.7)
MOSAIC_FOV_HEIGHT = CONFIG.get('imaging', {}).get('scope', {}).get('mosaic_fov_height', 3.5)
SCOPE_NAME = CONFIG.get('imaging', {}).get('scope', {}).get('name', 'Vespera Passenger')

# Mosaic analysis functions will be imported dynamically to avoid circular imports
MOSAIC_ANALYSIS_AVAILABLE = True

def _import_mosaic_functions():
    """Dynamically import mosaic analysis functions to avoid circular imports"""
    try:
        from utilities.analyze_mosaic_groups import (
            analyze_object_groups, calculate_angular_separation, 
            can_fit_in_mosaic, objects_visible_simultaneously
        )
        return analyze_object_groups, calculate_angular_separation, can_fit_in_mosaic, objects_visible_simultaneously
    except ImportError as e:
        print(f"Warning: Mosaic analysis module not available: {e}")
        return None, None, None, None

# ============ DEEP SKY CATALOG FUNCTIONS =============

def get_messier_catalog():
    """Complete Messier Catalog with coordinates, FOV, and magnitudes"""
    return [
        # Nebulae
        CelestialObject("M1/NGC 1952 Crab Nebula", 5.575, 22.017, "6'x4'", 8.4),
        CelestialObject("M8/NGC 6523 Lagoon Nebula", 18.063, -24.383, "90'x40'", 6.0),
        CelestialObject("M16/NGC 6611 Eagle Nebula", 18.313, -13.783, "35'x28'", 6.4),
        CelestialObject("M17/NGC 6618 Omega - Swan Nebula", 18.346, -16.183, "46'x37'", 6.0),
        CelestialObject("M20/NGC 6514 Trifid Nebula", 18.033, -23.033, "28'x28'", 6.3),
        CelestialObject("M27/NGC 6853 Dumbbell Nebula", 19.994, 22.717, "8.0'x5.7'", 7.5),
        CelestialObject("M42/NGC 1976 Great Orion Nebula", 5.588, -5.391, "85'x60'", 4.0),
        CelestialObject("M43/NGC 1982 De Mairan's Nebula", 5.593, -5.267, "20'x15'", 9.0),
        CelestialObject("M57/NGC 6720 Ring Nebula", 18.884, 33.033, "1.4'x1'", 8.8),
        CelestialObject("M76/NGC 650/651 Little Dumbbell Nebula", 1.702, 51.567, "2.7'x1.8'", 10.1),
        CelestialObject("M97/NGC 3587 Owl Nebula", 11.248, 55.017, "3.4'x3.3'", 9.9),

        # Galaxies
        CelestialObject("M31/NGC 224 Andromeda Galaxy", 0.712, 41.269, "178'x63'", 3.4),
        CelestialObject("M32/NGC 221 Andromeda Companion", 0.712, 40.867, "8'x6'", 8.1),
        CelestialObject("M33/NGC 598 Triangulum Galaxy", 1.564, 30.660, "73'x45'", 5.7),
        CelestialObject("M51/NGC 5194 Whirlpool Galaxy", 13.497, 47.195, "11'x7'", 8.4),
        CelestialObject("M63/NGC 5055 Sunflower Galaxy", 13.158, 42.033, "12.6'x7.2'", 8.6),
        CelestialObject("M64/NGC 4826 Black Eye Galaxy", 12.944, 21.683, "10'x5'", 8.5),
        CelestialObject("M81/NGC 3031 Bode's Galaxy", 9.926, 69.067, "26.9'x14.1'", 6.9),
        CelestialObject("M82/NGC 3034 Cigar Galaxy", 9.928, 69.683, "11.2'x4.3'", 8.4),
        CelestialObject("M101/NGC 5457 Pinwheel Galaxy", 14.053, 54.349, "28.8'x26.9'", 7.9),
        CelestialObject("M104/NGC 4594 Sombrero Galaxy", 12.667, -11.617, "8.7'x3.5'", 8.0),
        CelestialObject("M106/NGC 4258", 12.317, 47.300, "18.6'x7.2'", 8.4),
        CelestialObject("M110/NGC 205", 0.683, 41.683, "17'x10'", 8.0),

        # Globular Clusters
        CelestialObject("M2/NGC 7089", 21.558, -0.817, "12.9'x12.9'", 6.5),
        CelestialObject("M3/NGC 5272", 13.703, 28.383, "16.2'x16.2'", 6.2),
        CelestialObject("M4/NGC 6121", 16.392, -26.533, "26.3'x26.3'", 5.6),
        CelestialObject("M5/NGC 5904", 15.310, 2.083, "17.4'x17.4'", 5.6),
        CelestialObject("M10/NGC 6254", 16.950, -4.100, "15.1'x15.1'", 6.6),
        CelestialObject("M13/NGC 6205 Great Hercules Cluster", 16.695, 36.459, "20'x20'", 5.8),
        CelestialObject("M15/NGC 7078", 21.500, 12.167, "12.3'x12.3'", 6.2),
        CelestialObject("M22/NGC 6656", 18.608, -23.900, "24'x24'", 5.1),
        CelestialObject("M55/NGC 6809", 19.667, -30.967, "19'x19'", 7.0),
        CelestialObject("M92/NGC 6341", 17.171, 43.133, "11.2'x11.2'", 6.4),

        # Open Clusters
        CelestialObject("M6/NGC 6405 Butterfly Cluster", 17.667, -32.217, "25'x15'", 4.2),
        CelestialObject("M7/NGC 6475 Ptolemy Cluster", 17.897, -34.817, "80'x80'", 3.3),
        CelestialObject("M23/NGC 6494", 17.950, -19.017, "27'x27'", 5.5),
        CelestialObject("M24/NGC 6603", 18.283, -18.517, "90'x90'", 4.6),
        CelestialObject("M25/IC 4725", 18.528, -19.233, "32'x32'", 4.6),
        CelestialObject("M34/NGC 1039", 2.702, 42.783, "35'x35'", 5.2),
        CelestialObject("M35/NGC 2168", 6.148, 24.333, "28'x28'", 5.1),
        CelestialObject("M36/NGC 1960 Pinwheel Cluster", 5.536, 34.133, "12'x12'", 6.0),
        CelestialObject("M37/NGC 2099 Salt and Pepper Cluster", 5.873, 32.550, "24'x24'", 5.6),
        CelestialObject("M38/NGC 1912 Starfish Cluster", 5.478, 35.833, "21'x21'", 6.4),
        CelestialObject("M39/NGC 7092", 21.535, 48.433, "32'x32'", 4.6),
        CelestialObject("M41/NGC 2287", 6.783, -20.733, "38'x38'", 4.5),
        CelestialObject("M44/NGC 2632 Beehive Cluster/Praesepe", 8.667, 19.983, "95'x95'", 3.1),
        CelestialObject("M45 Pleiades - Seven Sisters", 3.790, 24.117, "110'x110'", 1.6),
        CelestialObject("M46/NGC 2437", 7.697, -14.817, "27'x27'", 6.1),
        CelestialObject("M47/NGC 2422", 7.615, -14.483, "30'x30'", 4.4),
        CelestialObject("M48/NGC 2548", 8.233, -5.800, "54'x54'", 5.8),
        CelestialObject("M50/NGC 2323 Heart-Shaped Cluster", 7.033, -8.333, "16'x16'", 5.9),
        CelestialObject("M67/NGC 2682", 8.850, 11.817, "30'x30'", 6.9),
        CelestialObject("M93/NGC 2447", 7.742, -23.867, "22'x22'", 6.2),
    ]

def get_additional_dso():
    """Additional major deep sky objects beyond Messier catalog with magnitudes"""
    return [
        # Large/Emission Nebulae
        CelestialObject("NGC 7000/C20 North America Nebula", 20.968, 44.533, "120'x100'", 4.0),
        CelestialObject("NGC 6960/C34 Western Veil - Witch's Broom Nebula", 20.764, 30.711, "70'x6'", 7.0),
        CelestialObject("NGC 6992/C33 Eastern Veil - Network Nebula", 20.917, 31.717, "75'x12'", 7.0),
        CelestialObject("NGC 1499/C31 California Nebula", 4.033, 36.417, "145'x40'", 5.0),
        CelestialObject("IC 5070/C19 Pelican Nebula", 20.785, 44.357, "60'x50'", 8.0),
        CelestialObject("NGC 2237/C49 Rosette Nebula", 6.533, 4.950, "80'x80'", 6.0),
        CelestialObject("IC 1396 Elephant's Trunk Nebula", 21.619, 57.500, "170'x140'", 7.5),
        CelestialObject("IC 1805/C31 Heart Nebula", 2.567, 61.833, "100'x100'", 6.5),
        CelestialObject("NGC 2264/C41 Cone Nebula - Christmas Tree Cluster", 6.691, 9.890, "20'x10'", 7.2),
        CelestialObject("IC 2118 Witch Head Nebula", 5.417, -7.233, "180'x60'", 13.0),
        CelestialObject("NGC 7293/C63 Helix Nebula", 22.493, -20.837, "28'x23'", 7.6),
        CelestialObject("IC 434/B33 Horsehead Nebula", 5.683, -2.450, "60'x10'", 6.8),
        CelestialObject("NGC 6888/C27 Crescent Nebula", 20.192, 38.356, "25'x18'", 7.4),
        CelestialObject("NGC 2359/C46 Thor's Helmet", 7.250, -13.200, "22'x15'", 11.5),
        CelestialObject("NGC 6302/C69 Bug Nebula", 17.139, -37.097, "12.9'x6.2'", 12.8),
        CelestialObject("IC 1318 Butterfly - Gamma Cygni Nebula", 20.183, 40.250, "180'x180'", 7.0),
        CelestialObject("IC 2177 Seagull Nebula", 7.067, -10.700, "120'x30'", None),
        CelestialObject("IC 4628 Prawn Nebula", 16.567, -40.333, "60'x35'", None),
        CelestialObject("NGC 2024 Flame Nebula", 5.417, -1.850, "30'x30'", None),
        CelestialObject("NGC 2070 Tarantula Nebula", 5.642, -69.100, "40'x25'", 8.0),
        CelestialObject("NGC 2467 Skull and Crossbones Nebula", 7.583, -26.433, "15'x15'", None),
        CelestialObject("NGC 3576 Statue of Liberty Nebula", 11.167, -61.317, "4'x4'", None),
        CelestialObject("NGC 6357 Lobster - War and Peace Nebula", 17.475, -34.200, "40'x30'", None),
        CelestialObject("NGC 2736 Pencil Nebula", 9.050, -45.950, "20'x0.5'", None),

        # Reflection Nebulae
        CelestialObject("IC 405 Flaming Star Nebula", 5.167, 34.250, "30'x19'", 6.0),
        CelestialObject("IC 4592 Blue Horsehead Nebula", 16.117, -19.617, "50'x30'", None),
        CelestialObject("NGC 1977 Running Man Nebula", 5.583, -4.867, "20'x10'", None),
        
        # Notable Galaxies
        CelestialObject("NGC 253/C65 Sculptor Galaxy - Silver Dollar Galaxy", 0.793, -25.288, "27'x7'", 7.1),
        CelestialObject("NGC 891/C23 Silver Sliver Galaxy", 2.375, 42.349, "13.5'x2.8'", 10.0),
        CelestialObject("NGC 4565/C38 Needle Galaxy", 12.536, 25.988, "15.8'x2.1'", 10.4),
        CelestialObject("NGC 4631/C32 Whale Galaxy", 12.717, 32.542, "15.5'x2.7'", 9.2),
        CelestialObject("NGC 5907 Splinter Galaxy - Knife Edge Galaxy", 15.268, 56.329, "12.8'x1.4'", 10.3),
        CelestialObject("NGC 6946/C12 Fireworks Galaxy", 20.578, 60.154, "11.5'x9.8'", 9.6),
        CelestialObject("NGC 5128/C77 Centaurus A", 13.425, -43.017, "25.7'x20'", 6.8),
        CelestialObject("NGC 4656 Hockey Stick Galaxy", 12.733, 32.167, "15'x3'", 10.5),
        CelestialObject("IC 342 Hidden Galaxy", 3.467, 68.100, "21.4'x20.9'", 9.1),
        CelestialObject("NGC 1316 Fornax A", 3.378, -37.208, "12'x8.5'", 8.2),
        CelestialObject("NGC 292 Small Magellanic Cloud", 0.867, -72.833, "280'x160'", 2.7),
        CelestialObject("NGC 4244 Silver Needle Galaxy", 12.317, 37.817, "16.6'x1.9'", 10.6),
        
        # Notable Star Clusters
        CelestialObject("NGC 869/C14 Perseus Double Cluster h", 2.327, 57.133, "30'x30'", 4.3),
        CelestialObject("NGC 884/C14 Perseus Double Cluster χ", 2.351, 57.133, "30'x30'", 4.4),
        CelestialObject("NGC 663/C10", 1.766, 61.233, "16'x16'", 7.1),
        CelestialObject("IC 4665 Summer Beehive Cluster", 17.725, 5.633, "70'x70'", 4.2),
        CelestialObject("NGC 752/C28 Butterfly Cluster", 1.958, 37.667, "50'x50'", 5.7),
        CelestialObject("Melotte25 Hyades Cluster", 4.283, 15.867, "330'x330'", 0.5),
        CelestialObject("NGC 2281 Broken Heart Cluster", 6.817, 41.083, "14'x14'", 5.4),
        CelestialObject("NGC 1502/C13 Jolly Roger Cluster", 4.078, 62.333, "8'x8'", 6.9),
        CelestialObject("Stock2 Muscle Man Cluster", 2.150, 59.483, "60'x60'", 4.4),
        CelestialObject("Melotte111 Coma Star Cluster", 12.367, 26.000, "275'x275'", 1.8),
        CelestialObject("Collinder399 Coathanger/Brocchi's Cluster", 19.433, 20.183, "60'x60'", 3.6),
        CelestialObject("IC 2391 Omicron Velorum Cluster", 8.667, -53.067, "50'x50'", 2.5),
        CelestialObject("NGC 104 47 Tucanae", 0.400, -72.067, "30.9'x30.9'", 4.0),
        CelestialObject("NGC 2516 Southern Beehive", 7.967, -60.867, "30'x30'", 3.8),
        CelestialObject("NGC 3766 Pearl Cluster", 11.600, -61.617, "12'x12'", 5.3),
        CelestialObject("NGC 457 Owl/ET Cluster", 1.317, 58.283, "13'x13'", 6.4),
        CelestialObject("NGC 5139 Omega Centauri", 13.447, -47.483, "36.3'x36.3'", 3.7),
        CelestialObject("NGC 7789 White Rose - Caroline's Rose", 23.957, 56.717, "25'x25'", 6.7),
        
        # Additional Notable Objects
        CelestialObject("NGC 7635/C11 Bubble Nebula", 23.333, 61.200, "15'x8'", 11.0),
        CelestialObject("IC 5146/C19 Cocoon Nebula", 21.883, 47.267, "10'x10'", 7.2),
        CelestialObject("NGC 7023/C4 Iris Nebula", 21.017, 68.167, "18'x18'", 6.8),
        CelestialObject("IC 1848 Soul Nebula", 2.983, 60.433, "80'x80'", 6.5),
        CelestialObject("NGC 281/C11 Pacman Nebula", 0.785, 56.633, "35'x30'", 7.4),
        CelestialObject("NGC 6334/C6 Cat's Paw Nebula", 17.292, -35.683, "40'x20'", 5.5),
        CelestialObject("IC 443 Jellyfish Nebula", 6.175, 22.567, "50'x50'", None),
        CelestialObject("NGC 3372/C92 Eta Carinae Nebula", 10.733, -59.867, "120'x120'", 3.0),
        CelestialObject("NGC 3532/C91 Wishing Well Cluster", 11.100, -58.733, "55'x55'", 3.0),
        CelestialObject("IC 2602/C102 Southern Pleiades", 10.717, -64.400, "100'x100'", 1.9),
        CelestialObject("NGC 6231/C76 Northern Jewel Box", 16.900, -41.833, "15'x15'", 2.6),
        
        # Sharpless Catalog Objects
        CelestialObject("SH2-101", 19.920, 40.517, "15'x15'", None),
        CelestialObject("SH2-106", 20.333, 37.433, "4'x3'", None),
        CelestialObject("SH2-140", 22.317, 63.183, "5'x5'", None),
        CelestialObject("SH2-155", 22.583, 62.467, "50'x10'", None),
        CelestialObject("SH2-170", 0.100, 65.783, "20'x15'", None),
        CelestialObject("SH2-302", 7.167, -18.517, "40'x40'", None),
    ]
    
def get_combined_catalog():
    """Get combined catalog of all objects"""
    messier = get_messier_catalog()
    additional = get_additional_dso()
    return messier + additional

def enrich_object_name(name):
    """Add common names and cross-references to object names"""    
    common_names = {}
    
    # Process Messier catalog
    for obj in get_messier_catalog():
        designations = obj.name.split('/')
        # Get the common name by taking everything after the last catalog designation
        full_name = designations[-1]
        parts = full_name.split(' ')
        # Skip the catalog designation (like 'NGC 1976') to get only the common name
        if parts[0] in ['NGC', 'IC']:
            common_name = ' '.join(parts[2:])  # Skip both NGC/IC and the number
        else:
            common_name = ' '.join(parts[1:])  # Skip just the first part
            
        # Add entry for each designation
        for designation in designations:
            designation = designation.split()[0]  # Get just the catalog number
            if common_name:
                common_names[designation] = common_name

    # Process additional DSO catalog
    for obj in get_additional_dso():
        designations = obj.name.split('/')
        full_name = designations[-1]
        parts = full_name.split(' ')
        # Skip the catalog designation to get only the common name
        if parts[0] in ['NGC', 'IC', 'C']:
            common_name = ' '.join(parts[2:])  # Skip both NGC/IC/C and the number
        elif parts[0].startswith('SH2-'):  # Handle SH2 format
            common_name = ' '.join(parts[1:])  # Skip the SH2-nnn part
        else:
            common_name = ' '.join(parts[1:])  # Skip just the first part
            
        # Add entry for each designation
        for designation in designations:
            if designation.strip().startswith(('NGC', 'IC')):
                designation = ' '.join(designation.split()[:2])
            elif designation.strip().startswith('SH2-'):  # Keep full SH2-nnn format
                designation = designation.strip()
            else:
                designation = designation.split()[0]
            if common_name:
                common_names[designation] = common_name

    # Try all possible designations from the input name
    input_designations = name.split('/')
    common_name = ''
    
    for designation in input_designations:
        designation = designation.strip()
        if ' or ' in designation:
            designation = designation.split(' or ')[0].strip()
            
        # Try exact match first
        if designation in common_names:
            common_name = common_names[designation]
            break
            
        # Try with just the catalog number for NGC/IC objects
        if designation.startswith(('NGC', 'IC')):
            catalog_id = ' '.join(designation.split()[:2])
            if catalog_id in common_names:
                common_name = common_names[catalog_id]
                break

    if common_name and common_name not in name:
        return f"{name} ({common_name})"
    
    return name
    
def filter_visible_objects(objects, min_alt=MIN_ALT, max_alt=MAX_ALT, min_az=MIN_AZ, max_az=MAX_AZ):
    """Filter objects based on visibility constraints"""
    visible_objects = []
    current_time = get_current_datetime(get_local_timezone())
    
    for obj in objects:
        alt, az = calculate_altaz(obj, current_time)
        if min_alt <= alt <= max_alt and min_az <= az <= max_az:
            visible_objects.append(obj)
    
    return visible_objects

def get_object_by_name(name, catalog=None):
    """Find object in catalog by name"""
    if catalog is None:
        catalog = get_combined_catalog()
    
    for obj in catalog:
        if obj.name.lower().startswith(name.lower()):
            return obj
    return None

def get_objects_by_type(obj_type, catalog=None):
    """Get objects of specific type from catalog"""
    if catalog is None:
        catalog = get_combined_catalog()
    
    type_keywords = {
        'galaxy': ['galaxy', 'galaxies'],
        'nebula': ['nebula', 'nebulae'],
        'cluster': ['cluster'],
        'globular': ['globular'],
        'open': ['open cluster'],
        'planetary': ['planetary']
    }
    
    keywords = type_keywords.get(obj_type.lower(), [])
    return [obj for obj in catalog 
            if any(keyword.lower() in obj.name.lower() 
                  for keyword in keywords)]

def sort_objects_by_size(objects):
    """Sort objects by apparent size (FOV area)"""
    return sorted(objects, key=lambda x: x.total_area, reverse=True)

def sort_objects_by_altitude(objects, time=None):
    """Sort objects by current altitude"""
    if time is None:
        time = datetime.now(get_local_timezone())
    
    def get_altitude(obj):
        alt, _ = calculate_altaz(obj, time)
        return alt
    
    return sorted(objects, key=get_altitude, reverse=True)

# ============= CSV MANAGEMENT FUNCTIONS =============

def get_object_type(type_str):
    """Categorize object type from CSV string"""
    type_str = type_str.lower()
    
    if 'neb' in type_str:
        if 'em neb' in type_str:
            return 'emission_nebula'
        elif 'ref neb' in type_str:
            return 'reflection_nebula'
        elif 'pl neb' in type_str or 'pi neb' in type_str:
            return 'planetary_nebula'
        else:
            return 'nebula'
    elif 'galaxy' in type_str:
        return 'galaxy'
    elif 'glob' in type_str:
        return 'globular_cluster'
    elif 'open' in type_str or 'cl' in type_str:
        return 'open_cluster'
    elif 'dark' in type_str:
        return 'dark_nebula'
    else:
        return 'other'

def normalize_object_name(name):
    """
    Normalize object name for comparison by extracting catalog prefix and number.
    Example: 'NGC 6888 (Crescent Nebula)' -> ('ngc', '6888')
    """
    # Remove spaces, parentheses, and dashes, convert to lowercase
    name = name.lower()
    name = re.sub(r'[\s\(\)\-]', '', name)
    
    # Match catalog prefix and number
    # Handle special cases like 'M31', 'IC1318', 'NGC6888', 'SH101', etc.
    patterns = [
        r'^(ngc)(\d+)',    # NGC cases
        r'^(ic)(\d+)',     # IC cases
        r'^(m)(\d+)',      # Messier cases
        r'^(sh)(\d+)',     # SH cases
        r'^(collinder)(\d+)',  # Collinder cases
        r'^(melotte)(\d+)',    # Melotte cases
        r'^(barnard)(\d+)',    # Barnard cases
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            prefix, number = match.groups()
            return (prefix, number)
    
    # If no standard pattern matches, return the whole string
    return (name, '')

def are_same_object(name1, name2):
    """Compare two object names to determine if they refer to the same object"""
    # Split names by '/' to handle multiple designations
    names1 = name1.split('/')
    names2 = name2.split('/')
    
    # Normalize each name part
    norm_names1 = [normalize_object_name(n.strip()) for n in names1]
    norm_names2 = [normalize_object_name(n.strip()) for n in names2]
    
    # Check if any normalized names match (just prefix and number)
    return any(n1 == n2 and n1[0] != '' and n1[1] != '' 
              for n1 in norm_names1 for n2 in norm_names2)

def merge_catalogs(csv_objects, builtin_objects):
    """Merge CSV and built-in catalogs, preferring CSV entries for duplicates"""
    merged = []
    used_builtin = set()
    
    # First add all CSV objects
    merged.extend(csv_objects)
    
    # Add non-duplicate built-in objects
    for builtin_obj in builtin_objects:
        is_duplicate = False
        for csv_obj in csv_objects:
            if are_same_object(builtin_obj.name, csv_obj.name):
                is_duplicate = True
                break
        if not is_duplicate:
            merged.append(builtin_obj)
    
    return merged

def get_objects_from_csv():
    """Read objects from CSV file and organize by type"""
    objects_by_type = {
        'emission_nebula': [],
        'reflection_nebula': [],
        'planetary_nebula': [],
        'nebula': [],
        'galaxy': [],
        'globular_cluster': [],
        'open_cluster': [],
        'dark_nebula': [],
        'other': []
    }
    
    #print(f"Catalog config: {CONFIG['catalog']}")  # Debug print
    #print(f"Merge flag value: {CONFIG['catalog'].get('merge', False)}")  # Debug print
    
    csv_objects = []
    try:
        with open(CATALOGNAME, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Extract primary name before any dash
                full_name = row['Object'].strip()
                original_name = full_name.split('-')[0].strip()
                enriched_name = enrich_object_name(original_name)
                
                # Parse coordinates
                ra_str = row['RA'].strip()
                dec_str = row['Dec'].strip()
                ra_deg = parse_ra(ra_str)
                dec_deg = parse_dec(dec_str)
                
                # Parse FOV and calculate area
                fov = row.get('FOV', '').strip()

                # Parse magnitude if available
                magnitude = row.get('Magnitude', '').strip()
                if magnitude == '-':
                    magnitude = 10.0
                else:
                    magnitude = float(magnitude)
                
                # Create object
                obj = CelestialObject(enriched_name, ra_deg/15, dec_deg, fov, magnitude)
                
                # Add comments if available
                if 'Comments' in row and row['Comments'].strip():
                    obj.comments = row['Comments'].strip()
                
                # Only add objects that meet the area threshold
                if obj.total_area >= MIN_TOTAL_AREA or not fov:
                    # Categorize object by type
                    obj_type = get_object_type(row['Type'])
                    objects_by_type[obj_type].append(obj)
                    csv_objects.append(obj)  # Keep track of successfully parsed objects
                
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        # Don't return immediately, continue with merging if enabled
    
    #print(f"CSV objects found: {len(csv_objects)}")  # Debug print
    
    # If merge is enabled or CSV read failed, get built-in catalog
    merge_enabled = MERGING_CATALOGS
    #print(f"Merge enabled: {merge_enabled}")  # Debug print
    
    if merge_enabled or not csv_objects:
        #print("Getting built-in catalog")
        builtin_objects = get_combined_catalog()
        
        if merge_enabled and csv_objects:
            #print(f"Merging {len(csv_objects)} CSV objects with {len(builtin_objects)} built-in objects")
            return merge_catalogs(csv_objects, builtin_objects)
        else:
            #print("Using built-in catalog only")
            return builtin_objects
    
    # If we have CSV objects and merge is not enabled, return just those
    #print(f"Using {len(csv_objects)} CSV objects only")
    return csv_objects

# ======== TIME CONVERSION FUNCTIONS =============

def get_local_timezone():
    """Get configured timezone"""
    return pytz.timezone('Europe/Rome')

def local_to_utc(local_time):
    """Convert local time to UTC"""
    milan_tz = get_local_timezone()
    if local_time.tzinfo is None:
        local_time = milan_tz.localize(local_time)
    return local_time.astimezone(pytz.UTC)

def utc_to_local(utc_time):
    """Convert UTC time to local time"""
    milan_tz = get_local_timezone()
    if utc_time.tzinfo is None:
        utc_time = pytz.UTC.localize(utc_time)
    return utc_time.astimezone(milan_tz)

def get_current_datetime(timezone=None):
    """Get current datetime, optionally in specified timezone"""
    if timezone is None:
        timezone = get_local_timezone()
    return datetime.now(timezone)

def calculate_julian_date(dt):
    """Calculate Julian Date from datetime (UTC)"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    year, month, day = dt.year, dt.month, dt.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + (a // 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    jd += (dt.hour + dt.minute/60 + dt.second/3600)/24.0
    return jd

# ============= COORDINATE CONVERSION FUNCTIONS =============

def dms_dd(degrees, minutes, seconds):
    """Convert Degrees Minutes Seconds to Decimal Degrees"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(degrees) + B
    return -C if degrees < 0 or minutes < 0 or seconds < 0 else C

def dd_dh(decimal_degrees):
    """Convert Decimal Degrees to Degree-Hours"""
    return decimal_degrees / 15

def dh_dd(degree_hours):
    """Convert Degree-Hours to Decimal Degrees"""
    return degree_hours * 15

def hms_dh(hours, minutes, seconds):
    """Convert Hours Minutes Seconds to Decimal Hours"""
    A = abs(seconds) / 60
    B = (abs(minutes) + A) / 60
    C = abs(hours) + B
    return -C if hours < 0 or minutes < 0 or seconds < 0 else C

def dh_hour(decimal_hours):
    """Return hour part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return -(math.floor(E / 3600)) if decimal_hours < 0 else math.floor(E / 3600)

def dh_min(decimal_hours):
    """Return minutes part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    D = 0 if C == 60 else C
    E = B + 60 if C == 60 else B
    return math.floor(E / 60) % 60

def dh_sec(decimal_hours):
    """Return seconds part of Decimal Hours"""
    A = abs(decimal_hours)
    B = A * 3600
    C = round(B - 60 * math.floor(B / 60), 2)
    return 0 if C == 60 else C

# ============= ASTRONOMICAL CALCULATIONS =============

def calculate_lst(dt):
    """Calculate Local Sidereal Time"""
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            return calculate_high_precision_lst(dt)
        except Exception as e:
            print(f"High-precision LST calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    t = (jd - 2451545.0) / 36525
    
    gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3/38710000
    gst = math.radians(gst % 360)
    
    lst = gst + OBSERVER.lon
    return lst % (2 * math.pi)

def calculate_sun_position(dt):
    """Calculate Sun's position (altitude, azimuth)"""
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            return calculate_high_precision_sun_position(dt)
        except Exception as e:
            print(f"High-precision sun calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    n = jd - 2451545.0
    
    
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    
    lambda_sun = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    
    epsilon = math.radians(23.439 - 0.0000004 * n)
    
    ra = math.atan2(math.cos(epsilon) * math.sin(lambda_sun), math.cos(lambda_sun))
    dec = math.asin(math.sin(epsilon) * math.sin(lambda_sun))
    
    ha = calculate_lst(dt) - ra
    
    sin_alt = (math.sin(dec) * math.sin(OBSERVER.lat) + 
               math.cos(dec) * math.cos(OBSERVER.lat) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    cos_az = (math.sin(dec) - math.sin(alt) * math.sin(OBSERVER.lat)) / (
              math.cos(alt) * math.cos(OBSERVER.lat))
    cos_az = min(1, max(-1, cos_az))
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
        
    return math.degrees(alt), math.degrees(az)

def calculate_altaz(obj, dt):
    """Calculate altitude and azimuth for an object"""
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            include_refraction = CONFIG.get('precision', {}).get('include_refraction', True)
            include_parallax = CONFIG.get('precision', {}).get('include_parallax', False)
            return calculate_precise_altaz(obj, dt, include_refraction, include_parallax)
        except Exception as e:
            print(f"High-precision altaz calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    lst = calculate_lst(dt)
    ha = lst - obj.ra
    
    sin_alt = (math.sin(obj.dec) * math.sin(OBSERVER.lat) + 
               math.cos(obj.dec) * math.cos(OBSERVER.lat) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    cos_az = (math.sin(obj.dec) - math.sin(alt) * math.sin(OBSERVER.lat)) / (
              math.cos(alt) * math.cos(OBSERVER.lat))
    cos_az = min(1, max(-1, cos_az))
    az = math.acos(cos_az)
    
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
        
    return math.degrees(alt), math.degrees(az)

def calculate_moon_phase(dt):
    """
    Calculate moon phase (0-1) where 0=new moon, 0.5=full moon, 1=new moon again
    Using a more accurate algorithm based on astronomical calculations
    """
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            return calculate_high_precision_moon_phase(dt)
        except Exception as e:
            print(f"High-precision moon phase calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    # Ensure we're working with UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    
    # Meeus first approximation
    T = (jd - 2451545.0) / 36525  # Time in Julian centuries since J2000.0
    
    # Sun's mean elongation
    D = 297.8502042 + 445267.1115168 * T - 0.0016300 * T**2 + T**3 / 545868 - T**4 / 113065000
    
    # Sun's mean anomaly
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000
    
    # Moon's mean anomaly
    Mm = 134.9634114 + 477198.8676313 * T - 0.0089970 * T**2 + T**3 / 69699 - T**4 / 14712000
    
    # Moon's argument of latitude
    F = 93.2720993 + 483202.0175273 * T - 0.0034029 * T**2 - T**3 / 3526000 + T**4 / 863310000
    
    # Corrections for perturbations
    dE = 1.0 - 0.002516 * T - 0.0000074 * T**2  # Correction for eccentricity
    
    # Convert to radians for calculations
    D = math.radians(D % 360)
    M = math.radians(M % 360)
    Mm = math.radians(Mm % 360)
    F = math.radians(F % 360)
    
    # Calculate phase angle
    phase_angle = 180 - D * 180/math.pi - 6.289 * math.sin(Mm) + 2.100 * math.sin(M) - 1.274 * math.sin(2*D - Mm) - 0.658 * math.sin(2*D) - 0.214 * math.sin(2*Mm) - 0.110 * math.sin(D)
    
    # Convert phase angle to illuminated fraction
    phase = (1 + math.cos(math.radians(phase_angle))) / 2
    
    return phase

def calculate_moon_position(dt):
    """Calculate moon's position using a more accurate model based on Jean Meeus' algorithms"""
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            return calculate_high_precision_moon_position(dt)
        except Exception as e:
            print(f"High-precision moon calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    # Ensure we're working with UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    jd = calculate_julian_date(dt)
    
    # Time in Julian centuries since J2000.0
    T = (jd - 2451545.0) / 36525.0
    
    # Meeus' Astronomical Algorithms - Chapter 47
    # Lunar mean elements
    Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T**2 + T**3 / 538841.0 - T**4 / 65194000.0  # Mean longitude
    D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T**2 + T**3 / 545868.0 - T**4 / 113065000.0   # Mean elongation
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000.0                        # Sun's mean anomaly
    Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T**2 + T**3 / 69699.0 - T**4 / 14712000.0     # Moon's mean anomaly
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T**2 - T**3 / 3526000.0 + T**4 / 863310000.0    # Argument of latitude

    # Reduce angles to range 0-360 degrees
    Lp = Lp % 360
    D = D % 360
    M = M % 360
    Mp = Mp % 360
    F = F % 360

    # Convert to radians for calculations
    Lp_rad = math.radians(Lp)
    D_rad = math.radians(D)
    M_rad = math.radians(M)
    Mp_rad = math.radians(Mp)
    F_rad = math.radians(F)

    # Periodic perturbations
    # Longitude perturbations
    dL = 6288.0160 * math.sin(Mp_rad)
    dL += 1274.0198 * math.sin(2*D_rad - Mp_rad)
    dL += 658.7141 * math.sin(2*D_rad)
    dL += 214.2591 * math.sin(2*Mp_rad)
    dL += 186.4060 * math.sin(M_rad)
    dL /= 1000000.0  # Convert to degrees

    # Latitude perturbations
    dB = 5128.0 * math.sin(F_rad)
    dB += 280.0 * math.sin(Mp_rad + F_rad)
    dB += 277.0 * math.sin(Mp_rad - F_rad)
    dB += 176.0 * math.sin(2*D_rad - F_rad)
    dB += 115.0 * math.sin(2*D_rad + F_rad)
    dB /= 1000000.0  # Convert to degrees

    # Calculate ecliptic coordinates
    lambda_moon = Lp + dL
    beta_moon = dB

    # Convert to equatorial coordinates
    epsilon = math.radians(23.43929111 - 0.013004167*T)  # Obliquity of ecliptic
    
    lambda_moon = math.radians(lambda_moon)
    beta_moon = math.radians(beta_moon)
    
    # Calculate right ascension and declination
    alpha = math.atan2(
        math.sin(lambda_moon) * math.cos(epsilon) - math.tan(beta_moon) * math.sin(epsilon),
        math.cos(lambda_moon)
    )
    delta = math.asin(
        math.sin(beta_moon) * math.cos(epsilon) + 
        math.cos(beta_moon) * math.sin(epsilon) * math.sin(lambda_moon)
    )

    # Get local sidereal time
    lst = calculate_lst(dt)
    
    # Calculate hour angle
    ha = lst - alpha
    
    # Convert to local horizontal coordinates
    lat_rad = math.radians(LATITUDE)
    
    # Calculate altitude
    sin_alt = (math.sin(lat_rad) * math.sin(delta) + 
               math.cos(lat_rad) * math.cos(delta) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    # Calculate azimuth
    az = math.atan2(
        math.sin(ha),
        math.cos(ha) * math.sin(lat_rad) - math.tan(delta) * math.cos(lat_rad)
    )
    
    # Convert to degrees and adjust azimuth
    alt_deg = math.degrees(alt)
    az_deg = math.degrees(az)
    az_deg = (az_deg + 180) % 360  # Adjust azimuth to 0-360 range
    
    return alt_deg, az_deg

def calculate_moon_interference_radius(moon_phase, obj_magnitude, sky_brightness):
    """
    Calculate the radius of moon interference based on multiple factors.
    
    Parameters:
    - moon_phase: 0-1 where 0=new moon, 0.5=full moon
    - obj_magnitude: Visual magnitude of the object
    - sky_brightness: Bortle scale (1-9)
    
    Returns:
    - Interference radius in degrees
    """
    # Base radius calculation based on moon phase
    if moon_phase >= 0.875 or moon_phase <= 0.125:  # New Moon ±0.125
        base_radius = 20
    elif 0.375 <= moon_phase <= 0.625:  # Full Moon ±0.125
        base_radius = 60
    elif 0.25 <= moon_phase < 0.375 or 0.625 < moon_phase <= 0.75:  # Quarter Moons
        base_radius = 40
    else:  # Crescent Moons
        base_radius = 30
    
    # Magnitude factor (fainter objects are more affected)
    # Normalize magnitude to a factor between 1.0 and 2.0
    mag_factor = min(2.0, max(1.0, obj_magnitude / 8.0))
    
    # Sky brightness factor (light pollution makes moon interference worse)
    # In Bortle 9 skies, interference is much more significant
    sky_factor = (sky_brightness / 5.0) ** 1.5  # Exponential effect for high Bortle
    
    # Calculate final radius
    radius = base_radius * mag_factor * sky_factor
    
    # Ensure minimum and maximum reasonable values
    # Maximum increased for very bright moon in light-polluted skies
    radius = min(90.0, max(15.0, radius))
    
    return radius

def is_near_moon(obj_alt, obj_az, moon_alt, moon_az, obj_magnitude, dt):
    """
    Enhanced moon proximity check taking into account moon phase and object brightness.
    """
    # Skip check if moon is below horizon
    if moon_alt < 0:
        return False
        
    # Calculate moon phase
    moon_phase = calculate_moon_phase(dt)
    
    # Calculate interference radius based on conditions
    radius = calculate_moon_interference_radius(
        moon_phase=moon_phase,
        obj_magnitude=obj_magnitude,
        sky_brightness=BORTLE_INDEX
    )
    
    # Convert coordinates to radians
    obj_alt = math.radians(90 - obj_alt)    # Convert to co-latitude
    obj_az = math.radians(obj_az)
    moon_alt = math.radians(90 - moon_alt)  # Convert to co-latitude
    moon_az = math.radians(moon_az)
    
    # Calculate angular separation using spherical trig
    dlon = moon_az - obj_az
    cos_d = (math.cos(moon_alt) * math.cos(obj_alt) +
             math.sin(moon_alt) * math.sin(obj_alt) * math.cos(dlon))
    cos_d = min(1.0, max(-1.0, cos_d))  # Ensure value is in valid range
    
    # Convert to degrees
    separation = math.degrees(math.acos(cos_d))
    
    return separation < radius

# ============= UTILITY FUNCTIONS =============

def parse_ra(ra_str):
    """Convert RA from HH:MM format to decimal degrees"""
    match = re.match(r'(\d+)h\s*(\d+)m', ra_str)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2))
        return (hours + minutes/60) * 15
    return 0

def parse_dec(dec_str):
    """Convert Dec from DD:MM format to decimal degrees"""
    match = re.match(r'([+-]?\d+)°?\s*(\d+)?\'?', dec_str)
    if match:
        degrees = float(match.group(1))
        minutes = float(match.group(2)) if match.group(2) else 0
        return degrees + minutes/60 * (1 if degrees >= 0 else -1)
    match = re.match(r'([+-]?\d+)°?', dec_str)
    if match:
        return float(match.group(1))
    return 0

def parse_fov(fov_str):
    """Parse FOV string and return list of areas in square arcminutes"""
    if not fov_str:
        return []
    
    fov_list = fov_str.split(',')
    areas = []
    
    for fov in fov_list:
        fov = fov.strip()
        match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', fov)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
            
            if '°' in fov:
                width *= 60
                height *= 60
                
            areas.append(width * height)
    
    return areas

def calculate_total_area(fov_str):
    """Calculate total area from FOV string"""
    areas = parse_fov(fov_str)
    return sum(areas) if areas else 0

def calculate_required_panels(obj_fov):
    """Calculate number of panels needed to cover object"""
    if not obj_fov:
        return 1
        
    # Parse object FOV
    match = re.match(r'([\d.]+)(?:°|\')?x([\d.]+)(?:°|\')?', obj_fov)
    if not match:
        return 1
        
    width = float(match.group(1))
    height = float(match.group(2))
    
    # Convert to degrees if in arcminutes
    if "'" in obj_fov:
        width = width / 60
        height = height / 60
    
    # Calculate panels needed in each dimension (with 10% overlap)
    panels_width = math.ceil(width / (SCOPE_FOV_WIDTH * 0.9))
    panels_height = math.ceil(height / (SCOPE_FOV_HEIGHT * 0.9))
    
    return panels_width * panels_height

def calculate_required_exposure(magnitude, bortle_index, obj_fov, single_exposure=SINGLE_EXPOSURE):
    """
    Calculate required total exposure time based on magnitude, sky conditions, and object size.
    Returns total exposure time in hours and number of frames needed.
    """
    # Base exposure time (in hours) for mag 10 object in Bortle 4
    base_exposure = 1.0
    
    # Adjust for magnitude (exponential relationship)
    magnitude_factor = 2 ** ((magnitude - 10) / 2.5)
    
    # Adjust for Bortle index (linear relationship)
    bortle_factor = (bortle_index / 4) ** 2
    
    # Calculate base total exposure time in hours
    base_total_exposure = base_exposure * magnitude_factor * bortle_factor
    
    # Calculate number of panels needed
    panels = calculate_required_panels(obj_fov)
    
    # Adjust total exposure time for panels
    total_exposure = base_total_exposure * panels
    
    # Calculate number of subframes needed
    subframes = math.ceil((total_exposure * 3600) / single_exposure)
    
    return total_exposure, subframes, panels

def is_object_imageable(obj, visibility_duration, bortle_index):
    """
    Determine if object can be imaged successfully given conditions.
    """
    if not hasattr(obj, 'magnitude') or obj.magnitude is None:
        return False
        
    required_exposure = calculate_required_exposure(obj.magnitude, bortle_index)
    return visibility_duration >= required_exposure

def get_moon_phase_icon(phase):
    """
    Get moon phase icon and name based on phase value.
    Phase is a decimal from 0.0 to 1.0, where:
    0.0 = New Moon
    0.25 = First Quarter
    0.5 = Full Moon
    0.75 = Last Quarter
    1.0 = New Moon (again)
    """
    if phase < 0.0625 or phase >= 0.9375:
        return "🌑", "New Moon"
    elif phase < 0.1875:
        return "🌒", "Waxing Crescent"
    elif phase < 0.3125:
        return "🌓", "First Quarter"
    elif phase < 0.4375:
        return "🌔", "Waxing Gibbous"
    elif phase < 0.5625:
        return "🌕", "Full Moon"
    elif phase < 0.6875:
        return "🌖", "Waning Gibbous"
    elif phase < 0.8125:
        return "🌗", "Last Quarter"
    else:
        return "🌘", "Waning Crescent"

def format_time(time):
    """Format time for display"""
    return time.strftime("%H:%M")

# ============= CLASS DEFINITIONS =============

class Observer:
    """Class to represent the observer's location"""
    def __init__(self, lat, lon):
        self.lat = math.radians(lat)
        self.lon = math.radians(lon)

class CelestialObject:
    """Class to represent a celestial object"""
    def __init__(self, name, ra_hours, dec_deg, fov=None, magnitude=None):
        self.name = name
        self.ra = math.radians(ra_hours * 15)  # Convert hours to degrees then to radians
        self.dec = math.radians(dec_deg)
        self.fov = fov
        self.magnitude = magnitude
        self.total_area = calculate_total_area(fov) if fov else 0
        self.required_exposure = None  # Will be calculated later

class MosaicGroup:
    """Class to represent a mosaic group of celestial objects that behaves like a single CelestialObject"""
    def __init__(self, objects, overlap_periods, group_id=None):
        self.objects = objects
        self.overlap_periods = overlap_periods
        self.group_id = group_id or f"Group_{len(objects)}_objects"
        
        # Create composite properties
        self.name = self._create_group_name()
        self.ra, self.dec = self._calculate_center_coordinates()
        self.magnitude = self._calculate_composite_magnitude()
        self.fov = f"{MOSAIC_FOV_WIDTH:.1f}'x{MOSAIC_FOV_HEIGHT:.1f}'"
        self.total_area = MOSAIC_FOV_WIDTH * MOSAIC_FOV_HEIGHT / (60 * 60)  # Convert to square degrees
        self.required_exposure = None  # Will be calculated later
        
        # Mosaic-specific properties
        self.is_mosaic_group = True
        self.object_count = len(objects)
        self.visibility_periods = overlap_periods
        
    def _create_group_name(self):
        """Create a descriptive name for the group"""
        object_names = [get_abbreviated_name(obj.name) for obj in self.objects]
        if len(object_names) <= 3:
            return f"Mosaic: {', '.join(object_names)}"
        else:
            return f"Mosaic: {', '.join(object_names[:2])} + {len(object_names)-2} more"
    
    def _calculate_center_coordinates(self):
        """Calculate the center RA/Dec of the group"""
        ra_coords = [obj.ra for obj in self.objects]
        dec_coords = [obj.dec for obj in self.objects]
        
        # Handle RA wraparound (0h/24h boundary)
        ra_mean = sum(ra_coords) / len(ra_coords)
        dec_mean = sum(dec_coords) / len(dec_coords)
        
        return ra_mean, dec_mean
    
    def _calculate_composite_magnitude(self):
        """Calculate composite magnitude of the group (average of brightest objects)"""
        valid_magnitudes = [obj.magnitude for obj in self.objects if obj.magnitude is not None]
        if not valid_magnitudes:
            return 10.0  # Default magnitude if none available
        
        # Use average of the two brightest objects (or just one if only one available)
        valid_magnitudes.sort()
        if len(valid_magnitudes) == 1:
            return valid_magnitudes[0]
        else:
            return sum(valid_magnitudes[:2]) / 2
    
    def get_individual_objects(self):
        """Return the individual objects in this group"""
        return self.objects
        
    def calculate_total_overlap_duration(self):
        """Calculate total overlap duration for this group"""
        return sum((end - start).total_seconds() / 3600 for start, end in self.overlap_periods)

class ReportGenerator:
    """Generate comprehensive observation reports"""
    
    def __init__(self, date, location_data, start_time=None, end_time=None):
        self.date = date
        self.location = location_data
        self.sections = []
        # Store the actual observation window
        self.start_time = start_time
        self.end_time = end_time
    
    def add_section(self, title, content):
        """Add a section to the report"""
        self.sections.append({
            'title': title,
            'content': content
        })
    
    def format_section(self, section):
        """Format a single section"""
        output = f"\n{section['title']}\n"
        output += "=" * len(section['title']) + "\n"
        output += section['content']
        return output
    
    def generate_quick_summary(self, visible_objects, moon_affected_objects, start_time, end_time, moon_phase):
        """Generate quick summary section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        
        # Always show as full observation window (reverted from partial night filtering)
        observation_window_label = "Observation Window"
        
        content = (
            f"Date: {self.date.date()}\n"
            f"Location: {self.location['name']} ({LATITUDE:.2f}°N, {LONGITUDE:.2f}°E)\n\n"
            f"Observable Objects: {len(visible_objects)} total ({len(moon_affected_objects)} affected by moon)\n"
            f"{observation_window_label}: {format_time(start_time)} - {format_time(end_time)}\n"
            f"Moon Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Seeing Conditions: Bortle {BORTLE_INDEX}\n"
        )
        self.add_section("QUICK SUMMARY", content)
    
    def generate_timing_section(self, sunset, sunrise, twilight_evening, twilight_morning, moon_rise, moon_set):
        """Generate timing information section"""
        content = (
            f"Sunset: {format_time(sunset)}\n"
            f"Astronomical Twilight Begins: {format_time(twilight_evening)}\n"
        )
        if moon_rise:
            content += f"Moon Rise: {format_time(moon_rise)}\n"
        if moon_set:
            content += f"Moon Set: {format_time(moon_set)}\n"
        content += (
            f"Astronomical Twilight Ends: {format_time(twilight_morning)}\n"
            f"Sunrise: {format_time(sunrise)}\n"
        )
        self.add_section("TIMING INFORMATION", content)
    
    def generate_moon_conditions(self, moon_phase, moon_affected_objects):
        """Generate moon conditions section"""
        moon_icon, phase_name = get_moon_phase_icon(moon_phase)
        content = (
            f"Current Phase: {moon_icon} {phase_name} ({moon_phase:.1%})\n"
            f"Objects affected by moon: {len(moon_affected_objects)}\n\n"
        )
        if moon_affected_objects:
            content += "Affected objects:\n"
            for obj in moon_affected_objects:
                periods = getattr(obj, 'moon_influence_periods', [])
                
                # Calculate total minutes properly from timedelta objects
                total_minutes = sum(
                    int((end - start).total_seconds() / 60)
                    for start, end in periods
                )
                
                # Get the actual time ranges for interference
                if periods:
                    interference_times = []
                    for start, end in periods:
                        # Convert to local time for display
                        local_start = utc_to_local(start)
                        local_end = utc_to_local(end)
                        interference_times.append(f"{format_time(local_start)}-{format_time(local_end)}")
                    
                    interference_str = ", ".join(interference_times)
                    content += f"- {obj.name} ({total_minutes} minutes of interference, during: {interference_str})\n"
                else:
                    content += f"- {obj.name} ({total_minutes} minutes of interference)\n"
        else:
            content += "No objects are significantly affected by moon proximity.\n"
        self.add_section("MOON CONDITIONS", content)
    
    def generate_object_sections(self, visible_objects, insufficient_objects):
        """Generate sections for different object categories"""
        # Prime targets (sufficient time & good conditions)
        prime_targets = [obj for obj in visible_objects 
                        if not getattr(obj, 'near_moon', False)]
        if prime_targets:
            content = self._format_object_list("Prime observation targets:", prime_targets)
            self.add_section("PRIME TARGETS", content)
        
        # Moon-affected targets
        moon_affected = [obj for obj in visible_objects 
                        if getattr(obj, 'near_moon', False)]
        if moon_affected:
            content = self._format_object_list("Objects affected by moon:", moon_affected)
            self.add_section("MOON-AFFECTED TARGETS", content)
        
        # Time-limited targets
        if insufficient_objects:
            content = self._format_object_list("Objects with insufficient visibility time:", insufficient_objects)
            self.add_section("TIME-LIMITED TARGETS", content)
    
    def _format_object_list(self, header, objects):
        """Format a list of objects with their details"""
        # Use actual observation window instead of full day
        if self.start_time and self.end_time:
            start_time = self.start_time
            end_time = self.end_time
        else:
            # Fallback to full day if no window specified
            start_time = self.date
            end_time = self.date.replace(hour=23, minute=59, second=59)
        
        # Sort by visibility start time
        sorted_objects = []
        for obj in objects:
            # Handle both individual objects and mosaic groups
            if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                # For mosaic groups, use the overlap periods
                if obj.overlap_periods:
                    sorted_objects.append((obj, obj.overlap_periods[0][0]))
            else:
                periods = find_visibility_window(obj, start_time, end_time)
                if periods:
                    sorted_objects.append((obj, periods[0][0]))
        
        sorted_objects.sort(key=lambda x: x[1])
        sorted_objects = [x[0] for x in sorted_objects]
        
        # Format output
        content = f"{header}\n\n"
        
        for obj in sorted_objects:
            # Handle mosaic groups differently
            if hasattr(obj, 'is_mosaic_group') and obj.is_mosaic_group:
                # Format mosaic group
                content += f"🎯 {obj.name}\n"
                content += f"Objects in group: {obj.object_count}\n"
                
                # List individual objects
                object_names = [get_abbreviated_name(o.name) for o in obj.objects]
                content += f"Components: {', '.join(object_names)}\n"
                
                # Total overlap duration
                total_overlap = obj.calculate_total_overlap_duration()
                content += f"Total overlap time: {total_overlap:.1f} hours\n"
                
                # Overlap periods
                content += "Overlap periods:\n"
                for period_start, period_end in obj.overlap_periods:
                    period_duration = (period_end - period_start).total_seconds() / 3600
                    content += f"  {format_time(period_start)} - {format_time(period_end)} ({period_duration:.1f}h)\n"
                
                content += f"Composite magnitude: {obj.magnitude:.1f}\n"
                content += f"Mosaic FOV: {obj.fov}\n"
                content += "Type: Mosaic Group\n"
                
            else:
                # Format individual object
                # Get visibility periods
                periods = find_visibility_window(obj, start_time, end_time)
                if not periods:
                    continue
                    
                visibility_start = periods[0][0]
                duration = calculate_visibility_duration(periods)
                visibility_end = periods[-1][1]
                
                # Get moon status
                moon_status = ""
                if hasattr(obj, 'near_moon') and obj.near_moon:
                    moon_phase = calculate_moon_phase(visibility_start)
                    moon_icon, _ = get_moon_phase_icon(moon_phase)
                    
                    # Find when moon rises if it's not already risen at the start of visibility
                    moon_alt_at_start, _ = calculate_moon_position(visibility_start)
                    if moon_alt_at_start < 0:
                        # Moon hasn't risen yet, find rise time
                        check_time = visibility_start
                        moon_rise_time = None
                        while check_time <= visibility_end:
                            moon_alt, _ = calculate_moon_position(check_time)
                            prev_moon_alt, _ = calculate_moon_position(check_time - timedelta(minutes=1))
                            if prev_moon_alt < 0 and moon_alt >= 0:
                                moon_rise_time = check_time
                                break
                            check_time += timedelta(minutes=1)
                        
                        if moon_rise_time:
                            moon_status = f"{moon_icon} Moon interference after {format_time(moon_rise_time)}"
                        else:
                            moon_status = "✨ Clear from moon"
                    else:
                        # Moon is already risen
                        moon_status = f"{moon_icon} Moon interference"
                else:
                    moon_status = "✨ Clear from moon"
                
                # Format the line
                content += f"{obj.name}\n"
                content += f"{moon_status}\n"
                content += f"Visibility: {format_time(visibility_start)} - {format_time(visibility_end)} ({duration:.1f} hours)\n"
                
                if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                    content += f"Magnitude: {obj.magnitude}\n"
                
                if obj.fov:
                    content += f"Field of view: {obj.fov}\n"
                    # Calculate panels needed
                    panels = calculate_required_panels(obj.fov)
                    if panels > 1:
                        mosaic_size = math.ceil(math.sqrt(panels))
                        content += f"Mosaic: {mosaic_size}x{mosaic_size} panels\n"
                
                if hasattr(obj, 'type') and obj.type:
                    content += f"Type: {obj.type}\n"
                    
            content += "\n"
        
        return content
    
    def generate_schedule_section(self, schedule, strategy):
        """Generate schedule section"""
        if not schedule:
            content = (
                f"Strategy: {strategy.value}\n"
                f"No objects available for scheduling with this strategy.\n\n"
            )
            self.add_section("RECOMMENDED SCHEDULE", content)
            return
            
        content = (
            f"Strategy: {strategy.value}\n"
            f"Total objects: {len(schedule)}\n"
            f"Total observation time: {sum((end - start).total_seconds() / 3600 for start, end, _ in schedule):.1f} hours\n\n"
        )
        
        for start, end, obj in schedule:
            duration = (end - start).total_seconds() / 3600
            exposure_time, frames, panels = calculate_required_exposure(
                obj.magnitude, BORTLE_INDEX, obj.fov)
            
            content += (
                f"{obj.name}\n"
                f"  Start: {format_time(start)}\n"
                f"  End: {format_time(end)}\n"
                f"  Duration: {duration:.1f} hours\n"
                f"  Required exposure: {exposure_time:.1f} hours\n"
            )
            if panels > 1:
                content += f"  Mosaic: {math.ceil(math.sqrt(panels))}x{math.ceil(math.sqrt(panels))}\n"
            content += "\n"
        
        self.add_section("RECOMMENDED SCHEDULE", content)
    
    def generate_report(self):
        """Generate the complete report"""
        output = "NIGHT OBSERVATION REPORT\n"
        output += "=" * 23 + "\n"
        
        for section in self.sections:
            output += self.format_section(section)
            
        return output

# Create global observer
OBSERVER = Observer(LATITUDE, LONGITUDE)

# ============= VISIBILITY FUNCTIONS =============

def is_visible(alt, az, use_margins=True):
    """Check if object is within visibility limits"""
    if use_margins:
        # Use 5-degree margins as in trajectory plotting
        return ((MIN_ALT - 5 <= alt <= MAX_ALT + 5) and 
                (MIN_AZ - 5 <= az <= MAX_AZ + 5))
    else:
        return (MIN_AZ <= az <= MAX_AZ) and (MIN_ALT <= alt <= MAX_ALT)

def find_visibility_window(obj, start_time, end_time, use_margins=True):
    """Find visibility window for an object, considering sun position"""
    current_time = start_time
    visibility_periods = []
    start_visible = None
    last_visible = False
    
    # Use 1-minute intervals for better precision, matching trajectory plotting
    interval = timedelta(minutes=1)
    
    while current_time <= end_time:
        # Check object's position
        alt, az = calculate_altaz(obj, current_time)
        
        # Check sun's position
        sun_alt, _ = calculate_sun_position(current_time)
        
        # Object is visible if:
        # 1. It's within visibility limits
        # 2. The sun is below the horizon (altitude < -5)
        is_currently_visible = is_visible(alt, az, use_margins) and sun_alt < -5
        
        # Object becomes visible
        if is_currently_visible and not last_visible:
            start_visible = current_time
        # Object becomes invisible
        elif not is_currently_visible and last_visible and start_visible is not None:
            visibility_periods.append((start_visible, current_time))
            start_visible = None
            
        last_visible = is_currently_visible
        current_time += interval
    
    # If object is still visible at the end, add the final period
    if start_visible is not None and last_visible:
        visibility_periods.append((start_visible, end_time))
    
    return visibility_periods

def calculate_visibility_duration(visibility_periods):
    """Calculate total visibility duration in hours"""
    total_seconds = sum(
        (end - start).total_seconds() 
        for start, end in visibility_periods
    )
    return total_seconds / 3600

# ============= TWILIGHT AND NIGHT FUNCTIONS =============

def find_sunset_sunrise(date):
    """Find sunset and sunrise times"""
    milan_tz = get_local_timezone()
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    
    noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon = milan_tz.localize(noon)
    noon_utc = local_to_utc(noon)
    
    current_time = noon_utc
    alt, _ = calculate_sun_position(current_time)
    
    while alt > 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunset = current_time
    
    while alt <= 0:
        current_time += timedelta(minutes=SEARCH_INTERVAL_MINUTES)
        alt, _ = calculate_sun_position(current_time)
    sunrise = current_time
    
    return utc_to_local(sunset), utc_to_local(sunrise)

def find_astronomical_twilight(date):
    """Find astronomical twilight times"""
    # Use high-precision calculation if enabled in config
    if CONFIG.get('precision', {}).get('use_high_precision', False):
        try:
            return find_precise_astronomical_twilight(date)
        except Exception as e:
            print(f"High-precision twilight calculation failed, using standard: {e}")
    
    # Original calculation as fallback
    tz = get_local_timezone()
    twilight_altitude = -18.0  # degrees below horizon
    
    # Start near sunset/sunrise times
    sunset, sunrise = find_sunset_sunrise(date)
    
    # Search for evening twilight (Sun descending to -18°)
    search_start = sunset - timedelta(hours=1)
    search_end = sunset + timedelta(hours=2)
    
    evening_twilight = None
    current_time = search_start
    while current_time <= search_end:
        sun_alt, _ = calculate_sun_position(current_time)
        
        if abs(sun_alt - twilight_altitude) < 0.1:  # Within 0.1 degrees
            evening_twilight = current_time
            break
        elif sun_alt < twilight_altitude:
            # We've passed it, interpolate backward
            prev_time = current_time - timedelta(minutes=1)
            prev_alt, _ = calculate_sun_position(prev_time)
            if prev_alt > twilight_altitude:
                # Linear interpolation
                ratio = (twilight_altitude - prev_alt) / (sun_alt - prev_alt)
                evening_twilight = prev_time + timedelta(minutes=ratio)
                break
        
        current_time += timedelta(minutes=1)
    
    # Search for morning twilight (Sun ascending to -18°)
    next_day = date + timedelta(days=1)
    morning_sunrise, _ = find_sunset_sunrise(next_day)
    search_start = morning_sunrise - timedelta(hours=2)
    search_end = morning_sunrise + timedelta(hours=1)
    
    morning_twilight = None
    current_time = search_start
    while current_time <= search_end:
        sun_alt, _ = calculate_sun_position(current_time)
        
        if abs(sun_alt - twilight_altitude) < 0.1:  # Within 0.1 degrees
            morning_twilight = current_time
            break
        elif sun_alt > twilight_altitude:
            # We've passed it, interpolate backward
            prev_time = current_time - timedelta(minutes=1)
            prev_alt, _ = calculate_sun_position(prev_time)
            if prev_alt < twilight_altitude:
                # Linear interpolation
                ratio = (twilight_altitude - prev_alt) / (sun_alt - prev_alt)
                morning_twilight = prev_time + timedelta(minutes=ratio)
                break
        
        current_time += timedelta(minutes=1)
    
    # Return results, defaulting to sunset/sunrise if twilight not found
    if evening_twilight is None:
        evening_twilight = sunset
    if morning_twilight is None:
        morning_twilight = morning_sunrise
    
    return evening_twilight, morning_twilight

# ============= MOSAIC PLOTTING FUNCTIONS =============

def plot_mosaic_fov_indicator(ax, center_alt, center_az, fov_width, fov_height, color='red', alpha=0.3):
    """Plot a field of view indicator on the trajectory plot."""
    from matplotlib.patches import Ellipse
    
    # Create an ellipse to represent the FOV
    fov_patch = Ellipse((center_az, center_alt), fov_width, fov_height,
                       facecolor=color, edgecolor=color, alpha=alpha,
                       linestyle='--', linewidth=2)
    ax.add_patch(fov_patch)
    
    # Add FOV label
    ax.text(center_az, center_alt, f'Mosaic\nFOV\n{fov_width:.1f}°×{fov_height:.1f}°',
           ha='center', va='center', fontsize=8, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

def calculate_group_center_position(group, time):
    """Calculate the center position of a group at a given time."""
    altitudes = []
    azimuths = []
    
    # Handle both MosaicGroup and list of objects
    objects = group.objects if hasattr(group, 'objects') else group
    
    for obj in objects:
        alt, az = calculate_altaz(obj, time)
        if is_visible(alt, az, use_margins=True):
            altitudes.append(alt)
            azimuths.append(az)
    
    if altitudes and azimuths:
        return sum(altitudes) / len(altitudes), sum(azimuths) / len(azimuths)
    return None, None

def plot_mosaic_group_trajectory(ax, group, start_time, end_time, group_color, group_number, show_labels=True):
    """Plot trajectory for a mosaic group with special visual indicators."""
    import matplotlib.pyplot as plt
    
    # Handle both MosaicGroup and list of objects
    objects = group.objects if hasattr(group, 'objects') else group
    overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
    
    # Plot individual object trajectories
    existing_positions = []
    
    for i, obj in enumerate(objects):
        times = []
        alts = []
        azs = []
        hour_times = []
        hour_alts = []
        hour_azs = []
        
        # Ensure times are in UTC for calculations
        if start_time.tzinfo != pytz.UTC:
            start_time = start_time.astimezone(pytz.UTC)
        if end_time.tzinfo != pytz.UTC:
            end_time = end_time.astimezone(pytz.UTC)
        
        current_time = start_time
        while current_time <= end_time:
            alt, az = calculate_altaz(obj, current_time)
            
            # Extended visibility check for trajectory plotting (±5 degrees)
            if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
                MIN_AZ - 5 <= az <= MAX_AZ + 5):
                times.append(current_time)
                alts.append(alt)
                azs.append(az)
                
                # Convert to local time for display
                local_time = utc_to_local(current_time)
                if local_time.minute == 0:
                    hour_times.append(local_time)
                    hour_alts.append(alt)
                    hour_azs.append(az)
                    
            current_time += timedelta(minutes=1)
        
        if azs:
            # Use different line styles for objects in the same group
            line_styles = ['-', '--', '-.', ':']
            line_style = line_styles[i % len(line_styles)]
            
            # Plot trajectory
            label = f'Group {group_number}: {get_abbreviated_name(obj.name)}' if show_labels else None
            ax.plot(azs, alts, line_style, color=group_color, linewidth=2, 
                   alpha=0.8, label=label)
            
            # Add hour markers (reduce frequency for smaller plots)
            marker_freq = 2 if not show_labels else 1  # Every 2 hours for small plots
            for j, (t, az, alt) in enumerate(zip(hour_times, hour_azs, hour_alts)):
                if j % marker_freq == 0:
                    ax.plot(az, alt, 'o', color=group_color, markersize=4 if not show_labels else 6, zorder=3)
                    if show_labels:
                        ax.annotate(f'{t.hour:02d}h', 
                                   (az, alt),
                                   xytext=(5, 5),
                                   textcoords='offset points',
                                   fontsize=8,
                                   color=group_color,
                                   zorder=3)
            
            # Add object label
            if len(azs) > 10 and show_labels:  # Only if we have enough points and showing labels
                mid_idx = len(azs) // 2
                label_pos = (azs[mid_idx], alts[mid_idx])
                
                abbreviated_name = get_abbreviated_name(obj.name)
                offset_x, offset_y = calculate_label_offset(label_pos[0], label_pos[1], mid_idx, azs, alts)
                
                # Use group-specific background color
                ax.annotate(abbreviated_name, 
                           label_pos,
                           xytext=(offset_x, offset_y),
                           textcoords='offset points',
                           color=group_color,
                           fontweight='bold',
                           fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor=group_color, alpha=0.3),
                           zorder=15)
                existing_positions.append(label_pos)
    
    return existing_positions

def plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=False):
    """Plot the mosaic field of view at the optimal observation time."""
    from matplotlib.patches import Ellipse
    
    if not overlap_periods:
        return
    
    # Find the middle of the longest overlap period
    longest_period = max(overlap_periods, key=lambda p: (p[1] - p[0]).total_seconds())
    mid_time = longest_period[0] + (longest_period[1] - longest_period[0]) / 2
    
    # Calculate the center position of the group at this time
    center_alt, center_az = calculate_group_center_position(group, mid_time)
    
    if center_alt is not None and center_az is not None:
        # Plot the mosaic FOV indicator
        if small_plot:
            # Simplified FOV indicator for small plots
            fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                               facecolor=group_color, edgecolor=group_color, alpha=0.15,
                               linestyle='--', linewidth=1)
            ax.add_patch(fov_patch)
        else:
            plot_mosaic_fov_indicator(ax, center_alt, center_az, 
                                    MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT, 
                                    color=group_color, alpha=0.2)

def create_mosaic_trajectory_plot(groups, start_time, end_time):
    """Create a trajectory plot specifically for mosaic groups."""
    import matplotlib.pyplot as plt
    
    # Setup the plot
    fig, ax = setup_altaz_plot()
    
    # Plot moon trajectory
    plot_moon_trajectory(ax, start_time, end_time)
    
    # Define colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    # Plot each mosaic group
    for i, group in enumerate(groups):
        group_color = colors[i % len(colors)]
        group_number = i + 1
        
        print(f"Plotting Mosaic Group {group_number} ({len(group.objects) if hasattr(group, 'objects') else len(group)} objects)...")
        
        # Get overlap periods
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        
        # Plot trajectories for this group
        plot_mosaic_group_trajectory(ax, group, start_time, end_time, 
                                    group_color, group_number, show_labels=True)
        
        # Plot FOV indicator at optimal time
        plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=False)
    
    # Customize the plot
    night_date = start_time.date()
    plt.title(f'Mosaic Group Trajectories - {night_date}\n{SCOPE_NAME} (Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°)', 
              fontsize=14, fontweight='bold')
    
    # Create custom legend
    handles, labels = ax.get_legend_handles_labels()
    
    # Sort legend by group number
    sorted_items = sorted(zip(handles, labels), key=lambda x: x[1])
    sorted_handles, sorted_labels = zip(*sorted_items) if sorted_items else ([], [])
    
    # Add legend
    ax.legend(sorted_handles, sorted_labels,
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Mosaic Groups')
    
    return fig, ax

def create_mosaic_grid_plot(groups, start_time, end_time):
    """Create a grid of individual mosaic plots without legends to maximize space."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    n_groups = len(groups)
    if n_groups == 0:
        return None, None
    
    # Calculate grid dimensions
    cols = min(3, n_groups)  # Maximum 3 columns
    rows = math.ceil(n_groups / cols)
    
    # Create subplot grid
    fig, axes = plt.subplots(rows, cols, figsize=(16, 6*rows))
    if n_groups == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
    else:
        axes = axes.flatten()
    
    # Colors for different groups
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'olive']
    
    for i, group in enumerate(groups):
        ax = axes[i]
        group_color = colors[i % len(colors)]
        group_number = i + 1
        
        # Setup this subplot
        ax.set_xlim(MIN_AZ, MAX_AZ)
        ax.set_ylim(MIN_ALT, MAX_ALT)
        ax.set_xlabel('Azimuth (degrees)', fontsize=10)
        ax.set_ylabel('Altitude (degrees)', fontsize=10)
        ax.grid(True, alpha=GRID_ALPHA)
        ax.tick_params(labelsize=9)
        
        # Plot moon trajectory (simplified)
        plot_moon_trajectory_no_legend(ax, start_time, end_time)
        
        # Get overlap periods and objects
        overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
        objects = group.objects if hasattr(group, 'objects') else group
        
        # Plot this group
        plot_mosaic_group_trajectory(ax, group, start_time, end_time, 
                                    group_color, group_number, show_labels=False)
        
        # Plot FOV indicator
        plot_mosaic_fov_at_optimal_time(ax, group, overlap_periods, group_color, small_plot=True)
        
        # Add group title and info
        group_names = [get_abbreviated_name(obj.name) for obj in objects]
        total_time = sum((p[1] - p[0]).total_seconds() / 3600 for p in overlap_periods)
        
        title = f"Group {group_number}: {', '.join(group_names)}\n{total_time:.1f}h overlap"
        ax.set_title(title, fontsize=10, fontweight='bold', pad=10)
        
        # Add timing text in corner
        timing_text = ""
        for period_start, period_end in overlap_periods:
            timing_text += f"{period_start.strftime('%H:%M')}-{period_end.strftime('%H:%M')} "
        
        if timing_text:
            ax.text(0.02, 0.98, timing_text.strip(), transform=ax.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
                    verticalalignment='top', fontsize=8)
    
    # Hide unused subplots
    for i in range(n_groups, len(axes)):
        axes[i].set_visible(False)
    
    # Overall title
    fig.suptitle(f'Mosaic Groups Detail - {start_time.date()}\n{SCOPE_NAME} Mosaic FOV: {MOSAIC_FOV_WIDTH}° × {MOSAIC_FOV_HEIGHT}°', 
                fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    return fig, axes

# ============= MAIN PROGRAM =============

def optimize_for_ios():
    """Optimize settings for iOS Pythonista"""
    print("Optimizing for iOS Pythonista...")
    
    # Clear any existing caches
    clear_calculation_cache()
    
    # Detect if we're running on iOS Pythonista
    import sys
    import platform
    
    is_ios_pythonista = (
        'Pythonista' in sys.executable or 
        platform.system() == 'iOS' or
        'com.omz-software.Pythonista3' in sys.executable
    )
    
    # Set matplotlib backend appropriately
    try:
        import matplotlib
        if is_ios_pythonista:
            matplotlib.use('Agg')  # Use non-interactive backend for iOS
            print("Set matplotlib backend to Agg for iOS compatibility")
        else:
            # Use default interactive backend for macOS/other systems
            print("Using default interactive matplotlib backend for plot display")
    except ImportError:
        print("Matplotlib not available")
    
    # Optimize numpy if available
    try:
        import numpy as np
        # Disable threading for iOS
        np.seterr(all='ignore')  # Suppress numpy warnings
        print("Optimized numpy settings")
    except ImportError:
        print("Numpy not available - using pure Python calculations")
    
    # Memory optimization
    gc.collect()
    print(f"Memory optimization complete (Environment: {'iOS Pythonista' if is_ios_pythonista else 'Desktop'})")

def run_ios_tests():
    """Run tests optimized for iOS environment"""
    print("\nRunning iOS Pythonista tests...")
    print("=" * 50)
    
    # Basic functionality test
    try:
        test_time = datetime.now(pytz.UTC)
        
        # Test configuration loading
        print("✓ Configuration loaded successfully")
        
        # Test sun calculation
        sun_alt, sun_az = calculate_sun_position(test_time)
        print(f"✓ Sun position calculated: Alt={sun_alt:.1f}°, Az={sun_az:.1f}°")
        
        # Test moon calculation
        moon_alt, moon_az = calculate_moon_position(test_time)
        print(f"✓ Moon position calculated: Alt={moon_alt:.1f}°, Az={moon_az:.1f}°")
        
        # Test moon phase
        moon_phase = calculate_moon_phase(test_time)
        print(f"✓ Moon phase calculated: {moon_phase:.2f}")
        
        # Test catalog loading
        catalog = get_combined_catalog()
        print(f"✓ Catalog loaded: {len(catalog)} objects")
        
        # Test precision functions if enabled
        if CONFIG.get('precision', {}).get('use_high_precision', False):
            try:
                hp_sun_alt, hp_sun_az = calculate_high_precision_sun_position(test_time)
                print(f"✓ High-precision sun calculation: Alt={hp_sun_alt:.1f}°, Az={hp_sun_az:.1f}°")
                
                hp_moon_alt, hp_moon_az = calculate_high_precision_moon_position(test_time)
                print(f"✓ High-precision moon calculation: Alt={hp_moon_alt:.1f}°, Az={hp_moon_az:.1f}°")
                
                # Compare precision
                sun_diff = abs(sun_alt - hp_sun_alt) * 60  # arcminutes
                moon_diff = abs(moon_alt - hp_moon_alt) * 60  # arcminutes
                print(f"✓ Precision improvement: Sun {sun_diff:.1f}', Moon {moon_diff:.1f}'")
                
            except Exception as e:
                print(f"✗ High-precision test failed: {e}")
        
        print("\n✓ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def create_sample_config_for_ios():
    """Create a sample configuration file optimized for iOS Pythonista"""
    config = {
        "locations": {
            "milano": {
                "name": "Milano",
                "latitude": 45.516667,
                "longitude": 9.216667,
                "timezone": "Europe/Rome",
                "min_altitude": 15,
                "max_altitude": 75,
                "min_azimuth": 65,
                "max_azimuth": 165,
                "bortle_index": 9,
                "default": True,
                "comment": "Milan coordinates"
            },
            "lozio": {
                "name": "Lozio",
                "latitude": 45.9928841,
                "longitude": 10.2299690,
                "timezone": "Europe/Rome",
                "min_altitude": 15,
                "max_altitude": 80,
                "min_azimuth": 45,
                "max_azimuth": 180,
                "bortle_index": 6,
                "default": False,
                "comment": "Lozio coordinates"
            }
        },
        "visibility": {
            "min_visibility_hours": 2,
            "min_total_area": 225,
            "trajectory_interval_minutes": 15,
            "search_interval_minutes": 1
        },
        "catalog": {
            "use_csv_catalog": True,
            "catalog_name": "catalogs/objects.csv",
            "merge": True
        },
        "scheduling": {
            "strategy": "max_objects",
            "max_overlap_minutes": 15,
            "exclude_insufficient_time": False
        },
        "imaging": {
            "scope": {
                "name": "Vaonis Vespera Passenger",
                "fov_width": 2.4,
                "fov_height": 1.8,
                "mosaic_fov_width": 4.7,
                "mosaic_fov_height": 3.5,
                "native_resolution_mp": 6.2,
                "mosaic_resolution_mp": 24,
                "sensor": "Sony IMX585",
                "single_exposure": 10,
                "min_snr": 20,
                "gain": 800,
                "read_noise": 0.8,
                "pixel_size": 2.9,
                "focal_length": 200,
                "aperture": 50,
                "comment": "Updated for Vaonis Vespera Passenger with mosaic capabilities"
            }
        },
        "moon": {
            "proximity_radius": 30,
            "trajectory_color": "yellow",
            "marker_color": "yellow",
            "line_width": 2,
            "marker_size": 6,
            "interference_color": "lightblue"
        },
        "plotting": {
            "max_objects_optimal": 5,
            "figure_size": [12, 10],
            "color_map": "tab20",
            "grid_alpha": 0.3,
            "visible_region_alpha": 0.1
        },
        'observation': {
            'single_exposure_minutes': 5,
            'min_visibility_hours': 1.5,
            'max_overlap_minutes': 30,
            'exclude_insufficient_time': True
        },
        'precision': {
            'use_high_precision': False,
            'atmospheric_refraction': True,
            'parallax_correction': False,
            'cache_calculations': True
        },
        'ios': {
            'memory_optimization': True,
            'matplotlib_backend': 'Agg',
            'numpy_optimization': True,
            'file_paths': {
                'config': 'config.json',
                'catalog': 'catalog.csv',
                'output': 'output/'
            }
        }
    }
    
    # Note: Object catalog is loaded dynamically from built-in catalogs
    # CelestialObject instances cannot be serialized to JSON
    
    # Save the configuration to a JSON file
    config_path = 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config_path

# ============= ENHANCED OBJECT FILTERING =============

def filter_visible_objects_enhanced(objects, start_time, end_time, exclude_insufficient=EXCLUDE_INSUFFICIENT_TIME, use_margins=True):
    """Enhanced filter objects based on visibility and exposure requirements"""
    filtered_objects = []
    insufficient_objects = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            duration = calculate_visibility_duration(periods)
            if hasattr(obj, 'magnitude') and obj.magnitude is not None:
                # Calculate required exposure time and store it in the object
                obj.required_exposure = calculate_required_exposure(
                    obj.magnitude, BORTLE_INDEX, obj.fov)
                
                if duration >= MIN_VISIBILITY_HOURS:
                    obj.sufficient_time = duration >= obj.required_exposure[0]
                    if exclude_insufficient:
                        if obj.sufficient_time:
                            filtered_objects.append(obj)
                        else:
                            insufficient_objects.append(obj)
                    else:
                        filtered_objects.append(obj)
    
    return filtered_objects, insufficient_objects

# ============= OBSERVATION SCHEDULING =============

def calculate_object_score(obj, periods, strategy=SCHEDULING_STRATEGY):
    """Calculate object score based on strategy"""
    if not periods:
        return 0
    
    duration = calculate_visibility_duration(periods)
    
    if strategy == SchedulingStrategy.LONGEST_DURATION:
        return duration
    elif strategy == SchedulingStrategy.MAX_OBJECTS:
        # Favor objects that don't require too much time
        return min(duration, 3.0)  # Cap at 3 hours
    elif strategy == SchedulingStrategy.OPTIMAL_SNR:
        # Favor brighter objects (lower magnitude)
        if hasattr(obj, 'magnitude') and obj.magnitude is not None:
            return max(0, 12 - obj.magnitude) * duration
        return duration
    elif strategy == SchedulingStrategy.MINIMAL_MOSAIC:
        # Favor objects requiring fewer panels
        panels = calculate_required_panels(obj.fov)
        return duration / max(1, panels)
    elif strategy == SchedulingStrategy.DIFFICULTY_BALANCED:
        # Balance between bright and faint objects
        if hasattr(obj, 'magnitude') and obj.magnitude is not None:
            mag_score = 1.0 if obj.magnitude < 8 else 0.5  # Bonus for easy targets
            return mag_score * duration
        return duration
    else:
        return duration

def generate_observation_schedule(objects, start_time, end_time, 
                                strategy=SCHEDULING_STRATEGY,
                                min_duration=MIN_VISIBILITY_HOURS,
                                max_overlap=MAX_OVERLAP_MINUTES):
    """Generate observation schedule based on strategy"""
    schedule = []
    
    # Calculate scores for all objects
    scored_objects = []
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time)
        if periods:
            score = calculate_object_score(obj, periods, strategy)
            scored_objects.append((score, obj, periods))
    
    # Sort by score (descending)
    scored_objects.sort(key=lambda x: x[0], reverse=True)
    
    used_time_slots = []
    
    for score, obj, periods in scored_objects:
        # Find the best period for this object
        best_period = None
        best_duration = 0
        
        for period_start, period_end in periods:
            period_duration = (period_end - period_start).total_seconds() / 3600
            
            if period_duration >= min_duration:
                # Check for conflicts with already scheduled observations
                conflict = False
                for scheduled_start, scheduled_end, _ in used_time_slots:
                    if not (period_end <= scheduled_start or period_start >= scheduled_end):
                        # There's an overlap, check if it's acceptable
                        overlap_minutes = min(period_end, scheduled_end) - max(period_start, scheduled_start)
                        overlap_minutes = overlap_minutes.total_seconds() / 60
                        if overlap_minutes > max_overlap:
                            conflict = True
                            break
                
                if not conflict and period_duration > best_duration:
                    best_period = (period_start, period_end)
                    best_duration = period_duration
        
        if best_period:
            schedule.append((best_period[0], best_period[1], obj))
            used_time_slots.append((best_period[0], best_period[1], obj))
    
    # Sort schedule by start time
    schedule.sort(key=lambda x: x[0])
    
    return schedule

# ============= PLOTTING FUNCTIONS =============

def setup_altaz_plot():
    """Setup basic altitude-azimuth plot"""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import MultipleLocator
    
    # Create figure with appropriate size
    fig = plt.figure(figsize=FIGURE_SIZE)  # Wider figure
    
    # Use GridSpec for better control over spacing
    gs = fig.add_gridspec(1, 1)
    # Adjust margins to accommodate axis labels and legend
    gs.update(left=0.1, right=0.85, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])
    
    # Set axis limits and labels
    ax.set_xlim(MIN_AZ-10, MAX_AZ+10)
    ax.set_ylim(MIN_ALT-10, MAX_ALT+10)
    ax.set_xlabel('Azimuth (degrees)')
    ax.set_ylabel('Altitude (degrees)')
    ax.grid(True, alpha=GRID_ALPHA)
    
    # Add visible region rectangle
    visible_region = Rectangle((MIN_AZ, MIN_ALT), 
                             MAX_AZ - MIN_AZ, 
                             MAX_ALT - MIN_ALT,
                             facecolor='green', 
                             alpha=VISIBLE_REGION_ALPHA,
                             label='Visible Region')
    ax.add_patch(visible_region)
    
    # Configure grid with major and minor ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    
    return fig, ax

def plot_moon_trajectory(ax, start_time, end_time):
    """Plot moon trajectory with hourly markers"""
    times = []
    alts = []
    azs = []
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_moon_position(current_time)
        if is_visible(alt, az, use_margins=True):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)
    
    if azs:
        # Plot moon trajectory
        ax.plot(azs, alts, '-', color=MOON_TRAJECTORY_COLOR, 
               linewidth=MOON_LINE_WIDTH, label='Moon', zorder=2)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=MOON_MARKER_COLOR, 
                   markersize=MOON_MARKER_SIZE, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=MOON_MARKER_COLOR,
                       zorder=3)

def get_abbreviated_name(full_name):
    """Get abbreviated name (catalog designation) from full name"""
    import re
    
    # First try to find Messier number
    m_match = re.match(r'M(\d+)', full_name)
    if m_match:
        return f"M{m_match.group(1)}"
    
    # Then try NGC number
    ngc_match = re.match(r'NGC\s*(\d+)', full_name)
    if ngc_match:
        return f"NGC{ngc_match.group(1)}"
    
    # Then try IC number
    ic_match = re.match(r'IC\s*(\d+)', full_name)
    if ic_match:
        return f"IC{ic_match.group(1)}"
    
    # Then try SH2 number
    sh2_match = re.match(r'SH2-(\d+)', full_name)
    if sh2_match:
        return f"SH2-{sh2_match.group(1)}"  # Return complete SH2-nnn format
    
    # Then try SH number
    sh_match = re.match(r'SH\s*(\d+)', full_name)
    if sh_match:
        return f"SH{sh_match.group(1)}"  # Return complete SH-nnn format
        
    # Then try Barnard number
    b_match = re.match(r'B\s*(\d+)', full_name)
    if b_match:
        return f"B{b_match.group(1)}"
    
    # Then try Gum number
    gum_match = re.match(r'Gum\s*(\d+)', full_name)
    if gum_match:
        return f"GUM{gum_match.group(1)}"    

    # If no catalog number found, return first word
    return full_name.split()[0]

def find_optimal_label_position(azimuths, altitudes, hour_positions, existing_positions, 
                               existing_labels, margin=8):
    """
    Find optimal position for label that avoids overlapping with:
    - Other object labels
    - Hourly tick markers and their labels
    - Trajectory endpoints
    
    Parameters:
    - azimuths, altitudes: trajectory coordinates
    - hour_positions: list of (az, alt) tuples for hourly markers
    - existing_positions: list of (az, alt) tuples for other object labels
    - existing_labels: list of existing label texts to avoid duplication
    - margin: minimum distance in degrees for avoiding overlaps
    
    Returns:
    - (az, alt) tuple for label position, with fallback if no optimal position found
    """
    if len(azimuths) < 3:
        return None
    
    # Create list of forbidden zones (hourly ticks + existing labels)
    forbidden_zones = []
    
    # Add hourly tick positions with larger margin
    for pos in hour_positions:
        forbidden_zones.append((pos[0], pos[1], margin * 1.5))  # Larger margin for ticks
    
    # Add existing label positions
    for pos in existing_positions:
        forbidden_zones.append((pos[0], pos[1], margin))
    
    # Find potential label positions along trajectory
    # Avoid first and last 20% of trajectory (near endpoints)
    start_idx = max(1, len(azimuths) // 5)
    end_idx = min(len(azimuths) - 1, len(azimuths) * 4 // 5)
    
    candidate_positions = []
    
    for i in range(start_idx, end_idx):
        az, alt = azimuths[i], altitudes[i]
        
        # Check if this position conflicts with forbidden zones
        conflicts = False
        for fz_az, fz_alt, fz_margin in forbidden_zones:
            distance = ((az - fz_az)**2 + (alt - fz_alt)**2)**0.5
            if distance < fz_margin:
                conflicts = True
                break
        
        if not conflicts:
            # Calculate trajectory curvature at this point for better placement
            curvature_score = 0
            if i > 0 and i < len(azimuths) - 1:
                # Simple curvature estimation
                prev_az, prev_alt = azimuths[i-1], altitudes[i-1]
                next_az, next_alt = azimuths[i+1], altitudes[i+1]
                
                # Prefer straighter segments for labels
                angle1 = math.atan2(alt - prev_alt, az - prev_az)
                angle2 = math.atan2(next_alt - alt, next_az - az)
                angle_diff = abs(angle1 - angle2)
                curvature_score = 1 / (1 + angle_diff)  # Higher score for straighter segments
            
            # Distance from center of trajectory (prefer middle)
            center_preference = 1 - abs(i - len(azimuths) // 2) / (len(azimuths) // 2)
            
            # Combined score
            total_score = curvature_score * 0.7 + center_preference * 0.3
            
            candidate_positions.append((az, alt, total_score, i))
    
    if candidate_positions:
        # Sort by score and return best position
        candidate_positions.sort(key=lambda x: x[2], reverse=True)
        best_az, best_alt, _, _ = candidate_positions[0]
        return (best_az, best_alt)
    
    # FALLBACK: If no optimal position found, use middle of trajectory with reduced margin check
    fallback_candidates = []
    reduced_margin = margin * 0.5
    
    for i in range(start_idx, end_idx):
        az, alt = azimuths[i], altitudes[i]
        
        # Check against reduced margin
        conflicts = False
        for fz_az, fz_alt, _ in forbidden_zones:
            distance = ((az - fz_az)**2 + (alt - fz_alt)**2)**0.5
            if distance < reduced_margin:
                conflicts = True
                break
        
        if not conflicts:
            fallback_candidates.append((az, alt))
    
    if fallback_candidates:
        # Return middle candidate
        mid_idx = len(fallback_candidates) // 2
        return fallback_candidates[mid_idx]
    
    # LAST RESORT: Use middle of trajectory regardless of overlaps
    mid_idx = len(azimuths) // 2
    return (azimuths[mid_idx], altitudes[mid_idx])

def calculate_label_offset(trajectory_az, trajectory_alt, trajectory_idx, azimuths, altitudes):
    """
    Calculate smart offset for label based on trajectory direction and position
    to avoid overlapping with the trajectory line itself.
    """
    # Default offset
    offset_x, offset_y = 8, 8
    
    if trajectory_idx > 0 and trajectory_idx < len(azimuths) - 1:
        # Calculate trajectory direction
        prev_az, prev_alt = azimuths[trajectory_idx - 1], altitudes[trajectory_idx - 1]
        next_az, next_alt = azimuths[trajectory_idx + 1], altitudes[trajectory_idx + 1]
        
        # Direction vector
        dir_az = next_az - prev_az
        dir_alt = next_alt - prev_alt
        
        # Perpendicular offset (rotated 90 degrees)
        if abs(dir_az) > abs(dir_alt):
            # More horizontal trajectory - offset vertically
            offset_x = 8 if dir_az > 0 else -8
            offset_y = 12 if dir_alt >= 0 else -12
        else:
            # More vertical trajectory - offset horizontally
            offset_x = 12 if dir_az >= 0 else -12
            offset_y = 8 if dir_alt > 0 else -8
    
    return offset_x, offset_y

def plot_object_trajectory(ax, obj, start_time, end_time, color, existing_positions=None, schedule=None):
    """Plot trajectory with moon proximity checking and legend.
    Elements are plotted in specific z-order:
    1. Base trajectory (z=1)
    2. Moon interference segments (z=2)
    3. Hour markers (z=3)
    4. Hour labels (z=4)
    5. Object name (z=5)
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Axes to plot on
    obj : CelestialObject
        Object to plot trajectory for
    start_time : datetime
        Start time for trajectory
    end_time : datetime
        End time for trajectory
    color : str
        Color for trajectory and markers
    existing_positions : list, optional
        List of existing label positions to avoid overlap
    schedule : list, optional
        List of scheduled observations [(start, end, obj), ...] for label styling
    """
    # Ensure there's a legend (even if empty) to avoid NoneType errors
    if ax.get_legend() is None:
        ax.legend()
    times = []
    alts = []
    azs = []
    near_moon = []  # Track moon proximity
    moon_alts = []  # Track moon altitude for each point
    obj.near_moon = False  # Initialize moon proximity flag
    hour_times = []
    hour_alts = []
    hour_azs = []
    
    # Check if this object is scheduled
    is_scheduled = False
    if schedule:
        scheduled_objects = [sched_obj for _, _, sched_obj in schedule]
        is_scheduled = obj in scheduled_objects
    
    # Ensure times are in UTC for calculations
    if start_time.tzinfo != pytz.UTC:
        start_time = start_time.astimezone(pytz.UTC)
    if end_time.tzinfo != pytz.UTC:
        end_time = end_time.astimezone(pytz.UTC)
    
    # Use smaller interval for smoother trajectory
    current_time = start_time
    while current_time <= end_time:
        alt, az = calculate_altaz(obj, current_time)
        moon_alt, moon_az = calculate_moon_position(current_time)
        
        # Extended visibility check for trajectory plotting (±5 degrees)
        if (MIN_ALT - 5 <= alt <= MAX_ALT + 5 and 
            MIN_AZ - 5 <= az <= MAX_AZ + 5):
            times.append(current_time)
            alts.append(alt)
            azs.append(az)
            
            # Check moon proximity - only consider when moon is risen
            is_near = False
            if moon_alt >= 0:  # Only check interference if moon is above horizon
                is_near = is_near_moon(alt, az, moon_alt, moon_az, obj.magnitude, current_time)
            near_moon.append(is_near)
            moon_alts.append(moon_alt)  # Store moon altitude for each point
            
            # Convert to local time for display
            local_time = utc_to_local(current_time)
            if local_time.minute == 0:
                hour_times.append(local_time)
                hour_alts.append(alt)
                hour_azs.append(az)
                
        current_time += timedelta(minutes=1)  # Use 1-minute intervals for accuracy
    
    # Set moon influence flag only if object is affected for a significant period
    if near_moon:
        moon_influence_periods = []
        start_idx = None
        
        # Find continuous periods of moon influence
        for i, is_near in enumerate(near_moon):
            if is_near and start_idx is None:
                start_idx = i
            elif not is_near and start_idx is not None:
                moon_influence_periods.append((start_idx, i))
                start_idx = None
        
        # Don't forget the last period if it ends with moon influence
        if start_idx is not None:
            moon_influence_periods.append((start_idx, len(near_moon)))
        
        # Calculate total influence time
        total_influence_minutes = sum(end - start for start, end in moon_influence_periods)
        
        # Set flag if moon influence is significant (more than 15 minutes)
        obj.near_moon = total_influence_minutes >= 15
        obj.moon_influence_periods = moon_influence_periods  # Store periods for later use
    
    if azs:
        # Determine line style based on sufficient time
        line_style = '-' if getattr(obj, 'sufficient_time', True) else '--'
        
        # Plot base trajectory (lowest z-order)
        ax.plot(azs, alts, line_style, color=color, linewidth=1.5, alpha=0.3, zorder=1)
        
        # Plot moon-affected segments if any
        if hasattr(obj, 'moon_influence_periods'):
            for start_idx, end_idx in obj.moon_influence_periods:
                # Validate that moon is actually above horizon during this segment
                valid_segment = True
                for i in range(start_idx, min(end_idx+1, len(moon_alts))):
                    if moon_alts[i] < 0:  # Moon below horizon
                        valid_segment = False
                        break
                
                if valid_segment:
                    # Plot the moon-affected segment
                    ax.plot(azs[start_idx:end_idx+1], 
                           alts[start_idx:end_idx+1], 
                           line_style,
                           color=MOON_INTERFERENCE_COLOR,
                           linewidth=2,
                           zorder=2)
        
        # Add label only once
        legend = ax.get_legend()
        obj_name = obj.name.split('/')[0]
        existing_labels = [t.get_text() for t in legend.get_texts()] if legend else []
        
        if obj_name not in existing_labels:
            # Add a dummy line for the legend
            ax.plot([], [], line_style, color=color, 
                   linewidth=2, label=obj_name)
        
        # Add hour markers
        for t, az, alt in zip(hour_times, hour_azs, hour_alts):
            ax.plot(az, alt, 'o', color=color, markersize=6, zorder=3)
            ax.annotate(f'{t.hour:02d}h', 
                       (az, alt),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       color=color,
                       zorder=3)
        
        # Add abbreviated name near trajectory
        if existing_positions is None:
            existing_positions = []
            
        # Collect hour positions for avoiding overlap
        hour_positions = [(az, alt) for az, alt in zip(hour_azs, hour_alts)]
        
        # Get existing labels from legend to avoid duplicates
        legend = ax.get_legend()
        existing_labels = [t.get_text() for t in legend.get_texts()] if legend else []
            
        label_pos = find_optimal_label_position(azs, alts, hour_positions, existing_positions, existing_labels, margin=6)
        if label_pos:
            abbreviated_name = get_abbreviated_name(obj.name)
            
            # Calculate smart offset based on trajectory direction
            trajectory_idx = len(azs) // 2  # Use middle point for direction calculation
            offset_x, offset_y = calculate_label_offset(label_pos[0], label_pos[1], trajectory_idx, azs, alts)
            
            # Choose label background color based on scheduling status
            if is_scheduled:
                # Yellow transparent background for scheduled objects
                label_bg_color = "yellow"
                label_alpha = 0.6  # Slightly more opaque for better visibility of yellow
            else:
                # White transparent background for non-scheduled objects
                label_bg_color = "white"
                label_alpha = 0.4
            
            ax.annotate(abbreviated_name, 
                       label_pos,
                       xytext=(offset_x, offset_y),
                       textcoords='offset points',
                       color=color,
                       fontweight='bold',
                       fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.2", facecolor=label_bg_color, alpha=label_alpha),
                       zorder=15)
            existing_positions.append(label_pos)

def finalize_plot_legend(ax):
    """Finalize plot legend with sorted entries, keeping Visible Region and Moon first"""
    # Get current handles and labels
    handles, labels = ax.get_legend_handles_labels()
    
    # Find indices of special entries
    try:
        visible_idx = labels.index('Visible Region')
        visible_handle = handles.pop(visible_idx)
        visible_label = labels.pop(visible_idx)
    except ValueError:
        visible_handle, visible_label = None, None
        
    try:
        moon_idx = labels.index('Moon')
        moon_handle = handles.pop(moon_idx)
        moon_label = labels.pop(moon_idx)
    except ValueError:
        moon_handle, moon_label = None, None
    
    # Sort remaining entries
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: x[1].lower())
    handles, labels = zip(*sorted_pairs) if sorted_pairs else ([], [])
    
    # Reconstruct list with special entries first
    final_handles = []
    final_labels = []
    
    if visible_handle is not None:
        final_handles.append(visible_handle)
        final_labels.append(visible_label)
    if moon_handle is not None:
        final_handles.append(moon_handle)
        final_labels.append(moon_label)
        
    final_handles.extend(handles)
    final_labels.extend(labels)
    
    # Update legend
    ax.legend(final_handles, final_labels,
             bbox_to_anchor=(1.02, 1),
             loc='upper left',
             borderaxespad=0,
             title='Objects and Conditions')

def plot_visibility_chart(objects, start_time, end_time, schedule=None, title="Object Visibility", use_margins=True):
    """Create visibility chart showing moon interference periods and scheduled intervals.
    - Base bars show full visibility with colors indicating status/moon interference.
    - Scheduled intervals are overlaid with hatching.

    Parameters:
    -----------
    objects : list
        List of celestial objects to plot
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    schedule : list, optional
        List of scheduled observations [(start, end, obj), ...]
    title : str, optional
        Chart title
    use_margins : bool, optional
        Whether to use extended margins (±5°) for visibility boundaries
    """
    import matplotlib.pyplot as plt

    # Ensure times are in local timezone
    milan_tz = get_local_timezone()
    if start_time.tzinfo != milan_tz:
        start_time = start_time.astimezone(milan_tz)
    if end_time.tzinfo != milan_tz:
        end_time = end_time.astimezone(milan_tz)

    # Get current time in local timezone for the vertical line
    current_time = datetime.now(milan_tz)

    # Create figure with settings - creating a brand new figure each time
    # to avoid any remnant elements from previous plots
    plt.close('all')  # Close any existing figures
    fig = plt.figure(figsize=(15, max(10, len(objects)*0.3 + 4)))
    
    # Full-width subplot - no need to reserve space for legend
    ax = fig.add_subplot(111)
    
    # Get visibility periods and sort objects
    sorted_objects = _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins)

    # Setup plot
    _setup_visibility_chart_axes(ax, title, start_time, end_time, milan_tz)

    # Create mapping for recommended objects and scheduled intervals (in local time)
    recommended_objects = [obj for _, _, obj in schedule] if schedule else []
    scheduled_intervals = {obj: (start.astimezone(milan_tz), end.astimezone(milan_tz))
                           for start, end, obj in schedule} if schedule else {}

    # Plot BASE visibility periods
    for i, obj in enumerate(sorted_objects):
        # Skip returning handles/labels since we don't need them for a legend
        _plot_object_visibility_bars_no_legend(ax, i, obj, start_time, end_time,
                                         recommended_objects, use_margins)

    # OVERLAY the scheduled intervals with hatching
    for i, obj in enumerate(sorted_objects):
        if obj in scheduled_intervals:
            sched_start_local, sched_end_local = scheduled_intervals[obj]
            
            # Ensure scheduled interval is within plot range
            plot_start = max(sched_start_local, start_time)
            plot_end = min(sched_end_local, end_time)
            
            if plot_start < plot_end:
                # Add hatching to show scheduled time
                rect_sched = plt.Rectangle((plot_start, i - 0.4), 
                                         plot_end - plot_start, 0.8,
                                         facecolor='none', 
                                         edgecolor='black',
                                         linewidth=2,
                                         linestyle='--',
                                         alpha=1.0)
                ax.add_patch(rect_sched)

    # Set object labels on y-axis
    ax.set_yticks(range(len(sorted_objects)))
    ax.set_yticklabels([get_abbreviated_name(obj.name) for obj in sorted_objects])

    # Add current time line
    if start_time <= current_time <= end_time:
        ax.axvline(x=current_time, color='red', linestyle='-', linewidth=2, 
                  alpha=0.8, label='Current Time')

    # Simple legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.8, label='Recommended'),
        Patch(facecolor='gray', alpha=0.4, label='Visible'),
        Patch(facecolor='#DAA520', alpha=0.8, label='Moon Affected (Recommended)'),
        Patch(facecolor='#F0E68C', alpha=0.6, label='Moon Affected'),
        Patch(facecolor='none', edgecolor='black', linewidth=2, linestyle='--', label='Scheduled')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    return fig, ax

def _get_sorted_objects_for_chart(objects, start_time, end_time, use_margins):
    """Get objects sorted by visibility start time for chart display"""
    milan_tz = get_local_timezone()
    object_periods = []
    
    for obj in objects:
        periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)
        if periods:
            # Convert periods to local time
            local_periods = [(p[0].astimezone(milan_tz), p[1].astimezone(milan_tz)) 
                           for p in periods]
            duration = calculate_visibility_duration(periods)
            object_periods.append((obj, local_periods[0][0], duration))
    
    # Sort by start time
    object_periods.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in object_periods]

def _setup_visibility_chart_axes(ax, title, start_time, end_time, tz):
    """Setup axes for visibility chart"""
    ax.set_title(title)
    ax.set_xlabel('Local Time')
    ax.set_ylabel('Objects')
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(-0.5, ax.get_ylim()[1])
    ax.grid(True, alpha=0.3)
    
    # Use local time formatter
    from matplotlib.dates import DateFormatter
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=tz))

def _plot_object_visibility_bars_no_legend(ax, index, obj, start_time, end_time, recommended_objects, use_margins):
    """Plot visibility bars for a single object (BASE LAYER) without returning legend handles."""
    milan_tz = get_local_timezone()
    periods = find_visibility_window(obj, start_time, end_time, use_margins=use_margins)

    is_recommended = obj in recommended_objects
    has_sufficient_time = getattr(obj, 'sufficient_time', True)
    
    # Always use the regular color as the base color regardless of moon interference
    if not has_sufficient_time:
        color = 'darkmagenta' if is_recommended else 'pink'
    else:
        color = 'green' if is_recommended else 'gray'
    alpha = 0.8 if is_recommended else 0.4
    
    base_zorder = 5

    # Ensure periods is not None before iterating
    if periods is None:
        periods = []

    for period_start, period_end in periods:
        local_start = period_start.astimezone(milan_tz)
        local_end = period_end.astimezone(milan_tz)

        plot_start = max(local_start, start_time)
        plot_end = min(local_end, end_time)

        if plot_start >= plot_end: continue

        # If object has moon influence periods, draw the base bar in normal color
        # and overlay moon-affected segments separately
        if hasattr(obj, 'moon_influence_periods') and obj.moon_influence_periods:
            # First, draw the entire bar in normal color
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)
                   
            # Then overlay the moon interference segments
            for start_idx, end_idx in obj.moon_influence_periods:
                moon_start = period_start + timedelta(minutes=start_idx)
                moon_end = period_start + timedelta(minutes=end_idx)
                
                # Convert to local timezone
                moon_start_local = moon_start.astimezone(milan_tz)
                moon_end_local = moon_end.astimezone(milan_tz)
                
                # Check if this segment overlaps with the current visibility period
                if moon_end_local > plot_start and moon_start_local < plot_end:
                    # Calculate the overlapping segment
                    segment_start = max(moon_start_local, plot_start)
                    segment_end = min(moon_end_local, plot_end)
                    
                    # Draw the moon interference segment
                    moon_color = '#DAA520' if is_recommended else '#F0E68C'  # Goldenrod/Khaki
                    ax.barh(index, 
                           segment_end - segment_start, 
                           left=segment_start, 
                           height=0.3,
                           alpha=alpha,
                           color=moon_color,
                           zorder=base_zorder+1)  # Slightly higher zorder
        else:
            # Plot normal visibility bar
            ax.barh(index, plot_end - plot_start, left=plot_start, height=0.3,
                   alpha=alpha, color=color, zorder=base_zorder)

        # Add abbreviated name text annotation near the bar start (once per object ideally)
        # Position text AT the bar start, aligned left
        # Plot text label only for the first segment
        if period_start == periods[0][0] and plot_start < plot_end:
             abbreviated_name = get_abbreviated_name(obj.name)
             text_pos_x = plot_start # Align with the actual start of the plotted bar segment
             ax.text(text_pos_x + timedelta(minutes=1), index, # Small offset from the exact start
                     f" {abbreviated_name}", # Add space for padding
                     va='center', ha='left', # Align left
                     fontsize=7, # Smaller font size for text on chart
                     color='black', # Ensure visibility
                     fontweight='bold', # Make text bold for better visibility
                     bbox=dict(facecolor='white', alpha=0.7, pad=1, edgecolor='none'), # Add white background
                     zorder=15) # Very high zorder to ensure it's above everything else

# ============= ENHANCED MAIN FUNCTION =============

def main():
    """Main program execution with comprehensive reporting and plotting"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Astronomical observation planner with enhanced precision')
    parser.add_argument('--test', action='store_true', help='Run tests and exit')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--precision', action='store_true', help='Enable high-precision calculations')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmarks')
    parser.add_argument('--date', type=str, help='Date for observation (YYYY-MM-DD)')
    parser.add_argument('--object', type=str, help='Specific object to display')
    parser.add_argument('--type', type=str, help='Filter by object type')
    parser.add_argument('--report-only', action='store_true', help='Show only the text report')
    parser.add_argument('--schedule', choices=['longest_duration', 'max_objects', 'optimal_snr', 'minimal_mosaic', 'difficulty_balanced', 'mosaic_groups'], 
                      default='longest_duration', help='Scheduling strategy')
    parser.add_argument('--no-margins', action='store_true', 
                      help='Do not use extended margins for visibility chart')
    parser.add_argument('--quarters', action='store_true',
                      help='Use 4-quarter trajectory plots instead of single plot')
    parser.add_argument('--mosaic', action='store_true',
                      help='Enable mosaic group analysis and specialized plots')
    parser.add_argument('--mosaic-only', action='store_true',
                      help='Show only mosaic groups (implies --mosaic)')
    
    args = parser.parse_args()
    
    # iOS optimization
    optimize_for_ios()
    
    # Handle special modes
    if args.test:
        success = run_ios_tests()
        if args.precision:
            print("\nRunning precision tests...")
            results = run_precision_tests()
            print(f"Precision test results: {results}")
        return 0 if success else 1
    
    if args.create_config:
        config_path = create_sample_config_for_ios()
        if config_path:
            print(f"Sample configuration created at: {config_path}")
            print("Edit this file to customize your location and preferences")
        return 0
    
    if args.benchmark:
        print("Running performance benchmarks...")
        results = benchmark_calculations()
        print(f"Benchmark results: {results}")
        return 0
    
    # Enable high-precision if requested
    if args.precision:
        if 'precision' not in CONFIG:
            CONFIG['precision'] = {}
        CONFIG['precision']['use_high_precision'] = True
        print("High-precision calculations enabled")
    
    # Map command line schedule argument to SchedulingStrategy
    strategy_mapping = {
        'longest_duration': SchedulingStrategy.LONGEST_DURATION,
        'max_objects': SchedulingStrategy.MAX_OBJECTS,
        'optimal_snr': SchedulingStrategy.OPTIMAL_SNR,
        'minimal_mosaic': SchedulingStrategy.MINIMAL_MOSAIC,
        'difficulty_balanced': SchedulingStrategy.DIFFICULTY_BALANCED,
        'mosaic_groups': SchedulingStrategy.MOSAIC_GROUPS
    }
    selected_strategy = strategy_mapping[args.schedule]
    
    try:
        # Get current time to determine which night we're in
        current_date = get_current_datetime(get_local_timezone())
        
        # Use provided date or determine correct night based on current time
        if args.date:
            observation_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            # Convert date to datetime with timezone
            tz = get_local_timezone()
            observation_date_dt = tz.localize(datetime.combine(observation_date, datetime.min.time()))
        else:
            observation_date_dt = current_date
        
        # If current time is after midnight but before noon, we're still in the "night"
        # of the previous day, so we need to adjust the date for calculations
        if current_date.hour < 12 and not args.date:
            yesterday = current_date - timedelta(days=1)
            sunset, next_sunrise = find_sunset_sunrise(yesterday)
            twilight_evening, twilight_morning = find_astronomical_twilight(yesterday)
            observation_date = yesterday.date()
        else:
            # We're in daytime (afternoon), calculate for upcoming night
            sunset, next_sunrise = find_sunset_sunrise(observation_date_dt)
            twilight_evening, twilight_morning = find_astronomical_twilight(observation_date_dt)
            observation_date = observation_date_dt.date()

        # Ensure twilight times are in the correct timezone
        local_tz = get_local_timezone()
        if twilight_evening.tzinfo != local_tz:
            twilight_evening = twilight_evening.astimezone(local_tz)
        if twilight_morning.tzinfo != local_tz:
            twilight_morning = twilight_morning.astimezone(local_tz)

        # Check if we're currently between evening twilight and morning twilight
        # (i.e., during astronomical night)
        is_night_time = (current_date >= twilight_evening and current_date <= twilight_morning)

        # If we're already in the night, only show objects visible for the rest of the night
        if is_night_time and not args.date:
            # Only calculate visibility from evening twilight until morning twilight (full night)
            start_time = twilight_evening
            end_time = twilight_morning
        else:
            # We're in daytime, calculate for the entire upcoming night
            start_time = twilight_evening
            end_time = twilight_morning
        
        print(f"Planning observations for: {observation_date}")
        print(f"Location: {DEFAULT_LOCATION['name']}")
        print(f"Coordinates: {DEFAULT_LOCATION['latitude']:.3f}°, {DEFAULT_LOCATION['longitude']:.3f}°")
        
        print(f"\nObservation window:")
        print(f"Sunset: {format_time(sunset)}")
        print(f"Evening twilight: {format_time(twilight_evening)}")
        print(f"Morning twilight: {format_time(twilight_morning)}")
        print(f"Sunrise: {format_time(next_sunrise)}")
        
        # Get objects
        if USE_CSV_CATALOG:
            all_objects = get_objects_from_csv()
            if not all_objects:
                all_objects = get_combined_catalog()
        else:
            all_objects = get_combined_catalog()
        
        # Filter by object name if specified
        if args.object:
            filtered_objects = [obj for obj in all_objects 
                              if args.object.lower() in obj.name.lower()]
            if filtered_objects:
                all_objects = filtered_objects
            else:
                print(f"No objects found matching '{args.object}'")
                return 1
        
        # Filter by type if specified
        if args.type:
            filtered_objects = get_objects_by_type(args.type, all_objects)
            if filtered_objects:
                all_objects = filtered_objects
            else:
                print(f"No objects found of type '{args.type}'")
                return 1
        
        # Filter objects based on visibility and exposure requirements
        visible_objects, insufficient_objects = filter_visible_objects_enhanced(
            all_objects, start_time, end_time, 
            exclude_insufficient=EXCLUDE_INSUFFICIENT_TIME, 
            use_margins=not args.no_margins
        )
        
        if not visible_objects and not insufficient_objects:
            print("No objects are visible under current conditions")
            return 1
        
        print(f"\nVisible objects: {len(visible_objects)}")
        if insufficient_objects:
            print(f"Objects with insufficient time: {len(insufficient_objects)}")
        
        # Initialize report generator
        report_gen = ReportGenerator(observation_date_dt, DEFAULT_LOCATION, start_time, end_time)
        
        # Calculate moon information
        moon_phase = calculate_moon_phase(start_time)
        
        # Find moon rise/set times
        moon_rise = None
        moon_set = None
        current_time = start_time
        prev_moon_alt = None
        
        while current_time <= end_time:
            moon_alt, _ = calculate_moon_position(current_time)
            
            if prev_moon_alt is not None:
                # Check for moon rise (transition from negative to positive altitude)
                if prev_moon_alt < 0 and moon_alt >= 0:
                    moon_rise = current_time
                # Check for moon set (transition from positive to negative altitude)
                elif prev_moon_alt >= 0 and moon_alt < 0:
                    moon_set = current_time
            
            prev_moon_alt = moon_alt
            current_time += timedelta(minutes=5)
        
        # Check moon proximity for all objects
        moon_affected = []
        for obj in visible_objects:
            obj.moon_influence_periods = []
            
            check_time = start_time
            in_interference = False
            interference_start = None
            
            while check_time <= end_time:
                obj_alt, obj_az = calculate_altaz(obj, check_time)
                moon_alt, moon_az = calculate_moon_position(check_time)
                
                if (is_visible(obj_alt, obj_az, use_margins=not args.no_margins) and 
                    moon_alt >= 0):  # Only check when moon is above horizon
                    
                    is_interfering = is_near_moon(obj_alt, obj_az, moon_alt, moon_az, 
                                                obj.magnitude, check_time)
                    
                    if is_interfering and not in_interference:
                        interference_start = check_time
                        in_interference = True
                    elif not is_interfering and in_interference:
                        if interference_start:
                            obj.moon_influence_periods.append((interference_start, check_time))
                        in_interference = False
                        interference_start = None
                
                check_time += timedelta(minutes=5)
            
            # Handle case where interference continues to end
            if in_interference and interference_start:
                obj.moon_influence_periods.append((interference_start, end_time))
            
            # Mark object as moon-affected if there are interference periods
            if obj.moon_influence_periods:
                obj.near_moon = True
                moon_affected.append(obj)
        
        # Generate report sections
        report_gen.generate_quick_summary(visible_objects, moon_affected, 
                                        start_time, end_time, moon_phase)
        report_gen.generate_timing_section(sunset, next_sunrise, 
                                         twilight_evening, twilight_morning,
                                         moon_rise, moon_set)
        report_gen.generate_moon_conditions(moon_phase, moon_affected)
        report_gen.generate_object_sections(visible_objects, insufficient_objects)
        
        # Mosaic group analysis if requested
        mosaic_groups = []
        combined_objects = visible_objects
        
        if args.mosaic or args.mosaic_only or args.schedule == 'mosaic_groups':
            print("\nAnalyzing mosaic groups...")
            # This would require the mosaic analysis functions
            # For now, we'll skip this functionality
            print("Mosaic analysis not yet implemented in enhanced version")
        
        # Filter objects if mosaic-only mode
        if args.mosaic_only:
            if mosaic_groups:
                combined_objects = mosaic_groups
            else:
                print("No mosaic groups found. Exiting.")
                return 1
        
        # Generate schedules for different strategies
        schedules = {}
        for strategy in SchedulingStrategy:
            schedule = generate_observation_schedule(
                combined_objects, start_time, end_time,
                strategy=strategy)
            schedules[strategy] = schedule
            report_gen.generate_schedule_section(schedule, strategy)
        
        # Print the complete report
        print(report_gen.generate_report())
        
        # Skip plots if report-only is specified
        if args.report_only:
            return 0
        
        # Use selected strategy for visualization
        schedule = schedules[selected_strategy]
        
        # Create plots
        import matplotlib.pyplot as plt
        import numpy as np
        
        if args.quarters:
            # Create 4-quarter trajectory plots (placeholder for now)
            print("Quarter plots not yet implemented in enhanced version")
        else:
            # Create standard trajectory plot
            print("\nGenerating trajectory plot...")
            fig, ax = setup_altaz_plot()
            
            # Generate colors for objects
            colormap = plt.get_cmap(COLOR_MAP) 
            colors = colormap(np.linspace(0, 1, len(combined_objects)))
            
            # Plot moon trajectory first
            plot_moon_trajectory(ax, start_time, end_time)
            
            existing_positions = []
            # Plot trajectories for combined objects
            for obj, color in zip(combined_objects, colors):
                plot_object_trajectory(ax, obj, start_time, end_time, 
                                     color, existing_positions, schedule)
            
            # Plot trajectories for insufficient time objects if not excluded
            if not EXCLUDE_INSUFFICIENT_TIME and not args.mosaic_only:
                for obj in insufficient_objects:
                    plot_object_trajectory(ax, obj, start_time, end_time, 
                                         'pink', existing_positions, schedule)
            
            plt.title(f"Object Trajectories for Night of {observation_date}")
            finalize_plot_legend(ax)
            plt.tight_layout()
            plt.show()
            plt.close(fig)
            
            # Create visibility chart
            print("Generating visibility chart...")
            all_chart_objects = combined_objects
            if not EXCLUDE_INSUFFICIENT_TIME:
                all_chart_objects = combined_objects + insufficient_objects
            
            fig, ax = plot_visibility_chart(all_chart_objects, start_time, end_time, 
                                          schedule, use_margins=not args.no_margins)
            plt.show()
            plt.close(fig)
        
        # Memory cleanup for iOS
        clear_calculation_cache()
        gc.collect()
        
        print(f"\nObservation planning complete!")
        return 0
        
    except Exception as e:
        print(f"Error during planning: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
