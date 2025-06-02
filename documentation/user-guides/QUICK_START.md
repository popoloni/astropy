# AstroPy Quick Start Guide

Get up and running with AstroPy Observation Planner in minutes!

## 🚀 Installation & Setup

### 1. Basic Setup
```bash
# Clone or download the project
# Ensure you have Python 3.7+ with matplotlib, astropy, and pytz

# Basic usage
python3 nightplanner.py --report-only
```

### 2. Configure Your Location
Edit `config.json`:
```json
{
  "locations": {
    "my_location": {
      "name": "My Observatory",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York",
      "min_altitude": 15,
      "max_altitude": 75,
      "default": true
    }
  }
}
```

## 📱 Platform-Specific Quick Start

### Desktop (macOS/Linux/Windows)
```bash
# Text report only (fastest)
python3 nightplanner.py --report-only

# With trajectory plots
python3 nightplanner.py

# Mosaic photography planning
python3 nightplanner.py --mosaic

# Use wrapper scripts for convenience
python3 wrappers/run_report_only.py
```

### iPad (Pythonista)
1. Copy all files to Pythonista
2. Tap any wrapper script in `wrappers/` folder:
   - `run_report_only.py` - Quick text report
   - `run_with_plots.py` - Full plots
   - `run_mosaic_plots.py` - Mosaic photography

## 🎯 Common Tasks

### Quick Observation Report
```bash
# Fastest way to see tonight's targets
python3 nightplanner.py --report-only
```

### Visual Planning with Plots
```bash
# Complete trajectory plots
python3 nightplanner.py

# Clean 4-quarter plots (less cluttered)
python3 nightplanner.py --quarters
```

### Mosaic Astrophotography
```bash
# Find objects that can be photographed together
python3 nightplanner.py --mosaic --report-only

# Create specialized mosaic plots
python3 nightplanner.py --mosaic
```

### Different Scheduling Strategies
```bash
# Maximum number of objects (visual observing)
python3 nightplanner.py --schedule max_objects --report-only

# Best imaging conditions
python3 nightplanner.py --schedule optimal_snr --report-only

# Longest observation windows
python3 nightplanner.py --schedule longest_duration --report-only

# Mosaic group prioritization
python3 nightplanner.py --schedule mosaic_groups --report-only
```

## 🔧 Essential Configuration

### Telescope Setup (for astrophotography)
```json
{
  "imaging": {
    "scope": {
      "name": "Your Telescope",
      "fov_width": 2.4,
      "fov_height": 1.8,
      "mosaic_fov_width": 4.7,
      "mosaic_fov_height": 3.5
    }
  }
}
```

### Location Settings
```json
{
  "locations": {
    "your_site": {
      "latitude": 40.7128,    // Your latitude
      "longitude": -74.0060,  // Your longitude  
      "timezone": "America/New_York",  // IANA timezone
      "min_altitude": 15,     // Minimum object altitude
      "max_altitude": 75,     // Maximum altitude (avoid zenith)
      "bortle_index": 6       // Light pollution level (1-9)
    }
  }
}
```

## 📊 Understanding the Output

### Text Report Sections
1. **Configuration** - Your location and settings
2. **Observation Schedule** - Tonight's recommended targets
3. **Visibility Summary** - All visible objects with timing
4. **Moon Information** - Phase, rise/set times, interference
5. **Mosaic Groups** - Objects that can be photographed together (if using --mosaic)

### Plot Types
- **Trajectory Plot** - Object paths across the sky
- **Visibility Chart** - Timeline showing when objects are observable
- **Mosaic Plots** - Specialized charts for multi-target photography

### Visual Cues
- **🟡 Yellow labels** - Objects scheduled for tonight
- **⚪ White labels** - Visible but not scheduled
- **Red hatching** - Scheduled observation periods
- **Gold segments** - Moon interference periods

## 🎮 Wrapper Scripts (Convenience)

Instead of remembering command-line options, use these:

### Text Reports
- `run_report_only.py` - Quick text report
- `run_quarters_report.py` - 4-quarter analysis (text only)
- `tests/integration/run_test_simulation.py` - Test with simulated nighttime

### With Plots
- `run_with_plots.py` - Complete plots
- `run_quarters.py` - 4-quarter plots (cleaner)
- `run_mosaic_plots.py` - Mosaic photography plots

### Specific Strategies
- `run_max_objects.py` - Maximum targets
- `run_optimal_snr.py` - Best imaging conditions
- `run_longest_duration.py` - Longest observation windows

## 🆘 Quick Troubleshooting

### Common Issues
- **No objects found**: Check your location coordinates and altitude limits
- **Empty schedule**: Your visibility constraints might be too restrictive
- **Plot errors**: Ensure matplotlib is installed
- **Config errors**: Validate your JSON syntax

### Quick Fixes
```bash
# Test with relaxed constraints
python3 nightplanner.py --report-only  # Uses default settings

# Check your configuration
python3 -c "import json; print(json.load(open('config.json')))"

# Simulate nighttime during day
python3 nightplanner.py --simulate-time "22:00" --report-only
```

## 📚 Next Steps

Once you're comfortable with the basics:

1. **Read the full documentation**: [docs/README.md](README.md)
2. **Explore mosaic features**: [user-guides/MOSAIC_FEATURES_SUMMARY.md](user-guides/MOSAIC_FEATURES_SUMMARY.md)
3. **iPad setup**: [user-guides/README_PYTHONISTA.md](user-guides/README_PYTHONISTA.md)
4. **Advanced configuration**: [Main README](../README.md)

## 🎯 Most Common Workflows

### New User Workflow
1. Configure location in `config.json`
2. Run `python3 nightplanner.py --report-only`
3. Review the observation schedule
4. Try `python3 nightplanner.py` for plots

### Astrophotographer Workflow
1. Run `python3 nightplanner.py --mosaic --report-only`
2. Check mosaic groups for multi-target sessions
3. Use `python3 nightplanner.py --schedule optimal_snr` for best conditions
4. Generate plots with `python3 nightplanner.py --mosaic`

### Visual Observer Workflow
1. Run `python3 nightplanner.py --schedule max_objects --report-only`
2. Use `python3 nightplanner.py --quarters` for clean trajectory plots
3. Focus on the visibility chart for timing

---

*This quick start guide covers the essentials. For comprehensive documentation, see [docs/README.md](README.md).* 