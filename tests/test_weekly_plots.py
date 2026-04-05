"""
Test suite for weekly analysis plotting functions.

This module tests both desktop and mobile weekly analysis plotting functionality,
including comprehensive analysis plots, statistical visualizations, and mobile
optimizations.
"""

import pytest
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plots.weekly.desktop import (
    plot_weekly_analysis,
    create_weekly_comparison_plot,
    create_weekly_statistics_plot,
    create_weekly_summary_table_plot
)

from plots.weekly.mobile import (
    MobileWeeklyPlotter,
    create_mobile_weekly_analysis_plot,
    create_mobile_simple_weekly_plot,
    create_mobile_weekly_summary_plot,
    plot_weekly_analysis_mobile
)

from plots.weekly import (
    plot_weekly_analysis as weekly_main_plot,
    MobileWeeklyPlotter as WeeklyMobilePlotter
)

class TestWeeklyPlotsDesktop:
    """Test desktop weekly analysis plotting functions."""
    
    @pytest.fixture
    def sample_weekly_results(self):
        """Create sample weekly analysis results for testing."""
        weekly_results = {}
        base_date = datetime(2024, 1, 1)
        
        for week in range(1, 13):  # 12 weeks of data
            week_date = base_date + timedelta(weeks=week-1)
            
            # Generate realistic test data
            observable_objects = 15 + np.random.randint(-5, 10)
            sufficient_time_objects = max(5, observable_objects - np.random.randint(0, 5))
            moon_illumination = np.random.random()
            moon_phase = np.random.random()
            
            # Generate object lists
            moon_free_objects = [f"Object_{i}" for i in range(np.random.randint(3, 8))]
            moon_affected_objects = [f"MoonAff_{i}" for i in range(np.random.randint(2, 6))]
            mosaic_groups = [f"Mosaic_{i}" for i in range(np.random.randint(1, 4))]
            
            # Calculate score based on data
            score = (sufficient_time_objects * 2 + len(moon_free_objects) * 3 + 
                    len(mosaic_groups) * 5 - moon_illumination * 20)
            score = max(0, min(100, score))
            
            weekly_results[week] = {
                'week_date': week_date,
                'observable_objects': observable_objects,
                'sufficient_time_objects': sufficient_time_objects,
                'moon_illumination': moon_illumination,
                'moon_phase': moon_phase,
                'moon_free_objects': moon_free_objects,
                'moon_affected_objects': moon_affected_objects,
                'mosaic_groups': mosaic_groups,
                'score': score,
                'total_objects': observable_objects + 5,
                'exposure_limited_objects': np.random.randint(1, 4),
                'insufficient_time_objects': np.random.randint(0, 3),
                'bortle_index': 6,
                'single_objects': [f"Single_{i}" for i in range(np.random.randint(2, 5))],
                'moon_free_clusters': [f"Cluster_{i}" for i in range(np.random.randint(1, 3))],
                'night_duration': 8.5 + np.random.random() * 2,
                'top_objects': [
                    {'description': f'Top Object {i}', 'score': 80 + np.random.random() * 20, 
                     'moon_free': np.random.choice([True, False])}
                    for i in range(5)
                ]
            }
        
        return weekly_results
    
    def test_plot_weekly_analysis_basic(self, sample_weekly_results):
        """Test basic weekly analysis plotting."""
        fig = plot_weekly_analysis(sample_weekly_results, "test period")
        
        assert fig is not None
        assert len(fig.axes) >= 6  # Should have at least 6 subplots (colorbar may add extra axes)
        
        # Check that all axes have content
        for ax in fig.axes:
            assert len(ax.get_children()) > 0
        
        plt.close(fig)
    
    def test_plot_weekly_analysis_empty_data(self):
        """Test weekly analysis plotting with empty data."""
        fig = plot_weekly_analysis({}, "empty period")
        
        assert fig is not None
        assert len(fig.axes) == 1  # Should have single axis for empty message
        
        plt.close(fig)
    
    def test_create_weekly_comparison_plot(self, sample_weekly_results):
        """Test weekly comparison plotting."""
        fig = create_weekly_comparison_plot(sample_weekly_results, "comparison test")
        
        assert fig is not None
        assert len(fig.axes) == 3  # Should have 3 axes (2 main + 1 twin)
        
        plt.close(fig)
    
    def test_create_weekly_statistics_plot(self, sample_weekly_results):
        """Test weekly statistics plotting."""
        fig = create_weekly_statistics_plot(sample_weekly_results, "statistics test")
        
        assert fig is not None
        assert len(fig.axes) >= 4  # Should have at least 4 subplots
        
        plt.close(fig)
    
    def test_create_weekly_summary_table_plot(self, sample_weekly_results):
        """Test weekly summary table plotting."""
        fig = create_weekly_summary_table_plot(sample_weekly_results, "table test")
        
        assert fig is not None
        assert len(fig.axes) == 1  # Should have single axis for table
        
        plt.close(fig)
    
    def test_weekly_analysis_with_single_week(self):
        """Test weekly analysis with single week of data."""
        single_week_data = {
            1: {
                'week_date': datetime(2024, 1, 1),
                'observable_objects': 10,
                'sufficient_time_objects': 8,
                'moon_illumination': 0.3,
                'moon_phase': 0.25,
                'moon_free_objects': ['Obj1', 'Obj2', 'Obj3'],
                'moon_affected_objects': ['MoonObj1'],
                'mosaic_groups': ['Mosaic1'],
                'score': 75.0
            }
        }
        
        fig = plot_weekly_analysis(single_week_data, "single week")
        assert fig is not None
        plt.close(fig)
    
    def test_weekly_plots_with_extreme_values(self):
        """Test weekly plots with extreme values."""
        extreme_data = {
            1: {
                'week_date': datetime(2024, 1, 1),
                'observable_objects': 0,
                'sufficient_time_objects': 0,
                'moon_illumination': 1.0,
                'moon_phase': 1.0,
                'moon_free_objects': [],
                'moon_affected_objects': [],
                'mosaic_groups': [],
                'score': 0.0
            },
            2: {
                'week_date': datetime(2024, 1, 8),
                'observable_objects': 50,
                'sufficient_time_objects': 45,
                'moon_illumination': 0.0,
                'moon_phase': 0.0,
                'moon_free_objects': [f'Obj{i}' for i in range(20)],
                'moon_affected_objects': [],
                'mosaic_groups': [f'Mosaic{i}' for i in range(10)],
                'score': 100.0
            }
        }
        
        fig = plot_weekly_analysis(extreme_data, "extreme values")
        assert fig is not None
        plt.close(fig)

