# Legacy Scripts

This folder contains scripts that are no longer actively used in the main astropy system but are preserved for reference and compatibility.

## Contents

### `astropy_legacy.py`
- **Purpose**: The original astropy.py file before the mosaic integration
- **Status**: Superseded by the main astropy.py with integrated mosaic functionality
- **Use case**: Reference implementation for comparison and rollback if needed

### `plot_mosaic_trajectories.py`
- **Purpose**: Original standalone mosaic trajectory plotting script
- **Status**: Functionality integrated into main astropy.py
- **Use case**: Reference for the original mosaic-only approach

### `tests/legacy/test_mosaic_integration.py`
- **Purpose**: Early integration test script
- **Status**: Moved to tests/legacy/ directory
- **Use case**: Historical reference for integration testing approach

## Migration Notes

All functionality from these legacy scripts has been integrated into the main `astropy.py` system:

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