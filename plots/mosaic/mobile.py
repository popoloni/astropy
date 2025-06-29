"""
Mobile mosaic plotting functions.

This module provides mobile-optimized mosaic plotting with simplified
interface, touch-friendly controls, and performance optimizations for mobile devices.
"""

import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Ellipse
import numpy as np
import pytz
from datetime import datetime, timedelta
import logging

# Import required functions and constants
from plots.base import setup_altaz_plot
from plots.trajectory.mobile import MobileTrajectoryPlotter
from astronomy import (
    calculate_altaz, is_visible, utc_to_local
)
from config.settings import (
    MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ, GRID_ALPHA
)
from config.settings import MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT, SCOPE_NAME

# Mobile-specific constants
MOBILE_FIGURE_SIZE = (8, 6)
MOBILE_GRID_FIGURE_SIZE = (10, 8)
MOBILE_DPI = 100
MOBILE_FONT_SIZE = 8
MOBILE_TITLE_SIZE = 10
MOBILE_LABEL_SIZE = 9
MAX_MOBILE_GROUPS = 6  # Limit for mobile display
MOBILE_FOV_ALPHA = 0.4
MOBILE_FOV_SMALL_ALPHA = 0.2
MOBILE_BAR_HEIGHT = 0.4

# Colors optimized for mobile screens
MOBILE_GROUP_COLORS = ['#FF4444', '#4444FF', '#44FF44', '#FF44FF', '#FFAA44', '#44FFFF']

