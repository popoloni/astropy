"""
Visualization package for astronomical plotting and charting.

This package contains modules for:
- Trajectory plotting and chart generation
- Visibility charts and timeline plots
- Mosaic visualization and FOV plotting
- Plot formatting and legend management
"""

# Import main plotting functions
from .plotting import (
    setup_altaz_plot, finalize_plot_legend, get_abbreviated_name,
    plot_object_trajectory, plot_moon_trajectory, plot_visibility_chart,
    plot_quarterly_trajectories
)

from .mosaic_plots import (
    plot_mosaic_fov_indicator, calculate_group_center_position,
    plot_mosaic_group_trajectory, create_mosaic_trajectory_plot,
    create_mosaic_grid_plot
)

from .chart_utils import (
    find_optimal_label_position, calculate_label_offset,
    _get_sorted_objects_for_chart, _setup_visibility_chart_axes
)
