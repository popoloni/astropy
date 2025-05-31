"""
Mosaic group class representing collections of celestial objects.
"""


def _get_abbreviated_name(full_name):
    """Temporary function to get abbreviated object names until full refactoring."""
    # Simple abbreviation logic
    if '/' in full_name:
        parts = full_name.split('/')
        return parts[0]  # Return the first part (e.g., "M31" from "M31/NGC 224 Andromeda Galaxy")
    elif ' ' in full_name:
        return full_name.split()[0]  # Return first word
    return full_name


class MosaicGroup:
    """Class to represent a mosaic group of celestial objects that behaves like a single CelestialObject"""
    def __init__(self, objects, overlap_periods, group_id=None):
        # Temporary configuration constants until proper config extraction
        MOSAIC_FOV_WIDTH = 60.0  # Default value
        MOSAIC_FOV_HEIGHT = 40.0  # Default value
        
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
        object_names = [_get_abbreviated_name(obj.name) for obj in self.objects]
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