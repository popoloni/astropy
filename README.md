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
- Support for custom CSV catalogs with name enhancement
- Imaging configuration for telescope specifications
- Enhanced plotting capabilities:
  - Object trajectories with moon interference highlighting
  - Time-based visibility charts with moon influence periods
  - Moon phase icons and status indicators

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
- `MIN_ALT` - Minimum altitude in degrees (default: 15°)
- `MAX_ALT` - Maximum altitude in degrees (default: 75°)
- `MIN_AZ` - Minimum azimuth in degrees (default: 65°)
- `MAX_AZ` - Maximum azimuth in degrees (default: 165°)

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

### Moon Configuration
- `MOON_PROXIMITY_RADIUS` - Base radius in degrees to check for moon interference (default: 30°)
- `MOON_TRAJECTORY_COLOR` - Color for moon's trajectory (default: 'yellow')
- `MOON_INTERFERENCE_COLOR` - Color for object trajectories near moon (default: 'lightblue')
- `MOON_MARKER_SIZE` - Size of moon's hour markers (default: 6)

### Scheduling Options
- `SCHEDULING_STRATEGY` - Available strategies:
  - `LONGEST_DURATION` - Prioritize longest visibility windows
  - `MAX_OBJECTS` - Maximize number of observable objects
  - `OPTIMAL_SNR` - Optimize for best imaging conditions
- `MAX_OVERLAP_MINUTES` - Maximum allowed overlap between observations (default: 15)

## Usage

1. Set your observation location and preferences in the configuration section. At minimum, you should update:
   - `LATITUDE` and `LONGITUDE` to match your observation site
   - `TIMEZONE` to your local timezone
   - `MIN_ALT` and `MAX_ALT` based on your local horizon constraints
   - `BORTLE_INDEX` to match your local sky conditions

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

## Project Files

### Core Files
- `astropy.py` - Main planning tool with all features including moon tracking
- `astropy_legacy.py` - Legacy version without moon tracking features

### Data Files
- `objects.csv` - Default catalog file with object information
- `catalog_fixed.csv` - Alternative catalog with corrected coordinates
- `objects.json` - JSON format of the object catalog
- `Sac72.csv` - SAC catalog data
- `catalog_fixed_names.txt` - Additional object names for enhancement
- `objects_names.txt` - Extended object names database

### Utility Scripts
- `convert_json.py` - Converts between different catalog formats (CSV/JSON)
- `export_api_key.py` - Helper script for managing API keys for external services

## Catalog Conversion and Name Enhancement

### Converting JSON to CSV
The tool includes a `convert_json.py` script that can convert the `objects.json` catalog to CSV format. To convert:

1. Ensure you have both `objects.json` and `convert_json.py` in your directory
2. Run:
```bash
python convert_json.py
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
