"""
Reports Screen
Display and manage generated reports
"""

import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.logger import Logger

try:
    from utils.reports import mobile_report_generator
    REPORTS_AVAILABLE = True
except ImportError as e:
    Logger.warning(f"ReportsScreen: Reports not available: {e}")
    REPORTS_AVAILABLE = False

class ReportsScreen(Screen):
    """Screen for viewing and managing reports"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_report = None
        self.build_ui()
    
    def build_ui(self):
        """Build the reports screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Report type selection
        report_types = self.create_report_types()
        main_layout.add_widget(report_types)
        
        # Report display area
        report_display = self.create_report_display()
        main_layout.add_widget(report_display)
        
        # Action buttons
        actions = self.create_action_buttons()
        main_layout.add_widget(actions)
        
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
        
        # Title
        title = Label(
            text='Reports',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        return header
    
    def create_report_types(self):
        """Create report type selection buttons"""
        types_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Session report button
        session_btn = Button(
            text='Session Report',
            background_color=(0.2, 0.6, 1.0, 1.0)
        )
        session_btn.bind(on_press=self.generate_session_report)
        
        # Target report button
        target_btn = Button(
            text='Target Report',
            background_color=(0.6, 0.2, 1.0, 1.0)
        )
        target_btn.bind(on_press=self.generate_target_report)
        
        # Mosaic report button
        mosaic_btn = Button(
            text='Mosaic Report',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        mosaic_btn.bind(on_press=self.generate_mosaic_report)
        
        types_layout.add_widget(session_btn)
        types_layout.add_widget(target_btn)
        types_layout.add_widget(mosaic_btn)
        
        return types_layout
    
    def create_report_display(self):
        """Create report display area"""
        # Scrollable text area for report content
        self.report_text = TextInput(
            text='Select a report type above to generate a report.',
            multiline=True,
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp'
        )
        
        scroll = ScrollView()
        scroll.add_widget(self.report_text)
        
        return scroll
    
    def create_action_buttons(self):
        """Create action buttons for reports"""
        actions_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Save report button
        save_btn = Button(
            text='Save Report',
            background_color=(0.2, 0.8, 0.2, 1.0)
        )
        save_btn.bind(on_press=self.save_report)
        
        # Share report button
        share_btn = Button(
            text='Share Report',
            background_color=(0.8, 0.6, 0.2, 1.0)
        )
        share_btn.bind(on_press=self.share_report)
        
        # Clear button
        clear_btn = Button(
            text='Clear',
            background_color=(0.8, 0.2, 0.2, 1.0)
        )
        clear_btn.bind(on_press=self.clear_report)
        
        actions_layout.add_widget(save_btn)
        actions_layout.add_widget(share_btn)
        actions_layout.add_widget(clear_btn)
        
        return actions_layout
    
    def generate_session_report(self, instance):
        """Generate session report"""
        if not REPORTS_AVAILABLE:
            self.show_error("Reports functionality not available")
            return
        
        if not self.app or not self.app.app_state:
            self.show_error("No app data available")
            return
        
        try:
            self.report_text.text = "Generating session report..."
            
            # Generate report
            report_content = mobile_report_generator.generate_session_report(self.app.app_state)
            
            self.report_text.text = report_content
            self.current_report = report_content
            
            Logger.info("ReportsScreen: Session report generated")
            
        except Exception as e:
            Logger.error(f"ReportsScreen: Error generating session report: {e}")
            self.show_error(f"Error generating report: {str(e)}")
    
    def generate_target_report(self, instance):
        """Generate target report"""
        if not REPORTS_AVAILABLE:
            self.show_error("Reports functionality not available")
            return
        
        if not self.app or not self.app.app_state:
            self.show_error("No app data available")
            return
        
        selected_target = self.app.app_state.selected_target
        if not selected_target:
            self.show_error("No target selected. Please select a target first.")
            return
        
        try:
            self.report_text.text = "Generating target report..."
            
            # Generate report
            report_content = mobile_report_generator.generate_target_report(
                selected_target, self.app.app_state
            )
            
            self.report_text.text = report_content
            self.current_report = report_content
            
            Logger.info("ReportsScreen: Target report generated")
            
        except Exception as e:
            Logger.error(f"ReportsScreen: Error generating target report: {e}")
            self.show_error(f"Error generating report: {str(e)}")
    
    def generate_mosaic_report(self, instance):
        """Generate mosaic report"""
        if not REPORTS_AVAILABLE:
            self.show_error("Reports functionality not available")
            return
        
        if not self.app or not self.app.app_state:
            self.show_error("No app data available")
            return
        
        # For now, use a placeholder mosaic group
        # In a real implementation, this would come from the mosaic screen
        mosaic_groups = [
            {
                'name': 'Example Mosaic',
                'panel_count': 4,
                'total_time': 2.5
            }
        ]
        
        try:
            self.report_text.text = "Generating mosaic report..."
            
            # Generate report
            report_content = mobile_report_generator.generate_mosaic_report(
                mosaic_groups, self.app.app_state
            )
            
            self.report_text.text = report_content
            self.current_report = report_content
            
            Logger.info("ReportsScreen: Mosaic report generated")
            
        except Exception as e:
            Logger.error(f"ReportsScreen: Error generating mosaic report: {e}")
            self.show_error(f"Error generating report: {str(e)}")
    
    def save_report(self, instance):
        """Save current report to file"""
        if not self.current_report:
            self.show_error("No report to save")
            return
        
        try:
            if REPORTS_AVAILABLE:
                file_path = mobile_report_generator.save_report_to_file(self.current_report)
                if file_path:
                    self.show_success(f"Report saved to:\n{os.path.basename(file_path)}")
                else:
                    self.show_error("Failed to save report")
            else:
                self.show_error("Save functionality not available")
                
        except Exception as e:
            Logger.error(f"ReportsScreen: Error saving report: {e}")
            self.show_error(f"Error saving report: {str(e)}")
    
    def share_report(self, instance):
        """Share current report"""
        if not self.current_report:
            self.show_error("No report to share")
            return
        
        # In a real mobile app, this would use platform-specific sharing
        # For now, just show the report content in a popup
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        text_input = TextInput(
            text=self.current_report,
            multiline=True,
            readonly=True,
            size_hint_y=0.8
        )
        content.add_widget(text_input)
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Share Report',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def clear_report(self, instance):
        """Clear current report"""
        self.report_text.text = 'Select a report type above to generate a report.'
        self.current_report = None
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_success(self, message):
        """Show success popup"""
        popup = Popup(
            title='Success',
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
        # Auto-generate session report if no report is displayed
        if not self.current_report and REPORTS_AVAILABLE:
            self.generate_session_report(None)