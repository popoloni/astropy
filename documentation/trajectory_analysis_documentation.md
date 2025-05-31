# Trajectory Analysis and Weekly Astrophotography Planning Documentation

## Overview

The `trajectory_analysis.py` script is a comprehensive tool for analyzing and planning astrophotography sessions throughout the year. It evaluates astronomical objects based on visibility conditions, moon interference, telescope field of view constraints, and optimal timing to provide data-driven recommendations for weekly astrophotography planning.

## Key Features

### 1. **Temporal Analysis**
- Analyzes astrophotography opportunities across configurable time periods
- Supports year, half-year, quarter, and monthly analysis periods
- Provides week-by-week scoring and recommendations

### 2. **Moon Condition Analysis**
- Calculates moon phases and illumination percentages
- Determines moon interference based on angular separation and illumination
- Identifies moon-free observation windows for optimal dark-sky imaging

### 3. **Mosaic Planning**
- Automatically detects objects requiring mosaic imaging
- Groups nearby objects into efficient mosaic opportunities
- Considers telescope field of view constraints for practical imaging

### 4. **Visibility Window Compliance**
- Respects user-configured altitude and azimuth constraints
- Enforces minimum visibility duration requirements
- Accounts for exposure time requirements based on object magnitude and sky conditions

### 5. **Comprehensive Scoring System**
- Generates weekly astrophotography scores based on multiple factors
- Prioritizes moon-free objects and mosaic opportunities
- Considers object brightness, sky conditions, and practical constraints

## Dependencies

```python
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict, Counter
import math
from typing import List, Dict, Tuple, Optional
import argparse
```

### Required External Modules
- `astropy` (main astronomy calculation module)
- Configuration file: `config.json` for telescope and location settings

## Core Functions

### Time Period Management

#### `get_weeks_for_period(period_type, period_value, year=None)`
Converts time period specifications into week numbers for analysis.

**Parameters:**
- `period_type` (str): Type of period ('year', 'half', 'quarter', 'month')
- `period_value` (str/int): Specific period identifier (e.g., 'Q1', 'H2', month number)
- `year` (int, optional): Target year (defaults to current year)

**Returns:**
- List of week numbers to analyze

#### `get_weekly_dates(weeks_to_analyze, year=None)`
Converts week numbers to specific dates for analysis.

**Parameters:**
- `weeks_to_analyze` (list): List of week numbers
- `year` (int, optional): Target year

**Returns:**
- Dictionary mapping week numbers to datetime objects

### Moon Analysis Functions

#### `get_moon_phase(date)`
Calculates moon phase for a given date.

**Parameters:**
- `date` (datetime): Date for moon phase calculation

**Returns:**
- Float between 0 (new moon) and 1 (full moon)

#### `get_moon_illumination(phase)`
Converts moon phase to illumination percentage.

**Parameters:**
- `phase` (float): Moon phase value (0-1)

**Returns:**
- Float between 0 (no illumination) and 1 (full illumination)

#### `is_moon_interference(obj_ra, obj_dec, moon_ra, moon_dec, moon_illumination, separation_threshold=60)`
Determines if moon interferes with object observation.

**Parameters:**
- `obj_ra` (float): Object right ascension (degrees)
- `obj_dec` (float): Object declination (degrees)
- `moon_ra` (float): Moon right ascension (degrees)
- `moon_dec` (float): Moon declination (degrees)
- `moon_illumination` (float): Moon illumination fraction (0-1)
- `separation_threshold` (float): Base separation threshold (degrees)

**Returns:**
- Tuple: (is_interfered: bool, separation: float)

### Mosaic Detection and Planning

#### `detect_mosaic_clusters(objects, config_fov=None, bortle_index=6)`
Groups objects into efficient mosaic clusters based on telescope field of view.

**Parameters:**
- `objects` (list): List of astronomical objects
- `config_fov` (dict, optional): Field of view configuration
- `bortle_index` (int): Sky darkness level (1-9 scale)

**Returns:**
- List of object clusters for mosaic imaging

**Algorithm:**
1. Identifies objects requiring individual mosaics (large extended objects)
2. Groups remaining objects that fit within mosaic field of view
3. Optimizes cluster compactness and practical imaging constraints

#### `calculate_object_panels_required(obj_fov_str, telescope_fov_width=2.4, telescope_fov_height=1.8)`
Calculates mosaic panel requirements for an object.

