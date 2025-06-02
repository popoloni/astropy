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
from kivy.metrics import dp
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from analysis import calculate_object_score
    from astronomy import find_visibility_window, calculate_visibility_duration
except ImportError as e:
    Logger.error(f"TargetsScreen: Failed to import astropy modules: {e}")

class TargetsScreen(Screen):
    """Screen for browsing and filtering targets"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.filtered_targets = []
        self.current_filter_type = 'All Types'
        self.current_sort_method = 'Score (High to Low)'
        self.search_text = ''
        self.build_ui()
    
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
            # Main card layout
            card = BoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(100)
            )
            
            # Target info row
            info_row = BoxLayout(orientation='horizontal')
            
            # Target name and type
            name = getattr(target, 'name', target.get('name', 'Unknown'))
            obj_type = getattr(target, 'object_type', target.get('object_type', 'Unknown'))
            
            name_label = Label(
                text=f'{name}\n{obj_type}',
                font_size='16sp',
                bold=True,
                halign='left',
                valign='middle',
                size_hint_x=0.6
            )
            name_label.bind(size=name_label.setter('text_size'))
            
            # Score and details
            score = self.get_target_score(target)
            duration = self.get_visibility_duration(target)
            
            details_label = Label(
                text=f'Score: {score:.1f}\nDuration: {duration:.1f}h',
                font_size='14sp',
                halign='right',
                valign='middle',
                size_hint_x=0.4
            )
            details_label.bind(size=details_label.setter('text_size'))
            
            info_row.add_widget(name_label)
            info_row.add_widget(details_label)
            
            # Action buttons row
            actions_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            # View details button
            details_btn = Button(
                text='Details',
                size_hint_x=0.4,
                background_color=(0.2, 0.6, 1.0, 1.0)
            )
            details_btn.bind(on_press=lambda x, t=target: self.view_target_details(t))
            
            # Add to plan button
            plan_btn = Button(
                text='Add to Plan',
                size_hint_x=0.4,
                background_color=(0.2, 0.8, 0.2, 1.0)
            )
            plan_btn.bind(on_press=lambda x, t=target: self.add_to_plan(t))
            
            # Mosaic indicator
            if getattr(target, 'is_mosaic_candidate', target.get('is_mosaic_candidate', False)):
                mosaic_label = Label(
                    text='🧩',
                    size_hint_x=0.2,
                    font_size='20sp'
                )
                actions_row.add_widget(mosaic_label)
            else:
                actions_row.add_widget(Label(size_hint_x=0.2))  # Spacer
            
            actions_row.add_widget(details_btn)
            actions_row.add_widget(plan_btn)
            
            card.add_widget(info_row)
            card.add_widget(actions_row)
            
            # Add separator
            separator = Label(
                text='─' * 50,
                size_hint_y=None,
                height=dp(10),
                color=(0.5, 0.5, 0.5, 1.0)
            )
            card.add_widget(separator)
            
            return card
            
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