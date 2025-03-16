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
            "default": true
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
            "bortle_index": 6
        }
    },
    "catalog": {
        "use_csv_catalog": true,
        "catalog_name": "catalog_fixed.csv"
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
            "fov_width": 2.4,
            "fov_height": 1.8,
            "single_exposure": 10,
            "min_snr": 20,
            "gain": 1600,
            "read_noise": 1.7,
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
        "line_width": 1.5,
        "marker_size": 6,
        "interference_color": "goldenrod"
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
   - `catalog_name`: Path to your CSV catalog file

3. **Visibility**: Set observation parameters:
   - Minimum visibility duration
   - Minimum object area
   - Time intervals for calculations

4. **Scheduling**: Configure observation scheduling:
   - Strategy selection (`longest_duration`, `max_objects`, `optimal_snr`)
   - Maximum overlap between observations
   - Whether to exclude objects with insufficient visibility time

5. **Imaging**: Telescope and camera specifications:
   - Field of view dimensions
   - Exposure settings
   - Sensor characteristics
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
3. Save the file
4. Run the program - it will automatically use the new settings

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
