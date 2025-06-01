"""
Precision Utilities

This module provides utility functions for high-precision astronomical calculations,
including decorators, caching, error handling, and mathematical utilities.
"""

import math
import functools
import logging
import pytz
from datetime import datetime
from typing import Any, Callable, Optional, Union
from .config import get_performance_config, log_precision_fallback

logger = logging.getLogger(__name__)

class PrecisionError(Exception):
    """Exception raised for precision calculation errors"""
    pass

class PrecisionWarning(UserWarning):
    """Warning raised for precision calculation issues"""
    pass

def normalize_angle(angle_deg: float) -> float:
    """
    Normalize angle to range [0, 360) degrees
    
    Args:
        angle_deg: Angle in degrees
        
    Returns:
        Normalized angle in degrees [0, 360)
    """
    angle = angle_deg % 360.0
    return angle if angle >= 0 else angle + 360.0

def normalize_angle_rad(angle_rad: float) -> float:
    """
    Normalize angle to range [0, 2π) radians
    
    Args:
        angle_rad: Angle in radians
        
    Returns:
        Normalized angle in radians [0, 2π)
    """
    angle = angle_rad % (2.0 * math.pi)
    return angle if angle >= 0 else angle + 2.0 * math.pi

def normalize_angle_symmetric(angle_deg: float) -> float:
    """
    Normalize angle to range (-180, 180] degrees
    
    Args:
        angle_deg: Angle in degrees
        
    Returns:
        Normalized angle in degrees (-180, 180]
    """
    angle = angle_deg % 360.0
    if angle > 180.0:
        angle -= 360.0
    return angle

