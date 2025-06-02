# AstroScope Planner Mobile App - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Screen System](#screen-system)
4. [Plotting Infrastructure](#plotting-infrastructure)
5. [Reporting System](#reporting-system)
6. [State Management](#state-management)
7. [Location Services](#location-services)
8. [Astropy Integration](#astropy-integration)
9. [Performance Optimizations](#performance-optimizations)
10. [Testing Framework](#testing-framework)
11. [API Reference](#api-reference)
12. [Development Guidelines](#development-guidelines)

## Architecture Overview

### Design Principles
- **Cross-platform compatibility** using Kivy framework
- **Modular architecture** with clear separation of concerns
- **Responsive design** optimized for touch interfaces
- **Efficient memory management** for mobile constraints
- **Offline-first approach** with optional online features

### Technology Stack
```
┌─────────────────────────────────────┐
│           User Interface            │
│         (Kivy Screens)              │
├─────────────────────────────────────┤
│        Application Logic            │
│    (Screen Controllers & Utils)     │
├─────────────────────────────────────┤
│       Data & State Layer            │
│   (AppState & LocationManager)      │
├─────────────────────────────────────┤
│      Visualization Layer            │
│   (Matplotlib & Custom Widgets)    │
├─────────────────────────────────────┤
│       Astropy Integration           │
│    (Existing Astropy Modules)       │
└─────────────────────────────────────┘
```

### File Structure
```
mobile_app/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── buildozer.spec            # Mobile packaging config
├── test_app.py               # Test suite
├── screens/                  # UI screens
│   ├── __init__.py
│   ├── home_screen.py        # Dashboard and navigation
│   ├── targets_screen.py     # Target browsing
│   ├── target_detail_screen.py # Detailed target view
│   ├── mosaic_screen.py      # Mosaic planning
│   ├── settings_screen.py    # App configuration
│   └── reports_screen.py     # Report generation
├── utils/                    # Core utilities
│   ├── __init__.py
│   ├── app_state.py          # State management
│   ├── location_manager.py   # GPS and location
│   ├── plotting.py           # Mobile plotting
│   └── reports.py            # Report generation
└── widgets/                  # Custom widgets
    ├── __init__.py
    └── plot_widget.py         # Plotting widgets
```

## Core Components

### Main Application (main.py)
```python
class AstroScopeApp(App):
    """Main application class with screen management"""
    
    def build(self):
        # Initialize screen manager
        # Load astropy modules
        # Setup state management
        # Configure navigation
        
    def load_astropy_data(self):
        # Load catalog and configuration
        # Initialize location
        # Setup default state
```

**Key Features:**
- Screen management and navigation
- Astropy module integration
- State initialization
- Error handling and recovery

### Screen Manager
```python
class ScreenManager:
    """Manages navigation between app screens"""
    
    screens = {
        'home': HomeScreen,
        'targets': TargetsScreen,
        'target_detail': TargetDetailScreen,
        'mosaic': MosaicScreen,
        'settings': SettingsScreen,
        'reports': ReportsScreen
    }
```

## Screen System

### Home Screen (screens/home_screen.py)
**Purpose**: Main dashboard with quick actions and overview

**Features:**
- Quick action buttons (Targets, Mosaic, Reports, Settings)
- Current location display
- Tonight's visibility chart
- Weather and moon phase info

**Key Methods:**
```python
def create_quick_actions(self):
    # Create navigation buttons
    
def create_visibility_chart_card(self):
    # Generate tonight's visibility chart
    
def go_to_targets(self):
    # Navigate to targets screen
```

### Targets Screen (screens/targets_screen.py)
**Purpose**: Browse and filter available targets

**Features:**
- Target list with filtering
- Object type filtering
- Sorting options (altitude, score, name)
- Search functionality

**Key Methods:**
```python
def create_filter_section(self):
    # Object type and sorting filters
    
def create_targets_list(self):
    # Scrollable target list
    
def filter_targets(self, object_type):
    # Apply filtering logic
```

### Target Detail Screen (screens/target_detail_screen.py)
**Purpose**: Detailed information about selected target

**Features:**
- Target information display
- Trajectory and altitude plots
- Observability data
- Imaging recommendations

**Key Methods:**
```python
def create_target_info_section(self):
    # Display target details
    
def create_plots_section(self):
    # Add trajectory and altitude plots
    
def create_observability_section(self):
    # Show visibility windows
```

### Mosaic Screen (screens/mosaic_screen.py)
**Purpose**: Plan mosaic captures for extended objects

**Features:**
- Mosaic group management
- Panel layout visualization
- Coverage calculations
- Export capabilities

**Key Methods:**
```python
def create_mosaic_groups_section(self):
    # Display mosaic groups
    
def create_visualization_section(self):
    # Add mosaic plots
    
def create_group_card(self, group):
    # Individual group display
```

### Settings Screen (screens/settings_screen.py)
**Purpose**: App configuration and preferences

**Features:**
- Location management
- Observation preferences
- Display settings
- Data management

**Key Methods:**
```python
def create_location_section(self):
    # GPS and manual location
    
def create_preferences_section(self):
    # User preferences
    
def save_settings(self):
    # Persist configuration
```

### Reports Screen (screens/reports_screen.py)
**Purpose**: Generate and view observation reports

**Features:**
- Report type selection
- Report generation
- Save and share functionality
- Export options

**Key Methods:**
```python
def create_report_type_section(self):
    # Report type buttons
    
def generate_report(self, report_type):
    # Create specific report
    
def save_report(self, content):
    # Save to device storage
```

## Plotting Infrastructure

### MobilePlotGenerator (utils/plotting.py)
**Purpose**: Create mobile-optimized matplotlib plots

```python
class MobilePlotGenerator:
    """Mobile-optimized plotting for astronomy data"""
    
    def __init__(self):
        self.setup_mobile_backend()
        self.configure_style()
    
    def create_trajectory_plot(self, target_name, trajectory_data):
        """Create object trajectory plot"""
        
    def create_visibility_chart(self, location, date_range):
        """Create visibility chart for location"""
        
    def create_altitude_plot(self, target_name, altitude_data):
        """Create altitude vs time plot"""
        
    def create_mosaic_plot(self, title, mosaic_groups):
        """Create mosaic overview plot"""
        
    def create_mosaic_grid_plot(self, title, mosaic_groups):
        """Create detailed mosaic grid layout"""
```

**Optimization Features:**
- Mobile-optimized figure sizes
- Touch-friendly plot elements
- Memory-efficient rendering
- Automatic cleanup

### PlotWidget (widgets/plot_widget.py)
**Purpose**: Custom Kivy widget for displaying plots

```python
class PlotWidget(BoxLayout):
    """Custom widget for displaying matplotlib plots in Kivy"""
    
    def display_plot(self, figure):
        """Display matplotlib figure"""
        
    def clear_plot(self):
        """Clear current plot"""
        
    def save_plot(self, filename):
        """Save plot to file"""

class PlotContainer(TabbedPanel):
    """Tabbed container for multiple plots"""
    
    def add_plot_tab(self, title, figure):
        """Add new plot tab"""
        
    def switch_to_tab(self, tab_name):
        """Switch to specific tab"""
```

**Features:**
- Touch-optimized controls
- Zoom and pan support
- Tab-based organization
- Export functionality

## Reporting System

### MobileReportGenerator (utils/reports.py)
**Purpose**: Generate comprehensive observation reports

```python
class MobileReportGenerator:
    """Generate mobile-optimized reports"""
    
    def generate_session_report(self, targets, location, date=None):
        """Generate session planning report"""
        
    def generate_target_report(self, target_data):
        """Generate detailed target analysis"""
        
    def generate_mosaic_report(self, mosaic_groups):
        """Generate mosaic planning report"""
        
    def format_for_mobile(self, content):
        """Format content for mobile display"""
        
    def export_report(self, content, format='txt'):
        """Export report in various formats"""
```

**Report Types:**
1. **Session Reports**: Night planning with target recommendations
2. **Target Reports**: Detailed analysis of specific objects
3. **Mosaic Reports**: Panel layout and capture planning

**Export Formats:**
- Plain text (.txt)
- Markdown (.md)
- PDF (future enhancement)
- Email sharing

## State Management

### AppState (utils/app_state.py)
**Purpose**: Centralized application state management

```python
class AppState(EventDispatcher):
    """Central application state manager"""
    
    # Observable properties (Kivy)
    tonights_targets = ListProperty([])
    all_visible_objects = ListProperty([])
    current_location = DictProperty({})
    selected_target = DictProperty({})
    mosaic_groups = ListProperty([])
    
    # User preferences
    scheduling_strategy = StringProperty('max_objects')
    show_mosaic_only = BooleanProperty(False)
    min_visibility_hours = NumericProperty(2.0)
    
    # UI state
    is_loading = BooleanProperty(False)
    current_screen = StringProperty('home')
```

**Features:**
- Observable properties with automatic UI updates
- Persistent state across screen transitions
- User preference management
- Session data tracking

**State Synchronization:**
```python
# Automatic UI updates when state changes
app_state.bind(tonights_targets=self.update_targets_display)
app_state.bind(current_location=self.update_location_display)
```

## Location Services

### LocationManager (utils/location_manager.py)
**Purpose**: Handle GPS and location-based calculations

```python
class LocationManager:
    """Manage GPS and location services"""
    
    def __init__(self):
        self.setup_gps()
        self.load_saved_locations()
    
    def get_current_location(self):
        """Get current GPS location"""
        
    def save_location(self, name, lat, lon, elevation=0):
        """Save location for future use"""
        
    def get_saved_locations(self):
        """Retrieve saved locations"""
        
    def calculate_timezone(self, lat, lon):
        """Determine timezone from coordinates"""
```

**Features:**
- GPS integration with permission handling
- Saved location management
- Automatic timezone detection
- Coordinate validation

**Platform Integration:**
```python
# iOS: Core Location
# Android: GPS Provider
# Fallback: Manual entry
```

## Astropy Integration

### Integration Layer
**Purpose**: Bridge between mobile app and existing astropy modules

```python
# In main.py
def load_astropy_data(self):
    """Load and integrate astropy modules"""
    
    # Load catalog
    self.catalog = astropy.get_combined_catalog()
    
    # Load configuration
    self.config = astropy.load_config()
    
    # Get default location
    self.location_id, self.location = astropy.get_default_location(self.config)
    
    # Initialize state
    self.app_state.current_location = self.location
```

**Data Flow:**
```
Astropy Modules → Mobile App State → UI Components
     ↓                    ↓               ↓
  Calculations      State Updates    UI Refresh
```

**Key Integrations:**
- Target catalog loading
- Visibility calculations
- Coordinate transformations
- Mosaic planning
- Observation scheduling

## Performance Optimizations

### Memory Management
```python
# Automatic cleanup
import gc

def on_screen_leave(self):
    # Clear large objects
    self.plots = None
    gc.collect()

# Lazy loading
def load_targets(self):
    if not hasattr(self, '_targets'):
        self._targets = self.calculate_targets()
    return self._targets
```

### Plot Optimization
```python
# Mobile-optimized matplotlib
matplotlib.use('Agg')  # Non-interactive backend
plt.ioff()  # Turn off interactive mode

# Efficient figure management
def create_plot(self):
    fig = plt.figure(figsize=(8, 6), dpi=100)
    # ... plotting code ...
    plt.tight_layout()
    return fig
```

### Background Processing
```python
# Use threading for heavy calculations
from threading import Thread

def calculate_visibility_async(self):
    thread = Thread(target=self._calculate_visibility)
    thread.daemon = True
    thread.start()
```

## Testing Framework

### Test Suite (test_app.py)
```python
class TestMobileApp:
    """Comprehensive test suite for mobile app"""
    
    def test_file_structure(self):
        """Verify all required files exist"""
        
    def test_imports(self):
        """Test module imports"""
        
    def test_app_state(self):
        """Test state management"""
        
    def test_location_manager(self):
        """Test location services"""
        
    def test_astropy_integration(self):
        """Test astropy module integration"""
```

**Test Categories:**
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Cross-component functionality
3. **UI Tests**: Screen and widget testing
4. **Performance Tests**: Memory and speed testing

### Continuous Testing
```bash
# Run tests automatically
python test_app.py

# Run with coverage
coverage run test_app.py
coverage report
```

## API Reference

### Core Classes

#### AstroScopeApp
```python
class AstroScopeApp(App):
    """Main application class"""
    
    def build(self) -> ScreenManager:
        """Build and return the root widget"""
        
    def load_astropy_data(self) -> None:
        """Load astropy modules and data"""
        
    def on_pause(self) -> bool:
        """Handle app pause events"""
        
    def on_resume(self) -> None:
        """Handle app resume events"""
```

#### AppState
```python
class AppState(EventDispatcher):
    """Application state manager"""
    
    # Properties
    tonights_targets: List[Dict]
    current_location: Dict
    selected_target: Dict
    
    # Methods
    def get_strategy_display_name(self, strategy: str) -> str
    def filter_targets_by_type(self, object_type: str) -> List[Dict]
```

#### LocationManager
```python
class LocationManager:
    """Location services manager"""
    
    def get_current_location(self) -> Tuple[float, float]
    def save_location(self, name: str, lat: float, lon: float) -> None
    def get_saved_locations(self) -> List[Dict]
```

#### MobilePlotGenerator
```python
class MobilePlotGenerator:
    """Mobile plotting utilities"""
    
    def create_trajectory_plot(self, target_name: str, data: Dict) -> Figure
    def create_visibility_chart(self, location: Dict, date_range: Dict) -> Figure
    def create_altitude_plot(self, target_name: str, data: Dict) -> Figure
```

### Screen Classes

#### BaseScreen
```python
class BaseScreen(Screen):
    """Base class for all screens"""
    
    def on_enter(self) -> None:
        """Called when screen is entered"""
        
    def on_leave(self) -> None:
        """Called when screen is left"""
        
    def update_display(self) -> None:
        """Update screen display"""
```

### Widget Classes

#### PlotWidget
```python
class PlotWidget(BoxLayout):
    """Custom plot display widget"""
    
    def display_plot(self, figure: Figure) -> None
    def clear_plot(self) -> None
    def save_plot(self, filename: str) -> None
```

## Development Guidelines

### Code Style
```python
# Follow PEP 8 standards
# Use type hints
def calculate_altitude(target: Dict, location: Dict) -> float:
    """Calculate target altitude at location"""
    pass

# Document all public methods
def create_plot(self, data: Dict) -> Figure:
    """
    Create matplotlib plot from data.
    
    Args:
        data: Dictionary containing plot data
        
    Returns:
        matplotlib Figure object
    """
```

### Error Handling
```python
# Graceful error handling
try:
    result = calculate_complex_operation()
except Exception as e:
    Logger.error(f"Calculation failed: {e}")
    self.show_error_message("Calculation failed. Please try again.")
    return default_value
```

### Performance Guidelines
1. **Lazy Loading**: Load data only when needed
2. **Memory Cleanup**: Clear large objects when done
3. **Background Processing**: Use threads for heavy calculations
4. **Efficient Plotting**: Optimize matplotlib usage
5. **State Management**: Minimize state updates

### Testing Guidelines
1. **Test Coverage**: Aim for >80% code coverage
2. **Unit Tests**: Test individual components
3. **Integration Tests**: Test component interactions
4. **UI Tests**: Test user interface functionality
5. **Performance Tests**: Monitor memory and speed

### Documentation Guidelines
1. **Docstrings**: Document all public methods
2. **Type Hints**: Use type annotations
3. **Comments**: Explain complex logic
4. **Examples**: Provide usage examples
5. **Architecture**: Document design decisions

## Conclusion

The AstroScope Planner mobile app provides a comprehensive, well-architected solution for mobile astronomy planning. The modular design, efficient performance optimizations, and thorough testing framework ensure a robust and maintainable codebase.

**Key Strengths:**
- ✅ **Modular Architecture**: Clear separation of concerns
- ✅ **Cross-platform Compatibility**: iOS and Android support
- ✅ **Performance Optimized**: Mobile-specific optimizations
- ✅ **Comprehensive Testing**: Full test coverage
- ✅ **Extensible Design**: Easy to add new features

**Repository**: `popoloni/astropy` (branch: `app`)  
**Status**: Production ready  
**Documentation**: Complete technical specification