# AstroPy Observation Planner

A Python-based astronomical observation planning tool that helps astronomers and astrophotographers plan their observation sessions. The tool includes a comprehensive catalog of deep sky objects (DSOs) including Messier objects and other notable celestial objects, with features for visibility calculation, moon phase tracking, and observation scheduling.

## Features

- Comprehensive celestial object catalog including:
  - Complete Messier catalog
  - Notable deep sky objects beyond Messier
  - Detailed object information (coordinates, size, magnitude)
- Visibility calculation based on:
  - Observer's location (latitude/longitude)
  - Time and date
  - Minimum/maximum altitude and azimuth constraints
- Advanced moon phase and interference tracking:
  - Real-time moon phase calculation and visualization
  - Moon interference detection and visualization
  - Moon rise/set times
  - Phase-specific interference radius calculation
- Observation scheduling with multiple strategies:
  - Longest duration visibility
  - Maximum number of objects
  - Optimal signal-to-noise ratio
  - Minimal mosaic (fewer panels)
  - Difficulty balanced (mix of easy and challenging targets)
- Support for custom CSV catalogs with name enhancement
- Imaging configuration for telescope specifications
- Enhanced plotting capabilities:
  - Object trajectories with moon interference highlighting
  - Time-based visibility charts with moon influence periods
  - Moon phase icons and status indicators
  - **Professional-quality trajectory plots with intelligent label positioning**
  - **4-quarter trajectory visualization for reduced visual clutter**
  - **Smart collision detection preventing label overlaps**
  - **Transparent label backgrounds preserving trajectory visibility**
  - **🆕 Mosaic photography planning with specialized trajectory plots**
  - **🆕 Mosaic group analysis for multi-target imaging sessions**
  - **🆕 Three-chart mosaic visualization system (combined, grid, timeline)**
- **🆕 Mosaic Photography Support (January 2025)**:
  - Specialized planning for Vaonis Vespera Passenger smart telescope
  - Identifies objects that can be photographed together in 4.7° × 3.5° mosaic FOV
  - Three dedicated chart types: combined trajectory plot, detail grid, and visibility timeline
  - Angular separation calculations and simultaneous visibility analysis
  - Field of view indicators showing optimal mosaic positioning
  - iPad-optimized with Pythonista wrapper scripts

## Recent Updates

### 🆕 Weekly Trajectory Analysis Improvements (January 2025)

Major enhancements and bug fixes have been implemented for the comprehensive weekly astrophotography analysis system:

**🔧 Critical Bug Fixes**
- **Year Support Updated**: Fixed hardcoded 2024 references to properly use current year (2025)
- **Week Ordering Corrected**: Best weeks are now properly sorted in chronological order (e.g., "2, 6, 10, 12" instead of "10, 6, 2, 3")
- **Complete Object Display**: Removed arbitrary limits that were hiding objects from analysis summaries
- **Moon Phase Calculations**: Updated moon phase reference date to January 13, 2025 for accurate calculations

**📊 Enhanced Analysis Features**
- **Full Year Coverage**: Analyzes all 52 weeks of the current year with proper date calculations
- **Comprehensive Reporting**: Shows all observable objects without artificial cutoffs
- **Improved Monthly Distribution**: Objects now properly distributed across all months (Jan-Dec) instead of limited range
- **Accurate Scoring**: Week scoring system now uses correct year for consistent analysis

**🔍 Analysis Capabilities**
The `utilities/trajectory_analysis.py` script provides:
- Weekly visibility analysis for all catalog objects (175+ objects)
- Moon interference detection and optimal observation windows
- Mosaic photography planning with FOV-based grouping
- Exposure time calculations based on Bortle scale and object magnitude
- Best observation periods for each object throughout the year

**📈 Output Improvements**
- **Complete Object Lists**: All objects meeting criteria are displayed (previously limited to 15-20)
- **Properly Sorted Weeks**: Best observation weeks shown in chronological order
- **Realistic Monthly Distribution**: Objects spread across all months with peak periods in December (35 objects), May/June/August (11 each)
- **Current Year Dates**: All analysis uses 2025 dates with proper week-to-date mapping

**🚀 Usage Examples**
```bash
# Full year analysis (default)
python utilities/trajectory_analysis.py

# Specific time periods
python utilities/trajectory_analysis.py --quarter Q4
python utilities/trajectory_analysis.py --month 5
python utilities/trajectory_analysis.py --half H2

# Skip plots for faster analysis
python utilities/trajectory_analysis.py --no-plots
```

**📊 Analysis Output Sections**
1. **Weekly Summary**: Best weeks for astrophotography with scores and moon conditions
2. **Object Optimization**: When each object is best photographed throughout the year
3. **Mosaic Analysis**: Objects requiring individual mosaics vs. group opportunities
4. **Monthly Statistics**: Distribution of optimal observation periods