class TestWeeklyPlotsMobile:
    """Test mobile weekly analysis plotting functions."""
    
    @pytest.fixture
    def sample_weekly_results(self):
        """Create sample weekly analysis results for mobile testing."""
        weekly_results = {}
        base_date = datetime(2024, 1, 1)
        
        # Create more weeks than mobile limit to test limiting
        for week in range(1, 16):  # 15 weeks of data
            week_date = base_date + timedelta(weeks=week-1)
            
            observable_objects = 10 + np.random.randint(-3, 8)
            sufficient_time_objects = max(3, observable_objects - np.random.randint(0, 3))
            moon_illumination = np.random.random()
            moon_phase = np.random.random()
            
            moon_free_objects = [f"MF_{i}" for i in range(np.random.randint(2, 6))]
            moon_affected_objects = [f"MA_{i}" for i in range(np.random.randint(1, 4))]
            mosaic_groups = [f"MG_{i}" for i in range(np.random.randint(0, 3))]
            
            score = (sufficient_time_objects * 3 + len(moon_free_objects) * 4 + 
                    len(mosaic_groups) * 6 - moon_illumination * 25)
            score = max(0, min(100, score))
            
            weekly_results[week] = {
                'week_date': week_date,
                'observable_objects': observable_objects,
                'sufficient_time_objects': sufficient_time_objects,
                'moon_illumination': moon_illumination,
                'moon_phase': moon_phase,
                'moon_free_objects': moon_free_objects,
                'moon_affected_objects': moon_affected_objects,
                'mosaic_groups': mosaic_groups,
                'score': score
            }
        
        return weekly_results
    
    def test_mobile_weekly_plotter_initialization(self):
        """Test MobileWeeklyPlotter initialization."""
        plotter = MobileWeeklyPlotter()
        
        assert plotter.figure_size == (8, 6)
        assert plotter.max_weeks == 12
        assert plotter.font_size == 8
    
    def test_create_mobile_weekly_analysis_plot(self, sample_weekly_results):
        """Test mobile weekly analysis plot creation."""
        plotter = MobileWeeklyPlotter()
        fig = plotter.create_weekly_analysis_plot(sample_weekly_results, "mobile test")
        
        assert fig is not None
        assert len(fig.axes) == 4  # Should have 2x2 subplot layout
        
        plt.close(fig)
    
    def test_create_mobile_simple_weekly_plot(self, sample_weekly_results):
        """Test mobile simple weekly plot creation."""
        plotter = MobileWeeklyPlotter()
        fig = plotter.create_simple_weekly_plot(sample_weekly_results, "simple mobile test")
        
        assert fig is not None
        assert len(fig.axes) == 1  # Should have single plot
        
        plt.close(fig)
    
    def test_create_mobile_weekly_summary_plot(self, sample_weekly_results):
        """Test mobile weekly summary plot creation."""
        plotter = MobileWeeklyPlotter()
        fig = plotter.create_weekly_summary_plot(sample_weekly_results, "summary mobile test")
        
        assert fig is not None
        assert len(fig.axes) == 1  # Should have single axis for text summary
        
        plt.close(fig)
    
    def test_mobile_week_limiting(self, sample_weekly_results):
        """Test that mobile plots limit weeks for performance."""
        plotter = MobileWeeklyPlotter()
        
        # Should limit to max_weeks (12) from 15 weeks
        fig = plotter.create_weekly_analysis_plot(sample_weekly_results, "week limiting test")
        
        assert fig is not None
        # Check that the title indicates limiting
        title = fig._suptitle.get_text()
        assert "last 12 weeks" in title
        
        plt.close(fig)
    
    def test_mobile_empty_data_handling(self):
        """Test mobile plots with empty data."""
        plotter = MobileWeeklyPlotter()
        fig = plotter.create_weekly_analysis_plot({}, "empty mobile test")
        
        assert fig is not None
        assert len(fig.axes) == 1  # Should have single axis for empty message
        
        plt.close(fig)
    
    def test_mobile_error_handling(self):
        """Test mobile plots error handling."""
        plotter = MobileWeeklyPlotter()
        
        # Test with malformed data
        bad_data = {
            1: {
                'week_date': "not_a_date",  # This should cause an error
                'observable_objects': "not_a_number"
            }
        }
        
        fig = plotter.create_weekly_analysis_plot(bad_data, "error test")
        
        assert fig is not None
        # Should create error plot
        assert len(fig.axes) == 1
        
        plt.close(fig)
    
    def test_convenience_functions(self, sample_weekly_results):
        """Test convenience functions for mobile plotting."""
        # Test convenience functions
        fig1 = create_mobile_weekly_analysis_plot(sample_weekly_results, "convenience test 1")
        fig2 = create_mobile_simple_weekly_plot(sample_weekly_results, "convenience test 2")
        fig3 = create_mobile_weekly_summary_plot(sample_weekly_results, "convenience test 3")
        fig4 = plot_weekly_analysis_mobile(sample_weekly_results, "convenience test 4")
        
        assert all(fig is not None for fig in [fig1, fig2, fig3, fig4])
        
        for fig in [fig1, fig2, fig3, fig4]:
            plt.close(fig)

