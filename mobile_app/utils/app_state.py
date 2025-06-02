"""
Application State Management
Centralized state management for AstroScope Planner
"""

from datetime import datetime
from typing import List, Dict, Optional, Any

# Try to import Kivy components, fall back to basic implementations if not available
try:
    from kivy.event import EventDispatcher
    from kivy.properties import ListProperty, DictProperty, StringProperty, BooleanProperty, NumericProperty
    KIVY_AVAILABLE = True
except ImportError:
    # Fallback implementations for testing without Kivy
    class EventDispatcher:
        def __init__(self, **kwargs):
            super().__init__()
    
    class Property:
        def __init__(self, default_value=None):
            self.default_value = default_value
    
    ListProperty = DictProperty = StringProperty = BooleanProperty = NumericProperty = Property
    KIVY_AVAILABLE = False

class AppState(EventDispatcher):
    """Central application state manager"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize properties based on Kivy availability
        if KIVY_AVAILABLE:
            # Observable properties
            self.tonights_targets = ListProperty([])
            self.all_visible_objects = ListProperty([])
            self.current_location = DictProperty({})
            self.selected_target = DictProperty({})
            self.mosaic_groups = ListProperty([])
            
            # User preferences
            self.scheduling_strategy = StringProperty('max_objects')
            self.show_mosaic_only = BooleanProperty(False)
            self.min_visibility_hours = NumericProperty(2.0)
            
            # UI state
            self.is_loading = BooleanProperty(False)
            self.current_screen = StringProperty('home')
        else:
            # Simple attributes for testing
            self.tonights_targets = []
            self.all_visible_objects = []
            self.current_location = {}
            self.selected_target = {}
            self.mosaic_groups = []
            
            # User preferences
            self.scheduling_strategy = 'max_objects'
            self.show_mosaic_only = False
            self.min_visibility_hours = 2.0
            
            # UI state
            self.is_loading = False
            self.current_screen = 'home'
        
        # Initialize default values
        self.scheduling_strategies = [
            'longest_duration',
            'max_objects', 
            'optimal_snr',
            'minimal_mosaic',
            'difficulty_balanced',
            'mosaic_groups'
        ]
        
        self.object_types = [
            'All Types',
            'Galaxy',
            'Nebula', 
            'Star Cluster',
            'Planetary Nebula',
            'Supernova Remnant'
        ]
        
        # Current session data
        self.session_start_time = datetime.now()
        self.planned_objects = []
        self.completed_objects = []
        
    def get_strategy_display_name(self, strategy: str) -> str:
        """Get user-friendly display name for scheduling strategy"""
        strategy_names = {
            'longest_duration': 'Longest Duration',
            'max_objects': 'Maximum Objects',
            'optimal_snr': 'Optimal SNR',
            'minimal_mosaic': 'Minimal Mosaic',
            'difficulty_balanced': 'Balanced Difficulty',
            'mosaic_groups': 'Mosaic Groups'
        }
        return strategy_names.get(strategy, strategy.replace('_', ' ').title())
    
    def get_object_type_filter(self, object_type: str) -> Optional[str]:
        """Get filter value for object type"""
        if object_type == 'All Types':
            return None
        return object_type.lower()
    
    def filter_targets_by_type(self, object_type: str) -> List[Dict]:
        """Filter current targets by object type"""
        if object_type == 'All Types':
            return self.tonights_targets
        
        filtered = []
        for target in self.tonights_targets:
            if hasattr(target, 'object_type'):
                if target.object_type.lower() == object_type.lower():
                    filtered.append(target)
            elif isinstance(target, dict) and 'object_type' in target:
                if target['object_type'].lower() == object_type.lower():
                    filtered.append(target)
        
        return filtered
    
    def get_target_by_name(self, name: str) -> Optional[Dict]:
        """Get target object by name"""
        for target in self.tonights_targets:
            target_name = target.name if hasattr(target, 'name') else target.get('name', '')
            if target_name == name:
                return target
        return None
    
    def add_to_planned(self, target: Dict):
        """Add target to planned observations"""
        if target not in self.planned_objects:
            self.planned_objects.append(target)
    
    def remove_from_planned(self, target: Dict):
        """Remove target from planned observations"""
        if target in self.planned_objects:
            self.planned_objects.remove(target)
    
    def mark_completed(self, target: Dict):
        """Mark target as completed"""
        if target in self.planned_objects:
            self.planned_objects.remove(target)
        if target not in self.completed_objects:
            self.completed_objects.append(target)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            'session_duration': datetime.now() - self.session_start_time,
            'total_targets': len(self.tonights_targets),
            'planned_count': len(self.planned_objects),
            'completed_count': len(self.completed_objects),
            'remaining_count': len(self.planned_objects)
        }
    
    def reset_session(self):
        """Reset current observing session"""
        self.planned_objects.clear()
        self.completed_objects.clear()
        self.session_start_time = datetime.now()
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export current session data for sharing"""
        return {
            'date': datetime.now().isoformat(),
            'location': dict(self.current_location),
            'strategy': self.scheduling_strategy,
            'planned_objects': [
                {
                    'name': getattr(obj, 'name', obj.get('name', 'Unknown')),
                    'type': getattr(obj, 'object_type', obj.get('object_type', 'Unknown')),
                    'ra': getattr(obj, 'ra', obj.get('ra', 0)),
                    'dec': getattr(obj, 'dec', obj.get('dec', 0))
                }
                for obj in self.planned_objects
            ],
            'completed_objects': [
                {
                    'name': getattr(obj, 'name', obj.get('name', 'Unknown')),
                    'type': getattr(obj, 'object_type', obj.get('object_type', 'Unknown'))
                }
                for obj in self.completed_objects
            ],
            'stats': self.get_session_stats()
        }