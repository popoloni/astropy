# Advanced Filtering System for AstroScope Planner

## Overview

The Advanced Filtering System provides sophisticated filtering capabilities for astronomical targets, allowing users to find the perfect objects for their observing session based on multiple criteria including magnitude, size, object type, imaging difficulty, and technical requirements.

## Features

### Basic Filters
- **Magnitude Range**: Filter targets by brightness (0-20 magnitude scale)
- **Object Size Range**: Filter by angular size (0-180 arcminutes)
- **Object Types**: Select specific types (galaxy, nebula, cluster, etc.)
- **Imaging Difficulty**: Choose difficulty level (beginner to expert)
- **Moon Avoidance**: Automatically exclude targets affected by moonlight

### Advanced Filters
- **Altitude Range**: Filter by maximum altitude (0-90 degrees)
- **Visibility Hours**: Minimum time target is observable
- **Constellation Filter**: Select targets from specific constellations
- **Season Preference**: Filter by optimal observing season
- **Focal Length Range**: Match targets to your telescope setup
- **Pixel Scale Requirements**: Filter by imaging requirements
- **Maximum Exposure Time**: Limit based on tracking capabilities

### Custom Criteria
- **Flexible Operators**: Equals, greater than, less than, between, in, not in
- **Any Field**: Filter on any target property
- **Multiple Criteria**: Combine multiple custom filters
- **AND/OR Logic**: Choose how criteria are combined

### Filter Presets
- **Built-in Presets**: Beginner, Deep Sky, Wide Field
- **Custom Presets**: Save your own filter combinations
- **Quick Access**: Load presets with one tap

## Usage

### Mobile App Interface

1. **Access Advanced Filters**
   - Open the Targets screen
   - Tap the "Advanced" button in the filter controls
   - The Advanced Filter popup will open with three tabs

2. **Basic Filters Tab**
   - Use sliders to set magnitude and size ranges
   - Check/uncheck object types
   - Select imaging difficulty level
   - Toggle moon avoidance

3. **Advanced Filters Tab**
   - Set altitude and visibility requirements
   - Choose season preference
   - Configure technical parameters

4. **Presets Tab**
   - Load built-in or custom presets
   - Save current settings as new preset
   - View preset descriptions

5. **Apply Filters**
   - Tap "Apply Filters" to update target list
   - Use "Reset" to return to defaults
   - Tap "Close" to exit without applying

### Programmatic Usage

```python
from utils.advanced_filter import AdvancedFilter, FilterOperator

# Create filter instance
filter_obj = AdvancedFilter()

# Configure basic filters
filter_obj.magnitude_range = (5.0, 12.0)
filter_obj.object_types = ['galaxy', 'nebula']
filter_obj.imaging_difficulty = 'intermediate'

# Configure advanced filters
filter_obj.altitude_range = (30.0, 90.0)
filter_obj.visibility_hours_min = 3.0
filter_obj.moon_avoidance = True

# Add custom criteria
filter_obj.add_custom_criteria('constellation', FilterOperator.EQUALS, 'Orion')

# Apply filters to target list
filtered_targets = filter_obj.apply_filters(target_list)
```

## Filter Criteria Details

### Magnitude Range
- **Range**: 0.0 to 20.0 (astronomical magnitude scale)
- **Lower values**: Brighter objects
- **Higher values**: Fainter objects
- **Typical ranges**:
  - Naked eye: 0-6
  - Binoculars: 6-9
  - Small telescope: 9-12
  - Large telescope: 12+

