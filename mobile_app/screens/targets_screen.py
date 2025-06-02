"""
Targets Screen
Browse and filter tonight's observable targets
"""

import os
import sys
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import advanced filtering, gestures, themes, and smart scopes
try:
    from utils.advanced_filter import AdvancedFilter, FilterPresetManager, ImagingDifficulty, ObjectType
    from utils.gesture_manager import SwipeableWidget, AstronomyGestures
    from utils.theme_manager import get_theme_manager, ThemedWidget
    from utils.smart_scopes import get_scope_manager, get_all_scope_names
except ImportError:
    # Fallback if modules not available
    AdvancedFilter = None
    FilterPresetManager = None
    SwipeableWidget = object
    AstronomyGestures = None
    get_theme_manager = lambda: None
    ThemedWidget = object
    get_scope_manager = lambda: None
    get_all_scope_names = lambda: []

try:
    from analysis import calculate_object_score
    from astronomy import find_visibility_window, calculate_visibility_duration
except ImportError as e:
    Logger.error(f"TargetsScreen: Failed to import astropy modules: {e}")


class ThemedTargetCard(BoxLayout, SwipeableWidget, ThemedWidget):
    """Themed target card with gesture support"""
    
    def __init__(self, target, parent_screen, **kwargs):
        super().__init__(**kwargs)
        self.target = target
        self.parent_screen = parent_screen
        self.theme_manager = get_theme_manager()
        
        # Setup card properties
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(100)
        
        # Setup gestures
        self.setup_target_gestures()
        
        # Build card content
        self.build_card()
        
        # Apply theme
        self.apply_theme()
    
    def setup_target_gestures(self):
        """Setup gestures for target card"""
        if hasattr(self, 'gesture_manager'):
            # Swipe right to add to planned
            self.gesture_manager.register_gesture('swipe_right', self.on_swipe_add_to_plan)
            
            # Swipe left to remove from planned
            self.gesture_manager.register_gesture('swipe_left', self.on_swipe_remove_from_plan)
            
            # Long press for details
            self.gesture_manager.register_gesture('long_press', self.on_long_press_details)
            
            # Double tap for quick action
            self.gesture_manager.register_gesture('double_tap', self.on_double_tap_action)
    
    def build_card(self):
        """Build the card content"""
        # Target info row
        info_row = BoxLayout(orientation='horizontal')
        
        # Target name and type
        name = getattr(self.target, 'name', self.target.get('name', 'Unknown'))
        obj_type = getattr(self.target, 'object_type', self.target.get('object_type', 'Unknown'))
        
        self.name_label = Label(
            text=f'{name}\n{obj_type}',
            font_size='16sp',
            bold=True,
            halign='left',
            valign='middle',
            size_hint_x=0.6
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        
        # Score and details
        score = self.parent_screen.get_target_score(self.target)
        duration = self.parent_screen.get_visibility_duration(self.target)
        
        self.details_label = Label(
            text=f'Score: {score:.1f}\nDuration: {duration:.1f}h',
            font_size='14sp',
            halign='right',
            valign='middle',
            size_hint_x=0.4
        )
        self.details_label.bind(size=self.details_label.setter('text_size'))
        
        info_row.add_widget(self.name_label)
        info_row.add_widget(self.details_label)
        
        # Action buttons row
        buttons_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
        
        # View details button
        self.details_btn = Button(
            text='Details',
            font_size='14sp',
            size_hint_x=0.3
        )
        self.details_btn.bind(on_press=lambda x: self.parent_screen.view_target_details(self.target))
        
        # Add to plan button
        is_planned = self.parent_screen.app.app_state.is_target_planned(self.target)
        self.plan_btn = Button(
            text='Remove' if is_planned else 'Add to Plan',
            font_size='14sp',
            size_hint_x=0.4
        )
        self.plan_btn.bind(on_press=lambda x: self.toggle_planned())
        
        # Quick info
        self.info_label = Label(
            text=self.get_quick_info(),
            font_size='12sp',
            size_hint_x=0.3
        )
        
        buttons_row.add_widget(self.details_btn)
        buttons_row.add_widget(self.plan_btn)
        buttons_row.add_widget(self.info_label)
        
        self.add_widget(info_row)
        self.add_widget(buttons_row)
    
    def get_quick_info(self):
        """Get quick info text for target"""
        try:
            # Get magnitude if available
            mag = getattr(self.target, 'magnitude', self.target.get('magnitude', None))
            if mag is not None:
                return f'Mag: {mag:.1f}'
            
            # Get size if available
            size = getattr(self.target, 'size', self.target.get('size', None))
            if size is not None:
                return f'Size: {size:.1f}\'\''
            
            return 'Info'
        except:
            return 'Info'
    
    def apply_theme(self):
        """Apply current theme to the card"""
        if self.theme_manager:
            # Apply background color
            self.canvas.before.clear()
            with self.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(*self.theme_manager.get_color('background_card'))
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Bind to update background on size/position change
            self.bind(pos=self.update_bg, size=self.update_bg)
            
            # Apply text colors
            self.name_label.color = self.theme_manager.get_color('text_primary')
            self.details_label.color = self.theme_manager.get_color('text_secondary')
            self.info_label.color = self.theme_manager.get_color('text_hint')
            
            # Apply button colors
            self.details_btn.background_color = self.theme_manager.get_color('button_secondary')
            self.plan_btn.background_color = self.theme_manager.get_color('accent_primary')
    
    def update_bg(self, *args):
        """Update background rectangle"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def toggle_planned(self):
        """Toggle planned status"""
        if self.parent_screen.app.app_state.is_target_planned(self.target):
            self.parent_screen.app.app_state.remove_from_planned(self.target)
            self.plan_btn.text = 'Add to Plan'
        else:
            self.parent_screen.app.app_state.add_to_planned(self.target)
            self.plan_btn.text = 'Remove'
    
    def on_swipe_add_to_plan(self, data):
        """Handle swipe right gesture - add to plan"""
        if not self.parent_screen.app.app_state.is_target_planned(self.target):
            self.parent_screen.app.app_state.add_to_planned(self.target)
            self.plan_btn.text = 'Remove'
            Logger.info(f"Added {getattr(self.target, 'name', 'target')} to plan via swipe")
    
    def on_swipe_remove_from_plan(self, data):
        """Handle swipe left gesture - remove from plan"""
        if self.parent_screen.app.app_state.is_target_planned(self.target):
            self.parent_screen.app.app_state.remove_from_planned(self.target)
            self.plan_btn.text = 'Add to Plan'
            Logger.info(f"Removed {getattr(self.target, 'name', 'target')} from plan via swipe")
    
    def on_long_press_details(self, data):
        """Handle long press gesture - show details"""
        self.parent_screen.view_target_details(self.target)
        Logger.info(f"Showing details for {getattr(self.target, 'name', 'target')} via long press")
    
    def on_double_tap_action(self, data):
        """Handle double tap gesture - toggle planned status"""
        self.toggle_planned()
        Logger.info(f"Toggled planned status for {getattr(self.target, 'name', 'target')} via double tap")


class TargetsScreen(Screen, SwipeableWidget, ThemedWidget):
    """Screen for browsing and filtering targets"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.filtered_targets = []
        self.current_filter_type = 'All Types'
        self.current_sort_method = 'Score (High to Low)'
        self.search_text = ''
        
        # Initialize theme manager
        self.theme_manager = get_theme_manager()
        
        # Setup gestures
        self.setup_gestures()
        
        self.build_ui()
    
    def setup_gestures(self):
        """Setup gesture controls for the screen"""
        if hasattr(self, 'gesture_manager') and AstronomyGestures:
            # Setup standard screen navigation
            AstronomyGestures.setup_screen_navigation(self, self.app)
            
            # Custom gestures for targets screen
            self.gesture_manager.register_gesture('swipe_up', self.on_swipe_up)
            self.gesture_manager.register_gesture('swipe_down', self.on_swipe_down)
            self.gesture_manager.register_gesture('double_tap', self.on_double_tap)
    
    def on_swipe_up(self, data):
        """Handle swipe up gesture - scroll to top"""
        if hasattr(self, 'targets_scroll'):
            self.targets_scroll.scroll_y = 1.0
    
    def on_swipe_down(self, data):
        """Handle swipe down gesture - refresh targets"""
        self.refresh_targets()
    
    def on_double_tap(self, data):
        """Handle double tap gesture - quick filter toggle"""
        # Toggle between all targets and planned targets
        if self.current_filter_type == 'All Types':
            self.current_filter_type = 'Planned'
        else:
            self.current_filter_type = 'All Types'
        self.apply_filters()
    
    def apply_theme(self):
        """Apply current theme to the screen"""
        if self.theme_manager:
            # Apply theme colors to widgets
            pass  # Will be implemented when widgets are created
    
    def build_ui(self):
        """Build the targets screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header with back button and title
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Filters and controls
        controls = self.create_controls()
        main_layout.add_widget(controls)
        
        # Targets list
        targets_container = self.create_targets_list()
        main_layout.add_widget(targets_container)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header with navigation and title"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Back button
        back_btn = Button(
            text='← Home',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        # Title
        title = Label(
            text='Tonight\'s Targets',
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Refresh button
        refresh_btn = Button(
            text='↻',
            size_hint_x=None,
            width=dp(50),
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        refresh_btn.bind(on_press=self.refresh_targets)
        header.add_widget(refresh_btn)
        
        return header
    
    def create_controls(self):
        """Create filter and sort controls"""
        controls_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        # Search box
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        search_label = Label(text='Search:', size_hint_x=None, width=dp(60))
        self.search_input = TextInput(
            hint_text='Object name...',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        self.search_input.bind(text=self.on_search_text_change)
        
        search_layout.add_widget(search_label)
        search_layout.add_widget(self.search_input)
        controls_layout.add_widget(search_layout)
        
        # Filter and sort row
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # Object type filter
        type_label = Label(text='Type:', size_hint_x=None, width=dp(50))
        self.type_spinner = Spinner(
            text='All Types',
            values=['All Types', 'Galaxy', 'Nebula', 'Star Cluster', 'Planetary Nebula', 'Supernova Remnant'],
            size_hint_x=0.5
        )
        self.type_spinner.bind(text=self.on_type_filter_change)
        
        # Sort method
        sort_label = Label(text='Sort:', size_hint_x=None, width=dp(50))
        self.sort_spinner = Spinner(
            text='Score (High to Low)',
            values=[
                'Score (High to Low)',
                'Score (Low to High)',
                'Name (A-Z)',
                'Name (Z-A)',
                'Type',
                'Visibility Duration'
            ],
            size_hint_x=0.5
        )
        self.sort_spinner.bind(text=self.on_sort_change)
        
        filter_layout.add_widget(type_label)
        filter_layout.add_widget(self.type_spinner)
        filter_layout.add_widget(sort_label)
        filter_layout.add_widget(self.sort_spinner)
        
        # Advanced filter button
        advanced_filter_btn = Button(
            text='Advanced',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.3, 0.3, 0.8, 1.0)
        )
        advanced_filter_btn.bind(on_press=self.show_advanced_filter)
        filter_layout.add_widget(advanced_filter_btn)
        
        controls_layout.add_widget(filter_layout)
        
        # Options row
        options_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        # Mosaic only toggle
        mosaic_label = Label(text='Mosaic Only:', size_hint_x=None, width=dp(100))
        self.mosaic_switch = Switch(active=False, size_hint_x=None, width=dp(60))
        self.mosaic_switch.bind(active=self.on_mosaic_toggle)
        
        # Results count
        self.results_label = Label(
            text='0 targets',
            halign='right',
            valign='middle'
        )
        self.results_label.bind(size=self.results_label.setter('text_size'))
        
        options_layout.add_widget(mosaic_label)
        options_layout.add_widget(self.mosaic_switch)
        options_layout.add_widget(self.results_label)
        controls_layout.add_widget(options_layout)
        
        return controls_layout
    
    def create_targets_list(self):
        """Create scrollable targets list"""
        # Container for the scroll view
        container = BoxLayout(orientation='vertical')
        
        # Scroll view
        scroll = ScrollView()
        
        # Targets list layout
        self.targets_list = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.targets_list.bind(minimum_height=self.targets_list.setter('height'))
        
        scroll.add_widget(self.targets_list)
        container.add_widget(scroll)
        
        return container
    
    def update_targets_list(self):
        """Update the targets list based on current filters"""
        try:
            self.targets_list.clear_widgets()
            
            if not self.app or not self.app.app_state.tonights_targets:
                no_targets_label = Label(
                    text='No targets available.\nTap refresh to load tonight\'s targets.',
                    text_size=(dp(300), None),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(100)
                )
                self.targets_list.add_widget(no_targets_label)
                self.results_label.text = '0 targets'
                return
            
            # Apply filters
            self.apply_filters()
            
            # Update results count
            self.results_label.text = f'{len(self.filtered_targets)} targets'
            
            # Create target cards
            for target in self.filtered_targets:
                target_card = self.create_target_card(target)
                self.targets_list.add_widget(target_card)
            
            if not self.filtered_targets:
                no_results_label = Label(
                    text='No targets match current filters.',
                    text_size=(dp(300), None),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(60)
                )
                self.targets_list.add_widget(no_results_label)
            
        except Exception as e:
            Logger.error(f"TargetsScreen: Error updating targets list: {e}")
    
    def apply_filters(self):
        """Apply current filters to targets list"""
        try:
            targets = self.app.app_state.tonights_targets.copy()
            
            # Apply advanced filtering first (if enabled)
            if self.app.app_state.get_advanced_filter():
                targets = self.app.app_state.apply_advanced_filter(targets)
            
            # Apply type filter
            if self.current_filter_type != 'All Types':
                targets = [
                    t for t in targets
                    if getattr(t, 'object_type', t.get('object_type', '')).lower() == self.current_filter_type.lower()
                ]
            
            # Apply search filter
            if self.search_text:
                search_lower = self.search_text.lower()
                targets = [
                    t for t in targets
                    if search_lower in getattr(t, 'name', t.get('name', '')).lower()
                ]
            
            # Apply mosaic filter
            if self.mosaic_switch.active:
                targets = [
                    t for t in targets
                    if getattr(t, 'is_mosaic_candidate', t.get('is_mosaic_candidate', False))
                ]
            
            # Apply sorting
            targets = self.sort_targets(targets)
            
            self.filtered_targets = targets
            
        except Exception as e:
            Logger.error(f"TargetsScreen: Error applying filters: {e}")
            self.filtered_targets = []
    
    def sort_targets(self, targets):
        """Sort targets based on current sort method"""
        try:
            if self.current_sort_method == 'Score (High to Low)':
                return sorted(targets, key=lambda t: self.get_target_score(t), reverse=True)
            elif self.current_sort_method == 'Score (Low to High)':
                return sorted(targets, key=lambda t: self.get_target_score(t))
            elif self.current_sort_method == 'Name (A-Z)':
                return sorted(targets, key=lambda t: getattr(t, 'name', t.get('name', '')))
            elif self.current_sort_method == 'Name (Z-A)':
                return sorted(targets, key=lambda t: getattr(t, 'name', t.get('name', '')), reverse=True)
            elif self.current_sort_method == 'Type':
                return sorted(targets, key=lambda t: getattr(t, 'object_type', t.get('object_type', '')))
            elif self.current_sort_method == 'Visibility Duration':
                return sorted(targets, key=lambda t: self.get_visibility_duration(t), reverse=True)
            else:
                return targets
        except Exception as e:
            Logger.error(f"TargetsScreen: Error sorting targets: {e}")
            return targets
    
    def get_target_score(self, target):
        """Get score for a target"""
        try:
            if hasattr(target, 'score'):
                return target.score
            elif isinstance(target, dict) and 'score' in target:
                return target['score']
            else:
                # Calculate score using astropy function
                return calculate_object_score(target)
        except:
            return 0
    
    def get_visibility_duration(self, target):
        """Get visibility duration for a target"""
        try:
            if hasattr(target, 'visibility_duration'):
                return target.visibility_duration
            elif isinstance(target, dict) and 'visibility_duration' in target:
                return target['visibility_duration']
            else:
                # Calculate using astropy function
                if self.app and self.app.app_state.current_location:
                    location = self.app.app_state.current_location
                    duration = calculate_visibility_duration(
                        target,
                        datetime.now(),
                        location['latitude'],
                        location['longitude']
                    )
                    return duration
                return 0
        except:
            return 0
    
    def create_target_card(self, target):
        """Create a card widget for a target"""
        try:
            # Use the new themed target card
            return ThemedTargetCard(target, self)
            
        except Exception as e:
            Logger.error(f"TargetsScreen: Error creating target card: {e}")
            return Label(text='Error loading target', size_hint_y=None, height=dp(50))
    
    # Event handlers
    def on_search_text_change(self, instance, text):
        """Handle search text change"""
        self.search_text = text
        self.update_targets_list()
    
    def on_type_filter_change(self, instance, text):
        """Handle type filter change"""
        self.current_filter_type = text
        self.update_targets_list()
    
    def on_sort_change(self, instance, text):
        """Handle sort method change"""
        self.current_sort_method = text
        self.update_targets_list()
    
    def on_mosaic_toggle(self, instance, active):
        """Handle mosaic only toggle"""
        self.update_targets_list()
    
    def view_target_details(self, target):
        """View detailed information about a target"""
        if self.app:
            self.app.app_state.selected_target = target
            self.app.screen_manager.current = 'target_detail'
    
    def add_to_plan(self, target):
        """Add target to observation plan"""
        if self.app:
            self.app.app_state.add_to_planned(target)
            Logger.info(f"TargetsScreen: Added {getattr(target, 'name', 'target')} to plan")
    
    def refresh_targets(self, instance):
        """Refresh targets data"""
        if self.app:
            self.app.refresh_data()
            self.update_targets_list()
    
    def go_back(self, instance):
        """Navigate back to home screen"""
        if self.app:
            self.app.screen_manager.current = 'home'
    
    def on_enter(self):
        """Called when screen is entered"""
        self.update_targets_list()
    
    def show_advanced_filter(self, instance):
        """Show advanced filter popup"""
        if not AdvancedFilter:
            # Show simple message if advanced filter not available
            popup = Popup(
                title='Advanced Filter',
                content=Label(text='Advanced filtering not available'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            return
        
        # Initialize advanced filter if not exists
        if not self.app.app_state.get_advanced_filter():
            self.app.app_state.set_advanced_filter(AdvancedFilter())
        
        # Create advanced filter popup
        popup_content = self.create_advanced_filter_content()
        popup = Popup(
            title='Advanced Filter Settings',
            content=popup_content,
            size_hint=(0.9, 0.8)
        )
        popup.open()
    
    def create_advanced_filter_content(self):
        """Create advanced filter popup content"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Create tabbed panel for different filter categories
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Basic Filters Tab
        basic_tab = TabbedPanelItem(text='Basic')
        basic_content = self.create_basic_filters_tab()
        basic_tab.add_widget(basic_content)
        tab_panel.add_widget(basic_tab)
        
        # Advanced Filters Tab
        advanced_tab = TabbedPanelItem(text='Advanced')
        advanced_content = self.create_advanced_filters_tab()
        advanced_tab.add_widget(advanced_content)
        tab_panel.add_widget(advanced_tab)
        
        # Presets Tab
        presets_tab = TabbedPanelItem(text='Presets')
        presets_content = self.create_presets_tab()
        presets_tab.add_widget(presets_content)
        tab_panel.add_widget(presets_tab)
        
        main_layout.add_widget(tab_panel)
        
        # Action buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        apply_btn = Button(text='Apply Filters', background_color=(0.2, 0.8, 0.2, 1.0))
        apply_btn.bind(on_press=self.apply_advanced_filters)
        
        reset_btn = Button(text='Reset', background_color=(0.8, 0.4, 0.2, 1.0))
        reset_btn.bind(on_press=self.reset_advanced_filters)
        
        close_btn = Button(text='Close', background_color=(0.6, 0.6, 0.6, 1.0))
        close_btn.bind(on_press=self.close_advanced_filter_popup)
        
        buttons_layout.add_widget(apply_btn)
        buttons_layout.add_widget(reset_btn)
        buttons_layout.add_widget(close_btn)
        
        main_layout.add_widget(buttons_layout)
        
        return main_layout
    
    def create_basic_filters_tab(self):
        """Create basic filters tab content"""
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        filter_obj = self.app.app_state.get_advanced_filter()
        
        # Magnitude range
        mag_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        mag_layout.add_widget(Label(text='Magnitude Range', size_hint_y=None, height=dp(30)))
        
        mag_range_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.mag_min_slider = Slider(
            min=0, max=20, value=filter_obj.magnitude_range[0], step=0.1,
            size_hint_x=0.4
        )
        self.mag_max_slider = Slider(
            min=0, max=20, value=filter_obj.magnitude_range[1], step=0.1,
            size_hint_x=0.4
        )
        self.mag_range_label = Label(
            text=f'{filter_obj.magnitude_range[0]:.1f} - {filter_obj.magnitude_range[1]:.1f}',
            size_hint_x=0.2
        )
        
        self.mag_min_slider.bind(value=self.update_mag_range_label)
        self.mag_max_slider.bind(value=self.update_mag_range_label)
        
        mag_range_layout.add_widget(self.mag_min_slider)
        mag_range_layout.add_widget(self.mag_max_slider)
        mag_range_layout.add_widget(self.mag_range_label)
        
        mag_layout.add_widget(mag_range_layout)
        layout.add_widget(mag_layout)
        
        # Object size range
        size_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        size_layout.add_widget(Label(text='Object Size Range (arcmin)', size_hint_y=None, height=dp(30)))
        
        size_range_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.size_min_slider = Slider(
            min=0, max=180, value=filter_obj.size_range[0], step=1,
            size_hint_x=0.4
        )
        self.size_max_slider = Slider(
            min=0, max=180, value=filter_obj.size_range[1], step=1,
            size_hint_x=0.4
        )
        self.size_range_label = Label(
            text=f'{filter_obj.size_range[0]:.0f} - {filter_obj.size_range[1]:.0f}',
            size_hint_x=0.2
        )
        
        self.size_min_slider.bind(value=self.update_size_range_label)
        self.size_max_slider.bind(value=self.update_size_range_label)
        
        size_range_layout.add_widget(self.size_min_slider)
        size_range_layout.add_widget(self.size_max_slider)
        size_range_layout.add_widget(self.size_range_label)
        
        size_layout.add_widget(size_range_layout)
        layout.add_widget(size_layout)
        
        # Object types checkboxes
        types_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        types_layout.add_widget(Label(text='Object Types', size_hint_y=None, height=dp(30)))
        
        self.object_type_checkboxes = {}
        object_types = ['galaxy', 'nebula', 'cluster', 'planetary_nebula', 'supernova_remnant', 'star']
        
        for obj_type in object_types:
            type_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            checkbox = CheckBox(
                active=obj_type in filter_obj.object_types,
                size_hint_x=None,
                width=dp(30)
            )
            label = Label(text=obj_type.replace('_', ' ').title(), halign='left')
            label.bind(size=label.setter('text_size'))
            
            self.object_type_checkboxes[obj_type] = checkbox
            
            type_row.add_widget(checkbox)
            type_row.add_widget(label)
            types_layout.add_widget(type_row)
        
        layout.add_widget(types_layout)
        
        # Imaging difficulty
        difficulty_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        difficulty_layout.add_widget(Label(text='Imaging Difficulty', size_hint_y=None, height=dp(30)))
        
        self.difficulty_spinner = Spinner(
            text=filter_obj.imaging_difficulty,
            values=['beginner', 'intermediate', 'advanced', 'expert'],
            size_hint_y=None,
            height=dp(40)
        )
        difficulty_layout.add_widget(self.difficulty_spinner)
        layout.add_widget(difficulty_layout)
        
        # Moon avoidance
        moon_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        moon_layout.add_widget(Label(text='Avoid Moon Interference'))
        self.moon_checkbox = CheckBox(active=filter_obj.moon_avoidance)
        moon_layout.add_widget(self.moon_checkbox)
        layout.add_widget(moon_layout)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_advanced_filters_tab(self):
        """Create advanced filters tab content"""
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        filter_obj = self.app.app_state.get_advanced_filter()
        
        # Altitude range
        alt_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        alt_layout.add_widget(Label(text='Altitude Range (degrees)', size_hint_y=None, height=dp(30)))
        
        alt_range_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.alt_min_slider = Slider(
            min=0, max=90, value=filter_obj.altitude_range[0], step=1,
            size_hint_x=0.4
        )
        self.alt_max_slider = Slider(
            min=0, max=90, value=filter_obj.altitude_range[1], step=1,
            size_hint_x=0.4
        )
        self.alt_range_label = Label(
            text=f'{filter_obj.altitude_range[0]:.0f}° - {filter_obj.altitude_range[1]:.0f}°',
            size_hint_x=0.2
        )
        
        self.alt_min_slider.bind(value=self.update_alt_range_label)
        self.alt_max_slider.bind(value=self.update_alt_range_label)
        
        alt_range_layout.add_widget(self.alt_min_slider)
        alt_range_layout.add_widget(self.alt_max_slider)
        alt_range_layout.add_widget(self.alt_range_label)
        
        alt_layout.add_widget(alt_range_layout)
        layout.add_widget(alt_layout)
        
        # Minimum visibility hours
        vis_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        vis_layout.add_widget(Label(text='Minimum Visibility Hours', size_hint_y=None, height=dp(30)))
        
        self.vis_hours_slider = Slider(
            min=0, max=12, value=filter_obj.visibility_hours_min, step=0.5,
            size_hint_y=None, height=dp(40)
        )
        self.vis_hours_label = Label(
            text=f'{filter_obj.visibility_hours_min:.1f} hours',
            size_hint_y=None, height=dp(30)
        )
        self.vis_hours_slider.bind(value=self.update_vis_hours_label)
        
        vis_layout.add_widget(self.vis_hours_slider)
        vis_layout.add_widget(self.vis_hours_label)
        layout.add_widget(vis_layout)
        
        # Season preference
        season_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        season_layout.add_widget(Label(text='Season Preference', size_hint_y=None, height=dp(30)))
        
        self.season_spinner = Spinner(
            text=filter_obj.season_preference or 'Any',
            values=['Any', 'spring', 'summer', 'autumn', 'winter'],
            size_hint_y=None,
            height=dp(40)
        )
        season_layout.add_widget(self.season_spinner)
        layout.add_widget(season_layout)
        
        # Maximum exposure time
        exp_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        exp_layout.add_widget(Label(text='Maximum Exposure Time (seconds)', size_hint_y=None, height=dp(30)))
        
        self.exp_time_slider = Slider(
            min=60, max=1800, value=filter_obj.exposure_time_max, step=30,
            size_hint_y=None, height=dp(40)
        )
        self.exp_time_label = Label(
            text=f'{filter_obj.exposure_time_max:.0f}s',
            size_hint_y=None, height=dp(30)
        )
        self.exp_time_slider.bind(value=self.update_exp_time_label)
        
        exp_layout.add_widget(self.exp_time_slider)
        exp_layout.add_widget(self.exp_time_label)
        layout.add_widget(exp_layout)
        
        # Smart telescope scope selection
        scope_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        scope_layout.add_widget(Label(text='Smart Telescope Scope', size_hint_y=None, height=dp(30)))
        
        scope_selection_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Get available scopes
        scope_names = ['Default'] + get_all_scope_names()
        current_scope = filter_obj.selected_scope
        scope_manager = get_scope_manager()
        
        # Find current scope name
        current_scope_name = 'Default'
        if current_scope:
            scope_spec = scope_manager.get_scope(current_scope)
            if scope_spec:
                current_scope_name = scope_spec.name
        
        self.scope_spinner = Spinner(
            text=current_scope_name,
            values=scope_names,
            size_hint_x=0.6
        )
        
        scope_select_btn = Button(
            text='Configure',
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 0.8, 1.0)
        )
        scope_select_btn.bind(on_press=self.open_scope_selection)
        
        scope_selection_layout.add_widget(self.scope_spinner)
        scope_selection_layout.add_widget(scope_select_btn)
        
        # Mosaic mode toggle
        mosaic_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        mosaic_layout.add_widget(Label(text='Use Mosaic Mode:', size_hint_x=0.7))
        
        self.mosaic_switch = Switch(
            active=filter_obj.use_mosaic_mode,
            size_hint_x=0.3
        )
        mosaic_layout.add_widget(self.mosaic_switch)
        
        scope_layout.add_widget(scope_selection_layout)
        scope_layout.add_widget(mosaic_layout)
        layout.add_widget(scope_layout)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_presets_tab(self):
        """Create presets tab content"""
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Preset selection
        preset_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        preset_layout.add_widget(Label(text='Preset:', size_hint_x=None, width=dp(60)))
        
        preset_manager = FilterPresetManager()
        presets = preset_manager.list_presets()
        
        self.preset_spinner = Spinner(
            text='Select Preset',
            values=['Select Preset'] + presets,
            size_hint_x=0.6
        )
        
        load_preset_btn = Button(
            text='Load',
            size_hint_x=0.2,
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        load_preset_btn.bind(on_press=self.load_filter_preset)
        
        preset_layout.add_widget(self.preset_spinner)
        preset_layout.add_widget(load_preset_btn)
        layout.add_widget(preset_layout)
        
        # Save new preset
        save_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        save_layout.add_widget(Label(text='Save as:', size_hint_x=None, width=dp(60)))
        
        self.preset_name_input = TextInput(
            hint_text='Preset name...',
            multiline=False,
            size_hint_x=0.6
        )
        
        save_preset_btn = Button(
            text='Save',
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        save_preset_btn.bind(on_press=self.save_filter_preset)
        
        save_layout.add_widget(self.preset_name_input)
        save_layout.add_widget(save_preset_btn)
        layout.add_widget(save_layout)
        
        # Preset descriptions
        descriptions = BoxLayout(orientation='vertical', spacing=dp(5))
        descriptions.add_widget(Label(
            text='Built-in Presets:',
            size_hint_y=None,
            height=dp(30),
            bold=True
        ))
        descriptions.add_widget(Label(
            text='• Beginner: Bright, easy targets',
            size_hint_y=None,
            height=dp(25),
            halign='left'
        ))
        descriptions.add_widget(Label(
            text='• Deep Sky: Faint galaxies and nebulae',
            size_hint_y=None,
            height=dp(25),
            halign='left'
        ))
        descriptions.add_widget(Label(
            text='• Wide Field: Large targets for short focal lengths',
            size_hint_y=None,
            height=dp(25),
            halign='left'
        ))
        
        layout.add_widget(descriptions)
        
        return layout
    
    # Filter update methods
    def update_mag_range_label(self, instance, value):
        """Update magnitude range label"""
        min_val = self.mag_min_slider.value
        max_val = self.mag_max_slider.value
        self.mag_range_label.text = f'{min_val:.1f} - {max_val:.1f}'
    
    def update_size_range_label(self, instance, value):
        """Update size range label"""
        min_val = self.size_min_slider.value
        max_val = self.size_max_slider.value
        self.size_range_label.text = f'{min_val:.0f} - {max_val:.0f}'
    
    def update_alt_range_label(self, instance, value):
        """Update altitude range label"""
        min_val = self.alt_min_slider.value
        max_val = self.alt_max_slider.value
        self.alt_range_label.text = f'{min_val:.0f}° - {max_val:.0f}°'
    
    def update_vis_hours_label(self, instance, value):
        """Update visibility hours label"""
        self.vis_hours_label.text = f'{value:.1f} hours'
    
    def update_exp_time_label(self, instance, value):
        """Update exposure time label"""
        self.exp_time_label.text = f'{value:.0f}s'
    
    # Filter action methods
    def apply_advanced_filters(self, instance):
        """Apply advanced filter settings"""
        filter_obj = self.app.app_state.get_advanced_filter()
        
        # Update filter settings from UI
        filter_obj.magnitude_range = (self.mag_min_slider.value, self.mag_max_slider.value)
        filter_obj.size_range = (self.size_min_slider.value, self.size_max_slider.value)
        filter_obj.altitude_range = (self.alt_min_slider.value, self.alt_max_slider.value)
        filter_obj.visibility_hours_min = self.vis_hours_slider.value
        filter_obj.exposure_time_max = self.exp_time_slider.value
        filter_obj.imaging_difficulty = self.difficulty_spinner.text
        filter_obj.moon_avoidance = self.moon_checkbox.active
        
        # Update object types
        filter_obj.object_types = [
            obj_type for obj_type, checkbox in self.object_type_checkboxes.items()
            if checkbox.active
        ]
        
        # Update season preference
        season = self.season_spinner.text
        filter_obj.season_preference = None if season == 'Any' else season
        
        # Update scope selection
        scope_name = self.scope_spinner.text
        if scope_name == 'Default':
            filter_obj.selected_scope = None
        else:
            scope_manager = get_scope_manager()
            scope_id = scope_manager.get_scope_id_by_name(scope_name)
            filter_obj.selected_scope = scope_id
        
        # Update mosaic mode
        filter_obj.use_mosaic_mode = self.mosaic_switch.active
        
        # Apply filters and update display
        self.update_targets_list()
        
        # Close popup
        self.close_advanced_filter_popup(instance)
    
    def reset_advanced_filters(self, instance):
        """Reset advanced filters to defaults"""
        filter_obj = self.app.app_state.get_advanced_filter()
        filter_obj.reset_to_defaults()
        
        # Update UI elements
        self.mag_min_slider.value = filter_obj.magnitude_range[0]
        self.mag_max_slider.value = filter_obj.magnitude_range[1]
        self.size_min_slider.value = filter_obj.size_range[0]
        self.size_max_slider.value = filter_obj.size_range[1]
        self.alt_min_slider.value = filter_obj.altitude_range[0]
        self.alt_max_slider.value = filter_obj.altitude_range[1]
        self.vis_hours_slider.value = filter_obj.visibility_hours_min
        self.exp_time_slider.value = filter_obj.exposure_time_max
        self.difficulty_spinner.text = filter_obj.imaging_difficulty
        self.season_spinner.text = 'Any'
        self.moon_checkbox.active = filter_obj.moon_avoidance
        
        # Reset object type checkboxes
        for obj_type, checkbox in self.object_type_checkboxes.items():
            checkbox.active = obj_type in filter_obj.object_types
        
        # Reset scope selection
        self.scope_spinner.text = 'Default'
        self.mosaic_switch.active = filter_obj.use_mosaic_mode
    
    def load_filter_preset(self, instance):
        """Load selected filter preset"""
        preset_name = self.preset_spinner.text
        if preset_name != 'Select Preset':
            success = self.app.app_state.load_filter_preset(preset_name)
            if success:
                Logger.info(f"TargetsScreen: Loaded filter preset '{preset_name}'")
                # Update UI to reflect loaded preset
                self.reset_advanced_filters(instance)
            else:
                Logger.warning(f"TargetsScreen: Failed to load preset '{preset_name}'")
    
    def save_filter_preset(self, instance):
        """Save current filter settings as preset"""
        preset_name = self.preset_name_input.text.strip()
        if preset_name:
            self.app.app_state.save_filter_preset(preset_name)
            Logger.info(f"TargetsScreen: Saved filter preset '{preset_name}'")
            self.preset_name_input.text = ''
            
            # Update preset spinner
            presets = self.app.app_state.get_filter_presets()
            self.preset_spinner.values = ['Select Preset'] + presets
    
    def close_advanced_filter_popup(self, instance):
        """Close the advanced filter popup"""
        # Find and close the popup
        for widget in self.get_root_window().children:
            if hasattr(widget, 'title') and 'Advanced Filter' in str(widget.title):
                widget.dismiss()
                break
    
    def open_scope_selection(self, instance):
        """Open scope selection screen"""
        try:
            # Navigate to scope selection screen
            if hasattr(self.manager, 'current'):
                self.manager.current = 'scope_selection'
        except Exception as e:
            Logger.error(f"TargetsScreen: Failed to open scope selection: {e}")
            # Fallback: show simple popup with scope info
            self._show_scope_info_popup()