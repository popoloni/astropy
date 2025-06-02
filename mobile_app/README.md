# AstroScope Planner Mobile App

A Kivy-based mobile application for astrophotography planning that integrates the powerful astropy calculation engine.

## Features

- **Tonight's Targets**: View optimized list of observable targets for your location
- **Target Details**: Detailed information including visibility windows, imaging recommendations, and technical data
- **Mosaic Planning**: Plan complex mosaic imaging projects with automatic panel calculation
- **Multiple Strategies**: Choose from 6 different scheduling strategies
- **Location Management**: GPS support and saved location profiles
- **Cross-Platform**: Runs on Android, iOS, and desktop platforms

## Installation

### Development Setup

1. Install Python 3.8+ and pip
2. Install Kivy and dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

### Building for Android

1. Install Buildozer:
   ```bash
   pip install buildozer
   ```
2. Initialize and build:
   ```bash
   buildozer android debug
   ```

### Building for iOS

1. Install kivy-ios:
   ```bash
   pip install kivy-ios
   ```
2. Build dependencies:
   ```bash
   toolchain build python3 kivy
   ```
3. Create Xcode project:
   ```bash
   toolchain create AstroScope .
   ```

## Architecture

The app is built with a modular architecture:

- **main.py**: Main application entry point
- **screens/**: Individual screen implementations (8 screens total)
- **utils/**: Utility modules for state management and core functionality
- **widgets/**: Custom UI components and plotting widgets
- **assets/**: Images, icons, and resources

### **📱 Screen Architecture & User Experience**

The mobile app features 8 specialized screens designed for optimal touch interaction and astrophotography workflow:

#### **🏠 Home Screen** (`home_screen.py`)
**Purpose**: Main dashboard providing tonight's overview and quick actions
- **UX Flow**: Entry point → Quick overview → Navigate to specific features
- **Key Features**:
  - Tonight's best targets summary with visibility windows
  - Moon phase display with illumination percentage
  - Astronomical twilight times (civil, nautical, astronomical)
  - Weather-aware recommendations
  - Quick action buttons for common tasks
- **Touch Interactions**: 
  - Tap target cards to view details
  - Swipe for additional target recommendations
  - Pull-to-refresh for updated calculations
- **Visual Design**: Dark theme optimized for night use, large touch targets

#### **🎯 Targets Screen** (`targets_screen.py`)
**Purpose**: Browse and filter available celestial objects
- **UX Flow**: Browse catalog → Apply filters → Select targets → Add to session
- **Key Features**:
  - Comprehensive object catalog with real-time visibility
  - Advanced filtering by object type, magnitude, size, constellation
  - Sort by visibility, altitude, transit time, or imaging priority
  - Search functionality with autocomplete
  - Batch selection for session planning
- **Touch Interactions**:
  - Swipe left/right to navigate object categories
  - Long-press for multi-select mode
  - Pinch-to-zoom on object thumbnails
  - Filter drawer with touch-friendly controls
- **Visual Design**: Grid/list view toggle, visual magnitude indicators, altitude graphs

#### **📋 Target Detail Screen** (`target_detail_screen.py`)
**Purpose**: Comprehensive information for individual celestial objects
- **UX Flow**: Select target → View details → Plan imaging → Add to session
- **Key Features**:
  - Complete object information (coordinates, magnitude, size, type)
  - Real-time visibility chart with altitude/azimuth tracking
  - Imaging recommendations (exposure time, filter suggestions)
  - Best imaging windows for tonight and upcoming nights
  - Historical observation data and notes
- **Touch Interactions**:
  - Swipe between detail tabs (Info, Visibility, Imaging, Notes)
  - Pinch-to-zoom on star charts and images
  - Tap-and-hold for coordinate copying
  - Gesture-based chart navigation
- **Visual Design**: Full-screen charts, tabbed interface, contextual action buttons

#### **🧩 Mosaic Screen** (`mosaic_screen.py`)
**Purpose**: Plan complex mosaic imaging projects
- **UX Flow**: Select large object → Configure mosaic → Preview layout → Generate plan
- **Key Features**:
  - Automatic mosaic panel calculation based on telescope FOV
  - Visual mosaic preview with panel overlap indicators
  - Exposure time optimization per panel
  - Sequence planning with optimal panel order
  - Export capabilities for telescope control software
- **Touch Interactions**:
  - Drag to adjust mosaic center point
  - Pinch-to-zoom for detailed panel view
  - Tap panels to view individual exposure settings
  - Swipe to navigate between mosaic configurations
- **Visual Design**: Interactive mosaic grid, color-coded panels, progress indicators

#### **📅 Session Planner Screen** (`session_planner_screen.py`)
**Purpose**: Complete observation session planning and optimization
- **UX Flow**: Set session parameters → Add targets → Optimize schedule → Export plan
- **Key Features**:
  - Session duration and timing configuration
  - Target priority and time allocation
  - Automatic schedule optimization using multiple strategies
  - Real-time session timeline with altitude curves
  - Equipment change notifications and setup reminders
- **Touch Interactions**:
  - Drag-and-drop target reordering
  - Swipe to remove targets from session
  - Tap timeline for detailed timing information
  - Long-press for target-specific options
- **Visual Design**: Timeline view, Gantt-style scheduling, priority indicators

#### **🔭 Scope Selection Screen** (`scope_selection_screen.py`)
**Purpose**: Choose and configure telescope equipment
- **UX Flow**: Browse telescopes → Compare specifications → Select configuration → Apply settings
- **Key Features**:
  - Comprehensive telescope database (Vespera, Stellina, Hyperia, custom)
  - Side-by-side specification comparison
  - FOV visualization for different targets
  - Custom telescope configuration support
  - Equipment-specific recommendations
- **Touch Interactions**:
  - Swipe between telescope cards
  - Tap for detailed specifications
  - Pinch-to-zoom on FOV comparisons
  - Toggle switches for feature comparison
- **Visual Design**: Card-based layout, specification tables, visual FOV indicators

#### **⚙️ Settings Screen** (`settings_screen.py`)
**Purpose**: App configuration and user preferences
- **UX Flow**: Access settings → Modify preferences → Save configuration → Apply changes
- **Key Features**:
  - Location management with GPS integration
  - Observation preferences and constraints
  - Display settings (theme, units, chart preferences)
  - Data management (cache, offline catalogs)
  - Account and sync settings
- **Touch Interactions**:
  - Toggle switches for boolean preferences
  - Slider controls for numerical values
  - Tap to edit text fields
  - Swipe to delete saved locations
- **Visual Design**: Grouped settings, clear section headers, immediate feedback

#### **📊 Reports Screen** (`reports_screen.py`)
**Purpose**: Generate and view observation reports
- **UX Flow**: Select report type → Configure parameters → Generate report → View/export results
- **Key Features**:
  - Multiple report formats (session summary, target analysis, equipment comparison)
  - Customizable date ranges and filtering
  - Visual charts and graphs
  - Export to PDF, CSV, or image formats
  - Historical session tracking
- **Touch Interactions**:
  - Swipe between report sections
  - Pinch-to-zoom on charts and graphs
  - Tap to drill down into detailed data
  - Long-press for export options
- **Visual Design**: Chart-heavy interface, export controls, data visualization

### **🎨 User Experience Design Principles**

#### **Touch-First Design**
- **Large Touch Targets**: Minimum 44pt touch targets for easy finger navigation
- **Gesture Support**: Intuitive swipe, pinch, and tap gestures throughout the app
- **Haptic Feedback**: Tactile responses for important actions and confirmations
- **Edge-to-Edge Design**: Full-screen layouts optimized for modern mobile devices

#### **Night Vision Optimization**
- **Dark Theme**: Red-tinted dark mode to preserve night vision
- **Brightness Control**: Automatic and manual brightness adjustment
- **High Contrast**: Clear visibility in low-light conditions
- **Minimal Blue Light**: Reduced blue light emission for comfortable night use

#### **Progressive Disclosure**
- **Layered Information**: Complex data presented in digestible chunks
- **Contextual Actions**: Relevant actions appear when needed
- **Smart Defaults**: Intelligent default settings based on user behavior
- **Guided Workflows**: Step-by-step processes for complex tasks

#### **Performance Optimization**
- **Lazy Loading**: Data loaded on-demand to maintain responsiveness
- **Background Processing**: Heavy calculations performed in background threads
- **Caching Strategy**: Intelligent caching of frequently accessed data
- **Offline Capability**: Core functionality available without internet connection

### **🔧 Technical Implementation Details**

#### **State Management** (`utils/app_state.py`)
- **Centralized State**: Single source of truth for app-wide data
- **Reactive Updates**: Automatic UI updates when data changes
- **Persistence**: State saved across app sessions
- **Thread Safety**: Safe concurrent access from multiple screens

#### **Location Services** (`utils/location_manager.py`)
- **GPS Integration**: Automatic location detection with user permission
- **Manual Entry**: Coordinate input with validation
- **Location Profiles**: Save and manage multiple observing sites
- **Timezone Handling**: Automatic timezone detection and conversion

#### **Smart Recommendations** (`utils/smart_scopes.py`)
- **Equipment Matching**: Telescope recommendations based on targets
- **FOV Optimization**: Automatic field-of-view calculations
- **Imaging Suggestions**: Exposure and filter recommendations
- **Performance Metrics**: Equipment comparison and scoring

#### **Advanced Filtering** (`utils/advanced_filter.py`)
- **Multi-Criteria Filtering**: Complex filter combinations
- **Real-Time Updates**: Filters applied as user types
- **Saved Filters**: Store and recall common filter sets
- **Performance Optimization**: Efficient filtering algorithms

#### **Mobile Plotting** (`utils/plotting.py`)
- **Touch-Optimized Charts**: Interactive plots designed for mobile
- **Gesture Navigation**: Pinch, zoom, and pan support
- **Responsive Design**: Charts adapt to screen size and orientation
- **Export Capabilities**: Save charts as images or PDFs

#### **Custom Widgets** (`widgets/plot_widget.py`)
- **Astronomical Charts**: Specialized plotting widgets for sky data
- **Interactive Elements**: Touch-responsive chart components
- **Performance Optimized**: Efficient rendering for mobile devices
- **Customizable Themes**: Support for day/night modes

## Integration with AstroScope Engine

The mobile app seamlessly integrates with the existing astropy modules:

- **astronomy/**: Core astronomical calculations
- **analysis/**: Target scoring and optimization
- **catalogs/**: Object catalog management
- **models/**: Data models and scheduling strategies
- **config/**: Configuration management
- **utilities/**: Helper functions
- **visualization/**: Data visualization

## Configuration

The app uses the same configuration system as the desktop version:

- Location profiles from `config.json`
- Telescope configurations
- Scheduling preferences
- Imaging parameters

## Usage

1. **Set Location**: Configure your observing location in Settings
2. **Choose Strategy**: Select a scheduling strategy that fits your goals
3. **Browse Targets**: View tonight's optimized target list
4. **Plan Session**: Add targets to your observation plan
5. **Mosaic Planning**: Use the mosaic planner for large objects

## Supported Platforms

- **Android**: API 21+ (Android 5.0+)
- **iOS**: iOS 10.0+
- **Desktop**: Windows, macOS, Linux

## Dependencies

- Kivy 2.1.0+ (UI framework)
- NumPy (numerical calculations)
- Matplotlib (plotting and visualization)
- PyTZ (timezone handling)
- Pandas (data manipulation)
- Pillow (image processing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on target platforms
5. Submit a pull request

## License

This project is part of the AstroScope suite and follows the same licensing terms.

## Support

For support, bug reports, or feature requests, please use the GitHub issue tracker or contact the development team.