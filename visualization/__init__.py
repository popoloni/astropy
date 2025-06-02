"""
Visualization package for astronomical plotting and charting.

This package contains modules for:
- Trajectory plotting and chart generation
- Plot formatting and legend management
"""

# Import main plotting functions
from .plotting import (
    setup_altaz_plot, finalize_plot_legend, get_abbreviated_name,
    plot_moon_trajectory
)