def calculate_julian_date(dt: datetime) -> float:
    """
    Calculate Julian Date with enhanced precision
    
    Args:
        dt: Datetime object (assumed UTC if no timezone)
        
    Returns:
        Julian Date as float
    """
    # Ensure we have a timezone-aware datetime
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    elif dt.tzinfo != pytz.UTC:
        dt = dt.astimezone(pytz.UTC)
    
    # Extract date components
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    microsecond = dt.microsecond
    
    # Handle January and February as months 13 and 14 of previous year
    if month <= 2:
        year -= 1
        month += 12
    
    # Calculate Julian Date using standard algorithm
    a = year // 100
    b = 2 - a + (a // 4)
    
    # Julian Day Number at 0h UT
    jdn = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
    
    # Add fractional day
    fractional_day = (hour + minute/60.0 + (second + microsecond/1e6)/3600.0) / 24.0
    
    return jdn + fractional_day

def julian_centuries_since_j2000(jd: float) -> float:
    """
    Calculate Julian centuries since J2000.0 epoch
    
    Args:
        jd: Julian Date
        
    Returns:
        Julian centuries since J2000.0
    """
    from .constants import HIGH_PRECISION_CONSTANTS
    return (jd - HIGH_PRECISION_CONSTANTS.J2000_EPOCH) / HIGH_PRECISION_CONSTANTS.JULIAN_CENTURY

def polynomial_evaluation(coefficients: list, x: float) -> float:
    """
    Evaluate polynomial using Horner's method for numerical stability
    
    Args:
        coefficients: List of coefficients [a0, a1, a2, ...] for a0 + a1*x + a2*x² + ...
        x: Variable value
        
    Returns:
        Polynomial value
    """
    if not coefficients:
        return 0.0
    
    result = coefficients[-1]
    for i in range(len(coefficients) - 2, -1, -1):
        result = result * x + coefficients[i]
    
    return result

def precision_cache(maxsize: Optional[int] = None):
    """
    Decorator for caching expensive precision calculations
    
    Args:
        maxsize: Maximum cache size (None for unlimited)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Get cache size from configuration if not specified
        if maxsize is None:
            config = get_performance_config()
            cache_size = config.get('cache_size_limit', 1000)
        else:
            cache_size = maxsize
        
        # Only apply caching if enabled in configuration
        config = get_performance_config()
        if config.get('enable_caching', True):
            cached_func = functools.lru_cache(maxsize=cache_size)(func)
            
            # Add cache statistics method
            def get_cache_info():
                return cached_func.cache_info()
            
            def clear_cache():
                cached_func.cache_clear()
                logger.info(f"Cleared cache for {func.__name__}")
            
            cached_func.get_cache_info = get_cache_info
            cached_func.clear_cache = clear_cache
            
            return cached_func
        else:
            return func
    
    return decorator

def precision_fallback(fallback_func: Callable):
    """
    Decorator for graceful fallback to standard implementation
    
    Args:
        fallback_func: Function to call if high-precision fails
        
    Returns:
        Decorator function
    """
    def decorator(high_precision_func: Callable) -> Callable:
        @functools.wraps(high_precision_func)
        def wrapper(*args, **kwargs):
            try:
                return high_precision_func(*args, **kwargs)
            except Exception as e:
                # Log the fallback
                log_precision_fallback(high_precision_func.__name__, e)
                
                # Call fallback function
                return fallback_func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def validate_input_range(value: float, min_val: float, max_val: float, name: str) -> float:
    """
    Validate input value is within acceptable range
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        name: Name of the parameter for error messages
        
    Returns:
        Validated value
        
    Raises:
        PrecisionError: If value is out of range
    """
    if not (min_val <= value <= max_val):
        raise PrecisionError(f"{name} must be between {min_val} and {max_val}, got {value}")
    return value

def validate_datetime(dt: datetime) -> datetime:
    """
    Validate datetime object for astronomical calculations
    
    Args:
        dt: Datetime to validate
        
    Returns:
        Validated datetime
        
    Raises:
        PrecisionError: If datetime is invalid
    """
    if not isinstance(dt, datetime):
        raise PrecisionError("Input must be a datetime object")
    
    # Check for reasonable date range (1900-2100)
    if dt.year < 1900 or dt.year > 2100:
        logger.warning(f"Date {dt.year} is outside recommended range (1900-2100), accuracy may be reduced")
    
    return dt

def deg_to_rad(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * math.pi / 180.0

def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * 180.0 / math.pi

def arcsec_to_deg(arcseconds: float) -> float:
    """Convert arcseconds to degrees"""
    return arcseconds / 3600.0

def deg_to_arcsec(degrees: float) -> float:
    """Convert degrees to arcseconds"""
    return degrees * 3600.0

def arcmin_to_deg(arcminutes: float) -> float:
    """Convert arcminutes to degrees"""
    return arcminutes / 60.0

def deg_to_arcmin(degrees: float) -> float:
    """Convert degrees to arcminutes"""
    return degrees * 60.0

def interpolate_linear(x1: float, y1: float, x2: float, y2: float, x: float) -> float:
    """
    Linear interpolation between two points
    
    Args:
        x1, y1: First point
        x2, y2: Second point
        x: X value to interpolate
        
    Returns:
        Interpolated Y value
    """
    if x2 == x1:
        return y1
    
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

def newton_raphson_solve(func: Callable, derivative: Callable, initial_guess: float, 
                        tolerance: float = 1e-10, max_iterations: int = 50) -> float:
    """
    Solve equation using Newton-Raphson method
    
    Args:
        func: Function to find root of
        derivative: Derivative of the function
        initial_guess: Initial guess for the root
        tolerance: Convergence tolerance
        max_iterations: Maximum number of iterations
        
    Returns:
        Root of the function
        
    Raises:
        PrecisionError: If convergence fails
    """
    x = initial_guess
    
    for i in range(max_iterations):
        fx = func(x)
        
        if abs(fx) < tolerance:
            return x
        
        dfx = derivative(x)
        if abs(dfx) < 1e-15:
            raise PrecisionError("Newton-Raphson: derivative too small")
        
        x_new = x - fx / dfx
        
        if abs(x_new - x) < tolerance:
            return x_new
        
        x = x_new
    
    raise PrecisionError(f"Newton-Raphson failed to converge after {max_iterations} iterations")

def spherical_to_cartesian(r: float, theta: float, phi: float) -> tuple:
    """
    Convert spherical coordinates to Cartesian
    
    Args:
        r: Radius
        theta: Azimuthal angle (radians)
        phi: Polar angle (radians)
        
    Returns:
        (x, y, z) Cartesian coordinates
    """
    sin_phi = math.sin(phi)
    x = r * sin_phi * math.cos(theta)
    y = r * sin_phi * math.sin(theta)
    z = r * math.cos(phi)
    
    return x, y, z

def cartesian_to_spherical(x: float, y: float, z: float) -> tuple:
    """
    Convert Cartesian coordinates to spherical
    
    Args:
        x, y, z: Cartesian coordinates
        
    Returns:
        (r, theta, phi) Spherical coordinates (radius, azimuth, polar angle)
    """
    r = math.sqrt(x*x + y*y + z*z)
    
    if r == 0:
        return 0, 0, 0
    
    theta = math.atan2(y, x)
    phi = math.acos(z / r)
    
    return r, theta, phi

def format_angle_dms(angle_deg: float, precision: int = 1) -> str:
    """
    Format angle in degrees, minutes, seconds
    
    Args:
        angle_deg: Angle in degrees
        precision: Decimal places for seconds
        
    Returns:
        Formatted string "DD°MM'SS.s""
    """
    sign = "-" if angle_deg < 0 else ""
    angle_deg = abs(angle_deg)
    
    degrees = int(angle_deg)
    minutes_float = (angle_deg - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    
    return f"{sign}{degrees}°{minutes:02d}'{seconds:0{precision+3}.{precision}f}\""

def format_time_hms(time_hours: float, precision: int = 1) -> str:
    """
    Format time in hours, minutes, seconds
    
    Args:
        time_hours: Time in hours
        precision: Decimal places for seconds
        
    Returns:
        Formatted string "HH:MM:SS.s"
    """
    hours = int(time_hours)
    minutes_float = (time_hours - hours) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:0{precision+3}.{precision}f}"