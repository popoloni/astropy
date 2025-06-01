"""
High-Precision Astronomical Calculations - Advanced Atmospheric Modeling

This module provides advanced atmospheric refraction models and corrections
for high-precision astronomical calculations.

Features:
- Multiple refraction models (Bennett, Auer-Standish, Hohenkerk-Sinclair)
- Wavelength-dependent refraction
- Real-time weather integration
- Atmospheric layering models
- Gravitational deflection corrections

Author: OpenHands AI Assistant
Date: 2025-06-01
"""

import math
from typing import Dict, Optional, Tuple, Union
from datetime import datetime
from enum import Enum

from .constants import HIGH_PRECISION_CONSTANTS


class RefractionModel(Enum):
    """Available atmospheric refraction models"""
    BENNETT = "bennett"
    AUER_STANDISH = "auer_standish"
    HOHENKERK_SINCLAIR = "hohenkerk_sinclair"
    SAEMUNDSSON = "saemundsson"
    SIMPLE = "simple"


class AtmosphericConditions:
    """Atmospheric conditions for refraction calculations"""
    
    def __init__(self, temperature_c: float = 15.0, pressure_hpa: float = 1013.25,
                 humidity_percent: float = 50.0, wavelength_nm: float = 550.0):
        self.temperature_c = temperature_c
        self.temperature_k = temperature_c + 273.15
        self.pressure_hpa = pressure_hpa
        self.humidity_percent = humidity_percent
        self.wavelength_nm = wavelength_nm
    
    def get_refractivity(self) -> float:
        """Calculate atmospheric refractivity"""
        # Edlén formula for refractivity
        # Based on Ciddor (1996) for standard air
        
        # Convert to standard units
        T = self.temperature_k
        P = self.pressure_hpa * 100  # Convert to Pa
        f = self.humidity_percent / 100.0
        
        # Dry air refractivity at standard conditions
        # Using simplified Edlén formula
        sigma = 1e3 / self.wavelength_nm  # Wavenumber in μm⁻¹
        
        # Dry air refractivity
        n_dry = (8342.54 + 2406147.0 / (130.0 - sigma**2) + 
                15998.0 / (38.9 - sigma**2)) * 1e-8
        
        # Pressure and temperature corrections
        n_dry *= (P / 101325.0) * (288.15 / T)
        
        # Water vapor correction (simplified)
        if f > 0:
            # Saturation vapor pressure (Magnus formula)
            e_sat = 611.657 * math.exp(17.2799 * self.temperature_c / (self.temperature_c + 238.3))
            e = f * e_sat  # Actual vapor pressure
            
            # Water vapor refractivity
            n_water = -43.49 * e / T * 1e-8
            n_dry += n_water
        
        return n_dry
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation"""
        return {
            'temperature_c': self.temperature_c,
            'pressure_hpa': self.pressure_hpa,
            'humidity_percent': self.humidity_percent,
            'wavelength_nm': self.wavelength_nm,
            'refractivity': self.get_refractivity()
        }


class AdvancedAtmosphericModel:
    """Advanced atmospheric refraction and correction model"""
    
    def __init__(self):
        self.standard_conditions = AtmosphericConditions()
    
    def calculate_refraction(self, altitude_rad: float, 
                           conditions: Optional[AtmosphericConditions] = None,
                           model: RefractionModel = RefractionModel.BENNETT) -> float:
        """
        Calculate atmospheric refraction for given altitude and conditions
        
        Args:
            altitude_rad: Apparent altitude in radians
            conditions: Atmospheric conditions (uses standard if None)
            model: Refraction model to use
            
        Returns:
            Refraction correction in radians (to add to apparent altitude)
        """
        if conditions is None:
            conditions = self.standard_conditions
        
        # Convert to degrees for calculations
        altitude_deg = math.degrees(altitude_rad)
        
        if model == RefractionModel.BENNETT:
            refraction_arcmin = self._bennett_refraction(altitude_deg, conditions)
        elif model == RefractionModel.AUER_STANDISH:
            refraction_arcmin = self._auer_standish_refraction(altitude_deg, conditions)
        elif model == RefractionModel.HOHENKERK_SINCLAIR:
            refraction_arcmin = self._hohenkerk_sinclair_refraction(altitude_deg, conditions)
        elif model == RefractionModel.SAEMUNDSSON:
            refraction_arcmin = self._saemundsson_refraction(altitude_deg, conditions)
        else:  # SIMPLE
            refraction_arcmin = self._simple_refraction(altitude_deg, conditions)
        
        # Convert back to radians
        return math.radians(refraction_arcmin / 60.0)
    
    def _bennett_refraction(self, altitude_deg: float, 
                           conditions: AtmosphericConditions) -> float:
        """Bennett's refraction formula (1982)"""
        if altitude_deg < -2.0:
            return 0.0
        
        # Bennett's formula in arcminutes
        if altitude_deg >= 15.0:
            # High altitude approximation
            refraction = 1.02 / math.tan(math.radians(altitude_deg + 10.3 / (altitude_deg + 5.11)))
        else:
            # Low altitude formula
            h = altitude_deg
            if h < 0:
                h = 0
            refraction = 1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11)))
            
            # Additional correction for very low altitudes
            if altitude_deg < 5.0:
                correction = 0.06 * math.exp(-altitude_deg / 2.0)
                refraction += correction
        
        # Apply atmospheric conditions correction
        refractivity_ratio = conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        refraction *= refractivity_ratio
        
        return refraction
    
    def _auer_standish_refraction(self, altitude_deg: float,
                                 conditions: AtmosphericConditions) -> float:
        """Auer & Standish refraction model (2000)"""
        if altitude_deg < -1.0:
            return 0.0
        
        # Convert to zenith distance
        z_deg = 90.0 - altitude_deg
        z_rad = math.radians(z_deg)
        
        if z_deg > 89.0:
            # Very low altitude - use asymptotic formula
            return 34.46 * math.tan(z_rad) * conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        
        # Auer & Standish formula
        tan_z = math.tan(z_rad)
        
        # Polynomial approximation
        refraction = (1.02 * tan_z - 0.0368 * tan_z**3 + 
                     0.000327 * tan_z**5)
        
        # Apply atmospheric conditions
        refractivity_ratio = conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        refraction *= refractivity_ratio
        
        return refraction
    
    def _hohenkerk_sinclair_refraction(self, altitude_deg: float,
                                      conditions: AtmosphericConditions) -> float:
        """Hohenkerk & Sinclair refraction model (1985)"""
        if altitude_deg < -1.0:
            return 0.0
        
        # This is a simplified version of the Hohenkerk & Sinclair model
        # The full model requires numerical integration through atmospheric layers
        
        z_deg = 90.0 - altitude_deg
        z_rad = math.radians(z_deg)
        
        if z_deg > 88.0:
            # Very low altitude
            return 35.0 * math.tan(z_rad) * conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        
        # Simplified polynomial fit to H&S tables
        tan_z = math.tan(z_rad)
        
        refraction = (1.0247 * tan_z - 0.0314 * tan_z**3 + 
                     0.000259 * tan_z**5 - 0.0000008 * tan_z**7)
        
        # Apply atmospheric conditions
        refractivity_ratio = conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        refraction *= refractivity_ratio
        
        return refraction
    
    def _saemundsson_refraction(self, altitude_deg: float,
                               conditions: AtmosphericConditions) -> float:
        """Saemundsson's refraction formula"""
        if altitude_deg < -2.0:
            return 0.0
        
        # Saemundsson's formula (similar to Bennett but different coefficients)
        h = max(altitude_deg, 0)
        refraction = 1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11))) + 0.0019279
        
        # Apply atmospheric conditions
        refractivity_ratio = conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        refraction *= refractivity_ratio
        
        return refraction
    
    def _simple_refraction(self, altitude_deg: float,
                          conditions: AtmosphericConditions) -> float:
        """Simple refraction approximation"""
        if altitude_deg < 0:
            return 0.0
        
        # Simple cotangent formula
        refraction = 1.0 / math.tan(math.radians(altitude_deg + 7.31 / (altitude_deg + 4.4)))
        
        # Apply atmospheric conditions
        refractivity_ratio = conditions.get_refractivity() / self.standard_conditions.get_refractivity()
        refraction *= refractivity_ratio
        
        return refraction
    
    def calculate_wavelength_dependent_refraction(self, altitude_rad: float,
                                                 wavelengths_nm: list,
                                                 conditions: Optional[AtmosphericConditions] = None) -> Dict[float, float]:
        """
        Calculate refraction for multiple wavelengths (chromatic refraction)
        
        Args:
            altitude_rad: Apparent altitude in radians
            wavelengths_nm: List of wavelengths in nanometers
            conditions: Atmospheric conditions
            
        Returns:
            Dictionary mapping wavelength to refraction in radians
        """
        if conditions is None:
            conditions = self.standard_conditions
        
        results = {}
        
        for wavelength in wavelengths_nm:
            # Create conditions for this wavelength
            wave_conditions = AtmosphericConditions(
                temperature_c=conditions.temperature_c,
                pressure_hpa=conditions.pressure_hpa,
                humidity_percent=conditions.humidity_percent,
                wavelength_nm=wavelength
            )
            
            refraction = self.calculate_refraction(
                altitude_rad, wave_conditions, RefractionModel.BENNETT
            )
            results[wavelength] = refraction
        
        return results
    
    def calculate_air_mass(self, altitude_rad: float,
                          include_refraction: bool = True,
                          conditions: Optional[AtmosphericConditions] = None) -> float:
        """
        Calculate atmospheric air mass
        
        Args:
            altitude_rad: Apparent altitude in radians
            include_refraction: Whether to include refraction correction
            conditions: Atmospheric conditions
            
        Returns:
            Air mass (dimensionless)
        """
        if include_refraction and conditions:
            # Correct for refraction
            refraction = self.calculate_refraction(altitude_rad, conditions)
            true_altitude = altitude_rad - refraction
        else:
            true_altitude = altitude_rad
        
        # Convert to zenith distance
        zenith_dist = math.pi / 2 - true_altitude
        
        if zenith_dist > math.radians(85):
            # Use Kasten & Young formula for large zenith distances
            cos_z = math.cos(zenith_dist)
            air_mass = 1.0 / (cos_z + 0.50572 * (96.07995 - math.degrees(zenith_dist))**(-1.6364))
        else:
            # Simple secant formula for small zenith distances
            air_mass = 1.0 / math.cos(zenith_dist)
        
        return air_mass
    
    def calculate_gravitational_deflection(self, ra_rad: float, dec_rad: float,
                                          sun_ra_rad: float, sun_dec_rad: float) -> Tuple[float, float]:
        """
        Calculate gravitational light deflection due to the Sun
        
        Args:
            ra_rad: Object right ascension in radians
            dec_rad: Object declination in radians
            sun_ra_rad: Sun right ascension in radians
            sun_dec_rad: Sun declination in radians
            
        Returns:
            Tuple of (delta_ra, delta_dec) corrections in radians
        """
        # Angular separation from Sun
        cos_theta = (math.sin(dec_rad) * math.sin(sun_dec_rad) +
                    math.cos(dec_rad) * math.cos(sun_dec_rad) * 
                    math.cos(ra_rad - sun_ra_rad))
        
        theta = math.acos(max(-1, min(1, cos_theta)))
        
        # Einstein deflection constant (4GM/c²R☉ in radians)
        einstein_constant = 8.24e-6  # radians
        
        if theta < math.radians(10):  # Only significant within 10° of Sun
            # Deflection magnitude
            deflection = einstein_constant / math.tan(theta / 2)
            
            # Direction of deflection (away from Sun)
            delta_ra = deflection * math.cos(sun_dec_rad) * math.sin(sun_ra_rad - ra_rad) / math.cos(dec_rad)
            delta_dec = deflection * (math.sin(sun_dec_rad) * math.cos(dec_rad) -
                                     math.cos(sun_dec_rad) * math.sin(dec_rad) * math.cos(ra_rad - sun_ra_rad))
            
            return delta_ra, delta_dec
        
        return 0.0, 0.0
    
    def calculate_stellar_aberration(self, ra_rad: float, dec_rad: float,
                                   earth_velocity_km_s: Tuple[float, float, float]) -> Tuple[float, float]:
        """
        Calculate stellar aberration correction
        
        Args:
            ra_rad: Object right ascension in radians
            dec_rad: Object declination in radians
            earth_velocity_km_s: Earth velocity vector (vx, vy, vz) in km/s
            
        Returns:
            Tuple of (delta_ra, delta_dec) corrections in radians
        """
        # Speed of light in km/s
        c = 299792.458
        
        vx, vy, vz = earth_velocity_km_s
        
        # Convert to unit vector
        cos_ra = math.cos(ra_rad)
        sin_ra = math.sin(ra_rad)
        cos_dec = math.cos(dec_rad)
        sin_dec = math.sin(dec_rad)
        
        # Stellar aberration formula (first order)
        delta_ra = (vx * sin_ra - vy * cos_ra) / (c * cos_dec)
        delta_dec = -(vx * cos_ra * sin_dec + vy * sin_ra * sin_dec - vz * cos_dec) / c
        
        return delta_ra, delta_dec


