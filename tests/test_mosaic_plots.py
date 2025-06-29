"""
Tests for mosaic plotting functions.

This module tests both desktop and mobile mosaic plotting functionality,
including trajectory plots, grid plots, FOV indicators, and error handling.
"""

import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from unittest.mock import Mock, patch

# Import the functions to test
from plots.mosaic import (
    plot_mosaic_fov_indicator,
    calculate_group_center_position,
    plot_mosaic_group_trajectory,
    plot_mosaic_fov_at_optimal_time,
    create_mosaic_trajectory_plot,
    create_mosaic_grid_plot,
    analyze_group_visibility_overlap,
    create_mosaic_summary_plot,
    MobileMosaicPlotter,
    create_mobile_mosaic_trajectory_plot,
    create_mobile_simple_mosaic_plot,
    create_mobile_mosaic_grid_plot
)
from plots.utils.verification import PlotVerifier

class MockMosaicObject:
    """Mock object for testing"""
    def __init__(self, name):
        self.name = name
        self.ra = 10.0
        self.dec = 20.0

class MockMosaicGroup:
    """Mock mosaic group for testing"""
    def __init__(self, objects, overlap_periods=None):
        self.objects = objects
        self.overlap_periods = overlap_periods or []

@pytest.fixture
def test_objects():
    """Create test objects for mosaic groups"""
    return [
        MockMosaicObject("NGC 1234"),
        MockMosaicObject("M42"),
        MockMosaicObject("IC 5070")
    ]

@pytest.fixture
def test_groups(test_objects):
    """Create test mosaic groups"""
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=4)
    
    group1 = MockMosaicGroup(
        test_objects[:2],
        [(start_time, start_time + timedelta(hours=2))]
    )
    group2 = MockMosaicGroup(
        test_objects[1:],
        [(start_time + timedelta(hours=1), end_time)]
    )
    
    return [group1, group2]

@pytest.fixture
def test_times():
    """Create test time range"""
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=8)
    return start_time, end_time

# Desktop Mosaic Tests

def test_plot_mosaic_fov_indicator():
    """Test FOV indicator plotting"""
    fig, ax = plt.subplots()
    
    # Test basic FOV indicator
    plot_mosaic_fov_indicator(ax, 45.0, 180.0, 4.0, 3.0)
    
    # Check that patches were added
    assert len(ax.patches) > 0
    assert len(ax.texts) > 0
    
    plt.close(fig)

def test_calculate_group_center_position(test_groups):
    """Test group center position calculation"""
    group = test_groups[0]
    test_time = datetime(2024, 1, 1, 22, 0, tzinfo=pytz.UTC)
    
    with patch('plots.mosaic.desktop.calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.mosaic.desktop.is_visible', return_value=True):
        
        center_alt, center_az = calculate_group_center_position(group, test_time)
        
        assert center_alt is not None
        assert center_az is not None
        assert isinstance(center_alt, float)
        assert isinstance(center_az, float)

def test_calculate_group_center_position_no_visible_objects(test_groups):
    """Test group center position when no objects are visible"""
    group = test_groups[0]
    test_time = datetime(2024, 1, 1, 22, 0, tzinfo=pytz.UTC)
    
    with patch('plots.mosaic.desktop.calculate_altaz', return_value=(10.0, 180.0)), \
         patch('plots.mosaic.desktop.is_visible', return_value=False):
        
        center_alt, center_az = calculate_group_center_position(group, test_time)
        
        assert center_alt is None
        assert center_az is None

def test_plot_mosaic_group_trajectory(test_groups, test_times):
    """Test mosaic group trajectory plotting"""
    fig, ax = plt.subplots()
    start_time, end_time = test_times
    group = test_groups[0]
    
    # Test that the function can be called without errors
    # We'll mock the complex internal calculations
    with patch('plots.mosaic.desktop.calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.mosaic.desktop.is_visible', return_value=True), \
         patch('plots.mosaic.desktop.utc_to_local', return_value=start_time), \
         patch('plots.utils.common.get_abbreviated_name', return_value='NGC1234'), \
         patch('plots.utils.common.calculate_label_offset', return_value=(10, 10)):
        
        # The function should run without error and return a list
        existing_positions = plot_mosaic_group_trajectory(
            ax, group, start_time, end_time, 'red', 1, show_labels=True
        )
        
        # Verify the function returns the expected type
        assert isinstance(existing_positions, list)
    
    plt.close(fig)