class TestWeeklyPlotsIntegration:
    """Test integration of weekly plotting functions."""
    
    @pytest.fixture
    def sample_weekly_results(self):
        """Create sample weekly analysis results for integration testing."""
        weekly_results = {}
        base_date = datetime(2024, 1, 1)
        
        for week in range(1, 8):  # 7 weeks of data
            week_date = base_date + timedelta(weeks=week-1)
            
            weekly_results[week] = {
                'week_date': week_date,
                'observable_objects': 12 + week,
                'sufficient_time_objects': 8 + week,
                'moon_illumination': (week % 4) * 0.25,
                'moon_phase': (week % 4) * 0.25,
                'moon_free_objects': [f"MF_{i}" for i in range(3 + week % 3)],
                'moon_affected_objects': [f"MA_{i}" for i in range(2 + week % 2)],
                'mosaic_groups': [f"MG_{i}" for i in range(1 + week % 2)],
                'score': 60 + week * 5
            }
        
        return weekly_results
    
    def test_main_module_imports(self, sample_weekly_results):
        """Test that main module imports work correctly."""
        # Test main module function
        fig1 = weekly_main_plot(sample_weekly_results, "main module test")
        assert fig1 is not None
        plt.close(fig1)
        
        # Test mobile plotter class
        mobile_plotter = WeeklyMobilePlotter()
        fig2 = mobile_plotter.create_weekly_analysis_plot(sample_weekly_results, "mobile class test")
        assert fig2 is not None
        plt.close(fig2)
    
    def test_plots_module_integration(self, sample_weekly_results):
        """Test integration with main plots module."""
        try:
            from plots import plot_weekly_analysis as plots_weekly
            from plots import MobileWeeklyPlotter as PlotsMobileWeekly
            
            fig1 = plots_weekly(sample_weekly_results, "plots module test")
            assert fig1 is not None
            plt.close(fig1)
            
            mobile_plotter = PlotsMobileWeekly()
            fig2 = mobile_plotter.create_weekly_analysis_plot(sample_weekly_results, "plots mobile test")
            assert fig2 is not None
            plt.close(fig2)
            
        except ImportError:
            pytest.skip("Main plots module not available for integration testing")
    
    def test_figure_properties(self, sample_weekly_results):
        """Test that figures have correct properties."""
        # Desktop figure properties
        desktop_fig = plot_weekly_analysis(sample_weekly_results, "properties test")
        assert desktop_fig.get_figwidth() == 18
        assert desktop_fig.get_figheight() == 12
        plt.close(desktop_fig)
        
        # Mobile figure properties
        mobile_plotter = MobileWeeklyPlotter()
        mobile_fig = mobile_plotter.create_weekly_analysis_plot(sample_weekly_results, "mobile properties test")
        assert mobile_fig.get_figwidth() == 8
        assert mobile_fig.get_figheight() == 6
        plt.close(mobile_fig)
    
    def test_data_consistency(self, sample_weekly_results):
        """Test that plots handle data consistently."""
        # Test with same data on both desktop and mobile
        desktop_fig = plot_weekly_analysis(sample_weekly_results, "consistency test")
        mobile_fig = create_mobile_weekly_analysis_plot(sample_weekly_results, "consistency test")
        
        # Both should create valid figures
        assert desktop_fig is not None
        assert mobile_fig is not None
        
        # Desktop should have more subplots than mobile
        assert len(desktop_fig.axes) > len(mobile_fig.axes)
        
        plt.close(desktop_fig)
        plt.close(mobile_fig)

