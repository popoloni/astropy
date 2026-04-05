# Legacy Scripts

This folder contains scripts that are no longer actively used in the main astronightplanner system but are preserved for reference and compatibility.

## Contents

### Core Legacy Scripts

### `astropy_legacy.py`
- **Purpose**: The original astronightplanner.py file before the mosaic integration
- **Status**: Superseded by the main astronightplanner.py with integrated mosaic functionality
- **Use case**: Reference implementation for comparison and rollback if needed

### `astronightplanner_legacy.py`
- **Purpose**: Complete legacy version of the night planner with original plotting functions
- **Status**: Replaced by modular system using shared plotting libraries
- **Use case**: Reference for original plotting behavior and complete functionality

### `astroseasonplanner_legacy.py`
- **Purpose**: Complete legacy version of the seasonal trajectory analyzer
- **Status**: Replaced by modular system using shared libraries
- **Use case**: Reference for original analysis methods and seasonal planning

### `plot_mosaic_trajectories.py`
- **Purpose**: Original standalone mosaic trajectory plotting script
- **Status**: Functionality integrated into main astronightplanner.py
- **Use case**: Reference for the original mosaic-only approach

### Utility Legacy Scripts

### `constellation_visualizer_legacy.py`
- **Purpose**: Original monolithic constellation plotting script
- **Status**: Replaced by modular version using shared `plots.constellation` library
- **Use case**: Reference for original matplotlib-based constellation visualization

### `show_all_constellations_legacy.py`
- **Purpose**: Original complete SVG constellation visualizer with Pythonista integration
- **Status**: Replaced by version using shared calculation and plotting libraries
- **Use case**: Reference for full SVG functionality and Pythonista WebView integration

### Development Archives

### `test_mosaic_integration.py`
- **Purpose**: Early integration test script
- **Status**: Superseded by comprehensive_test.py in utilities/
- **Use case**: Historical reference for integration testing approach

## Migration Notes

All functionality from these legacy scripts has been integrated into the main `astronightplanner.py` system:

- **Mosaic analysis**: Now available via `--mosaic`, `--mosaic-only`, and `--schedule mosaic_groups`
- **Trajectory plotting**: Integrated with enhanced mosaic-specific plots
- **Testing**: Comprehensive test suite available in `utilities/`

## Usage (if needed)

These scripts can still be run if needed for comparison or debugging:

```bash
# Run legacy astropy (from legacy/ directory)
python3 astropy_legacy.py --report-only

# Run original mosaic plotting (from legacy/ directory)
python3 plot_mosaic_trajectories.py
```

**Note**: Legacy scripts may have different dependencies or configurations than the current system. 