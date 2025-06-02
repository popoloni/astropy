# Recent Updates - Mosaic Analysis Improvements

*Last Updated: January 2025*

## Overview

This document summarizes the recent improvements to the AstroPy Observation Planner, focusing on enhanced mosaic functionality and visual chart improvements.

## 🆕 New Features

### `--no-duplicates` Flag

A new command-line flag that enhances the mosaic analysis workflow by preventing duplicate object listings.

**Usage:**
```bash
# Standard mosaic analysis (shows individual objects + mosaic groups)
python nightplanner.py --mosaic

# Clean mosaic analysis (shows only mosaic groups, no individual duplicates)
python nightplanner.py --mosaic --no-duplicates
```

**Benefits:**
- **Cleaner Reports**: Objects appear only in their mosaic groups, eliminating confusion
- **Streamlined Scheduling**: Mosaic groups are treated as unified observation targets
- **Better Planning**: Reduces visual clutter in reports and charts

### Visual Chart Improvements

Two key visual enhancements improve the usability of visibility charts:

#### 1. Legend Position Fix
- **Before**: Legend appeared in bottom-right corner, often overlapping with visibility bars
- **After**: Legend moved to bottom-left corner, avoiding overlap with data
- **Impact**: Better chart readability and no data obstruction

#### 2. Enhanced Mosaic Labels
- **Before**: Mosaic groups displayed generic "Mosaic" labels
- **After**: Shows abbreviated names of constituent objects
- **Examples**:
  - Small groups (≤3 objects): "M8, M20, IC4685"
  - Larger groups: "M8, M20 +1" (shows first two + count)
- **Impact**: Immediately understand what objects are in each mosaic group

## 🔧 Technical Changes

### Modified Functions
- **`combine_objects_and_groups()`**: Added `no_duplicates` parameter for filtering
- **Visibility chart generation**: Updated to use filtered object lists
- **Y-axis labels**: Enhanced to show constituent object names for mosaic groups
- **Text annotations**: Updated to display abbreviated object names

### Workflow Improvements
- **Report generation**: Now uses combined object lists when filtering is enabled
- **Argument parsing**: Added `--no-duplicates` flag with proper help text
- **Wrapper integration**: Updated `run_mosaic_plots.py` to use new functionality

## 📊 User Impact

### Before the Changes
```
PRIME TARGETS
=============
M8 / Lagoon Nebula
M20 / Trifid Nebula
M16 / Eagle Nebula
M17 / Omega Nebula

MOSAIC GROUPS
=============
Group 1: Mosaic
Group 2: Mosaic
```

### After the Changes (with `--no-duplicates`)
```
PRIME TARGETS
=============
E_Nebula
IC 1318 (Butterfly Nebula)
IC 4665 (Summer Beehive Cluster)

MOSAIC GROUPS
=============
Group 1: M8, M20, IC4685
Group 2: M16, M17
```

## 🎯 Use Cases

### 1. Clean Planning Sessions
Use `--no-duplicates` when you want a focused view of unique observation targets without redundancy.

### 2. Mosaic-First Workflows
When your primary goal is mosaic photography, this flag ensures you see each sky region only once.

### 3. Streamlined Scheduling
The cleaner output makes it easier to plan observation sequences without confusion about duplicate targets.

## 📱 Platform Support

### Desktop Usage
```bash
python nightplanner.py --mosaic --no-duplicates
```

### iPad (Pythonista)
The `run_mosaic_plots.py` wrapper automatically includes the `--no-duplicates` functionality:
```python
exec(open('wrappers/run_mosaic_plots.py').read())
```

## 🔄 Migration Notes

### For Existing Users
- **No breaking changes**: All existing functionality remains unchanged
- **Optional enhancement**: Use `--no-duplicates` when you want cleaner output
- **Backward compatibility**: All existing scripts and commands continue to work

### For Wrapper Scripts
- **`run_mosaic_plots.py`**: Automatically uses `--no-duplicates` for cleaner output
- **Other wrappers**: Unaffected, continue to work as before

## 📚 Related Documentation

- **[Main README](../README.md)**: Complete project documentation
- **[Command Line Options](../README.md#command-line-options)**: Full list of available flags
- **[Mosaic Features Guide](user-guides/MOSAIC_FEATURES_SUMMARY.md)**: Comprehensive mosaic photography guide
- **[Wrapper Scripts Guide](user-guides/WRAPPERS_GUIDE.md)**: Using convenient wrapper scripts

## 🚀 Future Enhancements

Potential future improvements building on these changes:
- **Custom grouping rules**: Allow users to define custom mosaic grouping criteria
- **Export functionality**: Save clean observation lists to external formats
- **Interactive filtering**: Toggle duplicate filtering in real-time
- **Group prioritization**: Advanced scheduling based on mosaic group characteristics

---

*These improvements enhance the mosaic analysis workflow while maintaining full backward compatibility with existing usage patterns.* 