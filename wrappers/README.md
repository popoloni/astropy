# Astropy Wrapper Scripts

This directory contains convenient wrapper scripts for running specific astropy functionalities, optimized for both standard Python environments and iOS Pythonista.

## 📱 Pythonista Compatibility

All wrapper scripts are designed to work seamlessly in iOS Pythonista without subprocess dependencies. They use direct function calls and argument manipulation to provide the same functionality as command-line usage.

## 🎯 Available Wrappers

### Scheduling Strategy Wrappers

#### `run_longest_duration.py`
- **Purpose**: Prioritizes objects with longest visibility windows
- **Best for**: Deep sky imaging and extended exposures
- **Usage**: Perfect for nights when you want to focus on fewer objects with maximum exposure time

#### `run_max_objects.py`
- **Purpose**: Maximizes the number of observable objects
- **Best for**: Survey nights and star hopping sessions
- **Usage**: Ideal for exploring many different targets in one night

#### `run_optimal_snr.py`
- **Purpose**: Optimizes for best imaging conditions and signal-to-noise ratio
- **Best for**: High-quality astrophotography
- **Usage**: Use when you want the best possible image quality

### Mosaic-Specific Wrappers

#### `run_mosaic_analysis.py` ⭐
- **Purpose**: Comprehensive mosaic analysis and planning tool
- **Features**:
  - Detailed mosaic group identification
  - Trajectory plotting for all groups
  - Mosaic-optimized scheduling
  - Complete planning report
- **Usage**: **This replaces the old `plot_mosaic_trajectories.py` functionality**
- **Best for**: Advanced mosaic planning and optimization

### General Purpose Wrappers

#### `run_report_only.py`
- **Purpose**: Generates observation reports without plots
- **Best for**: Quick planning and text-based analysis
- **Usage**: Fast report generation for planning purposes

#### `run_with_plots.py`
- **Purpose**: Generates full reports with trajectory plots
- **Best for**: Complete visual analysis
- **Usage**: When you want both reports and visual plots

#### `run_quarters.py`
- **Purpose**: Generates quarterly trajectory plots
- **Best for**: Long-term planning and seasonal analysis
- **Usage**: Planning across multiple months

#### `run_quarters_report.py`
- **Purpose**: Quarterly analysis with reports
- **Best for**: Seasonal planning with detailed text analysis
- **Usage**: Comprehensive quarterly planning

#### `run_test_simulation.py`
- **Purpose**: Runs time simulation testing
- **Best for**: Testing different dates and scenarios
- **Usage**: Development and testing purposes

## 🚀 Usage Examples

### Standard Python Environment:
```bash
# 🆕 NEW: Dedicated mosaic multi-night planner (moved to root)
python3 astromultinightplanner.py

# Standard mosaic analysis (shows individuals + groups)
python3 astronightplanner.py --mosaic

# Clean mosaic analysis (groups only, no individual duplicates)
python3 astronightplanner.py --mosaic --no-duplicates

# Longest duration strategy
python3 wrappers/run_longest_duration.py

# Maximum objects strategy
python3 wrappers/run_max_objects.py
```

### iOS Pythonista:
```python
# Option 1: Direct execution
exec(open('wrappers/run_mosaic_analysis.py').read())

# Option 2: Import and run
import sys
sys.path.insert(0, 'wrappers')
import run_mosaic_analysis
run_mosaic_analysis.main()

# Option 3: Load and execute
with open('wrappers/run_longest_duration.py') as f:
    exec(f.read())
```

## 🔄 Migration from Legacy Scripts

### `run_mosaic_plots.py` → `astromultinightplanner.py` 🆕
The `run_mosaic_plots.py` wrapper has been **migrated to the root directory** as `astromultinightplanner.py`:
- ✅ **New location**: Root directory (no longer in wrappers/)
- ✅ **Enhanced functionality**: Dedicated mosaic multi-night planner
- ✅ **Simplified execution**: `python astromultinightplanner.py` or `./astromultinightplanner.py`
- ✅ **Multi-night mode**: Automatically enabled for comprehensive analysis
- ✅ **Same great features**: Mosaic plotting, group analysis, and reporting

### `plot_mosaic_trajectories.py` → `run_mosaic_analysis.py`
The old standalone `plot_mosaic_trajectories.py` script has been replaced by `run_mosaic_analysis.py`, which provides:
- ✅ Same mosaic analysis functionality
- ✅ Enhanced integration with scheduling
- ✅ Better plotting capabilities
- ✅ Pythonista compatibility
- ✅ More comprehensive reporting

### Scheduling Arguments Updated
All strategy names now use full descriptive names:
- ❌ `--schedule longest` 
- ✅ `--schedule longest_duration`

## 🛠️ Technical Details

All wrappers:
- Import astropy dynamically to avoid path issues
- Manipulate `sys.argv` to simulate command-line arguments
- Restore original arguments after execution
- Include proper error handling and user feedback
- Work identically on desktop and iOS platforms

## 📚 Integration with Main System

These wrappers complement the main astronightplanner system by providing:
- **Focused interfaces** for specific use cases
- **Simplified access** to complex functionality
- **Pythonista compatibility** without code changes
- **Consistent user experience** across platforms

For comprehensive functionality, use the main `astronightplanner.py` script directly or the wrapper scripts in the root directory (`run_tests.py`, `run_demo.py`). 