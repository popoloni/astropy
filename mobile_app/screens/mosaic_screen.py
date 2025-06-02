"""
Mosaic Planning Screen
Plan and visualize mosaic imaging projects
"""

import os
import sys
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from analysis import create_mosaic_groups, analyze_mosaic_compatibility
    from astronomy import calculate_required_panels, calculate_total_area
except ImportError as e:
    Logger.error(f"MosaicScreen: Failed to import astropy modules: {e}")

class MosaicScreen(Screen):
    """Screen for mosaic planning and visualization"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_mosaic_groups = []
        self.selected_group = None
        self.build_ui()
    
    def build_ui(self):
        """Build the mosaic screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Mosaic controls
        controls = self.create_controls()
        main_layout.add_widget(controls)
        
        # Mosaic groups list
        groups_container = self.create_groups_list()
        main_layout.add_widget(groups_container)
        
        # Selected group details
        details_container = self.create_details_section()
        main_layout.add_widget(details_container)
        
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
            text='Mosaic Planning',
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Analyze button
        analyze_btn = Button(
            text='Analyze',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.8, 0.4, 1.0, 1.0)
        )
        analyze_btn.bind(on_press=self.analyze_mosaics)
        header.add_widget(analyze_btn)
        
        return header
    
    def create_controls(self):
        """Create mosaic planning controls"""
        controls_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        # FOV settings row
        fov_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        fov_label = Label(text='Field of View:', size_hint_x=None, width=dp(100))
        
        self.fov_spinner = Spinner(
            text='Auto',
            values=['Auto', 'Single Frame', 'Mosaic Mode', 'Custom'],
            size_hint_x=0.5
        )
        self.fov_spinner.bind(text=self.on_fov_change)
        
        # Overlap setting
        overlap_label = Label(text='Overlap:', size_hint_x=None, width=dp(80))
        self.overlap_slider = Slider(
            min=10, max=50, value=20, step=5,
            size_hint_x=0.3
        )
        self.overlap_value_label = Label(
            text='20%',
            size_hint_x=None,
            width=dp(50)
        )
        self.overlap_slider.bind(value=self.on_overlap_change)
        
        fov_layout.add_widget(fov_label)
        fov_layout.add_widget(self.fov_spinner)
        fov_layout.add_widget(overlap_label)
        fov_layout.add_widget(self.overlap_slider)
        fov_layout.add_widget(self.overlap_value_label)
        
        # Filter options row
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        filter_label = Label(text='Show:', size_hint_x=None, width=dp(60))
        
        self.filter_spinner = Spinner(
            text='All Targets',
            values=['All Targets', 'Mosaic Candidates Only', 'Large Objects', 'Complex Mosaics'],
            size_hint_x=0.6
        )
        self.filter_spinner.bind(text=self.on_filter_change)
        
        # Results count
        self.results_label = Label(
            text='0 groups',
            halign='right',
            valign='middle',
            size_hint_x=0.4
        )
        self.results_label.bind(size=self.results_label.setter('text_size'))
        
        filter_layout.add_widget(filter_label)
        filter_layout.add_widget(self.filter_spinner)
        filter_layout.add_widget(self.results_label)
        
        # Status row
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        self.status_label = Label(
            text='Ready to analyze mosaic opportunities',
            halign='left',
            valign='middle',
            font_size='14sp'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        
        status_layout.add_widget(self.status_label)
        
        controls_layout.add_widget(fov_layout)
        controls_layout.add_widget(filter_layout)
        controls_layout.add_widget(status_layout)
        
        return controls_layout
    
    def create_groups_list(self):
        """Create scrollable mosaic groups list"""
        container = BoxLayout(orientation='vertical')
        
        # Section title
        title = Label(
            text='Mosaic Groups',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        container.add_widget(title)
        
        # Scroll view
        scroll = ScrollView()
        
        self.groups_list = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.groups_list.bind(minimum_height=self.groups_list.setter('height'))
        
        scroll.add_widget(self.groups_list)
        container.add_widget(scroll)
        
        return container
    
    def create_details_section(self):
        """Create selected group details section"""
        details_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Section title
        title = Label(
            text='Group Details',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        details_layout.add_widget(title)
        
        # Details content
        self.details_content = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            padding=dp(10)
        )
        
        # Initially show "no selection" message
        self.show_no_selection()
        
        details_layout.add_widget(self.details_content)
        
        return details_layout
    
    def analyze_mosaics(self, instance):
        """Analyze mosaic opportunities"""
        try:
            self.status_label.text = 'Analyzing mosaic opportunities...'
            
            if not self.app or not self.app.app_state.tonights_targets:
                self.status_label.text = 'No targets available for analysis'
                return
            
            # Create mosaic groups using existing astropy function
            mosaic_groups = create_mosaic_groups(
                self.app.app_state.tonights_targets,
                fov_mode=self.fov_spinner.text,
                overlap_percent=self.overlap_slider.value
            )
            
            # Analyze compatibility
            analyzed_groups = []
            for group in mosaic_groups:
                compatibility = analyze_mosaic_compatibility(group)
                group_data = {
                    'group': group,
                    'compatibility': compatibility,
                    'panel_count': len(group.objects) if hasattr(group, 'objects') else 1,
                    'total_area': self.calculate_group_area(group),
                    'estimated_time': self.estimate_imaging_time(group)
                }
                analyzed_groups.append(group_data)
            
            self.current_mosaic_groups = analyzed_groups
            self.update_groups_list()
            
            self.status_label.text = f'Found {len(analyzed_groups)} mosaic groups'
            
        except Exception as e:
            Logger.error(f"MosaicScreen: Error analyzing mosaics: {e}")
            self.status_label.text = f'Error analyzing mosaics: {str(e)}'
    
    def update_groups_list(self):
        """Update the mosaic groups list"""
        try:
            self.groups_list.clear_widgets()
            
            if not self.current_mosaic_groups:
                no_groups_label = Label(
                    text='No mosaic groups found.\nTap "Analyze" to find mosaic opportunities.',
                    text_size=(dp(300), None),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(80)
                )
                self.groups_list.add_widget(no_groups_label)
                self.results_label.text = '0 groups'
                return
            
            # Apply filters
            filtered_groups = self.apply_group_filters()
            self.results_label.text = f'{len(filtered_groups)} groups'
            
            # Create group cards
            for i, group_data in enumerate(filtered_groups):
                group_card = self.create_group_card(group_data, i)
                self.groups_list.add_widget(group_card)
            
        except Exception as e:
            Logger.error(f"MosaicScreen: Error updating groups list: {e}")
    
    def apply_group_filters(self):
        """Apply current filters to groups list"""
        try:
            filtered = self.current_mosaic_groups.copy()
            
            filter_type = self.filter_spinner.text
            
            if filter_type == 'Mosaic Candidates Only':
                filtered = [g for g in filtered if g['panel_count'] > 1]
            elif filter_type == 'Large Objects':
                filtered = [g for g in filtered if g['total_area'] > 500]  # arcmin²
            elif filter_type == 'Complex Mosaics':
                filtered = [g for g in filtered if g['panel_count'] > 4]
            
            return filtered
            
        except Exception as e:
            Logger.error(f"MosaicScreen: Error applying filters: {e}")
            return self.current_mosaic_groups
    
    def create_group_card(self, group_data, index):
        """Create a card for a mosaic group"""
        try:
            card = BoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(120)
            )
            
            # Group header
            header_layout = BoxLayout(orientation='horizontal')
            
            group_name = f"Group {index + 1}"
            if hasattr(group_data['group'], 'name'):
                group_name = group_data['group'].name
            elif hasattr(group_data['group'], 'objects') and group_data['group'].objects:
                first_obj = group_data['group'].objects[0]
                obj_name = getattr(first_obj, 'name', first_obj.get('name', 'Unknown'))
                group_name = f"{obj_name} Group"
            
            name_label = Label(
                text=group_name,
                font_size='16sp',
                bold=True,
                halign='left',
                valign='middle',
                size_hint_x=0.7
            )
            name_label.bind(size=name_label.setter('text_size'))
            
            # Panel count badge
            panel_badge = Label(
                text=f"{group_data['panel_count']} panels",
                font_size='14sp',
                halign='right',
                valign='middle',
                size_hint_x=0.3
            )
            panel_badge.bind(size=panel_badge.setter('text_size'))
            
            header_layout.add_widget(name_label)
            header_layout.add_widget(panel_badge)
            
            # Group details
            details_layout = BoxLayout(orientation='horizontal')
            
            area_text = f"Area: {group_data['total_area']:.0f} arcmin²"
            time_text = f"Time: {group_data['estimated_time']:.1f}h"
            compatibility = group_data['compatibility']
            compat_text = f"Compatibility: {compatibility:.0f}%"
            
            details_label = Label(
                text=f"{area_text} | {time_text} | {compat_text}",
                font_size='12sp',
                halign='left',
                valign='middle'
            )
            details_label.bind(size=details_label.setter('text_size'))
            
            details_layout.add_widget(details_label)
            
            # Action buttons
            actions_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            select_btn = Button(
                text='Select',
                size_hint_x=0.3,
                background_color=(0.2, 0.6, 1.0, 1.0)
            )
            select_btn.bind(on_press=lambda x, g=group_data: self.select_group(g))
            
            plan_btn = Button(
                text='Add to Plan',
                size_hint_x=0.4,
                background_color=(0.2, 0.8, 0.2, 1.0)
            )
            plan_btn.bind(on_press=lambda x, g=group_data: self.add_group_to_plan(g))
            
            # Difficulty indicator
            difficulty = self.calculate_group_difficulty(group_data)
            difficulty_label = Label(
                text=difficulty,
                size_hint_x=0.3,
                font_size='12sp'
            )
            
            actions_layout.add_widget(select_btn)
            actions_layout.add_widget(plan_btn)
            actions_layout.add_widget(difficulty_label)
            
            card.add_widget(header_layout)
            card.add_widget(details_layout)
            card.add_widget(actions_layout)
            
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
            Logger.error(f"MosaicScreen: Error creating group card: {e}")
            return Label(text='Error loading group', size_hint_y=None, height=dp(50))
    
    def select_group(self, group_data):
        """Select a mosaic group for detailed view"""
        try:
            self.selected_group = group_data
            self.update_group_details()
            Logger.info(f"MosaicScreen: Selected mosaic group with {group_data['panel_count']} panels")
        except Exception as e:
            Logger.error(f"MosaicScreen: Error selecting group: {e}")
    
    def update_group_details(self):
        """Update the group details section"""
        try:
            self.details_content.clear_widgets()
            
            if not self.selected_group:
                self.show_no_selection()
                return
            
            group_data = self.selected_group
            
            # Group summary
            summary_label = Label(
                text=f"Selected: {group_data['panel_count']} panel mosaic",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            summary_label.bind(size=summary_label.setter('text_size'))
            self.details_content.add_widget(summary_label)
            
            # Technical details
            details_text = (
                f"Total Area: {group_data['total_area']:.0f} arcmin²\n"
                f"Estimated Time: {group_data['estimated_time']:.1f} hours\n"
                f"Compatibility: {group_data['compatibility']:.0f}%\n"
                f"Overlap: {self.overlap_slider.value:.0f}%"
            )
            
            details_label = Label(
                text=details_text,
                font_size='14sp',
                size_hint_y=None,
                height=dp(80),
                halign='left',
                valign='top'
            )
            details_label.bind(size=details_label.setter('text_size'))
            self.details_content.add_widget(details_label)
            
            # Action buttons for selected group
            actions_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            visualize_btn = Button(
                text='Visualize',
                background_color=(0.8, 0.4, 1.0, 1.0)
            )
            visualize_btn.bind(on_press=self.visualize_group)
            
            export_btn = Button(
                text='Export Plan',
                background_color=(0.6, 0.6, 0.6, 1.0)
            )
            export_btn.bind(on_press=self.export_group)
            
            actions_layout.add_widget(visualize_btn)
            actions_layout.add_widget(export_btn)
            
            self.details_content.add_widget(actions_layout)
            
        except Exception as e:
            Logger.error(f"MosaicScreen: Error updating group details: {e}")
    
    def show_no_selection(self):
        """Show message when no group is selected"""
        self.details_content.clear_widgets()
        
        no_selection_label = Label(
            text='No group selected.\nSelect a mosaic group above to view details.',
            text_size=(dp(300), None),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(60)
        )
        self.details_content.add_widget(no_selection_label)
    
    # Helper methods
    def calculate_group_area(self, group):
        """Calculate total area of a mosaic group"""
        try:
            if hasattr(group, 'total_area'):
                return group.total_area
            elif hasattr(group, 'objects'):
                return calculate_total_area(group.objects)
            else:
                return 100  # Default estimate
        except:
            return 100
    
    def estimate_imaging_time(self, group):
        """Estimate total imaging time for a group"""
        try:
            panel_count = len(group.objects) if hasattr(group, 'objects') else 1
            base_time = 2.0  # hours per panel
            return panel_count * base_time
        except:
            return 2.0
    
    def calculate_group_difficulty(self, group_data):
        """Calculate difficulty rating for a group"""
        try:
            panel_count = group_data['panel_count']
            
            if panel_count == 1:
                return "Easy ⭐"
            elif panel_count <= 4:
                return "Moderate ⭐⭐"
            elif panel_count <= 9:
                return "Hard ⭐⭐⭐"
            else:
                return "Expert ⭐⭐⭐⭐"
        except:
            return "Unknown"
    
    # Event handlers
    def on_fov_change(self, instance, text):
        """Handle FOV setting change"""
        Logger.info(f"MosaicScreen: FOV changed to {text}")
    
    def on_overlap_change(self, instance, value):
        """Handle overlap slider change"""
        self.overlap_value_label.text = f'{int(value)}%'
    
    def on_filter_change(self, instance, text):
        """Handle filter change"""
        self.update_groups_list()
    
    def add_group_to_plan(self, group_data):
        """Add mosaic group to observation plan"""
        try:
            if self.app and hasattr(group_data['group'], 'objects'):
                for obj in group_data['group'].objects:
                    self.app.app_state.add_to_planned(obj)
                Logger.info(f"MosaicScreen: Added {group_data['panel_count']} objects to plan")
        except Exception as e:
            Logger.error(f"MosaicScreen: Error adding group to plan: {e}")
    
    def visualize_group(self, instance):
        """Visualize the selected mosaic group"""
        # TODO: Implement mosaic visualization
        Logger.info("MosaicScreen: Mosaic visualization not yet implemented")
    
    def export_group(self, instance):
        """Export mosaic group plan"""
        # TODO: Implement export functionality
        Logger.info("MosaicScreen: Export functionality not yet implemented")
    
    def go_back(self, instance):
        """Navigate back to previous screen"""
        if self.app:
            self.app.screen_manager.current = 'home'
    
    def on_enter(self):
        """Called when screen is entered"""
        # Auto-analyze if we have a selected target
        if (self.app and self.app.app_state.selected_target and 
            getattr(self.app.app_state.selected_target, 'is_mosaic_candidate', False)):
            self.analyze_mosaics(None)