if __name__ == "__main__":
    # Run basic tests if executed directly
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for testing
    
    # Create sample data
    sample_data = {}
    base_date = datetime(2024, 1, 1)
    
    for week in range(1, 6):
        week_date = base_date + timedelta(weeks=week-1)
        sample_data[week] = {
            'week_date': week_date,
            'observable_objects': 10 + week,
            'sufficient_time_objects': 8 + week,
            'moon_illumination': week * 0.2,
            'moon_phase': week * 0.2,
            'moon_free_objects': [f"MF_{i}" for i in range(3)],
            'moon_affected_objects': [f"MA_{i}" for i in range(2)],
            'mosaic_groups': [f"MG_{i}" for i in range(1)],
            'score': 60 + week * 8
        }
    
    print("Testing weekly analysis plotting functions...")
    
    # Test desktop functions
    print("Testing desktop functions...")
    fig1 = plot_weekly_analysis(sample_data, "test run")
    print(f"Desktop plot created: {fig1 is not None}")
    plt.close(fig1)
    
    # Test mobile functions
    print("Testing mobile functions...")
    mobile_plotter = MobileWeeklyPlotter()
    fig2 = mobile_plotter.create_weekly_analysis_plot(sample_data, "mobile test run")
    print(f"Mobile plot created: {fig2 is not None}")
    plt.close(fig2)
    
    print("Basic tests completed successfully!") 