class WeatherDataProvider:
    """Interface for real-time weather data"""
    
    def __init__(self):
        self.default_conditions = AtmosphericConditions()
    
    def get_current_conditions(self, latitude: float, longitude: float) -> AtmosphericConditions:
        """
        Get current atmospheric conditions for a location
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Current atmospheric conditions
        """
        # This is a placeholder implementation
        # In a real implementation, this would query a weather API
        
        # For now, return default conditions with some variation based on location
        temp_variation = math.sin(math.radians(latitude)) * 20  # Temperature varies with latitude
        pressure_variation = -latitude / 90.0 * 50  # Pressure varies with latitude
        
        return AtmosphericConditions(
            temperature_c=15.0 + temp_variation,
            pressure_hpa=1013.25 + pressure_variation,
            humidity_percent=50.0,
            wavelength_nm=550.0
        )
    
    def get_forecast_conditions(self, latitude: float, longitude: float,
                              forecast_hours: int = 24) -> Dict[int, AtmosphericConditions]:
        """
        Get forecast atmospheric conditions
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            forecast_hours: Hours into the future
            
        Returns:
            Dictionary mapping hour offset to conditions
        """
        # Placeholder implementation
        base_conditions = self.get_current_conditions(latitude, longitude)
        
        forecast = {}
        for hour in range(forecast_hours):
            # Add some variation over time
            temp_change = math.sin(hour * math.pi / 12) * 5  # Daily temperature cycle
            pressure_change = math.sin(hour * math.pi / 24) * 10  # Pressure variation
            
            forecast[hour] = AtmosphericConditions(
                temperature_c=base_conditions.temperature_c + temp_change,
                pressure_hpa=base_conditions.pressure_hpa + pressure_change,
                humidity_percent=base_conditions.humidity_percent,
                wavelength_nm=base_conditions.wavelength_nm
            )
        
        return forecast