### Object Size Range
- **Range**: 0 to 180 arcminutes
- **Considerations**:
  - Small objects (<5'): Require high magnification
  - Medium objects (5-30'): Good for most telescopes
  - Large objects (>30'): Need wide field of view

### Imaging Difficulty Assessment
The system calculates difficulty scores (1-10) based on:
- **Magnitude**: Fainter objects are harder
- **Size**: Smaller objects are more challenging
- **Object Type**: Some types inherently more difficult
- **Surface Brightness**: Lower values harder to image

**Difficulty Levels**:
- **Beginner (1-3)**: Bright, easy targets
- **Intermediate (2.5-5)**: Moderate challenge
- **Advanced (4-7)**: Requires experience
- **Expert (6-10)**: Very challenging

### Moon Avoidance
- **Separation**: Targets within 30° of moon are flagged
- **Impact**: Moon affects faint object visibility
- **Automatic**: System calculates moon position

### Technical Filters
- **Focal Length**: Match targets to telescope capabilities
- **Pixel Scale**: Ensure proper sampling for imaging
- **Exposure Time**: Consider mount tracking limits

## Filter Presets

### Built-in Presets

#### Beginner Friendly
- Magnitude: 0-8
- Size: 10-180 arcmin
- Types: Clusters, bright nebulae
- Difficulty: Beginner
- Altitude: 45-90°
- Visibility: 3+ hours

#### Deep Sky Objects
- Magnitude: 8-15
- Size: 2-60 arcmin
- Types: Galaxies, nebulae, planetary nebulae
- Difficulty: Advanced
- Altitude: 30-90°
- Visibility: 2+ hours
- Exposure: Up to 15 minutes

#### Wide Field Targets
- Magnitude: 0-10
- Size: 30-180 arcmin
- Types: Nebulae, clusters
- Difficulty: Intermediate
- Focal Length: 200-800mm
- Pixel Scale: 2-5 arcsec/pixel

### Creating Custom Presets

1. Configure filters to your preferences
2. Go to Presets tab
3. Enter a name for your preset
4. Tap "Save"
5. Preset will be available for future use

## Advanced Features

### Custom Filter Criteria

Add filters for any target property:

```python
# Filter by constellation
filter_obj.add_custom_criteria('constellation', FilterOperator.EQUALS, 'Orion')

# Filter by RA range
filter_obj.add_custom_criteria('ra', FilterOperator.BETWEEN, (0, 6))

# Filter by declination
filter_obj.add_custom_criteria('dec', FilterOperator.GREATER_THAN, 30)

# Filter by multiple constellations
filter_obj.add_custom_criteria('constellation', FilterOperator.IN, ['Orion', 'Taurus'])
```

### Filter Logic

Choose how multiple criteria are combined:
- **AND Logic**: All criteria must be met (default)
- **OR Logic**: Any criteria can be met

### Filter Performance

The system efficiently processes filters in order:
1. Advanced filters (magnitude, size, type)
2. Technical filters (altitude, visibility)
3. Custom criteria
4. Final sorting

## Integration with App State

The filtering system integrates with the app's state management:

```python
# Set filter in app state
app_state.set_advanced_filter(filter_obj)

# Apply filters to current targets
filtered_targets = app_state.get_filtered_targets()

# Save/load presets
app_state.save_filter_preset('my_preset')
app_state.load_filter_preset('my_preset')
```

## Troubleshooting

### No Targets Found
- Check if filters are too restrictive
- Try resetting to defaults
- Verify target data is loaded

### Slow Performance
- Reduce number of custom criteria
- Use simpler filter combinations
- Check target list size

### Filter Not Working
- Ensure filter is enabled
- Check target data has required fields
- Verify filter values are reasonable

## Best Practices

### For Beginners
1. Start with built-in presets
2. Use "Beginner Friendly" preset initially
3. Gradually add more criteria as you learn

### For Advanced Users
1. Create custom presets for different equipment
2. Use technical filters for imaging sessions
3. Combine multiple criteria for specific goals

### For Imaging
1. Consider moon phase and position
2. Match filters to your equipment capabilities
3. Plan for required exposure times

### For Visual Observing
1. Focus on altitude and visibility
2. Consider light pollution levels
3. Match object size to eyepiece field of view

## API Reference

### AdvancedFilter Class

#### Properties
- `magnitude_range`: Tuple of (min, max) magnitude
- `size_range`: Tuple of (min, max) size in arcminutes
- `object_types`: List of object type strings
- `imaging_difficulty`: String difficulty level
- `moon_avoidance`: Boolean for moon interference
- `altitude_range`: Tuple of (min, max) altitude in degrees
- `visibility_hours_min`: Minimum visibility hours
- `custom_criteria`: List of FilterCriteria objects

#### Methods
- `apply_filters(targets)`: Apply all filters to target list
- `add_custom_criteria(field, operator, value)`: Add custom filter
- `remove_custom_criteria(field)`: Remove custom filter
- `save_preset(name)`: Save current settings as preset
- `load_preset(preset)`: Load settings from preset
- `reset_to_defaults()`: Reset all filters to defaults

### FilterPresetManager Class

#### Methods
- `get_preset(name)`: Get preset by name
- `save_preset(name, filter_obj)`: Save new preset
- `delete_preset(name)`: Delete existing preset
- `list_presets()`: Get list of available presets

## Future Enhancements

### Planned Features
- **Weather Integration**: Filter based on weather conditions
- **Equipment Matching**: Automatic filter suggestions based on equipment
- **Observing History**: Filter based on previously observed targets
- **Social Features**: Share filter presets with other users
- **AI Recommendations**: Machine learning-based target suggestions

### Performance Improvements
- **Caching**: Cache filter results for faster updates
- **Indexing**: Index target properties for faster filtering
- **Lazy Loading**: Load target details on demand

### User Experience
- **Visual Feedback**: Show filter impact in real-time
- **Guided Setup**: Wizard for creating custom filters
- **Filter Analytics**: Statistics on filter usage and effectiveness

## Conclusion

The Advanced Filtering System provides powerful and flexible target selection capabilities for the AstroScope Planner mobile app. Whether you're a beginner looking for easy targets or an advanced imager seeking specific technical requirements, the filtering system helps you find the perfect objects for your observing session.

The combination of basic filters, advanced criteria, custom options, and preset management makes it easy to quickly find targets that match your equipment, experience level, and observing conditions.