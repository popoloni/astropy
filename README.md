# AstroPy Observation Planner

A Python-based astronomical observation planning tool that helps astronomers and astrophotographers plan their observation sessions. The tool includes a comprehensive catalog of deep sky objects (DSOs) including Messier objects and other notable celestial objects, with features for visibility calculation and observation scheduling.

## Features

- Comprehensive celestial object catalog including:
  - Complete Messier catalog
  - Notable deep sky objects beyond Messier
  - Detailed object information (coordinates, size, magnitude)
- Visibility calculation based on:
  - Observer's location (latitude/longitude)
  - Time and date
  - Minimum/maximum altitude and azimuth constraints
- Observation scheduling with multiple strategies:
  - Longest duration visibility
  - Maximum number of objects
  - Optimal signal-to-noise ratio
- Support for custom CSV catalogs
- Imaging configuration for telescope specifications
- Plotting capabilities for visibility windows and trajectories

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

The main configuration parameters can be found at the top of `astropy.py`. Key settings include:

### Location Settings
- `LATITUDE` - Observer's latitude (default: 45.516667 for Milan)
- `LONGITUDE` - Observer's longitude (default: 9.216667 for Milan)
- `TIMEZONE` - Local timezone (default: 'Europe/Rome')

### Visibility Constraints
- `MIN_ALT` - Minimum altitude in degrees (default: 20°)
- `MAX_ALT` - Maximum altitude in degrees (default: 75°)
- `MIN_AZ` - Minimum azimuth in degrees (default: 75°)
- `MAX_AZ` - Maximum azimuth in degrees (default: 160°)

### Time & Visibility Parameters
- `MIN_VISIBILITY_HOURS` - Minimum visibility window (default: 2 hours)
- `MIN_TOTAL_AREA` - Minimum area in square arcminutes (default: 225)
- `TRAJECTORY_INTERVAL_MINUTES` - Interval for trajectory calculations (default: 15)

### Telescope Settings (Vespera Specifications)
- `SCOPE_FOV_WIDTH` - Field of view width in degrees (default: 2.4°)
- `SCOPE_FOV_HEIGHT` - Field of view height in degrees (default: 1.8°)
- `SINGLE_EXPOSURE` - Exposure time in seconds (default: 10s)
- `FOCAL_LENGTH` - Focal length in mm (default: 200)
- `APERTURE` - Aperture in mm (default: 50)

### Scheduling Options
- `SCHEDULING_STRATEGY` - Available strategies:
  - `LONGEST_DURATION` - Prioritize longest visibility windows
  - `MAX_OBJECTS` - Maximize number of observable objects
  - `OPTIMAL_SNR` - Optimize for best imaging conditions
- `MAX_OVERLAP_MINUTES` - Maximum allowed overlap between observations (default: 15)

## Usage

1. Set your observation location and preferences in the configuration section of `astropy.py`. At minimum, you should update:
   - `LATITUDE` and `LONGITUDE` to match your observation site
   - `TIMEZONE` to your local timezone
   - `MIN_ALT` and `MAX_ALT` based on your local horizon constraints

2. Choose your catalog source:
   - Use the built-in catalog by setting `USE_CSV_CATALOG = False`
   - Use a custom CSV catalog:
     - Set `USE_CSV_CATALOG = True`
     - Update `CATALOGNAME` to point to your catalog file
     - Ensure your CSV has the required columns: name, RA (hours), Dec (degrees), size, magnitude

3. Select your scheduling strategy by setting `SCHEDULING_STRATEGY` to one of:
   - `SchedulingStrategy.LONGEST_DURATION`
   - `SchedulingStrategy.MAX_OBJECTS`
   - `SchedulingStrategy.OPTIMAL_SNR`

4. Run the planner:
```bash
python astropy.py  # Basic version
python "astropy 2.py"  # Enhanced version with moon influence tracking
```

The program will output:
- A list of observable objects for your location
- Visibility windows for each object
- An optimized observation schedule based on your chosen strategy
- Plots showing object trajectories and visibility periods

## Project Files

### Core Files
- `astropy.py` - Main planning tool containing:
  - Built-in celestial object catalogs (Messier and additional DSOs)
  - Visibility calculation algorithms
  - Scheduling optimization logic
  - Plotting functions

### Data Files
- `objects.csv` - Default catalog file with object information
- `catalog_fixed.csv` - Alternative catalog with corrected coordinates
- `objects.json` - JSON format of the object catalog
- `Sac72.csv` - SAC catalog data

### Utility Scripts
- `convert_json.py` - Converts between different catalog formats (CSV/JSON)
- `export_api_key.py` - Helper script for managing API keys for external services

### Development Files
- `astropy 2.py` - Enhanced version with moon influence tracking and extended features:
  - Moon position calculation and interference detection
  - Extended trajectory visualization (±5° outside visibility area)
  - Time-accurate moon influence display
  - Enhanced visibility charts with moon interference periods
- `Untitled.py` - Testing and development scratch file

## Moon Influence Features (astropy 2.py)

The enhanced version includes sophisticated moon interference tracking and visualization:

### Moon Configuration
- `MOON_PROXIMITY_RADIUS` - Radius in degrees to check for moon interference (default: 30°)
- `MOON_TRAJECTORY_COLOR` - Color for moon's trajectory (default: 'yellow')
- `MOON_INTERFERENCE_COLOR` - Color for object trajectories near moon (default: 'lightblue')
- `MOON_MARKER_SIZE` - Size of moon's hour markers (default: 6)

### Visualization Features
- Trajectory Plot:
  - Object paths shown ±5° outside visibility area
  - Moon interference highlighted in real-time
  - Clear distinction between normal and moon-affected periods
  - Proper z-ordering of visual elements

- Visibility Chart:
  - Moon-affected periods shown in yellow tones:
    - Goldenrod (#DAA520) for selected objects
    - Khaki (#F0E68C) for non-selected objects
  - Time-accurate display of interference periods
  - Split visibility bars showing exact affected times

### Moon Influence Detection
- Minute-by-minute moon position calculation
- Real-time interference checking for each object
- Influence periods tracked with precise timing
- Minimum 15-minute threshold for significant interference

### Reports and Analysis
- Moon influence summary in visibility reports
- Per-object moon interference status
- Detailed timing of affected periods
- Impact assessment on observation scheduling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
