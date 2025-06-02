"""
Location Management
Handles GPS location and saved locations for AstroScope Planner
"""

import json
from typing import Dict, List, Optional, Tuple

# Try to import Kivy logger, fall back to standard logging
try:
    from kivy.logger import Logger
except ImportError:
    import logging
    Logger = logging.getLogger(__name__)

class LocationManager:
    """Manages user locations and GPS functionality"""
    
    def __init__(self):
        self.saved_locations = []
        self.current_gps_location = None
        self.gps_available = False
        
        # Load default locations from astropy config
        self.load_default_locations()
        
        # Try to initialize GPS
        self.initialize_gps()
    
    def load_default_locations(self):
        """Load default locations from astropy configuration"""
        try:
            # Import astropy config
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
            from astropy import CONFIG, DEFAULT_LOCATION
            
            if CONFIG and 'locations' in CONFIG:
                for location_key, location_data in CONFIG['locations'].items():
                    self.saved_locations.append({
                        'name': location_data.get('name', location_key.title()),
                        'latitude': location_data['latitude'],
                        'longitude': location_data['longitude'],
                        'timezone': location_data.get('timezone', 'UTC'),
                        'min_altitude': location_data.get('min_altitude', 15),
                        'max_altitude': location_data.get('max_altitude', 75),
                        'min_azimuth': location_data.get('min_azimuth', 0),
                        'max_azimuth': location_data.get('max_azimuth', 360),
                        'bortle_index': location_data.get('bortle_index', 5),
                        'is_default': location_data.get('default', False),
                        'source': 'config'
                    })
            
            Logger.info(f"LocationManager: Loaded {len(self.saved_locations)} default locations")
            
        except Exception as e:
            Logger.error(f"LocationManager: Error loading default locations: {e}")
            # Add a fallback location
            self.saved_locations.append({
                'name': 'Default Location',
                'latitude': 45.516667,
                'longitude': 9.216667,
                'timezone': 'Europe/Rome',
                'min_altitude': 15,
                'max_altitude': 75,
                'min_azimuth': 0,
                'max_azimuth': 360,
                'bortle_index': 6,
                'is_default': True,
                'source': 'fallback'
            })
    
    def initialize_gps(self):
        """Initialize GPS functionality if available"""
        try:
            # Try to import GPS functionality
            # Note: This would require platform-specific GPS libraries
            # For now, we'll simulate GPS availability
            self.gps_available = False  # Set to True when GPS is implemented
            Logger.info("LocationManager: GPS functionality initialized")
            
        except Exception as e:
            Logger.warning(f"LocationManager: GPS not available: {e}")
            self.gps_available = False
    
    def get_current_location(self) -> Optional[Dict]:
        """Get current GPS location if available"""
        if not self.gps_available:
            return None
        
        # TODO: Implement actual GPS location retrieval
        # This would use platform-specific GPS APIs
        return self.current_gps_location
    
    def add_location(self, name: str, latitude: float, longitude: float, **kwargs) -> bool:
        """Add a new saved location"""
        try:
            new_location = {
                'name': name,
                'latitude': float(latitude),
                'longitude': float(longitude),
                'timezone': kwargs.get('timezone', 'UTC'),
                'min_altitude': kwargs.get('min_altitude', 15),
                'max_altitude': kwargs.get('max_altitude', 75),
                'min_azimuth': kwargs.get('min_azimuth', 0),
                'max_azimuth': kwargs.get('max_azimuth', 360),
                'bortle_index': kwargs.get('bortle_index', 5),
                'is_default': kwargs.get('is_default', False),
                'source': 'user'
            }
            
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90 degrees")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180 degrees")
            
            # Check if location already exists
            for location in self.saved_locations:
                if (location['name'] == name or 
                    (abs(location['latitude'] - latitude) < 0.001 and 
                     abs(location['longitude'] - longitude) < 0.001)):
                    Logger.warning(f"LocationManager: Location '{name}' already exists")
                    return False
            
            self.saved_locations.append(new_location)
            Logger.info(f"LocationManager: Added location '{name}'")
            return True
            
        except Exception as e:
            Logger.error(f"LocationManager: Error adding location: {e}")
            return False
    
    def remove_location(self, name: str) -> bool:
        """Remove a saved location"""
        try:
            for i, location in enumerate(self.saved_locations):
                if location['name'] == name and location['source'] == 'user':
                    del self.saved_locations[i]
                    Logger.info(f"LocationManager: Removed location '{name}'")
                    return True
            
            Logger.warning(f"LocationManager: Location '{name}' not found or cannot be removed")
            return False
            
        except Exception as e:
            Logger.error(f"LocationManager: Error removing location: {e}")
            return False
    
    def get_location_by_name(self, name: str) -> Optional[Dict]:
        """Get location by name"""
        for location in self.saved_locations:
            if location['name'] == name:
                return location.copy()
        return None
    
    def get_default_location(self) -> Optional[Dict]:
        """Get the default location"""
        for location in self.saved_locations:
            if location.get('is_default', False):
                return location.copy()
        
        # If no default is set, return the first location
        if self.saved_locations:
            return self.saved_locations[0].copy()
        
        return None
    
    def set_default_location(self, name: str) -> bool:
        """Set a location as default"""
        try:
            # Clear existing default
            for location in self.saved_locations:
                location['is_default'] = False
            
            # Set new default
            for location in self.saved_locations:
                if location['name'] == name:
                    location['is_default'] = True
                    Logger.info(f"LocationManager: Set '{name}' as default location")
                    return True
            
            Logger.warning(f"LocationManager: Location '{name}' not found")
            return False
            
        except Exception as e:
            Logger.error(f"LocationManager: Error setting default location: {e}")
            return False
    
    def get_location_names(self) -> List[str]:
        """Get list of all saved location names"""
        return [location['name'] for location in self.saved_locations]
    
    def load_location(self, app_state):
        """Load location into app state"""
        try:
            # Try to get current GPS location first
            gps_location = self.get_current_location()
            if gps_location:
                app_state.current_location = gps_location
                Logger.info("LocationManager: Using GPS location")
                return
            
            # Fall back to default saved location
            default_location = self.get_default_location()
            if default_location:
                app_state.current_location = default_location
                Logger.info(f"LocationManager: Using default location: {default_location['name']}")
                return
            
            Logger.warning("LocationManager: No location available")
            
        except Exception as e:
            Logger.error(f"LocationManager: Error loading location: {e}")
    
    def validate_coordinates(self, latitude: str, longitude: str) -> Tuple[bool, str, float, float]:
        """Validate coordinate input"""
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            if not (-90 <= lat <= 90):
                return False, "Latitude must be between -90 and 90 degrees", 0, 0
            
            if not (-180 <= lon <= 180):
                return False, "Longitude must be between -180 and 180 degrees", 0, 0
            
            return True, "Valid coordinates", lat, lon
            
        except ValueError:
            return False, "Invalid number format", 0, 0
        except Exception as e:
            return False, f"Validation error: {e}", 0, 0
    
    def get_location_info(self, location: Dict) -> str:
        """Get formatted location information"""
        try:
            info_parts = []
            
            # Coordinates
            lat_dir = "N" if location['latitude'] >= 0 else "S"
            lon_dir = "E" if location['longitude'] >= 0 else "W"
            info_parts.append(f"{abs(location['latitude']):.3f}°{lat_dir}, {abs(location['longitude']):.3f}°{lon_dir}")
            
            # Timezone
            if 'timezone' in location:
                info_parts.append(f"TZ: {location['timezone']}")
            
            # Bortle index
            if 'bortle_index' in location:
                info_parts.append(f"Bortle: {location['bortle_index']}")
            
            # Altitude limits
            if 'min_altitude' in location and 'max_altitude' in location:
                info_parts.append(f"Alt: {location['min_altitude']}°-{location['max_altitude']}°")
            
            return " | ".join(info_parts)
            
        except Exception as e:
            Logger.error(f"LocationManager: Error formatting location info: {e}")
            return "Location information unavailable"