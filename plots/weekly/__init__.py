"""
Weekly analysis plotting module for AstroScope.

This module provides comprehensive weekly analysis plotting functionality
for both desktop and mobile platforms.

Desktop Features:
- Comprehensive 6-panel weekly analysis plots
- Statistical analysis and comparison charts
- High-resolution plotting for detailed analysis
- Advanced correlation analysis

Mobile Features:
- Touch-optimized weekly analysis plots
- Simplified layouts for mobile screens
- Performance optimizations
- Week limiting for mobile performance

Usage:
    from plots.weekly import plot_weekly_analysis
    from plots.weekly import create_mobile_weekly_analysis_plot
    from plots.weekly.desktop import create_weekly_statistics_plot
    from plots.weekly.mobile import MobileWeeklyPlotter
"""

# Import desktop functions
from .desktop import (
    plot_weekly_analysis,
    create_weekly_comparison_plot,
    create_weekly_statistics_plot,
    create_weekly_summary_table_plot
)

# Import mobile functions
from .mobile import (
    MobileWeeklyPlotter,
    create_mobile_weekly_analysis_plot,
    create_mobile_simple_weekly_plot,
    create_mobile_weekly_summary_plot,
    plot_weekly_analysis_mobile
)

# Main exports - desktop functions by default
__all__ = [
    # Desktop functions (primary)
    'plot_weekly_analysis',
    'create_weekly_comparison_plot', 
    'create_weekly_statistics_plot',
    'create_weekly_summary_table_plot',
    
    # Mobile functions
    'MobileWeeklyPlotter',
    'create_mobile_weekly_analysis_plot',
    'create_mobile_simple_weekly_plot', 
    'create_mobile_weekly_summary_plot',
    'plot_weekly_analysis_mobile'
]

# Version info
__version__ = '1.0.0'
__author__ = 'AstroScope Development Team'