**🔧 Technical Improvements**
- Dynamic year detection using `datetime.now().year`
- Proper parameter passing throughout analysis pipeline
- Fixed moon phase calculations with current year reference
- Consistent configuration window compliance checking
- Enhanced week-to-date mapping for accurate scheduling

The system now provides reliable, comprehensive planning for the entire 2025 observation season with accurate timing and complete object coverage.

### 🆕 Configuration-Based Mosaic Settings (May 2025)

**Centralized Configuration Management**
- **Removed Hardcoded Values**: All mosaic FOV dimensions and scope names are now read from `config.json`
- **Configurable Scope Settings**: Mosaic FOV width/height and scope name are fully configurable
- **Consistent Configuration**: All utilities and plotting scripts use the same configuration source
- **Easy Customization**: Change telescope specifications by editing the configuration file

**Updated Configuration Structure**
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
            "mosaic_resolution_mp": 24
        }
    }
}
```

**Directory Structure Reorganization**
The project has been reorganized for better maintainability:
```
astropy/
├── README.md                    # Main documentation
├── config.json                  # Configuration file
├── astropy.py                   # Main application
├── plot_mosaic_trajectories.py  # Mosaic plotting
├── astropy_legacy.py           # Legacy version
├── catalogs/                   # Object catalogs
│   ├── objects.csv
│   ├── objects.json
│   └── *.txt, *.numbers
├── utilities/                  # Utility scripts
│   ├── analyze_mosaic_groups.py
│   ├── convert_json.py
│   ├── trajectory_analysis.py
│   ├── time_sim.py
│   └── test_yellow_labels.py
├── wrappers/                   # Pythonista wrappers
│   ├── run_report_only.py
│   ├── run_mosaic_plots.py
│   └── run_*.py
└── docs/                       # Documentation
    └── *.md
```

### 🆕 Mosaic Photography Features (January 2025)

A comprehensive mosaic photography planning system has been added with full configuration support:

**New Analysis Capabilities**
- **Mosaic Group Detection**: Automatically identifies objects that can be photographed together within the 4.7° × 3.5° mosaic field of view
- **Angular Separation Calculations**: Uses spherical trigonometry to compute precise object separations
- **Simultaneous Visibility**: Finds time windows when multiple objects are observable together
- **Optimal Positioning**: Calculates best telescope positioning for each mosaic group

**Three-Chart Visualization System**
1. **Combined Trajectory Plot**: All mosaic groups color-coded on one chart with legend
2. **Detail Grid Plot**: Individual group subplots without legends for space optimization
3. **Mosaic Visibility Chart**: Timeline showing observation windows and durations

**New Files Added**
- `analyze_mosaic_groups.py` - Core mosaic group analysis engine
- `plot_mosaic_trajectories.py` - Three-chart plotting system
- `run_mosaic_plots.py` - Pythonista wrapper script
- Updated `config.json` with Vespera Passenger specifications

**iPad Integration**
- Full integration with existing Pythonista wrapper script system
- Space-optimized grid layouts for tablet viewing
- Touch-friendly interface with comprehensive documentation

**Technical Features**
- Field of view ellipses showing optimal mosaic positioning
- Color-coded trajectories with consistent styling across all charts
- Duration and separation information for each group
- Automatic grid layout adjustment based on number of groups

**Example Usage**
```bash
# Analyze mosaic groups
python3 utilities/analyze_mosaic_groups.py

# Create all three chart types
python3 plot_mosaic_trajectories.py

# Pythonista (iPad) - just tap
wrappers/run_mosaic_plots.py
```

The system typically finds 6-8 mosaic groups per night, each containing 2-4 objects that can be photographed together, providing 8-15 hours of total observation opportunities.

### Time Simulation Feature (May 2025)

A new time simulation feature has been added to help test the application without waiting for specific astronomical events:

- Added `--simulate-time` command-line argument to run the application as if it were a different time of day
- Created modular time handling with a separate `time_sim.py` module
- Implemented `get_current_datetime()` function that returns either the actual or simulated time
- Added proper timezone handling for consistent time calculations
- Fixed schedule generation to work correctly with simulated time

These changes allow testing nighttime observation scenarios during daytime by simulating running the application at any specified time.

**Usage:**
```bash
# Run the application simulating 1:30 AM
python astropy.py --simulate-time "01:30" --report-only

# Run the application simulating 10:30 PM
python astropy.py --simulate-time "22:30" --report-only
```

#### The time_sim.py Module

The time simulation functionality is implemented in a separate module with the following key components:

```python
# Global variable to store simulated time
SIMULATED_DATETIME = None

# Parse and convert a time string to a datetime object
def get_simulated_datetime(simulation_time_str, timezone=None):
    """
    Convert a time string (HH:MM or HH:MM:SS) to a datetime.
    Returns a datetime object set to the specified time on the current or next day.
    """
    # Implementation details...
    
