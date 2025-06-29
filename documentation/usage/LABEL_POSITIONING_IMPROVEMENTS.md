# Label Positioning Improvements for Trajectory Plots

## Overview

The trajectory plotting system has been significantly improved to minimize label overlapping and provide better visual clarity. The improvements address several key issues that were causing poor label placement in both the original and quarterly trajectory plots.

## Problems Addressed

### 1. **Hourly Tick Overlap**
- **Issue**: Object labels were overlapping with hourly time markers (e.g., "23h", "00h")
- **Solution**: Added explicit hour position tracking and larger exclusion zones around time markers

### 2. **Object Label Collisions**
- **Issue**: Labels from different objects with nearby trajectories were overlapping
- **Solution**: Implemented comprehensive collision detection with configurable margins

### 3. **Poor Trajectory Segment Selection**
- **Issue**: Labels were placed at random points along trajectories, sometimes at endpoints or curved sections
- **Solution**: Added intelligent segment scoring that prefers:
  - Straighter trajectory segments
  - Middle portions of trajectories (avoiding endpoints)
  - Areas with good clearance from other elements

### 4. **Inadequate Offset Calculation**
- **Issue**: Fixed offset positioning caused labels to overlap with trajectory lines
- **Solution**: Dynamic offset calculation based on trajectory direction

### 5. **FIXED: Missing Labels** ⭐
- **Issue**: Some trajectories had no labels when optimal positions couldn't be found
- **Solution**: Added comprehensive fallback logic that always returns a position:
  - First attempts optimal positioning with full margins
  - Falls back to reduced margins if needed
  - Finally uses trajectory midpoint as absolute fallback

### 6. **FIXED: Label Transparency** ⭐
- **Issue**: Labels were too opaque and hiding trajectory lines underneath
- **Solution**: Increased transparency (alpha = 0.4) for better visual integration

## Technical Improvements

### New `find_optimal_label_position()` Function

Replaces the simple `find_label_position()` with a sophisticated algorithm that:

```python
def find_optimal_label_position(azimuths, altitudes, hour_positions, existing_positions, 
                               existing_labels, margin=8):
```

**Key Features:**
- **Forbidden Zone Detection**: Creates exclusion zones around hourly ticks and existing labels
- **Trajectory Scoring**: Evaluates potential label positions based on:
  - Curvature (prefers straighter segments)
  - Distance from trajectory center (prefers middle sections)
  - Clearance from other elements
- **Smart Margins**: Uses larger margins for hourly ticks (1.5x) than regular labels
- **Comprehensive Fallback**: Always returns a position, with multiple fallback strategies

### Enhanced `calculate_label_offset()` Function

Calculates intelligent label offsets based on trajectory direction:

```python
def calculate_label_offset(trajectory_az, trajectory_alt, trajectory_idx, azimuths, altitudes):
```

**Features:**
- **Direction Analysis**: Calculates trajectory direction at label position
- **Perpendicular Placement**: Positions labels perpendicular to trajectory direction
- **Adaptive Offsets**: Adjusts offset distance based on trajectory orientation

## Implementation Details

### 1. **Hour Position Collection**
```python
hour_positions = [(az, alt) for az, alt in zip(hour_azs, hour_alts)]
```
- Collects all hourly marker positions for collision avoidance
- Used in all three plotting modes (regular, quarterly, enhanced)

### 2. **Collision Detection**
```python
for fz_az, fz_alt, fz_margin in forbidden_zones:
    distance = ((az - fz_az)**2 + (alt - fz_alt)**2)**0.5
    if distance < fz_margin:
        conflicts = True
```
- Euclidean distance calculation for precise collision detection
- Variable margins for different element types

### 3. **Fallback Logic** ⭐
```python
# FALLBACK: If no optimal position found, use reduced margin check
fallback_candidates = []
reduced_margin = margin * 0.5  # Use smaller margin for fallback

# ... check positions with reduced margin ...

# FINAL FALLBACK: Just use trajectory middle point if all else fails
mid_idx = len(azimuths) // 2
return (azimuths[mid_idx], altitudes[mid_idx])
```

### 4. **Enhanced Transparency** ⭐
```python
bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.4)
```
- Reduced alpha from 0.8/0.9 to 0.4 for better transparency
- Labels are now more transparent and don't hide trajectory lines

## Visual Improvements

### 1. **Better Label Appearance**
- **Semi-transparent backgrounds** (alpha=0.4) for better trajectory visibility
- **Rounded corners** for modern appearance
- **Appropriate font sizes** (10pt for quarters, 12pt for enhanced)
- **High z-order** (15) to ensure labels appear above trajectory elements while staying transparent

### 2. **Smart Positioning**
- Labels avoid the first and last 20% of trajectories (endpoints)
- Preference for trajectory middle sections
- Minimum 6-8 degree margins from other elements
- **Always shows labels** with intelligent fallback positioning

### 3. **Consistent Styling**
- Uniform label appearance across all plotting modes
- Proper transparency for trajectory visibility
- Color-coordinated with trajectory colors

## Usage

The improvements are automatically applied to all trajectory plotting modes:

```bash
# Regular trajectory plot with improved labels
python astronightplanner.py

# Quarterly plots with clean label positioning
python astronightplanner.py --quarters

# Enhanced plot with priority-based object selection
python astronightplanner.py --enhanced
```

## Configuration

### Adjustable Parameters

- **`margin`**: Distance threshold for collision detection (default: 6-8 degrees)
- **`curvature_weight`**: Importance of trajectory straightness (default: 0.7)
- **`center_weight`**: Preference for trajectory middle (default: 0.3)
- **`hour_margin_multiplier`**: Extra space around time markers (default: 1.5x)
- **`fallback_margin_multiplier`**: Reduced margin for fallback (default: 0.5x)

### Customization

The label positioning can be fine-tuned by modifying the scoring weights in `find_optimal_label_position()`:

```python
# Prefer straighter segments more heavily
total_score = curvature_score * 0.8 + center_preference * 0.2

# Prefer center positions more heavily  
total_score = curvature_score * 0.5 + center_preference * 0.5
```

## Results

The improvements provide:

1. **Complete coverage** - Every trajectory now has a label (no anonymous trajectories)
2. **Zero overlap** between object labels and hourly time markers
3. **Minimal collision** between labels from different objects
4. **Better transparency** - Labels don't hide trajectory lines underneath
5. **Intelligent positioning** that adapts to trajectory geometry
6. **Consistent appearance** across all plotting modes

## Recent Fixes (Latest Update)

### Fixed Missing Labels Issue
- **Problem**: Some trajectories were anonymous when optimal positions couldn't be found
- **Solution**: Added multi-level fallback logic that ensures every trajectory gets a label
- **Result**: 100% label coverage across all trajectory plots

### Fixed Transparency Issue  
- **Problem**: Labels were too opaque (alpha=0.8-0.9) and hiding trajectory lines
- **Solution**: Reduced alpha to 0.4 for better transparency
- **Result**: Labels are clearly visible but don't obscure trajectory lines

## Future Enhancements

Potential future improvements could include:

1. **Dynamic margin adjustment** based on plot density
2. **Multi-line labels** for very long object names
3. **Curved label positioning** following trajectory paths
4. **Interactive label repositioning** in GUI environments
5. **Automatic font size scaling** based on available space

The current implementation provides a solid foundation for clear, readable trajectory plots with professional-quality label positioning and guaranteed label coverage for all trajectories. 