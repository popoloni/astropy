# Trajectory Plotting Improvements for Astropy Observatory Planning

## Overview

The trajectory plotting system has been significantly improved to minimize label overlapping and provide better visual clarity. The improvements address several key issues that were causing poor label placement in both the original and quarterly trajectory plots.

## Problems Addressed

### 1. **Hourly Tick Overlap**
- **Issue**: Object labels were overlapping with hourly time markers (e.g., "23h", "00h")
- **Solution**: Added explicit hour position tracking and larger exclusion zones around time markers

### 2. **Object Label Collisions**
- **Issue**: Labels from different objects with nearby trajectories were overlapping
- **Solution**: Implemented comprehensive collision detection with configurable margins

### 3. **Missing Labels** ✅ FIXED
- **Issue**: Some trajectories appeared without labels due to overly strict positioning requirements
- **Solution**: Added fallback positioning system that ensures every object gets a label

### 4. **Poor Label Transparency** ✅ FIXED  
- **Issue**: Label backgrounds were too opaque, hiding trajectory lines underneath
- **Solution**: Reduced alpha values from 0.8-0.9 to 0.4 for better transparency

### 5. **Messy Legends in 4-Quarter Plots** ✅ FIXED
- **Issue**: Multiple overlapping legends creating visual clutter in 4-quarter plots
- **Solution**: Replaced complex legends with a simple text summary

## Available Plotting Modes

### 1. **Original Single Plot (Default)**
**Usage**: `python astropy.py`

- Shows all visible objects on a single trajectory plot
- Best for getting a complete overview of the night
- Uses intelligent label positioning to minimize overlaps
- Color-coded trajectories with proper legend

### 2. **4-Quarter Trajectory Plots (`--quarters`)**
**Usage**: `python astropy.py --quarters`

- Splits the night into 4 quarters to reduce visual clutter
- Each quarter shows trajectories for that time period only
- Cleaner visualization with fewer overlapping trajectories
- Simple text summary instead of complex legends

## Technical Improvements

### Enhanced Label Positioning Algorithm

The new `find_optimal_label_position()` function:

1. **Avoids Hour Markers**: Labels stay clear of hourly time annotations
2. **Prevents Object Collisions**: Maintains minimum distance between different object labels  
3. **Fallback System**: Always returns a position, even if not optimal
4. **Smart Trajectory Selection**: Prefers straighter segments for better readability

### Improved Transparency

- **Label backgrounds**: Reduced from α=0.8-0.9 to α=0.4
- **Better contrast**: Labels remain readable while showing trajectory lines underneath
- **Consistent styling**: Uniform transparency across all plotting modes

### Cleaner 4-Quarter Implementation

- **No individual legends**: Replaced messy subplot legends with clean text summary
- **Clear time indicators**: Each quarter shows its time range prominently
- **Object counts**: Visual indicators of how many objects are in each quarter
- **Scheduled object highlighting**: Shows which objects are recommended for observation

## Usage Examples

```bash
# Standard trajectory plot with improved labels
python astropy.py

# 4-quarter view for less cluttered visualization  
python astropy.py --quarters

# Text report only (no plots)
python astropy.py --report-only

# Use visibility margins for extended coverage
python astropy.py --quarters

# Disable visibility margins for strict boundaries
python astropy.py --quarters --no-margins
```

## Configuration Options

| Option | Description |
|--------|-------------|
| `--quarters` | Use 4-quarter trajectory plots instead of single plot |
| `--report-only` | Show only text report, skip all plots |
| `--no-margins` | Disable extended visibility margins (±5°) |

## Results

### Before vs After

**Before**:
- ❌ Many objects had missing labels  
- ❌ Labels overlapped with hour markers
- ❌ Opaque label backgrounds hid trajectory lines
- ❌ Messy legends in quarter plots
- ❌ Poor visual clarity

**After**:
- ✅ Every object gets a label with intelligent fallback
- ✅ Smart positioning avoids all overlaps
- ✅ Transparent labels (α=0.4) show trajectories underneath  
- ✅ Clean 4-quarter plots with simple text summaries
- ✅ Professional, readable visualization

## Implementation Notes

### Label Positioning Strategy
1. **Primary Algorithm**: Find optimal position avoiding all conflicts
2. **Fallback Algorithm**: Use reduced margins if no optimal position found
3. **Final Fallback**: Use trajectory midpoint if all else fails

### Transparency Optimization
- **Background alpha**: 0.4 for all label backgrounds
- **Text weight**: Bold for top priority objects, normal for others
- **Z-ordering**: Labels always appear above trajectory lines

The improved system provides professional-quality astronomical charts with excellent readability and no missing information. 