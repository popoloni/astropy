"""
Celestial body calculations (sun, moon) for astronomical observations.

This module provides both standard and high-precision astronomical calculations
with configurable precision modes and graceful fallback capabilities.
"""

import math
import pytz
import logging
from typing import Optional, Dict, Any, Union
from .time_utils import calculate_julian_date

# Import precision modules
try:
    from .precision.config import should_use_high_precision, log_precision_fallback
    from .precision.high_precision import (
        calculate_high_precision_lst,
        calculate_high_precision_sun_position,
        calculate_high_precision_moon_position,
        calculate_high_precision_moon_phase
    )
    from .precision.atmospheric import apply_atmospheric_refraction
    PRECISION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"High-precision modules not available: {e}")
    PRECISION_AVAILABLE = False


def calculate_lst(dt, observer_lon: float, precision_mode: Optional[str] = None) -> float:
    """
    Calculate Local Sidereal Time with configurable precision
    
    Args:
        dt: Datetime object (UTC)
        observer_lon: Observer longitude in radians
        precision_mode: Override precision mode ('standard', 'high', 'auto', None)
        
    Returns:
        Local Sidereal Time in radians
    """
    # Try high-precision calculation if available and enabled
    if PRECISION_AVAILABLE and should_use_high_precision(precision_mode):
        try:
            # Convert longitude from radians to degrees for high-precision function
            observer_lon_deg = math.degrees(observer_lon)
            lst_hours = calculate_high_precision_lst(dt, observer_lon_deg)
            # Convert from hours to radians
            return (lst_hours * 15.0 * math.pi / 180.0) % (2 * math.pi)
        except Exception as e:
            if PRECISION_AVAILABLE:
                log_precision_fallback('LST', e)
    
    # Standard implementation (original code)
    return _calculate_standard_lst(dt, observer_lon)

def _calculate_standard_lst(dt, observer_lon: float) -> float:
    """Standard Local Sidereal Time calculation (original implementation)"""
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
        
    jd = calculate_julian_date(dt)
    t = (jd - 2451545.0) / 36525
    
    gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3/38710000
    gst = math.radians(gst % 360)
    
    lst = gst + observer_lon
    return lst % (2 * math.pi)


def calculate_sun_position(dt, precision_mode: Optional[str] = None) -> Union[tuple, Dict[str, float]]:
    """
    Calculate Sun's position with configurable precision
    
    Args:
        dt: Datetime object (UTC)
        precision_mode: Override precision mode ('standard', 'high', 'auto', None)
        
    Returns:
        For standard mode: (altitude, azimuth) tuple in degrees
        For high-precision mode: Dictionary with 'ra', 'dec', 'distance' keys
    """
    # Try high-precision calculation if available and enabled
    if PRECISION_AVAILABLE and should_use_high_precision(precision_mode):
        try:
            return calculate_high_precision_sun_position(dt)
        except Exception as e:
            if PRECISION_AVAILABLE:
                log_precision_fallback('sun_position', e)
    
    # Standard implementation (original code)
    return _calculate_standard_sun_position(dt)

def _calculate_standard_sun_position(dt) -> tuple:
    """Standard sun position calculation (original implementation)"""
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
    
    # Import here to avoid circular imports during refactoring
    from config.settings import OBSERVER
    
    ha = calculate_lst(dt, OBSERVER.lon) - ra
    
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
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    # Import here to avoid circular imports during refactoring
    from config.settings import OBSERVER
    
    lst = calculate_lst(dt, OBSERVER.lon)
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

    # Import here to avoid circular imports during refactoring
    from config.settings import OBSERVER
    
    # Get local sidereal time
    lst = calculate_lst(dt, OBSERVER.lon)
    
    # Calculate hour angle
    ha = lst - alpha
    
    # Convert to local horizontal coordinates
    lat_rad = OBSERVER.lat
    
    # Calculate altitude
    sin_alt = (math.sin(lat_rad) * math.sin(delta) + 
               math.cos(lat_rad) * math.cos(delta) * math.cos(ha))
    alt = math.asin(sin_alt)
    
    # Calculate azimuth
    az = math.atan2(
        math.sin(ha),
        math.cos(ha) * math.sin(lat_rad) - math.tan(delta) * math.cos(lat_rad)
    )
    az = (math.degrees(az) + 180) % 360
    
    # Convert altitude to degrees and apply refraction correction
    alt_deg = math.degrees(alt)
    if alt_deg > -0.575:
        R = 1.02 / math.tan(math.radians(alt_deg + 10.3/(alt_deg + 5.11)))
        alt_deg += R/60.0  # R is in arc-minutes, convert to degrees
    
    return alt_deg, az


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
    
    # Import here to avoid circular imports during refactoring
    from config.settings import BORTLE_INDEX
    
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