"""
Settings Screen
Configure app preferences, location, and telescope settings
"""

import os
import sys
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import theme and gesture managers
try:
    from utils.theme_manager import get_theme_manager, ThemedWidget
    from utils.gesture_manager import GestureManager, AstronomyGestures
except ImportError:
    # Fallback if modules not available
    get_theme_manager = lambda: None
    ThemedWidget = object
    GestureManager = None
    AstronomyGestures = None

class SettingsScreen(Screen, ThemedWidget):
    """Settings and configuration screen"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        # Initialize theme manager
        self.theme_manager = get_theme_manager()
        
        self.build_ui()
    
    def build_ui(self):
        """Build the settings screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Scrollable settings content
        scroll = ScrollView()
        self.settings_content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.settings_content.bind(minimum_height=self.settings_content.setter('height'))
        
        # Create settings sections
        self.create_settings_sections()
        
        scroll.add_widget(self.settings_content)
        main_layout.add_widget(scroll)
        
        # Action buttons
        actions = self.create_action_buttons()
        main_layout.add_widget(actions)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header with navigation and title"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Back button
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        # Title
        title = Label(
            text='Settings',
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Reset button
        reset_btn = Button(
            text='Reset',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.8, 0.4, 0.4, 1.0)
        )
        reset_btn.bind(on_press=self.reset_settings)
        header.add_widget(reset_btn)
        
        return header
    
    def create_settings_sections(self):
        """Create all settings sections"""
        # Theme Settings
        theme_section = self.create_theme_section()
        self.settings_content.add_widget(theme_section)
        
        # Gesture Settings
        gesture_section = self.create_gesture_section()
        self.settings_content.add_widget(gesture_section)
        
        # Location Settings
        location_section = self.create_location_section()
        self.settings_content.add_widget(location_section)
        
        # Observation Settings
        observation_section = self.create_observation_section()
        self.settings_content.add_widget(observation_section)
        
        # Telescope Settings
        telescope_section = self.create_telescope_section()
        self.settings_content.add_widget(telescope_section)
        
        # App Preferences
        preferences_section = self.create_preferences_section()
        self.settings_content.add_widget(preferences_section)
        
        # About Section
        about_section = self.create_about_section()
        self.settings_content.add_widget(about_section)
    
    def create_theme_section(self):
        """Create theme settings section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Theme Settings',
            size_hint_y=None,
            height=dp(200)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Theme selection
        if self.theme_manager:
            available_themes = self.theme_manager.get_available_themes()
            
            for theme_info in available_themes:
                theme_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10)
                )
                
                # Theme info
                info_layout = BoxLayout(orientation='vertical')
                
                name_label = Label(
                    text=theme_info['name'],
                    font_size='16sp',
                    bold=True,
                    halign='left',
                    size_hint_y=None,
                    height=dp(20)
                )
                name_label.bind(size=name_label.setter('text_size'))
                
                desc_label = Label(
                    text=theme_info['description'],
                    font_size='12sp',
                    halign='left',
                    size_hint_y=None,
                    height=dp(20)
                )
                desc_label.bind(size=desc_label.setter('text_size'))
                
                info_layout.add_widget(name_label)
                info_layout.add_widget(desc_label)
                
                # Selection button
                select_btn = Button(
                    text='Current' if theme_info['current'] else 'Select',
                    size_hint_x=None,
                    width=dp(80),
                    disabled=theme_info['current']
                )
                
                if not theme_info['current']:
                    select_btn.bind(on_press=lambda x, theme_id=theme_info['id']: self.select_theme(theme_id))
                
                theme_layout.add_widget(info_layout)
                theme_layout.add_widget(select_btn)
                content.add_widget(theme_layout)
        else:
            content.add_widget(Label(text='Theme manager not available'))
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(50)  # Collapsed height
        
        return accordion
    
    def create_gesture_section(self):
        """Create gesture settings section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Gesture Controls',
            size_hint_y=None,
            height=dp(150)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Enable gestures toggle
        gestures_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        gestures_label = Label(
            text='Enable Gesture Controls',
            font_size='16sp',
            halign='left'
        )
        gestures_label.bind(size=gestures_label.setter('text_size'))
        
        self.gestures_switch = Switch(
            active=True,  # Default enabled
            size_hint_x=None,
            width=dp(60)
        )
        self.gestures_switch.bind(active=self.on_gestures_toggle)
        
        gestures_row.add_widget(gestures_label)
        gestures_row.add_widget(self.gestures_switch)
        content.add_widget(gestures_row)
        
        # Gesture help button
        help_btn = Button(
            text='View Gesture Guide',
            size_hint_y=None,
            height=dp(35)
        )
        help_btn.bind(on_press=self.show_gesture_help)
        content.add_widget(help_btn)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(50)  # Collapsed height
        
        return accordion
    
    def create_location_section(self):
        """Create location settings section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Location Settings',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Current location display
        current_location = self.get_current_location_text()
        current_label = Label(
            text=f'Current: {current_location}',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        current_label.bind(size=current_label.setter('text_size'))
        content.add_widget(current_label)
        
        # Location selector
        location_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        location_label = Label(text='Location:', size_hint_x=None, width=dp(80))
        
        self.location_spinner = Spinner(
            text='Select Location',
            values=self.get_location_names(),
            size_hint_x=0.7
        )
        self.location_spinner.bind(text=self.on_location_change)
        
        gps_btn = Button(
            text='GPS',
            size_hint_x=None,
            width=dp(60),
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        gps_btn.bind(on_press=self.use_gps_location)
        
        location_layout.add_widget(location_label)
        location_layout.add_widget(self.location_spinner)
        location_layout.add_widget(gps_btn)
        content.add_widget(location_layout)
        
        # Manual coordinates
        coords_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(80))
        
        lat_label = Label(text='Latitude:')
        self.lat_input = TextInput(
            hint_text='45.516667',
            multiline=False,
            input_filter='float'
        )
        
        lon_label = Label(text='Longitude:')
        self.lon_input = TextInput(
            hint_text='9.216667',
            multiline=False,
            input_filter='float'
        )
        
        coords_layout.add_widget(lat_label)
        coords_layout.add_widget(self.lat_input)
        coords_layout.add_widget(lon_label)
        coords_layout.add_widget(self.lon_input)
        content.add_widget(coords_layout)
        
        # Add location button
        add_location_btn = Button(
            text='Add Custom Location',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        add_location_btn.bind(on_press=self.add_custom_location)
        content.add_widget(add_location_btn)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(220)
        
        return accordion
    
    def create_observation_section(self):
        """Create observation settings section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Observation Settings',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Scheduling strategy
        strategy_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        strategy_label = Label(text='Strategy:', size_hint_x=None, width=dp(80))
        
        self.strategy_spinner = Spinner(
            text='Maximum Objects',
            values=[
                'Longest Duration',
                'Maximum Objects',
                'Optimal SNR',
                'Minimal Mosaic',
                'Balanced Difficulty',
                'Mosaic Groups'
            ]
        )
        self.strategy_spinner.bind(text=self.on_strategy_change)
        
        strategy_layout.add_widget(strategy_label)
        strategy_layout.add_widget(self.strategy_spinner)
        content.add_widget(strategy_layout)
        
        # Altitude limits
        alt_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        alt_title = Label(text='Altitude Limits:', size_hint_y=None, height=dp(20), halign='left')
        alt_title.bind(size=alt_title.setter('text_size'))
        
        min_alt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        min_alt_label = Label(text='Min:', size_hint_x=None, width=dp(50))
        self.min_alt_slider = Slider(min=0, max=45, value=15, step=5)
        self.min_alt_value = Label(text='15°', size_hint_x=None, width=dp(50))
        self.min_alt_slider.bind(value=self.on_min_alt_change)
        
        min_alt_layout.add_widget(min_alt_label)
        min_alt_layout.add_widget(self.min_alt_slider)
        min_alt_layout.add_widget(self.min_alt_value)
        
        max_alt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        max_alt_label = Label(text='Max:', size_hint_x=None, width=dp(50))
        self.max_alt_slider = Slider(min=45, max=90, value=75, step=5)
        self.max_alt_value = Label(text='75°', size_hint_x=None, width=dp(50))
        self.max_alt_slider.bind(value=self.on_max_alt_change)
        
        max_alt_layout.add_widget(max_alt_label)
        max_alt_layout.add_widget(self.max_alt_slider)
        max_alt_layout.add_widget(self.max_alt_value)
        
        alt_layout.add_widget(alt_title)
        alt_layout.add_widget(min_alt_layout)
        alt_layout.add_widget(max_alt_layout)
        content.add_widget(alt_layout)
        
        # Minimum visibility hours
        visibility_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        visibility_label = Label(text='Min Visibility:', size_hint_x=None, width=dp(100))
        self.visibility_slider = Slider(min=0.5, max=8.0, value=2.0, step=0.5)
        self.visibility_value = Label(text='2.0h', size_hint_x=None, width=dp(60))
        self.visibility_slider.bind(value=self.on_visibility_change)
        
        visibility_layout.add_widget(visibility_label)
        visibility_layout.add_widget(self.visibility_slider)
        visibility_layout.add_widget(self.visibility_value)
        content.add_widget(visibility_layout)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(170)
        
        return accordion
    
    def create_telescope_section(self):
        """Create telescope settings section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Telescope Settings',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Telescope name
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        name_label = Label(text='Telescope:', size_hint_x=None, width=dp(80))
        self.telescope_input = TextInput(
            text='Vaonis Vespera Passenger',
            multiline=False
        )
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.telescope_input)
        content.add_widget(name_layout)
        
        # Field of view
        fov_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(80))
        
        fov_w_label = Label(text='FOV Width (°):')
        self.fov_w_input = TextInput(
            text='2.4',
            multiline=False,
            input_filter='float'
        )
        
        fov_h_label = Label(text='FOV Height (°):')
        self.fov_h_input = TextInput(
            text='1.8',
            multiline=False,
            input_filter='float'
        )
        
        fov_layout.add_widget(fov_w_label)
        fov_layout.add_widget(self.fov_w_input)
        fov_layout.add_widget(fov_h_label)
        fov_layout.add_widget(self.fov_h_input)
        content.add_widget(fov_layout)
        
        # Mosaic capabilities
        mosaic_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        mosaic_label = Label(text='Mosaic Capable:', size_hint_x=None, width=dp(120))
        self.mosaic_switch = Switch(active=True)
        mosaic_layout.add_widget(mosaic_label)
        mosaic_layout.add_widget(self.mosaic_switch)
        content.add_widget(mosaic_layout)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(170)
        
        return accordion
    
    def create_preferences_section(self):
        """Create app preferences section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='App Preferences',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Show mosaic only
        mosaic_only_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        mosaic_only_label = Label(text='Show Mosaic Only:', size_hint_x=None, width=dp(150))
        self.mosaic_only_switch = Switch(active=False)
        mosaic_only_layout.add_widget(mosaic_only_label)
        mosaic_only_layout.add_widget(self.mosaic_only_switch)
        content.add_widget(mosaic_only_layout)
        
        # Auto-refresh
        refresh_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        refresh_label = Label(text='Auto-refresh Data:', size_hint_x=None, width=dp(150))
        self.refresh_switch = Switch(active=True)
        refresh_layout.add_widget(refresh_label)
        refresh_layout.add_widget(self.refresh_switch)
        content.add_widget(refresh_layout)
        
        # Dark mode
        dark_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        dark_label = Label(text='Dark Mode:', size_hint_x=None, width=dp(150))
        self.dark_switch = Switch(active=False)
        dark_layout.add_widget(dark_label)
        dark_layout.add_widget(self.dark_switch)
        content.add_widget(dark_layout)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(130)
        
        return accordion
    
    def create_about_section(self):
        """Create about section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='About',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # App info
        app_info = (
            "AstroScope Planner v1.0\n"
            "Mobile Astrophotography Planning\n\n"
            "Built with Kivy and integrates the\n"
            "powerful astropy calculation engine.\n\n"
            "© 2024 AstroScope Project"
        )
        
        info_label = Label(
            text=app_info,
            text_size=(dp(300), None),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(120)
        )
        content.add_widget(info_label)
        
        # Links
        links_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        help_btn = Button(
            text='Help',
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        help_btn.bind(on_press=self.show_help)
        
        feedback_btn = Button(
            text='Feedback',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        feedback_btn.bind(on_press=self.show_feedback)
        
        links_layout.add_widget(help_btn)
        links_layout.add_widget(feedback_btn)
        content.add_widget(links_layout)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(170)
        
        return accordion
    
    def create_action_buttons(self):
        """Create action buttons at bottom"""
        actions = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Save button
        save_btn = Button(
            text='Save Settings',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        save_btn.bind(on_press=self.save_settings)
        
        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            background_color=(0.6, 0.6, 0.6, 1.0)
        )
        cancel_btn.bind(on_press=self.cancel_changes)
        
        actions.add_widget(save_btn)
        actions.add_widget(cancel_btn)
        
        return actions
    
    def load_current_settings(self):
        """Load current settings into UI controls"""
        try:
            if not self.app or not self.app.app_state:
                return
            
            app_state = self.app.app_state
            
            # Load location
            if app_state.current_location:
                location = app_state.current_location
                self.lat_input.text = str(location.get('latitude', ''))
                self.lon_input.text = str(location.get('longitude', ''))
                
                # Set location spinner
                location_name = location.get('name', 'Custom')
                if location_name in self.location_spinner.values:
                    self.location_spinner.text = location_name
            
            # Load strategy
            strategy_display = app_state.get_strategy_display_name(app_state.scheduling_strategy)
            if strategy_display in self.strategy_spinner.values:
                self.strategy_spinner.text = strategy_display
            
            # Load preferences
            self.mosaic_only_switch.active = app_state.show_mosaic_only
            self.visibility_slider.value = app_state.min_visibility_hours
            self.visibility_value.text = f'{app_state.min_visibility_hours:.1f}h'
            
            # Load telescope settings from config
            if hasattr(self.app, 'CONFIG') and 'imaging' in self.app.CONFIG:
                scope = self.app.CONFIG['imaging'].get('scope', {})
                self.telescope_input.text = scope.get('name', 'Unknown Telescope')
                self.fov_w_input.text = str(scope.get('fov_width', '2.4'))
                self.fov_h_input.text = str(scope.get('fov_height', '1.8'))
            
        except Exception as e:
            Logger.error(f"SettingsScreen: Error loading settings: {e}")
    
    def get_current_location_text(self):
        """Get current location display text"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                name = location.get('name', 'Custom')
                lat = location.get('latitude', 0)
                lon = location.get('longitude', 0)
                return f"{name} ({lat:.3f}, {lon:.3f})"
            return "No location set"
        except:
            return "Error loading location"
    
    def get_location_names(self):
        """Get list of available location names"""
        try:
            if self.app and self.app.location_manager:
                names = self.app.location_manager.get_location_names()
                names.append('Custom')
                return names
            return ['Custom']
        except:
            return ['Custom']
    
    # Event handlers
    def on_location_change(self, instance, text):
        """Handle location selection change"""
        try:
            if text != 'Custom' and self.app and self.app.location_manager:
                location = self.app.location_manager.get_location_by_name(text)
                if location:
                    self.lat_input.text = str(location['latitude'])
                    self.lon_input.text = str(location['longitude'])
        except Exception as e:
            Logger.error(f"SettingsScreen: Error changing location: {e}")
    
    def on_strategy_change(self, instance, text):
        """Handle strategy change"""
        Logger.info(f"SettingsScreen: Strategy changed to {text}")
    
    def on_min_alt_change(self, instance, value):
        """Handle minimum altitude change"""
        self.min_alt_value.text = f'{int(value)}°'
    
    def on_max_alt_change(self, instance, value):
        """Handle maximum altitude change"""
        self.max_alt_value.text = f'{int(value)}°'
    
    def on_visibility_change(self, instance, value):
        """Handle visibility hours change"""
        self.visibility_value.text = f'{value:.1f}h'
    
    def use_gps_location(self, instance):
        """Use GPS location"""
        try:
            if self.app and self.app.location_manager:
                gps_location = self.app.location_manager.get_current_location()
                if gps_location:
                    self.lat_input.text = str(gps_location['latitude'])
                    self.lon_input.text = str(gps_location['longitude'])
                    Logger.info("SettingsScreen: GPS location loaded")
                else:
                    self.show_message("GPS Error", "GPS location not available")
            else:
                self.show_message("GPS Error", "GPS functionality not available")
        except Exception as e:
            Logger.error(f"SettingsScreen: GPS error: {e}")
            self.show_message("GPS Error", str(e))
    
    def add_custom_location(self, instance):
        """Add custom location"""
        try:
            lat_text = self.lat_input.text.strip()
            lon_text = self.lon_input.text.strip()
            
            if not lat_text or not lon_text:
                self.show_message("Input Error", "Please enter both latitude and longitude")
                return
            
            if self.app and self.app.location_manager:
                valid, message, lat, lon = self.app.location_manager.validate_coordinates(lat_text, lon_text)
                
                if not valid:
                    self.show_message("Validation Error", message)
                    return
                
                # Show dialog to enter location name
                self.show_add_location_dialog(lat, lon)
            
        except Exception as e:
            Logger.error(f"SettingsScreen: Error adding location: {e}")
            self.show_message("Error", str(e))
    
    def show_add_location_dialog(self, lat, lon):
        """Show dialog to name and add location"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        content.add_widget(Label(text='Enter location name:', size_hint_y=None, height=dp(30)))
        
        name_input = TextInput(
            hint_text='My Observatory',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(name_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        add_btn = Button(text='Add')
        cancel_btn = Button(text='Cancel')
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Add Location',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        def add_location(instance):
            name = name_input.text.strip()
            if name:
                if self.app.location_manager.add_location(name, lat, lon):
                    self.location_spinner.values = self.get_location_names()
                    self.location_spinner.text = name
                    popup.dismiss()
                    self.show_message("Success", f"Location '{name}' added successfully")
                else:
                    self.show_message("Error", "Failed to add location")
            else:
                self.show_message("Error", "Please enter a location name")
        
        add_btn.bind(on_press=add_location)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def save_settings(self, instance):
        """Save all settings"""
        try:
            if not self.app:
                return
            
            # Save location
            lat_text = self.lat_input.text.strip()
            lon_text = self.lon_input.text.strip()
            
            if lat_text and lon_text:
                try:
                    lat = float(lat_text)
                    lon = float(lon_text)
                    
                    location_name = self.location_spinner.text
                    if location_name == 'Custom':
                        location_name = 'Custom Location'
                    
                    self.app.app_state.current_location = {
                        'name': location_name,
                        'latitude': lat,
                        'longitude': lon,
                        'min_altitude': int(self.min_alt_slider.value),
                        'max_altitude': int(self.max_alt_slider.value)
                    }
                except ValueError:
                    self.show_message("Error", "Invalid coordinates")
                    return
            
            # Save strategy
            strategy_map = {
                'Longest Duration': 'longest_duration',
                'Maximum Objects': 'max_objects',
                'Optimal SNR': 'optimal_snr',
                'Minimal Mosaic': 'minimal_mosaic',
                'Balanced Difficulty': 'difficulty_balanced',
                'Mosaic Groups': 'mosaic_groups'
            }
            
            strategy_display = self.strategy_spinner.text
            if strategy_display in strategy_map:
                self.app.app_state.scheduling_strategy = strategy_map[strategy_display]
            
            # Save preferences
            self.app.app_state.show_mosaic_only = self.mosaic_only_switch.active
            self.app.app_state.min_visibility_hours = self.visibility_slider.value
            
            # Save to persistent storage
            self.app.save_settings()
            
            # Refresh data with new settings
            self.app.refresh_data()
            
            self.show_message("Success", "Settings saved successfully")
            Logger.info("SettingsScreen: Settings saved")
            
        except Exception as e:
            Logger.error(f"SettingsScreen: Error saving settings: {e}")
            self.show_message("Error", f"Failed to save settings: {str(e)}")
    
    def cancel_changes(self, instance):
        """Cancel changes and go back"""
        self.go_back(instance)
    
    def reset_settings(self, instance):
        """Reset all settings to defaults"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        content.add_widget(Label(
            text='Reset all settings to defaults?\nThis cannot be undone.',
            text_size=(dp(250), None),
            halign='center',
            size_hint_y=None,
            height=dp(60)
        ))
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        reset_btn = Button(text='Reset', background_color=(0.8, 0.2, 0.2, 1.0))
        cancel_btn = Button(text='Cancel')
        
        buttons_layout.add_widget(reset_btn)
        buttons_layout.add_widget(cancel_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Reset Settings',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        def do_reset(instance):
            try:
                # Reset to defaults
                if self.app and self.app.location_manager:
                    default_location = self.app.location_manager.get_default_location()
                    if default_location:
                        self.app.app_state.current_location = default_location
                
                self.app.app_state.scheduling_strategy = 'max_objects'
                self.app.app_state.show_mosaic_only = False
                self.app.app_state.min_visibility_hours = 2.0
                
                # Reload UI
                self.load_current_settings()
                
                popup.dismiss()
                self.show_message("Success", "Settings reset to defaults")
                
            except Exception as e:
                Logger.error(f"SettingsScreen: Error resetting settings: {e}")
                self.show_message("Error", f"Failed to reset settings: {str(e)}")
        
        reset_btn.bind(on_press=do_reset)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def show_help(self, instance):
        """Show help information"""
        help_text = (
            "AstroScope Planner Help\n\n"
            "• Set your observing location in Location Settings\n"
            "• Choose a scheduling strategy for target selection\n"
            "• Adjust altitude limits based on your horizon\n"
            "• Configure your telescope's field of view\n"
            "• Use mosaic planning for large objects\n\n"
            "For more help, visit the documentation."
        )
        
        self.show_message("Help", help_text)
    
    def show_feedback(self, instance):
        """Show feedback information"""
        feedback_text = (
            "We'd love your feedback!\n\n"
            "Please report bugs, suggest features,\n"
            "or share your experience using\n"
            "AstroScope Planner.\n\n"
            "Contact: feedback@astroscope.app"
        )
        
        self.show_message("Feedback", feedback_text)
    
    def show_message(self, title, message):
        """Show a message popup"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        message_label = Label(
            text=message,
            text_size=(dp(300), None),
            halign='center',
            valign='middle'
        )
        content.add_widget(message_label)
        
        close_btn = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def select_theme(self, theme_id):
        """Select a theme"""
        if self.theme_manager:
            success = self.theme_manager.set_theme(theme_id)
            if success:
                Logger.info(f"SettingsScreen: Changed theme to {theme_id}")
                # Rebuild UI to reflect theme change
                self.clear_widgets()
                self.build_ui()
            else:
                Logger.error(f"SettingsScreen: Failed to change theme to {theme_id}")
    
    def on_gestures_toggle(self, instance, active):
        """Handle gesture toggle"""
        Logger.info(f"SettingsScreen: Gestures {'enabled' if active else 'disabled'}")
        # TODO: Implement gesture enable/disable in app state
    
    def show_gesture_help(self, instance):
        """Show gesture help popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        help_text = """Gesture Controls:

Target Cards:
• Swipe right: Add to plan
• Swipe left: Remove from plan
• Long press: View details
• Double tap: Toggle planned status

Navigation:
• Swipe up: Scroll to top
• Swipe down: Refresh
• Double tap: Quick filter toggle

General:
• Pinch: Zoom (where applicable)
• Two-finger tap: Context menu"""
        
        help_label = Label(
            text=help_text,
            text_size=(dp(300), None),
            halign='left',
            valign='top'
        )
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        
        content.add_widget(help_label)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Gesture Guide',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        """Navigate back to home screen"""
        if self.app:
            self.app.screen_manager.current = 'home'
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_current_settings()