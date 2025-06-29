"""
Theme Manager for AstroScope Planner
Manages application themes including day, night, and red night vision modes
"""

from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.app import App
import json
import os


class ThemeManager(EventDispatcher):
    """Manages application themes and color schemes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Current theme
        self.current_theme = 'light'
        
        # Theme definitions
        self.themes = {
            'light': {
                'name': 'Light Theme',
                'description': 'Bright theme for daytime use',
                'colors': {
                    # Background colors
                    'background_primary': (1.0, 1.0, 1.0, 1.0),      # White
                    'background_secondary': (0.95, 0.95, 0.95, 1.0),  # Light gray
                    'background_card': (0.98, 0.98, 0.98, 1.0),       # Very light gray
                    'background_header': (0.9, 0.9, 0.9, 1.0),        # Light gray
                    
                    # Text colors
                    'text_primary': (0.1, 0.1, 0.1, 1.0),             # Dark gray
                    'text_secondary': (0.4, 0.4, 0.4, 1.0),           # Medium gray
                    'text_hint': (0.6, 0.6, 0.6, 1.0),                # Light gray
                    'text_disabled': (0.7, 0.7, 0.7, 1.0),            # Very light gray
                    
                    # Accent colors
                    'accent_primary': (0.2, 0.6, 1.0, 1.0),           # Blue
                    'accent_secondary': (0.8, 0.4, 1.0, 1.0),         # Purple
                    'accent_success': (0.2, 0.8, 0.2, 1.0),           # Green
                    'accent_warning': (1.0, 0.6, 0.0, 1.0),           # Orange
                    'accent_error': (1.0, 0.2, 0.2, 1.0),             # Red
                    
                    # Button colors
                    'button_primary': (0.2, 0.6, 1.0, 1.0),           # Blue
                    'button_secondary': (0.6, 0.6, 0.6, 1.0),         # Gray
                    'button_disabled': (0.8, 0.8, 0.8, 1.0),          # Light gray
                    'button_text': (1.0, 1.0, 1.0, 1.0),              # White
                    
                    # Border and divider colors
                    'border_primary': (0.8, 0.8, 0.8, 1.0),           # Light gray
                    'border_secondary': (0.9, 0.9, 0.9, 1.0),         # Very light gray
                    'divider': (0.85, 0.85, 0.85, 1.0),               # Light gray
                    
                    # Special astronomy colors
                    'star_color': (1.0, 1.0, 0.8, 1.0),               # Warm white
                    'nebula_color': (0.8, 0.4, 1.0, 1.0),             # Purple
                    'galaxy_color': (1.0, 0.8, 0.4, 1.0),             # Orange
                    'planet_color': (0.4, 0.8, 1.0, 1.0),             # Light blue
                }
            },
            
            'dark': {
                'name': 'Dark Theme',
                'description': 'Dark theme for low-light conditions',
                'colors': {
                    # Background colors
                    'background_primary': (0.1, 0.1, 0.1, 1.0),       # Very dark gray
                    'background_secondary': (0.15, 0.15, 0.15, 1.0),  # Dark gray
                    'background_card': (0.2, 0.2, 0.2, 1.0),          # Medium dark gray
                    'background_header': (0.12, 0.12, 0.12, 1.0),     # Very dark gray
                    
                    # Text colors
                    'text_primary': (0.9, 0.9, 0.9, 1.0),             # Light gray
                    'text_secondary': (0.7, 0.7, 0.7, 1.0),           # Medium gray
                    'text_hint': (0.5, 0.5, 0.5, 1.0),                # Dark gray
                    'text_disabled': (0.4, 0.4, 0.4, 1.0),            # Very dark gray
                    
                    # Accent colors
                    'accent_primary': (0.3, 0.7, 1.0, 1.0),           # Light blue
                    'accent_secondary': (0.9, 0.5, 1.0, 1.0),         # Light purple
                    'accent_success': (0.3, 0.9, 0.3, 1.0),           # Light green
                    'accent_warning': (1.0, 0.7, 0.1, 1.0),           # Light orange
                    'accent_error': (1.0, 0.3, 0.3, 1.0),             # Light red
                    
                    # Button colors
                    'button_primary': (0.3, 0.7, 1.0, 1.0),           # Light blue
                    'button_secondary': (0.4, 0.4, 0.4, 1.0),         # Dark gray
                    'button_disabled': (0.25, 0.25, 0.25, 1.0),       # Very dark gray
                    'button_text': (0.9, 0.9, 0.9, 1.0),              # Light gray
                    
                    # Border and divider colors
                    'border_primary': (0.3, 0.3, 0.3, 1.0),           # Dark gray
                    'border_secondary': (0.25, 0.25, 0.25, 1.0),      # Very dark gray
                    'divider': (0.3, 0.3, 0.3, 1.0),                  # Dark gray
                    
                    # Special astronomy colors
                    'star_color': (1.0, 1.0, 0.9, 1.0),               # Warm white
                    'nebula_color': (0.9, 0.5, 1.0, 1.0),             # Light purple
                    'galaxy_color': (1.0, 0.9, 0.5, 1.0),             # Light orange
                    'planet_color': (0.5, 0.9, 1.0, 1.0),             # Light blue
                }
            },
            
            'red': {
                'name': 'Red Night Vision',
                'description': 'Red theme to preserve night vision',
                'colors': {
                    # Background colors
                    'background_primary': (0.05, 0.0, 0.0, 1.0),      # Very dark red
                    'background_secondary': (0.1, 0.0, 0.0, 1.0),     # Dark red
                    'background_card': (0.15, 0.05, 0.05, 1.0),       # Medium dark red
                    'background_header': (0.08, 0.0, 0.0, 1.0),       # Very dark red
                    
                    # Text colors
                    'text_primary': (1.0, 0.3, 0.3, 1.0),             # Light red
                    'text_secondary': (0.8, 0.2, 0.2, 1.0),           # Medium red
                    'text_hint': (0.6, 0.1, 0.1, 1.0),                # Dark red
                    'text_disabled': (0.4, 0.05, 0.05, 1.0),          # Very dark red
                    
                    # Accent colors
                    'accent_primary': (1.0, 0.4, 0.4, 1.0),           # Light red
                    'accent_secondary': (1.0, 0.6, 0.6, 1.0),         # Very light red
                    'accent_success': (0.8, 0.4, 0.4, 1.0),           # Red-green
                    'accent_warning': (1.0, 0.5, 0.3, 1.0),           # Red-orange
                    'accent_error': (1.0, 0.2, 0.2, 1.0),             # Bright red
                    
                    # Button colors
                    'button_primary': (0.8, 0.2, 0.2, 1.0),           # Medium red
                    'button_secondary': (0.4, 0.1, 0.1, 1.0),         # Dark red
                    'button_disabled': (0.2, 0.05, 0.05, 1.0),        # Very dark red
                    'button_text': (1.0, 0.4, 0.4, 1.0),              # Light red
                    
                    # Border and divider colors
                    'border_primary': (0.4, 0.1, 0.1, 1.0),           # Dark red
                    'border_secondary': (0.3, 0.05, 0.05, 1.0),       # Very dark red
                    'divider': (0.3, 0.08, 0.08, 1.0),                # Dark red
                    
                    # Special astronomy colors
                    'star_color': (1.0, 0.5, 0.5, 1.0),               # Light red
                    'nebula_color': (1.0, 0.4, 0.4, 1.0),             # Red
                    'galaxy_color': (0.9, 0.3, 0.3, 1.0),             # Medium red
                    'planet_color': (1.0, 0.6, 0.6, 1.0),             # Light red
                }
            }
        }
        
        # Theme change callbacks
        self.theme_callbacks = []
        
        # Load saved theme
        self.load_theme_preference()
    
    def get_color(self, color_name):
        """Get a color from the current theme"""
        if self.current_theme in self.themes:
            theme = self.themes[self.current_theme]
            if color_name in theme['colors']:
                return theme['colors'][color_name]
        
        # Fallback to light theme
        if color_name in self.themes['light']['colors']:
            return self.themes['light']['colors'][color_name]
        
        # Ultimate fallback
        Logger.warning(f"ThemeManager: Color '{color_name}' not found, using default")
        return (0.5, 0.5, 0.5, 1.0)  # Gray
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            old_theme = self.current_theme
            self.current_theme = theme_name
            
            Logger.info(f"ThemeManager: Changed theme from '{old_theme}' to '{theme_name}'")
            
            # Save preference
            self.save_theme_preference()
            
            # Notify callbacks
            self._notify_theme_change(old_theme, theme_name)
            
            return True
        else:
            Logger.error(f"ThemeManager: Theme '{theme_name}' not found")
            return False
    
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme
    
    def get_theme_info(self, theme_name=None):
        """Get theme information"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name in self.themes:
            return {
                'name': self.themes[theme_name]['name'],
                'description': self.themes[theme_name]['description'],
                'current': theme_name == self.current_theme
            }
        return None
    
    def get_available_themes(self):
        """Get list of available themes"""
        return [
            {
                'id': theme_id,
                'name': theme_data['name'],
                'description': theme_data['description'],
                'current': theme_id == self.current_theme
            }
            for theme_id, theme_data in self.themes.items()
        ]
    
    def register_theme_callback(self, callback):
        """Register a callback for theme changes"""
        if callback not in self.theme_callbacks:
            self.theme_callbacks.append(callback)
            Logger.info("ThemeManager: Registered theme change callback")
    
    def unregister_theme_callback(self, callback):
        """Unregister a theme change callback"""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
            Logger.info("ThemeManager: Unregistered theme change callback")
    
    def _notify_theme_change(self, old_theme, new_theme):
        """Notify all callbacks of theme change"""
        for callback in self.theme_callbacks:
            try:
                callback(old_theme, new_theme)
            except Exception as e:
                Logger.error(f"ThemeManager: Error in theme change callback: {e}")
    
    def save_theme_preference(self):
        """Save theme preference to file"""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir'):
                config_file = os.path.join(app.user_data_dir, 'theme_config.json')
                
                config = {
                    'current_theme': self.current_theme,
                    'auto_night_mode': getattr(self, 'auto_night_mode', False),
                    'night_mode_start': getattr(self, 'night_mode_start', '20:00'),
                    'night_mode_end': getattr(self, 'night_mode_end', '06:00')
                }
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                Logger.info(f"ThemeManager: Saved theme preference: {self.current_theme}")
        except Exception as e:
            Logger.error(f"ThemeManager: Error saving theme preference: {e}")
    
    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'user_data_dir'):
                config_file = os.path.join(app.user_data_dir, 'theme_config.json')
                
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    theme = config.get('current_theme', 'light')
                    if theme in self.themes:
                        self.current_theme = theme
                        Logger.info(f"ThemeManager: Loaded theme preference: {theme}")
                    
                    # Load other settings
                    self.auto_night_mode = config.get('auto_night_mode', False)
                    self.night_mode_start = config.get('night_mode_start', '20:00')
                    self.night_mode_end = config.get('night_mode_end', '06:00')
        except Exception as e:
            Logger.error(f"ThemeManager: Error loading theme preference: {e}")
    
    def apply_theme_to_widget(self, widget, widget_type='default'):
        """Apply current theme colors to a widget"""
        try:
            if widget_type == 'button':
                widget.background_color = self.get_color('button_primary')
                if hasattr(widget, 'color'):
                    widget.color = self.get_color('button_text')
            
            elif widget_type == 'label':
                if hasattr(widget, 'color'):
                    widget.color = self.get_color('text_primary')
            
            elif widget_type == 'background':
                if hasattr(widget, 'background_color'):
                    widget.background_color = self.get_color('background_primary')
            
            elif widget_type == 'card':
                if hasattr(widget, 'background_color'):
                    widget.background_color = self.get_color('background_card')
            
            elif widget_type == 'header':
                if hasattr(widget, 'background_color'):
                    widget.background_color = self.get_color('background_header')
                if hasattr(widget, 'color'):
                    widget.color = self.get_color('text_primary')
            
            # Add more widget types as needed
            
        except Exception as e:
            Logger.error(f"ThemeManager: Error applying theme to widget: {e}")
    
    def get_themed_style(self, style_type):
        """Get a complete style dictionary for a widget type"""
        styles = {
            'button_primary': {
                'background_color': self.get_color('button_primary'),
                'color': self.get_color('button_text')
            },
            'button_secondary': {
                'background_color': self.get_color('button_secondary'),
                'color': self.get_color('button_text')
            },
            'label_primary': {
                'color': self.get_color('text_primary')
            },
            'label_secondary': {
                'color': self.get_color('text_secondary')
            },
            'background': {
                'background_color': self.get_color('background_primary')
            },
            'card': {
                'background_color': self.get_color('background_card')
            }
        }
        
        return styles.get(style_type, {})
    
    def is_dark_theme(self):
        """Check if current theme is dark"""
        return self.current_theme in ['dark', 'red']
    
    def is_red_theme(self):
        """Check if current theme is red night vision"""
        return self.current_theme == 'red'


# Themed widget mixins
class ThemedWidget:
    """Mixin class to add theme support to widgets"""
    
    def __init__(self, theme_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = theme_manager or ThemeManager()
        self.theme_manager.register_theme_callback(self.on_theme_change)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to this widget - override in subclasses"""
        pass
    
    def on_theme_change(self, old_theme, new_theme):
        """Called when theme changes"""
        self.apply_theme()
    
    def get_color(self, color_name):
        """Get a color from the theme manager"""
        return self.theme_manager.get_color(color_name)


class ThemedButton(ThemedWidget):
    """Button with automatic theme support"""
    
    def apply_theme(self):
        """Apply theme to button"""
        self.background_color = self.get_color('button_primary')
        if hasattr(self, 'color'):
            self.color = self.get_color('button_text')


class ThemedLabel(ThemedWidget):
    """Label with automatic theme support"""
    
    def apply_theme(self):
        """Apply theme to label"""
        if hasattr(self, 'color'):
            self.color = self.get_color('text_primary')


# Global theme manager instance
_theme_manager = None

def get_theme_manager():
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager