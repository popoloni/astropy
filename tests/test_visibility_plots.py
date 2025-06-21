"""
Tests for visibility plotting functions.

This module tests both desktop and mobile visibility chart plotting functions
to ensure they work correctly and produce expected outputs.
"""

import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytz

# Import the functions to test
from plots.visibility.desktop import (
    plot_visibility_chart,
    create_mosaic_visibility_chart,
    _get_sorted_objects_for_chart,
    _setup_visibility_chart_axes,
    _plot_object_visibility_bars,
    _add_visibility_chart_legend
)

from plots.visibility.mobile import (
    MobileVisibilityPlotter,
    create_mobile_visibility_chart,
    create_mobile_simple_visibility_chart,
    create_mobile_multi_object_chart
)

from plots.base import setup_plot
from plots.utils.verification import PlotVerifier

class MockCelestialObject:
    """Mock celestial object for testing"""
    def __init__(self, name="Test Object", sufficient_time=True, is_mosaic_group=False):
        self.name = name
        self.sufficient_time = sufficient_time
        self.is_mosaic_group = is_mosaic_group
        self.magnitude = 5.0
        if is_mosaic_group:
            self.objects = [MockCelestialObject(f"Sub-{name}-{i}") for i in range(3)]

@pytest.fixture
def mock_objects():
    """Create mock celestial objects for testing"""
    return [
        MockCelestialObject("NGC 1234", sufficient_time=True),
        MockCelestialObject("M42/Orion Nebula", sufficient_time=True),
        MockCelestialObject("IC 5146", sufficient_time=False),
        MockCelestialObject("Mosaic Group 1", sufficient_time=True, is_mosaic_group=True)
    ]

@pytest.fixture
def time_range():
    """Create time range for testing"""
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    return start_time, end_time

@pytest.fixture
def mock_schedule(mock_objects):
    """Create mock schedule for testing"""
    start_time = datetime(2024, 1, 1, 21, 0, 0)
    end_time = start_time + timedelta(hours=2)
    return [(start_time, end_time, mock_objects[0])]

@pytest.fixture
def verifier():
    """Create plot verifier for testing"""
    return PlotVerifier()

# Desktop visibility chart tests

def test_plot_visibility_chart_basic(mock_objects, time_range):
    """Test basic desktop visibility chart creation"""
    start_time, end_time = time_range
    
    with patch('plots.visibility.desktop._find_visibility_window', return_value=[(start_time, end_time)]), \
         patch('plots.visibility.desktop._get_local_timezone', return_value=pytz.UTC):
        
        fig, ax = plot_visibility_chart(mock_objects, start_time, end_time)
        
        assert fig is not None
        assert ax is not None
        assert ax.get_title() == "Object Visibility"
        assert ax.get_xlabel() == "Local Time"
        assert ax.get_ylabel() == "Objects"
        
        plt.close(fig)

def test_plot_visibility_chart_with_schedule(mock_objects, time_range, mock_schedule):
    """Test desktop visibility chart with schedule"""
    start_time, end_time = time_range
    
    with patch('plots.visibility.desktop._find_visibility_window', return_value=[(start_time, end_time)]), \
         patch('plots.visibility.desktop._get_local_timezone', return_value=pytz.UTC):
        
        fig, ax = plot_visibility_chart(mock_objects, start_time, end_time, 
                                      schedule=mock_schedule, title="Scheduled Visibility")
        
        assert fig is not None
        assert ax is not None
        assert ax.get_title() == "Scheduled Visibility"
        
        # Check that legend exists (should have scheduled observation entry)
        legend = ax.get_legend()
        assert legend is not None
        
        plt.close(fig)

def test_create_mosaic_visibility_chart():
    """Test mosaic visibility chart creation"""
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    # Create mock mosaic groups
    mock_group = MockCelestialObject("Group 1", is_mosaic_group=True)
    overlap_periods = [(start_time + timedelta(hours=1), start_time + timedelta(hours=3))]
    groups = [(mock_group, overlap_periods)]
    
    fig, ax = create_mosaic_visibility_chart(groups, start_time, end_time)
    
    assert fig is not None
    assert ax is not None
    assert "Mosaic Groups Visibility Chart" in ax.get_title()
    
    plt.close(fig)

