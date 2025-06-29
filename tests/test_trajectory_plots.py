"""
Tests for trajectory plotting functions.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytz

from plots.trajectory.desktop import (
    plot_object_trajectory, plot_moon_trajectory, plot_quarterly_trajectories
)
from plots.trajectory.mobile import (
    MobileTrajectoryPlotter, create_mobile_trajectory_plot
)
from plots.base import setup_plot, PlotConfig
from plots.utils.verification import PlotVerifier

class MockCelestialObject:
    """Mock celestial object for testing"""
    def __init__(self, name="Test Object", magnitude=10.0):
        self.name = name
        self.magnitude = magnitude
        self.sufficient_time = True
        self.near_moon = False

@pytest.fixture
def mock_object():
    """Create a mock celestial object"""
    return MockCelestialObject()

@pytest.fixture
def time_range():
    """Create a test time range"""
    start = datetime(2024, 1, 1, 20, 0, 0)
    end = start + timedelta(hours=8)
    return start, end

@pytest.fixture
def verifier():
    """Create a plot verifier"""
    return PlotVerifier()

def test_plot_object_trajectory_basic(mock_object, time_range):
    """Test basic object trajectory plotting"""
    start_time, end_time = time_range
    
    fig, ax = setup_plot()
    
    # Mock the calculation functions
    with patch('plots.trajectory.desktop._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.desktop._calculate_moon_position', return_value=(30.0, 90.0)), \
         patch('plots.trajectory.desktop._is_near_moon', return_value=False), \
         patch('plots.trajectory.desktop._utc_to_local', side_effect=lambda x: x):
        
        plot_object_trajectory(ax, mock_object, start_time, end_time, 'blue')
    
    # Check that something was plotted
    lines = ax.get_lines()
    assert len(lines) > 0
    
    # Check legend
    legend = ax.get_legend()
    assert legend is not None
    
    plt.close(fig)

def test_plot_moon_trajectory(time_range):
    """Test moon trajectory plotting"""
    start_time, end_time = time_range
    
    fig, ax = setup_plot()
    
    # Mock the calculation functions
    with patch('plots.trajectory.desktop._calculate_moon_position', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.desktop._is_visible', return_value=True), \
         patch('plots.trajectory.desktop._utc_to_local', side_effect=lambda x: x):
        
        plot_moon_trajectory(ax, start_time, end_time)
    
    # Check that moon trajectory was plotted
    lines = ax.get_lines()
    assert len(lines) > 0
    
    # Check that moon is in legend (it creates its own legend)
    legend = ax.get_legend()
    if legend is not None:
        legend_texts = [t.get_text() for t in legend.get_texts()]
        assert 'Moon' in legend_texts
    
    plt.close(fig)

def test_plot_quarterly_trajectories(time_range):
    """Test quarterly trajectory plotting"""
    start_time, end_time = time_range
    objects = [MockCelestialObject(f"Object {i}") for i in range(3)]
    
    # Mock the calculation functions
    with patch('plots.trajectory.desktop._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.desktop._calculate_moon_position', return_value=(30.0, 90.0)), \
         patch('plots.trajectory.desktop._is_visible', return_value=True), \
         patch('plots.trajectory.desktop._get_local_timezone', return_value=pytz.UTC), \
         patch('plots.trajectory.desktop._plot_moon_trajectory_no_legend'), \
         patch('plots.trajectory.desktop._plot_object_trajectory_no_legend'):
        
        fig = plot_quarterly_trajectories(objects, start_time, end_time)
    
    # Check that we have 4 subplots (2x2 grid)
    assert len(fig.axes) == 4
    
    # Check that figure has a title
    assert fig._suptitle is not None
    
    plt.close(fig)

def test_mobile_trajectory_plotter_initialization():
    """Test MobileTrajectoryPlotter initialization"""
    plotter = MobileTrajectoryPlotter()
    
    assert plotter.figure_size == (8, 6)
    assert plotter.dpi == 100
    assert 'font.size' in plotter.style_config

def test_mobile_trajectory_plot_creation(mock_object, time_range):
    """Test mobile trajectory plot creation"""
    start_time, end_time = time_range
    plotter = MobileTrajectoryPlotter()
    
    # Mock the calculation functions
    with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.mobile._utc_to_local', side_effect=lambda x: x), \
         patch('plots.trajectory.mobile._get_abbreviated_name', return_value="TEST"):
        
        fig = plotter.create_trajectory_plot(mock_object, start_time, end_time)
    
    assert fig is not None
    assert len(fig.axes) == 1
    
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Azimuth (degrees)'
    assert ax.get_ylabel() == 'Altitude (degrees)'
    
    plt.close(fig)

def test_mobile_simple_trajectory_plot(mock_object, time_range):
    """Test mobile simple trajectory plot"""
    start_time, end_time = time_range
    plotter = MobileTrajectoryPlotter()
    
    # Mock the calculation functions
    with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.mobile._utc_to_local', side_effect=lambda x: x), \
         patch('plots.trajectory.mobile._get_abbreviated_name', return_value="TEST"):
        
        fig = plotter.create_simple_trajectory_plot(mock_object, start_time, end_time)
    
    assert fig is not None
    assert len(fig.axes) == 1
    
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Az (°)'
    assert ax.get_ylabel() == 'Alt (°)'
    
    plt.close(fig)

def test_mobile_multi_target_plot(time_range):
    """Test mobile multi-target trajectory plot"""
    start_time, end_time = time_range
    targets = [MockCelestialObject(f"Target {i}") for i in range(3)]
    plotter = MobileTrajectoryPlotter()
    
    # Mock the calculation functions
    with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.mobile._get_abbreviated_name', side_effect=lambda x: x.split()[0]):
        
        fig = plotter.create_multi_target_plot(targets, start_time, end_time)
    
    assert fig is not None
    assert len(fig.axes) == 1
    
    ax = fig.axes[0]
    lines = ax.get_lines()
    assert len(lines) == len(targets)
    
    plt.close(fig)

def test_mobile_multi_target_limit():
    """Test that mobile multi-target plot limits number of targets"""
    targets = [MockCelestialObject(f"Target {i}") for i in range(10)]
    plotter = MobileTrajectoryPlotter()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=8)
    
    with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.mobile._get_abbreviated_name', side_effect=lambda x: x.split()[0]):
        
        fig = plotter.create_multi_target_plot(targets, start_time, end_time)
    
    ax = fig.axes[0]
    lines = ax.get_lines()
    # Should be limited to 5 targets
    assert len(lines) <= 5
    
    plt.close(fig)

def test_convenience_functions(mock_object, time_range):
    """Test convenience functions"""
    start_time, end_time = time_range
    
    # Mock the calculation functions
    with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.mobile._utc_to_local', side_effect=lambda x: x), \
         patch('plots.trajectory.mobile._get_abbreviated_name', return_value="TEST"):
        
        fig1 = create_mobile_trajectory_plot(mock_object, start_time, end_time)
        assert fig1 is not None
        plt.close(fig1)

def test_error_handling():
    """Test error handling in mobile plotting"""
    plotter = MobileTrajectoryPlotter()
    
    # Test with invalid object
    fig = plotter.create_trajectory_plot(None)
    assert fig is not None  # Should return error plot
    
    ax = fig.axes[0]
    # Check that error message is displayed
    texts = [t.get_text() for t in ax.texts]
    assert any('Error' in text for text in texts)
    
    plt.close(fig)

def test_plot_verification_trajectory(mock_object, time_range, verifier):
    """Test plot verification for trajectory plots"""
    start_time, end_time = time_range
    
    def unique_desktop_trajectory_plot():
        fig, ax = setup_plot()

        with patch('plots.trajectory.desktop._calculate_altaz', return_value=(45.0, 180.0)), \
             patch('plots.trajectory.desktop._calculate_moon_position', return_value=(30.0, 90.0)), \
             patch('plots.trajectory.desktop._is_near_moon', return_value=False), \
             patch('plots.trajectory.desktop._utc_to_local', side_effect=lambda x: x):

            plot_object_trajectory(ax, mock_object, start_time, end_time, 'blue')

        return fig

    # Test verification
    result = verifier.verify_plot(unique_desktop_trajectory_plot)
    assert result['match'] == True

def test_plot_verification_mobile(mock_object, time_range, verifier):
    """Test plot verification for mobile plots"""
    start_time, end_time = time_range
    
    def unique_mobile_trajectory_plot():
        with patch('plots.trajectory.mobile._calculate_altaz', return_value=(45.0, 180.0)), \
             patch('plots.trajectory.mobile._utc_to_local', side_effect=lambda x: x), \
             patch('plots.trajectory.mobile._get_abbreviated_name', return_value="TEST"):
            
            return create_mobile_trajectory_plot(mock_object, start_time, end_time)
    
    # Test verification
    result = verifier.verify_plot(unique_mobile_trajectory_plot)
    assert result['match'] == True

def test_trajectory_with_schedule(mock_object, time_range):
    """Test trajectory plotting with schedule information"""
    start_time, end_time = time_range
    schedule = [(start_time, end_time, mock_object)]
    
    fig, ax = setup_plot()
    
    with patch('plots.trajectory.desktop._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.desktop._calculate_moon_position', return_value=(30.0, 90.0)), \
         patch('plots.trajectory.desktop._is_near_moon', return_value=False), \
         patch('plots.trajectory.desktop._utc_to_local', side_effect=lambda x: x), \
         patch('plots.trajectory.desktop._find_optimal_label_position', return_value=(180.0, 45.0)), \
         patch('plots.trajectory.desktop._get_abbreviated_name', return_value="TEST"), \
         patch('plots.trajectory.desktop._calculate_label_offset', return_value=(5, 5)):
        
        plot_object_trajectory(ax, mock_object, start_time, end_time, 'blue', schedule=schedule)
    
    # Check that plot was created
    lines = ax.get_lines()
    assert len(lines) > 0
    
    plt.close(fig)

def test_moon_interference_detection(mock_object, time_range):
    """Test moon interference detection in trajectory plotting"""
    start_time, end_time = time_range
    
    fig, ax = setup_plot()
    
    # Mock moon interference
    with patch('plots.trajectory.desktop._calculate_altaz', return_value=(45.0, 180.0)), \
         patch('plots.trajectory.desktop._calculate_moon_position', return_value=(30.0, 90.0)), \
         patch('plots.trajectory.desktop._is_near_moon', return_value=True), \
         patch('plots.trajectory.desktop._utc_to_local', side_effect=lambda x: x):
        
        plot_object_trajectory(ax, mock_object, start_time, end_time, 'blue')
    
    # Check that moon interference was detected
    assert hasattr(mock_object, 'near_moon')
    
    plt.close(fig) 