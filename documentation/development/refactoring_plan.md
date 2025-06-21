# Plotting Functions Refactoring Plan

## Overview
This document outlines the plan for refactoring all plotting functions in the AstroScope application. The goal is to consolidate and organize plotting functions into a dedicated `plots` module while ensuring backward compatibility and maintaining functionality across both desktop and mobile platforms.

## Directory Structure
```
plots/
├── __init__.py
├── base.py              # Base plotting utilities and common functions
├── trajectory/
│   ├── __init__.py
│   ├── desktop.py      # Desktop trajectory plotting
│   └── mobile.py       # Mobile trajectory plotting
├── visibility/
│   ├── __init__.py
│   ├── desktop.py      # Desktop visibility charts
│   └── mobile.py       # Mobile visibility charts
├── mosaic/
│   ├── __init__.py
│   ├── desktop.py      # Desktop mosaic plotting
│   └── mobile.py       # Mobile mosaic plotting
├── weekly/
│   ├── __init__.py
│   ├── desktop.py      # Desktop weekly analysis
│   └── mobile.py       # Mobile weekly analysis
└── utils/
    ├── __init__.py
    ├── verification.py # Plot verification utilities
    └── common.py       # Shared utilities
```

## Function Analysis and Split

### 1. Trajectory Plots
#### Desktop Functions
- `plot_object_trajectory()`
- `plot_moon_trajectory()`
- `plot_quarterly_trajectories()`
- `setup_altaz_plot()`

#### Mobile Adaptations
- Touch-optimized controls
- Reduced resolution
- Simplified labels
- Memory-efficient rendering
- Touch-friendly navigation

### 2. Visibility Charts
#### Desktop Functions
- `plot_visibility_chart()`
- Time-based visualization
- Detailed scheduling display

#### Mobile Adaptations
- Simplified time display
- Touch-friendly time selection
- Optimized for small screens
- Reduced data points

### 3. Mosaic Plots
#### Desktop Functions
- `plot_mosaic_group_trajectory()`
- `create_mosaic_trajectory_plot()`
- `create_mosaic_grid_plot()`
- `plot_mosaic_fov_indicator()`
- `plot_mosaic_fov_at_optimal_time()`

#### Mobile Adaptations
- Simplified FOV indicators
- Touch-friendly group selection
- Optimized grid layout
- Reduced detail level

### 4. Weekly Analysis
#### Desktop Functions
- `plot_weekly_analysis()`
- Comprehensive statistics
- Detailed visualizations

#### Mobile Adaptations
- Simplified statistics
- Touch-friendly navigation
- Optimized for small screens
- Reduced data visualization

## Implementation Plan (Scrum Approach)

### Sprint 1: Base Infrastructure
#### Goals
- Create directory structure
- Implement base plotting utilities
- Set up verification framework

#### Tasks
1. Create `plots` directory and subdirectories
2. Implement `base.py` with common utilities
3. Set up verification framework
4. Create baseline plots
5. Implement basic verification
6. Test framework functionality

#### Deliverables
- Working base infrastructure
- Verification system
- Documentation

### Sprint 2: Trajectory Plots
#### Goals
- Migrate trajectory plotting functions
- Implement mobile adaptations
- Update references

#### Tasks
1. Move trajectory functions to new structure
2. Implement mobile adaptations
3. Update imports and references
4. Create verification tests
5. Test on both platforms

#### Deliverables
- Working trajectory plots
- Mobile support
- Updated documentation

### Sprint 3: Visibility Charts
#### Goals
- Migrate visibility chart functions
- Implement mobile adaptations
- Update references

#### Tasks
1. Move visibility functions to new structure
2. Implement mobile adaptations
3. Update imports and references
4. Create verification tests
5. Test on both platforms

#### Deliverables
- Working visibility charts
- Mobile support
- Updated documentation

### Sprint 4: Mosaic Plots
#### Goals
- Migrate mosaic plotting functions
- Implement mobile adaptations
- Update references

#### Tasks
1. Move mosaic functions to new structure
2. Implement mobile adaptations
3. Update imports and references
4. Create verification tests
5. Test on both platforms

#### Deliverables
- Working mosaic plots
- Mobile support
- Updated documentation

