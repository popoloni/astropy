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
    """
    Class to represent the observer's location with improved coordinate handling
    
    IMPROVEMENTS MADE:
    - Added elevation/height support
    - Coordinate validation
    - Better coordinate management
    - Support for both radians and degrees
    """
    def __init__(self, lat, lon, elevation=0.0):
        """
        Initialize observer location
        
        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees  
            elevation: Elevation above sea level in meters (default: 0.0)
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude must be between -180 and 180 degrees, got {lon}")
        if elevation < -500:  # Allow below sea level but not too extreme
            raise ValueError(f"Elevation must be >= -500 meters, got {elevation}")
        
        # Store coordinates in both formats for convenience
        self.lat_deg = float(lat)
        self.lon_deg = float(lon)
        self.elevation = float(elevation)
        
        # Store in radians for astronomical calculations
        self.lat = math.radians(lat)
        self.lon = math.radians(lon)
    
    def __repr__(self):
        return f"Observer(lat={self.lat_deg:.3f}°, lon={self.lon_deg:.3f}°, elevation={self.elevation}m)"
    
    def __str__(self):
        lat_dir = "N" if self.lat_deg >= 0 else "S"
        lon_dir = "E" if self.lon_deg >= 0 else "W"
        return f"{abs(self.lat_deg):.3f}°{lat_dir}, {abs(self.lon_deg):.3f}°{lon_dir}, {self.elevation}m"


class CelestialObject:
    """Class to represent a celestial object"""
    def __init__(self, name, ra_hours, dec_deg, fov=None, magnitude=None, object_type=None):
        self.name = name
        self.ra = math.radians(ra_hours * 15)  # Convert hours to degrees then to radians
        self.dec = math.radians(dec_deg)
        self.fov = fov
        self.magnitude = magnitude
        self.total_area = _calculate_total_area(fov) if fov else 0
        self.required_exposure = None  # Will be calculated later
        
        # Add attributes that the mobile UI expects
        self.object_type = object_type or self._infer_object_type(name)
        self.score = 0.0  # Will be calculated by analysis functions
        self.visibility_hours = 0.0  # Will be calculated by visibility functions
        self.is_mosaic_candidate = False  # Will be determined by analysis
        self.optimal_time = None  # Will be set by scheduling
        self.near_moon = False  # Will be calculated by moon avoidance
        
        # Additional convenience attributes
        self.ra_degrees = ra_hours * 15  # Store RA in degrees for easier access
        self.dec_degrees = dec_deg  # Store Dec in degrees for easier access
        
    def _infer_object_type(self, name):
        """Infer object type from name patterns"""
        name_lower = name.lower()
        
        # Nebulae patterns
        if any(word in name_lower for word in ['nebula', 'ngc 1976', 'ngc 1982', 'ngc 6523', 'ngc 6611', 'ngc 6618', 'ngc 6514', 'ngc 6853', 'ngc 6720', 'ngc 650', 'ngc 3587']):
            return 'Nebula'
        
        # Galaxy patterns  
        if any(word in name_lower for word in ['galaxy', 'ngc 224', 'ngc 221', 'ngc 598', 'ngc 5194', 'ngc 5055', 'ngc 4826', 'ngc 3031', 'ngc 3034', 'ngc 5457', 'ngc 4594', 'ngc 4258', 'ngc 205']):
            return 'Galaxy'
            
        # Star cluster patterns (globular clusters)
        if any(word in name_lower for word in ['ngc 7089', 'ngc 5272', 'ngc 6121', 'ngc 5904', 'ngc 6254', 'ngc 6205', 'ngc 7078', 'ngc 6656', 'ngc 6809', 'ngc 6341']):
            return 'Star Cluster'
            
        # Open clusters and other star clusters
        if any(word in name_lower for word in ['cluster', 'pleiades', 'beehive', 'praesepe', 'ngc 6405', 'ngc 6475', 'ngc 6494', 'ngc 6603', 'ic 4725', 'ngc 1039', 'ngc 2168', 'ngc 1960', 'ngc 2099', 'ngc 1912', 'ngc 7092', 'ngc 2287', 'ngc 2632', 'ngc 2437', 'ngc 2422', 'ngc 2548', 'ngc 2323', 'ngc 2682', 'ngc 2447']):
            return 'Star Cluster'
            
        # Planetary nebulae (specific cases)
        if any(word in name_lower for word in ['ring nebula', 'dumbbell', 'owl nebula', 'little dumbbell']):
            return 'Planetary Nebula'
            
        # Supernova remnants
        if 'crab' in name_lower:
            return 'Supernova Remnant'
        
        # Default
        return 'Deep Sky Object'
        
    def set_analysis_results(self, score=None, visibility_hours=None, is_mosaic_candidate=None, optimal_time=None, near_moon=None):
        """Set results from analysis functions"""
        if score is not None:
            self.score = score
        if visibility_hours is not None:
            self.visibility_hours = visibility_hours
        if is_mosaic_candidate is not None:
            self.is_mosaic_candidate = is_mosaic_candidate
        if optimal_time is not None:
            self.optimal_time = optimal_time
        if near_moon is not None:
            self.near_moon = near_moon
            
    def __repr__(self):
        return f"CelestialObject(name='{self.name}', type='{self.object_type}', mag={self.magnitude})" 