def test_plot_mosaic_fov_at_optimal_time(test_groups):
    """Test FOV plotting at optimal time"""
    fig, ax = plt.subplots()
    group = test_groups[0]
    
    with patch('plots.mosaic.desktop.calculate_group_center_position', return_value=(45.0, 180.0)):
        plot_mosaic_fov_at_optimal_time(ax, group, group.overlap_periods, 'blue')
        
        # Check that patches were added for FOV
        assert len(ax.patches) > 0
    
    plt.close(fig)

def test_create_mosaic_trajectory_plot(test_groups, test_times):
    """Test main mosaic trajectory plot creation"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.desktop.setup_altaz_plot', return_value=(plt.figure(), plt.gca())), \
         patch('plots.mosaic.desktop.plot_moon_trajectory'), \
         patch('plots.mosaic.desktop.plot_mosaic_group_trajectory', return_value=[]), \
         patch('plots.mosaic.desktop.plot_mosaic_fov_at_optimal_time'):
        
        fig, ax = create_mosaic_trajectory_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        assert ax is not None
        
        plt.close(fig)

def test_create_mosaic_grid_plot(test_groups, test_times):
    """Test mosaic grid plot creation"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.desktop.plot_moon_trajectory_no_legend'), \
         patch('plots.mosaic.desktop.plot_mosaic_group_trajectory', return_value=[]), \
         patch('plots.mosaic.desktop.plot_mosaic_fov_at_optimal_time'):
        
        fig, axes = create_mosaic_grid_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        assert axes is not None
        
        plt.close(fig)

def test_create_mosaic_grid_plot_empty():
    """Test mosaic grid plot with empty groups"""
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=8)
    
    fig, axes = create_mosaic_grid_plot([], start_time, end_time)
    
    assert fig is None
    assert axes is None

def test_analyze_group_visibility_overlap(test_groups, test_times):
    """Test group visibility overlap analysis"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.desktop.calculate_group_center_position', return_value=(45.0, 180.0)):
        analysis = analyze_group_visibility_overlap(test_groups, start_time, end_time)
        
        assert isinstance(analysis, dict)
        assert len(analysis) == len(test_groups)
        
        for group_num, results in analysis.items():
            assert 'objects' in results
            assert 'overlap_periods' in results
            assert 'total_overlap_hours' in results
            assert 'optimal_time' in results
            assert 'center_position' in results
            assert 'object_count' in results

def test_create_mosaic_summary_plot(test_groups, test_times):
    """Test mosaic summary plot creation"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.desktop.setup_altaz_plot', return_value=(plt.figure(), plt.gca())), \
         patch('plots.mosaic.desktop.plot_moon_trajectory'), \
         patch('plots.mosaic.desktop.analyze_group_visibility_overlap') as mock_analyze:
        
        # Mock analysis results
        mock_analyze.return_value = {
            1: {
                'objects': test_groups[0].objects,
                'overlap_periods': test_groups[0].overlap_periods,
                'total_overlap_hours': 2.0,
                'optimal_time': start_time + timedelta(hours=1),
                'center_position': (45.0, 180.0),
                'object_count': 2
            }
        }
        
        fig, ax = create_mosaic_summary_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        assert ax is not None
        
        plt.close(fig)

# Mobile Mosaic Tests

def test_mobile_mosaic_plotter_initialization():
    """Test mobile mosaic plotter initialization"""
    plotter = MobileMosaicPlotter()
    
    assert plotter.figure_size == (8, 6)
    assert plotter.dpi == 100
    assert plotter.font_size == 8
    assert plotter.max_groups == 6

