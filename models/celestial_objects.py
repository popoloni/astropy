"""
Core classes representing celestial objects and observers.
"""

import math
import re


def _calculate_total_area(fov_str):
    """Calculate total area in square degrees from FOV string. Temporary function until full refactoring."""
    if not fov_str:
        return 0
    
    # Parse format like "60'x40'" or "2.5°x1.8°"
    if 'x' in fov_str:
        parts = fov_str.split('x')
        if len(parts) == 2:
            width_str = parts[0].strip()
            height_str = parts[1].strip()
            
            # Extract numeric values and units
            width_match = re.match(r"(\d*\.?\d+)([°'\"]+)", width_str)
            height_match = re.match(r"(\d*\.?\d+)([°'\"]+)", height_str)
            
            if width_match and height_match:
                width_val = float(width_match.group(1))
                height_val = float(height_match.group(1))
                width_unit = width_match.group(2)
                height_unit = height_match.group(2)
                
                # Convert to degrees
                if width_unit == "°":
                    width_deg = width_val
                elif width_unit == "'":
                    width_deg = width_val / 60.0
                elif width_unit == "\"":
                    width_deg = width_val / 3600.0
                else:
                    width_deg = width_val / 60.0  # Default to arcminutes
                
                if height_unit == "°":
                    height_deg = height_val
                elif height_unit == "'":
                    height_deg = height_val / 60.0
                elif height_unit == "\"":
                    height_deg = height_val / 3600.0
                else:
                    height_deg = height_val / 60.0  # Default to arcminutes
                
                return width_deg * height_deg
    
    return 0


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
        self.total_area = _calculate_total_area(fov) if fov else 0
        self.required_exposure = None  # Will be calculated later 