### Sprint 5: Weekly Analysis
#### Goals
- Migrate weekly analysis functions
- Implement mobile adaptations
- Update references

#### Tasks
1. Move weekly analysis functions to new structure
2. Implement mobile adaptations
3. Update imports and references
4. Create verification tests
5. Test on both platforms

#### Deliverables
- Working weekly analysis
- Mobile support
- Updated documentation

## Verification System

### Plot Verification Framework
```python
class PlotVerifier:
    def __init__(self):
        self.baseline_dir = "tests/baseline_plots"
        self.temp_dir = "tests/temp_plots"
        
    def verify_plot(self, plot_func, *args, **kwargs):
        """Verify a plot function against its baseline"""
        # Generate new plot
        new_plot = plot_func(*args, **kwargs)
        
        # Get baseline plot
        baseline_name = self._get_baseline_name(plot_func)
        baseline_plot = self._load_baseline(baseline_name)
        
        # Compare plots
        return self._compare_plots(new_plot, baseline_plot)
```

### Verification Methods
1. **Pixel Comparison**
   - Compare plot images pixel by pixel
   - Allow for small differences (1-2 pixels)
   - Check color distributions

2. **Data Point Comparison**
   - Compare actual data points plotted
   - Verify correct positioning
   - Check data transformations

3. **Metadata Comparison**
   - Compare plot titles, labels, legends
   - Verify axis ranges and scales
   - Check styling and formatting

4. **Performance Comparison**
   - Compare rendering times
   - Check memory usage
   - Verify mobile optimization

## Testing Strategy

### 1. Unit Tests
- Test individual functions
- Verify parameter handling
- Check error cases

### 2. Integration Tests
- Test function combinations
- Verify data flow
- Check dependencies

### 3. Visual Regression
- Compare plot outputs
- Verify styling
- Check mobile display

### 4. Performance Tests
- Measure execution time
- Check memory usage
- Verify mobile optimization

## Continuous Integration

### CI Configuration
```yaml
stages:
  - test
  - verify
  - deploy

test:
  script:
    - python -m pytest tests/unit
    - python -m pytest tests/integration

verify:
  script:
    - python -m pytest tests/verification
    - python -m pytest tests/performance

deploy:
  script:
    - python -m pytest tests/regression
    - deploy_to_staging
```

## Progress Tracking

### Sprint Progress
- [x] Sprint 1: Base Infrastructure ✅ COMPLETED
- [x] Sprint 2: Trajectory Plots ✅ COMPLETED
- [x] Sprint 3: Visibility Charts ✅ COMPLETED
- [x] Sprint 4: Mosaic Plots ✅ COMPLETED
- [x] Sprint 5: Weekly Analysis ✅ COMPLETED

### Current Status
- All Sprints Complete
- Refactoring Project Complete ✅

### Sprint 1 Completion Summary
**Completed Tasks:**
- ✅ Created complete directory structure
- ✅ Implemented base plotting utilities (`plots/base.py`)
- ✅ Created comprehensive verification framework (`plots/utils/verification.py`)
- ✅ Added complete test suite with 83% coverage
- ✅ Set up proper imports and module structure
- ✅ Created documentation and requirements

**Deliverables:**
- Working base infrastructure with `PlotConfig`, `setup_plot()`, `setup_altaz_plot()`
- Robust verification system with `PlotVerifier` class
- Comprehensive test suite (5 tests, all passing)
- Complete documentation and setup files

### Sprint 2 Completion Summary
**Completed Tasks:**
- ✅ Created trajectory plotting modules (`plots/trajectory/`)
- ✅ Implemented desktop trajectory functions (`plots/trajectory/desktop.py`)
- ✅ Implemented mobile trajectory functions (`plots/trajectory/mobile.py`)
- ✅ Added comprehensive test suite (`tests/test_trajectory_plots.py`)
- ✅ Updated main plots module with trajectory exports
- ✅ Created mobile-optimized plotting class `MobileTrajectoryPlotter`

