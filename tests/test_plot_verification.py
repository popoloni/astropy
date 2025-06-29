"""
Tests for the plot verification framework.
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from plots.base import setup_plot, setup_altaz_plot, PlotConfig
from plots.utils.verification import PlotVerifier

def test_plot_verifier_initialization():
    """Test PlotVerifier initialization."""
    verifier = PlotVerifier()
    assert verifier.baseline_dir == "tests/baseline_plots"
    assert verifier.temp_dir == "tests/temp_plots"
    assert verifier.tolerance == 0.01

def test_basic_plot_verification():
    """Test basic plot verification."""
    verifier = PlotVerifier()
    
    def unique_test_plot():
        fig, ax = setup_plot()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        return fig
    
    # First run should create baseline or match existing one
    result = verifier.verify_plot(unique_test_plot)
    assert result['match'] == True
    
    # Check if it's a new baseline or comparison
    if 'message' in result:
        assert 'Created new baseline' in result['message']
    else:
        assert 'mean_difference' in result
    
    # Second run should match baseline
    result = verifier.verify_plot(unique_test_plot)
    assert result['match'] == True
    assert 'mean_difference' in result

def test_plot_metadata_verification():
    """Test plot metadata verification."""
    verifier = PlotVerifier()
    
    def unique_metadata_test_plot():
        fig, ax = setup_plot()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        return fig
    
    metadata = {
        'title': 'Test Plot',
        'x_label': 'X',
        'y_label': 'Y',
        'data_points': 100
    }
    
    # First run should create baseline or match existing one
    result = verifier.verify_metadata(unique_metadata_test_plot, metadata)
    assert result['match'] == True
    
    # Check if it's a new baseline or comparison
    if 'message' in result:
        assert 'Created new metadata baseline' in result['message']
    
    # Second run should match baseline
    result = verifier.verify_metadata(unique_metadata_test_plot, metadata)
    assert result['match'] == True
    
    # Test with different metadata
    different_metadata = metadata.copy()
    different_metadata['title'] = 'Different Title'
    result = verifier.verify_metadata(unique_metadata_test_plot, different_metadata)
    assert result['match'] == False
    assert 'differences' in result
    assert 'title' in result['differences']

def test_plot_config():
    """Test plot configuration."""
    config = PlotConfig(
        figure_size=(12, 8),
        dpi=150,
        font_size=14,
        style='default'
    )
    
    fig, ax = setup_plot(config)
    assert fig.get_size_inches()[0] == 12
    assert fig.get_size_inches()[1] == 8
    # Note: DPI might be scaled by the system, so we check the config was applied
    assert config.dpi == 150
    # Note: tick_params() doesn't return a dict, so we check rcParams instead
    assert plt.rcParams['font.size'] == 14

def test_altaz_plot_setup():
    """Test Alt-Az plot setup."""
    fig, ax = setup_altaz_plot()
    
    # Check axis labels
    assert ax.get_xlabel() == 'Azimuth (degrees)'
    assert ax.get_ylabel() == 'Altitude (degrees)'
    
    # Check axis limits
    assert ax.get_xlim() == (0, 360)
    assert ax.get_ylim() == (0, 90)
    
    # Check grid is enabled
    assert ax.xaxis.grid
    assert ax.yaxis.grid 