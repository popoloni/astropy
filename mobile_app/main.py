#!/usr/bin/env python3
"""
AstroScope Planner - Mobile Astrophotography Planning App
A Kivy-based mobile application for planning astrophotography sessions
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Add parent directory to path to import astronightplanner modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Import existing astropy modules
try:
    from astronightplanner import (
        filter_visible_objects, generate_observation_schedule,
        get_combined_catalog, find_astronomical_twilight,
        calculate_moon_phase, get_moon_phase_icon,
        DEFAULT_LOCATION, CONFIG, MIN_ALT, MAX_ALT
    )
#    from astroseasonplanner import analyze_trajectory_density  # Function not available
    from analysis import (
        calculate_object_score, find_best_objects,
        create_mosaic_groups, analyze_mosaic_compatibility
    )
    from models import SchedulingStrategy
    from astronomy import (
        get_local_timezone, calculate_altaz, find_visibility_window,
        calculate_visibility_duration, is_visible
    )
    Logger.info("AstroScope: Successfully imported astropy modules")
except ImportError as e:
    Logger.error(f"AstroScope: Failed to import astronightplanner modules: {e}")
    sys.exit(1)

# Import custom screens and widgets
from mobile_app.screens.home_screen import HomeScreen
from mobile_app.screens.targets_screen import TargetsScreen
from mobile_app.screens.target_detail_screen import TargetDetailScreen
from mobile_app.screens.mosaic_screen import MosaicScreen
from mobile_app.screens.settings_screen import SettingsScreen
from mobile_app.screens.reports_screen import ReportsScreen
from mobile_app.screens.session_planner_screen import SessionPlannerScreen
from mobile_app.screens.scope_selection_screen import ScopeSelectionScreen
from mobile_app.utils.app_state import AppState
from mobile_app.utils.location_manager import LocationManager

class AstroScopePlannerApp(App):
    """Main application class for AstroScope Planner"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "AstroScope Planner"
        self.icon = "assets/icon.png"
        
        # Initialize app state
        self.app_state = AppState()
        self.location_manager = LocationManager()
        
        # Initialize data storage
        self.store = JsonStore('astroscope_settings.json')
        
        # Load saved settings
        self.load_settings()
        
    def build(self):
        """Build the main application interface"""
        Logger.info("AstroScope: Building application interface")
        
        # Create screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Create and add screens
        self.home_screen = HomeScreen(name="home", app=self)
        self.targets_screen = TargetsScreen(name="targets", app=self)
        self.target_detail_screen = TargetDetailScreen(name="target_detail", app=self)
        self.mosaic_screen = MosaicScreen(name="mosaic", app=self)
        self.settings_screen = SettingsScreen(name="settings", app=self)
        self.reports_screen = ReportsScreen(name="reports")
        self.session_planner_screen = SessionPlannerScreen(name='session_planner')
        self.scope_selection_screen = ScopeSelectionScreen(name='scope_selection')
        
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.targets_screen)
        self.screen_manager.add_widget(self.target_detail_screen)
        self.screen_manager.add_widget(self.mosaic_screen)
        self.screen_manager.add_widget(self.settings_screen)
        self.screen_manager.add_widget(self.reports_screen)
        self.screen_manager.add_widget(self.session_planner_screen)
        self.screen_manager.add_widget(self.scope_selection_screen)
        
        # Set initial screen
        self.screen_manager.current = 'home'
        
        # Schedule initial data loading
        Clock.schedule_once(self.initialize_data, 0.1)
        
        return self.screen_manager
    
    def initialize_data(self, dt):
        """Initialize application data"""
        Logger.info("AstroScope: Initializing application data")
        
        try:
            # Load location
            self.location_manager.load_location(self.app_state)
            
            # Load tonight's targets
            self.load_tonights_targets()
            
            # Update home screen
            self.home_screen.update_display()
            
        except Exception as e:
            Logger.error(f"AstroScope: Error initializing data: {e}")
            self.show_error_popup("Initialization Error", str(e))
    
    def load_tonights_targets(self):
        """Load and filter tonight's best targets"""
        Logger.info("AstroScope: Loading tonight's targets")
        
        try:
            visible_objects = []; # Get current date and location
            current_date = datetime.now()
            location = self.app_state.current_location
            
            if not location:
                Logger.warning("AstroScope: No location set, using default")
                location = DEFAULT_LOCATION
            
            # Filter visible objects using existing astropy function
            # visible_objects = filter_visible_objects(
                # Temporary fix - use empty list
                visible_objects = []
            # Generate optimized schedule
            from datetime import timedelta; start_time = current_date; end_time = start_time + timedelta(hours=8); schedule = generate_observation_schedule(
                visible_objects, start_time, end_time,
                strategy=self.app_state.scheduling_strategy
            )
            
            # Store in app state
            self.app_state.tonights_targets = schedule[:20]  # Top 20 targets
            self.app_state.all_visible_objects = visible_objects
            
            Logger.info(f"AstroScope: Loaded {len(schedule)} targets for tonight")
            
        except Exception as e:
            Logger.error(f"AstroScope: Error loading targets: {e}")
            self.app_state.tonights_targets = []
            self.app_state.all_visible_objects = []
    
    def load_settings(self):
        """Load saved application settings"""
        try:
            if self.store.exists('location'):
                location_data = self.store.get('location')
                self.app_state.current_location = location_data
            
            if self.store.exists('preferences'):
                prefs = self.store.get('preferences')
                self.app_state.scheduling_strategy = prefs.get('strategy', 'max_objects')
                self.app_state.show_mosaic_only = prefs.get('mosaic_only', False)
                self.app_state.min_visibility_hours = prefs.get('min_visibility', 2.0)
            
        except Exception as e:
            Logger.error(f"AstroScope: Error loading settings: {e}")
    
    def save_settings(self):
        """Save current application settings"""
        try:
            if self.app_state.current_location:
                self.store.put('location', **self.app_state.current_location)
            
            preferences = {
                'strategy': self.app_state.scheduling_strategy,
                'mosaic_only': self.app_state.show_mosaic_only,
                'min_visibility': self.app_state.min_visibility_hours
            }
            # self.store.put("preferences", **preferences) # disabled
            
        except Exception as e:
            Logger.error(f"AstroScope: Error saving settings: {e}")
    
    def show_error_popup(self, title, message):
        """Show error popup to user"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        error_label = Label(
            text=message,
            text_size=(dp(300), None),
            halign='center',
            valign='middle'
        )
        content.add_widget(error_label)
        
        close_button = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        close_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def refresh_data(self):
        """Refresh all application data"""
        Logger.info("AstroScope: Refreshing application data")
        self.load_tonights_targets()
        
        # Update all screens
        if hasattr(self, 'home_screen'):
            self.home_screen.update_display()
        if hasattr(self, 'targets_screen'):
            self.targets_screen.update_targets_list()
    
    def on_stop(self):
        """Called when application is closing"""
        Logger.info("AstroScope: Application stopping")
        self.save_settings()
        return True

if __name__ == '__main__':
    # Configure Kivy settings
    from kivy.config import Config
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    Config.set('graphics', 'resizable', False)
    
    # Run the application
    AstroScopePlannerApp().run()