"""
Mobile weekly analysis plotting module for AstroScope.

This module provides mobile-optimized weekly analysis plotting functionality,
including simplified visualizations, touch-friendly interfaces, and performance
optimizations for mobile devices.

Features:
- Touch-optimized weekly analysis plots
- Simplified 2-panel layouts for mobile screens
- Performance optimizations (reduced data points, simplified styling)
- Mobile-friendly legends and labels
- Error handling with fallback plots
- Week limiting for performance (max 12 weeks)
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from config.settings import *

# Mobile-specific constants
MOBILE_FIGURE_SIZE = (8, 6)
MOBILE_DPI = 100
MOBILE_FONT_SIZE = 8
MOBILE_TITLE_SIZE = 10
MOBILE_LABEL_SIZE = 7
MOBILE_MAX_WEEKS = 12

class MobileWeeklyPlotter:
    """Mobile-optimized weekly analysis plotter with touch-friendly interface."""
    
    def __init__(self):
        """Initialize mobile weekly plotter with optimized settings."""
        self.figure_size = MOBILE_FIGURE_SIZE
        self.dpi = MOBILE_DPI
        self.font_size = MOBILE_FONT_SIZE
        self.title_size = MOBILE_TITLE_SIZE
        self.label_size = MOBILE_LABEL_SIZE
        self.max_weeks = MOBILE_MAX_WEEKS
        
    def create_weekly_analysis_plot(self, weekly_results, period_desc="analysis period"):
        """
        Create mobile-optimized weekly analysis plot.
        
        Args:
            weekly_results (dict): Dictionary containing weekly analysis results
            period_desc (str): Description of the analysis period
            
        Returns:
            matplotlib.figure.Figure: Mobile-optimized weekly analysis figure
        """
        try:
            weeks = sorted(weekly_results.keys())
            
            # Limit weeks for mobile performance
            if len(weeks) > self.max_weeks:
                weeks = weeks[-self.max_weeks:]  # Show most recent weeks
                limited_results = {w: weekly_results[w] for w in weeks}
                period_desc += f" (last {self.max_weeks} weeks)"
            else:
                limited_results = weekly_results
            
            if not weeks:
                return self._create_empty_plot("No weekly data available")
            
            # Extract data for plotting
            observable_objects = [limited_results[w]['observable_objects'] for w in weeks]
            moon_free_counts = [len(limited_results[w]['moon_free_objects']) for w in weeks]
            scores = [limited_results[w]['score'] for w in weeks]
            moon_illuminations = [limited_results[w]['moon_illumination'] * 100 for w in weeks]
            
            # Create 2x2 subplot layout for mobile
            fig, axes = plt.subplots(2, 2, figsize=self.figure_size, dpi=self.dpi)
            fig.suptitle(f'Weekly Analysis - {period_desc}', 
                        fontsize=self.title_size, fontweight='bold')
            
            # Plot 1: Weekly scores (top-left)
            ax1 = axes[0, 0]
            score_bars = ax1.bar(weeks, scores, alpha=0.8, color='purple', width=0.6)
            ax1.set_xlabel('Week', fontsize=self.label_size)
            ax1.set_ylabel('Score', fontsize=self.label_size)
            ax1.set_title('Weekly Scores', fontsize=self.font_size, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(labelsize=self.label_size-1)
            
            # Highlight best week
            if weeks:
                best_week = max(weeks, key=lambda w: limited_results[w]['score'])
                best_week_idx = weeks.index(best_week)
                score_bars[best_week_idx].set_color('gold')
            
            # Plot 2: Observable objects (top-right)
            ax2 = axes[0, 1]
            ax2.plot(weeks, observable_objects, 'o-', color='blue', linewidth=2, 
                    markersize=4, alpha=0.8)
            ax2.set_xlabel('Week', fontsize=self.label_size)
            ax2.set_ylabel('Objects', fontsize=self.label_size)
            ax2.set_title('Observable Objects', fontsize=self.font_size, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(labelsize=self.label_size-1)
            
            # Plot 3: Moon-free objects (bottom-left)
            ax3 = axes[1, 0]
            ax3.bar(weeks, moon_free_counts, alpha=0.8, color='green', width=0.6)
            ax3.set_xlabel('Week', fontsize=self.label_size)
            ax3.set_ylabel('Moon-Free', fontsize=self.label_size)
            ax3.set_title('Moon-Free Objects', fontsize=self.font_size, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(labelsize=self.label_size-1)
            
            # Plot 4: Moon illumination (bottom-right)
            ax4 = axes[1, 1]
            ax4.fill_between(weeks, moon_illuminations, alpha=0.5, color='lightblue')
            ax4.plot(weeks, moon_illuminations, 'o-', color='darkblue', linewidth=2, markersize=4)
            ax4.set_xlabel('Week', fontsize=self.label_size)
            ax4.set_ylabel('Moon %', fontsize=self.label_size)
            ax4.set_title('Moon Illumination', fontsize=self.font_size, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.tick_params(labelsize=self.label_size-1)
            ax4.set_ylim(0, 100)
            
            plt.tight_layout()
            plt.subplots_adjust(top=0.90)
            
            return fig
            
        except Exception as e:
            return self._create_error_plot(f"Error creating weekly plot: {str(e)}")
    
    def create_simple_weekly_plot(self, weekly_results, period_desc="analysis period"):
        """
        Create simplified single-panel weekly plot for mobile.
        
        Args:
            weekly_results (dict): Dictionary containing weekly analysis results
            period_desc (str): Description of the analysis period
            
        Returns:
            matplotlib.figure.Figure: Simple weekly analysis figure
        """
        try:
            weeks = sorted(weekly_results.keys())
            
            # Limit weeks for mobile performance
            if len(weeks) > self.max_weeks:
                weeks = weeks[-self.max_weeks:]
                limited_results = {w: weekly_results[w] for w in weeks}
            else:
                limited_results = weekly_results
            
            if not weeks:
                return self._create_empty_plot("No weekly data available")
            
            scores = [limited_results[w]['score'] for w in weeks]
            
            # Create single plot
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            # Plot weekly scores with color coding
            colors = ['red' if s < 50 else 'orange' if s < 70 else 'green' for s in scores]
            bars = ax.bar(weeks, scores, alpha=0.8, color=colors, width=0.7)
            
            ax.set_xlabel('Week Number', fontsize=self.label_size)
            ax.set_ylabel('Astrophotography Score', fontsize=self.label_size)
            ax.set_title(f'Weekly Scores - {period_desc}', fontsize=self.title_size, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=self.label_size-1)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{score:.0f}', ha='center', va='bottom', 
                       fontsize=self.label_size-1, fontweight='bold')
            
            # Add legend for color coding
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='green', alpha=0.8, label='Good (≥70)'),
                Patch(facecolor='orange', alpha=0.8, label='Fair (50-69)'),
                Patch(facecolor='red', alpha=0.8, label='Poor (<50)')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=self.label_size-1)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            return self._create_error_plot(f"Error creating simple weekly plot: {str(e)}")
    
    def create_weekly_summary_plot(self, weekly_results, period_desc="analysis period"):
        """
        Create weekly summary plot with key metrics.
        
        Args:
            weekly_results (dict): Dictionary containing weekly analysis results
            period_desc (str): Description of the analysis period
            
        Returns:
            matplotlib.figure.Figure: Weekly summary figure
        """
        try:
            weeks = sorted(weekly_results.keys())
            
            if not weeks:
                return self._create_empty_plot("No weekly data available")
            
            # Calculate summary statistics
            scores = [weekly_results[w]['score'] for w in weeks]
            observable_counts = [weekly_results[w]['observable_objects'] for w in weeks]
            moon_free_counts = [len(weekly_results[w]['moon_free_objects']) for w in weeks]
            
            best_week = max(weeks, key=lambda w: weekly_results[w]['score'])
            best_score = weekly_results[best_week]['score']
            avg_score = np.mean(scores)
            avg_observable = np.mean(observable_counts)
            avg_moon_free = np.mean(moon_free_counts)
            
            # Create summary plot
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            ax.axis('off')
            
            # Title
            fig.suptitle(f'Weekly Summary - {period_desc}', 
                        fontsize=self.title_size, fontweight='bold')
            
            # Summary text
            summary_text = f"""