**Deliverables:**
- Desktop trajectory functions: `plot_object_trajectory()`, `plot_moon_trajectory()`, `plot_quarterly_trajectories()`
- Mobile trajectory functions: `MobileTrajectoryPlotter`, `create_mobile_trajectory_plot()`, etc.
- Comprehensive test suite (14 tests covering both desktop and mobile functionality)
- Full integration with verification framework
- Platform-specific optimizations (mobile: reduced detail, touch-friendly, performance optimized)

### Sprint 3 Completion Summary
**Completed Tasks:**
- ✅ Created visibility chart modules (`plots/visibility/`)
- ✅ Implemented desktop visibility functions (`plots/visibility/desktop.py`)
- ✅ Implemented mobile visibility functions (`plots/visibility/mobile.py`)
- ✅ Added comprehensive test suite (`tests/test_visibility_plots.py`)
- ✅ Updated main plots module with visibility exports
- ✅ Created mobile-optimized plotting class `MobileVisibilityPlotter`

**Deliverables:**
- Desktop visibility functions: `plot_visibility_chart()`, `create_mosaic_visibility_chart()`
- Mobile visibility functions: `MobileVisibilityPlotter`, `create_mobile_visibility_chart()`, etc.
- Comprehensive test suite (21 tests covering both desktop and mobile functionality)
- Full integration with verification framework
- Advanced features: scheduling visualization, moon interference, mosaic group support
- Mobile optimizations: object limiting, touch-friendly interface, error handling

### Sprint 4 Completion Summary
**Completed Tasks:**
- ✅ Created mosaic plotting modules (`plots/mosaic/`)
- ✅ Implemented desktop mosaic functions (`plots/mosaic/desktop.py`)
- ✅ Implemented mobile mosaic functions (`plots/mosaic/mobile.py`)
- ✅ Added comprehensive test suite (`tests/test_mosaic_plots.py`)
- ✅ Updated main plots module with mosaic exports
- ✅ Created mobile-optimized plotting class `MobileMosaicPlotter`
- ✅ Migrated all mosaic functions from main application file
- ✅ Maintained full backward compatibility

**Deliverables:**
- Desktop mosaic functions: `create_mosaic_trajectory_plot()`, `create_mosaic_grid_plot()`, `plot_mosaic_fov_indicator()`, etc.
- Mobile mosaic functions: `MobileMosaicPlotter`, `create_mobile_mosaic_trajectory_plot()`, etc.
- Comprehensive test suite (26 tests covering both desktop and mobile functionality)
- Full integration with verification framework
- Advanced features: FOV indicators, group analysis, summary plots, overlap analysis
- Mobile optimizations: group limiting (max 6), touch-friendly interface, error handling, simplified UI
- Complete migration from main application with zero duplication

### Sprint 5 Completion Summary
**Completed Tasks:**
- ✅ Created weekly analysis modules (`plots/weekly/`)
- ✅ Implemented desktop weekly functions (`plots/weekly/desktop.py`)
- ✅ Implemented mobile weekly functions (`plots/weekly/mobile.py`)
- ✅ Added comprehensive test suite (`tests/test_weekly_plots.py`)
- ✅ Updated main plots module with weekly exports
- ✅ Created mobile-optimized plotting class `MobileWeeklyPlotter`
- ✅ Migrated weekly analysis function from main application file
- ✅ Maintained full backward compatibility

**Deliverables:**
- Desktop weekly functions: `plot_weekly_analysis()`, `create_weekly_comparison_plot()`, `create_weekly_statistics_plot()`, `create_weekly_summary_table_plot()`
- Mobile weekly functions: `MobileWeeklyPlotter`, `create_mobile_weekly_analysis_plot()`, `create_mobile_simple_weekly_plot()`, `create_mobile_weekly_summary_plot()`
- Comprehensive test suite (19 tests covering both desktop and mobile functionality)
- Full integration with verification framework
- Advanced features: 6-panel analysis, statistical plots, correlation analysis, summary tables
- Mobile optimizations: week limiting (max 12), touch-friendly interface, error handling, simplified layouts
- Complete migration from main application with zero duplication

## Notes
- Each sprint is independent and can be stopped after completion
- All changes are verified before moving to the next sprint
- Documentation is updated with each sprint
- Mobile adaptations are implemented alongside desktop functions
- Verification system ensures consistency across platforms 