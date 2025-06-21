#!/usr/bin/env python3
"""
Constellation plotting module

Provides matplotlib and SVG-based constellation visualization capabilities.
"""

from .desktop import (
    ConstellationPlotter,
    plot_constellation_map,
    plot_constellation_stars,
    plot_constellation_lines,
    plot_deep_sky_objects,
    plot_nebula_paths,
    create_constellation_legend
)

# SVG functionality now available as shared module
try:
    from .svg import (
        VectorConfig,
        ObjectStats,
        PythonistaWebView,
        MacOSBrowserView,
        coord_to_svg,
        create_svg_output,
        plot_stars_svg,
        plot_constellation_lines_svg,
        plot_bright_stars_svg,
        plot_dso_objects_svg,
        plot_nebula_paths_svg,
        calculate_bounds
    )
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

__all__ = [
    'ConstellationPlotter',
    'plot_constellation_map',
    'plot_constellation_stars',
    'plot_constellation_lines',
    'plot_deep_sky_objects',
    'plot_nebula_paths',
    'create_constellation_legend'
]

if SVG_AVAILABLE:
    __all__.extend([
        'VectorConfig',
        'ObjectStats', 
        'PythonistaWebView',
        'MacOSBrowserView',
        'coord_to_svg',
        'create_svg_output',
        'plot_stars_svg',
        'plot_constellation_lines_svg',
        'plot_bright_stars_svg',
        'plot_dso_objects_svg',
        'plot_nebula_paths_svg',
        'calculate_bounds'
    ]) 