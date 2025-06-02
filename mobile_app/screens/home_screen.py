"""
Home Screen
Main dashboard showing tonight's overview and quick actions
"""

import os
import sys
from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.card import Card
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from astropy import calculate_moon_phase, get_moon_phase_icon, find_astronomical_twilight
    from astronomy import get_local_timezone, utc_to_local
except ImportError as e:
    Logger.error(f"HomeScreen: Failed to import astropy modules: {e}")

# Import plotting utilities
try:
    from utils.plotting import mobile_plot_generator
    from widgets.plot_widget import PlotWidget
    PLOTTING_AVAILABLE = True
except ImportError as e:
    Logger.warning(f"HomeScreen: Plotting not available: {e}")
    PLOTTING_AVAILABLE = False

class HomeScreen(Screen):
    """Main home screen with tonight's overview"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()
        
        # Schedule periodic updates
        Clock.schedule_interval(self.update_time_display, 60)  # Update every minute
    
    def build_ui(self):
        """Build the home screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header with app title and current time
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Tonight's conditions card
        conditions_card = self.create_conditions_card()
        main_layout.add_widget(conditions_card)
        
        # Quick stats
        stats_card = self.create_stats_card()
        main_layout.add_widget(stats_card)
        
        # Quick action buttons
        actions_grid = self.create_action_buttons()
        main_layout.add_widget(actions_grid)
        
        # Tonight's highlights
        highlights_card = self.create_highlights_card()
        main_layout.add_widget(highlights_card)
        
        # Visibility chart
        if PLOTTING_AVAILABLE:
            chart_card = self.create_visibility_chart_card()
            main_layout.add_widget(chart_card)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header with title and time"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        # App title
        title_label = Label(
            text='AstroScope Planner',
            font_size='20sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # Current time
        self.time_label = Label(
            text=self.get_current_time_string(),
            font_size='16sp',
            halign='right',
            valign='middle',
            size_hint_x=None,
            width=dp(120)
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        header.add_widget(title_label)
        header.add_widget(self.time_label)
        
        return header
    
    def create_conditions_card(self):
        """Create tonight's conditions overview card"""
        card_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150)
        )
        
        # Card title
        title = Label(
            text='Tonight\'s Conditions',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        card_layout.add_widget(title)
        
        # Conditions grid
        conditions_grid = GridLayout(cols=2, spacing=dp(10))
        
        # Moon phase
        self.moon_label = Label(
            text=self.get_moon_info(),
            halign='left',
            valign='middle'
        )
        self.moon_label.bind(size=self.moon_label.setter('text_size'))
        conditions_grid.add_widget(self.moon_label)
        
        # Twilight times
        self.twilight_label = Label(
            text=self.get_twilight_info(),
            halign='left',
            valign='middle'
        )
        self.twilight_label.bind(size=self.twilight_label.setter('text_size'))
        conditions_grid.add_widget(self.twilight_label)
        
        # Location
        self.location_label = Label(
            text=self.get_location_info(),
            halign='left',
            valign='middle'
        )
        self.location_label.bind(size=self.location_label.setter('text_size'))
        conditions_grid.add_widget(self.location_label)
        
        # Session status
        self.session_label = Label(
            text=self.get_session_info(),
            halign='left',
            valign='middle'
        )
        self.session_label.bind(size=self.session_label.setter('text_size'))
        conditions_grid.add_widget(self.session_label)
        
        card_layout.add_widget(conditions_grid)
        
        return card_layout
    
    def create_stats_card(self):
        """Create quick stats card"""
        stats_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(100)
        )
        
        # Title
        title = Label(
            text='Quick Stats',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        stats_layout.add_widget(title)
        
        # Stats grid
        stats_grid = GridLayout(cols=3, spacing=dp(10))
        
        # Total targets
        self.total_targets_label = Label(
            text='0\nTargets',
            halign='center',
            valign='middle',
            font_size='14sp'
        )
        self.total_targets_label.bind(size=self.total_targets_label.setter('text_size'))
        stats_grid.add_widget(self.total_targets_label)
        
        # Planned
        self.planned_label = Label(
            text='0\nPlanned',
            halign='center',
            valign='middle',
            font_size='14sp'
        )
        self.planned_label.bind(size=self.planned_label.setter('text_size'))
        stats_grid.add_widget(self.planned_label)
        
        # Completed
        self.completed_label = Label(
            text='0\nCompleted',
            halign='center',
            valign='middle',
            font_size='14sp'
        )
        self.completed_label.bind(size=self.completed_label.setter('text_size'))
        stats_grid.add_widget(self.completed_label)
        
        stats_layout.add_widget(stats_grid)
        
        return stats_layout
    
    def create_action_buttons(self):
        """Create quick action buttons grid"""
        actions_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        # View Targets button
        targets_btn = Button(
            text='View Tonight\'s\nTargets',
            font_size='16sp',
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        targets_btn.bind(on_press=self.go_to_targets)
        actions_grid.add_widget(targets_btn)
        
        # Mosaic Planning button
        mosaic_btn = Button(
            text='Mosaic\nPlanning',
            font_size='16sp',
            background_color=(0.8, 0.4, 1.0, 1.0)
        )
        mosaic_btn.bind(on_press=self.go_to_mosaic)
        actions_grid.add_widget(mosaic_btn)
        
        # Refresh Data button
        refresh_btn = Button(
            text='Refresh\nData',
            font_size='16sp',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        refresh_btn.bind(on_press=self.refresh_data)
        actions_grid.add_widget(refresh_btn)
        
        # Settings button
        settings_btn = Button(
            text='Settings',
            font_size='16sp',
            background_color=(0.6, 0.6, 0.6, 1.0)
        )
        settings_btn.bind(on_press=self.go_to_settings)
        actions_grid.add_widget(settings_btn)
        
        # Reports button
        reports_btn = Button(
            text='Reports',
            font_size='16sp',
            background_color=(0.8, 0.6, 0.2, 1.0)
        )
        reports_btn.bind(on_press=self.go_to_reports)
        actions_grid.add_widget(reports_btn)
        
        return actions_grid
    
    def create_highlights_card(self):
        """Create tonight's highlights card"""
        highlights_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )
        
        # Title
        title = Label(
            text='Tonight\'s Highlights',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        highlights_layout.add_widget(title)
        
        # Scrollable highlights list
        scroll = ScrollView()
        self.highlights_list = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.highlights_list.bind(minimum_height=self.highlights_list.setter('height'))
        
        scroll.add_widget(self.highlights_list)
        highlights_layout.add_widget(scroll)
        
        return highlights_layout
    
    def create_visibility_chart_card(self):
        """Create visibility chart card"""
        chart_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )
        
        # Title
        title = Label(
            text="Tonight's Visibility Chart",
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        chart_layout.add_widget(title)
        
        # Plot widget
        self.visibility_plot = PlotWidget()
        chart_layout.add_widget(self.visibility_plot)
        
        # Generate chart button
        generate_btn = Button(
            text='Generate Chart',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        generate_btn.bind(on_press=self.generate_visibility_chart)
        chart_layout.add_widget(generate_btn)
        
        return chart_layout
    
    def generate_visibility_chart(self, instance):
        """Generate visibility chart for tonight's targets"""
        if not self.app:
            Logger.warning("HomeScreen: No app available for chart generation")
            return
        
        try:
            # Get visible targets for tonight
            visible_targets = self.app.app_state.visible_objects[:10]  # Top 10
            location = self.app.app_state.current_location
            
            if not visible_targets or not location:
                Logger.warning("HomeScreen: No targets or location for chart")
                return
            
            # Generate visibility chart
            self.visibility_plot.load_plot_async(
                mobile_plot_generator.create_visibility_chart,
                "Tonight's Visibility",
                visible_targets,
                location
            )
            
            Logger.info("HomeScreen: Visibility chart generation initiated")
            
        except Exception as e:
            Logger.error(f"HomeScreen: Error generating visibility chart: {e}")
    
    def update_display(self):
        """Update all display elements"""
        try:
            # Update time
            self.time_label.text = self.get_current_time_string()
            
            # Update conditions
            self.moon_label.text = self.get_moon_info()
            self.twilight_label.text = self.get_twilight_info()
            self.location_label.text = self.get_location_info()
            self.session_label.text = self.get_session_info()
            
            # Update stats
            if self.app and self.app.app_state:
                stats = self.app.app_state.get_session_stats()
                self.total_targets_label.text = f"{stats['total_targets']}\nTargets"
                self.planned_label.text = f"{stats['planned_count']}\nPlanned"
                self.completed_label.text = f"{stats['completed_count']}\nCompleted"
            
            # Update highlights
            self.update_highlights()
            
        except Exception as e:
            Logger.error(f"HomeScreen: Error updating display: {e}")
    
    def update_highlights(self):
        """Update tonight's highlights list"""
        try:
            self.highlights_list.clear_widgets()
            
            if not self.app or not self.app.app_state.tonights_targets:
                no_data_label = Label(
                    text='No targets loaded. Tap "Refresh Data" to load tonight\'s targets.',
                    text_size=(dp(300), None),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(60)
                )
                self.highlights_list.add_widget(no_data_label)
                return
            
            # Show top 5 targets
            top_targets = self.app.app_state.tonights_targets[:5]
            
            for i, target in enumerate(top_targets):
                target_name = getattr(target, 'name', target.get('name', 'Unknown'))
                target_type = getattr(target, 'object_type', target.get('object_type', 'Unknown'))
                
                target_btn = Button(
                    text=f"{i+1}. {target_name} ({target_type})",
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    background_color=(0.3, 0.3, 0.3, 1.0)
                )
                target_btn.bind(on_press=lambda x, t=target: self.view_target_detail(t))
                self.highlights_list.add_widget(target_btn)
            
            # Add "View All" button
            view_all_btn = Button(
                text='View All Targets →',
                size_hint_y=None,
                height=dp(40),
                background_color=(0.2, 0.6, 1.0, 1.0)
            )
            view_all_btn.bind(on_press=self.go_to_targets)
            self.highlights_list.add_widget(view_all_btn)
            
        except Exception as e:
            Logger.error(f"HomeScreen: Error updating highlights: {e}")
    
    def get_current_time_string(self):
        """Get formatted current time string"""
        try:
            now = datetime.now()
            return now.strftime('%H:%M')
        except:
            return '--:--'
    
    def get_moon_info(self):
        """Get moon phase information"""
        try:
            moon_phase = calculate_moon_phase(datetime.now())
            moon_icon = get_moon_phase_icon(moon_phase)
            illumination = int(moon_phase * 100)
            return f"Moon: {moon_icon} {illumination}%"
        except:
            return "Moon: -- %"
    
    def get_twilight_info(self):
        """Get twilight times"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                twilight_times = find_astronomical_twilight(
                    datetime.now(),
                    location['latitude'],
                    location['longitude']
                )
                
                if twilight_times:
                    sunset, sunrise = twilight_times
                    sunset_local = utc_to_local(sunset)
                    sunrise_local = utc_to_local(sunrise)
                    return f"Dark: {sunset_local.strftime('%H:%M')} - {sunrise_local.strftime('%H:%M')}"
            
            return "Twilight: --:-- - --:--"
        except:
            return "Twilight: --:-- - --:--"
    
    def get_location_info(self):
        """Get current location info"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                return f"Location: {location.get('name', 'Unknown')}"
            return "Location: Not set"
        except:
            return "Location: Error"
    
    def get_session_info(self):
        """Get session information"""
        try:
            if self.app and self.app.app_state:
                strategy = self.app.app_state.get_strategy_display_name(
                    self.app.app_state.scheduling_strategy
                )
                return f"Strategy: {strategy}"
            return "Strategy: Not set"
        except:
            return "Strategy: Error"
    
    def update_time_display(self, dt):
        """Periodic time update"""
        self.time_label.text = self.get_current_time_string()
    
    # Button callbacks
    def go_to_targets(self, instance):
        """Navigate to targets screen"""
        if self.app:
            self.app.screen_manager.current = 'targets'
    
    def go_to_mosaic(self, instance):
        """Navigate to mosaic screen"""
        if self.app:
            self.app.screen_manager.current = 'mosaic'
    
    def go_to_settings(self, instance):
        """Navigate to settings screen"""
        if self.app:
            self.app.screen_manager.current = 'settings'
    
    def go_to_reports(self, instance):
        """Navigate to reports screen"""
        if self.app:
            self.app.screen_manager.current = 'reports'
    
    def refresh_data(self, instance):
        """Refresh application data"""
        if self.app:
            self.app.refresh_data()
            self.update_display()
    
    def view_target_detail(self, target):
        """View detailed information about a target"""
        if self.app:
            self.app.app_state.selected_target = target
            self.app.screen_manager.current = 'target_detail'