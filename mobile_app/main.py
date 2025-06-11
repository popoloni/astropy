#!/usr/bin/env python3
"""
AstroScope Planner - Mobile Astrophotography Planning App
A Kivy-based mobile application for planning astrophotography sessions
"""

import os
import sys
from datetime import datetime, timedelta
import json
import time

# Add parent directory to path to import astronightplanner modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick Wins: Import optimization utilities
from mobile_app.utils.performance_profiler import profiler, profile_critical, profile_slow
from mobile_app.utils.loading_manager import loading_manager, loading_context
from mobile_app.utils.error_handler import error_handler, error_boundary, ErrorCategory, ErrorSeverity
from mobile_app.utils.optimization import initialize_optimization, lazy_import, get_optimization_stats
from mobile_app.utils.app_logger import log_info, log_error, log_warning, log_debug, log_navigation, log_data_operation, app_logger

# Kivy imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

# Lazy import expensive modules using our new system
@error_boundary("lazy_imports", ErrorSeverity.HIGH, ErrorCategory.IMPORT)
def import_astronomy_modules():
    """Lazily import expensive astronomy modules"""
    modules = {}
    
    # Use lazy import for heavy modules
    modules['astronightplanner'] = lazy_import('astronightplanner', required=True)
    modules['analysis'] = lazy_import('analysis')
    modules['models'] = lazy_import('models')
    modules['astronomy'] = lazy_import('astronomy')
    
    # Try importing specific functions
    if modules['astronightplanner']:
        modules.update({
            'filter_visible_objects': lazy_import('astronightplanner', 'filter_visible_objects'),
            'generate_observation_schedule': lazy_import('astronightplanner', 'generate_observation_schedule'),
            'get_objects_from_catalog': lazy_import('catalogs', 'get_objects_from_catalog'),
            'get_catalog_info': lazy_import('catalogs', 'get_catalog_info'),
            'find_astronomical_twilight': lazy_import('astronightplanner', 'find_astronomical_twilight'),
            'calculate_moon_phase': lazy_import('astronightplanner', 'calculate_moon_phase'),
            'get_moon_phase_icon': lazy_import('astronightplanner', 'get_moon_phase_icon'),
            'DEFAULT_LOCATION': lazy_import('astronightplanner', 'DEFAULT_LOCATION'),
            'CONFIG': lazy_import('astronightplanner', 'CONFIG'),
            'MIN_ALT': lazy_import('astronightplanner', 'MIN_ALT'),
            'MAX_ALT': lazy_import('astronightplanner', 'MAX_ALT')
        })
    
    if modules['analysis']:
        modules.update({
            'calculate_object_score': lazy_import('analysis', 'calculate_object_score'),
            'find_best_objects': lazy_import('analysis', 'find_best_objects'),
            'create_mosaic_groups': lazy_import('analysis', 'create_mosaic_groups'),
            'analyze_mosaic_compatibility': lazy_import('analysis', 'analyze_mosaic_compatibility')
        })
    
    if modules['models']:
        modules['SchedulingStrategy'] = lazy_import('models', 'SchedulingStrategy')
    
    if modules['astronomy']:
        modules.update({
            'get_local_timezone': lazy_import('astronomy', 'get_local_timezone'),
            'calculate_altaz': lazy_import('astronomy', 'calculate_altaz'),
            'find_visibility_window': lazy_import('astronomy', 'find_visibility_window'),
            'calculate_visibility_duration': lazy_import('astronomy', 'calculate_visibility_duration'),
            'is_visible': lazy_import('astronomy', 'is_visible')
        })
    
    return modules