def test_mobile_mosaic_trajectory_plot_creation(test_groups, test_times):
    """Test mobile mosaic trajectory plot creation"""
    start_time, end_time = test_times
    plotter = MobileMosaicPlotter()
    
    with patch.object(plotter, '_calculate_mobile_group_center', return_value=(45.0, 180.0)):
        fig = plotter.create_mosaic_trajectory_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        plt.close(fig)

def test_mobile_simple_mosaic_plot(test_groups, test_times):
    """Test mobile simple mosaic plot creation"""
    start_time, end_time = test_times
    plotter = MobileMosaicPlotter()
    
    with patch.object(plotter, '_calculate_mobile_group_center', return_value=(45.0, 180.0)):
        fig = plotter.create_simple_mosaic_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        plt.close(fig)

def test_mobile_mosaic_grid_plot(test_groups, test_times):
    """Test mobile mosaic grid plot creation"""
    start_time, end_time = test_times
    plotter = MobileMosaicPlotter()
    
    with patch.object(plotter, '_calculate_mobile_group_center', return_value=(45.0, 180.0)):
        fig = plotter.create_mosaic_grid_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        plt.close(fig)

def test_mobile_mosaic_group_limiting():
    """Test mobile group limiting functionality"""
    # Create many groups (more than mobile limit)
    many_groups = []
    for i in range(10):
        group = MockMosaicGroup([MockMosaicObject(f"Object {i}")])
        many_groups.append(group)
    
    plotter = MobileMosaicPlotter()
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=8)
    
    with patch.object(plotter, '_calculate_mobile_group_center', return_value=(45.0, 180.0)):
        fig = plotter.create_mosaic_trajectory_plot(many_groups, start_time, end_time)
        
        assert fig is not None
        plt.close(fig)

def test_mobile_mosaic_empty_groups():
    """Test mobile mosaic plotting with empty groups"""
    plotter = MobileMosaicPlotter()
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=8)
    
    fig = plotter.create_mosaic_trajectory_plot([], start_time, end_time)
    
    assert fig is not None  # Should return error plot
    plt.close(fig)

def test_mobile_mosaic_error_handling():
    """Test mobile mosaic error handling"""
    plotter = MobileMosaicPlotter()
    start_time = datetime(2024, 1, 1, 20, 0, tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=8)
    
    # Test with None groups
    fig = plotter.create_mosaic_trajectory_plot(None, start_time, end_time)
    
    assert fig is not None  # Should return error plot
    plt.close(fig)

# Convenience Function Tests

def test_create_mobile_mosaic_trajectory_plot_function(test_groups, test_times):
    """Test convenience function for mobile mosaic trajectory plot"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.mobile.MobileMosaicPlotter') as mock_plotter_class:
        mock_plotter = Mock()
        mock_plotter.create_mosaic_trajectory_plot.return_value = plt.figure()
        mock_plotter_class.return_value = mock_plotter
        
        fig = create_mobile_mosaic_trajectory_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        mock_plotter.create_mosaic_trajectory_plot.assert_called_once()
        plt.close(fig)

def test_create_mobile_simple_mosaic_plot_function(test_groups, test_times):
    """Test convenience function for mobile simple mosaic plot"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.mobile.MobileMosaicPlotter') as mock_plotter_class:
        mock_plotter = Mock()
        mock_plotter.create_simple_mosaic_plot.return_value = plt.figure()
        mock_plotter_class.return_value = mock_plotter
        
        fig = create_mobile_simple_mosaic_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        mock_plotter.create_simple_mosaic_plot.assert_called_once()
        plt.close(fig)

