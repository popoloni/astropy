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
# from kivy.uix.card import Card  # Not available, using BoxLayout instead
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock
from mobile_app.utils.app_logger import log_error, log_warning, log_debug, log_info, log_navigation

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from astronightplanner import calculate_moon_phase, get_moon_phase_icon, find_astronomical_twilight
    from astronomy import find_configured_twilight, get_local_timezone, utc_to_local
except ImportError as e:
    Logger.error(f"HomeScreen: Failed to import astronightplanner modules: {e}")

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
        
        # Schedule initial data update with a small delay
        Clock.schedule_once(self.initial_update, 1.0)
        
        # Schedule periodic data checks to catch when data loads
        Clock.schedule_interval(self.periodic_data_check, 5.0)  # Check every 5 seconds
    
    def build_ui(self):
        """Build the home screen UI with proper mobile layout"""
        # Use ScrollView as the main container to handle content overflow
        scroll = ScrollView()
        
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=dp(15), 
            spacing=dp(15),
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Header with app title and current time
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Quick stats (compact version)
        stats_card = self.create_stats_card()
        main_layout.add_widget(stats_card)
        
        # Primary action buttons (reduced to essentials)
        actions_grid = self.create_action_buttons()
        main_layout.add_widget(actions_grid)
        
        # Tonight's conditions card
        conditions_card = self.create_conditions_card()
        main_layout.add_widget(conditions_card)
        
        # Visibility chart (if available)
        if PLOTTING_AVAILABLE:
            chart_card = self.create_visibility_chart_card()
            main_layout.add_widget(chart_card)
        
        # Tonight's highlights (compact)
        highlights_card = self.create_highlights_card()
        main_layout.add_widget(highlights_card)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def create_header(self):
        """Create header with title and navigation"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[dp(10), 0]
        )
        
        # Title and welcome message
        title_layout = BoxLayout(orientation='vertical')
        
        title_label = Label(
            text='AstroScope Planner',
            font_size='20sp',
            bold=True,
            halign='left',
            size_hint_y=None,
            height=dp(30),
            color=(1, 1, 1, 1)
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        welcome_label = Label(
            text=f'Welcome back! Tonight: {datetime.now().strftime("%b %d")}',
            font_size='14sp',
            halign='left',
            size_hint_y=None,
            height=dp(20),
            color=(0.8, 0.8, 0.8, 1)
        )
        welcome_label.bind(size=welcome_label.setter('text_size'))
        
        title_layout.add_widget(title_label)
        title_layout.add_widget(welcome_label)
        
        # Settings button
        settings_btn = Button(
            text='⚙',
            size_hint_x=None,
            width=dp(50),
            font_size='20sp',
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        settings_btn.bind(on_press=self.open_settings)
        
        header.add_widget(title_layout)
        header.add_widget(settings_btn)
        
        return header
    
    def create_stats_card(self):
        """Create compact quick stats card"""
        stats_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),
            spacing=dp(8)
        )
        
        # Title
        title = Label(
            text='Quick Stats',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        stats_layout.add_widget(title)
        
        # Stats grid - horizontal layout for mobile
        stats_grid = GridLayout(
            cols=3, 
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Total targets
        targets_box = BoxLayout(orientation='vertical')
        self.total_targets_label = Label(
            text='0',
            halign='center',
            font_size='20sp',
            bold=True,
            color=(0.2, 0.8, 1.0, 1)
        )
        targets_subtext = Label(
            text='Targets',
            halign='center',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        targets_box.add_widget(self.total_targets_label)
        targets_box.add_widget(targets_subtext)
        stats_grid.add_widget(targets_box)
        
        # Planned
        planned_box = BoxLayout(orientation='vertical')
        self.planned_label = Label(
            text='0',
            halign='center',
            font_size='20sp',
            bold=True,
            color=(0.1, 0.8, 0.4, 1)
        )
        planned_subtext = Label(
            text='Planned',
            halign='center',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        planned_box.add_widget(self.planned_label)
        planned_box.add_widget(planned_subtext)
        stats_grid.add_widget(planned_box)
        
        # Completed
        completed_box = BoxLayout(orientation='vertical')
        self.completed_label = Label(
            text='0',
            halign='center',
            font_size='20sp',
            bold=True,
            color=(0.8, 0.4, 1.0, 1)
        )
        completed_subtext = Label(
            text='Completed',
            halign='center',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        completed_box.add_widget(self.completed_label)
        completed_box.add_widget(completed_subtext)
        stats_grid.add_widget(completed_box)
        
        stats_layout.add_widget(stats_grid)
        
        return stats_layout
    
    def create_action_buttons(self):
        """Create essential action buttons with proper spacing"""
        actions_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(10)
        )
        
        # Title
        title = Label(
            text='Quick Actions',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        actions_layout.add_widget(title)
        
        # Primary actions - 2x2 grid with essential buttons only
        actions_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(115)
        )
        
        # View Targets button (primary)
        targets_btn = Button(
            text='View Tonight\'s\nTargets',
            font_size='14sp',
            background_color=(0.2, 0.6, 1.0, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        targets_btn.bind(on_press=self.go_to_targets)
        actions_grid.add_widget(targets_btn)
        
        # Session Planner button (primary)
        session_btn = Button(
            text='Session\nPlanner',
            font_size='14sp',
            background_color=(0.1, 0.8, 0.4, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        session_btn.bind(on_press=self.go_to_session_planner)
        actions_grid.add_widget(session_btn)
        
        # Secondary actions row
        refresh_btn = Button(
            text='Refresh',
            font_size='14sp',
            background_color=(0.6, 0.6, 0.6, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        refresh_btn.bind(on_press=self.refresh_data)
        actions_grid.add_widget(refresh_btn)
        
        # Fullscreen toggle
        fullscreen_btn = Button(
            text='Fullscreen',
            font_size='14sp',
            background_color=(0.8, 0.4, 1.0, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        fullscreen_btn.bind(on_press=self.toggle_fullscreen)
        actions_grid.add_widget(fullscreen_btn)
        
        actions_layout.add_widget(actions_grid)
        
        return actions_layout
    
    def create_conditions_card(self):
        """Create compact tonight's conditions card"""
        conditions_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(8)
        )
        
        # Title
        title = Label(
            text='Tonight\'s Conditions',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        conditions_layout.add_widget(title)
        
        # Conditions grid - 2x2 for mobile
        conditions_grid = GridLayout(
            cols=2, 
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Moon phase
        self.moon_label = Label(
            text=self.get_moon_info(),
            halign='left',
            valign='middle',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.moon_label.bind(size=self.moon_label.setter('text_size'))
        conditions_grid.add_widget(self.moon_label)
        
        # Twilight times
        self.twilight_label = Label(
            text=self.get_twilight_info(),
            halign='left',
            valign='middle',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.twilight_label.bind(size=self.twilight_label.setter('text_size'))
        conditions_grid.add_widget(self.twilight_label)
        
        # Location
        self.location_label = Label(
            text=self.get_location_info(),
            halign='left',
            valign='middle',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.location_label.bind(size=self.location_label.setter('text_size'))
        conditions_grid.add_widget(self.location_label)
        
        # Session status
        self.session_label = Label(
            text=self.get_session_info(),
            halign='left',
            valign='middle',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.session_label.bind(size=self.session_label.setter('text_size'))
        conditions_grid.add_widget(self.session_label)
        
        conditions_layout.add_widget(conditions_grid)
        
        return conditions_layout
    
    def create_visibility_chart_card(self):
        """Create compact visibility chart card"""
        chart_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(300),
            spacing=dp(8)
        )
        
        # Title
        title = Label(
            text="Tonight's Visibility Chart",
            size_hint_y=None,
            height=dp(25),
            font_size='16sp',
            bold=True,
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        chart_layout.add_widget(title)
        
        # Import and create plot widget
        try:
            from mobile_app.widgets.plot_widget import PlotWidget
            self.plot_widget = PlotWidget(size_hint_y=None, height=dp(200))
            chart_layout.add_widget(self.plot_widget)
            PLOT_WIDGET_AVAILABLE = True
            
            # Auto-generate chart after a short delay to allow the app to load data
            Clock.schedule_once(self.auto_generate_chart, 2.0)
            
        except ImportError as e:
            Logger.warning(f"HomeScreen: PlotWidget not available: {e}")
            # Fallback: simple status label
            self.plot_status = Label(
                text='Plot widget not available',
                size_hint_y=None,
                height=dp(200),
                halign='center',
                valign='middle',
                color=(0.7, 0.7, 0.7, 1)
            )
            chart_layout.add_widget(self.plot_status)
            PLOT_WIDGET_AVAILABLE = False
        
        # Generate chart button (still available for manual refresh)
        generate_btn = Button(
            text='Refresh Chart',
            size_hint_y=None,
            height=dp(45),
            background_color=(0.2, 0.6, 1.0, 1.0),
            font_size='14sp'
        )
        generate_btn.bind(on_press=self.generate_visibility_chart)
        chart_layout.add_widget(generate_btn)
        
        return chart_layout
    
    def auto_generate_chart(self, dt):
        """Automatically generate the visibility chart when the home screen loads"""
        Logger.info("HomeScreen: Auto-generating visibility chart")
        self.generate_visibility_chart(None)  # Pass None since we don't have a button instance
    
    def create_highlights_card(self):
        """Create compact tonight's highlights card"""
        highlights_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(8)
        )
        
        # Title
        title = Label(
            text='Tonight\'s Highlights',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        highlights_layout.add_widget(title)
        
        # Highlights content
        self.highlights_content = Label(
            text='Loading highlights...',
            size_hint_y=None,
            height=dp(100),
            halign='left',
            valign='top',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1),
            text_size=(None, None)
        )
        highlights_layout.add_widget(self.highlights_content)
        
        # Save session button
        save_btn = Button(
            text='Save',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.1, 0.8, 0.4, 1.0),
            font_size='14sp'
        )
        save_btn.bind(on_press=self.save_session)
        highlights_layout.add_widget(save_btn)
        
        return highlights_layout
    
    def generate_visibility_chart(self, instance):
        """Generate visibility chart for tonight's targets"""
        if not self.app:
            Logger.warning("HomeScreen: No app available for chart generation")
            return
        
        try:
            # Get visible targets for tonight
            visible_targets = getattr(self.app.app_state, 'all_visible_objects', [])[:10]  # Top 10
            location = getattr(self.app.app_state, 'current_location', {})
            
            if not visible_targets:
                # Try tonights_targets as fallback
                visible_targets = getattr(self.app.app_state, 'tonights_targets', [])[:10]
            
            if not visible_targets or not location:
                Logger.warning("HomeScreen: No targets or location for chart")
                # Update status to show user what happened
                if hasattr(self, 'plot_status'):
                    self.plot_status.text = 'No targets or location available for chart'
                elif hasattr(self, 'plot_widget'):
                    self.plot_widget.show_error('No targets or location available')
                return
            
            # Try to generate actual plot if plotting is available
            if hasattr(self, 'plot_widget'):
                try:
                    from mobile_app.utils.plotting import mobile_plot_generator
                    from datetime import datetime, timedelta
                    
                    # Update widget status
                    self.plot_widget.status_label.text = 'Generating visibility chart...'
                    
                    # Generate the plot asynchronously
                    self.plot_widget.load_plot_async(
                        mobile_plot_generator.create_visibility_chart,
                        "Tonight's Visibility Chart",
                        visible_targets,
                        location
                    )
                    
                    Logger.info("HomeScreen: Visibility chart generation initiated with PlotWidget")
                    
                except Exception as e:
                    Logger.error(f"HomeScreen: Error with plot generation: {e}")
                    self.plot_widget.show_error(f"Plot generation failed: {str(e)}")
                    
            else:
                # Fallback for when plot widget is not available
                if hasattr(self, 'plot_status'):
                    self.plot_status.text = 'Generating visibility chart...'
                
                # Create a simple text representation
                def update_status(dt):
                    if hasattr(self, 'plot_status'):
                        chart_text = f'Visibility Chart for {len(visible_targets)} targets:\n\n'
                        for i, target in enumerate(visible_targets[:5]):
                            name = self.get_target_attribute(target, 'name', 'Unknown')
                            obj_type = self.get_target_attribute(target, 'object_type', 'Unknown')
                            chart_text += f'{i+1}. {name} ({obj_type})\n'
                        
                        if len(visible_targets) > 5:
                            chart_text += f'... and {len(visible_targets) - 5} more objects'
                        
                        self.plot_status.text = chart_text
                
                from kivy.clock import Clock
                Clock.schedule_once(update_status, 1.0)
                Logger.info("HomeScreen: Generated text-based visibility chart")
            
        except Exception as e:
            Logger.error(f"HomeScreen: Error generating visibility chart: {e}")
            if hasattr(self, 'plot_status'):
                self.plot_status.text = f'Error generating chart: {str(e)}'
            elif hasattr(self, 'plot_widget'):
                self.plot_widget.show_error(f'Error: {str(e)}')
    
    def update_display(self):
        """Update all display elements with improved data handling"""
        try:
            # Update conditions
            self.moon_label.text = self.get_moon_info()
            self.twilight_label.text = self.get_twilight_info()
            self.location_label.text = self.get_location_info()
            self.session_label.text = self.get_session_info()
            
            # Update stats with improved data collection
            if self.app and self.app.app_state:
                try:
                    # Initialize counters
                    total_targets = 0
                    planned_count = 0
                    completed_count = 0
                    
                    # Get total targets from multiple sources with priority
                    if hasattr(self.app.app_state, 'tonights_targets') and self.app.app_state.tonights_targets:
                        # Handle Kivy ListProperty properly
                        targets_prop = self.app.app_state.tonights_targets
                        if hasattr(targets_prop, '__len__'):
                            total_targets = len(targets_prop)
                        else:
                            # It's a Kivy ListProperty, convert to list first
                            total_targets = len(list(targets_prop))
                        log_debug(f"Found {total_targets} targets in tonights_targets")
                    elif hasattr(self.app.app_state, 'all_visible_objects') and self.app.app_state.all_visible_objects:
                        # Handle Kivy ListProperty properly
                        objects_prop = self.app.app_state.all_visible_objects
                        if hasattr(objects_prop, '__len__'):
                            total_targets = len(objects_prop)
                        else:
                            total_targets = len(list(objects_prop))
                        log_debug(f"Found {total_targets} targets in all_visible_objects")
                    elif hasattr(self.app.app_state, 'catalog_objects') and self.app.app_state.catalog_objects:
                        # Fallback to catalog objects if nothing else is available
                        # Handle Kivy ListProperty properly
                        catalog_prop = self.app.app_state.catalog_objects
                        if hasattr(catalog_prop, '__len__'):
                            total_targets = len(catalog_prop)
                        else:
                            total_targets = len(list(catalog_prop))
                        log_debug(f"Found {total_targets} targets in catalog_objects (fallback)")
                    
                    # Get planned objects count
                    if hasattr(self.app.app_state, 'planned_objects'):
                        if self.app.app_state.planned_objects:
                            # Handle Kivy ListProperty properly
                            planned_prop = self.app.app_state.planned_objects
                            if hasattr(planned_prop, '__len__'):
                                planned_count = len(planned_prop)
                            else:
                                planned_count = len(list(planned_prop))
                            log_debug(f"Found {planned_count} planned objects")
                        else:
                            planned_count = 0
                    
                    # Get completed objects count
                    if hasattr(self.app.app_state, 'completed_objects'):
                        if self.app.app_state.completed_objects:
                            # Handle Kivy ListProperty properly
                            completed_prop = self.app.app_state.completed_objects
                            if hasattr(completed_prop, '__len__'):
                                completed_count = len(completed_prop)
                            else:
                                completed_count = len(list(completed_prop))
                            log_debug(f"Found {completed_count} completed objects")
                        else:
                            completed_count = 0
                    
                    # Try session stats as additional source
                    if hasattr(self.app.app_state, 'get_session_stats'):
                        try:
                            stats = self.app.app_state.get_session_stats()
                            # Use stats values if they're higher or our counts are still 0
                            stats_total = stats.get('total_targets', 0)
                            stats_planned = stats.get('planned_count', 0)
                            stats_completed = stats.get('completed_count', 0)
                            
                            if stats_total > total_targets:
                                total_targets = stats_total
                                log_debug(f"Using session stats total: {total_targets}")
                            if stats_planned > planned_count:
                                planned_count = stats_planned
                                log_debug(f"Using session stats planned: {planned_count}")
                            if stats_completed > completed_count:
                                completed_count = stats_completed
                                log_debug(f"Using session stats completed: {completed_count}")
                                
                        except Exception as e:
                            log_warning(f"Error getting session stats: {e}")
                    
                    # Update display labels
                    self.total_targets_label.text = f"{total_targets}"
                    self.planned_label.text = f"{planned_count}"
                    self.completed_label.text = f"{completed_count}"
                    
                    log_info(f"Updated home screen stats: {total_targets} total, {planned_count} planned, {completed_count} completed")
                    
                except Exception as e:
                    log_error(f"Error updating stats", e)
                    # Set to 0 only if there's an error, not as default
                    self.total_targets_label.text = "0"
                    self.planned_label.text = "0"
                    self.completed_label.text = "0"
            else:
                # No app_state available - show loading state
                if hasattr(self, 'total_targets_label'):
                    self.total_targets_label.text = "..."
                    self.planned_label.text = "..."
                    self.completed_label.text = "..."
                log_debug("No app_state available, showing loading state")
            
            # Update highlights
            self.update_highlights()
            
        except Exception as e:
            log_error(f"Error updating display", e)
    
    def update_highlights(self):
        """Update tonight's highlights list"""
        try:
            self.highlights_content.text = self.get_highlights_content()
            
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
            moon_icon, moon_name = get_moon_phase_icon(moon_phase)
            illumination = int(moon_phase * 100)
            
            # Use simple ASCII symbols for maximum compatibility
            ascii_phases = {
                "🌑": "*",      # New Moon
                "🌒": ")",      # Waxing Crescent
                "🌓": "D",      # First Quarter
                "🌔": "(",      # Waxing Gibbous
                "🌕": "O",      # Full Moon
                "🌖": "C",      # Waning Gibbous
                "🌗": "(",      # Last Quarter
                "🌘": "("       # Waning Crescent
            }
            
            # Use ASCII symbol
            display_icon = ascii_phases.get(moon_icon, "O")
            return f"Moon: {display_icon} {illumination}%"
        except Exception as e:
            Logger.error(f"HomeScreen: Error getting moon info: {e}")
            return "Moon: O --%"
    
    def get_twilight_info(self):
        """Get twilight times using configured twilight type"""
        try:
            # Use the new centralized twilight function
            twilight_times = find_configured_twilight(datetime.now())
            
            if twilight_times and len(twilight_times) == 2:
                evening_twilight, morning_twilight = twilight_times
                
                # Get twilight type for display
                twilight_type = "Astro"  # Default
                try:
                    if self.app and hasattr(self.app.app_state, 'twilight_type'):
                        if self.app.app_state.twilight_type == 'civil':
                            twilight_type = "Civil"
                        elif self.app.app_state.twilight_type == 'nautical':
                            twilight_type = "Nautical"
                        elif self.app.app_state.twilight_type == 'astronomical':
                            twilight_type = "Astro"
                except:
                    pass
                
                # Convert to local timezone if needed
                try:
                    from astronomy import utc_to_local
                    evening_local = utc_to_local(evening_twilight)
                    return f"{twilight_type} Twilight: {evening_local.strftime('%H:%M')}"
                except:
                    return f"{twilight_type} Twilight: {evening_twilight.strftime('%H:%M')}"
            
            return "Twilight: --:--"
        except Exception as e:
            Logger.error(f"HomeScreen: Error getting twilight info: {e}")
            # Fallback to legacy function
            try:
                twilight_times = find_astronomical_twilight(datetime.now())
                if twilight_times and len(twilight_times) == 2:
                    evening_twilight, morning_twilight = twilight_times
                    try:
                        from astronomy import utc_to_local
                        evening_local = utc_to_local(evening_twilight)
                        return f"Twilight: {evening_local.strftime('%H:%M')}"
                    except:
                        return f"Twilight: {evening_twilight.strftime('%H:%M')}"
            except:
                pass
            return "Twilight: --:--"
    
    def get_location_info(self):
        """Get current location info"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                
                # Use safe attribute getter
                name = self.get_target_attribute(location, 'name', 'Unknown')
                lat = self.get_target_attribute(location, 'latitude', None) or self.get_target_attribute(location, 'lat', None)
                lon = self.get_target_attribute(location, 'longitude', None) or self.get_target_attribute(location, 'lon', None)
                
                if lat is not None and lon is not None:
                    try:
                        lat_float = float(lat)
                        lon_float = float(lon)
                        return f"Location: {name} ({lat_float:.1f}°, {lon_float:.1f}°)"
                    except (ValueError, TypeError):
                        return f"Location: {name}"
                else:
                    return f"Location: {name}"
            return "Location: Not set"
        except Exception as e:
            Logger.error(f"HomeScreen: Error getting location info: {e}")
            return "Location: Error"
    
    def get_session_info(self):
        """Get session information"""
        try:
            if self.app and self.app.app_state:
                # Handle Kivy StringProperty correctly
                strategy_prop = getattr(self.app.app_state, 'scheduling_strategy', 'max_objects')
                
                log_debug(f"Strategy property type: {type(strategy_prop)}, value: {strategy_prop}")
                
                # Get the actual string value from Kivy property
                strategy_value = 'max_objects'  # Default fallback
                
                try:
                    # Try different methods to extract the value
                    if hasattr(strategy_prop, 'get') and callable(strategy_prop.get):
                        # It's a Kivy property with get method
                        strategy_value = strategy_prop.get(self.app.app_state)
                    elif hasattr(strategy_prop, '_get') and callable(strategy_prop._get):
                        # Internal getter method
                        strategy_value = strategy_prop._get(self.app.app_state)
                    elif hasattr(strategy_prop, '__get__'):
                        # Descriptor get method
                        strategy_value = strategy_prop.__get__(self.app.app_state, type(self.app.app_state))
                    elif 'StringProperty' in str(type(strategy_prop)):
                        # Try to parse StringProperty representation
                        prop_str = str(strategy_prop)
                        # Look for patterns like "StringProperty('value')"
                        if "'" in prop_str:
                            parts = prop_str.split("'")
                            if len(parts) >= 2:
                                strategy_value = parts[1]
                        else:
                            # Fallback: try to get the name
                            strategy_value = getattr(strategy_prop, 'name', 'max_objects')
                    else:
                        # It's already a regular string or can be converted
                        strategy_value = str(strategy_prop)
                        
                    log_debug(f"Extracted strategy value: {strategy_value}")
                    
                except Exception as e:
                    log_error(f"Error extracting strategy value", e, {'strategy_prop': str(strategy_prop)})
                    strategy_value = 'max_objects'
                
                # Clean up the value
                strategy_value = str(strategy_value).strip()
                if not strategy_value or strategy_value == 'None' or 'StringProperty' in strategy_value:
                    strategy_value = 'max_objects'
                
                # Format for display
                try:
                    if hasattr(self.app.app_state, 'get_strategy_display_name'):
                        strategy_name = self.app.app_state.get_strategy_display_name(strategy_value)
                    else:
                        # Fallback formatting
                        strategy_name = strategy_value.replace('_', ' ').title()
                        
                    log_debug(f"Final strategy display: {strategy_name}")
                    return f"Strategy: {strategy_name}"
                    
                except Exception as e:
                    log_error(f"Error formatting strategy name", e, {'strategy_value': strategy_value})
                    return f"Strategy: {strategy_value.replace('_', ' ').title()}"
            
            return "Strategy: Max Objects"
            
        except Exception as e:
            log_error(f"Error getting session info", e)
            return "Strategy: Max Objects"
    
    def get_target_attribute(self, target, attr_name, default_value='Unknown'):
        """Safely get attribute from target (handles both objects and dicts)"""
        try:
            if isinstance(target, dict):
                return target.get(attr_name, default_value)
            else:
                return getattr(target, attr_name, default_value)
        except Exception:
            return default_value

    def get_highlights_content(self):
        """Get formatted highlights content"""
        try:
            if not self.app or not hasattr(self.app, 'app_state'):
                return 'App loading...'
            
            targets = getattr(self.app.app_state, 'tonights_targets', [])
            if not targets:
                location = getattr(self.app.app_state, 'current_location', {})
                if location:
                    location_name = self.get_target_attribute(location, 'name', 'current location')
                    return f'No targets loaded for {location_name}.\nTap "View Tonight\'s Targets" to see available objects.'
                else:
                    return 'No location set.\nPlease set location in Settings first.'
            
            # Show top 3 targets for mobile
            # Handle Kivy ListProperty properly
            if hasattr(targets, '__getitem__'):
                # It's subscriptable (regular list or similar)
                top_targets = targets[:3]
            else:
                # It's a Kivy ListProperty, convert to list first
                targets_list = list(targets)
                top_targets = targets_list[:3]
            highlights = []
            
            for i, target in enumerate(top_targets, 1):
                try:
                    # Use safe attribute getter for both CelestialObject and dict
                    name = self.get_target_attribute(target, 'name', 'Unknown')
                    obj_type = self.get_target_attribute(target, 'object_type', 'Unknown')
                    
                    highlights.append(f"{i}. {name} ({obj_type})")
                    
                except Exception as e:
                    log_error(f"Error processing target {i}", e, {'target': str(target)})
                    highlights.append(f"{i}. Error processing target")
            
            if highlights:
                result = '\n'.join(highlights)
                # Handle Kivy ListProperty properly for length calculation
                if hasattr(targets, '__len__'):
                    targets_count = len(targets)
                else:
                    targets_count = len(list(targets))
                result += f'\n\nTap "View Tonight\'s Targets" to see all {targets_count} targets'
                return result
            else:
                return 'Unable to load target highlights.\nPlease check targets list.'
            
        except Exception as e:
            log_error(f"Error getting highlights content", e)
            return 'Error loading highlights.\nPlease refresh the app.'
    
    def update_time_display(self, dt):
        """Periodic time update"""
        # Only update if time_label exists
        if hasattr(self, 'time_label') and self.time_label:
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
        if self.app and self.app.screen_manager:
            self.app.screen_manager.current = 'settings'
            log_navigation("home", "settings", "button")
    
    def go_to_reports(self, instance):
        """Navigate to reports screen"""
        if self.app:
            self.app.screen_manager.current = 'reports'
    
    def go_to_session_planner(self, instance):
        """Navigate to session planner screen"""
        if self.app:
            self.app.screen_manager.current = 'session_planner'
    
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

    def toggle_fullscreen(self, instance):
        """Toggle fullscreen mode"""
        try:
            from kivy.core.window import Window
            if Window.fullscreen == 'auto':
                Window.fullscreen = False
                instance.text = 'Fullscreen'
            else:
                Window.fullscreen = 'auto'
                instance.text = 'Exit Fullscreen'
        except Exception as e:
            Logger.error(f"HomeScreen: Error toggling fullscreen: {e}")

    def save_session(self, instance):
        """Save current session"""
        try:
            if self.app:
                self.app.save_settings()
                instance.text = 'Saved!'
                # Reset button text after 2 seconds
                Clock.schedule_once(lambda dt: setattr(instance, 'text', 'Save'), 2)
            else:
                Logger.warning("HomeScreen: No app available for saving")
        except Exception as e:
            Logger.error(f"HomeScreen: Error saving session: {e}")
            instance.text = 'Error'
            Clock.schedule_once(lambda dt: setattr(instance, 'text', 'Save'), 2)

    def open_settings(self, instance):
        """Navigate to settings screen"""
        if self.app and self.app.screen_manager:
            self.app.screen_manager.current = 'settings'
            log_navigation("home", "settings", "button")

    def periodic_data_check(self, dt):
        """Periodic check for data availability and update counters"""
        try:
            if self.app and self.app.app_state:
                # Check if data has been loaded
                has_targets = (hasattr(self.app.app_state, 'tonights_targets') and 
                             self.app.app_state.tonights_targets)
                has_visible = (hasattr(self.app.app_state, 'all_visible_objects') and 
                             self.app.app_state.all_visible_objects)
                has_planned = (hasattr(self.app.app_state, 'planned_objects') and 
                             self.app.app_state.planned_objects)
                
                # Check current counter values
                current_total = getattr(self.total_targets_label, 'text', '0') if hasattr(self, 'total_targets_label') else '0'
                current_planned = getattr(self.planned_label, 'text', '0') if hasattr(self, 'planned_label') else '0'
                
                # Force update if we have data but counters are still 0, or if planned count doesn't match
                should_update = False
                
                if (has_targets or has_visible) and current_total == '0':
                    should_update = True
                    log_debug("Data detected but total counter is 0, updating")
                
                if has_planned and current_planned != str(len(self.app.app_state.planned_objects)):
                    should_update = True
                    log_debug(f"Planned count mismatch: UI shows {current_planned}, actual is {len(self.app.app_state.planned_objects)}")
                
                # Also check if we have any non-zero data but UI still shows all zeros
                if (has_targets or has_visible or has_planned):
                    if current_total == '0' and current_planned == '0':
                        should_update = True
                        log_debug("Have data but UI shows all zeros, forcing update")
                
                if should_update:
                    log_info("Triggering home screen counter update due to data availability")
                    self.update_display()
                    
                    # After successful update, check if we can reduce frequency
                    new_total = getattr(self.total_targets_label, 'text', '0') if hasattr(self, 'total_targets_label') else '0'
                    if new_total != '0':
                        # Successfully updated, reduce check frequency
                        Clock.unschedule(self.periodic_data_check)
                        Clock.schedule_interval(self.periodic_data_check, 30.0)  # Check every 30s instead of 5s
                        log_debug("Reduced periodic check frequency to 30 seconds")
                        
        except Exception as e:
            log_error(f"Error in periodic data check", e)
    
    def initial_update(self, dt):
        """Initial update of data when screen is created"""
        self.update_display()
    
    def on_enter(self):
        """Called when entering the home screen"""
        log_navigation("previous", "home", "navigation")
        # Update display when screen is entered
        self.update_display()
        
        # Force additional data checks shortly after entering
        Clock.schedule_once(lambda dt: self.update_display(), 0.5)
        Clock.schedule_once(lambda dt: self.update_display(), 2.0)  # Extra check after 2 seconds