def test_create_mosaic_visibility_chart_empty():
    """Test mosaic visibility chart with empty groups"""
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    result = create_mosaic_visibility_chart([], start_time, end_time)
    
    assert result == (None, None)

def test_get_sorted_objects_for_chart(mock_objects, time_range):
    """Test object sorting for chart display"""
    start_time, end_time = time_range
    
    with patch('plots.visibility.desktop._find_visibility_window', return_value=[(start_time, end_time)]), \
         patch('plots.visibility.desktop._calculate_visibility_duration', return_value=timedelta(hours=4)), \
         patch('plots.visibility.desktop._get_local_timezone', return_value=pytz.UTC):
        
        sorted_objects = _get_sorted_objects_for_chart(mock_objects, start_time, end_time, use_margins=True)
        
        assert len(sorted_objects) == len(mock_objects)
        assert all(obj in mock_objects for obj in sorted_objects)

# Mobile visibility chart tests

def test_mobile_visibility_plotter_initialization():
    """Test mobile visibility plotter initialization"""
    plotter = MobileVisibilityPlotter()
    
    assert plotter.figure_size == (8, 6)
    assert plotter.dpi == 100
    assert plotter.font_size == 8
    assert plotter.max_objects == 8

def test_mobile_visibility_chart_creation(mock_objects, time_range):
    """Test mobile visibility chart creation"""
    start_time, end_time = time_range
    plotter = MobileVisibilityPlotter()
    
    fig = plotter.create_visibility_chart(mock_objects, start_time, end_time)
    
    assert fig is not None
    assert fig.get_size_inches()[0] == 8  # Width
    assert fig.get_size_inches()[1] == 6  # Height
    
    plt.close(fig)

def test_mobile_simple_visibility_chart(mock_objects, time_range):
    """Test mobile simple visibility chart"""
    start_time, end_time = time_range
    plotter = MobileVisibilityPlotter()
    
    fig = plotter.create_simple_visibility_chart(mock_objects, start_time, end_time)
    
    assert fig is not None
    assert fig.get_size_inches()[0] == 8
    assert fig.get_size_inches()[1] == 6
    
    plt.close(fig)

def test_mobile_visibility_chart_with_schedule(mock_objects, time_range, mock_schedule):
    """Test mobile visibility chart with schedule"""
    start_time, end_time = time_range
    plotter = MobileVisibilityPlotter()
    
    fig = plotter.create_visibility_chart(mock_objects, start_time, end_time, schedule=mock_schedule)
    
    assert fig is not None
    
    plt.close(fig)

def test_mobile_visibility_chart_object_limit():
    """Test mobile visibility chart object limiting"""
    # Create more objects than mobile limit
    many_objects = [MockCelestialObject(f"Object {i}") for i in range(15)]
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    plotter = MobileVisibilityPlotter()
    fig = plotter.create_visibility_chart(many_objects, start_time, end_time)
    
    assert fig is not None
    # Should limit to max_objects (8)
    
    plt.close(fig)

def test_mobile_visibility_chart_empty_objects():
    """Test mobile visibility chart with empty objects list"""
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    plotter = MobileVisibilityPlotter()
    fig = plotter.create_visibility_chart([], start_time, end_time)
    
    assert fig is not None
    # Should create error plot
    
    plt.close(fig)

# Convenience function tests

def test_create_mobile_visibility_chart_function(mock_objects, time_range):
    """Test convenience function for mobile visibility chart"""
    start_time, end_time = time_range
    
    fig = create_mobile_visibility_chart(mock_objects, start_time, end_time)
    
    assert fig is not None
    
    plt.close(fig)

def test_create_mobile_simple_visibility_chart_function(mock_objects, time_range):
    """Test convenience function for simple mobile visibility chart"""
    start_time, end_time = time_range
    
    fig = create_mobile_simple_visibility_chart(mock_objects, start_time, end_time)
    
    assert fig is not None
    
    plt.close(fig)

def test_create_mobile_multi_object_chart(mock_objects, time_range):
    """Test mobile multi-object chart with limiting"""
    start_time, end_time = time_range
    
    # Test with default limit
    fig = create_mobile_multi_object_chart(mock_objects, start_time, end_time)
    assert fig is not None
    plt.close(fig)
    
    # Test with custom limit
    fig = create_mobile_multi_object_chart(mock_objects, start_time, end_time, max_objects=2)
    assert fig is not None
    plt.close(fig)

