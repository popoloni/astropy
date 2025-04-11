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
            "fov_width": 2.4,
            "fov_height": 1.8,
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
   - `catalog_name`: Path to your CSV catalog file
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

To use these new features, update your config.json with the new options shown in the Configuration section above.
