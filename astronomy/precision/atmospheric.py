"""
Atmospheric Refraction Corrections

This module provides high-precision atmospheric refraction calculations using
various models including Bennett's formula, Saemundsson's formula, and others.
"""

import math
import logging
from typing import Optional, Dict, Any
from .constants import ATMOSPHERIC_CONSTANTS
from .config import get_atmospheric_config
from .utils import validate_input_range, deg_to_rad, rad_to_deg, precision_cache

logger = logging.getLogger(__name__)

@precision_cache(maxsize=500)
def apply_atmospheric_refraction(altitude_deg: float, 
                               pressure_mbar: Optional[float] = None,
                               temperature_c: Optional[float] = None,
                               humidity_percent: Optional[float] = None,
                               model: str = 'auto') -> float:
    """
    Apply atmospheric refraction correction to altitude
    
    Args:
        altitude_deg: Apparent altitude in degrees
        pressure_mbar: Atmospheric pressure in millibars (optional)
        temperature_c: Temperature in Celsius (optional)
        humidity_percent: Relative humidity percentage (optional)
        model: Refraction model ('bennett', 'saemundsson', 'simple', 'auto')
        
    Returns:
        Refraction correction in degrees (add to apparent altitude to get true altitude)
    """
    # Validate input
    validate_input_range(altitude_deg, -90.0, 90.0, "altitude")
    
    # Get configuration defaults
    config = get_atmospheric_config()
    
    if pressure_mbar is None:
        pressure_mbar = config['default_pressure_mbar']
    if temperature_c is None:
        temperature_c = config['default_temperature_c']
    if humidity_percent is None:
        humidity_percent = 0.0  # Assume dry air if not specified
    if model == 'auto':
        model = config.get('refraction_model', 'bennett')
    
    # Validate atmospheric parameters
    validate_input_range(pressure_mbar, 500.0, 1100.0, "pressure")
    validate_input_range(temperature_c, -50.0, 50.0, "temperature")
    validate_input_range(humidity_percent, 0.0, 100.0, "humidity")
    
    # No refraction for objects below horizon
    if altitude_deg < -1.0:
        return 0.0
    
    # Choose refraction model
    if model == 'bennett':
        return _bennett_refraction(altitude_deg, pressure_mbar, temperature_c, humidity_percent)
    elif model == 'saemundsson':
        return _saemundsson_refraction(altitude_deg, pressure_mbar, temperature_c)
    elif model == 'simple':
        return _simple_refraction(altitude_deg, pressure_mbar, temperature_c)
    else:
        raise ValueError(f"Unknown refraction model: {model}")

def _bennett_refraction(altitude_deg: float, pressure_mbar: float, 
                       temperature_c: float, humidity_percent: float) -> float:
    """
    Bennett's atmospheric refraction formula (1982)
    
    Accurate to ~0.1 arcmin for altitudes > 5°
    """
    constants = ATMOSPHERIC_CONSTANTS['bennett']
    
    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15
    
    # Pressure and temperature corrections
    pressure_factor = pressure_mbar / constants['standard_pressure']
    temperature_factor = constants['standard_temperature'] / temperature_k
    
    # Humidity correction (simplified)
    humidity_factor = 1.0 - 0.0013 * humidity_percent / 100.0
    
    # Bennett's formula
    if altitude_deg > 15.0:
        # High altitude approximation (simpler, more accurate)
        refraction_arcmin = constants['A'] / math.tan(deg_to_rad(altitude_deg + 
                           constants['C'] / (altitude_deg + 3.0)))
    else:
        # Low altitude formula
        refraction_arcmin = constants['B'] / math.tan(deg_to_rad(altitude_deg + 
                           constants['C'] / (altitude_deg + 3.0)))
    
    # Apply atmospheric corrections
    refraction_arcmin *= pressure_factor * temperature_factor * humidity_factor
    
    # Convert to degrees
    return refraction_arcmin / 60.0

def _saemundsson_refraction(altitude_deg: float, pressure_mbar: float, 
                           temperature_c: float) -> float:
    """
    Saemundsson's atmospheric refraction formula
    
    Alternative to Bennett's formula with slightly different coefficients
    """
    constants = ATMOSPHERIC_CONSTANTS['saemundsson']
    
    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15
    
    # Pressure and temperature corrections
    pressure_factor = pressure_mbar / constants['standard_pressure']
    temperature_factor = constants['standard_temperature'] / temperature_k
    
    # Saemundsson's formula
    if altitude_deg > 15.0:
        refraction_arcmin = constants['A'] / math.tan(deg_to_rad(altitude_deg))
    else:
        refraction_arcmin = (constants['B'] / math.tan(deg_to_rad(altitude_deg + 
                            constants['C'] / (altitude_deg + 3.0))) - 
                            constants['D'] * math.tan(deg_to_rad(altitude_deg)))
    
    # Apply atmospheric corrections
    refraction_arcmin *= pressure_factor * temperature_factor
    
    # Convert to degrees
    return refraction_arcmin / 60.0

def _simple_refraction(altitude_deg: float, pressure_mbar: float, 
                      temperature_c: float) -> float:
    """
    Simple atmospheric refraction model
    
    Less accurate but faster computation
    """
    constants = ATMOSPHERIC_CONSTANTS['simple']
    
    # Only apply for reasonable altitudes
    if altitude_deg < constants['min_altitude']:
        return 0.0
    
    # Convert temperature to Kelvin
    temperature_k = temperature_c + 273.15
    
    # Simple pressure and temperature corrections
    pressure_factor = pressure_mbar / 1013.25
    temperature_factor = 288.15 / temperature_k
    
    # Simple refraction formula
    refraction_deg = constants['coefficient'] / math.tan(deg_to_rad(altitude_deg))
    
    # Apply atmospheric corrections
    refraction_deg *= pressure_factor * temperature_factor
    
    return refraction_deg

