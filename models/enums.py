"""
Enums used throughout the astropy application.
"""

from enum import Enum


class SchedulingStrategy(Enum):
    """Enumeration of different scheduling strategies for observation planning."""
    LONGEST_DURATION = "longest_duration"  # Current strategy: prioritize longest visibility
    MAX_OBJECTS = "max_objects"           # Maximum number of objects
    OPTIMAL_SNR = "optimal_snr"           # Best imaging conditions
    MINIMAL_MOSAIC = "minimal_mosaic"     # Fewer panels needed
    DIFFICULTY_BALANCED = "difficulty_balanced"  # Mix of easy and challenging
    MOSAIC_GROUPS = "mosaic_groups"       # Prioritize mosaic groups over individual objects 