class MobileMosaicPlotter:
    """Mobile-optimized mosaic chart plotter"""
    
    def __init__(self):
        """Initialize mobile mosaic plotter with optimized settings"""
        self.figure_size = MOBILE_FIGURE_SIZE
        self.dpi = MOBILE_DPI
        self.font_size = MOBILE_FONT_SIZE
        self.max_groups = MAX_MOBILE_GROUPS
        
        # Configure matplotlib for mobile
        plt.rcParams.update({
            'font.size': self.font_size,
            'axes.titlesize': MOBILE_TITLE_SIZE,
            'axes.labelsize': MOBILE_LABEL_SIZE,
            'xtick.labelsize': self.font_size,
            'ytick.labelsize': self.font_size,
            'legend.fontsize': self.font_size,
            'figure.dpi': self.dpi
        })
        
        logging.info("MobileMosaicPlotter initialized")

    def create_mosaic_trajectory_plot(self, groups, start_time, end_time, title="Mosaic Groups"):
        """
        Create mobile-optimized mosaic trajectory plot.
        
        Parameters:
        -----------
        groups : list
            List of mosaic groups (limited to max_groups for mobile)
        start_time : datetime
            Start time for trajectory window
        end_time : datetime
            End time for trajectory window
        title : str, optional
            Chart title
            
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        try:
            logging.info(f"Creating mobile mosaic trajectory plot for {len(groups)} groups")
            
            # Limit groups for mobile display
            limited_groups = groups[:self.max_groups] if groups else []
            
            if not limited_groups:
                return self._create_error_plot("No mosaic groups available")
            
            # Create figure with mobile settings
            fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
            ax = fig.add_subplot(111)
            
            # Setup mobile-optimized chart
            self._setup_mobile_mosaic_chart(ax, start_time, end_time, title)
            
            # Plot mosaic groups
            self._plot_mobile_mosaic_groups(ax, limited_groups, start_time, end_time)
            
            # Add mobile-friendly legend
            self._add_mobile_mosaic_legend(ax, limited_groups)
            
            # Mobile-specific formatting
            self._apply_mobile_formatting(fig, ax)
            
            logging.info("Mobile mosaic trajectory plot created successfully")
            return fig
            
        except Exception as e:
            logging.error(f"Error creating mobile mosaic trajectory plot: {e}")
            return self._create_error_plot(f"Mosaic plot creation failed: {str(e)}")

    def create_simple_mosaic_plot(self, groups, start_time, end_time, title="Mosaic Groups"):
        """
        Create simplified mosaic plot for mobile with minimal features.
        
        Parameters:
        -----------
        groups : list
            List of mosaic groups
        start_time : datetime
            Start time for trajectory window
        end_time : datetime
            End time for trajectory window
        title : str, optional
            Chart title
            
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        try:
            logging.info(f"Creating simple mobile mosaic plot for {len(groups)} groups")
            
            # Limit groups for mobile display
            limited_groups = groups[:self.max_groups] if groups else []
            
            if not limited_groups:
                return self._create_error_plot("No mosaic groups available")
            
            # Create figure
            fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
            ax = fig.add_subplot(111)
            
            # Simple chart setup
            ax.set_title(title, fontsize=MOBILE_TITLE_SIZE, fontweight='bold')
            ax.set_xlabel('Azimuth (degrees)', fontsize=MOBILE_LABEL_SIZE)
            ax.set_ylabel('Altitude (degrees)', fontsize=MOBILE_LABEL_SIZE)
            ax.set_xlim(MIN_AZ, MAX_AZ)
            ax.set_ylim(MIN_ALT, MAX_ALT)
            ax.grid(True, alpha=GRID_ALPHA)
            
            # Create simple FOV indicators for each group
            for i, group in enumerate(limited_groups):
                color = MOBILE_GROUP_COLORS[i % len(MOBILE_GROUP_COLORS)]
                group_name = self._get_mobile_group_name(group, i + 1)
                
                # Calculate center position at mid-time
                mid_time = start_time + (end_time - start_time) / 2
                center_alt, center_az = self._calculate_mobile_group_center(group, mid_time)
                
                if center_alt is not None and center_az is not None:
                    # Simple FOV indicator
                    fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                                       facecolor=color, edgecolor=color, alpha=MOBILE_FOV_ALPHA,
                                       label=group_name)
                    ax.add_patch(fov_patch)
                    
                    # Add group number
                    ax.text(center_az, center_alt, str(i + 1),
                           ha='center', va='center', fontsize=10, fontweight='bold',
                           color='white', zorder=10)
            
            # Mobile formatting
            self._apply_mobile_formatting(fig, ax)
            
            logging.info("Simple mobile mosaic plot created successfully")
            return fig
            
        except Exception as e:
            logging.error(f"Error creating simple mobile mosaic plot: {e}")
            return self._create_error_plot(f"Simple mosaic plot failed: {str(e)}")

    def create_mosaic_grid_plot(self, groups, start_time, end_time):
        """
        Create mobile-optimized grid plot for mosaic groups.
        
        Parameters:
        -----------
        groups : list
            List of mosaic groups
        start_time : datetime
            Start time for trajectory window
        end_time : datetime
            End time for trajectory window
            
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        try:
            logging.info(f"Creating mobile mosaic grid plot for {len(groups)} groups")
            
            # Limit groups for mobile display
            limited_groups = groups[:self.max_groups] if groups else []
            
            if not limited_groups:
                return self._create_error_plot("No mosaic groups available")
            
            n_groups = len(limited_groups)
            
            # Calculate grid dimensions (optimized for mobile)
            cols = min(2, n_groups)  # Maximum 2 columns for mobile
            rows = math.ceil(n_groups / cols)
            
            # Create subplot grid
            fig, axes = plt.subplots(rows, cols, figsize=MOBILE_GRID_FIGURE_SIZE, dpi=self.dpi)
            if n_groups == 1:
                axes = [axes]
            elif rows == 1:
                axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
            else:
                axes = axes.flatten()
            
            for i, group in enumerate(limited_groups):
                ax = axes[i]
                color = MOBILE_GROUP_COLORS[i % len(MOBILE_GROUP_COLORS)]
                group_number = i + 1
                
                # Setup this subplot
                ax.set_xlim(MIN_AZ, MAX_AZ)
                ax.set_ylim(MIN_ALT, MAX_ALT)
                ax.set_xlabel('Az (°)', fontsize=MOBILE_FONT_SIZE)
                ax.set_ylabel('Alt (°)', fontsize=MOBILE_FONT_SIZE)
                ax.grid(True, alpha=GRID_ALPHA)
                ax.tick_params(labelsize=MOBILE_FONT_SIZE - 1)
                
                # Plot simplified group representation
                self._plot_mobile_group_simple(ax, group, start_time, end_time, color, group_number)
                
                # Add group title
                group_name = self._get_mobile_group_name(group, group_number)
                ax.set_title(group_name, fontsize=MOBILE_FONT_SIZE, fontweight='bold', pad=5)
            
            # Hide unused subplots
            for i in range(n_groups, len(axes)):
                axes[i].set_visible(False)
            
            # Overall title
            fig.suptitle(f'Mosaic Groups - {start_time.date()}', 
                        fontsize=MOBILE_TITLE_SIZE, fontweight='bold')
            
            plt.tight_layout()
            
            logging.info("Mobile mosaic grid plot created successfully")
            return fig
            
        except Exception as e:
            logging.error(f"Error creating mobile mosaic grid plot: {e}")
            return self._create_error_plot(f"Grid plot failed: {str(e)}")

    def _setup_mobile_mosaic_chart(self, ax, start_time, end_time, title):
        """Setup mobile-optimized mosaic chart axes and formatting"""
        ax.set_title(title, fontsize=MOBILE_TITLE_SIZE, fontweight='bold')
        ax.set_xlabel('Azimuth (degrees)', fontsize=MOBILE_LABEL_SIZE)
        ax.set_ylabel('Altitude (degrees)', fontsize=MOBILE_LABEL_SIZE)
        ax.set_xlim(MIN_AZ, MAX_AZ)
        ax.set_ylim(MIN_ALT, MAX_ALT)
        ax.grid(True, alpha=GRID_ALPHA)
        ax.tick_params(labelsize=self.font_size)

    def _plot_mobile_mosaic_groups(self, ax, groups, start_time, end_time):
        """Plot mosaic groups with mobile optimizations"""
        for i, group in enumerate(groups):
            color = MOBILE_GROUP_COLORS[i % len(MOBILE_GROUP_COLORS)]
            group_number = i + 1
            
            # Get overlap periods
            overlap_periods = group.overlap_periods if hasattr(group, 'overlap_periods') else []
            
            # Plot simplified trajectory for mobile
            self._plot_mobile_group_trajectory(ax, group, start_time, end_time, color, group_number)
            
            # Plot FOV indicator at optimal time
            self._plot_mobile_fov_at_optimal_time(ax, group, overlap_periods, color)

    def _plot_mobile_group_trajectory(self, ax, group, start_time, end_time, color, group_number):
        """Plot simplified group trajectory for mobile"""
        objects = group.objects if hasattr(group, 'objects') else group
        
        # Plot only the center trajectory for mobile (simplified)
        times = []
        alts = []
        azs = []
        
        current_time = start_time
        time_step = (end_time - start_time) / 20  # Reduced points for mobile
        
        while current_time <= end_time:
            center_alt, center_az = self._calculate_mobile_group_center(group, current_time)
            if center_alt is not None and center_az is not None:
                times.append(current_time)
                alts.append(center_alt)
                azs.append(center_az)
            current_time += time_step
        
        if azs:
            # Plot simplified trajectory
            group_name = self._get_mobile_group_name(group, group_number)
            ax.plot(azs, alts, '-', color=color, linewidth=2, alpha=0.8, label=group_name)

    def _plot_mobile_fov_at_optimal_time(self, ax, group, overlap_periods, color):
        """Plot mobile-optimized FOV indicator"""
        if not overlap_periods:
            return
        
        # Find the middle of the longest overlap period
        longest_period = max(overlap_periods, key=lambda p: (p[1] - p[0]).total_seconds())
        mid_time = longest_period[0] + (longest_period[1] - longest_period[0]) / 2
        
        # Calculate the center position
        center_alt, center_az = self._calculate_mobile_group_center(group, mid_time)
        
        if center_alt is not None and center_az is not None:
            # Mobile FOV indicator
            fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                               facecolor=color, edgecolor=color, alpha=MOBILE_FOV_SMALL_ALPHA,
                               linestyle='--', linewidth=1)
            ax.add_patch(fov_patch)

    def _plot_mobile_group_simple(self, ax, group, start_time, end_time, color, group_number):
        """Plot simplified group representation for grid plots"""
        # Calculate center position at mid-time
        mid_time = start_time + (end_time - start_time) / 2
        center_alt, center_az = self._calculate_mobile_group_center(group, mid_time)
        
        if center_alt is not None and center_az is not None:
            # Simple FOV indicator
            fov_patch = Ellipse((center_az, center_alt), MOSAIC_FOV_WIDTH, MOSAIC_FOV_HEIGHT,
                               facecolor=color, edgecolor=color, alpha=MOBILE_FOV_ALPHA,
                               linewidth=1)
            ax.add_patch(fov_patch)
            
            # Add group number
            ax.text(center_az, center_alt, str(group_number),
                   ha='center', va='center', fontsize=MOBILE_FONT_SIZE, fontweight='bold',
                   color='white', zorder=10)

    def _calculate_mobile_group_center(self, group, time):
        """Calculate group center position for mobile (simplified)"""
        altitudes = []
        azimuths = []
        
        # Handle both MosaicGroup and list of objects
        objects = group.objects if hasattr(group, 'objects') else group
        
        for obj in objects:
            alt, az = calculate_altaz(obj, time)
            if is_visible(alt, az, use_margins=True):
                altitudes.append(alt)
                azimuths.append(az)
        
        if altitudes and azimuths:
            return sum(altitudes) / len(altitudes), sum(azimuths) / len(azimuths)
        return None, None

    def _add_mobile_mosaic_legend(self, ax, groups):
        """Add mobile-friendly legend for mosaic groups"""
        handles, labels = ax.get_legend_handles_labels()
        
        if handles:
            # Simplified legend for mobile
            ax.legend(handles, labels, loc='upper right', fontsize=self.font_size - 1,
                     framealpha=0.9, fancybox=True, shadow=True)

    def _apply_mobile_formatting(self, fig, ax):
        """Apply mobile-specific formatting"""
        # Adjust layout for mobile
        fig.tight_layout(pad=1.0)
        
        # Optimize tick spacing for mobile
        ax.tick_params(labelsize=self.font_size - 1)
        
        # Ensure text is readable on mobile
        for text in ax.texts:
            if hasattr(text, 'set_fontsize'):
                text.set_fontsize(max(self.font_size - 1, 6))

    def _get_mobile_group_name(self, group, group_number):
        """Get abbreviated group name for mobile display"""
        objects = group.objects if hasattr(group, 'objects') else group
        
        if len(objects) == 1:
            return f"G{group_number}: {self._get_mobile_object_name(objects[0])}"
        elif len(objects) == 2:
            names = [self._get_mobile_object_name(obj) for obj in objects[:2]]
            return f"G{group_number}: {', '.join(names)}"
        else:
            names = [self._get_mobile_object_name(obj) for obj in objects[:2]]
            return f"G{group_number}: {', '.join(names)} +{len(objects)-2}"

    def _get_mobile_object_name(self, obj):
        """Get mobile-friendly object name (abbreviated)"""
        name = obj.name if hasattr(obj, 'name') else str(obj)
        
        # Abbreviate long names for mobile
        if len(name) > 8:
            # Try to extract catalog number
            import re
            match = re.search(r'(M|NGC|IC)\s*(\d+)', name)
            if match:
                return f"{match.group(1)}{match.group(2)}"
            else:
                return name[:8]
        return name

    def _create_error_plot(self, error_message):
        """Create error plot for mobile"""
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        ax = fig.add_subplot(111)
        
        ax.text(0.5, 0.5, f"Error:\n{error_message}", 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=self.font_size, color='red',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title("Mosaic Plot Error", fontsize=MOBILE_TITLE_SIZE, color='red')
        ax.axis('off')
        
        return fig

# Convenience functions for mobile mosaic plotting
def create_mobile_mosaic_trajectory_plot(groups, start_time, end_time, title="Mosaic Groups"):
    """
    Convenience function to create mobile mosaic trajectory plot.
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups
    start_time : datetime
        Start time for trajectory window
    end_time : datetime
        End time for trajectory window
    title : str, optional
        Chart title
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    plotter = MobileMosaicPlotter()
    return plotter.create_mosaic_trajectory_plot(groups, start_time, end_time, title)

def create_mobile_simple_mosaic_plot(groups, start_time, end_time, title="Mosaic Groups"):
    """
    Convenience function to create simple mobile mosaic plot.
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups
    start_time : datetime
        Start time for trajectory window
    end_time : datetime
        End time for trajectory window
    title : str, optional
        Chart title
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    plotter = MobileMosaicPlotter()
    return plotter.create_simple_mosaic_plot(groups, start_time, end_time, title)

def create_mobile_mosaic_grid_plot(groups, start_time, end_time):
    """
    Convenience function to create mobile mosaic grid plot.
    
    Parameters:
    -----------
    groups : list
        List of mosaic groups
    start_time : datetime
        Start time for trajectory window
    end_time : datetime
        End time for trajectory window
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    plotter = MobileMosaicPlotter()
    return plotter.create_mosaic_grid_plot(groups, start_time, end_time) 