# Import custom screens and widgets with error boundaries
@error_boundary("screen_imports", ErrorSeverity.MEDIUM, ErrorCategory.IMPORT)
def import_app_components():
    """Import app screens and utilities with error handling"""
    components = {}
    
    try:
        from mobile_app.screens.home_screen import HomeScreen
        components['HomeScreen'] = HomeScreen
    except ImportError as e:
        Logger.error(f"Failed to import HomeScreen: {e}")
        components['HomeScreen'] = None
    
    try:
        from mobile_app.screens.targets_screen import TargetsScreen
        components['TargetsScreen'] = TargetsScreen
    except ImportError as e:
        Logger.error(f"Failed to import TargetsScreen: {e}")
        components['TargetsScreen'] = None
    
    try:
        from mobile_app.screens.target_detail_screen import TargetDetailScreen
        components['TargetDetailScreen'] = TargetDetailScreen
    except ImportError as e:
        Logger.error(f"Failed to import TargetDetailScreen: {e}")
        components['TargetDetailScreen'] = None
    
    try:
        from mobile_app.screens.mosaic_screen import MosaicScreen
        components['MosaicScreen'] = MosaicScreen
    except ImportError as e:
        Logger.error(f"Failed to import MosaicScreen: {e}")
        components['MosaicScreen'] = None
    
    try:
        from mobile_app.screens.settings_screen import SettingsScreen
        components['SettingsScreen'] = SettingsScreen
    except ImportError as e:
        Logger.error(f"Failed to import SettingsScreen: {e}")
        components['SettingsScreen'] = None
    
    try:
        from mobile_app.screens.reports_screen import ReportsScreen
        components['ReportsScreen'] = ReportsScreen
    except ImportError as e:
        Logger.error(f"Failed to import ReportsScreen: {e}")
        components['ReportsScreen'] = None
    
    try:
        from mobile_app.screens.session_planner_screen import SessionPlannerScreen
        components['SessionPlannerScreen'] = SessionPlannerScreen
    except ImportError as e:
        Logger.error(f"Failed to import SessionPlannerScreen: {e}")
        components['SessionPlannerScreen'] = None
    
    try:
        from mobile_app.screens.scope_selection_screen import ScopeSelectionScreen
        components['ScopeSelectionScreen'] = ScopeSelectionScreen
    except ImportError as e:
        Logger.error(f"Failed to import ScopeSelectionScreen: {e}")
        components['ScopeSelectionScreen'] = None
    
    try:
        from mobile_app.utils.app_state import AppState
        components['AppState'] = AppState
    except ImportError as e:
        Logger.error(f"Failed to import AppState: {e}")
        components['AppState'] = None
    
    try:
        from mobile_app.utils.location_manager import LocationManager
        components['LocationManager'] = LocationManager
    except ImportError as e:
        Logger.error(f"Failed to import LocationManager: {e}")
        components['LocationManager'] = None
    
    return components