# Return either simulated or actual current time
def get_current_datetime(timezone=None):
    """
    Get the current datetime, using the simulated time if set.
    This function serves as the central time provider for the application.
    """
    if SIMULATED_DATETIME is not None:
        return SIMULATED_DATETIME
    return datetime.now(timezone)
```

This modular approach ensures that all datetime operations throughout the application can be simulated consistently by simply modifying the global `SIMULATED_DATETIME` variable.

### Trajectory Plotting Enhancements (December 2024)

Major improvements have been made to the trajectory plotting system to provide cleaner, more readable visualizations with better label positioning and reduced visual clutter.

#### Key Improvements

**1. Enhanced Label Positioning System**
- **Smart Collision Detection**: Implemented comprehensive algorithm that avoids overlaps between object labels and hourly time markers
- **Fallback Positioning**: Added multiple fallback strategies to ensure every trajectory gets a label, even in crowded plots
- **Trajectory-Aware Placement**: Labels are positioned on straighter segments of trajectories for better readability
- **Configurable Margins**: Adjustable minimum distances between different label types

**2. Improved Label Transparency**
- **Reduced Background Opacity**: Changed label background alpha from 0.8-0.9 to 0.4 for better transparency
- **Trajectory Visibility**: Labels no longer hide the trajectory lines underneath
- **Consistent Styling**: Uniform transparency across all plotting modes

**3. 4-Quarter Trajectory Plots**
- **Clean Visualization**: Splits the night into 4 quarters to reduce trajectory overlapping
- **Simplified Legends**: Replaced messy individual subplot legends with a clean text summary
- **Time Indicators**: Each quarter clearly shows its time range and object count
- **Scheduled Object Highlighting**: Visual indicators for recommended observations

**4. Enhanced Object Labeling**
- **Intelligent Abbreviation**: Smart extraction of catalog designations (M31, NGC 6888, etc.)
- **Multi-Catalog Support**: Handles Messier, NGC, IC, Sharpless, and other catalog formats
- **Directional Offsets**: Labels positioned based on trajectory direction to avoid line overlap

#### Available Plotting Modes

**Standard Single Plot (Default)**
```bash
python astropy.py
```
- Complete night overview with all visible objects
- Intelligent label positioning to minimize overlaps
- Color-coded trajectories with comprehensive legend
- Moon trajectory and interference highlighting

**4-Quarter Trajectory Plots**
```bash
python astropy.py --quarters
```
- Night split into 4 time periods for reduced clutter
- Each quarter shows objects visible during that period
- Cleaner visualization with fewer overlapping trajectories
- Simple text summary instead of complex legends

#### Technical Features

**Label Positioning Algorithm**
- **Primary Strategy**: Find optimal positions avoiding all conflicts with 8-degree margins around hour markers
- **Fallback Strategy**: Use reduced margins (4 degrees) if no optimal position found
- **Final Fallback**: Use trajectory midpoint to ensure every object gets labeled

**Visual Improvements**
- **Smart Trajectory Selection**: Prefers straighter segments for label placement
- **Z-Order Management**: Proper layering with labels above trajectories
- **Offset Calculation**: Direction-aware label offsets based on trajectory slope

**Performance Optimizations**
- **Efficient Collision Detection**: Fast distance calculations for overlap prevention
- **Reduced Computation**: Optimized trajectory sampling for better performance
- **Memory Management**: Proper cleanup of plot resources

#### Usage Examples

```bash
# Standard trajectory plot with enhanced labels
python astropy.py

# 4-quarter view for reduced clutter
python astropy.py --quarters

# Text report only (skip all plots)
python astropy.py --report-only

# Use extended visibility margins
python astropy.py --quarters