def test_create_mobile_multi_object_chart_many_objects():
    """Test mobile multi-object chart with many objects"""
    many_objects = [MockCelestialObject(f"Object {i}") for i in range(10)]
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    fig = create_mobile_multi_object_chart(many_objects, start_time, end_time, max_objects=3)
    
    assert fig is not None
    
    plt.close(fig)

# Error handling tests

def test_mobile_visibility_chart_error_handling():
    """Test mobile visibility chart error handling"""
    plotter = MobileVisibilityPlotter()
    
    # Test with invalid time range
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time - timedelta(hours=1)  # End before start
    
    with patch.object(plotter, '_setup_mobile_chart', side_effect=Exception("Test error")):
        fig = plotter.create_visibility_chart([MockCelestialObject()], start_time, end_time)
        
        assert fig is not None  # Should create error plot
        
        plt.close(fig)

# Integration tests with verification framework

def test_plot_verification_desktop_visibility(mock_objects, time_range, verifier):
    """Test plot verification for desktop visibility charts"""
    start_time, end_time = time_range
    
    def unique_desktop_visibility_chart_plot():
        with patch('plots.visibility.desktop._find_visibility_window', return_value=[(start_time, end_time)]), \
             patch('plots.visibility.desktop._get_local_timezone', return_value=pytz.UTC):
            
            fig, ax = plot_visibility_chart(mock_objects, start_time, end_time, title="Test Visibility")
            return fig  # Return only the figure for verification
    
    # Test verification
    result = verifier.verify_plot(unique_desktop_visibility_chart_plot)
    assert result['match'] == True

def test_plot_verification_mobile_visibility(mock_objects, time_range, verifier):
    """Test plot verification for mobile visibility charts"""
    start_time, end_time = time_range
    
    def unique_mobile_visibility_chart_plot():
        return create_mobile_visibility_chart(mock_objects, start_time, end_time, title="Test Mobile")
    
    # Test verification
    result = verifier.verify_plot(unique_mobile_visibility_chart_plot)
    assert result['match'] == True

# Performance and optimization tests

def test_mobile_object_name_abbreviation():
    """Test mobile object name abbreviation"""
    plotter = MobileVisibilityPlotter()
    
    # Test normal name
    obj1 = MockCelestialObject("NGC 1234")
    assert plotter._get_mobile_object_name(obj1) == "NGC 1234"
    
    # Test name with slash
    obj2 = MockCelestialObject("M42/Orion Nebula")
    assert plotter._get_mobile_object_name(obj2) == "M42"
    
    # Test long name
    obj3 = MockCelestialObject("Very Long Object Name")
    assert len(plotter._get_mobile_object_name(obj3)) <= 8

def test_mobile_chart_formatting():
    """Test mobile chart formatting and layout"""
    mock_objects = [MockCelestialObject("Test")]
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    plotter = MobileVisibilityPlotter()
    fig = plotter.create_visibility_chart(mock_objects, start_time, end_time)
    
    # Check figure properties
    assert fig.get_dpi() == 100
    assert fig.get_size_inches()[0] == 8
    assert fig.get_size_inches()[1] == 6
    
    plt.close(fig)

# Integration with existing plotting system

def test_visibility_chart_integration():
    """Test integration with existing plotting system"""
    # Test that visibility functions can be imported from main plots module
    from plots import plot_visibility_chart, MobileVisibilityPlotter
    
    assert plot_visibility_chart is not None
    assert MobileVisibilityPlotter is not None
    
    # Test basic functionality
    mock_objects = [MockCelestialObject("Test")]
    start_time = datetime(2024, 1, 1, 20, 0, 0)
    end_time = start_time + timedelta(hours=8)
    
    with patch('plots.visibility.desktop._find_visibility_window', return_value=[(start_time, end_time)]), \
         patch('plots.visibility.desktop._get_local_timezone', return_value=pytz.UTC):
        
        fig, ax = plot_visibility_chart(mock_objects, start_time, end_time)
        assert fig is not None
        plt.close(fig)
    
    plotter = MobileVisibilityPlotter()
    fig = plotter.create_visibility_chart(mock_objects, start_time, end_time)
    assert fig is not None
    plt.close(fig) 