# Trajectory Analysis Quick Reference Guide

## Quick Start

```bash
# Basic yearly analysis
python seasonplanner.py

# Analyze spring quarter
python seasonplanner.py --quarter Q2

# Analyze current month only
python seasonplanner.py --month $(date +%m)

# Generate analysis without plots (faster)
python seasonplanner.py --no-plots
```

## Common Use Cases

### 1. **Planning Annual Astrophotography Schedule**
```bash
# Full year analysis for strategic planning
python seasonplanner.py --year
```
**Output**: Complete yearly overview with best weeks identified, seasonal trends, and object-specific optimal periods.

### 2. **Seasonal Planning**
```bash
# Winter imaging opportunities (Q1)
python seasonplanner.py --quarter Q1

# Summer imaging opportunities (Q3) 
python seasonplanner.py --quarter Q3
```
**Use for**: Identifying seasonal targets and planning equipment requirements.

### 3. **Monthly Session Planning**
```bash
# Detailed planning for specific month
python seasonplanner.py --month 10  # October
```
**Use for**: Weekly session planning with specific target recommendations.

### 4. **Quick Assessment Without Plots**
```bash
# Fast analysis for regular updates
python seasonplanner.py --month 3 --no-plots
```
**Use for**: Regular monitoring without generating time-intensive visualizations.

## Key Output Sections

### 1. Weekly Analysis Summary
- **Best Week Identification**: Highest scoring week with optimal conditions
- **Weekly Scores**: Comparative scores across all analyzed weeks
- **Configuration Compliance**: Objects meeting visibility requirements
- **Moon Conditions**: Illumination percentages and interference levels

### 2. Object Optimization Analysis
- **Best Observation Times**: Optimal weeks for each object
- **Moon-Free Opportunities**: Periods with minimal lunar interference
- **Mosaic Requirements**: Objects needing special imaging techniques
- **Monthly Recommendations**: Seasonal target suggestions

### 3. Visual Analysis (when plots enabled)
- **Observable Objects Trend**: Seasonal availability patterns
- **Moon Phase Calendar**: Illumination cycles throughout period
- **Mosaic Opportunities**: Distribution of complex imaging targets
- **Weekly Scoring**: Comparative analysis with best periods highlighted

## Interpreting Results

### Weekly Scores
- **>200**: Excellent conditions with multiple moon-free targets and mosaic opportunities
- **100-200**: Good conditions with several viable targets
- **50-100**: Moderate conditions, limited by moon or target availability
- **<50**: Poor conditions, heavily moon-affected or few targets

### Object Categories
- **Excellent Opportunities**: ≥4 moon-free weeks per analyzed period
- **Limited Opportunities**: <4 moon-free weeks, requires careful timing
- **Mosaic Candidates**: Objects requiring or benefiting from multi-panel imaging

### Moon Interference Levels
- **Moon-Free (🌑)**: No significant interference, optimal for deep-sky imaging
- **Moon-Affected (🌕)**: Some interference, consider brightness and filters
- **Full Moon Periods**: Generally avoided for faint object imaging

## Configuration Tips

### Before First Use
1. **Verify Telescope Settings**: Check `config.json` for accurate FOV specifications
2. **Location Accuracy**: Ensure coordinates and timezone are correct
3. **Bortle Index**: Set appropriate light pollution level (1-9 scale)
4. **Visibility Constraints**: Adjust altitude/azimuth limits for your setup

### Optimizing for Your Setup
```json
{
  "imaging": {
    "scope": {
      "fov_width": 2.4,      // Your telescope's single-frame FOV width
      "fov_height": 1.8,     // Your telescope's single-frame FOV height  
      "mosaic_fov_width": 4.7,   // Effective mosaic area width
      "mosaic_fov_height": 3.5   // Effective mosaic area height
    }
  }
}
```

## Common Workflows

### Weekly Planning Workflow
1. Run monthly analysis for current month
2. Identify highest-scoring week
3. Review top 5 recommended targets for that week
4. Cross-reference with weather forecasts
5. Plan imaging sessions around moon-free periods

### Seasonal Planning Workflow
1. Run quarterly analysis for upcoming season
2. Identify objects with excellent opportunities (≥4 weeks)
3. Note objects with limited windows requiring priority
4. Plan mosaic projects during optimal periods
5. Schedule equipment setup and calibration

### Yearly Strategy Workflow
1. Run full yearly analysis
2. Map out seasonal target priorities
3. Identify best months for specific object types
4. Plan major mosaic projects during optimal periods
5. Schedule equipment maintenance during poor weather months

## Troubleshooting

### Common Issues
- **No Objects Found**: Check CSV catalog file or main module configuration
- **Configuration Errors**: Verify `config.json` format and telescope settings
- **Date/Time Issues**: Ensure system timezone matches observing location
- **Plot Generation Fails**: Install required matplotlib dependencies or use `--no-plots`

### Performance Optimization
- Use `--no-plots` for faster analysis when only text output needed
- Focus on specific quarters/months rather than full year for detailed planning
- Regular monthly updates rather than continuous yearly re-analysis

## Integration with Other Tools

### With Weather Services
1. Run trajectory analysis to identify optimal astronomical windows
2. Cross-reference highest-scoring weeks with weather forecasts
3. Adjust session timing based on combined astronomical and meteorological data

### With Equipment Planning
1. Use mosaic analysis to plan mounting and tracking requirements
2. Consider exposure time requirements for filter and camera selection
3. Plan power and storage needs based on session duration estimates

### With Target Selection
1. Prioritize objects with excellent opportunities (≥4 weeks)
2. Group mosaic targets for efficient imaging sessions
3. Balance challenging targets with reliable backup options

## Quick Reference Commands

```bash
# Current conditions
python seasonplanner.py --month $(date +%m)

# Next quarter planning  
python seasonplanner.py --quarter Q$(( ($(date +%m)-1)/3 + 1 ))

# Fast update without plots
python seasonplanner.py --month $(date +%m) --no-plots

# Specific season analysis
python seasonplanner.py --quarter Q1  # Winter
python seasonplanner.py --quarter Q2  # Spring  
python seasonplanner.py --quarter Q3  # Summer
python seasonplanner.py --quarter Q4  # Fall
``` 