# Strict visibility boundaries
python astropy.py --quarters --no-margins
```

#### Configuration Options

The trajectory plotting improvements work with existing configuration options:

| Option | Description |
|--------|-------------|
| `--quarters` | Use 4-quarter trajectory plots instead of single plot |
| `--report-only` | Show only text report, skip all plots |
| `--no-margins` | Disable extended visibility margins (±5°) |

#### Results

**Before Improvements**:
- ❌ Missing labels on many trajectories
- ❌ Labels overlapping with hour markers and each other
- ❌ Opaque label backgrounds hiding trajectory lines
- ❌ Messy legends in 4-quarter plots
- ❌ Poor visual clarity in crowded plots

**After Improvements**:
- ✅ Every trajectory has a clear, readable label
- ✅ Smart positioning avoids all types of overlaps
- ✅ Transparent labels (α=0.4) show trajectories underneath
- ✅ Clean 4-quarter plots with simple text summaries
- ✅ Professional-quality astronomical charts

The enhanced trajectory plotting system provides professional-quality visualizations that maintain readability even with many objects visible simultaneously. The 4-quarter approach is particularly useful for crowded nights when many objects are visible, while the improved single-plot mode offers the best overall view of the entire observing session.

### Schedule Generation Improvements

Fixed an issue where the schedule generation would produce empty schedules:

- Added proper return statement to the `generate_observation_schedule` function
- Improved handling of moon-affected objects in scheduling
- Implemented fallback logic to include moon-affected objects when no other options are available
- Enhanced error handling for exposure time calculations
- Added more robust handling for empty schedules in the report generator

## Installation

1. Clone this repository:
```bash
git clone https://github.com/popoloni/astropy.git
cd astropy
```

2. Install the required dependencies:
```bash
pip install numpy matplotlib pytz
```

The project uses the following Python libraries:
- `numpy` - For numerical computations
- `matplotlib` - For plotting visibility windows and trajectories
- `pytz` - For timezone handling
- Standard library modules: `datetime`, `enum`, `csv`, `json`, `math`, `re`

## Configuration

The tool now uses a `config.json` file for all configuration settings. This makes it easier to manage multiple observation locations and adjust settings without modifying the code.

### Configuration File Structure

The `config.json` file is organized into the following sections:

```json
{
    "locations": {
        "Milano": {
            "name": "Milano",
            "latitude": 45.516667,
            "longitude": 9.216667,
            "timezone": "Europe/Rome",
            "min_altitude": 15,
            "max_altitude": 75,
            "min_azimuth": 65,
            "max_azimuth": 165,
            "bortle_index": 9,
            "default": true,
            "comment": "Milan coordinates"
        },
        "Lozio": {
            "name": "Lozio",
            "latitude": 45.516667,
            "longitude": 9.216667,
            "timezone": "Europe/Rome",
            "min_altitude": 15,
            "max_altitude": 75,
            "min_azimuth": 65,
            "max_azimuth": 165,
            "bortle_index": 6,
            "comment": "Lozio coordinates"
        }
    },
    "catalog": {
        "use_csv_catalog": true,
        "catalog_name": "catalog_fixed.csv",
        "merge": true
    },
    "visibility": {
        "min_visibility_hours": 2,
        "min_total_area": 225,
        "trajectory_interval_minutes": 15,
        "search_interval_minutes": 1
    },
    "scheduling": {
        "strategy": "longest_duration",
        "max_overlap_minutes": 15,
        "exclude_insufficient_time": true
    },
    "imaging": {
        "scope": {
            "name": "Vaonis Vespera Passenger",
            "fov_width": 2.4,
            "fov_height": 1.8,
            "mosaic_fov_width": 4.7,
            "mosaic_fov_height": 3.5,
            "native_resolution_mp": 6.2,
            "mosaic_resolution_mp": 24,
            "sensor": "Sony IMX585",
            "single_exposure": 10,
            "min_snr": 20,
            "gain": 800,
            "read_noise": 0.8,
            "pixel_size": 2.9,
            "focal_length": 200,
            "aperture": 50
        }
    },
    "plotting": {
        "max_objects_optimal": 5,
        "figure_size": [12, 10],
        "color_map": "tab20",
        "grid_alpha": 0.3,
        "visible_region_alpha": 0.1
    },
    "moon": {
        "proximity_radius": 30,
        "trajectory_color": "yellow",
        "marker_color": "yellow",
        "line_width": 2,
        "marker_size": 6,
        "interference_color": "lightblue"
    }
}
```

### Key Configuration Sections

1. **Locations**: Define multiple observation sites with their specific parameters:
   - Geographic coordinates (latitude/longitude)
   - Timezone
   - Visibility constraints (altitude/azimuth limits)
   - Bortle index for light pollution
   - Set `"default": true` for your primary location

2. **Catalog**: Configure catalog sources:
   - `use_csv_catalog`: Whether to use a custom CSV catalog
   - `catalog_name`: Path to your CSV catalog file (now in `catalogs/` directory)
   - `merge`: Whether to combine CSV catalog with built-in objects

3. **Visibility**: Set observation parameters:
   - Minimum visibility duration
   - Minimum object area
   - Time intervals for calculations

4. **Scheduling**: Configure observation scheduling:
   - Strategy selection (`longest_duration`, `max_objects`, `optimal_snr`, `minimal_mosaic`, `difficulty_balanced`)
   - Maximum overlap between observations
   - Whether to exclude objects with insufficient visibility time

5. **Imaging**: Telescope and camera specifications:
   - Scope name and identification
   - Single-shot field of view dimensions
   - Mosaic field of view dimensions
   - Resolution specifications (native and mosaic)
   - Sensor information
   - Exposure settings
   - Optical specifications

6. **Plotting**: Visualization settings:
   - Maximum number of objects to show
   - Figure dimensions
   - Color schemes
   - Transparency settings

7. **Moon**: Moon-related visualization settings:
   - Interference radius
   - Colors for trajectory and markers
   - Line and marker styles

### Using the Configuration

1. Create a `config.json` file in your project directory using the structure above.

2. Customize the settings for your needs:
   - Add your observation locations
   - Set your preferred location as default
   - Adjust visibility constraints
   - Configure your telescope specifications

3. The program will automatically load these settings when run:
```bash
python astropy.py
```

4. To switch between locations, either:
   - Modify the `"default": true` flag in the config file
   - Use the location-specific functions in the code

### Modifying the Configuration

To modify settings:
1. Open `config.json` in any text editor
2. Make your changes while maintaining the JSON structure

## Command-Line Arguments

The application supports various command-line arguments to customize its behavior:

```
usage: astropy.py [-h] [--date DATE] [--object OBJECT] [--type TYPE] [--report-only]
                 [--schedule {longest,max_objects,optimal_snr}] [--no-margins]
                 [--simulate-time SIMULATE_TIME] [--quarters]