def calculate_atmospheric_conditions(location: Dict[str, float], 
                                   datetime_obj: Any = None) -> Dict[str, float]:
    """
    Calculate atmospheric conditions based on location and time
    
    Args:
        location: Dictionary with 'latitude', 'longitude', 'elevation' keys
        datetime_obj: Datetime object (optional, for seasonal variations)
        
    Returns:
        Dictionary with atmospheric parameters
    """
    elevation_m = location.get('elevation', 0.0)
    
    # Standard atmosphere model
    # Temperature decreases with altitude
    temperature_c = 15.0 - 0.0065 * elevation_m
    
    # Pressure decreases with altitude
    pressure_mbar = 1013.25 * math.pow(1.0 - 0.0065 * elevation_m / 288.15, 5.255)
    
    # Default humidity (could be enhanced with weather data)
    humidity_percent = 50.0
    
    # Seasonal temperature variation (simplified)
    if datetime_obj is not None:
        try:
            # Simple seasonal variation based on day of year
            day_of_year = datetime_obj.timetuple().tm_yday
            seasonal_variation = 10.0 * math.sin(2 * math.pi * (day_of_year - 80) / 365.25)
            temperature_c += seasonal_variation
        except:
            pass  # Ignore if datetime processing fails
    
    return {
        'pressure_mbar': pressure_mbar,
        'temperature_c': temperature_c,
        'humidity_percent': humidity_percent,
        'elevation_m': elevation_m
    }

def get_refraction_correction(altitude_deg: float, 
                            atmospheric_conditions: Optional[Dict[str, float]] = None,
                            model: str = 'auto') -> float:
    """
    Get refraction correction with optional atmospheric conditions
    
    Args:
        altitude_deg: Apparent altitude in degrees
        atmospheric_conditions: Dictionary with atmospheric parameters
        model: Refraction model to use
        
    Returns:
        Refraction correction in degrees
    """
    if atmospheric_conditions is None:
        atmospheric_conditions = {}
    
    return apply_atmospheric_refraction(
        altitude_deg,
        pressure_mbar=atmospheric_conditions.get('pressure_mbar'),
        temperature_c=atmospheric_conditions.get('temperature_c'),
        humidity_percent=atmospheric_conditions.get('humidity_percent'),
        model=model
    )

def apply_refraction_to_coordinates(altitude_deg: float, azimuth_deg: float,
                                  atmospheric_conditions: Optional[Dict[str, float]] = None,
                                  model: str = 'auto') -> tuple:
    """
    Apply atmospheric refraction to altitude/azimuth coordinates
    
    Args:
        altitude_deg: Apparent altitude in degrees
        azimuth_deg: Azimuth in degrees
        atmospheric_conditions: Dictionary with atmospheric parameters
        model: Refraction model to use
        
    Returns:
        (corrected_altitude, azimuth) tuple in degrees
    """
    # Azimuth is not affected by atmospheric refraction
    corrected_altitude = altitude_deg + get_refraction_correction(
        altitude_deg, atmospheric_conditions, model
    )
    
    return corrected_altitude, azimuth_deg

def estimate_refraction_uncertainty(altitude_deg: float, 
                                  pressure_uncertainty: float = 5.0,
                                  temperature_uncertainty: float = 2.0) -> float:
    """
    Estimate uncertainty in refraction correction due to atmospheric parameter uncertainties
    
    Args:
        altitude_deg: Altitude in degrees
        pressure_uncertainty: Pressure uncertainty in mbar
        temperature_uncertainty: Temperature uncertainty in Celsius
        
    Returns:
        Refraction uncertainty in arcseconds
    """
    # Calculate nominal refraction
    nominal_refraction = apply_atmospheric_refraction(altitude_deg)
    
    # Calculate refraction with perturbed parameters
    config = get_atmospheric_config()
    
    # Pressure perturbation
    pressure_high = apply_atmospheric_refraction(
        altitude_deg, 
        pressure_mbar=config['default_pressure_mbar'] + pressure_uncertainty
    )
    pressure_low = apply_atmospheric_refraction(
        altitude_deg,
        pressure_mbar=config['default_pressure_mbar'] - pressure_uncertainty
    )
    
    # Temperature perturbation
    temp_high = apply_atmospheric_refraction(
        altitude_deg,
        temperature_c=config['default_temperature_c'] + temperature_uncertainty
    )
    temp_low = apply_atmospheric_refraction(
        altitude_deg,
        temperature_c=config['default_temperature_c'] - temperature_uncertainty
    )
    
    # Calculate uncertainties
    pressure_uncertainty_deg = abs(pressure_high - pressure_low) / 2.0
    temperature_uncertainty_deg = abs(temp_high - temp_low) / 2.0
    
    # Combine uncertainties (root sum of squares)
    total_uncertainty_deg = math.sqrt(pressure_uncertainty_deg**2 + 
                                    temperature_uncertainty_deg**2)
    
    # Convert to arcseconds
    return total_uncertainty_deg * 3600.0

def get_refraction_model_comparison(altitude_deg: float,
                                  atmospheric_conditions: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Compare refraction corrections from different models
    
    Args:
        altitude_deg: Altitude in degrees
        atmospheric_conditions: Atmospheric conditions dictionary
        
    Returns:
        Dictionary with refraction corrections from each model
    """
    models = ['bennett', 'saemundsson', 'simple']
    results = {}
    
    for model in models:
        try:
            correction = get_refraction_correction(altitude_deg, atmospheric_conditions, model)
            results[model] = correction
        except Exception as e:
            logger.warning(f"Failed to calculate refraction with {model} model: {e}")
            results[model] = 0.0
    
    return results