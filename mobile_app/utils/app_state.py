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
        
        # Advanced filtering
        self.advanced_filter = None
        self.filter_presets = {}
        self.active_filter_preset = None
        
        # Session planning
        self.session_planner = None
        self.current_session = None
        self.session_manager = None
        self.saved_sessions = []
        
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
    
    def get_target_name(self, target):
        """Safely get target name from either CelestialObject or dict"""
        try:
            if hasattr(target, 'name'):
                return target.name
            elif isinstance(target, dict):
                return target.get('name', '')
            else:
                return str(target) if target else ''
        except Exception:
            return ''
    
    def is_target_planned(self, target) -> bool:
        """Check if target is in planned observations"""
        # Compare by name since target objects might be different instances
        target_name = self.get_target_name(target)
        for planned in self.planned_objects:
            planned_name = self.get_target_name(planned)
            if target_name == planned_name:
                return True
        return False
    
    def is_target_completed(self, target) -> bool:
        """Check if target is completed"""
        target_name = self.get_target_name(target)
        for completed in self.completed_objects:
            completed_name = self.get_target_name(completed)
            if target_name == completed_name:
                return True
        return False
    
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
                    'name': self.get_target_name(obj),
                    'type': getattr(obj, 'object_type', 'Unknown') if hasattr(obj, 'object_type') else obj.get('object_type', 'Unknown') if isinstance(obj, dict) else 'Unknown',
                    'ra': getattr(obj, 'ra', 0) if hasattr(obj, 'ra') else obj.get('ra', 0) if isinstance(obj, dict) else 0,
                    'dec': getattr(obj, 'dec', 0) if hasattr(obj, 'dec') else obj.get('dec', 0) if isinstance(obj, dict) else 0
                }
                for obj in self.planned_objects
            ],
            'completed_objects': [
                {
                    'name': self.get_target_name(obj),
                    'type': getattr(obj, 'object_type', 'Unknown') if hasattr(obj, 'object_type') else obj.get('object_type', 'Unknown') if isinstance(obj, dict) else 'Unknown'
                }
                for obj in self.completed_objects
            ],
            'stats': self.get_session_stats()
        }
    
    def apply_advanced_filter(self, targets: List[Dict]) -> List[Dict]:
        """Apply advanced filtering to targets"""
        if self.advanced_filter and self.advanced_filter.enabled:
            return self.advanced_filter.apply_filters(targets)
        return targets
    
    def set_advanced_filter(self, filter_obj) -> None:
        """Set the advanced filter object"""
        self.advanced_filter = filter_obj
    
    def get_advanced_filter(self):
        """Get the current advanced filter object"""
        return self.advanced_filter
    
    def save_filter_preset(self, name: str) -> None:
        """Save current filter as a preset"""
        if self.advanced_filter:
            self.filter_presets[name] = self.advanced_filter.save_preset(name)
    
    def load_filter_preset(self, name: str) -> bool:
        """Load a filter preset"""
        if name in self.filter_presets:
            if self.advanced_filter:
                self.advanced_filter.load_preset(self.filter_presets[name])
                self.active_filter_preset = name
                return True
        return False
    
    def get_filter_presets(self) -> List[str]:
        """Get list of available filter presets"""
        return list(self.filter_presets.keys())
    
    def get_filtered_targets(self) -> List[Dict]:
        """Get targets with advanced filtering applied"""
        return self.apply_advanced_filter(self.tonights_targets)
    
    # Session Planning Methods
    def initialize_session_planner(self):
        """Initialize session planning system"""
        try:
            from utils.session_planner import SessionPlanner, SessionManager
            self.session_manager = SessionManager()
            self.session_planner = SessionPlanner(self.session_manager)
            self.refresh_saved_sessions()
            return True
        except ImportError as e:
            print(f"Session planner not available: {e}")
            return False
    
    def get_session_planner(self):
        """Get session planner instance"""
        if not self.session_planner:
            self.initialize_session_planner()
        return self.session_planner
    
    def get_session_manager(self):
        """Get session manager instance"""
        if not self.session_manager:
            self.initialize_session_planner()
        return self.session_manager
    
    def create_new_session(self, date, duration, priorities, targets, location, 
                          session_type=None, optimization_strategy=None):
        """Create a new observation session"""
        planner = self.get_session_planner()
        if not planner:
            return None
        
        try:
            from utils.session_planner import SessionType, OptimizationStrategy
            
            # Set defaults if not provided
            if session_type is None:
                session_type = SessionType.MIXED
            if optimization_strategy is None:
                optimization_strategy = OptimizationStrategy.BALANCED
            
            session = planner.create_session(
                date=date,
                duration=duration,
                priorities=priorities,
                targets=targets,
                location=location,
                session_type=session_type,
                optimization_strategy=optimization_strategy
            )
            
            self.current_session = session
            return session
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    def save_current_session(self):
        """Save the current session"""
        if not self.current_session or not self.session_manager:
            return False
        
        success = self.session_manager.save_session(self.current_session)
        if success:
            self.refresh_saved_sessions()
        return success
    
    def load_session(self, session_id):
        """Load a saved session"""
        manager = self.get_session_manager()
        if not manager:
            return None
        
        session = manager.load_session(session_id)
        if session:
            self.current_session = session
        return session
    
    def delete_session(self, session_id):
        """Delete a saved session"""
        manager = self.get_session_manager()
        if not manager:
            return False
        
        success = manager.delete_session(session_id)
        if success:
            self.refresh_saved_sessions()
        return success
    
    def refresh_saved_sessions(self):
        """Refresh the list of saved sessions"""
        manager = self.get_session_manager()
        if manager:
            self.saved_sessions = manager.list_sessions()
        else:
            self.saved_sessions = []
    
    def export_session(self, session, format='pdf', output_path=None):
        """Export session plan"""
        planner = self.get_session_planner()
        if not planner:
            return None
        
        try:
            return planner.export_session(session, format, output_path)
        except Exception as e:
            print(f"Error exporting session: {e}")
            return None
    
    def get_session_statistics(self):
        """Get statistics about saved sessions"""
        if not self.saved_sessions:
            return {}
        
        total_sessions = len(self.saved_sessions)
        total_targets = sum(s.get('target_count', 0) for s in self.saved_sessions)
        session_types = {}
        
        for session in self.saved_sessions:
            session_type = session.get('session_type', 'unknown')
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'total_targets_planned': total_targets,
            'average_targets_per_session': total_targets / total_sessions if total_sessions > 0 else 0,
            'session_types': session_types
        }