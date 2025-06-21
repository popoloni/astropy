# 🌅 Configurable Twilight System

**Flexible twilight configuration for optimized astronomical observation planning**

## Overview

The Configurable Twilight System allows users to choose between different twilight definitions to optimize observation planning for their specific astronomical goals. This feature provides precise control over when observations begin and end based on sky darkness requirements.

## Twilight Types

### 🌆 **Civil Twilight (-6°)**
- **Definition**: Sun is 6° below the horizon
- **Sky Conditions**: Bright twilight, horizon still visible
- **Best For**: 
  - Planetary observations
  - Bright star measurements
  - Moon and bright object imaging
  - Setup and equipment testing
- **Observation Window**: **Shorter** but starts earlier in evening

### 🌌 **Nautical Twilight (-12°)**
- **Definition**: Sun is 12° below the horizon  
- **Sky Conditions**: Moderate darkness, navigation stars visible
- **Best For**:
  - General amateur astronomy
  - Balanced observation sessions
  - Star cluster observations
  - Wide-field astrophotography
- **Observation Window**: **Balanced** timing and duration

### ⭐ **Astronomical Twilight (-18°)** _(Default)_
- **Definition**: Sun is 18° below the horizon
- **Sky Conditions**: Complete darkness, faintest objects visible
- **Best For**:
  - Deep sky imaging  
  - Faint nebula and galaxy photography
  - Scientific observations
  - Professional astronomy work
- **Observation Window**: **Longest** but starts latest in evening

## Configuration

### Setting Twilight Type

Edit `config.json` in the visibility section:

```json
{
  "visibility": {
    "min_visibility_hours": 2,
    "min_total_area": 225, 
    "trajectory_interval_minutes": 15,
    "search_interval_minutes": 1,
    "twilight_type": "astronomical",
    "comment": "twilight_type options: 'civil' (-6°), 'nautical' (-12°), 'astronomical' (-18°)"
  }
}
```

### Valid Options
- `"civil"` - Civil twilight (-6°)
- `"nautical"` - Nautical twilight (-12°) 
- `"astronomical"` - Astronomical twilight (-18°)

## Implementation

### Core Function

The system uses a centralized twilight calculation function:

```python
from astronomy import find_configured_twilight
from datetime import datetime

# Automatically uses configured twilight type
evening_twilight, morning_twilight = find_configured_twilight(datetime.now())
```

### High Precision Support

The system automatically uses high-precision calculations when available:

```python
# High precision mode (if available)
evening, morning = find_configured_twilight(date, precision_mode='high')

# Standard mode fallback
evening, morning = find_configured_twilight(date, precision_mode='standard')
```

### Backward Compatibility

Legacy code continues to work unchanged:

```python
# Legacy function still works (delegates to configured twilight)
from astronomy import find_astronomical_twilight
evening, morning = find_astronomical_twilight(date)
```

## Applications Updated

All main applications automatically use the configured twilight type:

### 🌟 astronightplanner.py
- **Main observation planner** uses configured twilight for night definition
- **Visibility analysis** respects chosen twilight boundaries
- **Report generation** shows appropriate observation windows

### 🌌 astroseasonplanner.py  
- **Multi-night planning** uses configured twilight across all weeks
- **Seasonal analysis** respects twilight type for consistency
- **Mosaic planning** optimizes using configured night boundaries

### 🔭 run_mosaic_plots.py
- **Mosaic trajectory plotting** uses configured twilight through astronightplanner
- **Group analysis** respects chosen observation windows
- **Visualization** shows accurate night boundaries

## Example Outputs

### Civil Twilight Example
```
NIGHT OBSERVATION REPORT
=======================
Observation Window: 20:45 - 06:15
Twilight Type: Civil (-6°)
```

### Nautical Twilight Example  
```
NIGHT OBSERVATION REPORT
=======================
Observation Window: 21:30 - 05:30
Twilight Type: Nautical (-12°)
```

### Astronomical Twilight Example
```
NIGHT OBSERVATION REPORT
=======================
Observation Window: 22:26 - 05:32
Twilight Type: Astronomical (-18°)
```

## Technical Details

### Architecture
- **Centralized calculations**: `astronomy/celestial.py`
- **Configuration loading**: `config/settings.py`
- **Function delegation**: Legacy functions delegate to new system
- **Error handling**: Graceful fallbacks and validation

### Performance
- **No performance impact**: Same calculation methods used
- **Intelligent caching**: High-precision results cached when available
- **Minimal overhead**: Configuration read once at startup

### Error Handling
- **Invalid twilight types**: Defaults to astronomical twilight
- **Missing configuration**: Falls back to astronomical twilight
- **Calculation failures**: Uses standard method fallback
- **Timezone issues**: Proper timezone handling and conversion

## Use Case Examples

### Deep Sky Astrophotography
```json
"twilight_type": "astronomical"
```
- **Darkest possible skies** for faint object imaging
- **Maximum contrast** for nebulae and galaxies
- **Professional-grade** observation conditions

### Planetary Imaging
```json
"twilight_type": "civil"  
```
- **Earlier observation start** when planets are higher
- **Sufficient darkness** for planetary detail
- **Longer observation window** for tracking

### General Amateur Astronomy
```json
"twilight_type": "nautical"
```
- **Balanced approach** between darkness and duration
- **Good compromise** for mixed observation sessions
- **Practical timing** for hobbyist schedules

## Migration Guide

### From Fixed Astronomical Twilight
No changes needed - astronomical twilight remains the default.

### Existing Custom Twilight Code
Replace custom twilight calculations with the centralized system:

```python
# Before - custom twilight calculation
def my_twilight_calc(date):
    # Custom implementation
    pass

# After - use configured system  
from astronomy import find_configured_twilight
evening, morning = find_configured_twilight(date)
```

### Testing Configuration Changes
Test different twilight types safely:

```python
# Test configuration impact
for twilight_type in ['civil', 'nautical', 'astronomical']:
    # Update config.json with twilight_type
    # Run: python astronightplanner.py --report-only  
    # Compare observation windows
```

## Troubleshooting

### Configuration Not Loading
- Verify `config.json` syntax is valid JSON
- Check `twilight_type` is in `visibility` section
- Ensure value is one of: "civil", "nautical", "astronomical"

### Unexpected Observation Windows
- Check twilight type is appropriate for your goals
- Verify location settings are correct
- Consider seasonal variations in twilight timing

### High Precision Issues
- System falls back to standard calculations automatically
- Check `astronomy/precision/` module availability
- Review error logs for precision calculation failures

## Status

✅ **PRODUCTION READY** - Fully implemented and tested across all applications
✅ **BACKWARD COMPATIBLE** - Existing code works unchanged  
✅ **WELL TESTED** - Configuration, calculation, and integration tests passing
✅ **DOCUMENTED** - Complete usage and technical documentation 