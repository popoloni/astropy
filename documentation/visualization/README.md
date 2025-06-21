# Visualization Documentation

This directory contains comprehensive documentation for the constellation visualization tools in the astropy-app project.

## 📚 Documentation Files

### **Main Guides**
- **[CONSTELLATION_VISUALIZER_GUIDE.md](CONSTELLATION_VISUALIZER_GUIDE.md)** - Complete user guide for the SVG constellation visualizer
- **[LEGACY_CONSTELLATION_DOCS.md](LEGACY_CONSTELLATION_DOCS.md)** - Previous matplotlib-based documentation (historical reference)

### **Technical Documentation**
- **[VISUALIZATION_IMPROVEMENTS.md](VISUALIZATION_IMPROVEMENTS.md)** - Detailed improvements and enhancements
- **[ULTRA_HIGH_DPI_SUMMARY.md](ULTRA_HIGH_DPI_SUMMARY.md)** - High-DPI display optimizations
- **[ULTRA_THIN_FIXES.md](ULTRA_THIN_FIXES.md)** - Performance and rendering fixes
- **[MICRO_SIZING_FINAL.md](MICRO_SIZING_FINAL.md)** - Size optimization details

## 🌟 Quick Start

The main constellation visualizer tool is located at:
```
utilities/show_all_constellations.py
```

### **Basic Usage**
```bash
# Full sky view
python utilities/show_all_constellations.py

# Individual constellation (e.g., Orion)
python utilities/show_all_constellations.py Ori

# List all available constellations
python utilities/show_all_constellations.py --all
```

### **Key Features**
- ✅ **Vector SVG output** with infinite zoom capability
- ✅ **Interactive browser viewing** on macOS
- ✅ **Native iOS support** via Pythonista
- ✅ **Proper astronomical orientation** (fixed coordinate system)
- ✅ **Color-coded deep sky objects** by type
- ✅ **Professional presentation** quality

## 🗂️ Related Files

### **Source Code**
- `utilities/show_all_constellations.py` - Main SVG visualizer
- `utilities/show_all.py` - Legacy matplotlib version
- `utilities/constellation_visualizer.py` - Core functions

### **Output Directory**
- `images/` - SVG files are saved here
  - `celestial_grid.svg` - Full sky constellation map
  - `constellation_*.svg` - Individual constellation views

### **Data Sources**
- `catalogs/constellations.json` - Star positions and patterns
- `catalogs/objects.json` - Deep sky objects
- `catalogs/nebula-paths.json` - Nebula boundaries
- `catalogs/simbad-objects.json` - Object boundary data

## 🎯 Platform Support

| Platform | Viewing Method | Features |
|----------|----------------|----------|
| **macOS** | Auto-browser launch | Mouse zoom/pan, zoom buttons |
| **iOS** | Pythonista WebView | Touch zoom/pan, full-screen |
| **Windows** | Browser (manual) | Mouse controls |
| **Linux** | Browser (auto/manual) | Mouse controls |

## 📊 Available Data

- **88 constellations** with traditional star patterns
- **695 constellation stars** with accurate magnitudes  
- **374 deep sky objects** (galaxies, nebulae, clusters)
- **37 named bright stars** (Betelgeuse, Rigel, Vega, etc.)
- **291 object boundaries** with precise shapes
- **124 nebula regions** with coordinate paths

## 🔄 Recent Major Updates

### **v2.0 - Vector SVG Edition**
- Fixed coordinate mirroring for proper astronomical orientation
- Added macOS browser support with interactive controls
- Organized SVG output into `images/` directory
- Enhanced cross-platform compatibility
- Improved documentation and user guides

### **Performance & Quality**
- Faster SVG generation (2-3x speed improvement)
- Reduced file sizes while maintaining quality
- Better error handling and user feedback
- Professional-grade vector output

## 🆘 Support

For issues or questions:
1. Check the [troubleshooting section](CONSTELLATION_VISUALIZER_GUIDE.md#-troubleshooting) in the main guide
2. Review the technical documentation in this directory
3. Verify all required catalog files are present in `catalogs/`

---

*This documentation is actively maintained and reflects the current state of the constellation visualization tools.* 