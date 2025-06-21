"""
Visibility chart plotting module.

This module provides both desktop and mobile visibility chart plotting functions
for astronomical object visibility analysis.

Desktop functions provide comprehensive features including:
- Advanced scheduling visualization
- Moon interference detection
- Detailed object analysis
- High-resolution plotting

Mobile functions provide optimized features including:
- Touch-friendly interface
- Simplified visualization
- Performance optimization
- Reduced data display

Usage:
    # Desktop visibility charts
    from plots.visibility import plot_visibility_chart, create_mosaic_visibility_chart
    
    # Mobile visibility charts  
    from plots.visibility import MobileVisibilityPlotter, create_mobile_visibility_chart
    
    # Create desktop chart
    fig, ax = plot_visibility_chart(objects, start_time, end_time, schedule)
    
    # Create mobile chart
    fig = create_mobile_visibility_chart(objects, start_time, end_time)
"""

# Import desktop functions
from .desktop import (
    plot_visibility_chart,
    create_mosaic_visibility_chart
)

# Import mobile functions
from .mobile import (
    MobileVisibilityPlotter,
    create_mobile_visibility_chart,
    create_mobile_simple_visibility_chart,
    create_mobile_multi_object_chart
)

# Import submodules for direct access
from . import desktop
from . import mobile

__all__ = [
    # Desktop functions
    'plot_visibility_chart',
    'create_mosaic_visibility_chart',
    
    # Mobile functions
    'MobileVisibilityPlotter',
    'create_mobile_visibility_chart',
    'create_mobile_simple_visibility_chart',
    'create_mobile_multi_object_chart',
    
    # Submodules
    'desktop',
    'mobile'
]

__version__ = "1.0.0"
