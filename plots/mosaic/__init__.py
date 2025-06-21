"""
Mosaic plotting module for AstroScope.

This module provides comprehensive mosaic plotting functionality for both desktop
and mobile platforms, including trajectory plots, field of view indicators, and
grid layouts for mosaic group visualization.

Desktop Features:
- Advanced mosaic trajectory plots with detailed FOV indicators
- Grid plots for individual group analysis
- Summary plots with statistical overlays
- High-resolution plotting with comprehensive legends

Mobile Features:
- Touch-optimized mosaic plotting with simplified interface
- Group limiting for performance (max 6 groups)
- Mobile-friendly FOV indicators and legends
- Error handling with fallback plots

Usage Examples:
--------------

Desktop mosaic plotting:
    from plots.mosaic import create_mosaic_trajectory_plot, create_mosaic_grid_plot
    
    # Create main trajectory plot
    fig, ax = create_mosaic_trajectory_plot(groups, start_time, end_time)
    
    # Create detailed grid plot
    fig, axes = create_mosaic_grid_plot(groups, start_time, end_time)

Mobile mosaic plotting:
    from plots.mosaic import MobileMosaicPlotter, create_mobile_mosaic_trajectory_plot
    
    # Using the plotter class
    plotter = MobileMosaicPlotter()
    fig = plotter.create_mosaic_trajectory_plot(groups, start_time, end_time)
    
    # Using convenience functions
    fig = create_mobile_mosaic_trajectory_plot(groups, start_time, end_time)

Advanced features:
    from plots.mosaic import analyze_group_visibility_overlap, create_mosaic_summary_plot
    
    # Analyze group overlaps
    analysis = analyze_group_visibility_overlap(groups, start_time, end_time)
    
    # Create summary plot
    fig, ax = create_mosaic_summary_plot(groups, start_time, end_time, analysis)
"""

# Desktop mosaic functions
from .desktop import (
    plot_mosaic_fov_indicator,
    calculate_group_center_position,
    plot_mosaic_group_trajectory,
    plot_mosaic_fov_at_optimal_time,
    create_mosaic_trajectory_plot,
    create_mosaic_grid_plot,
    analyze_group_visibility_overlap,
    create_mosaic_summary_plot
)

# Mobile mosaic functions
from .mobile import (
    MobileMosaicPlotter,
    create_mobile_mosaic_trajectory_plot,
    create_mobile_simple_mosaic_plot,
    create_mobile_mosaic_grid_plot
)

# Submodule access
from . import desktop
from . import mobile

__all__ = [
    # Desktop functions
    'plot_mosaic_fov_indicator',
    'calculate_group_center_position', 
    'plot_mosaic_group_trajectory',
    'plot_mosaic_fov_at_optimal_time',
    'create_mosaic_trajectory_plot',
    'create_mosaic_grid_plot',
    'analyze_group_visibility_overlap',
    'create_mosaic_summary_plot',
    
    # Mobile functions
    'MobileMosaicPlotter',
    'create_mobile_mosaic_trajectory_plot',
    'create_mobile_simple_mosaic_plot',
    'create_mobile_mosaic_grid_plot',
    
    # Submodules
    'desktop',
    'mobile'
]
