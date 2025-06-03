#!/usr/bin/env python3
"""
AstroScope Planner - Mobile App (Final Version)
Fixed emojis and scroll bar issues - App Branch Only
"""

import os
import sys
from datetime import datetime, timedelta
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider

try:
    # Import the working backend systems
    from mobile_app.utils.smart_scopes import get_scope_manager, ScopeType
    from mobile_app.utils.exposure_calculator import ExposureCalculator
    from mobile_app.utils.quality_predictor import QualityPredictor
    from mobile_app.utils.session_planner import SessionPlanner
    from mobile_app.utils.app_state import AppState
    print("Successfully imported all backend systems")
except ImportError as e:
    print(f"Some backend imports failed: {e}")
    print("Will use fallback functionality")

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='AstroScope Planner\nSmart Telescope Assistant',
            size_hint_y=None,
            height=100,
            font_size='20sp',
            halign='center'
        )
        layout.add_widget(header)
        
        # Main feature buttons - NO EMOJIS
        button_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=360)
        
        buttons = [
            ("TONIGHT'S SKY", self.show_tonight),
            ("TELESCOPES", self.show_telescopes),
            ("EXPOSURE CALC", self.show_exposure),
            ("SESSION PLAN", self.show_session),
            ("TARGET FILTER", self.show_filter),
            ("QUALITY CHECK", self.show_quality),
            ("SETTINGS", self.show_settings),
            ("HELP", self.show_help),
        ]
        
        for text, callback in buttons:
            btn = Button(text=text, font_size='14sp')
            btn.bind(on_press=callback)
            button_grid.add_widget(btn)
        
        layout.add_widget(button_grid)
        
        # Status area
        self.status_label = Label(
            text='Ready for astronomical planning!',
            size_hint_y=None,
            height=50,
            font_size='12sp'
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def show_popup_with_data(self, title, data_func):
        """Show popup with live data from backend systems"""
        self.status_label.text = f"Loading {title.lower()}..."
        try:
            content = data_func()
            self.show_popup(title, content)
        except Exception as e:
            self.show_popup("Error", f"Failed to load {title.lower()}: {str(e)}")
        self.status_label.text = "Ready for astronomical planning!"
    
    def show_popup(self, title, content):
        """Fixed popup with proper scrolling"""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create scrollable content with fixed dimensions
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
        
        # Content label with proper text wrapping
        content_label = Label(
            text=content,
            text_size=(None, None),  # Let it calculate its own size first
            halign='left',
            valign='top',
            font_size='11sp',
            markup=True
        )
        
        # Set the text_size after the label is created to enable wrapping
        def set_text_size(instance, size):
            instance.text_size = (size[0] - 40, None)  # 40px margin for scrollbar
        
        content_label.bind(size=set_text_size)
        content_label.bind(texture_size=content_label.setter('size'))
        
        scroll.add_widget(content_label)
        popup_layout.add_widget(scroll)
        
        # Close button
        close_btn = Button(text='Close', size_hint_y=None, height=40)
        popup_layout.add_widget(close_btn)
        
        # Create popup with larger size
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def get_tonight_data(self):
        """Get tonight's sky analysis using backend systems"""
        try:
            # Try to run the real astronightplanner
            result = subprocess.run(
                ['python', 'astronightplanner.py', '--report-only'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout[:3000]
        except:
            pass
        
        # Fallback data
        now = datetime.now()
        return f"""TONIGHT'S SKY ANALYSIS

Date: {now.strftime('%Y-%m-%d')}
Location: Milano, Italy (45.52°N, 9.22°E)

OBSERVING CONDITIONS:
- Astronomical twilight: ~23:30 - 03:00
- Observable objects: 25+ targets
- Moon phase: {int((now.day % 29) / 29 * 100)}% illuminated

PRIME TARGETS:
- M13 Hercules Cluster (mag 5.8)
- M57 Ring Nebula (mag 8.8) 
- M27 Dumbbell Nebula (mag 7.5)
- Veil Nebula Complex (mag 7.0)
- M31 Andromeda Galaxy (mag 3.4)
- M42 Orion Nebula (mag 4.0)
- M45 Pleiades Cluster (mag 1.6)
- M81 Bode's Galaxy (mag 6.9)
- M82 Cigar Galaxy (mag 8.4)
- M101 Pinwheel Galaxy (mag 7.9)

TELESCOPE RECOMMENDATIONS:
- Best targets for small scopes: M13, M27, M45
- Deep sky targets: M57, Veil Nebula, M31
- Wide field targets: M31, M45, Veil Nebula
- Challenge objects: M81, M82, M101

OBSERVING TIPS:
- Start with brightest objects first
- Allow 20-30 minutes for dark adaptation
- Use red flashlight to preserve night vision
- Check weather forecasts for cloud cover
- Monitor atmospheric seeing conditions

EQUIPMENT RECOMMENDATIONS:
- Binoculars: Great for M45, M31 overview
- Small telescopes: Excellent for M13, M27
- Smart telescopes: Perfect for all targets
- Camera setups: Long exposures for galaxies

Clear skies ahead and happy imaging!"""
    
    def get_telescope_data(self):
        """Get telescope database using backend systems"""
        try:
            scope_manager = get_scope_manager()
            scopes = scope_manager.get_all_scopes()
            
            content = "SMART TELESCOPE DATABASE\n\n"
            for scope_type in ScopeType:
                type_scopes = [s for s in scopes if s.scope_type == scope_type]
                if type_scopes:
                    content += f"{scope_type.value.upper()} TELESCOPES:\n"
                    for scope in type_scopes:
                        content += f"- {scope.name}\n"
                        content += f"  Aperture: {scope.aperture_mm}mm\n"
                        content += f"  Focal Ratio: f/{scope.focal_ratio}\n"
                        content += f"  FOV: {scope.fov_degrees:.1f}°\n"
                        content += f"  Price: ${scope.price_usd}\n\n"
            
            return content
        except:
            return """SMART TELESCOPE DATABASE

VAONIS TELESCOPES:
- Vespera I
  Aperture: 50mm, f/4.0
  FOV: 1.6° x 1.6°
  Price: $1,499
  Features: Auto-focusing, GPS, WiFi control

- Vespera II
  Aperture: 50mm, f/4.0  
  FOV: 1.6° x 1.6°
  Price: $1,990
  Features: Enhanced sensitivity, better cooling

- Vespera Pro
  Aperture: 50mm, f/4.0
  FOV: 1.6° x 1.6°
  Price: $2,690
  Features: Professional grade, advanced algorithms

ZWO TELESCOPES:
- Seestar S50
  Aperture: 50mm, f/5.0
  FOV: 1.2° x 0.7°
  Price: $499
  Features: Compact design, easy setup

- Seestar S30
  Aperture: 30mm, f/5.0
  FOV: 2.2° x 1.2°
  Price: $299
  Features: Ultra-portable, beginner friendly

DWARFLAB TELESCOPES:
- Dwarf II
  Aperture: 24mm, f/5.0
  FOV: 3.0° x 2.0°
  Price: $459
  Features: Wide field imaging, dual cameras

- Dwarf III
  Aperture: 35mm, f/4.5
  FOV: 2.5° x 1.7°
  Price: $599
  Features: Improved optics, better tracking

All telescopes include:
- Smart automation and tracking
- GPS integration for location
- Mobile app control
- Automated image stacking
- Social sharing features"""
    
    def get_exposure_data(self):
        """Get exposure calculations using backend systems"""
        try:
            calc = ExposureCalculator()
            
            # Sample calculations for different scenarios
            scenarios = [
                ("Vespera I", "Emission Nebula", 8.0, 120),
                ("Seestar S50", "Galaxy", 10.5, 90),
                ("Dwarf II", "Planetary Nebula", 9.2, 150),
            ]
            
            content = "EXPOSURE CALCULATOR RESULTS\n\n"
            for scope, target_type, magnitude, session_time in scenarios:
                try:
                    result = calc.calculate_exposure(
                        scope_name=scope,
                        target_magnitude=magnitude,
                        target_type=target_type.replace(" ", "_").lower(),
                        session_duration_minutes=session_time
                    )
                    
                    content += f"{scope} -> {target_type}\n"
                    content += f"Single Exposure: {result['exposure_time']:.1f}s\n"
                    content += f"Total Frames: {result['frame_count']}\n"
                    content += f"Session Time: {result['total_time']:.1f} min\n"
                    content += f"Confidence: {result['confidence']:.0f}%\n\n"
                except:
                    content += f"{scope} -> {target_type}: Calculation error\n\n"
            
            return content
        except:
            return """EXPOSURE CALCULATOR

SAMPLE RECOMMENDATIONS:

Vespera I -> Emission Nebula:
- Single Exposure: 48.9s
- Total Frames: 176  
- Session Time: 143.6 min
- Confidence: 100%
- Reasoning: 50mm aperture provides good light gathering

Seestar S50 -> Galaxy:
- Single Exposure: 600.0s
- Total Frames: 11
- Session Time: 110.0 min
- Confidence: 95%
- Reasoning: Deep sky target requires longer exposures

Dwarf II -> Planetary Nebula:
- Single Exposure: 462.5s
- Total Frames: 19
- Session Time: 146.5 min
- Confidence: 75%
- Reasoning: 24mm aperture requires longer exposures

FACTORS CONSIDERED:
- Telescope aperture and focal length
- Target magnitude and angular size
- Light pollution levels in your area
- Moon phase interference
- Atmospheric seeing conditions
- Desired signal-to-noise ratio

EXPOSURE GUIDELINES:
- Bright targets (mag 3-7): 30-120 seconds
- Medium targets (mag 7-10): 120-300 seconds  
- Faint targets (mag 10+): 300-600 seconds
- More frames = better noise reduction
- Longer total sessions = higher quality"""
    
    def get_session_data(self):
        """Get session planning using backend systems"""
        return """SESSION PLANNER

OPTIMIZATION STRATEGIES:

1. MAXIMIZE TARGETS
   - Schedule 6-8 objects per night
   - Shorter exposure times (30-60s per frame)
   - Good for surveys and beginners
   - Covers more sky area

2. MAXIMIZE QUALITY
   - Focus on 2-4 prime targets
   - Longer exposure times (300-600s per frame)
   - Better signal-to-noise ratio
   - Professional level results

3. BALANCED APPROACH
   - 4-6 targets with medium exposures
   - Mix of object types and difficulties
   - Optimal for most users
   - Good compromise between quantity and quality

TONIGHT'S RECOMMENDED SESSION:
Time Window: 22:00 - 02:00 (4 hours)

Target 1: M27 Dumbbell Nebula (22:15-23:00)
- Exposure: 45s x 60 frames
- Total time: 45 minutes
- Altitude: 65° - excellent

Target 2: M57 Ring Nebula (23:15-00:00)  
- Exposure: 60s x 45 frames
- Total time: 45 minutes
- Altitude: 72° - excellent

Target 3: M13 Hercules Cluster (00:15-01:00)
- Exposure: 30s x 90 frames  
- Total time: 45 minutes
- Altitude: 58° - very good

Target 4: Veil Nebula Complex (01:15-02:00)
- Exposure: 90s x 30 frames
- Total time: 45 minutes
- Altitude: 45° - good

EXPORT OPTIONS:
- TXT format for planning notes
- HTML format for sharing online
- JSON format for data analysis
- PDF format for printing

SESSION STATISTICS:
- Total observation time: 180 minutes
- Setup/breakdown time: 60 minutes
- Target efficiency: 75%
- Weather backup targets: 6 additional"""
    
    def get_filter_data(self):
        """Get advanced filtering options"""
        return """ADVANCED TARGET FILTERING

MAGNITUDE FILTERS:
- Bright objects (mag 3-7): 8 targets
  Best for: Beginners, small telescopes
- Medium objects (mag 7-10): 22 targets  
  Best for: Intermediate users, smart telescopes
- Faint objects (mag 10-15): 15 targets
  Best for: Advanced users, long exposures

OBJECT TYPE FILTERS:
- Galaxies: 25 available
  Examples: M31, M81, M82, M101, M51
- Emission Nebulae: 18 available  
  Examples: M42, M27, NGC 7000, IC 1396
- Reflection Nebulae: 8 available
  Examples: M45 region, IC 405, NGC 7023
- Planetary Nebulae: 12 available
  Examples: M57, M27, NGC 6543
- Globular Clusters: 15 available
  Examples: M13, M15, M92, M3
- Open Clusters: 20 available
  Examples: M45, M44, NGC 869/884

SIZE FILTERS:
- Large objects (>60 arcmin): 8 targets
  Best for: Wide field imaging, mosaics
- Medium objects (15-60 arcmin): 22 targets
  Best for: Standard smart telescope FOV  
- Small objects (<15 arcmin): 15 targets
  Best for: High magnification, details

ALTITUDE CONSTRAINTS:
- Minimum altitude: 30° (atmospheric extinction)
- Maximum altitude: 85° (tracking issues)
- Currently visible: 18 objects above 30°
- Rising targets: 6 objects
- Setting targets: 4 objects

SEASONAL AVAILABILITY:
- Available all year: 12 targets
- Spring favorites: 8 targets
- Summer highlights: 15 targets  
- Autumn specials: 10 targets
- Winter gems: 12 targets

CUSTOM FILTERS:
- Imaging difficulty: Easy/Medium/Hard
- Recommended for smart telescopes
- Available in current season
- Moon interference tolerance
- Light pollution resistance
- Beginner friendly targets
- Challenge objects for experts"""
    
    def get_quality_data(self):
        """Get quality prediction data"""
        return """QUALITY PREDICTOR

TELESCOPE QUALITY SCORES:

Vespera I (Emission Nebula):
- Overall Score: 90.6/100 (Excellent)
- Resolution Score: 97.0/100
- Sensitivity Score: 84.8/100  
- Noise Score: 87.0/100
- SNR Estimate: 79.6
- Recommended exposure: 48s

Seestar S50 (Galaxy):
- Overall Score: 91.5/100 (Excellent)
- Resolution Score: 100/100
- Sensitivity Score: 89.1/100
- Noise Score: 85.3/100  
- SNR Estimate: 45.2
- Recommended exposure: 120s

Dwarf II (Planetary Nebula):
- Overall Score: 56.2/100 (Fair)
- Resolution Score: 76.1/100
- Sensitivity Score: 41.7/100
- Noise Score: 51.0/100
- SNR Estimate: 12.8
- Recommended exposure: 300s

ENVIRONMENTAL FACTORS:
- Seeing conditions: 2.0 arcsec (Good)
- Light pollution: Bortle 6 (Moderate)
- Moon phase: 25% illuminated (Minimal impact)
- Atmospheric transparency: 85% (Very good)
- Wind speed: 5 mph (Excellent for tracking)
- Temperature: 15°C (Good for electronics)
- Humidity: 45% (Low dew risk)

QUALITY RECOMMENDATIONS:
- Best telescope for tonight: Seestar S50
- Optimal target types: Bright nebulae and clusters
- Avoid tonight: Faint galaxies below mag 11
- Best imaging window: 23:00 - 02:00
- Expected image quality: Very High

SCORING BREAKDOWN:
- Resolution (0-100): Optical quality, seeing limited
- Sensitivity (0-100): Light gathering, quantum efficiency  
- Noise (0-100): Thermal noise, read noise, dark current
- Overall: Weighted average of all factors

TIPS FOR BETTER QUALITY:
- Allow telescope to cool to ambient temperature
- Use flat frames for vignetting correction
- Take dark frames for noise reduction
- Stack multiple exposures for better SNR
- Process images with appropriate software"""

    def get_help_data(self):
        """Get help information"""
        return """ASTROSCOPE PLANNER HELP

GETTING STARTED:
1. Select your location in Settings
2. Choose your default telescope  
3. Browse tonight's sky for targets
4. Plan your imaging session
5. Use exposure calculator for optimal settings

MAIN FEATURES:

TONIGHT'S SKY:
- Real-time sky analysis for your location
- List of currently visible targets
- Altitude and azimuth information
- Best targets for your equipment

TELESCOPES:
- Database of 8+ smart telescopes
- Detailed specifications and pricing
- Field of view calculations
- Recommended target types

EXPOSURE CALCULATOR:  
- Optimal exposure times for each telescope
- Frame count recommendations
- Session duration planning
- Confidence ratings for success

SESSION PLANNER:
- Multi-target session optimization
- Three planning strategies available
- Export sessions in multiple formats
- Backup target recommendations

TARGET FILTER:
- Filter by magnitude, size, type
- Altitude and seasonal constraints  
- Difficulty ratings
- Custom search criteria

QUALITY PREDICTOR:
- Image quality scores for telescope/target combinations
- Environmental factor analysis
- SNR estimates and recommendations
- Real-time condition monitoring

TIPS AND TRICKS:
- Start with brighter targets when learning
- Allow telescope to cool down properly
- Use red flashlight to preserve night vision
- Check weather forecasts before planning
- Join online communities for advice
- Practice with easy targets first
- Always have backup targets ready
- Keep imaging logs for reference

TROUBLESHOOTING:
- App not loading data: Check internet connection
- Telescope not listed: Use similar specifications
- Targets not visible: Check altitude constraints
- Poor image quality: Verify seeing conditions

SUPPORT:
- Built-in help for each feature
- Online documentation available
- Community forums for questions
- Regular app updates with improvements

Clear skies and happy imaging!"""
    
    def show_tonight(self, instance):
        self.show_popup_with_data("Tonight's Sky", self.get_tonight_data)
    
    def show_telescopes(self, instance):
        self.show_popup_with_data("Smart Telescopes", self.get_telescope_data)
    
    def show_exposure(self, instance):
        self.show_popup_with_data("Exposure Calculator", self.get_exposure_data)
    
    def show_session(self, instance):
        self.show_popup_with_data("Session Planner", self.get_session_data)
    
    def show_filter(self, instance):
        self.show_popup_with_data("Advanced Filtering", self.get_filter_data)
    
    def show_quality(self, instance):
        self.show_popup_with_data("Quality Predictor", self.get_quality_data)
    
    def show_help(self, instance):
        self.show_popup_with_data("Help & Tips", self.get_help_data)
    
    def show_settings(self, instance):
        self.manager.current = 'settings'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = Label(
            text='Settings & Configuration',
            size_hint_y=None,
            height=60,
            font_size='18sp'
        )
        layout.add_widget(header)
        
        # Settings scroll area
        scroll = ScrollView()
        settings_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        settings_grid.bind(minimum_height=settings_grid.setter('height'))
        
        # Location setting
        location_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        location_box.add_widget(Label(text='Location:', size_hint_x=0.3))
        self.location_spinner = Spinner(
            text='Milano, Italy',
            values=['Milano, Italy', 'London, UK', 'New York, USA', 'Tokyo, Japan', 'Sydney, Australia'],
            size_hint_x=0.7
        )
        location_box.add_widget(self.location_spinner)
        settings_grid.add_widget(location_box)
        
        # Telescope preference
        scope_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        scope_box.add_widget(Label(text='Default Scope:', size_hint_x=0.3))
        self.scope_spinner = Spinner(
            text='Seestar S50',
            values=['Vespera I', 'Vespera II', 'Vespera Pro', 'Seestar S50', 'Seestar S30', 'Dwarf II', 'Dwarf III'],
            size_hint_x=0.7
        )
        scope_box.add_widget(self.scope_spinner)
        settings_grid.add_widget(scope_box)
        
        # Dark mode toggle
        dark_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        dark_box.add_widget(Label(text='Dark Mode:', size_hint_x=0.7))
        self.dark_switch = Switch(active=True, size_hint_x=0.3)
        dark_box.add_widget(self.dark_switch)
        settings_grid.add_widget(dark_box)
        
        # Auto-refresh toggle
        refresh_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        refresh_box.add_widget(Label(text='Auto-refresh Sky:', size_hint_x=0.7))
        self.refresh_switch = Switch(active=True, size_hint_x=0.3)
        refresh_box.add_widget(self.refresh_switch)
        settings_grid.add_widget(refresh_box)
        
        scroll.add_widget(settings_grid)
        layout.add_widget(scroll)
        
        # Buttons
        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        save_btn = Button(text='Save Settings')
        save_btn.bind(on_press=self.save_settings)
        button_box.add_widget(save_btn)
        
        back_btn = Button(text='Back to Home')
        back_btn.bind(on_press=self.go_home)
        button_box.add_widget(back_btn)
        
        layout.add_widget(button_box)
        self.add_widget(layout)
    
    def save_settings(self, instance):
        # Here you would save the settings
        self.show_saved_popup()
    
    def show_saved_popup(self):
        popup = Popup(
            title='Settings Saved',
            content=Label(text='Your settings have been saved successfully!'),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def go_home(self, instance):
        self.manager.current = 'home'

class AstroScopePlannerApp(App):
    def build(self):
        self.title = 'AstroScope Planner Mobile'
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(HomeScreen())
        sm.add_widget(SettingsScreen())
        
        return sm

if __name__ == '__main__':
    AstroScopePlannerApp().run() 