"""
AstroScope Plotting Module

This module provides comprehensive plotting utilities for the AstroScope application,
supporting both desktop and mobile platforms.
"""

from .base import (
    PlotConfig,
    setup_plot,
    setup_altaz_plot,
    save_plot,
    get_color_cycle,
    format_time_axis
)

from .trajectory import (
    plot_object_trajectory,
    plot_moon_trajectory,
    plot_quarterly_trajectories,
    MobileTrajectoryPlotter,
    create_mobile_trajectory_plot,
    create_mobile_simple_plot,
    create_mobile_multi_plot
)

from .visibility import (
    plot_visibility_chart,
    create_mosaic_visibility_chart,
    MobileVisibilityPlotter,
    create_mobile_visibility_chart,
    create_mobile_simple_visibility_chart,
    create_mobile_multi_object_chart
)

from .mosaic import (
    plot_mosaic_fov_indicator,
    calculate_group_center_position,
    plot_mosaic_group_trajectory,
    plot_mosaic_fov_at_optimal_time,
    create_mosaic_trajectory_plot,
    create_mosaic_grid_plot,
    analyze_group_visibility_overlap,
    create_mosaic_summary_plot,
    MobileMosaicPlotter,
    create_mobile_mosaic_trajectory_plot,
    create_mobile_simple_mosaic_plot,
    create_mobile_mosaic_grid_plot
)

from .weekly import (
    plot_weekly_analysis,
    create_weekly_comparison_plot,
    create_weekly_statistics_plot,
    create_weekly_summary_table_plot,
    MobileWeeklyPlotter,
    create_mobile_weekly_analysis_plot,
    create_mobile_simple_weekly_plot,
    create_mobile_weekly_summary_plot,
    plot_weekly_analysis_mobile
)

from .constellation import (
    ConstellationPlotter,
    plot_constellation_map,
    plot_constellation_stars,
    plot_constellation_lines,
    plot_deep_sky_objects,
    plot_nebula_paths
)

from .utils import (
    PlotVerifier,
    get_abbreviated_name,
    calculate_label_offset,
    find_optimal_label_position,
    format_time_range,
    calculate_overlap_duration,
    validate_groups_for_plotting,
    create_color_palette,
    finalize_plot_legend
)

__version__ = "1.0.0"
__all__ = [
    # Base functions
    "PlotConfig",
    "setup_plot", 
    "setup_altaz_plot",
    "save_plot",
    "get_color_cycle",
    "format_time_axis",
    
    # Trajectory functions
    "plot_object_trajectory",
    "plot_moon_trajectory",
    "plot_quarterly_trajectories",
    "MobileTrajectoryPlotter",
    "create_mobile_trajectory_plot",
    "create_mobile_simple_plot",
    "create_mobile_multi_plot",
    
    # Visibility functions
    "plot_visibility_chart",
    "create_mosaic_visibility_chart",
    "MobileVisibilityPlotter",
    "create_mobile_visibility_chart",
    "create_mobile_simple_visibility_chart",
    "create_mobile_multi_object_chart",
    
    # Mosaic functions
    "plot_mosaic_fov_indicator",
    "calculate_group_center_position",
    "plot_mosaic_group_trajectory",
    "plot_mosaic_fov_at_optimal_time",
    "create_mosaic_trajectory_plot",
    "create_mosaic_grid_plot",
    "analyze_group_visibility_overlap",
    "create_mosaic_summary_plot",
    "MobileMosaicPlotter",
    "create_mobile_mosaic_trajectory_plot",
    "create_mobile_simple_mosaic_plot",
    "create_mobile_mosaic_grid_plot",
    
    # Weekly analysis functions
    "plot_weekly_analysis",
    "create_weekly_comparison_plot",
    "create_weekly_statistics_plot",
    "create_weekly_summary_table_plot",
    "MobileWeeklyPlotter",
    "create_mobile_weekly_analysis_plot",
    "create_mobile_simple_weekly_plot",
    "create_mobile_weekly_summary_plot",
    "plot_weekly_analysis_mobile",
    
    # Constellation functions
    "ConstellationPlotter",
    "plot_constellation_map",
    "plot_constellation_stars",
    "plot_constellation_lines",
    "plot_deep_sky_objects",
    "plot_nebula_paths",
    
    # Utility functions
    "get_abbreviated_name",
    "calculate_label_offset",
    "find_optimal_label_position",
    "format_time_range",
    "calculate_overlap_duration",
    "validate_groups_for_plotting",
    "create_color_palette",
    "finalize_plot_legend",
    
    # Verification
    "PlotVerifier"
]