def test_create_mobile_mosaic_grid_plot_function(test_groups, test_times):
    """Test convenience function for mobile mosaic grid plot"""
    start_time, end_time = test_times
    
    with patch('plots.mosaic.mobile.MobileMosaicPlotter') as mock_plotter_class:
        mock_plotter = Mock()
        mock_plotter.create_mosaic_grid_plot.return_value = plt.figure()
        mock_plotter_class.return_value = mock_plotter
        
        fig = create_mobile_mosaic_grid_plot(test_groups, start_time, end_time)
        
        assert fig is not None
        mock_plotter.create_mosaic_grid_plot.assert_called_once()
        plt.close(fig)

# Verification Tests

def test_plot_verification_desktop_mosaic():
    """Test plot verification for desktop mosaic functions"""
    verifier = PlotVerifier()
    
    # Create a simple test function that returns a figure
    def test_mosaic_plot():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_title("Test Mosaic Plot")
        return fig
    
    # Test verification
    result = verifier.verify_plot(test_mosaic_plot)
    assert result is not None

def test_plot_verification_mobile_mosaic():
    """Test plot verification for mobile mosaic functions"""
    verifier = PlotVerifier()
    
    # Create a simple test function that returns a figure
    def test_mobile_mosaic_plot():
        fig = plt.figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_title("Test Mobile Mosaic Plot")
        return fig
    
    # Test verification
    result = verifier.verify_plot(test_mobile_mosaic_plot)
    assert result is not None

# Integration Tests

def test_mosaic_chart_integration(test_groups, test_times):
    """Test complete mosaic chart integration"""
    start_time, end_time = test_times
    
    # Test that we can import and use all functions
    from plots import (
        create_mosaic_trajectory_plot,
        create_mosaic_grid_plot,
        MobileMosaicPlotter,
        create_mobile_mosaic_trajectory_plot
    )
    
    # Test desktop functions
    with patch('plots.mosaic.desktop.setup_altaz_plot', return_value=(plt.figure(), plt.gca())), \
         patch('plots.mosaic.desktop.plot_moon_trajectory'), \
         patch('plots.mosaic.desktop.plot_mosaic_group_trajectory', return_value=[]), \
         patch('plots.mosaic.desktop.plot_mosaic_fov_at_optimal_time'):
        
        fig, ax = create_mosaic_trajectory_plot(test_groups, start_time, end_time)
        assert fig is not None
        plt.close(fig)
    
    # Test mobile functions
    with patch('plots.mosaic.mobile.MobileMosaicPlotter.create_mosaic_trajectory_plot', return_value=plt.figure()):
        fig = create_mobile_mosaic_trajectory_plot(test_groups, start_time, end_time)
        assert fig is not None
        plt.close(fig)

def test_mobile_object_name_abbreviation():
    """Test mobile object name abbreviation"""
    plotter = MobileMosaicPlotter()
    
    # Test normal name
    obj1 = MockMosaicObject("M42")
    assert plotter._get_mobile_object_name(obj1) == "M42"
    
    # Test long name
    obj2 = MockMosaicObject("NGC 1234 Very Long Name")
    abbreviated = plotter._get_mobile_object_name(obj2)
    assert len(abbreviated) <= 8

def test_mobile_group_name_generation():
    """Test mobile group name generation"""
    plotter = MobileMosaicPlotter()
    
    # Test single object group
    group1 = MockMosaicGroup([MockMosaicObject("M42")])
    name1 = plotter._get_mobile_group_name(group1, 1)
    assert "G1:" in name1
    assert "M42" in name1
    
    # Test multi-object group
    group2 = MockMosaicGroup([
        MockMosaicObject("M42"),
        MockMosaicObject("NGC 1234"),
        MockMosaicObject("IC 5070")
    ])
    name2 = plotter._get_mobile_group_name(group2, 2)
    assert "G2:" in name2
    assert "+1" in name2  # Should show +1 for the third object

def test_mobile_chart_formatting():
    """Test mobile chart formatting"""
    plotter = MobileMosaicPlotter()
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    
    # Test formatting application
    plotter._apply_mobile_formatting(fig, ax)
    
    # Check that formatting was applied (basic check)
    assert fig.get_size_inches()[0] == 8
    assert fig.get_size_inches()[1] == 6
    
    plt.close(fig) 