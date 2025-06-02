"""
Mobile Plotting Utilities
Matplotlib integration for Kivy mobile app with touch-optimized plots
"""

import os
import sys
import io
import tempfile
from datetime import datetime, timedelta
from kivy.logger import Logger

# Matplotlib backend configuration for mobile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for mobile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from astropy import (
        plot_object_trajectory, plot_visibility_chart, plot_quarterly_trajectories,
        create_mosaic_trajectory_plot, create_mosaic_grid_plot, plot_weekly_analysis
    )
    from astronomy import calculate_altaz, find_visibility_window
    from analysis.reporting import ReportGenerator
    ASTROPY_AVAILABLE = True
except ImportError as e:
    Logger.warning(f"PlottingUtils: Astropy modules not available: {e}")
    ASTROPY_AVAILABLE = False

class MobilePlotGenerator:
    """Generate mobile-optimized plots for astronomical data"""
    
    def __init__(self):
        self.figure_size = (8, 6)  # Mobile-optimized size
        self.dpi = 100
        self.style_config = {
            'font.size': 10,
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
        
    def create_trajectory_plot(self, target, location, start_time=None, end_time=None):
        """Create trajectory plot for a single target"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Trajectory Plot", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            # Plot trajectory
            plot_object_trajectory(ax, target, start_time, end_time, 'blue')
            
            # Mobile-specific formatting
            ax.set_title(f"Trajectory: {getattr(target, 'name', 'Target')}", fontsize=12, pad=20)
            ax.grid(True, alpha=0.3)
            
            # Optimize for mobile viewing
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating trajectory plot: {e}")
            return self._create_placeholder_plot("Trajectory Plot", f"Error: {str(e)}")
    
    def create_visibility_chart(self, targets, location, start_time=None, end_time=None):
        """Create visibility chart for multiple targets"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Visibility Chart", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            # Create the plot
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            plot_visibility_chart(targets, start_time, end_time, 
                                title="Tonight's Visibility", use_margins=True)
            
            # Mobile-specific formatting
            plt.tight_layout()
            
            return self._save_plot_to_temp(plt.gcf())
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating visibility chart: {e}")
            return self._create_placeholder_plot("Visibility Chart", f"Error: {str(e)}")
    
    def create_mosaic_plot(self, mosaic_groups, start_time=None, end_time=None):
        """Create mosaic planning visualization"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Mosaic Plan", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            # Create trajectory plot
            fig = create_mosaic_trajectory_plot(mosaic_groups, start_time, end_time)
            
            # Mobile-specific formatting
            fig.set_size_inches(self.figure_size)
            fig.set_dpi(self.dpi)
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating mosaic plot: {e}")
            return self._create_placeholder_plot("Mosaic Plan", f"Error: {str(e)}")
    
    def create_mosaic_grid_plot(self, mosaic_groups, start_time=None, end_time=None):
        """Create mosaic grid visualization"""
        if not ASTROPY_AVAILABLE:
            return self._create_placeholder_plot("Mosaic Grid", "Astropy modules not available")
            
        try:
            self.configure_mobile_style()
            
            if start_time is None:
                start_time = datetime.now()
            if end_time is None:
                end_time = start_time + timedelta(hours=12)
                
            # Create grid plot
            fig = create_mosaic_grid_plot(mosaic_groups, start_time, end_time)
            
            # Mobile-specific formatting
            fig.set_size_inches(self.figure_size)
            fig.set_dpi(self.dpi)
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating mosaic grid plot: {e}")
            return self._create_placeholder_plot("Mosaic Grid", f"Error: {str(e)}")
    
    def create_target_altitude_plot(self, target, location, date=None):
        """Create altitude vs time plot for a target"""
        try:
            self.configure_mobile_style()
            
            if date is None:
                date = datetime.now().date()
                
            # Create time range for the night
            start_time = datetime.combine(date, datetime.min.time().replace(hour=18))
            end_time = start_time + timedelta(hours=12)
            
            # Generate time points
            times = []
            altitudes = []
            current_time = start_time
            
            while current_time <= end_time:
                times.append(current_time)
                
                # Calculate altitude (simplified calculation for demo)
                if ASTROPY_AVAILABLE:
                    try:
                        alt, az = calculate_altaz(target, location, current_time)
                        altitudes.append(alt)
                    except:
                        # Fallback calculation
                        hour_angle = (current_time.hour - 12) * 15  # degrees
                        altitude = 45 + 30 * np.sin(np.radians(hour_angle))  # simplified
                        altitudes.append(max(0, altitude))
                else:
                    # Demo data
                    hour_angle = (current_time.hour - 12) * 15
                    altitude = 45 + 30 * np.sin(np.radians(hour_angle))
                    altitudes.append(max(0, altitude))
                
                current_time += timedelta(minutes=30)
            
            # Create plot
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            ax.plot(times, altitudes, 'b-', linewidth=2, label='Altitude')
            ax.axhline(y=30, color='r', linestyle='--', alpha=0.7, label='Min altitude (30°)')
            ax.fill_between(times, 0, altitudes, alpha=0.3, color='blue')
            
            ax.set_xlabel('Time')
            ax.set_ylabel('Altitude (degrees)')
            ax.set_title(f"Altitude Profile: {getattr(target, 'name', 'Target')}")
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format time axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating altitude plot: {e}")
            return self._create_placeholder_plot("Altitude Plot", f"Error: {str(e)}")
    
    def _create_placeholder_plot(self, title, message):
        """Create a placeholder plot when data is not available"""
        try:
            self.configure_mobile_style()
            
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            ax.text(0.5, 0.5, message, 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            
            ax.set_title(title)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.tight_layout()
            
            return self._save_plot_to_temp(fig)
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating placeholder: {e}")
            return None
    
    def _save_plot_to_temp(self, fig):
        """Save plot to temporary file and return path"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Save plot
            fig.savefig(temp_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)  # Free memory
            
            Logger.info(f"MobilePlotGenerator: Plot saved to {temp_path}")
            return temp_path
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error saving plot: {e}")
            return None

    def create_mosaic_grid_plot(self, title, mosaic_groups):
        """Create mosaic grid layout visualization"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if not mosaic_groups:
                ax.text(0.5, 0.5, 'No mosaic groups available', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title)
                return fig
            
            # Create a grid layout for mosaic panels
            colors = plt.cm.Set3(np.linspace(0, 1, len(mosaic_groups)))
            
            for i, group in enumerate(mosaic_groups):
                name = group.get('name', f'Group {i+1}')
                panel_count = group.get('panel_count', 4)
                
                # Calculate grid dimensions
                grid_size = int(np.ceil(np.sqrt(panel_count)))
                
                # Plot panels in a grid
                for panel in range(panel_count):
                    px = (panel % grid_size) + i * (grid_size + 1)
                    py = (panel // grid_size)
                    
                    # Draw panel as rectangle
                    rect = plt.Rectangle((px-0.4, py-0.4), 0.8, 0.8, 
                                       facecolor=colors[i], alpha=0.7, 
                                       edgecolor='black', linewidth=1)
                    ax.add_patch(rect)
                    
                    # Add panel number
                    ax.text(px, py, str(panel+1), ha='center', va='center', 
                           fontsize=8, fontweight='bold')
                
                # Add group label
                center_x = i * (grid_size + 1) + (grid_size - 1) / 2
                ax.text(center_x, -0.8, name, ha='center', va='top', 
                       fontsize=10, fontweight='bold')
            
            ax.set_xlim(-1, len(mosaic_groups) * 6)
            ax.set_ylim(-1.5, 5)
            ax.set_aspect('equal')
            ax.set_title(title)
            ax.set_xlabel('Panel Grid Layout')
            ax.grid(True, alpha=0.3)
            
            # Remove y-axis labels for cleaner look
            ax.set_yticks([])
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            Logger.error(f"MobilePlotGenerator: Error creating mosaic grid plot: {e}")
            return self._create_error_plot(f"Mosaic grid plot error: {str(e)}")

# Global instance
mobile_plot_generator = MobilePlotGenerator()