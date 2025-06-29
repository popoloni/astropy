"""
Mobile visibility chart plotting functions.

This module provides mobile-optimized visibility chart plotting with simplified
interface, touch-friendly controls, and performance optimizations for mobile devices.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.dates import DateFormatter
import numpy as np
import pytz
from datetime import datetime, timedelta
import logging

# Mobile-specific constants
MOBILE_FIGURE_SIZE = (8, 6)
MOBILE_DPI = 100
MOBILE_FONT_SIZE = 8
MOBILE_TITLE_SIZE = 10
MOBILE_LABEL_SIZE = 9
MAX_MOBILE_OBJECTS = 8  # Limit for mobile display
MOBILE_BAR_HEIGHT = 0.4
MOBILE_GRID_ALPHA = 0.2

# Colors optimized for mobile screens
MOBILE_MOON_COLOR = '#FF4444'
MOBILE_SCHEDULED_COLOR = '#FF0000'
MOBILE_RECOMMENDED_COLOR = '#00AA00'
MOBILE_NON_RECOMMENDED_COLOR = '#666666'
MOBILE_INSUFFICIENT_COLOR = '#FF99CC'

class MobileVisibilityPlotter:
    """Mobile-optimized visibility chart plotter"""
    
    def __init__(self):
        """Initialize mobile plotter with optimized settings"""
        self.figure_size = MOBILE_FIGURE_SIZE
        self.dpi = MOBILE_DPI
        self.font_size = MOBILE_FONT_SIZE
        self.max_objects = MAX_MOBILE_OBJECTS
        
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
        
        logging.info("MobileVisibilityPlotter initialized")

    def create_visibility_chart(self, objects, start_time, end_time, location=None, 
                               schedule=None, title="Tonight's Visibility"):
        """
        Create mobile-optimized visibility chart.
        
        Parameters:
        -----------
        objects : list
            List of celestial objects (limited to max_objects for mobile)
        start_time : datetime
            Start time for visibility window
        end_time : datetime
            End time for visibility window
        location : dict, optional
            Location information (not used in mobile version)
        schedule : list, optional
            List of scheduled observations
        title : str, optional
            Chart title
            
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        try:
            logging.info(f"Creating mobile visibility chart for {len(objects)} objects")
            
            # Limit objects for mobile display
            limited_objects = objects[:self.max_objects] if objects else []
            
            if not limited_objects:
                return self._create_error_plot("No objects available for visibility chart")
            
            # Create figure with mobile settings
            fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
            ax = fig.add_subplot(111)
            
            # Setup mobile-optimized chart
            self._setup_mobile_chart(ax, limited_objects, start_time, end_time, title)
            
            # Plot visibility bars
            self._plot_mobile_visibility_bars(ax, limited_objects, start_time, end_time, schedule)
            
            # Add mobile-friendly legend
            self._add_mobile_legend(ax, schedule, limited_objects)
            
            # Mobile-specific formatting
            self._apply_mobile_formatting(fig, ax)
            
            logging.info("Mobile visibility chart created successfully")
            return fig
            
        except Exception as e:
            logging.error(f"Error creating mobile visibility chart: {e}")
            return self._create_error_plot(f"Chart creation failed: {str(e)}")

    def create_simple_visibility_chart(self, objects, start_time, end_time, title="Visibility"):
        """
        Create simplified visibility chart for mobile with minimal features.
        
        Parameters:
        -----------
        objects : list
            List of celestial objects
        start_time : datetime
            Start time for visibility window
        end_time : datetime
            End time for visibility window
        title : str, optional
            Chart title
            
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        try:
            logging.info(f"Creating simple mobile visibility chart for {len(objects)} objects")
            
            # Limit objects for mobile display
            limited_objects = objects[:self.max_objects] if objects else []
            
            if not limited_objects:
                return self._create_error_plot("No objects available")
            
            # Create figure
            fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
            ax = fig.add_subplot(111)
            
            # Simple chart setup
            ax.set_title(title, fontsize=MOBILE_TITLE_SIZE, fontweight='bold')
            ax.set_xlabel('Time', fontsize=MOBILE_LABEL_SIZE)
            ax.set_ylabel('Objects', fontsize=MOBILE_LABEL_SIZE)
            
            # Create simple visibility bars
            colors = ['#00AA00', '#0066CC', '#FF6600', '#CC00CC', '#FFAA00', '#00CCAA', '#CC6600', '#6600CC']
            
            for i, obj in enumerate(limited_objects):
                color = colors[i % len(colors)]
                obj_name = self._get_mobile_object_name(obj)
                
                # Simple time-based visibility simulation
                times = []
                current_time = start_time
                time_interval = (end_time - start_time) / 20  # 20 points for mobile
                
                while current_time <= end_time:
                    times.append(current_time)
                    current_time += time_interval
                
                if times:
                    # Simple bar for the entire period
                    ax.barh(i, end_time - start_time, left=start_time, 
                           height=MOBILE_BAR_HEIGHT, color=color, alpha=0.7, 
                           label=obj_name)
            
            # Setup axes
            ax.set_yticks(range(len(limited_objects)))
            ax.set_yticklabels([self._get_mobile_object_name(obj) for obj in limited_objects])
            ax.set_xlim(start_time, end_time)
            
            # Time formatting
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            
            # Mobile formatting
            self._apply_mobile_formatting(fig, ax)
            
            logging.info("Simple mobile visibility chart created successfully")
            return fig
            
        except Exception as e:
            logging.error(f"Error creating simple mobile visibility chart: {e}")
            return self._create_error_plot(f"Simple chart failed: {str(e)}")

    def _setup_mobile_chart(self, ax, objects, start_time, end_time, title):
        """Setup mobile-optimized chart axes and formatting"""
        # Ensure times are in local timezone
        local_tz = self._get_local_timezone()
        if start_time.tzinfo != local_tz:
            start_time = start_time.astimezone(local_tz)
        if end_time.tzinfo != local_tz:
            end_time = end_time.astimezone(local_tz)
        
        ax.set_title(title, fontsize=MOBILE_TITLE_SIZE, fontweight='bold')
        ax.set_xlabel('Time', fontsize=MOBILE_LABEL_SIZE)
        ax.set_ylabel('Objects', fontsize=MOBILE_LABEL_SIZE)
        ax.set_xlim(start_time, end_time)
        
        # Mobile-friendly time formatting
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=local_tz))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Every 2 hours for mobile
        
        # Simplified grid
        ax.grid(True, axis='x', alpha=MOBILE_GRID_ALPHA)

    def _plot_mobile_visibility_bars(self, ax, objects, start_time, end_time, schedule):
        """Plot visibility bars optimized for mobile display"""
        recommended_objects = [obj for _, _, obj in schedule] if schedule else []
        
        for i, obj in enumerate(objects):
            is_recommended = obj in recommended_objects
            has_sufficient_time = getattr(obj, 'sufficient_time', True)
            
            # Determine color (simplified for mobile)
            if not has_sufficient_time:
                color = MOBILE_INSUFFICIENT_COLOR
            elif is_recommended:
                color = MOBILE_RECOMMENDED_COLOR
            else:
                color = MOBILE_NON_RECOMMENDED_COLOR
            
            alpha = 0.8 if is_recommended else 0.6
            
            # Simple visibility bar (no complex moon interference for mobile)
            ax.barh(i, end_time - start_time, left=start_time, 
                   height=MOBILE_BAR_HEIGHT, color=color, alpha=alpha)
            
            # Add scheduled overlay if applicable
            if schedule and obj in recommended_objects:
                self._add_mobile_scheduled_overlay(ax, i, obj, schedule, start_time, end_time)
        
        # Setup object labels
        ax.set_yticks(range(len(objects)))
        ax.set_yticklabels([self._get_mobile_object_name(obj) for obj in objects])

    def _add_mobile_scheduled_overlay(self, ax, index, obj, schedule, start_time, end_time):
        """Add simplified scheduled overlay for mobile"""
        for sched_start, sched_end, sched_obj in schedule:
            if sched_obj == obj:
                # Ensure times are in local timezone
                local_tz = self._get_local_timezone()
                sched_start_local = sched_start.astimezone(local_tz)
                sched_end_local = sched_end.astimezone(local_tz)
                
                # Clip to chart boundaries
                plot_start = max(sched_start_local, start_time)
                plot_end = min(sched_end_local, end_time)
                
                if plot_start < plot_end:
                    ax.barh(index, plot_end - plot_start, left=plot_start,
                           height=MOBILE_BAR_HEIGHT * 1.1, color='none',
                           edgecolor=MOBILE_SCHEDULED_COLOR, linewidth=2,
                           alpha=0.9, zorder=10)

    def _add_mobile_legend(self, ax, schedule, objects):
        """Add simplified legend for mobile display"""
        legend_handles = []
        
        # Only add essential legend items for mobile
        rec_handle = Patch(facecolor=MOBILE_RECOMMENDED_COLOR, alpha=0.8, 
                          label='Recommended')
        legend_handles.append(rec_handle)
        
        if any(not getattr(obj, 'sufficient_time', True) for obj in objects):
            insuf_handle = Patch(facecolor=MOBILE_INSUFFICIENT_COLOR, alpha=0.6, 
                               label='Insufficient Time')
            legend_handles.append(insuf_handle)
        
        if schedule:
            sched_handle = Patch(facecolor='none', edgecolor=MOBILE_SCHEDULED_COLOR, 
                               linewidth=2, label='Scheduled')
            legend_handles.append(sched_handle)
        
        # Add legend with mobile-friendly positioning
        if legend_handles:
            ax.legend(handles=legend_handles, loc='upper right', fontsize=self.font_size,
                     framealpha=0.9, fancybox=True)

    def _apply_mobile_formatting(self, fig, ax):
        """Apply mobile-specific formatting"""
        # Tight layout for mobile
        fig.tight_layout(pad=1.0)
        
        # Rotate x-axis labels for better mobile readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Adjust margins for mobile
        fig.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.9)

    def _get_mobile_object_name(self, obj):
        """Get abbreviated object name suitable for mobile display"""
        if hasattr(obj, 'name'):
            name = obj.name
        elif isinstance(obj, dict):
            name = obj.get('name', 'Unknown')
        else:
            name = str(obj)
        
        # Abbreviate for mobile display
        if '/' in name:
            name = name.split('/')[0]
        
        # Limit length for mobile
        return name[:8] if len(name) > 8 else name

    def _create_error_plot(self, error_message):
        """Create error plot for mobile display"""
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        ax = fig.add_subplot(111)
        
        ax.text(0.5, 0.5, f"Error:\n{error_message}", 
                transform=ax.transAxes, ha='center', va='center',
                fontsize=self.font_size, color='red',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Visibility Chart Error", fontsize=MOBILE_TITLE_SIZE)
        
        fig.tight_layout()
        return fig

    def _get_local_timezone(self):
        """Get local timezone for mobile"""
        return pytz.timezone('Europe/Rome')  # Milan timezone

# Convenience functions for easy access

def create_mobile_visibility_chart(objects, start_time, end_time, location=None, 
                                  schedule=None, title="Tonight's Visibility"):
    """
    Create mobile visibility chart using the MobileVisibilityPlotter.
    
    Parameters:
    -----------
    objects : list
        List of celestial objects
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    location : dict, optional
        Location information
    schedule : list, optional
        List of scheduled observations
    title : str, optional
        Chart title
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    plotter = MobileVisibilityPlotter()
    return plotter.create_visibility_chart(objects, start_time, end_time, 
                                         location, schedule, title)

def create_mobile_simple_visibility_chart(objects, start_time, end_time, title="Visibility"):
    """
    Create simplified mobile visibility chart.
    
    Parameters:
    -----------
    objects : list
        List of celestial objects
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    title : str, optional
        Chart title
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    plotter = MobileVisibilityPlotter()
    return plotter.create_simple_visibility_chart(objects, start_time, end_time, title)

def create_mobile_multi_object_chart(objects_list, start_time, end_time, max_objects=5):
    """
    Create multi-object visibility chart for mobile with automatic object limiting.
    
    Parameters:
    -----------
    objects_list : list
        List of celestial objects
    start_time : datetime
        Start time for visibility window
    end_time : datetime
        End time for visibility window
    max_objects : int, optional
        Maximum number of objects to display (default: 5)
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    # Limit objects for mobile performance
    limited_objects = objects_list[:max_objects] if objects_list else []
    
    plotter = MobileVisibilityPlotter()
    plotter.max_objects = max_objects
    
    title = f"Visibility ({len(limited_objects)} objects)"
    if len(objects_list) > max_objects:
        title += f" - Showing top {max_objects}"
    
    return plotter.create_visibility_chart(limited_objects, start_time, end_time, 
                                         title=title) 