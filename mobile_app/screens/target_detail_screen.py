"""
Target Detail Screen
Detailed view of a selected astronomical target
"""

import os
import sys
from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.metrics import dp
from kivy.logger import Logger

# Add parent directory to path for astropy imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from astronomy import (
        calculate_altaz, find_visibility_window, calculate_visibility_duration,
        is_visible, calculate_required_exposure, calculate_required_panels
    )
    from analysis import calculate_object_score
except ImportError as e:
    Logger.error(f"TargetDetailScreen: Failed to import astropy modules: {e}")

class TargetDetailScreen(Screen):
    """Detailed view of a selected target"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_target = None
        self.build_ui()
    
    def build_ui(self):
        """Build the target detail screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header with back button and target name
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView()
        self.content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll.add_widget(self.content_layout)
        main_layout.add_widget(scroll)
        
        # Action buttons
        actions = self.create_action_buttons()
        main_layout.add_widget(actions)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header with navigation and target name"""
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
        
        # Target name
        self.target_name_label = Label(
            text='Target Details',
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.target_name_label.bind(size=self.target_name_label.setter('text_size'))
        header.add_widget(self.target_name_label)
        
        # Share button
        share_btn = Button(
            text='📤',
            size_hint_x=None,
            width=dp(50),
            background_color=(0.6, 0.6, 0.6, 1.0)
        )
        share_btn.bind(on_press=self.share_target)
        header.add_widget(share_btn)
        
        return header
    
    def create_action_buttons(self):
        """Create action buttons at bottom"""
        actions = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Add to plan button
        self.plan_btn = Button(
            text='Add to Plan',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        self.plan_btn.bind(on_press=self.toggle_plan)
        
        # Mosaic planning button
        self.mosaic_btn = Button(
            text='Plan Mosaic',
            background_color=(0.8, 0.4, 1.0, 1.0)
        )
        self.mosaic_btn.bind(on_press=self.plan_mosaic)
        
        actions.add_widget(self.plan_btn)
        actions.add_widget(self.mosaic_btn)
        
        return actions
    
    def update_display(self):
        """Update display with current target information"""
        try:
            if not self.app or not self.app.app_state.selected_target:
                self.show_no_target()
                return
            
            self.current_target = self.app.app_state.selected_target
            target_name = getattr(self.current_target, 'name', self.current_target.get('name', 'Unknown'))
            
            # Update header
            self.target_name_label.text = target_name
            
            # Clear and rebuild content
            self.content_layout.clear_widgets()
            
            # Basic information
            basic_info = self.create_basic_info_section()
            self.content_layout.add_widget(basic_info)
            
            # Visibility information
            visibility_info = self.create_visibility_section()
            self.content_layout.add_widget(visibility_info)
            
            # Imaging information
            imaging_info = self.create_imaging_section()
            self.content_layout.add_widget(imaging_info)
            
            # Coordinates and technical data
            technical_info = self.create_technical_section()
            self.content_layout.add_widget(technical_info)
            
            # Update action buttons
            self.update_action_buttons()
            
        except Exception as e:
            Logger.error(f"TargetDetailScreen: Error updating display: {e}")
            self.show_error()
    
    def create_basic_info_section(self):
        """Create basic information section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Basic Information',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Object type and magnitude
        obj_type = getattr(self.current_target, 'object_type', self.current_target.get('object_type', 'Unknown'))
        magnitude = getattr(self.current_target, 'magnitude', self.current_target.get('magnitude', 'N/A'))
        
        type_label = Label(
            text=f'Type: {obj_type}',
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        mag_label = Label(
            text=f'Magnitude: {magnitude}',
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        mag_label.bind(size=mag_label.setter('text_size'))
        
        # Size information
        size_info = self.get_size_info()
        size_label = Label(
            text=size_info,
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        size_label.bind(size=size_label.setter('text_size'))
        
        # Score
        score = self.calculate_target_score()
        score_label = Label(
            text=f'Observability Score: {score:.1f}/100',
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        score_label.bind(size=score_label.setter('text_size'))
        
        content.add_widget(type_label)
        content.add_widget(mag_label)
        content.add_widget(size_label)
        content.add_widget(score_label)
        
        item.add_widget(content)
        accordion.add_widget(item)
        
        # Set initial height
        accordion.height = dp(44) + dp(140)  # Header + content
        
        return accordion
    
    def create_visibility_section(self):
        """Create visibility information section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Visibility Tonight',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                
                # Current position
                current_alt, current_az = calculate_altaz(
                    self.current_target,
                    datetime.now(),
                    location['latitude'],
                    location['longitude']
                )
                
                current_pos_label = Label(
                    text=f'Current Position: Alt {current_alt:.1f}°, Az {current_az:.1f}°',
                    halign='left',
                    size_hint_y=None,
                    height=dp(30)
                )
                current_pos_label.bind(size=current_pos_label.setter('text_size'))
                
                # Visibility window
                visibility_window = find_visibility_window(
                    self.current_target,
                    datetime.now(),
                    location['latitude'],
                    location['longitude']
                )
                
                if visibility_window:
                    start_time, end_time = visibility_window
                    duration = calculate_visibility_duration(
                        self.current_target,
                        datetime.now(),
                        location['latitude'],
                        location['longitude']
                    )
                    
                    window_label = Label(
                        text=f'Visible: {start_time.strftime("%H:%M")} - {end_time.strftime("%H:%M")} ({duration:.1f}h)',
                        halign='left',
                        size_hint_y=None,
                        height=dp(30)
                    )
                    window_label.bind(size=window_label.setter('text_size'))
                else:
                    window_label = Label(
                        text='Not visible tonight',
                        halign='left',
                        size_hint_y=None,
                        height=dp(30)
                    )
                    window_label.bind(size=window_label.setter('text_size'))
                
                # Best time
                best_time = self.calculate_best_observation_time()
                best_time_label = Label(
                    text=f'Best Time: {best_time}',
                    halign='left',
                    size_hint_y=None,
                    height=dp(30)
                )
                best_time_label.bind(size=best_time_label.setter('text_size'))
                
                content.add_widget(current_pos_label)
                content.add_widget(window_label)
                content.add_widget(best_time_label)
                
            else:
                no_location_label = Label(
                    text='Location not set - cannot calculate visibility',
                    halign='left',
                    size_hint_y=None,
                    height=dp(30)
                )
                no_location_label.bind(size=no_location_label.setter('text_size'))
                content.add_widget(no_location_label)
                
        except Exception as e:
            Logger.error(f"TargetDetailScreen: Error creating visibility section: {e}")
            error_label = Label(
                text='Error calculating visibility',
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            error_label.bind(size=error_label.setter('text_size'))
            content.add_widget(error_label)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(110)
        
        return accordion
    
    def create_imaging_section(self):
        """Create imaging information section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Imaging Information',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        try:
            # Recommended exposure
            exposure_time = self.calculate_recommended_exposure()
            exposure_label = Label(
                text=f'Recommended Exposure: {exposure_time}',
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            exposure_label.bind(size=exposure_label.setter('text_size'))
            
            # Mosaic information
            mosaic_info = self.get_mosaic_info()
            mosaic_label = Label(
                text=mosaic_info,
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            mosaic_label.bind(size=mosaic_label.setter('text_size'))
            
            # Difficulty rating
            difficulty = self.calculate_difficulty_rating()
            difficulty_label = Label(
                text=f'Imaging Difficulty: {difficulty}',
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            difficulty_label.bind(size=difficulty_label.setter('text_size'))
            
            # Special notes
            notes = self.get_imaging_notes()
            if notes:
                notes_label = Label(
                    text=f'Notes: {notes}',
                    halign='left',
                    text_size=(dp(300), None),
                    size_hint_y=None,
                    height=dp(60)
                )
                content.add_widget(notes_label)
            
            content.add_widget(exposure_label)
            content.add_widget(mosaic_label)
            content.add_widget(difficulty_label)
            
        except Exception as e:
            Logger.error(f"TargetDetailScreen: Error creating imaging section: {e}")
            error_label = Label(
                text='Error loading imaging information',
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            error_label.bind(size=error_label.setter('text_size'))
            content.add_widget(error_label)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(110)
        
        return accordion
    
    def create_technical_section(self):
        """Create technical data section"""
        accordion = Accordion(orientation='vertical', size_hint_y=None)
        
        item = AccordionItem(
            title='Technical Data',
            size_hint_y=None,
            min_space=dp(44)
        )
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Coordinates
        ra = getattr(self.current_target, 'ra', self.current_target.get('ra', 'N/A'))
        dec = getattr(self.current_target, 'dec', self.current_target.get('dec', 'N/A'))
        
        coords_label = Label(
            text=f'RA: {ra}, Dec: {dec}',
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        coords_label.bind(size=coords_label.setter('text_size'))
        
        # Catalog information
        catalog_info = self.get_catalog_info()
        catalog_label = Label(
            text=catalog_info,
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        catalog_label.bind(size=catalog_label.setter('text_size'))
        
        content.add_widget(coords_label)
        content.add_widget(catalog_label)
        
        item.add_widget(content)
        accordion.add_widget(item)
        accordion.height = dp(44) + dp(80)
        
        return accordion
    
    def update_action_buttons(self):
        """Update action button states"""
        try:
            # Check if target is in plan
            if self.app and self.current_target in self.app.app_state.planned_objects:
                self.plan_btn.text = 'Remove from Plan'
                self.plan_btn.background_color = (0.8, 0.2, 0.2, 1.0)
            else:
                self.plan_btn.text = 'Add to Plan'
                self.plan_btn.background_color = (0.2, 0.8, 0.2, 1.0)
            
            # Show/hide mosaic button
            is_mosaic_candidate = getattr(self.current_target, 'is_mosaic_candidate', 
                                        self.current_target.get('is_mosaic_candidate', False))
            self.mosaic_btn.disabled = not is_mosaic_candidate
            
        except Exception as e:
            Logger.error(f"TargetDetailScreen: Error updating action buttons: {e}")
    
    # Helper methods
    def get_size_info(self):
        """Get size information for the target"""
        try:
            size_major = getattr(self.current_target, 'size_major', self.current_target.get('size_major'))
            size_minor = getattr(self.current_target, 'size_minor', self.current_target.get('size_minor'))
            
            if size_major and size_minor:
                return f'Size: {size_major:.1f}\' × {size_minor:.1f}\''
            elif size_major:
                return f'Size: {size_major:.1f}\''
            else:
                return 'Size: Unknown'
        except:
            return 'Size: Unknown'
    
    def calculate_target_score(self):
        """Calculate observability score for the target"""
        try:
            return calculate_object_score(self.current_target)
        except:
            return 0.0
    
    def calculate_best_observation_time(self):
        """Calculate best observation time"""
        try:
            if self.app and self.app.app_state.current_location:
                location = self.app.app_state.current_location
                
                # Find time of highest altitude tonight
                best_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
                best_alt = 0
                
                for hour in range(18, 30):  # 6 PM to 6 AM next day
                    test_time = datetime.now().replace(hour=hour % 24, minute=0, second=0, microsecond=0)
                    if hour >= 24:
                        test_time += timedelta(days=1)
                    
                    alt, az = calculate_altaz(
                        self.current_target,
                        test_time,
                        location['latitude'],
                        location['longitude']
                    )
                    
                    if alt > best_alt:
                        best_alt = alt
                        best_time = test_time
                
                return f"{best_time.strftime('%H:%M')} (Alt: {best_alt:.1f}°)"
            
            return "Unknown"
        except:
            return "Error calculating"
    
    def calculate_recommended_exposure(self):
        """Calculate recommended exposure time"""
        try:
            if self.app and hasattr(self.app, 'CONFIG'):
                scope_config = self.app.CONFIG.get('imaging', {}).get('scope', {})
                exposure = calculate_required_exposure(self.current_target, scope_config)
                return f"{exposure:.1f} minutes"
            return "Unknown"
        except:
            return "Unknown"
    
    def get_mosaic_info(self):
        """Get mosaic information"""
        try:
            is_mosaic = getattr(self.current_target, 'is_mosaic_candidate', 
                              self.current_target.get('is_mosaic_candidate', False))
            
            if is_mosaic:
                panels = getattr(self.current_target, 'required_panels', 
                               self.current_target.get('required_panels', 1))
                return f"Mosaic recommended: {panels} panels"
            else:
                return "Single frame suitable"
        except:
            return "Mosaic info unavailable"
    
    def calculate_difficulty_rating(self):
        """Calculate imaging difficulty rating"""
        try:
            magnitude = getattr(self.current_target, 'magnitude', self.current_target.get('magnitude', 10))
            
            if magnitude < 8:
                return "Easy ⭐"
            elif magnitude < 10:
                return "Moderate ⭐⭐"
            elif magnitude < 12:
                return "Challenging ⭐⭐⭐"
            else:
                return "Expert ⭐⭐⭐⭐"
        except:
            return "Unknown"
    
    def get_imaging_notes(self):
        """Get special imaging notes"""
        try:
            obj_type = getattr(self.current_target, 'object_type', self.current_target.get('object_type', ''))
            
            if 'nebula' in obj_type.lower():
                return "Consider narrowband filters for enhanced contrast"
            elif 'galaxy' in obj_type.lower():
                return "Long exposures recommended for faint details"
            elif 'cluster' in obj_type.lower():
                return "Wide field of view may be beneficial"
            else:
                return None
        except:
            return None
    
    def get_catalog_info(self):
        """Get catalog information"""
        try:
            catalog = getattr(self.current_target, 'catalog', self.current_target.get('catalog', 'Unknown'))
            catalog_id = getattr(self.current_target, 'catalog_id', self.current_target.get('catalog_id', ''))
            
            if catalog_id:
                return f"Catalog: {catalog} {catalog_id}"
            else:
                return f"Catalog: {catalog}"
        except:
            return "Catalog: Unknown"
    
    def show_no_target(self):
        """Show message when no target is selected"""
        self.content_layout.clear_widgets()
        self.target_name_label.text = 'No Target Selected'
        
        no_target_label = Label(
            text='No target selected.\nGo back and select a target to view details.',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100)
        )
        no_target_label.bind(size=no_target_label.setter('text_size'))
        self.content_layout.add_widget(no_target_label)
    
    def show_error(self):
        """Show error message"""
        self.content_layout.clear_widgets()
        self.target_name_label.text = 'Error'
        
        error_label = Label(
            text='Error loading target details.\nPlease try again.',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(100)
        )
        error_label.bind(size=error_label.setter('text_size'))
        self.content_layout.add_widget(error_label)
    
    # Event handlers
    def toggle_plan(self, instance):
        """Toggle target in/out of observation plan"""
        if self.app and self.current_target:
            if self.current_target in self.app.app_state.planned_objects:
                self.app.app_state.remove_from_planned(self.current_target)
                Logger.info(f"TargetDetailScreen: Removed target from plan")
            else:
                self.app.app_state.add_to_planned(self.current_target)
                Logger.info(f"TargetDetailScreen: Added target to plan")
            
            self.update_action_buttons()
    
    def plan_mosaic(self, instance):
        """Navigate to mosaic planning for this target"""
        if self.app and self.current_target:
            self.app.app_state.selected_target = self.current_target
            self.app.screen_manager.current = 'mosaic'
    
    def share_target(self, instance):
        """Share target information"""
        # TODO: Implement sharing functionality
        Logger.info("TargetDetailScreen: Share functionality not yet implemented")
    
    def go_back(self, instance):
        """Navigate back to previous screen"""
        if self.app:
            self.app.screen_manager.current = 'targets'
    
    def on_enter(self):
        """Called when screen is entered"""
        self.update_display()