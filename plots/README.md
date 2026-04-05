# AstroScope Plotting Module

This module provides a comprehensive set of plotting utilities for the AstroScope application. It is designed to handle both desktop and mobile platforms while maintaining consistent output quality and performance.

## Directory Structure

```
plots/
├── __init__.py
├── base.py              # Base plotting utilities and common functions
├── trajectory/          # Trajectory plotting functions
├── visibility/          # Visibility chart functions
├── mosaic/             # Mosaic plotting functions
├── weekly/             # Weekly analysis plotting functions
└── utils/              # Utility functions and verification tools
```

## Features

- Common plotting utilities and configurations
- Platform-specific adaptations (desktop/mobile)
- Automated plot verification system
- Consistent styling and formatting
- Performance optimization for mobile devices

## Usage

### Basic Plot Setup

```python
from plots.base import setup_plot, PlotConfig

# Create a plot with default settings
fig, ax = setup_plot()

# Or with custom configuration
config = PlotConfig(
    figure_size=(12, 8),
    dpi=150,
    font_size=14,
    style='seaborn'
)
fig, ax = setup_plot(config)
```

### Alt-Az Plot Setup

```python
from plots.base import setup_altaz_plot

# Create an Alt-Az plot with proper axis labels and grid
fig, ax = setup_altaz_plot()
```

### Plot Verification

```python
from plots.utils.verification import PlotVerifier

# Initialize verifier
verifier = PlotVerifier()

# Verify a plot function
result = verifier.verify_plot(my_plot_function)

# Verify plot metadata
metadata = {
    'title': 'My Plot',
    'data_points': 100
}
result = verifier.verify_metadata(my_plot_function, metadata)
```

## Testing

Run the test suite with:

```bash
pytest tests/
```

For coverage report:

```bash
pytest --cov=plots tests/
```

## Contributing

1. Follow the established directory structure
2. Add appropriate tests for new functionality
3. Update documentation as needed
4. Ensure mobile compatibility
5. Run the test suite before submitting changes

## Notes

- Each plot type has its own module for better organization
- Mobile adaptations are implemented alongside desktop functions
- The verification system ensures consistency across platforms
- Performance is optimized for both desktop and mobile use 