"""
Analysis package for astronomical observation planning.

This package contains modules for:
- Object selection and scoring
- Filtering and visibility analysis  
- Scheduling and optimization
- Mosaic analysis and grouping
- Report generation
"""

# Analysis and filtering modules
from .object_selection import (
    calculate_object_score, calculate_max_altitude, find_best_objects
)
from .filtering import (
    filter_objects_by_criteria,
    filter_objects_by_altitude_azimuth
)
from .scheduling import (
    generate_observation_schedule, combine_objects_and_groups
)
from .mosaic_analysis import (
    create_mosaic_groups, analyze_mosaic_compatibility
)

# Reporting functions
from .reporting import (
    print_schedule_strategy_report,
    generate_schedule_section_content,
    print_combined_report,
    print_objects_by_type,
    ReportGenerator
)

__all__ = [
    # Object selection functions
    'calculate_object_score', 'calculate_max_altitude', 'find_best_objects',
    # Filtering functions
    'filter_objects_by_criteria',
    # Scheduling functions
    'generate_observation_schedule', 'combine_objects_and_groups',
    # Mosaic analysis functions
    'create_mosaic_groups', 'analyze_mosaic_compatibility',
    # Reporting functions
    'print_schedule_strategy_report',
    'generate_schedule_section_content',
    'print_combined_report',
    'print_objects_by_type',
    'ReportGenerator'
] 