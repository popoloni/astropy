"""
Mobile trajectory plotting functions for AstroScope application.
This module provides trajectory plotting functions optimized for mobile display.
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta, datetime
import pytz
from typing import List, Tuple, Optional, Any
import logging

from ..base import setup_plot, PlotConfig
from astronomy import (
    calculate_altaz, calculate_moon_position, is_visible, 
    utc_to_local
)
from .desktop import get_abbreviated_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mobile-specific constants
MOBILE_FIGURE_SIZE = (8, 6)
MOBILE_DPI = 100
MOBILE_FONT_SIZE = 10
MOBILE_MARKER_SIZE = 4
MOBILE_LINE_WIDTH = 1.5

class MobileTrajectoryPlotter:
    """Mobile-optimized trajectory plotting class"""
    
    def __init__(self):
        self.figure_size = MOBILE_FIGURE_SIZE
        self.dpi = MOBILE_DPI
        self.style_config = {
            'font.size': MOBILE_FONT_SIZE,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        }
        
    def configure_mobile_style(self):
        """Configure matplotlib for mobile display"""
        plt.rcParams.update(self.style_config)
        plt.style.use('default')
        
    def create_trajectory_plot(self, target, start_time=None, end_time=None):
        """Create trajectory plot for a single target optimized for mobile"""
        try:
            logger.info(f"Creating mobile trajectory plot for {getattr(target, 'name', 'Unknown')}")
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
            
            # Create mobile-optimized plot
            config = PlotConfig(
                figure_size=self.figure_size,
                dpi=self.dpi,
                font_size=MOBILE_FONT_SIZE
            )
            fig, ax = setup_plot(config)
            
            # Plot trajectory with mobile optimizations
            self._plot_mobile_trajectory(ax, target, start_time, end_time)
            
            # Mobile-specific formatting
            target_name = getattr(target, 'name', 'Target')
            ax.set_title(f"Trajectory: {target_name}", fontsize=12, pad=20)
            ax.set_xlabel('Azimuth (degrees)', fontsize=10)
            ax.set_ylabel('Altitude (degrees)', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Optimize for mobile viewing
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating mobile trajectory plot: {str(e)}")
            return self._create_error_plot("Trajectory Plot", f"Error: {str(e)}")
    
    def create_simple_trajectory_plot(self, target, start_time=None, end_time=None):
        """Create simplified trajectory plot for mobile with reduced detail"""
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
            
            config = PlotConfig(
                figure_size=self.figure_size,
                dpi=self.dpi,
                font_size=MOBILE_FONT_SIZE
            )
            fig, ax = setup_plot(config)
            
            # Simplified trajectory calculation
            times = []
            alts = []
            azs = []
            
            # Use larger time intervals for mobile (every 15 minutes)
            current_time = start_time
            while current_time <= end_time:
                alt, az = calculate_altaz(target, current_time)
                if alt > 0:  # Only plot when above horizon
                    times.append(current_time)
                    alts.append(alt)
                    azs.append(az)
                current_time += timedelta(minutes=15)
            
            if azs:
                # Plot simplified trajectory
                ax.plot(azs, alts, '-', color='blue', linewidth=MOBILE_LINE_WIDTH, 
                       label=get_abbreviated_name(target.name))
                
                # Add fewer hour markers for mobile
                hour_indices = range(0, len(times), 4)  # Every hour
                for i in hour_indices:
                    if i < len(times):
                        local_time = utc_to_local(times[i])
                        ax.plot(azs[i], alts[i], 'o', color='blue', 
                               markersize=MOBILE_MARKER_SIZE)
                        ax.annotate(f'{local_time.hour:02d}h', 
                                   (azs[i], alts[i]),
                                   xytext=(3, 3),
                                   textcoords='offset points',
                                   fontsize=8,
                                   color='blue')
            
            # Mobile-specific formatting
            target_name = getattr(target, 'name', 'Target')
            ax.set_title(f"{get_abbreviated_name(target_name)}", fontsize=12)
            ax.set_xlabel('Az (°)', fontsize=10)
            ax.set_ylabel('Alt (°)', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=9)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            logger.error(f"Error creating simple trajectory plot: {str(e)}")
            return self._create_error_plot("Trajectory", f"Error: {str(e)}")
    
    def create_multi_target_plot(self, targets, start_time=None, end_time=None):
        """Create trajectory plot for multiple targets optimized for mobile"""
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
            
            # Limit number of targets for mobile display
            max_targets = 5
            if len(targets) > max_targets:
                targets = targets[:max_targets]
                logger.warning(f"Limited to {max_targets} targets for mobile display")
            
            config = PlotConfig(
                figure_size=self.figure_size,
                dpi=self.dpi,
                font_size=MOBILE_FONT_SIZE
            )
            fig, ax = setup_plot(config)
            
            # Generate colors for targets
            colors = plt.cm.Set1(np.linspace(0, 1, len(targets)))
            
            # Plot each target with mobile optimizations
            for target, color in zip(targets, colors):
                self._plot_mobile_trajectory_simple(ax, target, start_time, end_time, color)
            
            # Mobile-specific formatting
            ax.set_title(f"Trajectories ({len(targets)} targets)", fontsize=12)
            ax.set_xlabel('Az (°)', fontsize=10)
            ax.set_ylabel('Alt (°)', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Compact legend for mobile
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            logger.error(f"Error creating multi-target plot: {str(e)}")
            return self._create_error_plot("Multi-Target", f"Error: {str(e)}")
    
    def _plot_mobile_trajectory(self, ax, target, start_time, end_time):
        """Plot trajectory optimized for mobile display"""
        times = []
        alts = []
        azs = []
        hour_times = []
        hour_alts = []
        hour_azs = []
        
        # Use 5-minute intervals for mobile (balance between smoothness and performance)
        current_time = start_time
        while current_time <= end_time:
            alt, az = calculate_altaz(target, current_time)
            if alt > 0:  # Only plot when above horizon
                times.append(current_time)
                alts.append(alt)
                azs.append(az)
                
                # Mark every 2 hours for mobile
                local_time = utc_to_local(current_time)
                if local_time.minute == 0 and local_time.hour % 2 == 0:
                    hour_times.append(local_time)
                    hour_alts.append(alt)
                    hour_azs.append(az)
                    
            current_time += timedelta(minutes=5)
        
        if azs:
            # Plot trajectory
            ax.plot(azs, alts, '-', color='blue', linewidth=MOBILE_LINE_WIDTH, 
                   label=get_abbreviated_name(target.name))
            
            # Add hour markers (reduced frequency for mobile)
            for t, az, alt in zip(hour_times, hour_azs, hour_alts):
                ax.plot(az, alt, 'o', color='blue', markersize=MOBILE_MARKER_SIZE)
                ax.annotate(f'{t.hour:02d}h', 
                           (az, alt),
                           xytext=(3, 3),
                           textcoords='offset points',
                           fontsize=8,
                           color='blue')
    
    def _plot_mobile_trajectory_simple(self, ax, target, start_time, end_time, color):
        """Plot simplified trajectory for multi-target mobile display"""
        times = []
        alts = []
        azs = []
        
        # Use 10-minute intervals for multi-target mobile display
        current_time = start_time
        while current_time <= end_time:
            alt, az = calculate_altaz(target, current_time)
            if alt > 0:  # Only plot when above horizon
                times.append(current_time)
                alts.append(alt)
                azs.append(az)
            current_time += timedelta(minutes=10)
        
        if azs:
            # Plot simplified trajectory (no hour markers for multi-target)
            abbreviated_name = get_abbreviated_name(target.name)
            ax.plot(azs, alts, '-', color=color, linewidth=MOBILE_LINE_WIDTH, 
                   label=abbreviated_name, alpha=0.8)
    
    def _create_error_plot(self, title, message):
        """Create error plot for mobile display"""
        self.configure_mobile_style()
        
        config = PlotConfig(
            figure_size=self.figure_size,
            dpi=self.dpi,
            font_size=MOBILE_FONT_SIZE
        )
        fig, ax = setup_plot(config)
        
        ax.text(0.5, 0.5, message, 
               transform=ax.transAxes,
               ha='center', va='center',
               fontsize=12,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.8))
        
        ax.set_title(title, fontsize=14)
        ax.set_xlabel('Azimuth (degrees)', fontsize=10)
        ax.set_ylabel('Altitude (degrees)', fontsize=10)
        
        return fig

def create_mobile_trajectory_plot(target, start_time=None, end_time=None):
    """Convenience function to create mobile trajectory plot"""
    plotter = MobileTrajectoryPlotter()
    return plotter.create_trajectory_plot(target, start_time, end_time)

def create_mobile_simple_plot(target, start_time=None, end_time=None):
    """Convenience function to create simple mobile trajectory plot"""
    plotter = MobileTrajectoryPlotter()
    return plotter.create_simple_trajectory_plot(target, start_time, end_time)

def create_mobile_multi_plot(targets, start_time=None, end_time=None):
    """Convenience function to create multi-target mobile plot"""
    plotter = MobileTrajectoryPlotter()
    return plotter.create_multi_target_plot(targets, start_time, end_time) 