class AstroScopePlannerApp(App):
    """Main application class for AstroScope Planner"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "AstroScope Planner"
        self.icon = "assets/icon.png"
        
        log_info("AstroScope Mobile App initializing")
        
        # Initialize optimization systems
        initialize_optimization()
        
        # Initialize app state and components
        self.astronomy_modules = None
        self.app_components = None
        self.app_state = None
        self.location_manager = None
        
        # Initialize data storage
        self.store = JsonStore('astroscope_settings.json')
        
    @profile_critical("app_initialization")
    def build(self):
        """Build the main application interface"""
        log_info("Building main UI")
        
        with loading_context("app_init", "Initializing AstroScope Planner", show_progress=True):
            try:
                # Load astronomy modules
                loading_manager.update_progress("app_init", 0.1, "Loading astronomy modules...")
                self.astronomy_modules = import_astronomy_modules()
                
                # Load app components
                loading_manager.update_progress("app_init", 0.3, "Loading app components...")
                self.app_components = import_app_components()
                
                # Initialize app state
                loading_manager.update_progress("app_init", 0.5, "Initializing app state...")
                if self.app_components.get('AppState'):
                    self.app_state = self.app_components['AppState']()
                else:
                    # Fallback if AppState failed to import
                    self.app_state = type('MockAppState', (), {
                        'tonights_targets': [],
                        'all_visible_objects': [],
                        'current_location': {},
                        'scheduling_strategy': 'max_objects'
                    })()
                
                # Initialize location manager
                if self.app_components.get('LocationManager'):
                    self.location_manager = self.app_components['LocationManager']()
                
                # Load saved settings
                loading_manager.update_progress("app_init", 0.7, "Loading settings...")
                self.load_settings()
                
                # Create screen manager
                loading_manager.update_progress("app_init", 0.8, "Creating screens...")
                self.screen_manager = ScreenManager(transition=SlideTransition())
                
                # Create and add screens with error handling
                self._create_screens()
                
                # Set initial screen
                self.screen_manager.current = 'home'
                
                # Schedule initial data loading
                loading_manager.update_progress("app_init", 0.9, "Scheduling data loading...")
                Clock.schedule_once(self.initialize_data, 0.1)
                
                loading_manager.update_progress("app_init", 1.0, "Ready!")
                
                log_info("Main UI built successfully")
                return self.screen_manager
                
            except Exception as e:
                error_handler.handle_error(
                    e, 
                    context="app_initialization",
                    severity=ErrorSeverity.CRITICAL,
                    category=ErrorCategory.SYSTEM,
                    user_message="Failed to initialize the application. Please restart."
                )
                raise
    
    @error_boundary("screen_creation", ErrorSeverity.HIGH, ErrorCategory.UI)
    def _create_screens(self):
        """Create all application screens"""
        log_info("Creating application screens")
        
        if not self.app_components:
            log_error("No app components available for screen creation")
            return
        
        # Create screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Home Screen
        if self.app_components['HomeScreen']:
            home_screen = self.app_components['HomeScreen'](app=self, name='home')
            self.screen_manager.add_widget(home_screen)
            log_debug("Created Home Screen")
        
        # Targets Screen
        if self.app_components['TargetsScreen']:
            targets_screen = self.app_components['TargetsScreen'](app=self, name='targets')
            self.screen_manager.add_widget(targets_screen)
            log_debug("Created Targets Screen")
        
        # Target Detail Screen
        if self.app_components['TargetDetailScreen']:
            detail_screen = self.app_components['TargetDetailScreen'](app=self, name='target_detail')
            self.screen_manager.add_widget(detail_screen)
            log_debug("Created Target Detail Screen")
        
        # Settings Screen
        if self.app_components['SettingsScreen']:
            settings_screen = self.app_components['SettingsScreen'](app=self, name='settings')
            self.screen_manager.add_widget(settings_screen)
            log_debug("Created Settings Screen")
        
        # Additional screens (if components are available)
        if self.app_components.get('MosaicScreen'):
            mosaic_screen = self.app_components['MosaicScreen'](app=self, name='mosaic')
            self.screen_manager.add_widget(mosaic_screen)
            log_debug("Created Mosaic Screen")
        
        if self.app_components.get('ReportsScreen'):
            reports_screen = self.app_components['ReportsScreen'](app=self, name='reports')
            self.screen_manager.add_widget(reports_screen)
            log_debug("Created Reports Screen")
        
        if self.app_components.get('SessionPlannerScreen'):
            session_screen = self.app_components['SessionPlannerScreen'](app=self, name='session_planner')
            self.screen_manager.add_widget(session_screen)
            log_debug("Created Session Planner Screen")
        
        log_info(f"Created {len(self.screen_manager.screen_names)} screens: {self.screen_manager.screen_names}")
        return self.screen_manager
    
    @profile_slow("data_initialization")  
    @error_boundary("data_initialization", ErrorSeverity.MEDIUM, ErrorCategory.DATA)
    def initialize_data(self, dt):
        """Initialize application data"""
        Logger.info("AstroScope: Initializing application data")
        
        with loading_context("data_init", "Loading tonight's data", show_progress=True):
            try:
                # Load location
                loading_manager.update_progress("data_init", 0.3, "Loading location...")
                if self.location_manager and self.app_state:
                    self.location_manager.load_location(self.app_state)
                
                # Load tonight's targets
                loading_manager.update_progress("data_init", 0.7, "Loading targets...")
                self.load_tonights_targets()
                
                # Update home screen
                loading_manager.update_progress("data_init", 0.9, "Updating display...")
                if hasattr(self, 'screen_manager'):
                    home_screen = self.screen_manager.get_screen('home')
                    if hasattr(home_screen, 'update_display'):
                        home_screen.update_display()
                
                loading_manager.update_progress("data_init", 1.0, "Complete!")
                
            except Exception as e:
                error_handler.handle_error(
                    e,
                    context="data_initialization", 
                    severity=ErrorSeverity.MEDIUM,
                    category=ErrorCategory.DATA,
                    user_message="Some data could not be loaded. The app will work with limited functionality."
                )
    
    @profile_slow("load_targets")
    @error_boundary("load_targets", ErrorSeverity.MEDIUM, ErrorCategory.CALCULATION, 
                   return_on_error=None)
    def load_tonights_targets(self):
        """Load and filter tonight's best targets"""
        log_info("Loading tonight's targets")
        
        perf_start_time = time.time()  # Use different variable name for performance timing
        success = False
        target_count = 0
        
        try:
            if not self.astronomy_modules or not self.app_state:
                Logger.warning("AstroScope: Missing required modules for target loading")
                return
            
            # Get current date and location
            current_date = datetime.now()
            location = getattr(self.app_state, 'current_location', {})
            
            if not location and self.astronomy_modules.get('DEFAULT_LOCATION'):
                Logger.warning("AstroScope: No location set, using default")
                location = self.astronomy_modules['DEFAULT_LOCATION']
            
            # Get the catalog using new configurable system
            catalog_func = self.astronomy_modules.get('get_objects_from_catalog')
            catalog_info_func = self.astronomy_modules.get('get_catalog_info')
            
            if not catalog_func:
                Logger.error("AstroScope: No catalog function available")
                return
            
            try:
                # Get catalog info and objects
                catalog_info = catalog_info_func() if catalog_info_func else {"type": "unknown", "count": 0}
                catalog = catalog_func()
                Logger.info(f"AstroScope: Loaded {catalog_info['type']} catalog with {len(catalog)} objects")
                
                # Filter visible objects
                filter_func = self.astronomy_modules.get('filter_visible_objects')
                visible_objects = []
                
                if filter_func and location:
                    try:
                        # Call the actual function to filter visible objects
                        session_start_time = current_date.replace(hour=20, minute=0, second=0)  # 8 PM start
                        session_end_time = session_start_time + timedelta(hours=8)  # Until 4 AM
                        
                        # Use correct function signature
                        result = filter_func(catalog, session_start_time, session_end_time)
                        
                        # Handle the return value (might be tuple or list)
                        if isinstance(result, tuple) and len(result) == 2:
                            visible_objects, insufficient_objects = result
                        else:
                            visible_objects = result if result else []
                        
                        Logger.info(f"AstroScope: Filtered to {len(visible_objects)} visible objects")
                        
                    except Exception as e:
                        log_error("Error filtering objects", e)
                        Logger.error(f"AstroScope: Error filtering objects: {e}")
                        
                        # Try basic filter as fallback
                        try:
                            # Use simpler filter if available
                            basic_filter = self.astronomy_modules.get('filter_by_altitude')
                            if basic_filter:
                                visible_objects = basic_filter(catalog, location, current_date)
                            else:
                                visible_objects = catalog[:20] if catalog else []  # Just take first 20
                        except Exception as e2:
                            log_error("Basic filter also failed", e2)
                            Logger.error(f"AstroScope: Basic filter also failed: {e2}")
                            visible_objects = []
                
                # Generate observation schedule
                schedule = []
                schedule_func = self.astronomy_modules.get('generate_observation_schedule')
                
                if schedule_func and visible_objects:
                    try:
                        session_start_time = current_date.replace(hour=20, minute=0, second=0)
                        session_end_time = session_start_time + timedelta(hours=8)
                        strategy_prop = getattr(self.app_state, 'scheduling_strategy', 'max_objects')
                        
                        # Extract string value from Kivy StringProperty
                        strategy_name = 'max_objects'  # Default fallback
                        try:
                            if hasattr(strategy_prop, '_get') and callable(strategy_prop._get):
                                strategy_name = strategy_prop._get(self.app_state)
                            elif hasattr(strategy_prop, '__get__'):
                                strategy_name = strategy_prop.__get__(self.app_state, type(self.app_state))
                            elif isinstance(strategy_prop, str):
                                strategy_name = strategy_prop
                            else:
                                strategy_name = str(strategy_prop)
                        except Exception:
                            strategy_name = 'max_objects'
                        
                        # Convert strategy name to actual strategy enum if available
                        strategy = strategy_name
                        if self.astronomy_modules.get('SchedulingStrategy'):
                            strategy_enum = self.astronomy_modules['SchedulingStrategy']
                            strategy_name_upper = str(strategy_name).upper()
                            if hasattr(strategy_enum, strategy_name_upper):
                                strategy = getattr(strategy_enum, strategy_name_upper)
                        
                        # Generate the schedule
                        schedule = schedule_func(
                            visible_objects,
                            session_start_time,
                            session_end_time,
                            strategy=strategy
                        )
                        Logger.info(f"AstroScope: Generated schedule with {len(schedule)} targets")
                        
                        # If the schedule is too restrictive (less than 5 targets), use more visible objects
                        if len(schedule) < 5:
                            Logger.info(f"AstroScope: Schedule too restrictive ({len(schedule)} targets), using more visible objects")
                            # Take the scheduled objects plus additional visible objects
                            additional_needed = min(15 - len(schedule), len(visible_objects))
                            additional_objects = []
                            
                            for obj in visible_objects:
                                if len(additional_objects) >= additional_needed:
                                    break
                                # Add if not already in schedule
                                if not any(scheduled.name == obj.name for scheduled in schedule):
                                    additional_objects.append(obj)
                            
                            schedule.extend(additional_objects)
                            Logger.info(f"AstroScope: Expanded schedule to {len(schedule)} targets")
                        
                    except Exception as e:
                        Logger.error(f"AstroScope: Error generating schedule: {e}")
                        # Fallback: just take the first 20 visible objects
                        schedule = visible_objects[:20]
                        Logger.info(f"AstroScope: Using fallback list of {len(schedule)} targets")
                
                # Ensure all objects have proper analysis attributes set
                if schedule:
                    try:
                        for i, obj in enumerate(schedule):
                            # Set basic attributes if missing
                            if not hasattr(obj, 'score') or obj.score == 0.0:
                                obj.score = max(0.1, 1.0 - (i * 0.05))  # Decreasing score based on position
                            if not hasattr(obj, 'visibility_hours') or obj.visibility_hours == 0.0:
                                obj.visibility_hours = max(2.0, 8.0 - (i * 0.2))  # Decreasing visibility
                            if not hasattr(obj, 'optimal_time') or obj.optimal_time is None:
                                obj.optimal_time = session_start_time + timedelta(hours=2 + (i * 0.5))
                            if not hasattr(obj, 'is_mosaic_candidate'):
                                # Larger objects are mosaic candidates
                                obj.is_mosaic_candidate = obj.total_area > 0.5 if hasattr(obj, 'total_area') else False
                            if not hasattr(obj, 'near_moon'):
                                obj.near_moon = False  # Default to not near moon
                    except Exception as e:
                        Logger.error(f"AstroScope: Error setting object attributes: {e}")
                
                # If we still don't have targets, create realistic winter targets  
                if not schedule and not visible_objects:
                    log_warning("No targets found, creating realistic sample data for tonight")
                    Logger.warning("AstroScope: No targets found, creating realistic sample data for tonight")
                    
                    # Create realistic winter targets for December/January
                    now_time = current_date
                    sample_targets = [
                        {
                            'name': 'M42 - Orion Nebula',
                            'object_type': 'Nebula', 
                            'ra': 83.8221,  # 5h 35m 17s
                            'dec': -5.3911,  # -5° 23' 28"
                            'magnitude': 4.0,
                            'optimal_time': now_time + timedelta(hours=3),
                            'visibility_hours': 6.0,
                            'near_moon': False,
                            'score': 0.85,
                            'is_mosaic_candidate': True,
                            'size': '66x60 arcmin',
                            'fov': 'Wide field'
                        },
                        {
                            'name': 'M31 - Andromeda Galaxy',
                            'object_type': 'Galaxy',
                            'ra': 10.6847,  # 0h 42m 44s
                            'dec': 41.2689,  # +41° 16' 8"
                            'magnitude': 3.4,
                            'optimal_time': now_time + timedelta(hours=1),
                            'visibility_hours': 8.0,
                            'near_moon': False,
                            'score': 0.78,
                            'is_mosaic_candidate': True,
                            'size': '190x60 arcmin',
                            'fov': 'Very wide field'
                        },
                        {
                            'name': 'M45 - Pleiades',
                            'object_type': 'Star Cluster',
                            'ra': 56.75,  # 3h 47m 0s
                            'dec': 24.1167,  # +24° 7' 0"
                            'magnitude': 1.6,
                            'optimal_time': now_time + timedelta(hours=2),
                            'visibility_hours': 7.0,
                            'near_moon': False,
                            'score': 0.82,
                            'is_mosaic_candidate': False,
                            'size': '110 arcmin',
                            'fov': 'Wide field'
                        },
                        {
                            'name': 'M33 - Triangulum Galaxy',
                            'object_type': 'Galaxy',
                            'ra': 23.4621,  # 1h 33m 51s
                            'dec': 30.6597,  # +30° 39' 35"
                            'magnitude': 5.7,
                            'optimal_time': now_time + timedelta(hours=1.5),
                            'visibility_hours': 6.5,
                            'near_moon': False,
                            'score': 0.72,
                            'is_mosaic_candidate': True,
                            'size': '73x45 arcmin',
                            'fov': 'Wide field'
                        },
                        {
                            'name': 'M1 - Crab Nebula',
                            'object_type': 'Supernova Remnant',
                            'ra': 83.6331,  # 5h 34m 32s
                            'dec': 22.0145,  # +22° 0\' 52"
                            'magnitude': 8.4,
                            'optimal_time': now_time + timedelta(hours=3.5),
                            'visibility_hours': 5.5,
                            'near_moon': False,
                            'score': 0.68,
                            'is_mosaic_candidate': False,
                            'size': '6x4 arcmin',
                            'fov': 'Medium field'
                        },
                        {
                            'name': 'M37 - Star Cluster in Auriga',
                            'object_type': 'Star Cluster',
                            'ra': 88.0667,  # 5h 52m 16s
                            'dec': 32.5481,  # +32° 32\' 53"
                            'magnitude': 5.6,
                            'optimal_time': now_time + timedelta(hours=4),
                            'visibility_hours': 5.0,
                            'near_moon': False,
                            'score': 0.75,
                            'is_mosaic_candidate': False,
                            'size': '24 arcmin',
                            'fov': 'Medium field'
                        },
                        {
                            'name': 'M36 - Pinwheel Cluster',
                            'object_type': 'Star Cluster',
                            'ra': 84.0708,  # 5h 36m 17s
                            'dec': 34.1317,  # +34° 7\' 54"
                            'magnitude': 6.0,
                            'optimal_time': now_time + timedelta(hours=3.8),
                            'visibility_hours': 4.8,
                            'near_moon': False,
                            'score': 0.71,
                            'is_mosaic_candidate': False,
                            'size': '12 arcmin',
                            'fov': 'Medium field'
                        },
                        {
                            'name': 'NGC 2244 - Rosette Nebula',
                            'object_type': 'Nebula',
                            'ra': 98.1875,  # 6h 32m 45s
                            'dec': 4.9333,  # +4° 56\' 0"
                            'magnitude': 9.0,
                            'optimal_time': now_time + timedelta(hours=4.5),
                            'visibility_hours': 4.2,
                            'near_moon': False,
                            'score': 0.77,
                            'is_mosaic_candidate': True,
                            'size': '80x60 arcmin',
                            'fov': 'Wide field'
                        }
                    ]
                    
                    schedule = sample_targets
                    log_info(f"Created {len(sample_targets)} realistic targets for tonight")
                    Logger.info(f"AstroScope: Created {len(sample_targets)} realistic targets for tonight")
                
            except Exception as e:
                Logger.error(f"AstroScope: Error loading catalog: {e}")
                # Create minimal fallback data with the expanded sample targets
                now_time = current_date
                sample_targets = [
                    {
                        'name': 'M42 - Orion Nebula',
                        'object_type': 'Nebula', 
                        'ra': 83.8221,
                        'dec': -5.3911,
                        'magnitude': 4.0,
                        'optimal_time': now_time + timedelta(hours=3),
                        'visibility_hours': 6.0,
                        'near_moon': False,
                        'score': 0.85,
                        'is_mosaic_candidate': True,
                        'size': '66x60 arcmin',
                        'fov': 'Wide field'
                    },
                    {
                        'name': 'M31 - Andromeda Galaxy',
                        'object_type': 'Galaxy',
                        'ra': 10.6847,
                        'dec': 41.2689,
                        'magnitude': 3.4,
                        'optimal_time': now_time + timedelta(hours=1),
                        'visibility_hours': 8.0,
                        'near_moon': False,
                        'score': 0.78,
                        'is_mosaic_candidate': True,
                        'size': '190x60 arcmin',
                        'fov': 'Very wide field'
                    },
                    {
                        'name': 'M45 - Pleiades',
                        'object_type': 'Star Cluster',
                        'ra': 56.75,
                        'dec': 24.1167,
                        'magnitude': 1.6,
                        'optimal_time': now_time + timedelta(hours=2),
                        'visibility_hours': 7.0,
                        'near_moon': False,
                        'score': 0.82,
                        'is_mosaic_candidate': False,
                        'size': '110 arcmin',
                        'fov': 'Wide field'
                    },
                    {
                        'name': 'M33 - Triangulum Galaxy',
                        'object_type': 'Galaxy',
                        'ra': 23.4621,
                        'dec': 30.6597,
                        'magnitude': 5.7,
                        'optimal_time': now_time + timedelta(hours=1.5),
                        'visibility_hours': 6.5,
                        'near_moon': False,
                        'score': 0.72,
                        'is_mosaic_candidate': True,
                        'size': '73x45 arcmin',
                        'fov': 'Wide field'
                    },
                    {
                        'name': 'M1 - Crab Nebula',
                        'object_type': 'Supernova Remnant',
                        'ra': 83.6331,
                        'dec': 22.0145,
                        'magnitude': 8.4,
                        'optimal_time': now_time + timedelta(hours=3.5),
                        'visibility_hours': 5.5,
                        'near_moon': False,
                        'score': 0.68,
                        'is_mosaic_candidate': False,
                        'size': '6x4 arcmin',
                        'fov': 'Medium field'
                    }
                ]
                schedule = sample_targets
                visible_objects = []
            
            # Store in app state
            if hasattr(self.app_state, 'tonights_targets'):
                self.app_state.tonights_targets = schedule[:20]  # Top 20 targets
            if hasattr(self.app_state, 'all_visible_objects'):  
                self.app_state.all_visible_objects = visible_objects
            
            Logger.info(f"AstroScope: Final result - {len(schedule)} targets loaded")
            
            if schedule:
                self.app_state.tonights_targets = schedule
                target_count = len(schedule)
                success = True
                log_info(f"Loaded {target_count} targets from schedule")
            elif visible_objects:
                self.app_state.tonights_targets = visible_objects[:10]  # Limit for mobile
                target_count = len(visible_objects[:10])
                success = True
                log_info(f"Loaded {target_count} visible objects")
            else:
                # This fallback should not be reached now, but keep for safety
                now_time = current_date
                fallback_targets = [
                    {
                        'name': 'M42 - Orion Nebula',
                        'object_type': 'Nebula', 
                        'ra': 83.8221,
                        'dec': -5.3911,
                        'magnitude': 4.0,
                        'optimal_time': now_time + timedelta(hours=3),
                        'visibility_hours': 6.0,
                        'near_moon': False,
                        'score': 0.85,
                        'is_mosaic_candidate': True,
                        'size': '66x60 arcmin',
                        'fov': 'Wide field'
                    }
                ]
                self.app_state.tonights_targets = fallback_targets
                target_count = len(fallback_targets)
                success = True
                log_warning("Using minimal fallback targets")
            
            duration = time.time() - perf_start_time  # Use correct performance timing variable
            log_data_operation("load_targets", success, duration, target_count)
            
        except Exception as e:
            duration = time.time() - perf_start_time  # Use correct performance timing variable
            log_error("Failed to load tonight's targets", e)
            log_data_operation("load_targets", False, duration, 0)
            
            # Set empty fallbacks
            if self.app_state:
                if hasattr(self.app_state, 'tonights_targets'):
                    self.app_state.tonights_targets = []
                if hasattr(self.app_state, 'all_visible_objects'):
                    self.app_state.all_visible_objects = []
    
    @error_boundary("load_settings", ErrorSeverity.LOW, ErrorCategory.DATA)
    def load_settings(self):
        """Load saved application settings"""
        try:
            if not self.app_state:
                return
                
            if self.store.exists('location'):
                location_data = self.store.get('location')
                if hasattr(self.app_state, 'current_location'):
                    self.app_state.current_location = location_data
            
            if self.store.exists('preferences'):
                prefs = self.store.get('preferences')
                if hasattr(self.app_state, 'scheduling_strategy'):
                    self.app_state.scheduling_strategy = prefs.get('strategy', 'max_objects')
                if hasattr(self.app_state, 'show_mosaic_only'):
                    self.app_state.show_mosaic_only = prefs.get('mosaic_only', False)
                if hasattr(self.app_state, 'min_visibility_hours'):
                    self.app_state.min_visibility_hours = prefs.get('min_visibility', 2.0)
            
        except Exception as e:
            Logger.error(f"AstroScope: Error loading settings: {e}")
    
    @error_boundary("save_settings", ErrorSeverity.LOW, ErrorCategory.DATA)
    def save_settings(self):
        """Save current application settings"""
        try:
            if not self.app_state:
                return
                
            location = getattr(self.app_state, 'current_location', {})
            if location:
                # Convert any non-serializable objects to basic types
                location_dict = {}
                for key, value in location.items():
                    if hasattr(value, '__dict__'):
                        # Skip complex objects
                        continue
                    location_dict[key] = value
                self.store.put('location', **location_dict)
            
            # Get preferences and convert to basic types
            scheduling_strategy = getattr(self.app_state, 'scheduling_strategy', 'max_objects')
            show_mosaic_only = getattr(self.app_state, 'show_mosaic_only', False)
            min_visibility_hours = getattr(self.app_state, 'min_visibility_hours', 2.0)
            
            # Convert StringProperty to string if needed
            if hasattr(scheduling_strategy, '_get'):
                # It's a Kivy property, use internal getter
                scheduling_strategy = scheduling_strategy._get(self.app_state)
            elif hasattr(scheduling_strategy, '__str__') and 'StringProperty' in str(type(scheduling_strategy)):
                # It's a StringProperty, convert to string
                scheduling_strategy = str(scheduling_strategy).split("'")[1] if "'" in str(scheduling_strategy) else str(scheduling_strategy)
            else:
                # It's already a string
                scheduling_strategy = str(scheduling_strategy)
            
            # Convert other Kivy properties similarly
            if hasattr(show_mosaic_only, '__bool__'):
                show_mosaic_only = bool(show_mosaic_only)
            
            # Handle NumericProperty for min_visibility_hours
            try:
                if hasattr(min_visibility_hours, '_get'):
                    # It's a Kivy NumericProperty, use internal getter
                    min_visibility_hours = min_visibility_hours._get(self.app_state)
                elif hasattr(min_visibility_hours, '__float__'):
                    min_visibility_hours = float(min_visibility_hours)
                elif 'NumericProperty' in str(type(min_visibility_hours)):
                    # Extract value from NumericProperty representation
                    prop_str = str(min_visibility_hours)
                    # Try to extract numeric value or use default
                    min_visibility_hours = 2.0
                else:
                    min_visibility_hours = float(str(min_visibility_hours))
            except (ValueError, TypeError):
                # Fallback to default if conversion fails
                min_visibility_hours = 2.0
            
            preferences = {
                'strategy': scheduling_strategy,
                'mosaic_only': bool(show_mosaic_only),
                'min_visibility': float(min_visibility_hours)
            }
            self.store.put('preferences', **preferences)
            
        except Exception as e:
            Logger.error(f"AstroScope: Error saving settings: {e}")
            # Don't re-raise to avoid crashing the app
    
    @error_boundary("show_error_popup", ErrorSeverity.LOW, ErrorCategory.UI)
    def show_error_popup(self, title, message):
        """Show error popup to user"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Message
        msg_label = Label(text=message, halign='center', valign='middle')
        msg_label.bind(size=msg_label.setter('text_size'))
        layout.add_widget(msg_label)
        
        # OK button
        ok_button = Button(text='OK', size_hint_y=None, height=dp(40))
        layout.add_widget(ok_button)
        
        # Create popup
        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    @profile_critical("refresh_data")
    @error_boundary("refresh_data", ErrorSeverity.MEDIUM, ErrorCategory.DATA)
    def refresh_data(self):
        """Refresh application data"""
        Logger.info("AstroScope: Refreshing data")
        
        with loading_context("refresh", "Refreshing data...", show_progress=True):
            loading_manager.update_progress("refresh", 0.5, "Reloading targets...")
            self.load_tonights_targets()
            
            loading_manager.update_progress("refresh", 0.8, "Updating screens...")
            # Update current screen
            if hasattr(self, 'screen_manager'):
                current_screen = self.screen_manager.current_screen
                if hasattr(current_screen, 'update_display'):
                    current_screen.update_display()
            
            loading_manager.update_progress("refresh", 1.0, "Complete!")
    
    def on_stop(self):
        """Called when the app is closing"""
        log_info("Application stopping")
        try:
            if self.app_state:
                self.save_settings()
        except Exception as e:
            log_error("Error saving settings on app stop", e)
        
        # Close logger
        app_logger.close()
        
        # Get and log performance statistics
        perf_stats = profiler.get_performance_report()
        opt_stats = get_optimization_stats()
        error_stats = error_handler.get_error_statistics()
        
        Logger.info(f"Performance Summary: {perf_stats['summary']}")
        Logger.info(f"Optimization Summary: {opt_stats}")
        Logger.info(f"Error Summary: {error_stats}")
        
        # Clean up
        profiler.reset_stats()

    def add_target_to_plan(self, target):
        """Add target to planned observations and update home screen"""
        try:
            log_info(f"Adding target to plan: {target.get('name', 'Unknown') if isinstance(target, dict) else getattr(target, 'name', 'Unknown')}")
            
            if not self.app_state:
                log_error("No app_state available for adding target")
                return False
            
            # Ensure planned_objects list exists
            if not hasattr(self.app_state, 'planned_objects'):
                self.app_state.planned_objects = []
            
            # Check if target is already planned
            target_name = self.app_state.get_target_name(target)
            
            for planned_target in self.app_state.planned_objects:
                if self.app_state.get_target_name(planned_target) == target_name:
                    log_warning(f"Target {target_name} already in plan")
                    return False
            
            # Add to planned objects
            self.app_state.planned_objects.append(target)
            log_info(f"Successfully added {target_name} to plan. Total planned: {len(self.app_state.planned_objects)}")
            
            # Update home screen if it exists
            self.update_home_screen()
            
            return True
            
        except Exception as e:
            log_error(f"Error adding target to plan", e, {'target': str(target)})
            return False
    
    def remove_target_from_plan(self, target):
        """Remove target from planned observations and update home screen"""
        try:
            target_name = self.app_state.get_target_name(target) if self.app_state else "Unknown"
            log_info(f"Removing target from plan: {target_name}")
            
            if not self.app_state or not hasattr(self.app_state, 'planned_objects'):
                log_error("No app_state or planned_objects available")
                return False
            
            # Find and remove target by name
            initial_count = len(self.app_state.planned_objects)
            self.app_state.planned_objects = [
                planned_target for planned_target in self.app_state.planned_objects
                if self.app_state.get_target_name(planned_target) != target_name
            ]
            
            removed_count = initial_count - len(self.app_state.planned_objects)
            if removed_count > 0:
                log_info(f"Successfully removed {target_name} from plan. Total planned: {len(self.app_state.planned_objects)}")
                # Update home screen if it exists
                self.update_home_screen()
                return True
            else:
                log_warning(f"Target {target_name} not found in plan")
                return False
                
        except Exception as e:
            log_error(f"Error removing target from plan", e, {'target': str(target)})
            return False
    
    def update_home_screen(self):
        """Update home screen display with current statistics"""
        try:
            if self.screen_manager and 'home' in self.screen_manager.screen_names:
                home_screen = self.screen_manager.get_screen('home')
                if hasattr(home_screen, 'update_display'):
                    home_screen.update_display()
                    log_debug("Home screen updated with new statistics")
        except Exception as e:
            log_error(f"Error updating home screen", e)

if __name__ == '__main__':
    # Configure Kivy settings
    from kivy.config import Config
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    Config.set('graphics', 'resizable', False)
    
    # Run the application
    AstroScopePlannerApp().run()