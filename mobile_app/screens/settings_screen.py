"""
Settings Screen
Configuration screen for location, visibility constraints, and app preferences
"""

import os
import sys
from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.logger import Logger
from mobile_app.utils.app_logger import log_error, log_warning, log_debug, log_info

class SettingsScreen(Screen):
    """Settings and configuration screen"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()
    
    def build_ui(self):
        """Build the settings screen UI"""
        # Use ScrollView for content that might overflow
        scroll = ScrollView()
        
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=dp(15), 
            spacing=dp(15),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Location Settings
        location_section = self.create_location_section()
        main_layout.add_widget(location_section)
        
        # Visibility Constraints
        visibility_section = self.create_visibility_section()
        main_layout.add_widget(visibility_section)
        
        # App Preferences
        preferences_section = self.create_preferences_section()
        main_layout.add_widget(preferences_section)
        
        # Action Buttons
        actions = self.create_action_buttons()
        main_layout.add_widget(actions)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def create_header(self):
        """Create header with title and back button"""
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
        title_label = Label(
            text='Settings',
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        header.add_widget(title_label)
        
        # Spacer for symmetry
        spacer = Label(size_hint_x=None, width=dp(80))
        header.add_widget(spacer)
        
        return header
    
    def create_location_section(self):
        """Create location settings section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=dp(10)
        )
        
        # Section title
        title = Label(
            text='Location Settings',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Location input grid
        location_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Latitude
        location_grid.add_widget(Label(text='Latitude:', halign='right'))
        self.latitude_input = TextInput(
            text=self.get_current_latitude(),
            multiline=False,
            size_hint_y=None,
            height=dp(30)
        )
        location_grid.add_widget(self.latitude_input)
        
        # Longitude
        location_grid.add_widget(Label(text='Longitude:', halign='right'))
        self.longitude_input = TextInput(
            text=self.get_current_longitude(),
            multiline=False,
            size_hint_y=None,
            height=dp(30)
        )
        location_grid.add_widget(self.longitude_input)
        
        # Location name
        location_grid.add_widget(Label(text='Location Name:', halign='right'))
        self.location_name_input = TextInput(
            text=self.get_current_location_name(),
            multiline=False,
            size_hint_y=None,
            height=dp(30)
        )
        location_grid.add_widget(self.location_name_input)
        
        section.add_widget(location_grid)
        
        # Preset locations button
        preset_btn = Button(
            text='Use Preset Location',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.4, 0.4, 0.8, 1.0)
        )
        preset_btn.bind(on_press=self.show_preset_locations)
        section.add_widget(preset_btn)
        
        return section
    
    def create_visibility_section(self):
        """Create visibility constraints section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(250),
            spacing=dp(10)
        )
        
        # Section title
        title = Label(
            text='Visibility Constraints',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Minimum altitude
        min_alt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        min_alt_layout.add_widget(Label(text='Min Altitude:', size_hint_x=None, width=dp(120)))
        
        self.min_altitude_slider = Slider(
            min=0, max=60, value=self.get_current_min_altitude(), step=5
        )
        self.min_altitude_slider.bind(value=self.update_min_altitude_label)
        min_alt_layout.add_widget(self.min_altitude_slider)
        
        self.min_altitude_label = Label(
            text=f'{int(self.min_altitude_slider.value)}°',
            size_hint_x=None,
            width=dp(50)
        )
        min_alt_layout.add_widget(self.min_altitude_label)
        section.add_widget(min_alt_layout)
        
        # Minimum visibility hours
        min_vis_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        min_vis_layout.add_widget(Label(text='Min Visibility:', size_hint_x=None, width=dp(120)))
        
        self.min_visibility_slider = Slider(
            min=0.5, max=8.0, value=self.get_current_min_visibility(), step=0.5
        )
        self.min_visibility_slider.bind(value=self.update_min_visibility_label)
        min_vis_layout.add_widget(self.min_visibility_slider)
        
        self.min_visibility_label = Label(
            text=f'{self.min_visibility_slider.value:.1f}h',
            size_hint_x=None,
            width=dp(50)
        )
        min_vis_layout.add_widget(self.min_visibility_label)
        section.add_widget(min_vis_layout)
        
        # Maximum moon illumination
        moon_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        moon_layout.add_widget(Label(text='Max Moon:', size_hint_x=None, width=dp(120)))
        
        self.max_moon_slider = Slider(
            min=0, max=100, value=self.get_current_max_moon(), step=10
        )
        self.max_moon_slider.bind(value=self.update_max_moon_label)
        moon_layout.add_widget(self.max_moon_slider)
        
        self.max_moon_label = Label(
            text=f'{int(self.max_moon_slider.value)}%',
            size_hint_x=None,
            width=dp(50)
        )
        moon_layout.add_widget(self.max_moon_label)
        section.add_widget(moon_layout)
        
        # Advanced constraints toggle
        advanced_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        advanced_layout.add_widget(Label(text='Advanced Filtering:', size_hint_x=None, width=dp(150)))
        
        self.advanced_switch = Switch(active=self.get_current_advanced_filtering())
        advanced_layout.add_widget(self.advanced_switch)
        section.add_widget(advanced_layout)
        
        return section
    
    def create_preferences_section(self):
        """Create app preferences section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            spacing=dp(10)
        )
        
        # Section title
        title = Label(
            text='App Preferences',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Auto-refresh interval
        refresh_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        refresh_layout.add_widget(Label(text='Auto-refresh:', size_hint_x=None, width=dp(120)))
        
        self.refresh_slider = Slider(
            min=5, max=60, value=self.get_current_refresh_interval(), step=5
        )
        self.refresh_slider.bind(value=self.update_refresh_label)
        refresh_layout.add_widget(self.refresh_slider)
        
        self.refresh_label = Label(
            text=f'{int(self.refresh_slider.value)}min',
            size_hint_x=None,
            width=dp(60)
        )
        refresh_layout.add_widget(self.refresh_label)
        section.add_widget(refresh_layout)
        
        # Theme selection (placeholder)
        theme_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        theme_layout.add_widget(Label(text='Dark Theme:', size_hint_x=None, width=dp(120)))
        
        self.theme_switch = Switch(active=True)  # Default to dark theme
        theme_layout.add_widget(self.theme_switch)
        section.add_widget(theme_layout)
        
        # Enable logging
        logging_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        logging_layout.add_widget(Label(text='Enable Logging:', size_hint_x=None, width=dp(120)))
        
        self.logging_switch = Switch(active=True)
        logging_layout.add_widget(self.logging_switch)
        section.add_widget(logging_layout)
        
        return section
    
    def create_action_buttons(self):
        """Create action buttons"""
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
        
        # Reset button
        reset_btn = Button(
            text='Reset to Defaults',
            background_color=(0.8, 0.4, 0.2, 1.0)
        )
        reset_btn.bind(on_press=self.reset_to_defaults)
        
        # Export button
        export_btn = Button(
            text='Export Settings',
            background_color=(0.4, 0.4, 0.8, 1.0)
        )
        export_btn.bind(on_press=self.export_settings)
        
        actions.add_widget(save_btn)
        actions.add_widget(reset_btn)
        actions.add_widget(export_btn)
        
        return actions
    
    # Helper methods for getting current values
    def get_current_latitude(self):
        """Get current latitude setting"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                lat = location.get('latitude', location.get('lat', 40.0))
                return str(float(lat))
        except Exception:
            pass
        return "40.0"  # Default to NYC
    
    def get_current_longitude(self):
        """Get current longitude setting"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                lon = location.get('longitude', location.get('lon', -74.0))
                return str(float(lon))
        except Exception:
            pass
        return "-74.0"  # Default to NYC
    
    def get_current_location_name(self):
        """Get current location name"""
        try:
            if self.app and self.app.app_state.current_location:
                return self.app.app_state.current_location.get('name', 'New York City')
        except Exception:
            pass
        return "New York City"
    
    def get_current_min_altitude(self):
        """Get current minimum altitude constraint"""
        return 30.0  # Default
    
    def get_current_min_visibility(self):
        """Get current minimum visibility hours"""
        try:
            if self.app and hasattr(self.app.app_state, 'min_visibility_hours'):
                return float(self.app.app_state.min_visibility_hours)
        except Exception:
            pass
        return 2.0
    
    def get_current_max_moon(self):
        """Get current maximum moon illumination"""
        return 50.0  # Default 50%
    
    def get_current_advanced_filtering(self):
        """Get current advanced filtering state"""
        try:
            if self.app and self.app.app_state.advanced_filter:
                return self.app.app_state.advanced_filter.enabled
        except Exception:
            pass
        return False
    
    def get_current_refresh_interval(self):
        """Get current auto-refresh interval"""
        return 15.0  # Default 15 minutes
    
    # Update label methods
    def update_min_altitude_label(self, instance, value):
        """Update minimum altitude label"""
        self.min_altitude_label.text = f'{int(value)}°'
    
    def update_min_visibility_label(self, instance, value):
        """Update minimum visibility label"""
        self.min_visibility_label.text = f'{value:.1f}h'
    
    def update_max_moon_label(self, instance, value):
        """Update maximum moon label"""
        self.max_moon_label.text = f'{int(value)}%'
    
    def update_refresh_label(self, instance, value):
        """Update refresh interval label"""
        self.refresh_label.text = f'{int(value)}min'
    
    # Action methods
    def save_settings(self, instance):
        """Save all settings"""
        try:
            log_info("Saving settings...")
            
            if not self.app or not self.app.app_state:
                log_error("No app state available for saving settings")
                return
            
            # Save location
            try:
                lat = float(self.latitude_input.text)
                lon = float(self.longitude_input.text)
                name = self.location_name_input.text or "Custom Location"
                
                self.app.app_state.current_location = {
                    'name': name,
                    'latitude': lat,
                    'longitude': lon
                }
                log_info(f"Location saved: {name} ({lat}, {lon})")
            except ValueError:
                log_error("Invalid latitude/longitude values")
                self.show_error_popup("Invalid location coordinates")
                return
            
            # Save visibility constraints
            self.app.app_state.min_visibility_hours = self.min_visibility_slider.value
            
            # Save app preferences
            # (These would be saved to app config/preferences)
            
            # Trigger app refresh with new settings
            if hasattr(self.app, 'refresh_data'):
                self.app.refresh_data()
            
            # Update home screen
            if hasattr(self.app, 'update_home_screen'):
                self.app.update_home_screen()
            
            self.show_success_popup("Settings saved successfully!")
            log_info("Settings saved successfully")
            
        except Exception as e:
            log_error(f"Error saving settings", e)
            self.show_error_popup(f"Error saving settings: {str(e)}")
    
    def reset_to_defaults(self, instance):
        """Reset all settings to defaults"""
        try:
            # Reset location to NYC
            self.latitude_input.text = "40.0"
            self.longitude_input.text = "-74.0"
            self.location_name_input.text = "New York City"
            
            # Reset visibility constraints
            self.min_altitude_slider.value = 30.0
            self.min_visibility_slider.value = 2.0
            self.max_moon_slider.value = 50.0
            self.advanced_switch.active = False
            
            # Reset preferences
            self.refresh_slider.value = 15.0
            self.theme_switch.active = True
            self.logging_switch.active = True
            
            log_info("Settings reset to defaults")
            
        except Exception as e:
            log_error(f"Error resetting settings", e)
    
    def export_settings(self, instance):
        """Export current settings"""
        try:
            settings_data = {
                'location': {
                    'name': self.location_name_input.text,
                    'latitude': float(self.latitude_input.text),
                    'longitude': float(self.longitude_input.text)
                },
                'visibility': {
                    'min_altitude': self.min_altitude_slider.value,
                    'min_visibility_hours': self.min_visibility_slider.value,
                    'max_moon_illumination': self.max_moon_slider.value,
                    'advanced_filtering': self.advanced_switch.active
                },
                'preferences': {
                    'refresh_interval': self.refresh_slider.value,
                    'dark_theme': self.theme_switch.active,
                    'logging_enabled': self.logging_switch.active
                },
                'export_date': datetime.now().isoformat()
            }
            
            # For now, just log the export (could save to file later)
            log_info(f"Settings exported: {settings_data}")
            self.show_success_popup("Settings exported to log!")
            
        except Exception as e:
            log_error(f"Error exporting settings", e)
            self.show_error_popup(f"Export failed: {str(e)}")
    
    def show_preset_locations(self, instance):
        """Show preset location selection popup"""
        preset_locations = [
            {"name": "New York City", "lat": 40.7128, "lon": -74.0060},
            {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
            {"name": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
            {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
            {"name": "Paris", "lat": 48.8566, "lon": 2.3522}
        ]
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        for location in preset_locations:
            btn = Button(
                text=f"{location['name']} ({location['lat']:.2f}, {location['lon']:.2f})",
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_press=lambda x, loc=location: self.select_preset_location(loc))
            content.add_widget(btn)
        
        popup = Popup(
            title='Select Preset Location',
            content=content,
            size_hint=(0.8, 0.6)
        )
        popup.open()
        self.preset_popup = popup
    
    def select_preset_location(self, location):
        """Select a preset location"""
        self.latitude_input.text = str(location['lat'])
        self.longitude_input.text = str(location['lon'])
        self.location_name_input.text = location['name']
        
        if hasattr(self, 'preset_popup'):
            self.preset_popup.dismiss()
        
        log_info(f"Selected preset location: {location['name']}")
    
    def show_success_popup(self, message):
        """Show success message popup"""
        content = Label(text=message)
        popup = Popup(
            title='Success',
            content=content,
            size_hint=(0.6, 0.4)
        )
        popup.open()
    
    def show_error_popup(self, message):
        """Show error message popup"""
        content = Label(text=message)
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.6, 0.4)
        )
        popup.open()
    
    def go_back(self, instance):
        """Navigate back to home screen"""
        if self.app:
            self.app.screen_manager.current = 'home'
    
    def on_enter(self):
        """Called when screen is entered"""
        # Refresh current values when entering settings
        pass