```

### Available Arguments

| Argument | Description |
|----------|-------------|
| `--date DATE` | Specify a date for calculations (format: YYYY-MM-DD) |
| `--object OBJECT` | Display information for a specific celestial object |
| `--type TYPE` | Filter objects by type (galaxy, nebula, cluster, etc.) |
| `--report-only` | Show only text report without generating plots |
| `--schedule {longest,max_objects,optimal_snr}` | Specify the scheduling strategy |
| `--no-margins` | Do not use extended margins for visibility calculations |
| `--simulate-time SIMULATE_TIME` | Simulate running at a specific time (format: HH:MM) |
| `--quarters` | Use 4-quarter trajectory plots instead of single plot |

### Examples

```bash
# Show only text report for default settings
python astropy.py --report-only

# Generate report for a specific object
python astropy.py --object "M31"

# Generate report for a specific date
python astropy.py --date "2025-06-01"

# Filter objects by type
python astropy.py --type "nebula"

# Use a specific scheduling strategy
python astropy.py --schedule max_objects

# Simulate running at 1:30 AM
python astropy.py --simulate-time "01:30" --report-only

# Use 4-quarter trajectory plots for cleaner visualization
python astropy.py --quarters

# Combine options for specific analysis
python astropy.py --quarters --no-margins --date "2025-06-01"
```

## Usage

1. Create or edit your `config.json` file with your observation location and preferences:
   - Add your location under the `"locations"` section
   - Set your preferred location as `"default": true` 
   - Adjust `"min_altitude"` and `"max_altitude"` based on your local horizon constraints
   - Set `"bortle_index"` to match your local sky conditions (1-9 scale)

2. Configure your catalog source:
   - Use the built-in catalog by setting `"use_csv_catalog": false`
   - Use a custom CSV catalog:
     - Set `"use_csv_catalog": true`
     - Update `"catalog_name"` to point to your catalog file
     - Set `"merge": true` if you want to combine with built-in objects
     - Ensure your CSV has the required columns: name, RA (hours), Dec (degrees), size, magnitude

3. Select your scheduling strategy by setting the `"strategy"` field in your config.json to one of:
   - `"longest_duration"` - For extended imaging sessions on fewer objects
   - `"max_objects"` - To see the maximum number of objects in one night
   - `"optimal_snr"` - For the best imaging conditions
   - `"minimal_mosaic"` - For objects requiring fewer imaging panels
   - `"difficulty_balanced"` - For a mix of easy and challenging targets

4. Run the planner:
```bash
python astropy.py
```

The program will output:
- A list of observable objects for your location
- Moon phase and interference information
- Visibility windows for each object
- An optimized observation schedule based on your chosen strategy
- Enhanced plots showing:
  - Object trajectories with moon interference
  - Visibility periods with moon influence indicators
  - Moon phase and position information

## Scheduling Strategies

The observation planner offers five different scheduling strategies, each optimized for different observing goals:

### 1. Longest Duration (LONGEST_DURATION)
- **What it optimizes**: Prioritizes objects with the longest visibility windows.
- **Algorithm**: Scores objects directly by their total visibility duration in hours.
- **Best for**: Long exposure deep sky imaging when you want to maximize time on a single target.
- **Advantages**: Ensures you have plenty of time for long imaging sessions without interruption.
- **Disadvantages**: May favor easy targets over more interesting but shorter-duration objects.

### 2. Maximum Objects (MAX_OBJECTS)
- **What it optimizes**: Fits as many different objects as possible into your observing night.
- **Algorithm**: Uses a sophisticated multi-slot scheduling approach with gap minimization and post-processing.
  - Generates multiple potential start/end times throughout each object's visibility period
  - Selects non-overlapping slots using a greedy algorithm
  - Post-processes to minimize idle time between observations
- **Best for**: Survey nights, star hopping, or visual observation of multiple targets.
- **Advantages**: See the maximum number of different objects in a single night.
- **Disadvantages**: May not allocate enough time for challenging targets that require longer exposures.

### 3. Optimal Signal-to-Noise Ratio (OPTIMAL_SNR)
- **What it optimizes**: Balances object brightness and altitude for optimal imaging conditions.
- **Algorithm**: Scores objects based on a combination of:
  - Altitude score (higher altitude = better seeing)
  - Magnitude score (brighter objects score higher)
- **Best for**: Getting the best possible image quality when imaging multiple objects.
- **Advantages**: Prioritizes objects when they're at their best position for imaging.
- **Disadvantages**: May not optimize for total number of objects or specific targets of interest.

### 4. Minimal Mosaic (MINIMAL_MOSAIC)
- **What it optimizes**: Favors objects that require fewer panels for complete imaging.
- **Algorithm**: Scores objects inversely to the number of panels required to capture them.
- **Best for**: Astrophotographers with limited time who want to complete full targets.
- **Advantages**: Avoids starting complex mosaic projects that you won't have time to complete.
- **Disadvantages**: May bias toward smaller objects that might not be as visually impressive.

### 5. Difficulty Balanced (DIFFICULTY_BALANCED)
- **What it optimizes**: Creates a mix of easy and challenging targets.
- **Algorithm**: Balances:
  - Difficulty (based on magnitude and number of panels required)
  - Feasibility (based on available time vs. required exposure time)
- **Best for**: Mixed observing sessions when you want variety in your targets.
- **Advantages**: Provides a balanced observing plan with both quick wins and challenging objects.
- **Disadvantages**: May not be optimal for either maximum count or highest quality imaging.

To select a strategy, set the `"strategy"` field in your config.json file to one of: `"longest_duration"`, `"max_objects"`, `"optimal_snr"`, `"minimal_mosaic"`, or `"difficulty_balanced"`.

## Project Files

### Core Files (Root Directory)
- `astropy.py` - Main planning tool with all features including moon tracking
- `astropy_legacy.py` - Legacy version without moon tracking features
- `plot_mosaic_trajectories.py` - Mosaic trajectory plotting with three-chart system
- `config.json` - Configuration file with all settings

### Catalogs Directory (`catalogs/`)
- `objects.csv` - Default catalog file with object information
- `objects.json` - JSON format of the object catalog
- `Sac72.csv` - SAC catalog data
- `catalog_fixed_names.txt` - Additional object names for enhancement
- `objects_names.txt` - Extended object names database
- `*.numbers` - Additional catalog files

### Utilities Directory (`utilities/`)
- `analyze_mosaic_groups.py` - Core mosaic group analysis engine
- `convert_json.py` - Converts between different catalog formats (CSV/JSON)
- `trajectory_analysis.py` - Advanced trajectory analysis tools
- `time_sim.py` - Time simulation module for testing
- `test_yellow_labels.py` - Label positioning testing utility
- `export_api_key.py` - Helper script for managing API keys

### Wrappers Directory (`wrappers/`)
- `run_report_only.py` - Pythonista wrapper for text-only reports
- `run_mosaic_plots.py` - Pythonista wrapper for mosaic plotting
- `run_with_plots.py` - Pythonista wrapper for full plotting
- `run_max_objects.py` - Pythonista wrapper for maximum objects strategy
- Additional wrapper scripts for various use cases

### Documentation Directory (`docs/`)
- Additional documentation files (*.md)

## Built-in Deep Sky Object Catalog

The AstroPy Observation Planner includes a comprehensive built-in catalog of deep sky objects. These objects are available without needing to load any external CSV files.

### Messier Objects

| Designation | Common Name | Type | Size | Magnitude |
|-------------|-------------|------|------|-----------|
| M1 | Crab Nebula | Nebula | 6'x4' | 8.4 |
| M8 | Lagoon Nebula | Nebula | 90'x40' | 6.0 |
| M16 | Eagle Nebula | Nebula | 35'x28' | 6.4 |
| M17 | Omega/Swan Nebula | Nebula | 46'x37' | 6.0 |
| M20 | Trifid Nebula | Nebula | 28'x28' | 6.3 |
| M27 | Dumbbell Nebula | Nebula | 8.0'x5.7' | 7.5 |
| M31 | Andromeda Galaxy | Galaxy | 178'x63' | 3.4 |
| M32 | Andromeda Companion | Galaxy | 8'x6' | 8.1 |
| M33 | Triangulum Galaxy | Galaxy | 73'x45' | 5.7 |
| M42 | Great Orion Nebula | Nebula | 85'x60' | 4.0 |
| M43 | De Mairan's Nebula | Nebula | 20'x15' | 9.0 |
| M45 | Pleiades (Seven Sisters) | Open Cluster | 110'x110' | 1.6 |
| M51 | Whirlpool Galaxy | Galaxy | 11'x7' | 8.4 |
| M57 | Ring Nebula | Nebula | 1.4'x1' | 8.8 |
| M63 | Sunflower Galaxy | Galaxy | 12.6'x7.2' | 8.6 |
| M64 | Black Eye Galaxy | Galaxy | 10'x5' | 8.5 |
| M76 | Little Dumbbell Nebula | Nebula | 2.7'x1.8' | 10.1 |
| M81 | Bode's Galaxy | Galaxy | 26.9'x14.1' | 6.9 |
| M82 | Cigar Galaxy | Galaxy | 11.2'x4.3' | 8.4 |
| M97 | Owl Nebula | Nebula | 3.4'x3.3' | 9.9 |
| M101 | Pinwheel Galaxy | Galaxy | 28.8'x26.9' | 7.9 |
| M104 | Sombrero Galaxy | Galaxy | 8.7'x3.5' | 8.0 |

### Notable Non-Messier Objects

| Designation | Common Name | Type | Size | Magnitude |
|-------------|-------------|------|------|-----------|
| NGC 7000/C20 | North America Nebula | Nebula | 120'x100' | 4.0 |
| NGC 6960/C34 | Western Veil/Witch's Broom | Nebula | 70'x6' | 7.0 |
| NGC 6992/C33 | Eastern Veil/Network Nebula | Nebula | 75'x12' | 7.0 |
| NGC 1499/C31 | California Nebula | Nebula | 145'x40' | 5.0 |
| IC 5070/C19 | Pelican Nebula | Nebula | 60'x50' | 8.0 |
| NGC 2237/C49 | Rosette Nebula | Nebula | 80'x80' | 6.0 |
| IC 1396 | Elephant's Trunk Nebula | Nebula | 170'x140' | 7.5 |
| IC 1805/C31 | Heart Nebula | Nebula | 100'x100' | 6.5 |
| NGC 2264/C41 | Cone Nebula/Christmas Tree | Nebula | 20'x10' | 7.2 |
| IC 434/B33 | Horsehead Nebula | Nebula | 60'x10' | 6.8 |
| NGC 7293/C63 | Helix Nebula | Nebula | 28'x23' | 7.6 |
| NGC 6888/C27 | Crescent Nebula | Nebula | 25'x18' | 7.4 |
| NGC 3372/C92 | Eta Carinae Nebula | Nebula | 120'x120' | 3.0 |
| NGC 5139 | Omega Centauri | Globular Cluster | 36.3'x36.3' | 3.7 |
| NGC 104 | 47 Tucanae | Globular Cluster | 30.9'x30.9' | 4.0 |
| IC 2602/C102 | Southern Pleiades | Open Cluster | 100'x100' | 1.9 |
| Melotte25 | Hyades Cluster | Open Cluster | 330'x330' | 0.5 |
| Collinder399 | Coathanger/Brocchi's Cluster | Open Cluster | 60'x60' | 3.6 |

### Additional Catalog Features

The built-in catalog includes:
- Complete Messier catalog (M1-M110)
- Notable NGC and IC objects
- Sharpless catalog (SH2) objects
- Collinder, Melotte, and Stock catalog objects
- Double clusters and multiple designation objects

The catalog can be extended by using custom CSV files, and the built-in object names can be enhanced with common names via the name enhancement algorithm.

## Catalog Conversion and Name Enhancement

### CSV Format Requirements
If you choose to use a custom CSV catalog, ensure it has these columns:
- **name**: Object designation (e.g., "M31", "NGC 7000")
- **ra_hours**: Right Ascension in decimal hours (0-24)
- **dec_deg**: Declination in decimal degrees (-90 to +90)
- **size**: Angular size in arcminutes (e.g., "10'x5'")
- **magnitude**: Visual magnitude (lower is brighter)

Example CSV format:
```csv
name,ra_hours,dec_deg,size,magnitude
M31,0.712,41.269,"178'x63'",3.4
NGC 7000,20.968,44.533,"120'x100'",4.0
```

### Converting JSON to CSV
The tool includes a `utilities/convert_json.py` script that can convert the `catalogs/objects.json` catalog to CSV format. To convert:

1. Ensure you have the catalog files in the `catalogs/` directory
2. Run:
```bash
python utilities/convert_json.py
```

The script will:
- Parse the JSON catalog
- Extract relevant fields (name, RA, Dec, size, magnitude)
- Format coordinates properly
- Generate a CSV file with the required columns

### Object Name Enhancement
The tool automatically enhances object names by:

1. Cross-referencing multiple catalogs:
   - Messier catalog (M)
   - New General Catalog (NGC)
   - Index Catalog (IC)
   - Sharpless catalog (SH2)
   - Barnard catalog (B)

2. Adding common names when available:
   - Extracts common names from the full designation
   - Handles multiple catalog designations (e.g., "M31/NGC 224")
   - Preserves original catalog numbers
   - Adds parenthetical common names (e.g., "M31 (Andromeda Galaxy)")

3. Processing special cases:
   - Double clusters
   - Multiple designations
   - Catalog-specific formats (e.g., "SH2-" prefix)

Example enhancements:
- "M31" → "M31/NGC 224 (Andromeda Galaxy)"
- "NGC 7000" → "NGC 7000/C20 (North America Nebula)"
- "IC 434" → "IC 434/B33 (Horsehead Nebula)"

## Command Line Options

The tool supports several command line options:
```bash
python astropy.py [options]
```

Available options:
- `--date YYYY-MM-DD`: Specify a date for calculations (default: today)
- `--location NAME`: Use a specific location from your config file
- `--strategy NAME`: Override the scheduling strategy
- `--csv FILENAME`: Use a specific CSV catalog file
- `--no-plot`: Run without generating plots
- `--help`: Show all available options

## Configuration Examples

### Dark Site Configuration
```json
{
  "locations": {
    "dark_site": {
      "name": "Dark Sky Location",
      "latitude": 38.123,
      "longitude": -105.456,
      "timezone": "America/Denver",
      "min_altitude": 20,
      "max_altitude": 85,
      "min_azimuth": 0,
      "max_azimuth": 360,
      "bortle_index": 3,
      "default": true
    }
  },
  "scheduling": {
    "strategy": "optimal_snr",
    "exclude_insufficient_time": true
  }
}
```

### Visual Observation Setup
```json
{
  "scheduling": {
    "strategy": "max_objects",
    "exclude_insufficient_time": false
  },
  "visibility": {
    "min_visibility_hours": 0.5
  }
}
```

## Troubleshooting

- **File Not Found Errors**: Ensure your config.json file exists in the same directory as astropy.py
- **JSON Parsing Errors**: Check your config.json for valid JSON syntax
- **Empty Results**: Verify your location settings and visibility constraints aren't too restrictive
- **Plotting Errors**: Make sure matplotlib is properly installed
- **Timezone Errors**: Confirm your timezone is a valid IANA timezone string (e.g., "America/New_York")

## 📚 Documentation

For comprehensive documentation, visit the **[docs/](docs/)** directory:

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running in minutes ⚡
- **[Documentation Index](docs/README.md)** - Complete guide to all documentation
- **[Pythonista (iPad) Guide](docs/user-guides/README_PYTHONISTA.md)** - Running AstroPy on iPad
- **[Mosaic Photography Guide](docs/user-guides/MOSAIC_FEATURES_SUMMARY.md)** - Specialized astrophotography features
- **[Wrapper Scripts Guide](docs/user-guides/WRAPPERS_GUIDE.md)** - Convenient script access
- **[Development Documentation](docs/development/)** - Technical implementation details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Changelog

### Recent Updates

#### Scheduling Algorithm Enhancements
- **Improved MAX_OBJECTS Strategy**: The scheduler now uses a more sophisticated algorithm that generates multiple potential observation slots and optimizes to fit more objects in the schedule.
- **Gap Minimization**: Added post-processing step to minimize idle time between observations, which shifts observations earlier when possible while avoiding conflicts.
- **Conflict Detection**: Enhanced conflict detection logic to ensure zero overlaps between scheduled observations.
- **Additional Scheduling Strategies**: Added two new scheduling strategies:
  - `MINIMAL_MOSAIC`: Optimizes for objects requiring fewer panels (reducing imaging complexity)
  - `DIFFICULTY_BALANCED`: Balances between observation difficulty and feasibility

#### Configuration File Updates
- **Catalog Merging Option**: Added `"merge": true` option to the catalog configuration to combine CSV catalogs with built-in objects.
- **Location Enhancements**: Added comments field to location entries for better documentation.
- **Configuration Override**: The legacy version now forces `USE_CSV_CATALOG = False` to ensure consistent behavior.

#### Moon Interference Visualization
- Changed default moon interference color to "lightblue" for better visibility on charts.
- Increased default line width for moon trajectory to 2 for improved clarity.
- Reduced imaging sensor gain to 800 and read noise to 0.8 for more realistic exposure calculations.

#### Code Maintenance
- Fixed various edge cases in the scheduling algorithm for more reliable operation.
- Added validation to prevent scheduling objects with invalid exposure time calculations.
- Enhanced file loading logic for more robust configuration handling.

#### Trajectory Plotting System Overhaul (December 2024)
- **Enhanced Label Positioning**: Implemented comprehensive label positioning algorithm with smart collision detection
- **Transparency Improvements**: Reduced label background opacity from 0.8-0.9 to 0.4 for better trajectory visibility
- **4-Quarter Plot Optimization**: Replaced complex legends with clean text summaries in quarterly trajectory plots
- **Fallback Systems**: Added multiple fallback strategies to ensure every trajectory gets a label
- **Visual Polish**: Improved z-ordering, directional offsets, and trajectory-aware label placement
- **Code Cleanup**: Removed the problematic enhanced plotting mode and streamlined to two clean plotting options

To use these new features, update your config.json with the new options shown in the Configuration section above.