**Parameters:**
- `obj_fov_str` (str): Object field of view specification
- `telescope_fov_width` (float): Telescope FOV width (degrees)
- `telescope_fov_height` (float): Telescope FOV height (degrees)

**Returns:**
- Dictionary with panel requirements and feasibility analysis

### Exposure Time Calculation

#### `calculate_required_exposure_time(magnitude, bortle_index, base_exposure_hours=1.0)`
Calculates required total exposure time based on object and sky conditions.

**Parameters:**
- `magnitude` (float): Object magnitude (brighter = lower number)
- `bortle_index` (int): Sky darkness level (1-9)
- `base_exposure_hours` (float): Base exposure for magnitude 10 in Bortle 4

**Returns:**
- Required exposure time in hours

**Formula:**
- Magnitude factor: 2.5^(magnitude - 10)
- Bortle factor: (bortle_index / 4.0)^1.5
- Final time = base × magnitude_factor × bortle_factor (clamped to 0.5-20 hours)

### Weekly Analysis Functions

#### `analyze_weekly_conditions(objects, week_date)`
Performs comprehensive analysis for a specific week.

**Parameters:**
- `objects` (list): List of astronomical objects to analyze
- `week_date` (datetime): Date representing the week

**Returns:**
- Dictionary containing detailed weekly analysis data

**Analysis includes:**
- Object visibility within configured windows
- Exposure time requirements
- Moon interference assessment
- Mosaic clustering optimization
- Scoring and recommendations

#### `score_week_for_astrophotography(week_data)`
Generates a numerical score for astrophotography potential.

**Parameters:**
- `week_data` (dict): Weekly analysis data

**Returns:**
- Numerical score (higher = better conditions)

**Scoring factors:**
- Observable objects: +2 points each
- Moon-free objects: +10 points each
- Mosaic groups: +15 points each
- Moon-free mosaics: +25 points each
- Moon illumination penalty: -50 × moon_fraction
- Night duration bonus: +5 × hours

### Yearly Object Analysis

#### `analyze_yearly_object_conditions(weeks_to_analyze, year=None)`
Analyzes optimal conditions for each object throughout the specified period.

**Parameters:**
- `weeks_to_analyze` (list): List of week numbers to analyze
- `year` (int, optional): Target year

**Returns:**
- Dictionary mapping object names to their optimal observation periods

### Visualization and Reporting

#### `plot_weekly_analysis(weekly_results, period_desc="analysis period")`
Creates comprehensive visualization plots for weekly analysis.

**Parameters:**
- `weekly_results` (dict): Results from weekly analysis
- `period_desc` (str): Description of analysis period

**Returns:**
- matplotlib figure object with 6 subplots:
  1. Observable objects by week (scatter plot with score coloring)
  2. Moon-free objects by week (bar chart)
  3. Mosaic opportunities by week (bar chart)
  4. Weekly astrophotography scores (bar chart with best week highlighted)
  5. Moon phase throughout weeks (line plot)
  6. Object distribution with config compliance (grouped bar chart)

#### `print_weekly_summary(weekly_results, period_desc="analysis period")`
Prints comprehensive text summary of weekly analysis.

#### `print_yearly_object_analysis(object_analysis, period_desc="analysis period")`
Prints detailed analysis of optimal observation times for each object.

## Configuration

### Field of View Configuration
The script reads telescope configuration from `config.json`:

```json
{
  "imaging": {
    "scope": {
      "fov_width": 2.4,
      "fov_height": 1.8,
      "mosaic_fov_width": 4.7,
      "mosaic_fov_height": 3.5
    }
  }
}
```

### Time Period Definitions

```python
HALF_YEAR_RANGES = {
    'H1': (1, 26),   # First half: weeks 1-26
    'H2': (27, 52)   # Second half: weeks 27-52
}

QUARTER_RANGES = {
    'Q1': (1, 13),   # Q1: weeks 1-13
    'Q2': (14, 26),  # Q2: weeks 14-26
    'Q3': (27, 39),  # Q3: weeks 27-39
    'Q4': (40, 52)   # Q4: weeks 40-52
}

MONTH_TO_WEEKS = {
    1: (1, 4),    # January: weeks 1-4
    2: (5, 8),    # February: weeks 5-8
    # ... (continues for all 12 months)
}
```