WEEKLY ANALYSIS SUMMARY
{'='*30}

Period: {len(weeks)} weeks analyzed
Best Week: Week {best_week} (Score: {best_score:.1f})

AVERAGES:
• Weekly Score: {avg_score:.1f}
• Observable Objects: {avg_observable:.1f}
• Moon-Free Objects: {avg_moon_free:.1f}

BEST WEEK DETAILS:
• Date: {weekly_results[best_week]['week_date'].strftime('%Y-%m-%d')}
• Observable: {weekly_results[best_week]['observable_objects']} objects
• Moon-Free: {len(weekly_results[best_week]['moon_free_objects'])} objects
• Mosaics: {len(weekly_results[best_week]['mosaic_groups'])} groups
• Moon: {weekly_results[best_week]['moon_illumination']*100:.1f}% illuminated
            """
            
            ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
                   fontsize=self.font_size, verticalalignment='top',
                   fontfamily='monospace',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
            
            return fig
            
        except Exception as e:
            return self._create_error_plot(f"Error creating weekly summary: {str(e)}")
    
    def _create_empty_plot(self, message):
        """Create an empty plot with a message."""
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        ax.text(0.5, 0.5, message, ha='center', va='center', 
                fontsize=self.font_size, transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        ax.set_title('Weekly Analysis', fontsize=self.title_size)
        ax.axis('off')
        return fig
    
    def _create_error_plot(self, error_message):
        """Create an error plot with error message."""
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        ax.text(0.5, 0.5, f"Error:\n{error_message}", ha='center', va='center',
                fontsize=self.font_size, transform=ax.transAxes, color='red',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="mistyrose", alpha=0.8))
        ax.set_title('Weekly Analysis - Error', fontsize=self.title_size)
        ax.axis('off')
        return fig

# Convenience functions for direct use
def create_mobile_weekly_analysis_plot(weekly_results, period_desc="analysis period"):
    """
    Convenience function to create mobile weekly analysis plot.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: Mobile weekly analysis figure
    """
    plotter = MobileWeeklyPlotter()
    return plotter.create_weekly_analysis_plot(weekly_results, period_desc)

def create_mobile_simple_weekly_plot(weekly_results, period_desc="analysis period"):
    """
    Convenience function to create simple mobile weekly plot.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: Simple mobile weekly figure
    """
    plotter = MobileWeeklyPlotter()
    return plotter.create_simple_weekly_plot(weekly_results, period_desc)

def create_mobile_weekly_summary_plot(weekly_results, period_desc="analysis period"):
    """
    Convenience function to create mobile weekly summary plot.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: Mobile weekly summary figure
    """
    plotter = MobileWeeklyPlotter()
    return plotter.create_weekly_summary_plot(weekly_results, period_desc)

def plot_weekly_analysis_mobile(weekly_results, period_desc="analysis period"):
    """
    Mobile version of the main weekly analysis plotting function.
    
    This is the mobile equivalent of the desktop plot_weekly_analysis function,
    optimized for mobile screens and touch interaction.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: Mobile-optimized weekly analysis figure
    """
    return create_mobile_weekly_analysis_plot(weekly_results, period_desc) 