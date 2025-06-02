"""
Session Planner Screen
Advanced observation session planning interface
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.filechooser import FileChooserIconView
from kivy.metrics import dp
from kivy.logger import Logger
from datetime import datetime, timedelta
import os
import tempfile

try:
    from utils.session_planner import SessionType, OptimizationStrategy, SessionPriority
    SESSION_PLANNER_AVAILABLE = True
except ImportError:
    SESSION_PLANNER_AVAILABLE = False


class SessionPlannerScreen(Screen):
    """Session planning and management screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_session = None
        self.selected_targets = []
        self.build_ui()
    
    def build_ui(self):
        """Build the session planner interface"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.3, 0.3, 0.3, 1.0)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='Session Planner',
            font_size='20sp',
            bold=True
        )
        
        new_session_btn = Button(
            text='New Session',
            size_hint_x=None,
            width=dp(120),
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        new_session_btn.bind(on_press=self.create_new_session)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        header_layout.add_widget(new_session_btn)
        
        main_layout.add_widget(header_layout)
        
        # Check if session planner is available
        if not SESSION_PLANNER_AVAILABLE:
            error_label = Label(
                text='Session planning not available.\nRequired modules not installed.',
                halign='center',
                valign='middle'
            )
            main_layout.add_widget(error_label)
            self.add_widget(main_layout)
            return
        
        # Tabbed interface
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Current Session Tab
        current_tab = TabbedPanelItem(text='Current Session')
        current_content = self.create_current_session_tab()
        current_tab.add_widget(current_content)
        tab_panel.add_widget(current_tab)
        
        # Create Session Tab
        create_tab = TabbedPanelItem(text='Create Session')
        create_content = self.create_session_creation_tab()
        create_tab.add_widget(create_content)
        tab_panel.add_widget(create_tab)
        
        # Saved Sessions Tab
        saved_tab = TabbedPanelItem(text='Saved Sessions')
        saved_content = self.create_saved_sessions_tab()
        saved_tab.add_widget(saved_content)
        tab_panel.add_widget(saved_tab)
        
        main_layout.add_widget(tab_panel)
        self.add_widget(main_layout)
    
    def create_current_session_tab(self):
        """Create current session display tab"""
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Session info section
        self.session_info_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(200),
            spacing=dp(5)
        )
        layout.add_widget(self.session_info_layout)
        
        # Session controls
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        save_btn = Button(
            text='Save Session',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        save_btn.bind(on_press=self.save_current_session)
        
        export_btn = Button(
            text='Export',
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        export_btn.bind(on_press=self.export_current_session)
        
        clear_btn = Button(
            text='Clear',
            background_color=(0.8, 0.4, 0.2, 1.0)
        )
        clear_btn.bind(on_press=self.clear_current_session)
        
        controls_layout.add_widget(save_btn)
        controls_layout.add_widget(export_btn)
        controls_layout.add_widget(clear_btn)
        
        layout.add_widget(controls_layout)
        
        # Target schedule section
        self.schedule_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.schedule_layout.bind(minimum_height=self.schedule_layout.setter('height'))
        layout.add_widget(self.schedule_layout)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_session_creation_tab(self):
        """Create session creation tab"""
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        layout.bind(minimum_height=layout.setter('height'))
        
        # Session basic info
        info_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
        info_section.add_widget(Label(text='Session Information', font_size='16sp', bold=True, size_hint_y=None, height=dp(30)))
        
        # Session name
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        name_layout.add_widget(Label(text='Name:', size_hint_x=None, width=dp(80)))
        self.session_name_input = TextInput(
            hint_text='Enter session name...',
            multiline=False
        )
        name_layout.add_widget(self.session_name_input)
        info_section.add_widget(name_layout)
        
        # Date selection
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        date_layout.add_widget(Label(text='Date:', size_hint_x=None, width=dp(80)))
        self.date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            hint_text='YYYY-MM-DD',
            multiline=False
        )
        date_layout.add_widget(self.date_input)
        info_section.add_widget(date_layout)
        
        # Duration
        duration_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        duration_layout.add_widget(Label(text='Duration (hours)', size_hint_y=None, height=dp(30)))
        self.duration_slider = Slider(
            min=1, max=12, value=4, step=0.5,
            size_hint_y=None, height=dp(40)
        )
        self.duration_label = Label(text='4.0 hours', size_hint_y=None, height=dp(30))
        self.duration_slider.bind(value=self.update_duration_label)
        duration_layout.add_widget(self.duration_slider)
        duration_layout.add_widget(self.duration_label)
        info_section.add_widget(duration_layout)
        
        layout.add_widget(info_section)
        
        # Session type and optimization
        options_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        options_section.add_widget(Label(text='Session Options', font_size='16sp', bold=True, size_hint_y=None, height=dp(30)))
        
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        type_layout.add_widget(Label(text='Type:', size_hint_x=None, width=dp(80)))
        self.session_type_spinner = Spinner(
            text='Mixed',
            values=['Visual', 'Imaging', 'Mixed', 'Survey', 'Specific Target']
        )
        type_layout.add_widget(self.session_type_spinner)
        options_section.add_widget(type_layout)
        
        opt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        opt_layout.add_widget(Label(text='Strategy:', size_hint_x=None, width=dp(80)))
        self.optimization_spinner = Spinner(
            text='Balanced',
            values=['Maximize Targets', 'Maximize Quality', 'Balanced', 'Time Efficient', 'Priority Based']
        )
        opt_layout.add_widget(self.optimization_spinner)
        options_section.add_widget(opt_layout)
        
        layout.add_widget(options_section)
        
        # Target selection
        targets_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
        targets_section.add_widget(Label(text='Target Selection', font_size='16sp', bold=True, size_hint_y=None, height=dp(30)))
        
        # Target selection buttons
        target_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        from_planned_btn = Button(text='From Planned')
        from_planned_btn.bind(on_press=self.select_from_planned)
        
        from_filtered_btn = Button(text='From Filtered')
        from_filtered_btn.bind(on_press=self.select_from_filtered)
        
        custom_select_btn = Button(text='Custom Selection')
        custom_select_btn.bind(on_press=self.custom_target_selection)
        
        target_buttons.add_widget(from_planned_btn)
        target_buttons.add_widget(from_filtered_btn)
        target_buttons.add_widget(custom_select_btn)
        targets_section.add_widget(target_buttons)
        
        # Selected targets display
        self.selected_targets_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200)
        )
        targets_scroll = ScrollView(size_hint_y=None, height=dp(200))
        targets_scroll.add_widget(self.selected_targets_layout)
        targets_section.add_widget(targets_scroll)
        
        layout.add_widget(targets_section)
        
        # Create session button
        create_btn = Button(
            text='Create Session Plan',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        create_btn.bind(on_press=self.create_session_plan)
        layout.add_widget(create_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_saved_sessions_tab(self):
        """Create saved sessions management tab"""
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Header with refresh button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        header_layout.add_widget(Label(text='Saved Sessions', font_size='16sp', bold=True))
        
        refresh_btn = Button(
            text='Refresh',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.3, 0.6, 1.0, 1.0)
        )
        refresh_btn.bind(on_press=self.refresh_saved_sessions)
        header_layout.add_widget(refresh_btn)
        
        layout.add_widget(header_layout)
        
        # Sessions list
        self.sessions_scroll = ScrollView()
        self.sessions_list = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.sessions_list.bind(minimum_height=self.sessions_list.setter('height'))
        self.sessions_scroll.add_widget(self.sessions_list)
        
        layout.add_widget(self.sessions_scroll)
        
        return layout
    
    def update_duration_label(self, instance, value):
        """Update duration label"""
        self.duration_label.text = f'{value:.1f} hours'
    
    def select_from_planned(self, instance):
        """Select targets from planned list"""
        if not self.app or not self.app.app_state.planned_objects:
            self.show_message("No planned targets available")
            return
        
        self.selected_targets = self.app.app_state.planned_objects.copy()
        self.update_selected_targets_display()
    
    def select_from_filtered(self, instance):
        """Select targets from filtered list"""
        if not self.app or not self.app.app_state.tonights_targets:
            self.show_message("No targets available")
            return
        
        # Use filtered targets if advanced filter is active
        if self.app.app_state.get_advanced_filter():
            self.selected_targets = self.app.app_state.get_filtered_targets()
        else:
            self.selected_targets = self.app.app_state.tonights_targets.copy()
        
        self.update_selected_targets_display()
    
    def custom_target_selection(self, instance):
        """Show custom target selection dialog"""
        self.show_target_selection_popup()
    
    def show_target_selection_popup(self):
        """Show target selection popup"""
        if not self.app or not self.app.app_state.tonights_targets:
            self.show_message("No targets available")
            return
        
        popup_content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Target list with checkboxes
        scroll = ScrollView()
        targets_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        targets_layout.bind(minimum_height=targets_layout.setter('height'))
        
        self.target_checkboxes = {}
        
        for target in self.app.app_state.tonights_targets:
            target_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            checkbox = CheckBox(
                active=target in self.selected_targets,
                size_hint_x=None,
                width=dp(30)
            )
            
            target_name = getattr(target, 'name', target.get('name', 'Unknown'))
            target_type = getattr(target, 'object_type', target.get('object_type', 'Unknown'))
            magnitude = getattr(target, 'magnitude', target.get('magnitude', 0))
            
            label = Label(
                text=f"{target_name} ({target_type}, mag {magnitude:.1f})",
                halign='left'
            )
            label.bind(size=label.setter('text_size'))
            
            self.target_checkboxes[target_name] = (checkbox, target)
            
            target_row.add_widget(checkbox)
            target_row.add_widget(label)
            targets_layout.add_widget(target_row)
        
        scroll.add_widget(targets_layout)
        popup_content.add_widget(scroll)
        
        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        select_all_btn = Button(text='Select All')
        select_all_btn.bind(on_press=self.select_all_targets)
        
        clear_all_btn = Button(text='Clear All')
        clear_all_btn.bind(on_press=self.clear_all_targets)
        
        ok_btn = Button(text='OK', background_color=(0.2, 0.8, 0.2, 1.0))
        ok_btn.bind(on_press=self.apply_target_selection)
        
        cancel_btn = Button(text='Cancel', background_color=(0.8, 0.4, 0.2, 1.0))
        cancel_btn.bind(on_press=self.close_target_selection)
        
        buttons_layout.add_widget(select_all_btn)
        buttons_layout.add_widget(clear_all_btn)
        buttons_layout.add_widget(ok_btn)
        buttons_layout.add_widget(cancel_btn)
        
        popup_content.add_widget(buttons_layout)
        
        self.target_selection_popup = Popup(
            title='Select Targets',
            content=popup_content,
            size_hint=(0.9, 0.8)
        )
        self.target_selection_popup.open()
    
    def select_all_targets(self, instance):
        """Select all targets in popup"""
        for checkbox, target in self.target_checkboxes.values():
            checkbox.active = True
    
    def clear_all_targets(self, instance):
        """Clear all target selections in popup"""
        for checkbox, target in self.target_checkboxes.values():
            checkbox.active = False
    
    def apply_target_selection(self, instance):
        """Apply target selection from popup"""
        self.selected_targets = []
        for checkbox, target in self.target_checkboxes.values():
            if checkbox.active:
                self.selected_targets.append(target)
        
        self.update_selected_targets_display()
        self.target_selection_popup.dismiss()
    
    def close_target_selection(self, instance):
        """Close target selection popup"""
        self.target_selection_popup.dismiss()
    
    def update_selected_targets_display(self):
        """Update the selected targets display"""
        self.selected_targets_layout.clear_widgets()
        
        if not self.selected_targets:
            no_targets_label = Label(
                text='No targets selected',
                size_hint_y=None,
                height=dp(30)
            )
            self.selected_targets_layout.add_widget(no_targets_label)
            return
        
        for target in self.selected_targets:
            target_name = getattr(target, 'name', target.get('name', 'Unknown'))
            target_type = getattr(target, 'object_type', target.get('object_type', 'Unknown'))
            magnitude = getattr(target, 'magnitude', target.get('magnitude', 0))
            
            target_label = Label(
                text=f"• {target_name} ({target_type}, mag {magnitude:.1f})",
                size_hint_y=None,
                height=dp(25),
                halign='left'
            )
            target_label.bind(size=target_label.setter('text_size'))
            self.selected_targets_layout.add_widget(target_label)
    
    def create_session_plan(self, instance):
        """Create the session plan"""
        if not self.app:
            self.show_message("App not available")
            return
        
        if not self.selected_targets:
            self.show_message("Please select targets first")
            return
        
        try:
            # Parse date
            date_str = self.date_input.text
            session_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Get duration in minutes
            duration_hours = self.duration_slider.value
            duration_minutes = int(duration_hours * 60)
            
            # Convert UI values to enum values
            session_type_map = {
                'Visual': SessionType.VISUAL,
                'Imaging': SessionType.IMAGING,
                'Mixed': SessionType.MIXED,
                'Survey': SessionType.SURVEY,
                'Specific Target': SessionType.SPECIFIC_TARGET
            }
            
            optimization_map = {
                'Maximize Targets': OptimizationStrategy.MAXIMIZE_TARGETS,
                'Maximize Quality': OptimizationStrategy.MAXIMIZE_QUALITY,
                'Balanced': OptimizationStrategy.BALANCED,
                'Time Efficient': OptimizationStrategy.TIME_EFFICIENT,
                'Priority Based': OptimizationStrategy.PRIORITY_BASED
            }
            
            session_type = session_type_map.get(self.session_type_spinner.text, SessionType.MIXED)
            optimization = optimization_map.get(self.optimization_spinner.text, OptimizationStrategy.BALANCED)
            
            # Convert targets to dictionaries
            target_dicts = []
            for target in self.selected_targets:
                if hasattr(target, '__dict__'):
                    target_dict = target.__dict__.copy()
                else:
                    target_dict = target.copy()
                target_dicts.append(target_dict)
            
            # Create priorities (default to medium for all)
            priorities = ['medium'] * len(target_dicts)
            
            # Get location (use default if not available)
            location = getattr(self.app.app_state, 'location', {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'name': 'Default Location'
            })
            
            # Create session
            session = self.app.app_state.create_new_session(
                date=session_date,
                duration=duration_minutes,
                priorities=priorities,
                targets=target_dicts,
                location=location,
                session_type=session_type,
                optimization_strategy=optimization
            )
            
            if session:
                # Update session name if provided
                if self.session_name_input.text.strip():
                    session.name = self.session_name_input.text.strip()
                
                self.current_session = session
                self.app.app_state.current_session = session
                self.update_current_session_display()
                self.show_message("Session plan created successfully!")
            else:
                self.show_message("Failed to create session plan")
                
        except ValueError as e:
            self.show_message(f"Invalid date format: {e}")
        except Exception as e:
            Logger.error(f"SessionPlanner: Error creating session: {e}")
            self.show_message(f"Error creating session: {e}")
    
    def update_current_session_display(self):
        """Update the current session display"""
        self.session_info_layout.clear_widgets()
        self.schedule_layout.clear_widgets()
        
        if not self.current_session:
            no_session_label = Label(
                text='No current session',
                size_hint_y=None,
                height=dp(50)
            )
            self.session_info_layout.add_widget(no_session_label)
            return
        
        # Session info
        info_data = [
            f"Name: {self.current_session.name}",
            f"Date: {self.current_session.date.strftime('%Y-%m-%d')}",
            f"Duration: {self.current_session.duration // 60:.1f} hours",
            f"Type: {self.current_session.session_type.value.title()}",
            f"Strategy: {self.current_session.optimization_strategy.value.replace('_', ' ').title()}",
            f"Targets: {len(self.current_session.targets)}",
            f"Backup Targets: {len(self.current_session.backup_targets)}"
        ]
        
        for info in info_data:
            info_label = Label(
                text=info,
                size_hint_y=None,
                height=dp(25),
                halign='left'
            )
            info_label.bind(size=info_label.setter('text_size'))
            self.session_info_layout.add_widget(info_label)
        
        # Target schedule
        schedule_title = Label(
            text='Target Schedule:',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        self.schedule_layout.add_widget(schedule_title)
        
        for i, target in enumerate(self.current_session.targets, 1):
            start_time = target.optimal_start_time.strftime('%H:%M') if target.optimal_start_time else 'TBD'
            target_info = f"{i}. {start_time} - {target.name} ({target.estimated_time} min)"
            
            target_label = Label(
                text=target_info,
                size_hint_y=None,
                height=dp(25),
                halign='left'
            )
            target_label.bind(size=target_label.setter('text_size'))
            self.schedule_layout.add_widget(target_label)
    
    def save_current_session(self, instance):
        """Save the current session"""
        if not self.current_session:
            self.show_message("No session to save")
            return
        
        if self.app and self.app.app_state.save_current_session():
            self.show_message("Session saved successfully!")
            self.refresh_saved_sessions(None)
        else:
            self.show_message("Failed to save session")
    
    def export_current_session(self, instance):
        """Export the current session"""
        if not self.current_session:
            self.show_message("No session to export")
            return
        
        self.show_export_options()
    
    def show_export_options(self):
        """Show export format options"""
        popup_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        popup_content.add_widget(Label(text='Select Export Format:', size_hint_y=None, height=dp(30)))
        
        # Format buttons
        formats = [
            ('PDF', 'pdf', (0.8, 0.2, 0.2, 1.0)),
            ('HTML', 'html', (0.2, 0.6, 1.0, 1.0)),
            ('Text', 'txt', (0.2, 0.8, 0.2, 1.0)),
            ('JSON', 'json', (0.8, 0.6, 0.2, 1.0))
        ]
        
        for format_name, format_code, color in formats:
            btn = Button(
                text=format_name,
                size_hint_y=None,
                height=dp(40),
                background_color=color
            )
            btn.bind(on_press=lambda x, fmt=format_code: self.export_session_format(fmt))
            popup_content.add_widget(btn)
        
        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.6, 0.6, 0.6, 1.0)
        )
        cancel_btn.bind(on_press=self.close_export_popup)
        popup_content.add_widget(cancel_btn)
        
        self.export_popup = Popup(
            title='Export Session',
            content=popup_content,
            size_hint=(0.6, 0.7)
        )
        self.export_popup.open()
    
    def export_session_format(self, format_code):
        """Export session in specified format"""
        self.export_popup.dismiss()
        
        if not self.app:
            self.show_message("App not available")
            return
        
        try:
            output_path = self.app.app_state.export_session(self.current_session, format_code)
            if output_path:
                self.show_message(f"Session exported to:\n{output_path}")
            else:
                self.show_message("Export failed")
        except Exception as e:
            Logger.error(f"SessionPlanner: Export error: {e}")
            self.show_message(f"Export error: {e}")
    
    def close_export_popup(self, instance):
        """Close export popup"""
        self.export_popup.dismiss()
    
    def clear_current_session(self, instance):
        """Clear the current session"""
        self.current_session = None
        if self.app:
            self.app.app_state.current_session = None
        self.update_current_session_display()
        self.show_message("Session cleared")
    
    def refresh_saved_sessions(self, instance):
        """Refresh the saved sessions list"""
        if not self.app:
            return
        
        self.app.app_state.refresh_saved_sessions()
        self.update_saved_sessions_display()
    
    def update_saved_sessions_display(self):
        """Update the saved sessions display"""
        self.sessions_list.clear_widgets()
        
        if not self.app or not self.app.app_state.saved_sessions:
            no_sessions_label = Label(
                text='No saved sessions',
                size_hint_y=None,
                height=dp(50)
            )
            self.sessions_list.add_widget(no_sessions_label)
            return
        
        for session_info in self.app.app_state.saved_sessions:
            session_card = self.create_session_card(session_info)
            self.sessions_list.add_widget(session_card)
    
    def create_session_card(self, session_info):
        """Create a card for a saved session"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        
        # Session info
        info_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70))
        
        name_label = Label(
            text=session_info.get('name', 'Unnamed Session'),
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        date_str = session_info.get('date', datetime.now()).strftime('%Y-%m-%d') if isinstance(session_info.get('date'), datetime) else str(session_info.get('date', 'Unknown'))
        details_label = Label(
            text=f"Date: {date_str} | Duration: {session_info.get('duration', 0)//60:.1f}h | Targets: {session_info.get('target_count', 0)}",
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        details_label.bind(size=details_label.setter('text_size'))
        
        type_label = Label(
            text=f"Type: {session_info.get('session_type', 'Unknown').title()}",
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(details_label)
        info_layout.add_widget(type_label)
        
        # Action buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        load_btn = Button(
            text='Load',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        load_btn.bind(on_press=lambda x, sid=session_info['session_id']: self.load_saved_session(sid))
        
        export_btn = Button(
            text='Export',
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        export_btn.bind(on_press=lambda x, sid=session_info['session_id']: self.export_saved_session(sid))
        
        delete_btn = Button(
            text='Delete',
            background_color=(0.8, 0.4, 0.2, 1.0)
        )
        delete_btn.bind(on_press=lambda x, sid=session_info['session_id']: self.delete_saved_session(sid))
        
        buttons_layout.add_widget(load_btn)
        buttons_layout.add_widget(export_btn)
        buttons_layout.add_widget(delete_btn)
        
        card.add_widget(info_layout)
        card.add_widget(buttons_layout)
        
        # Add separator
        separator = Label(
            text='─' * 50,
            size_hint_y=None,
            height=dp(10),
            color=(0.5, 0.5, 0.5, 1.0)
        )
        card.add_widget(separator)
        
        return card
    
    def load_saved_session(self, session_id):
        """Load a saved session"""
        if not self.app:
            return
        
        session = self.app.app_state.load_session(session_id)
        if session:
            self.current_session = session
            self.update_current_session_display()
            self.show_message("Session loaded successfully!")
        else:
            self.show_message("Failed to load session")
    
    def export_saved_session(self, session_id):
        """Export a saved session"""
        if not self.app:
            return
        
        session = self.app.app_state.load_session(session_id)
        if session:
            self.current_session = session
            self.show_export_options()
        else:
            self.show_message("Failed to load session for export")
    
    def delete_saved_session(self, session_id):
        """Delete a saved session"""
        if not self.app:
            return
        
        # Show confirmation dialog
        self.show_delete_confirmation(session_id)
    
    def show_delete_confirmation(self, session_id):
        """Show delete confirmation dialog"""
        popup_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        popup_content.add_widget(Label(
            text='Are you sure you want to delete this session?',
            size_hint_y=None,
            height=dp(40)
        ))
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        yes_btn = Button(
            text='Yes, Delete',
            background_color=(0.8, 0.2, 0.2, 1.0)
        )
        yes_btn.bind(on_press=lambda x: self.confirm_delete_session(session_id))
        
        no_btn = Button(
            text='Cancel',
            background_color=(0.6, 0.6, 0.6, 1.0)
        )
        no_btn.bind(on_press=self.close_delete_confirmation)
        
        buttons_layout.add_widget(yes_btn)
        buttons_layout.add_widget(no_btn)
        popup_content.add_widget(buttons_layout)
        
        self.delete_popup = Popup(
            title='Confirm Delete',
            content=popup_content,
            size_hint=(0.6, 0.4)
        )
        self.delete_popup.open()
    
    def confirm_delete_session(self, session_id):
        """Confirm session deletion"""
        self.delete_popup.dismiss()
        
        if self.app.app_state.delete_session(session_id):
            self.update_saved_sessions_display()
            self.show_message("Session deleted successfully!")
        else:
            self.show_message("Failed to delete session")
    
    def close_delete_confirmation(self, instance):
        """Close delete confirmation dialog"""
        self.delete_popup.dismiss()
    
    def create_new_session(self, instance):
        """Switch to create session tab"""
        # This would switch to the create session tab
        # Implementation depends on how tabs are managed
        pass
    
    def show_message(self, message):
        """Show a message popup"""
        popup = Popup(
            title='Session Planner',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def go_back(self, instance):
        """Navigate back to previous screen"""
        if self.app:
            self.app.screen_manager.current = 'home'
    
    def on_enter(self):
        """Called when screen is entered"""
        if self.app:
            # Initialize session planner if needed
            self.app.app_state.initialize_session_planner()
            
            # Update current session display
            self.current_session = self.app.app_state.current_session
            self.update_current_session_display()
            
            # Update saved sessions
            self.refresh_saved_sessions(None)