## Command Line Usage

### Basic Usage
```bash
# Analyze entire year
python trajectory_analysis.py

# Analyze specific periods
python trajectory_analysis.py --quarter Q1
python trajectory_analysis.py --half H2
python trajectory_analysis.py --month 3

# Skip plot generation
python trajectory_analysis.py --no-plots
```

### Command Line Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `--half` | choice | Analyze first (H1) or second (H2) half of year |
| `--quarter` | choice | Analyze specific quarter (Q1, Q2, Q3, Q4) |
| `--month` | int | Analyze specific month (1-12) |
| `--year` | flag | Analyze entire year (default) |
| `--no-plots` | flag | Skip generating plots |

## Output

### Weekly Analysis Output
For each analyzed week, the script provides:
- Total catalog objects
- Observable objects (within visibility window)
- Config-compliant objects (meeting time requirements)
- Exposure-limited objects
- Moon illumination percentage
- Moon-free vs moon-affected object counts
- Single-frame targets vs mosaic groups
- Weekly astrophotography score

### Object Analysis Output
For each astronomical object:
- Best observation weeks with scores
- Moon-free opportunity count
- Config-compliant weeks
- Optimal month recommendations
- Mosaic requirements

### Visualizations
- **Weekly Trends**: Observable objects, scores, moon phases
- **Mosaic Opportunities**: Distribution of mosaic groups by week
- **Object Distribution**: Config-compliant vs moon-affected objects
- **Comparative Analysis**: Week-by-week scoring and ranking

## Algorithm Details

### Moon Interference Algorithm
1. **Angular Separation**: Calculate great circle distance between object and moon
2. **Illumination-Based Thresholds**:
   - New moon (0-10%): 20° interference radius
   - Thin crescent (10-30%): 30° radius
   - Quarter moon (30-50%): 45° radius
   - Gibbous moon (50-70%): 60° radius
   - Nearly full (70-90%): 90° radius
   - Full moon (90-100%): 120° radius + sky brightness penalty

### Mosaic Clustering Algorithm
1. **Individual Assessment**: Identify objects requiring individual mosaics
2. **Seed Selection**: Start clusters with remaining objects
3. **Proximity Grouping**: Add nearby objects within effective mosaic FOV
4. **Compactness Optimization**: Ensure cluster fits comfortably within FOV
5. **Practical Limits**: Limit clusters to 6 objects for practical imaging

### Scoring Algorithm
The weekly astrophotography score combines multiple weighted factors:
- **Object Availability**: Base score from observable objects
- **Moon Conditions**: Heavy penalty for bright moon phases
- **Mosaic Opportunities**: Significant bonus for efficient groupings
- **Night Duration**: Bonus for longer observation windows
- **Config Compliance**: Bonus for objects meeting visibility requirements

## Best Practices

### For Accurate Analysis
1. Ensure `config.json` contains accurate telescope specifications
2. Update location coordinates and Bortle index in configuration
3. Adjust minimum visibility hours based on imaging requirements
4. Consider seasonal weather patterns in planning

### For Mosaic Planning
1. Review clustered objects for practical imaging sequences
2. Consider object brightness compatibility within clusters
3. Plan transition times between mosaic panels
4. Account for meridian flips and tracking limitations

### For Long-term Planning
1. Run yearly analysis for seasonal trend identification
2. Use monthly analysis for detailed session planning
3. Cross-reference with weather forecasting services
4. Consider moon-free periods for faint object imaging

## Error Handling and Limitations

### Known Limitations
1. **Simplified Moon Calculations**: Uses approximate lunar position
2. **Weather Independence**: Does not consider meteorological conditions
3. **Seasonal Assumptions**: Based on astronomical visibility only
4. **Fixed Configuration**: Requires manual telescope specification updates

### Error Handling
- Graceful fallback for missing object data
- Default values for unparseable magnitude or FOV information
- Robust date handling across year boundaries
- Configuration file error recovery

## Integration Notes

This script integrates with the main `astropy` module and expects:
- Object catalog access via `get_objects_from_csv()` or `get_combined_catalog()`
- Twilight calculation functions
- Visibility window analysis functions
- Location and configuration data from the main module

For optimal results, ensure the main astropy configuration is properly set up with accurate location data, telescope specifications, and observing constraints. 