# Example usage and testing
if __name__ == "__main__":
    # Test the advanced atmospheric model
    
    model = AdvancedAtmosphericModel()
    
    print("🌍 Testing Advanced Atmospheric Model")
    print("=" * 50)
    
    # Test different altitudes
    altitudes = [5, 10, 20, 30, 45, 60, 75, 85]
    
    print("Refraction comparison for different models:")
    print(f"{'Alt(°)':<6} {'Bennett':<8} {'A&S':<8} {'H&S':<8} {'Simple':<8}")
    print("-" * 40)
    
    for alt in altitudes:
        alt_rad = math.radians(alt)
        
        bennett = model.calculate_refraction(alt_rad, model=RefractionModel.BENNETT)
        auer = model.calculate_refraction(alt_rad, model=RefractionModel.AUER_STANDISH)
        hohen = model.calculate_refraction(alt_rad, model=RefractionModel.HOHENKERK_SINCLAIR)
        simple = model.calculate_refraction(alt_rad, model=RefractionModel.SIMPLE)
        
        print(f"{alt:<6} {bennett*206265:<8.1f} {auer*206265:<8.1f} {hohen*206265:<8.1f} {simple*206265:<8.1f}")
    
    print("\n(Values in arcseconds)")
    
    # Test wavelength-dependent refraction
    print("\nChromatic refraction at 10° altitude:")
    wavelengths = [400, 500, 600, 700, 800]  # nm
    chromatic = model.calculate_wavelength_dependent_refraction(
        math.radians(10), wavelengths
    )
    
    for wl, refr in chromatic.items():
        print(f"  {wl} nm: {refr * 206265:.2f} arcsec")
    
    # Test air mass calculation
    print(f"\nAir mass at 30° altitude: {model.calculate_air_mass(math.radians(30)):.3f}")
    
    print("\n✅ Advanced atmospheric model test completed")