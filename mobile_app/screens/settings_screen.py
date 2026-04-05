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
from kivy.uix.spinner import Spinner

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
            height=dp(370),  # Increased to accommodate new settings
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
        
        # Create slider with safe initialization
        try:
            min_alt_value = float(self.get_current_min_altitude())
        except (ValueError, TypeError):
            min_alt_value = 30.0
            
        self.min_altitude_slider = Slider(
            min=0, max=60, value=min_alt_value, step=5
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
        
        # Maximum altitude
        max_alt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        max_alt_layout.add_widget(Label(text='Max Altitude:', size_hint_x=None, width=dp(120)))
        
        # Create slider with safe initialization
        try:
            max_alt_value = float(self.get_current_max_altitude())
        except (ValueError, TypeError):
            max_alt_value = 85.0
            
        self.max_altitude_slider = Slider(
            min=60, max=90, value=max_alt_value, step=5
        )
        self.max_altitude_slider.bind(value=self.update_max_altitude_label)
        max_alt_layout.add_widget(self.max_altitude_slider)
        
        self.max_altitude_label = Label(
            text=f'{int(self.max_altitude_slider.value)}°',
            size_hint_x=None,
            width=dp(50)
        )
        max_alt_layout.add_widget(self.max_altitude_label)
        section.add_widget(max_alt_layout)
        
        # Azimuth range (optional - can be disabled for most users)
        azimuth_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        azimuth_layout.add_widget(Label(text='Azimuth Range:', size_hint_x=None, width=dp(120)))
        
        self.azimuth_range_label = Label(
            text=f'{int(self.get_current_min_azimuth())}° - {int(self.get_current_max_azimuth())}°',
            size_hint_x=0.7
        )
        azimuth_layout.add_widget(self.azimuth_range_label)
        
        azimuth_btn = Button(
            text='Edit',
            size_hint_x=None,
            width=dp(60),
            background_color=(0.4, 0.4, 0.8, 1.0)
        )
        azimuth_btn.bind(on_press=self.show_azimuth_editor)
        azimuth_layout.add_widget(azimuth_btn)
        section.add_widget(azimuth_layout)
        
        # Minimum visibility hours
        min_vis_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        min_vis_layout.add_widget(Label(text='Min Visibility:', size_hint_x=None, width=dp(120)))
        
        # Create slider with safe initialization
        try:
            min_vis_value = float(self.get_current_min_visibility())
        except (ValueError, TypeError):
            min_vis_value = 2.0
            
        self.min_visibility_slider = Slider(
            min=0.5, max=8.0, value=min_vis_value, step=0.5
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
        
        # Create slider with safe initialization
        try:
            max_moon_value = float(self.get_current_max_moon())
        except (ValueError, TypeError):
            max_moon_value = 50.0
            
        self.max_moon_slider = Slider(
            min=0, max=100, value=max_moon_value, step=10
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
        
        # Exclude insufficient time objects
        exclude_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        exclude_layout.add_widget(Label(text='Exclude Insufficient Time:', size_hint_x=None, width=dp(180)))
        
        # Create toggle button instead of Switch to avoid Kivy BooleanProperty issues
        self.exclude_insufficient_state = self.get_current_exclude_insufficient()
        self.exclude_insufficient_button = Button(
            text='ON' if self.exclude_insufficient_state else 'OFF',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.8, 0.2, 1.0) if self.exclude_insufficient_state else (0.8, 0.2, 0.2, 1.0)
        )
        self.exclude_insufficient_button.bind(on_press=self.toggle_exclude_insufficient)
        exclude_layout.add_widget(self.exclude_insufficient_button)
        section.add_widget(exclude_layout)
        
        # Advanced constraints toggle
        advanced_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        advanced_layout.add_widget(Label(text='Advanced Filtering:', size_hint_x=None, width=dp(150)))
        
        # Create toggle button instead of Switch to avoid Kivy BooleanProperty issues
        self.advanced_filtering_state = self.get_current_advanced_filtering()
        self.advanced_button = Button(
            text='ON' if self.advanced_filtering_state else 'OFF',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.8, 0.2, 1.0) if self.advanced_filtering_state else (0.8, 0.2, 0.2, 1.0)
        )
        self.advanced_button.bind(on_press=self.toggle_advanced_filtering)
        advanced_layout.add_widget(self.advanced_button)
        section.add_widget(advanced_layout)
        
        return section
    
    def create_preferences_section(self):
        """Create app preferences section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),  # Increased height to accommodate twilight selector
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
        
        # Twilight Type Selector - NEW FEATURE
        twilight_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        twilight_layout.add_widget(Label(text='Twilight Type:', size_hint_x=None, width=dp(120)))
        
        self.twilight_spinner = Spinner(
            text=self.get_current_twilight_type(),
            values=['Civil (-6°)', 'Nautical (-12°)', 'Astronomical (-18°)'],
            size_hint_x=0.7,
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        twilight_layout.add_widget(self.twilight_spinner)
        
        # Info button for twilight explanation
        twilight_info_btn = Button(
            text='?',
            size_hint_x=None,
            width=dp(30),
            background_color=(0.4, 0.4, 0.8, 1.0)
        )
        twilight_info_btn.bind(on_press=self.show_twilight_info)
        twilight_layout.add_widget(twilight_info_btn)
        
        section.add_widget(twilight_layout)
        
        # Auto-refresh interval
        refresh_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        refresh_layout.add_widget(Label(text='Auto-refresh:', size_hint_x=None, width=dp(120)))
        
        # Create slider with safe initialization
        try:
            refresh_value = float(self.get_current_refresh_interval())
        except (ValueError, TypeError):
            refresh_value = 15.0
            
        self.refresh_slider = Slider(
            min=5, max=60, value=refresh_value, step=5
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
        
        # Create toggle button instead of Switch to avoid Kivy BooleanProperty issues
        self.theme_state = True  # Default to dark theme
        self.theme_button = Button(
            text='ON' if self.theme_state else 'OFF',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.8, 0.2, 1.0) if self.theme_state else (0.8, 0.2, 0.2, 1.0)
        )
        self.theme_button.bind(on_press=self.toggle_theme)
        theme_layout.add_widget(self.theme_button)
        section.add_widget(theme_layout)
        
        # Enable logging
        logging_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        logging_layout.add_widget(Label(text='Enable Logging:', size_hint_x=None, width=dp(120)))
        
        # Create toggle button instead of Switch to avoid Kivy BooleanProperty issues
        self.logging_state = True
        self.logging_button = Button(
            text='ON' if self.logging_state else 'OFF',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.8, 0.2, 1.0) if self.logging_state else (0.8, 0.2, 0.2, 1.0)
        )
        self.logging_button.bind(on_press=self.toggle_logging)
        logging_layout.add_widget(self.logging_button)
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
        # Use default values from AppState - NumericProperty(30.0)
        return 30.0
    
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
    
    def get_current_max_altitude(self):
        """Get current maximum altitude setting"""
        # Use default values from AppState - NumericProperty(85.0)
        return 85.0
    
    def get_current_min_azimuth(self):
        """Get current minimum azimuth setting"""
        # Use default values from AppState - NumericProperty(0.0)
        return 0.0
    
    def get_current_max_azimuth(self):
        """Get current maximum azimuth setting"""
        # Use default values from AppState - NumericProperty(360.0)
        return 360.0
    
    def get_current_exclude_insufficient(self):
        """Get current exclude insufficient time setting"""
        try:
            return getattr(self.app.app_state, 'exclude_insufficient_time', True)
        except:
            return True
    
    def get_current_refresh_interval(self):
        """Get current auto-refresh interval"""
        return 15.0  # Default 15 minutes
    
    def get_current_twilight_type(self):
        """Get current twilight type"""
        try:
            if self.app and hasattr(self.app.app_state, 'twilight_type'):
                twilight_type = self.app.app_state.twilight_type
                # Convert internal format to display format
                if twilight_type == 'civil':
                    return 'Civil (-6°)'
                elif twilight_type == 'nautical':
                    return 'Nautical (-12°)'
                elif twilight_type == 'astronomical':
                    return 'Astronomical (-18°)'
        except Exception:
            pass
        return "Astronomical (-18°)"  # Default to Astronomical
    
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
    
    def update_max_altitude_label(self, instance, value):
        """Update maximum altitude label"""
        self.max_altitude_label.text = f'{int(value)}°'
    
    # Toggle button methods (replacing Switch widgets to avoid Kivy BooleanProperty issues)
    def toggle_exclude_insufficient(self, instance):
        """Toggle exclude insufficient time setting"""
        self.exclude_insufficient_state = not self.exclude_insufficient_state
        instance.text = 'ON' if self.exclude_insufficient_state else 'OFF'
        instance.background_color = (0.2, 0.8, 0.2, 1.0) if self.exclude_insufficient_state else (0.8, 0.2, 0.2, 1.0)
    
    def toggle_advanced_filtering(self, instance):
        """Toggle advanced filtering setting"""
        self.advanced_filtering_state = not self.advanced_filtering_state
        instance.text = 'ON' if self.advanced_filtering_state else 'OFF'
        instance.background_color = (0.2, 0.8, 0.2, 1.0) if self.advanced_filtering_state else (0.8, 0.2, 0.2, 1.0)
    
    def toggle_theme(self, instance):
        """Toggle theme setting"""
        self.theme_state = not self.theme_state
        instance.text = 'ON' if self.theme_state else 'OFF'
        instance.background_color = (0.2, 0.8, 0.2, 1.0) if self.theme_state else (0.8, 0.2, 0.2, 1.0)
    
    def toggle_logging(self, instance):
        """Toggle logging setting"""
        self.logging_state = not self.logging_state
        instance.text = 'ON' if self.logging_state else 'OFF'
        instance.background_color = (0.2, 0.8, 0.2, 1.0) if self.logging_state else (0.8, 0.2, 0.2, 1.0)
    
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

            # Save twilight type
            try:
                display_twilight = self.twilight_spinner.text
                # Convert display format to internal format
                if 'Civil' in display_twilight:
                    internal_twilight = 'civil'
                elif 'Nautical' in display_twilight:
                    internal_twilight = 'nautical'
                elif 'Astronomical' in display_twilight:
                    internal_twilight = 'astronomical'
                else:
                    internal_twilight = 'astronomical'  # Default
                
                # Update app state
                self.app.app_state.twilight_type = internal_twilight
                
                # Update main config file
                self.update_main_config_twilight(internal_twilight)
                
                # Trigger refresh of targets and visibility chart
                if hasattr(self.app, 'refresh_data'):
                    self.app.refresh_data()
                    log_info(f"Triggered app refresh after twilight change to: {internal_twilight}")
                
                # Close the spinner popup (if it exists)
                if hasattr(self, 'twilight_popup') and self.twilight_popup:
                    self.twilight_popup.dismiss()
                
                log_info(f"Twilight type saved: {internal_twilight}")
            except Exception as e:
                log_error(f"Error saving twilight type: {e}")
                
            # Save other preferences
            try:
                self.app.app_state.min_visibility_hours = self.min_visibility_slider.value
                log_info(f"Min visibility saved: {self.min_visibility_slider.value}h")
            except Exception as e:
                log_error(f"Error saving visibility hours: {e}")
                self.show_error_popup("Invalid location coordinates")
                return
            
            # Save visibility constraints
            self.app.app_state.min_visibility_hours = self.min_visibility_slider.value
            self.app.app_state.min_altitude = self.min_altitude_slider.value
            self.app.app_state.max_altitude = self.max_altitude_slider.value
            self.app.app_state.exclude_insufficient_time = self.exclude_insufficient_state
            
            # Save app preferences
            # (These would be saved to app config/preferences)
            
            log_info(f"Saved visibility settings: min_alt={self.min_altitude_slider.value}°, "
                    f"max_alt={self.max_altitude_slider.value}°, "
                    f"min_vis={self.min_visibility_slider.value}h, "
                    f"exclude_insufficient={self.exclude_insufficient_state}")
            
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
            self.max_altitude_slider.value = 85.0
            self.min_visibility_slider.value = 2.0
            self.max_moon_slider.value = 50.0
            
            # Reset toggle buttons
            self.exclude_insufficient_state = True
            self.exclude_insufficient_button.text = 'ON'
            self.exclude_insufficient_button.background_color = (0.2, 0.8, 0.2, 1.0)
            
            self.advanced_filtering_state = False
            self.advanced_button.text = 'OFF'
            self.advanced_button.background_color = (0.8, 0.2, 0.2, 1.0)
            
            # Reset preferences
            self.refresh_slider.value = 15.0
            
            self.theme_state = True
            self.theme_button.text = 'ON'
            self.theme_button.background_color = (0.2, 0.8, 0.2, 1.0)
            
            self.logging_state = True
            self.logging_button.text = 'ON'
            self.logging_button.background_color = (0.2, 0.8, 0.2, 1.0)
            
            # Reset twilight type
            self.twilight_spinner.text = "Civil (-6°)"
            
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
                    'advanced_filtering': self.advanced_filtering_state
                },
                'preferences': {
                    'refresh_interval': self.refresh_slider.value,
                    'dark_theme': self.theme_state,
                    'logging_enabled': self.logging_state,
                    'twilight_type': self.twilight_spinner.text
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

    def update_main_config_twilight(self, twilight_type):
        """Update the main config.json file with the new twilight type"""
        try:
            import json
            import os
            
            # Get the path to the main config file
            main_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            
            if os.path.exists(main_config_path):
                with open(main_config_path, 'r') as f:
                    config = json.load(f)
                
                # Update twilight type
                if 'visibility' not in config:
                    config['visibility'] = {}
                config['visibility']['twilight_type'] = twilight_type
                
                # Write back to file
                with open(main_config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                log_info(f"Main config updated with twilight type: {twilight_type}")
            else:
                log_warning("Main config.json not found, twilight setting saved locally only")
                
        except Exception as e:
            log_error(f"Error updating main config file: {e}")

    def show_twilight_info(self, instance):
        """Show twilight type explanation popup"""
        info_text = """Twilight types define when night observations begin and end:

🌆 Civil Twilight (-6°)
• Sun 6° below horizon
• Best for: Planets, Moon, bright stars
• Earlier start, shorter nights

🌌 Nautical Twilight (-12°)
• Sun 12° below horizon  
• Best for: General astronomy
• Balanced observation window

⭐ Astronomical Twilight (-18°)
• Sun 18° below horizon
• Best for: Deep-sky imaging
• Darkest skies, longer waits"""
        
        content = Label(
            text=info_text,
            text_size=(dp(300), None),
            halign='left',
            valign='top'
        )
        
        popup = Popup(
            title='Twilight Types Explained',
            content=content,
            size_hint=(0.9, 0.7)
        )
        popup.open()
    
    def show_azimuth_editor(self, instance):
        """Show azimuth range editor popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Min azimuth
        min_az_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        min_az_layout.add_widget(Label(text='Min Azimuth:', size_hint_x=None, width=dp(100)))
        
        min_az_slider = Slider(min=0, max=360, value=self.get_current_min_azimuth(), step=15)
        min_az_layout.add_widget(min_az_slider)
        
        min_az_label = Label(text=f'{int(min_az_slider.value)}°', size_hint_x=None, width=dp(50))
        min_az_slider.bind(value=lambda instance, value: setattr(min_az_label, 'text', f'{int(value)}°'))
        min_az_layout.add_widget(min_az_label)
        content.add_widget(min_az_layout)
        
        # Max azimuth
        max_az_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        max_az_layout.add_widget(Label(text='Max Azimuth:', size_hint_x=None, width=dp(100)))
        
        max_az_slider = Slider(min=0, max=360, value=self.get_current_max_azimuth(), step=15)
        max_az_layout.add_widget(max_az_slider)
        
        max_az_label = Label(text=f'{int(max_az_slider.value)}°', size_hint_x=None, width=dp(50))
        max_az_slider.bind(value=lambda instance, value: setattr(max_az_label, 'text', f'{int(value)}°'))
        max_az_layout.add_widget(max_az_label)
        content.add_widget(max_az_layout)
        
        # Info
        info_label = Label(
            text='Azimuth range limits telescope pointing direction.\n0° = North, 90° = East, 180° = South, 270° = West',
            size_hint_y=None,
            height=dp(60),
            halign='center',
            text_size=(dp(300), None)
        )
        content.add_widget(info_label)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        def save_azimuth(instance):
            self.app.app_state.min_azimuth = min_az_slider.value
            self.app.app_state.max_azimuth = max_az_slider.value
            self.azimuth_range_label.text = f'{int(min_az_slider.value)}° - {int(max_az_slider.value)}°'
            azimuth_popup.dismiss()
            
        def reset_azimuth(instance):
            min_az_slider.value = 0
            max_az_slider.value = 360
        
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1.0))
        save_btn.bind(on_press=save_azimuth)
        
        reset_btn = Button(text='Reset (0°-360°)', background_color=(0.8, 0.4, 0.2, 1.0))
        reset_btn.bind(on_press=reset_azimuth)
        
        cancel_btn = Button(text='Cancel', background_color=(0.6, 0.6, 0.6, 1.0))
        cancel_btn.bind(on_press=lambda x: azimuth_popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(reset_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)
        
        azimuth_popup = Popup(
            title='Edit Azimuth Range',
            content=content,
            size_hint=(0.8, 0.6)
        )
        azimuth_popup.open()