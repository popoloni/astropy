# Constellation Visualizer

A Python script to visualize astronomical constellations with stars, constellation lines, deep sky objects, and nebula boundaries.

## Features

- **Constellation Stars**: Displayed as white star markers, with size proportional to brightness (magnitude)
- **Constellation Lines**: Light blue lines connecting stars to form traditional constellation patterns
- **Bright Stars**: Notable bright stars (like Deneb, Albireo) displayed as large gold star markers
- **Deep Sky Objects**: Color-coded circles with labels showing photographable objects
  - **Blue**: Galaxies (spiral, lenticular, elliptical, groups)
  - **Purple**: Nebulae (emission, planetary, reflection, dark, remnant)
  - **Orange**: Clusters (open, globular)
  - **Dark Orange**: Other objects (solar system, miscellaneous)
- **Object Boundaries**: Dashed ellipses showing actual sizes/shapes of galaxies, clusters, and large objects
- **Nebula Boundaries**: Red outlines showing the extent of extended objects like nebulae
- **Smart Boundary Display**: Objects with nebula paths show red outlines; objects with ellipses show colored boundaries; others show dots
- **Color Toggle**: Optional `--no-colors-for-dso` flag to use classic red-only DSO display
- **Ellipse Toggle**: Optional `--no-ellipses` flag to hide object boundaries (dots only)
- **Smart Object Classification**: Automatically distinguishes between stars and actual deep sky objects
- **Integrated Legend**: Clear identification of all visual elements with object counts included

## Files

- `constellation_visualizer.py`: Main visualization script
- `constellation_demo.py`: Demo script with examples and statistics
- `README_constellation_visualizer.md`: This documentation file

## Data Sources

The script uses three JSON catalog files from the `../catalogs/` directory:

1. **constellations.json**: Star positions, magnitudes, and constellation line patterns
2. **objects.json**: Deep sky objects (galaxies, nebulae, clusters) with coordinates and metadata
3. **nebula-paths.json**: Coordinate boundaries for extended objects like nebulae
4. **simbad-objects.json**: SIMBAD catalog data with elliptical boundaries for galaxies, clusters, and large objects

## Requirements

```bash
pip install matplotlib numpy
```

## Usage

### Basic Usage

```bash
# Show help and available constellations
python constellation_visualizer.py

# Visualize a specific constellation
python constellation_visualizer.py <constellation_id>
```

### Examples

```bash
# Popular constellations (with color-coded DSO types)
python constellation_visualizer.py Ori    # Orion (rich in nebulae)
python constellation_visualizer.py UMa    # Ursa Major (Big Dipper)
python constellation_visualizer.py Cas    # Cassiopeia
python constellation_visualizer.py Cyg    # Cygnus (The Swan)
python constellation_visualizer.py And    # Andromeda (contains M31 galaxy)
python constellation_visualizer.py Sco    # Scorpius (The Scorpion)

# Classic mode (red DSOs only)
python constellation_visualizer.py Ori --no-colors-for-dso
python constellation_visualizer.py Cyg --no-colors-for-dso

# No ellipses mode (dots only)
python constellation_visualizer.py And --no-ellipses
python constellation_visualizer.py Vir --no-ellipses
```

### Demo Script

```bash
# Show demo with popular constellations
python constellation_demo.py

# Show object type statistics
python constellation_demo.py stats

# Interactive mode
python constellation_demo.py interactive
```

## Available Constellations

The script supports all 88 modern constellations:

```
And  Ant  Aps  Aql  Aqr  Ara  Ari  Aur  Boo  CMa  
CMi  CVn  Cae  Cam  Cap  Car  Cas  Cen  Cep  Cet  
Cha  Cir  Cnc  Col  Com  CrA  CrB  Crt  Cru  Crv  
Cyg  Del  Dor  Dra  Equ  Eri  For  Gem  Gru  Her  
Hor  Hya  Hyi  Ind  LMi  Lac  Leo  Lep  Lib  Lup  
Lyn  Lyr  Men  Mic  Mon  Mus  Nor  Oct  Oph  Ori  
Pav  Peg  Per  Phe  Pic  PsA  Psc  Pup  Pyx  Ret  
Scl  Sco  Sct  Ser  Sex  Sge  Sgr  Tau  Tel  TrA  
Tri  Tuc  UMa  UMi  Vel  Vir  Vol  Vul
```

## Object Statistics

The catalogs contain:
- **421 total deep sky objects** across 74 constellations
- **Object types include**:
  - Spiral Galaxies (95)
  - Globular Clusters (73)
  - Open Clusters (72)
  - Emission Nebulae (35)
  - Planetary Nebulae (25)
  - Multiple Stars (22)
  - And many more...

## Programmatic Usage

```python
from constellation_visualizer import ConstellationVisualizer

# Create visualizer instance
visualizer = ConstellationVisualizer()

# Get constellation data
constellation = visualizer.find_constellation("Ori")
objects = visualizer.get_constellation_objects("Ori")

# Plot constellation
visualizer.plot_constellation("Ori")

# List all available constellations
available = visualizer.list_available_constellations()
print(f"Available: {available}")
```

## Output

The script creates a matplotlib window showing:
- Black background (like the night sky)
- White stars with size indicating brightness (constellation pattern stars)
- Light blue constellation pattern lines
- Gold star markers for bright notable stars (like Deneb, Albireo)
- Smart object display: dots for small objects, dashed ellipses for large objects with known boundaries
- Color-coded by object type (blue=galaxies, purple=nebulae, orange=clusters)
- Red outlined regions for nebula boundaries
- Optional classic mode with red-only DSO display
- Optional ellipse-free mode for minimal display
- Integrated legend with symbols, names, and counts
- Proper astronomical coordinate system (RA inverted)

## Constellation Recommendations

**Best for beginners:**
- `Ori` (Orion): Rich in bright stars and nebulae
- `UMa` (Ursa Major): Familiar Big Dipper pattern
- `Cas` (Cassiopeia): Distinctive W shape

**Rich in deep sky objects:**
- `Sgr` (Sagittarius): 28 objects including galactic center
- `Cyg` (Cygnus): 19 objects including many nebulae
- `Vir` (Virgo): 18 objects including galaxy cluster

**Interesting nebula boundaries:**
- `Ori` (Orion): Multiple nebula regions
- `Cas` (Cassiopeia): Heart and Soul nebulae
- `Cyg` (Cygnus): North America nebula region

## Notes

- Coordinates are in degrees (Right Ascension and Declination)
- Right Ascension axis is inverted following astronomical convention
- Star sizes are based on visual magnitude (brighter = larger)
- Object names are displayed when available in the catalog
- Some constellations may have objects but no nebula boundaries, and vice versa 