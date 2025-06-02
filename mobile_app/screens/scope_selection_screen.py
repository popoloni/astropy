"""
Smart Telescope Scope Selection Screen
Allows users to select and configure their smart telescope
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
# from kivy.uix.card import Card  # Not available, using BoxLayout instead
# from kivy.uix.separator import Separator  # Widget not available
from kivy.metrics import dp
from kivy.clock import Clock

from mobile_app.utils.smart_scopes import get_scope_manager, ScopeType
from mobile_app.utils.theme_manager import get_theme_manager


class ScopeCard(BoxLayout):
    """Card widget for displaying scope information"""
    
    def __init__(self, scope_id, scope_spec, is_selected=False, **kwargs):
        super().__init__(**kwargs)
        self.scope_id = scope_id
        self.scope_spec = scope_spec
        self.is_selected = is_selected
        
        self.size_hint_y = None
        self.height = dp(200)
        self.elevation = 2 if not is_selected else 6
        
        self._build_ui()
        # self._apply_theme() # disabled
    
    def _build_ui(self):
        """Build the scope card UI"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        
        # Header with name and manufacturer
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        name_label = Label(
            text=self.scope_spec.name,
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        manufacturer_label = Label(
            text=self.scope_spec.manufacturer,
            font_size='14sp',
            halign='right',
            valign='middle',
            size_hint_x=None,
            width=dp(100)
        )
        manufacturer_label.bind(size=manufacturer_label.setter('text_size'))
        
        header_layout.add_widget(name_label)
        header_layout.add_widget(manufacturer_label)
        
        # Specifications grid
        specs_layout = GridLayout(cols=2, spacing=dp(4), size_hint_y=None)
        specs_layout.bind(minimum_height=specs_layout.setter('height'))
        
        specs = [
            ('Aperture', f"{self.scope_spec.aperture_mm}mm"),
            ('Focal Length', f"{self.scope_spec.focal_length_mm}mm"),
            ('F-Ratio', f"f/{self.scope_spec.focal_ratio}"),
            ('Sensor', self.scope_spec.sensor_model),
            ('Resolution', f"{self.scope_spec.resolution_mp}MP"),
            ('Native FOV', f"{self.scope_spec.native_fov_deg[0]:.1f}° × {self.scope_spec.native_fov_deg[1]:.1f}°"),
        ]
        
        if self.scope_spec.mosaic_fov_deg:
            specs.append(('Mosaic FOV', f"{self.scope_spec.mosaic_fov_deg[0]:.1f}° × {self.scope_spec.mosaic_fov_deg[1]:.1f}°"))
        
        if self.scope_spec.price_usd:
            specs.append(('Price', f"${self.scope_spec.price_usd:,}"))
        
        for label_text, value_text in specs:
            label = Label(
                text=label_text + ':',
                font_size='12sp',
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(20)
            )
            label.bind(size=label.setter('text_size'))
            
            value = Label(
                text=value_text,
                font_size='12sp',
                halign='right',
                valign='top',
                size_hint_y=None,
                height=dp(20)
            )
            value.bind(size=value.setter('text_size'))
            
            specs_layout.add_widget(label)
            specs_layout.add_widget(value)
        
        # Selection button
        select_button = Button(
            text='Selected' if self.is_selected else 'Select',
            size_hint_y=None,
            height=dp(40),
            disabled=self.is_selected
        )
        # select_button.bind(on_press=self._on_select) # disabled
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(Label(text="", height=1, size_hint_y=None))
        main_layout.add_widget(specs_layout)
        main_layout.add_widget(select_button)
        
        self.add_widget(main_layout)
        
        # Store references
        self.select_button = select_button
    

class ScopeComparisonPopup(Popup):
    """Popup for comparing multiple scopes"""
    
    def __init__(self, scope_ids, **kwargs):
        super().__init__(**kwargs)
        self.scope_ids = scope_ids
        self.title = 'Scope Comparison'
        self.size_hint = (0.9, 0.8)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build comparison UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Scrollable comparison table
        scroll = ScrollView()
        comparison_layout = GridLayout(
            cols=len(self.scope_ids) + 1,
            spacing=dp(5),
            size_hint_y=None
        )
        comparison_layout.bind(minimum_height=comparison_layout.setter('height'))
        
        scope_manager = get_scope_manager()
        comparison_data = scope_manager.get_scope_comparison(self.scope_ids)
        
        # Headers
        comparison_layout.add_widget(Label(text='Specification', bold=True, size_hint_y=None, height=dp(30)))
        for scope_id in self.scope_ids:
            scope = scope_manager.get_scope(scope_id)
            comparison_layout.add_widget(Label(
                text=scope.name if scope else scope_id,
                bold=True,
                size_hint_y=None,
                height=dp(30)
            ))
        
        # Comparison rows
        if comparison_data:
            first_scope = list(comparison_data.values())[0]
            for key in first_scope.keys():
                if key == 'name':
                    continue
                
                # Specification name
                spec_name = key.replace('_', ' ').title()
                comparison_layout.add_widget(Label(
                    text=spec_name,
                    size_hint_y=None,
                    height=dp(25)
                ))
                
                # Values for each scope
                for scope_id in self.scope_ids:
                    value = comparison_data.get(scope_id, {}).get(key, 'N/A')
                    if isinstance(value, tuple):
                        value = f"{value[0]:.1f} × {value[1]:.1f}"
                    elif isinstance(value, float):
                        value = f"{value:.1f}"
                    
                    comparison_layout.add_widget(Label(
                        text=str(value),
                        size_hint_y=None,
                        height=dp(25)
                    ))
        
        scroll.add_widget(comparison_layout)
        
        # Close button
        close_button = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40)
        )
        close_button.bind(on_press=self.dismiss)
        
        main_layout.add_widget(scroll)
        main_layout.add_widget(close_button)
        
        self.content = main_layout


