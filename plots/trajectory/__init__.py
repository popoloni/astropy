"""
Trajectory plotting module for AstroScope application.
This module provides trajectory plotting functions for both desktop and mobile platforms.
"""

from .desktop import (
    plot_object_trajectory,
    plot_moon_trajectory,
    plot_quarterly_trajectories
)

from .mobile import (
    MobileTrajectoryPlotter,
    create_mobile_trajectory_plot,
    create_mobile_simple_plot,
    create_mobile_multi_plot
)

__all__ = [
    # Desktop functions
    "plot_object_trajectory",
    "plot_moon_trajectory", 
    "plot_quarterly_trajectories",
    
    # Mobile functions
    "MobileTrajectoryPlotter",
    "create_mobile_trajectory_plot",
    "create_mobile_simple_plot",
    "create_mobile_multi_plot"
]
