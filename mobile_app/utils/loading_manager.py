"""
Loading State Management
Centralized loading states, spinners, and progress indicators
"""

from typing import Dict, Optional, Callable, Any
from datetime import datetime
import threading
from enum import Enum

try:
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.spinner import Spinner
    from kivy.clock import Clock
    from kivy.metrics import dp
    from kivy.logger import Logger
    from kivy.animation import Animation
    KIVY_AVAILABLE = True
except ImportError:
    Logger = None
    KIVY_AVAILABLE = False

class LoadingState(Enum):
    """Loading state types"""
    IDLE = "idle"
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"

class LoadingManager:
    """Manages loading states and UI indicators across the app"""
    
    def __init__(self):
        self.active_operations = {}
        self.loading_popups = {}
        self.progress_callbacks = {}
        self._lock = threading.Lock()
        
        # Default configuration
        self.config = {
            'show_progress_after': 0.5,  # Show progress bar after 500ms
            'auto_hide_success': 2.0,    # Hide success message after 2s
            'auto_hide_error': 5.0,      # Hide error message after 5s
            'animation_duration': 0.3    # Animation duration in seconds
        }
    
    def start_loading(self, 
                     operation_id: str, 
                     title: str = "Loading...", 
                     message: str = "", 
                     show_progress: bool = True,
                     cancellable: bool = False,
                     parent_widget: Optional[Any] = None) -> str:
        """Start a loading operation with UI feedback"""
        
        if not KIVY_AVAILABLE:
            if Logger:
                Logger.info(f"Loading: {operation_id} - {title}")
            return operation_id
        
        with self._lock:
            # Create loading operation
            operation = {
                'id': operation_id,
                'title': title,
                'message': message,
                'state': LoadingState.LOADING,
                'progress': 0.0,
                'start_time': datetime.now(),
                'show_progress': show_progress,
                'cancellable': cancellable,
                'parent_widget': parent_widget,
                'popup': None
            }
            
            self.active_operations[operation_id] = operation
            
            # Schedule UI creation to avoid blocking
            Clock.schedule_once(
                lambda dt: self._create_loading_ui(operation_id),
                self.config['show_progress_after']
            )
        
        return operation_id
    
    def update_progress(self, operation_id: str, progress: float, message: str = None):
        """Update progress for an active operation"""
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            operation['progress'] = max(0.0, min(1.0, progress))
            
            if message:
                operation['message'] = message
            
            # Update UI on main thread
            if KIVY_AVAILABLE:
                Clock.schedule_once(
                    lambda dt: self._update_progress_ui(operation_id), 0
                )
    
    def finish_loading(self, 
                      operation_id: str, 
                      success: bool = True, 
                      message: str = None,
                      auto_hide: bool = True):
        """Finish a loading operation"""
        
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            operation['state'] = LoadingState.SUCCESS if success else LoadingState.ERROR
            operation['progress'] = 1.0
            
            if message:
                operation['message'] = message
            
            # Update UI
            if KIVY_AVAILABLE:
                Clock.schedule_once(
                    lambda dt: self._finish_loading_ui(operation_id, success, auto_hide), 0
                )
            
            # Clean up after delay
            if auto_hide:
                hide_delay = self.config['auto_hide_success'] if success else self.config['auto_hide_error']
                Clock.schedule_once(
                    lambda dt: self._cleanup_operation(operation_id), hide_delay
                )
    
    def cancel_loading(self, operation_id: str, message: str = "Cancelled"):
        """Cancel a loading operation"""
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            if not operation.get('cancellable', False):
                return False
            
            operation['state'] = LoadingState.CANCELLED
            operation['message'] = message
            
            # Update UI
            if KIVY_AVAILABLE:
                Clock.schedule_once(
                    lambda dt: self._finish_loading_ui(operation_id, False, True), 0
                )
            
            # Clean up
            Clock.schedule_once(
                lambda dt: self._cleanup_operation(operation_id), 1.0
            )
            
            return True
    
    def is_loading(self, operation_id: str = None) -> bool:
        """Check if operations are currently loading"""
        with self._lock:
            if operation_id:
                operation = self.active_operations.get(operation_id)
                return operation and operation['state'] == LoadingState.LOADING
            else:
                return any(op['state'] == LoadingState.LOADING 
                          for op in self.active_operations.values())
    
    def get_loading_operations(self) -> Dict:
        """Get all active loading operations"""
        with self._lock:
            return {op_id: {
                'title': op['title'],
                'message': op['message'],
                'state': op['state'].value,
                'progress': op['progress'],
                'duration': (datetime.now() - op['start_time']).total_seconds()
            } for op_id, op in self.active_operations.items()}
    
    def _create_loading_ui(self, operation_id: str):
        """Create loading UI popup (runs on main thread)"""
        if not KIVY_AVAILABLE:
            return
        
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            
            if operation.get('popup'):  # Already created
                return
        
        # Create popup layout
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Title
        title_label = Label(
            text=operation['title'],
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        layout.add_widget(title_label)
        
        # Progress bar (if enabled)
        progress_bar = None
        if operation['show_progress']:
            progress_bar = ProgressBar(
                value=operation['progress'] * 100,
                max=100,
                size_hint_y=None,
                height=dp(20)
            )
            layout.add_widget(progress_bar)
        
        # Message label
        message_label = Label(
            text=operation['message'],
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle',
            text_size=(dp(300), None)
        )
        layout.add_widget(message_label)
        
        # Cancel button (if cancellable)
        if operation['cancellable']:
            from kivy.uix.button import Button
            cancel_btn = Button(
                text='Cancel',
                size_hint_y=None,
                height=dp(40),
                on_press=lambda x: self.cancel_loading(operation_id)
            )
            layout.add_widget(cancel_btn)
        
        # Create popup
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.8, None),
            height=dp(200 + (40 if operation['cancellable'] else 0)),
            auto_dismiss=False,
            separator_height=0
        )
        
        # Store references
        operation['popup'] = popup
        operation['progress_bar'] = progress_bar
        operation['message_label'] = message_label
        operation['title_label'] = title_label
        
        # Show with animation
        popup.open()
        self._animate_popup_in(popup)
    
    def _update_progress_ui(self, operation_id: str):
        """Update progress UI (runs on main thread)"""
        if not KIVY_AVAILABLE:
            return
        
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            
            # Update progress bar
            if operation.get('progress_bar'):
                operation['progress_bar'].value = operation['progress'] * 100
            
            # Update message
            if operation.get('message_label'):
                operation['message_label'].text = operation['message']
    
    def _finish_loading_ui(self, operation_id: str, success: bool, auto_hide: bool):
        """Finish loading UI (runs on main thread)"""
        if not KIVY_AVAILABLE:
            return
        
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            popup = operation.get('popup')
            
            if not popup:
                return
            
            # Update title with result
            if operation.get('title_label'):
                if success:
                    operation['title_label'].text = "✓ " + operation['title']
                    operation['title_label'].color = (0, 1, 0, 1)  # Green
                else:
                    operation['title_label'].text = "✗ " + operation['title']
                    operation['title_label'].color = (1, 0, 0, 1)  # Red
            
            # Update progress bar to full
            if operation.get('progress_bar'):
                operation['progress_bar'].value = 100
            
            # Update message
            if operation.get('message_label'):
                operation['message_label'].text = operation['message']
            
            # Hide after delay if auto_hide is enabled
            if auto_hide:
                hide_delay = self.config['auto_hide_success'] if success else self.config['auto_hide_error']
                Clock.schedule_once(
                    lambda dt: self._hide_popup(operation_id), hide_delay
                )
    
    def _hide_popup(self, operation_id: str):
        """Hide popup with animation"""
        if not KIVY_AVAILABLE:
            return
        
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation = self.active_operations[operation_id]
            popup = operation.get('popup')
            
            if popup:
                self._animate_popup_out(popup, 
                    lambda: self._cleanup_operation(operation_id))
    
    def _animate_popup_in(self, popup):
        """Animate popup entrance"""
        if not KIVY_AVAILABLE:
            return
        
        # Temporarily disable animations to prevent NoneType errors
        # Just show the popup without animation
        if popup:
            popup.opacity = 1
            popup.size_hint = (0.8, None)
    
    def _animate_popup_out(self, popup, callback: Callable = None):
        """Animate popup exit"""
        if not KIVY_AVAILABLE:
            return
        
        # Temporarily disable animations to prevent NoneType errors
        # Just dismiss the popup directly
        if popup:
            try:
                popup.dismiss()
            except:
                pass
        
        if callback:
            callback()
    
    def _cleanup_operation(self, operation_id: str):
        """Clean up operation resources"""
        with self._lock:
            if operation_id in self.active_operations:
                operation = self.active_operations[operation_id]
                
                # Dismiss popup if still open
                popup = operation.get('popup')
                if popup:
                    try:
                        popup.dismiss()
                    except:
                        pass
                
                # Remove from active operations
                del self.active_operations[operation_id]
                
                if Logger:
                    Logger.info(f"Loading: Cleaned up operation {operation_id}")