class ScopeSelectionScreen(Screen):
    """Screen for selecting smart telescope scope"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scope_selection'
        self.scope_manager = get_scope_manager()
        self.scope_cards = {}
        
        self._build_ui()
        self._load_scopes()
    
    def _build_ui(self):
        """Build the main UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        title_label = Label(
            text='Select Your Smart Telescope',
            font_size='24sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        back_button = Button(
            text='Back',
            size_hint_x=None,
            width=dp(80),
            height=dp(40)
        )
        back_button.bind(on_press=self._go_back)
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(back_button)
        
        # Filter buttons
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        all_button = Button(text='All', size_hint_x=None, width=dp(80))
        all_button.bind(on_press=lambda x: self._filter_scopes(None))
        
        vaonis_button = Button(text='Vaonis', size_hint_x=None, width=dp(80))
        vaonis_button.bind(on_press=lambda x: self._filter_scopes(ScopeType.VAONIS))
        
        zwo_button = Button(text='ZWO', size_hint_x=None, width=dp(80))
        zwo_button.bind(on_press=lambda x: self._filter_scopes(ScopeType.ZWO))
        
        dwarf_button = Button(text='DwarfLab', size_hint_x=None, width=dp(100))
        dwarf_button.bind(on_press=lambda x: self._filter_scopes(ScopeType.DWARFLAB))
        
        compare_button = Button(text='Compare Selected', size_hint_x=None, width=dp(150))
        compare_button.bind(on_press=self._show_comparison)
        
        filter_layout.add_widget(all_button)
        filter_layout.add_widget(vaonis_button)
        filter_layout.add_widget(zwo_button)
        filter_layout.add_widget(dwarf_button)
        filter_layout.add_widget(Label())  # Spacer
        filter_layout.add_widget(compare_button)
        
        # Mosaic mode toggle
        mosaic_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        mosaic_label = Label(
            text='Use Mosaic Mode (when available):',
            halign='left',
            valign='middle'
        )
        mosaic_label.bind(size=mosaic_label.setter('text_size'))
        
        self.mosaic_switch = Switch(active=False, size_hint_x=None, width=dp(60))
        self.mosaic_switch.bind(active=self._on_mosaic_toggle)
        
        mosaic_layout.add_widget(mosaic_label)
        mosaic_layout.add_widget(self.mosaic_switch)
        
        # Scrollable scope list
        self.scroll_view = ScrollView()
        self.scope_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.scope_layout.bind(minimum_height=self.scope_layout.setter('height'))
        
        self.scroll_view.add_widget(self.scope_layout)
        
        # Add all widgets to main layout
        main_layout.add_widget(header_layout)
        main_layout.add_widget(filter_layout)
        main_layout.add_widget(mosaic_layout)
        main_layout.add_widget(self.scroll_view)
        
        self.add_widget(main_layout)
        
        # Store references
        self.filter_buttons = {
            'all': all_button,
            'vaonis': vaonis_button,
            'zwo': zwo_button,
            'dwarflab': dwarf_button
        }
        self.compare_button = compare_button
    
    def _load_scopes(self):
        """Load and display all scopes"""
        self.scope_layout.clear_widgets()
        self.scope_cards.clear()
        
        selected_scope_id = getattr(self.scope_manager, "selected_scope", None)
        
        for scope_id, scope_spec in self.scope_manager.get_all_scopes().items():
            is_selected = (scope_id == selected_scope_id)
            
            scope_card = ScopeCard(
                scope_id=scope_id,
                scope_spec=scope_spec,
                is_selected=is_selected
            )
            
            self.scope_cards[scope_id] = scope_card
            self.scope_layout.add_widget(scope_card)
    
    def _filter_scopes(self, scope_type):
        """Filter scopes by type"""
        self.scope_layout.clear_widgets()
        
        if scope_type is None:
            # Show all scopes
            scopes = self.scope_manager.get_all_scopes()
        else:
            # Filter by type
            scopes = self.scope_manager.get_scopes_by_type(scope_type)
        
        for scope_id in scopes:
            if scope_id in self.scope_cards:
                self.scope_layout.add_widget(self.scope_cards[scope_id])
    
    def _on_scope_selected(self, scope_id):
        """Handle scope selection"""
        # Update scope manager
        success = self.scope_manager.set_selected_scope(scope_id)
        
        if success:
            # Update UI
            for card_id, card in self.scope_cards.items():
                card.set_selected(card_id == scope_id)
            
            # Update any active filters
            if hasattr(self.manager, 'get_screen'):
                try:
                    targets_screen = self.manager.get_screen('targets')
                    if hasattr(targets_screen, 'advanced_filter'):
                        targets_screen.advanced_filter.set_scope_filter(
                            scope_id, 
                            self.mosaic_switch.active
                        )
                        # Refresh targets if needed
                        if hasattr(targets_screen, '_apply_filters'):
                            Clock.schedule_once(lambda dt: targets_screen._apply_filters(), 0.1)
                except:
                    pass  # Screen might not exist yet
    
    def _on_mosaic_toggle(self, switch, active):
        """Handle mosaic mode toggle"""
        # Update current filter if scope is selected
        if self.scope_manager.selected_scope:
            if hasattr(self.manager, 'get_screen'):
                try:
                    targets_screen = self.manager.get_screen('targets')
                    if hasattr(targets_screen, 'advanced_filter'):
                        targets_screen.advanced_filter.use_mosaic_mode = active
                        # Refresh targets if needed
                        if hasattr(targets_screen, '_apply_filters'):
                            Clock.schedule_once(lambda dt: targets_screen._apply_filters(), 0.1)
                except:
                    pass
    
    def _show_comparison(self, button):
        """Show scope comparison popup"""
        # For now, compare all scopes - could be enhanced to allow selection
        scope_ids = list(self.scope_manager.get_all_scopes().keys())
        
        if len(scope_ids) > 1:
            popup = ScopeComparisonPopup(scope_ids)
            popup.open()
    
    def _go_back(self, button):
        """Go back to previous screen"""
        if hasattr(self.manager, 'current'):
            self.manager.current = 'targets'
    
    def on_enter(self):
        """Called when screen is entered"""
        # Update mosaic switch state
        if hasattr(self.manager, 'get_screen'):
            try:
                targets_screen = self.manager.get_screen('targets')
                if hasattr(targets_screen, 'advanced_filter'):
                    self.mosaic_switch.active = targets_screen.advanced_filter.use_mosaic_mode
            except:
                pass
        
        # Refresh scope selection
        self._load_scopes()