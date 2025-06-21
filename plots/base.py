"""
Base plotting utilities for AstroScope application.
This module provides common plotting functions and configurations used across different plot types.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
from typing import Tuple, Optional, Dict, Any
import logging

# Import configuration constants
from config.settings import (
    COLOR_MAP, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, 
    FIGURE_SIZE, GRID_ALPHA, VISIBLE_REGION_ALPHA
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common plot configurations
DEFAULT_FIGURE_SIZE = (10, 8)
DEFAULT_DPI = 100
DEFAULT_FONT_SIZE = 12

class PlotConfig:
    """Configuration class for plot settings."""
    def __init__(self, 
                 figure_size: Tuple[int, int] = DEFAULT_FIGURE_SIZE,
                 dpi: int = DEFAULT_DPI,
                 font_size: int = DEFAULT_FONT_SIZE,
                 style: str = 'default'):
        self.figure_size = figure_size
        self.dpi = dpi
        self.font_size = font_size
        self.style = style

def setup_plot(config: Optional[PlotConfig] = None) -> Tuple[Figure, plt.Axes]:
    """
    Set up a basic plot with common configurations.
    
    Args:
        config: PlotConfig object with plot settings
        
    Returns:
        Tuple of (Figure, Axes) objects
    """
    if config is None:
        config = PlotConfig()
    
    plt.style.use(config.style)
    fig = plt.figure(figsize=config.figure_size, dpi=config.dpi)
    ax = fig.add_subplot(111)
    
    # Set common properties
    ax.tick_params(labelsize=config.font_size)
    plt.rcParams['font.size'] = config.font_size
    
    return fig, ax

def setup_altaz_plot(config: Optional[PlotConfig] = None) -> Tuple[Figure, plt.Axes]:
    """
    Setup basic altitude-azimuth plot matching the legacy implementation.
    
    Args:
        config: PlotConfig object with plot settings
        
    Returns:
        Tuple of (Figure, Axes) objects
    """
    # Create figure with appropriate size
    fig = plt.figure(figsize=FIGURE_SIZE)  # Use config FIGURE_SIZE
    
    # Use GridSpec for better control over spacing
    gs = fig.add_gridspec(1, 1)
    # Adjust margins to accommodate axis labels and legend
    gs.update(left=0.1, right=0.85, top=0.95, bottom=0.1)
    
    ax = fig.add_subplot(gs[0, 0])
    
    # Set axis limits and labels using config constants with margins
    ax.set_xlim(MIN_AZ-10, MAX_AZ+10)
    ax.set_ylim(MIN_ALT-10, MAX_ALT+10)
    ax.set_xlabel('Azimuth (degrees)')
    ax.set_ylabel('Altitude (degrees)')
    ax.grid(True, alpha=GRID_ALPHA)
    
    # Add visible region rectangle
    visible_region = Rectangle((MIN_AZ, MIN_ALT), 
                             MAX_AZ - MIN_AZ, 
                             MAX_ALT - MIN_ALT,
                             facecolor='green', 
                             alpha=VISIBLE_REGION_ALPHA,
                             label='Visible Region')
    ax.add_patch(visible_region)
    
    # Configure grid with major and minor ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    
    return fig, ax

def save_plot(fig: Figure, 
             filename: str, 
             dpi: int = DEFAULT_DPI,
             bbox_inches: str = 'tight',
             **kwargs) -> None:
    """
    Save a plot to a file with consistent settings.
    
    Args:
        fig: Matplotlib Figure object
        filename: Output filename
        dpi: DPI for the output image
        bbox_inches: Bounding box setting
        **kwargs: Additional arguments for plt.savefig
    """
    try:
        fig.savefig(filename, 
                   dpi=dpi,
                   bbox_inches=bbox_inches,
                   **kwargs)
        logger.info(f"Plot saved successfully to {filename}")
    except Exception as e:
        logger.error(f"Error saving plot to {filename}: {str(e)}")
        raise

def get_color_cycle(n_colors: int) -> np.ndarray:
    """
    Get a color cycle for plotting multiple items.
    
    Args:
        n_colors: Number of colors needed
        
    Returns:
        Array of colors
    """
    return plt.get_cmap(COLOR_MAP)(np.linspace(0, 1, n_colors))

def format_time_axis(ax: plt.Axes, 
                    times: np.ndarray,
                    time_format: str = '%H:%M') -> None:
    """
    Format the time axis with proper labels and ticks.
    
    Args:
        ax: Matplotlib Axes object
        times: Array of time values
        time_format: Format string for time labels
    """
    from matplotlib.dates import DateFormatter
    ax.xaxis.set_major_formatter(DateFormatter(time_format))
    plt.xticks(rotation=45)