class LoadingContext:
    """Context manager for loading operations"""
    
    def __init__(self, 
                 manager: LoadingManager,
                 operation_id: str,
                 title: str = "Loading...",
                 message: str = "",
                 show_progress: bool = True,
                 cancellable: bool = False):
        self.manager = manager
        self.operation_id = operation_id
        self.title = title
        self.message = message
        self.show_progress = show_progress
        self.cancellable = cancellable
    
    def __enter__(self):
        self.manager.start_loading(
            self.operation_id,
            self.title,
            self.message,
            self.show_progress,
            self.cancellable
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_msg = str(exc_val) if exc_val else None
        
        self.manager.finish_loading(
            self.operation_id,
            success=success,
            message=error_msg if not success else "Complete"
        )
    
    def update_progress(self, progress: float, message: str = None):
        """Update progress within context"""
        self.manager.update_progress(self.operation_id, progress, message)

# Global loading manager instance
loading_manager = LoadingManager()

# Convenience functions
def start_loading(operation_id: str, title: str = "Loading...", **kwargs) -> str:
    """Start a loading operation"""
    return loading_manager.start_loading(operation_id, title, **kwargs)

def update_progress(operation_id: str, progress: float, message: str = None):
    """Update loading progress"""
    loading_manager.update_progress(operation_id, progress, message)

def finish_loading(operation_id: str, success: bool = True, message: str = None):
    """Finish loading operation"""
    loading_manager.finish_loading(operation_id, success, message)

def loading_context(operation_id: str, title: str = "Loading...", **kwargs) -> LoadingContext:
    """Create a loading context manager"""
    return LoadingContext(loading_manager, operation_id, title, **kwargs) 