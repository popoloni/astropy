"""
Pytest configuration for the plots module tests.
"""

import matplotlib
import pytest

def pytest_configure(config):
    """Configure matplotlib for testing"""
    matplotlib.use('Agg')  # Use non-interactive backend for testing

@pytest.fixture(autouse=True)
def setup_matplotlib():
    """Ensure matplotlib uses non-interactive backend for all tests"""
    import matplotlib.pyplot as plt
    plt.ioff()  # Turn off interactive mode
    yield
    plt.close('all')  # Clean up all figures after each test 