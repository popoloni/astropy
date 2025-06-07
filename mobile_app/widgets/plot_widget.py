"""
Plot Widget for Mobile App
Custom Kivy widget for displaying matplotlib plots with touch interaction
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.core.window import Window

class PlotWidget(BoxLayout):
    """Widget for displaying matplotlib plots in Kivy"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(5)
        self.plot_path = None
        self.plot_image = None
        self.loading_popup = None
        
        self.build_ui()
    
    def build_ui(self):
        """Build the plot widget UI"""
        # Plot display area
        self.plot_image = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.plot_image)
        
        # Control buttons
        controls = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )
        
        self.refresh_btn = Button(
            text='Refresh',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        self.refresh_btn.bind(on_press=self.refresh_plot)
        
        self.fullscreen_btn = Button(
            text='Fullscreen',
            size_hint_x=0.3,
            background_color=(0.6, 0.2, 1.0, 1.0)
        )
        self.fullscreen_btn.bind(on_press=self.show_fullscreen)
        
        self.save_btn = Button(
            text='Save',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        self.save_btn.bind(on_press=self.save_plot)
        
        controls.add_widget(self.refresh_btn)
        controls.add_widget(self.fullscreen_btn)
        controls.add_widget(self.save_btn)
        
        self.add_widget(controls)
        
        # Status label
        self.status_label = Label(
            text='No plot loaded',
            size_hint_y=None,
            height=dp(30),
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.status_label)
    
    def load_plot(self, plot_path, title="Plot"):
        """Load and display a plot from file path"""
        try:
            if plot_path and os.path.exists(plot_path):
                self.plot_path = plot_path
                self.plot_image.source = plot_path
                self.status_label.text = f'Loaded: {title}'
                Logger.info(f"PlotWidget: Loaded plot from {plot_path}")
            else:
                self.show_error("Plot file not found")
                
        except Exception as e:
            Logger.error(f"PlotWidget: Error loading plot: {e}")
            self.show_error(f"Error loading plot: {str(e)}")
    
    def load_plot_async(self, plot_generator_func, title="Plot", *args, **kwargs):
        """Load plot asynchronously with loading indicator"""
        self.show_loading(f"Generating {title}...")
        
        # Schedule plot generation on next frame
        Clock.schedule_once(
            lambda dt: self._generate_plot_async(plot_generator_func, title, *args, **kwargs),
            0.1
        )
    
    def _generate_plot_async(self, plot_generator_func, title, *args, **kwargs):
        """Generate plot in background"""
        try:
            plot_path = plot_generator_func(*args, **kwargs)
            self.hide_loading()
            
            if plot_path:
                self.load_plot(plot_path, title)
            else:
                self.show_error("Failed to generate plot")
                
        except Exception as e:
            self.hide_loading()
            Logger.error(f"PlotWidget: Error generating plot: {e}")
            self.show_error(f"Error generating plot: {str(e)}")
    
    def show_loading(self, message="Loading..."):
        """Show loading popup"""
        if self.loading_popup:
            self.loading_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        progress = ProgressBar()
        content.add_widget(progress)
        
        label = Label(text=message, size_hint_y=None, height=dp(40))
        content.add_widget(label)
        
        self.loading_popup = Popup(
            title='Generating Plot',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        self.loading_popup.open()
    
    def hide_loading(self):
        """Hide loading popup"""
        if self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.text = f'Error: {message}'
        self.plot_image.source = ''  # Clear image
        
        # Show error popup
        popup = Popup(
            title='Plot Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def refresh_plot(self, instance):
        """Refresh the current plot"""
        if self.plot_path and os.path.exists(self.plot_path):
            # Force reload the image
            self.plot_image.reload()
            self.status_label.text = 'Plot refreshed'
        else:
            self.show_error("No plot to refresh")
    
    def show_fullscreen(self, instance):
        """Show plot in fullscreen popup"""
        if not self.plot_path or not os.path.exists(self.plot_path):
            self.show_error("No plot to display")
            return
        
        # Create fullscreen popup
        content = BoxLayout(orientation='vertical')
        
        fullscreen_image = Image(
            source=self.plot_path,
            allow_stretch=True,
            keep_ratio=True
        )
        content.add_widget(fullscreen_image)
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1.0)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Plot - Fullscreen',
            content=content,
            size_hint=(0.95, 0.95)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def save_plot(self, instance):
        """Save plot to device storage"""
        if not self.plot_path or not os.path.exists(self.plot_path):
            self.show_error("No plot to save")
            return
        
        try:
            # For mobile, we'd typically save to app's documents directory
            # This is a simplified implementation
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"astroscope_plot_{timestamp}.png"
            
            # In a real mobile app, you'd use platform-specific storage
            save_path = os.path.join(os.path.expanduser("~"), save_name)
            shutil.copy2(self.plot_path, save_path)
            
            popup = Popup(
                title='Plot Saved',
                content=Label(text=f'Plot saved as:\n{save_name}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            
        except Exception as e:
            Logger.error(f"PlotWidget: Error saving plot: {e}")
            self.show_error(f"Error saving plot: {str(e)}")

class PlotContainer(BoxLayout):
    """Container for multiple plot widgets with tabs"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.plots = {}
        self.current_plot = None
        
        self.build_ui()
    
    def build_ui(self):
        """Build the plot container UI"""
        # Tab buttons
        self.tab_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(2)
        )
        self.add_widget(self.tab_layout)
        
        # Plot display area
        self.plot_area = BoxLayout()
        self.add_widget(self.plot_area)
    
    def add_plot_tab(self, tab_name, plot_widget):
        """Add a new plot tab"""
        # Create tab button
        tab_btn = Button(
            text=tab_name,
            size_hint_x=None,
            width=dp(100),
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        tab_btn.bind(on_press=lambda x: self.switch_to_plot(tab_name))
        
        self.tab_layout.add_widget(tab_btn)
        self.plots[tab_name] = {
            'widget': plot_widget,
            'button': tab_btn
        }
        
        # Show first plot by default
        if len(self.plots) == 1:
            self.switch_to_plot(tab_name)
    
    def switch_to_plot(self, tab_name):
        """Switch to a specific plot tab"""
        if tab_name not in self.plots:
            return
        
        # Update button colors
        for name, plot_info in self.plots.items():
            if name == tab_name:
                plot_info['button'].background_color = (0.2, 0.6, 1.0, 1.0)
            else:
                plot_info['button'].background_color = (0.3, 0.3, 0.3, 1.0)
        
        # Switch plot display
        self.plot_area.clear_widgets()
        self.plot_area.add_widget(self.plots[tab_name]['widget'])
        self.current_plot = tab_name
    
    def get_current_plot_widget(self):
        """Get the currently displayed plot widget"""
        if self.current_plot and self.current_plot in self.plots:
            return self.plots[self.current_plot]['widget']
        return None