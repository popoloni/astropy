# AstroPy for Pythonista (iPad)

This directory contains wrapper scripts designed specifically for running AstroPy Observation Planner in the Pythonista app on iPad. Since command-line arguments are difficult to use in Pythonista, these scripts provide simple one-tap access to the most common observation planning modes.

## ⭐ NEW FEATURE: Yellow Labels for Scheduled Objects

The trajectory plots now show **yellow transparent backgrounds** on labels for objects that are scheduled for observation! This makes it easy to spot which objects in the trajectory plots are recommended for tonight's session.

- **🟡 Yellow labels**: Objects scheduled for observation (same ones with red hatching in visibility chart)
- **⚪ White labels**: Objects visible but not scheduled

## 🆕 NEW FEATURE: Mosaic Group Trajectory Plots

**Specialized plotting for Vaonis Vespera Passenger mosaic photography!** The new mosaic trajectory plotter identifies objects that can be photographed together in the same 4.7° × 3.5° mosaic field of view and creates three dedicated chart types:

- **Combined mosaic group plot**: All groups color-coded on one chart with legend
- **Detail grid plot**: Individual group plots arranged in a grid without legends to maximize space  
- **Mosaic visibility chart**: Timeline showing when each group is observable with duration information
- **Field of view indicators**: Visual ellipses showing optimal mosaic positioning
- **Observation windows**: Exact timing for when groups are simultaneously visible

## Quick Start Scripts

Simply tap on any of these scripts in Pythonista to run them:

### 📱 **Text-Only Reports** (Fast, Mobile-Friendly)

#### `run_report_only.py`
- **What it does**: Generates a comprehensive text report without any plots
- **Best for**: Quick checks, mobile viewing, when you just need the information
- **Output**: Text-only observation report with all calculations

#### `run_quarters_report.py`  
- **What it does**: Text report optimized for 4-quarter night analysis
- **Best for**: Planning without plots, mobile-friendly analysis
- **Output**: Text report focused on quarterly time periods

#### `run_test_simulation.py`
- **What it does**: Simulates nighttime conditions (1:30 AM) during daytime
- **Best for**: Testing the app during the day, planning ahead
- **Output**: Text report as if it were the middle of the night

### 📊 **Full Reports with Plots**

#### `run_with_plots.py` 
- **What it does**: Complete report with trajectory plots and visibility charts
- **Best for**: Full analysis, visual planning, desktop-like experience
- **Output**: Text report + single trajectory plot + visibility charts
- **⭐ NEW**: Yellow labels for scheduled objects in trajectory plot

#### `run_quarters.py`
- **What it does**: 4-quarter trajectory plots for cleaner visualization  
- **Best for**: Nights with many visible objects, reduced visual clutter
- **Output**: Text report + 4 separate quarterly trajectory plots + visibility charts
- **⭐ NEW**: Yellow labels for scheduled objects in all quarter plots

#### `run_mosaic_plots.py` 🆕 **NEW**
- **What it does**: Creates specialized trajectory plots for Vespera Passenger mosaic groups
- **Best for**: Mosaic astrophotography planning, multi-target sessions
- **Output**: **Three specialized charts:**
  1. **Combined plot**: All groups with color-coding and legend
  2. **Detail grid**: Individual group subplots without legends  
  3. **Visibility chart**: Timeline view of observation windows
- **Features**: 
  - Objects color-coded by mosaic group
  - Field of view ellipses at optimal observation times
  - Detailed timing and separation information
  - Only shows objects that can be photographed together
  - Maximized space utilization in grid view

### 🎯 **Specialized Scheduling Strategies**

#### `run_max_objects.py`
- **What it does**: Optimizes for maximum number of different objects
- **Best for**: Survey nights, visual observation, star hopping
- **Strategy**: Fit as many objects as possible into the night
- **⭐ NEW**: Yellow labels highlight the selected objects in trajectory plots

#### `run_optimal_snr.py`
- **What it does**: Optimizes for best imaging conditions (brightness + altitude)
- **Best for**: Astrophotography when image quality is paramount  
- **Strategy**: Objects at optimal altitude and brightness
- **⭐ NEW**: Yellow labels highlight the selected objects in trajectory plots

#### `run_longest_duration.py`
- **What it does**: Prioritizes objects with longest visibility windows
- **Best for**: Deep sky imaging, extended exposures
- **Strategy**: Maximum time on individual targets
- **⭐ NEW**: Yellow labels highlight the selected objects in trajectory plots

### 🧪 **Testing Scripts**

#### `test_yellow_labels.py` ⭐ **NEW**
- **What it does**: Tests the new yellow label feature specifically
- **Best for**: Demonstrating the scheduled object highlighting
- **Output**: Full plots with clear examples of yellow vs white labels

## Setup Instructions

1. **Copy all files** from this directory to your Pythonista app
2. **Ensure you have** `astropy.py` and `config.json` in the same directory
3. **Tap any script** to run it directly in Pythonista

## ✅ iOS Compatibility

All wrapper scripts have been updated for full iOS/Pythonista compatibility:
- **No subprocess calls** - Scripts now directly import and call functions
- **Native iOS support** - Works perfectly in Pythonista 3
- **Error handling** - Comprehensive error reporting for debugging
- **Path management** - Automatic import path setup for all dependencies

