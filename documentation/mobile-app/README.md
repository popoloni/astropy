# 📱 Mobile App Documentation

**iOS Pythonista compatibility and experimental mobile app development**

> **📱 iOS Pythonista**: Wrapper scripts are fully functional on iOS Pythonista - designed to simplify running astropy.py without typing parameters.
> 
> **🧪 EXPERIMENTAL**: A separate native mobile app implementation is in development but not fully tested yet.

---

## 📋 **Table of Contents**

- [🎯 Overview](#-overview)
- [📱 Wrapper Scripts](#-wrapper-scripts)
- [🔧 Setup Instructions](#-setup-instructions)
- [📖 Usage Examples](#-usage-examples)
- [⚠️ Known Limitations](#️-known-limitations)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 🎯 **Overview**

This documentation covers two distinct mobile implementations:

1. **iOS Pythonista Compatibility** (Fully Functional)
2. **Experimental Native Mobile App** (In Development)

### **✅ iOS Pythonista Compatibility (Fully Functional)**
- All 10 wrapper scripts tested and working on desktop AND iOS Pythonista
- Designed specifically to simplify running astropy.py without typing parameters in iOS
- Complete observation planning and scheduling
- Mosaic analysis and trajectory plotting
- Report generation and data export
- Multiple scheduling strategies

### **🧪 Experimental Native Mobile App (In Development)**
- Separate mobile app implementation (not Pythonista-based)
- Not fully tested yet
- Independent of the wrapper scripts
- May have different features and limitations

---

## 📱 **Wrapper Scripts**

All wrapper scripts are located in the `wrappers/` directory and provide simplified access to core functionality:

### **📊 Analysis & Reporting**
- **`run_report_only.py`** - Generate comprehensive observation reports
- **`run_quarters_report.py`** - Quarterly analysis without plots
- **`run_telescope_analysis.py`** - Telescope analysis and listing (8 telescopes)

### **🎯 Scheduling Strategies**
- **`run_longest_duration.py`** - Maximize single object exposure time
- **`run_max_objects.py`** - Observe maximum number of objects
- **`run_optimal_snr.py`** - Optimize signal-to-noise ratio

### **🖼️ Mosaic & Visualization**
- **`run_mosaic_analysis.py`** - Comprehensive mosaic analysis with plots
- **`run_mosaic_plots.py`** - Mosaic trajectory plotting and visualization
- **`run_quarters.py`** - 4-quarter trajectory plots with scheduling
- **`run_with_plots.py`** - Full observation planner with comprehensive plots

---

## 🔧 **Setup Instructions**

### **Desktop Testing (Verified)**
```bash
# All scripts work correctly on desktop systems
cd astropy/wrappers
python run_report_only.py
python run_max_objects.py
python run_mosaic_analysis.py
```

### **iOS Pythonista Setup (Fully Functional)**

#### **1. Install Pythonista**
- Download Pythonista 3 from the App Store
- Ensure you have the latest version

#### **2. Transfer Files**
```python
# Option 1: Use Pythonista's file transfer feature
# Option 2: Use cloud storage (iCloud, Dropbox, etc.)
# Option 3: Use git clone if available
```

#### **3. Install Dependencies**
```python
# In Pythonista console
import pip
pip.main(['install', 'numpy'])
pip.main(['install', 'matplotlib'])
pip.main(['install', 'pytz'])
```

#### **4. Test Basic Functionality**
```python
# Test import
exec(open('wrappers/run_report_only.py').read())
```

---

## 📖 **Usage Examples**

### **Basic Report Generation**
```python
# Direct execution
exec(open('wrappers/run_report_only.py').read())

# Import and run
import sys
sys.path.insert(0, 'wrappers')
import run_report_only
```

### **Scheduling Strategies**
```python
# Maximum objects strategy
exec(open('wrappers/run_max_objects.py').read())

# Optimal SNR strategy
exec(open('wrappers/run_optimal_snr.py').read())

# Longest duration strategy
exec(open('wrappers/run_longest_duration.py').read())
```

### **Mosaic Analysis**
```python
# Comprehensive mosaic analysis
exec(open('wrappers/run_mosaic_analysis.py').read())

# Mosaic plotting only
exec(open('wrappers/run_mosaic_plots.py').read())
```

### **Advanced Features**
```python
# Quarterly analysis
exec(open('wrappers/run_quarters.py').read())

# Full plotting suite
exec(open('wrappers/run_with_plots.py').read())

# Telescope analysis
exec(open('wrappers/run_telescope_analysis.py').read())
```

---

## ⚠️ **Known Limitations**

### **iOS Pythonista Specific**
- **Library Dependencies**: Some scientific libraries may not be available
- **Plotting Limitations**: matplotlib functionality may be restricted
- **File System Access**: Limited file system access compared to desktop
- **Performance**: Slower execution on mobile devices
- **Memory Constraints**: Large datasets may cause memory issues

### **General Mobile Limitations**
- **Screen Size**: Complex plots may be difficult to view
- **Input Methods**: Command-line arguments not directly supported
- **Background Processing**: Limited background execution capabilities
- **Network Requirements**: Some features may require internet connectivity

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```python
# Error: No module named 'numpy'
# Solution: Install required dependencies
import pip
pip.main(['install', 'numpy', 'matplotlib', 'pytz'])
```

#### **File Path Issues**
```python
# Error: File not found
# Solution: Check file paths and ensure proper directory structure
import os
print(os.getcwd())  # Check current directory
print(os.listdir('.'))  # List files
```

#### **Configuration Errors**
```python
# Error: No module named 'config.settings'
# Solution: Ensure config directory and settings.py are present
# Check that config/settings.py exists in the project structure
```

#### **Plotting Issues**
```python
# Error: matplotlib backend issues
# Solution: Try different backends or disable plotting
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

### **Performance Optimization**
```python
# Reduce memory usage
# Use report-only modes when possible
exec(open('wrappers/run_report_only.py').read())
exec(open('wrappers/run_quarters_report.py').read())

# Avoid complex plotting on mobile devices
# Use desktop for full visualization features
```

### **Debugging Tips**
```python
# Enable verbose output
import sys
sys.argv.append('--verbose')  # If supported by wrapper

# Check system capabilities
import platform
print(f"Platform: {platform.platform()}")
print(f"Python: {platform.python_version()}")

# Test individual components
try:
    import numpy
    print("✅ NumPy available")
except ImportError:
    print("❌ NumPy not available")

try:
    import matplotlib
    print("✅ Matplotlib available")
except ImportError:
    print("❌ Matplotlib not available")
```

---

## 📞 **Support**

### **Getting Help**
- **Desktop Issues**: Use main project documentation
- **Mobile-Specific Issues**: Check this mobile app documentation
- **iOS Pythonista**: Consult Pythonista documentation and forums
- **Bug Reports**: Include device info and iOS version

### **Reporting Mobile Issues**
Please include:
- iOS version and device model
- Pythonista version
- Complete error messages
- Steps to reproduce the issue
- Whether the same script works on desktop

---

## 📱 **Experimental Native Mobile App**

> **🧪 EXPERIMENTAL**: This section describes the separate native mobile app implementation (not Pythonista-based) that is currently in development and not fully tested.

### **📋 App Architecture**

The experimental mobile app (`mobile_app/`) is built using Kivy framework and provides a native mobile interface with the following components:

#### **🏗️ Core Structure:**
```
mobile_app/
├── main.py              # Main application entry point
├── buildozer.spec       # Android build configuration
├── requirements.txt     # Mobile-specific dependencies
├── scope_data.json      # Mobile telescope configuration
├── screens/             # Screen implementations
├── widgets/             # Custom UI widgets
├── utils/               # Mobile utilities
└── assets/              # App icons and resources
```

### **📱 Screen Descriptions & UX**

#### **🏠 Home Screen** (`home_screen.py`)
**Purpose**: Main dashboard and entry point
**Features**:
- **Tonight's Best Targets**: Top 20 objects for current location and date
- **Quick Stats**: Moon phase, twilight times, weather summary
- **Quick Actions**: Direct access to planning, reports, and settings
- **Location Display**: Current observing location with edit option
- **Navigation Hub**: Central access to all app features

**UX Elements**:
- Large, touch-friendly target cards with object thumbnails
- Swipe gestures for target browsing
- Pull-to-refresh for updated calculations
- Quick action buttons with clear icons

#### **🎯 Targets Screen** (`targets_screen.py`)
**Purpose**: Browse and filter celestial objects
**Features**:
- **Object Browser**: Scrollable list of all available targets
- **Advanced Filtering**: Filter by object type, magnitude, visibility
- **Search Functionality**: Search by name, catalog number, or constellation
- **Sorting Options**: Sort by altitude, magnitude, visibility duration
- **Quick Preview**: Tap for basic info, long-press for details

**UX Elements**:
- Search bar with auto-complete suggestions
- Filter chips for quick category selection
- Infinite scroll with lazy loading
- Visual indicators for object visibility status

#### **📊 Target Detail Screen** (`target_detail_screen.py`)
**Purpose**: Comprehensive information for individual objects
**Features**:
- **Object Information**: Coordinates, magnitude, size, type
- **Visibility Analysis**: Rise/set times, optimal viewing windows
- **Observation Planning**: Best exposure settings, recommended filters
- **Trajectory Plot**: Altitude vs. time visualization
- **Mosaic Compatibility**: Grouping suggestions for mosaic imaging

**UX Elements**:
- Tabbed interface for different information categories
- Interactive charts with zoom and pan capabilities
- Action buttons for adding to session or mosaic plans
- Share functionality for object details

#### **🖼️ Mosaic Screen** (`mosaic_screen.py`)
**Purpose**: Plan and visualize mosaic imaging sessions
**Features**:
- **Mosaic Groups**: Pre-defined object groupings for wide-field imaging
- **Custom Mosaics**: Create custom mosaic plans
- **Trajectory Visualization**: Multi-object trajectory plotting
- **Timing Optimization**: Optimal scheduling for mosaic sequences
- **Equipment Matching**: Telescope-specific mosaic recommendations

**UX Elements**:
- Drag-and-drop interface for mosaic planning
- Multi-touch gestures for plot manipulation
- Color-coded trajectories for different objects
- Timeline scrubber for time-based visualization

#### **📅 Session Planner Screen** (`session_planner_screen.py`)
**Purpose**: Complete observation session planning
**Features**:
- **Session Timeline**: Hour-by-hour observation schedule
- **Strategy Selection**: Choose optimization strategy (max objects, SNR, etc.)
- **Equipment Configuration**: Select telescope and camera settings
- **Weather Integration**: Basic weather considerations
- **Export Options**: Share session plans via email or cloud storage

**UX Elements**:
- Timeline view with draggable session blocks
- Strategy picker with visual previews
- Equipment carousel for telescope selection
- One-tap session export and sharing

#### **⚙️ Settings Screen** (`settings_screen.py`)
**Purpose**: App configuration and preferences
**Features**:
- **Location Management**: Set observing location with GPS or manual entry
- **Telescope Profiles**: Select and configure telescope equipment
- **Display Preferences**: Dark mode, units, chart styles
- **Calculation Settings**: Precision levels, atmospheric models
- **Data Management**: Cache management, offline capabilities

**UX Elements**:
- Grouped settings with clear section headers
- Toggle switches for boolean preferences
- Slider controls for numeric values
- Location picker with map integration

#### **📋 Reports Screen** (`reports_screen.py`)
**Purpose**: Generate and view observation reports
**Features**:
- **Report Generation**: Create detailed observation reports
- **Multiple Formats**: Text, PDF, and image export options
- **Historical Data**: View past session reports
- **Sharing Options**: Email, cloud storage, social media
- **Print Support**: Direct printing to compatible printers

**UX Elements**:
- Report preview with live updates
- Format selection with visual previews
- Share sheet integration for easy distribution
- Print dialog with layout options

#### **🔭 Scope Selection Screen** (`scope_selection_screen.py`)
**Purpose**: Choose and configure telescope equipment
**Features**:
- **Telescope Database**: Browse 8+ pre-configured telescope profiles
- **Equipment Comparison**: Side-by-side telescope comparisons
- **Custom Configurations**: Create custom telescope setups
- **FOV Visualization**: Field of view previews for different targets
- **Compatibility Checking**: Verify telescope-target compatibility

**UX Elements**:
- Card-based telescope browser with images
- Comparison mode with swipe gestures
- Configuration wizard for custom setups
- Visual FOV overlays on sky charts

### **🎨 Design Principles**

#### **Night Vision Friendly**
- **Dark Theme**: Default dark interface to preserve night vision
- **Red Light Mode**: Optional red-tinted interface for extreme dark adaptation
- **Brightness Control**: Adjustable screen brightness within the app

#### **Touch-Optimized**
- **Large Touch Targets**: Minimum 44pt touch targets for easy interaction
- **Gesture Support**: Swipe, pinch, and long-press gestures throughout
- **Haptic Feedback**: Tactile feedback for important interactions

#### **Responsive Design**
- **Adaptive Layouts**: Optimized for phones and tablets
- **Orientation Support**: Both portrait and landscape modes
- **Dynamic Text**: Supports system text size preferences

### **⚙️ Technical Implementation**

#### **Framework & Tools**
- **Kivy**: Cross-platform Python framework for mobile development
- **Buildozer**: Android packaging and build system
- **JsonStore**: Local data persistence for settings and cache
- **Clock**: Kivy's scheduling system for background tasks

#### **Performance Optimizations**
- **Lazy Loading**: Load data only when needed
- **Background Processing**: Heavy calculations on background threads
- **Intelligent Caching**: Cache frequently accessed calculations
- **Memory Management**: Efficient memory usage for mobile constraints

#### **Data Integration**
- **Shared Modules**: Uses existing astropy calculation modules
- **Configuration Sync**: Synchronized with main system configuration
- **Real-time Updates**: Live updates as parameters change

### **🚧 Current Limitations**

#### **Development Status**
- **Limited Testing**: Not extensively tested on real devices
- **iOS Support**: Currently Android-focused, iOS support planned
- **Feature Completeness**: Some advanced features not yet implemented
- **Performance**: Not optimized for all device types

#### **Known Issues**
- **Plotting Performance**: Complex plots may be slow on older devices
- **Memory Usage**: Large catalogs may cause memory issues
- **Network Dependency**: Some features require internet connectivity
- **Battery Usage**: Intensive calculations may drain battery quickly

### **🔮 Roadmap**

#### **Short Term (Next Release)**
- **iOS Build Support**: Extend to iOS platform using kivy-ios
- **Performance Optimization**: Improve plotting and calculation speed
- **Bug Fixes**: Address known issues and stability problems
- **User Testing**: Conduct extensive testing on various devices

#### **Medium Term**
- **Enhanced UI**: Improved animations and visual polish
- **Offline Mode**: Full offline capability with local catalogs
- **Advanced Features**: Real-time tracking, notifications, automation
- **Integration**: Better integration with external tools and services

#### **Long Term**
- **Native Rewrite**: Consider native iOS/Android implementations
- **Cloud Sync**: Synchronize data across devices
- **Community Features**: Sharing, collaboration, and social features
- **Professional Tools**: Advanced features for serious astrophotographers

---

## 🔄 **Future Development**

### **Planned Improvements**
- Enhanced iOS Pythonista compatibility testing
- Simplified mobile-specific interfaces
- Reduced dependency requirements
- Mobile-optimized plotting options
- Touch-friendly user interfaces
- Complete experimental mobile app development

### **Contributing**
Mobile app development contributions are welcome:
- Test wrapper scripts on iOS devices
- Report compatibility issues
- Suggest mobile-specific improvements
- Help with iOS Pythonista optimization
- Contribute to experimental mobile app development
- Test mobile app on different devices and platforms

---

**🌟 Happy Mobile Observing! 📱🔭**

*Wrapper scripts are fully functional - experimental mobile app is in development*