The scripts are now fully optimized for iOS and will work without any compatibility issues.

## Configuration for iPad

Make sure your `config.json` is configured for your location:

```json
{
  "locations": {
    "your_location": {
      "name": "Your Location",
      "latitude": 45.516667,
      "longitude": 9.216667,
      "timezone": "Europe/Rome",
      "min_altitude": 15,
      "max_altitude": 75,
      "bortle_index": 6,
      "default": true
    }
  }
}
```

## Recommended Workflow for iPad

### For Quick Checks:
1. Run `run_report_only.py` for instant text results
2. Use `run_test_simulation.py` during daytime to test

### For Visual Planning:
1. Start with `run_quarters.py` for clean 4-quarter visualization with yellow scheduled labels
2. Use `run_with_plots.py` for complete single-plot overview with yellow scheduled labels

### For Mosaic Photography (Vespera Passenger): 🆕
1. First run `analyze_mosaic_groups.py` to see available mosaic groups
2. Then use `run_mosaic_plots.py` for specialized trajectory plots with FOV indicators
3. Use individual group plots for detailed planning of each mosaic session

### For Specific Goals:
- **Astrophotography**: Use `run_optimal_snr.py` or `run_longest_duration.py`
- **Mosaic astrophotography**: Use `run_mosaic_plots.py` 🆕
- **Visual observation**: Use `run_max_objects.py`
- **Survey work**: Use `run_max_objects.py`

### Testing the New Features:
- Use `test_yellow_labels.py` to see the yellow label feature in action
- Use `run_mosaic_plots.py` to see mosaic group plotting 🆕

## Understanding the Visual Cues

### In Standard Trajectory Plots:
- **🟡 Yellow label backgrounds**: Objects scheduled for observation tonight
- **⚪ White label backgrounds**: Objects visible but not in tonight's schedule
- **Solid lines**: Objects with sufficient observation time
- **Dashed lines**: Objects with insufficient observation time

### In Mosaic Trajectory Plots: 🆕
- **Color-coded trajectories**: Each mosaic group has a unique color
- **Different line styles**: Objects within the same group use varied line styles (solid, dashed, etc.)
- **Field of view ellipses**: Semi-transparent ellipses showing optimal mosaic positioning
- **Group information boxes**: Timing windows and object separations for each group
- **Three chart types**:
  - **Combined chart**: All groups with legend for overview
  - **Detail grid**: Individual plots without legends for detailed planning
  - **Visibility chart**: Timeline bars showing observation windows

### In Visibility Charts:
- **Red hatching**: Scheduled observation periods 
- **Green bars**: Recommended objects
- **Gray bars**: Other visible objects
- **Gold/Yellow segments**: Moon interference periods

The yellow labels in trajectory plots correspond exactly to the objects with red hatching in the visibility chart!

## Vespera Passenger Configuration 🆕

Your `config.json` now includes Vespera Passenger specifications:

```json
{
  "imaging": {
    "scope": {
      "name": "Vaonis Vespera Passenger",
      "fov_width": 2.4,
      "fov_height": 1.8,
      "mosaic_fov_width": 4.7,
      "mosaic_fov_height": 3.5,
      "native_resolution_mp": 6.2,
      "mosaic_resolution_mp": 24,
      "sensor": "Sony IMX585"
    }
  }
}
```

This enables:
- Accurate field of view calculations for both native and mosaic modes
- Proper mosaic group analysis based on your telescope's capabilities
- Realistic trajectory plotting with correct FOV indicators

## Troubleshooting

If you get import errors:
1. Make sure `astropy.py` is in the same folder
2. Check that all required libraries are installed in Pythonista:
   - numpy
   - matplotlib  
   - pytz

If plots don't display properly:
1. Try the text-only versions first (`run_report_only.py`)
2. Make sure matplotlib is working in your Pythonista installation

## Files Needed

Make sure you have these files in your Pythonista directory:
- `astropy.py` (main program)
- `config.json` (your configuration with Vespera Passenger specs) 🆕
- All the `run_*.py` scripts (these wrapper scripts)
- `test_yellow_labels.py` ⭐ **NEW** (test script for yellow labels)
- `analyze_mosaic_groups.py` 🆕 **NEW** (mosaic group analysis)
- `plot_mosaic_trajectories.py` 🆕 **NEW** (mosaic trajectory plotting)
- `run_mosaic_plots.py` 🆕 **NEW** (mosaic plotting wrapper)
- Any catalog files you're using (e.g., `catalog_fixed.csv`)

## Performance Tips

- Text-only scripts (`run_report_only.py`, `run_quarters_report.py`) run fastest
- Plot-generating scripts may take longer on iPad
- The 4-quarter plots (`run_quarters.py`) are often cleaner than single plots
- Mosaic plots (`run_mosaic_plots.py`) generate 3 charts and may take a few seconds to analyze groups 🆕
- Use simulation mode (`run_test_simulation.py`) for testing without waiting for nighttime
- Try `test_yellow_labels.py` to see the new yellow label feature in action

Enjoy your astronomical observations with better visual scheduling cues and comprehensive mosaic photography planning! 🌟 