"""
Error Boundary System
Graceful error handling and recovery mechanisms
"""

import traceback
import functools
import sys
from typing import Dict, List, Optional, Callable, Any, Type
from datetime import datetime
from enum import Enum
import threading

try:
    from kivy.logger import Logger
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.clock import Clock
    from kivy.metrics import dp
    KIVY_AVAILABLE = True
except ImportError:
    Logger = None
    KIVY_AVAILABLE = False

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, app continues normally
    MEDIUM = "medium"     # Moderate issues, some functionality affected
    HIGH = "high"         # Serious issues, major functionality broken
    CRITICAL = "critical" # Critical issues, app may be unstable

class ErrorCategory(Enum):
    """Error categories for better handling"""
    NETWORK = "network"
    CALCULATION = "calculation"
    UI = "ui"
    IMPORT = "import"
    DATA = "data"
    PERMISSION = "permission"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class ErrorHandler:
    """Centralized error handling and recovery system"""
    
    def __init__(self):
        self.error_log = []
        self.error_callbacks = {}
        self.recovery_strategies = {}
        self.error_counts = {}
        self._lock = threading.Lock()
        
        # Configuration
        self.config = {
            'max_error_log': 1000,
            'show_user_errors': True,
            'auto_retry_attempts': 3,
            'retry_delay': 1.0,
            'log_all_errors': True
        }
        
        # Default recovery strategies
        self._setup_default_strategies()
    
    def handle_error(self, 
                    error: Exception, 
                    context: str = "",
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    user_message: str = None,
                    show_to_user: bool = None,
                    recovery_data: Dict = None) -> bool:
        """Handle an error with appropriate response"""
        
        # Log the error
        error_info = self._log_error(error, context, severity, category, recovery_data)
        
        # Determine if we should show to user
        if show_to_user is None:
            show_to_user = (
                self.config['show_user_errors'] and 
                severity in [ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
            )
        
        # Show error to user if appropriate
        if show_to_user and KIVY_AVAILABLE:
            user_msg = user_message or self._generate_user_message(error, category, severity)
            Clock.schedule_once(
                lambda dt: self._show_error_popup(error_info, user_msg), 0
            )
        
        # Try recovery
        recovery_success = self._attempt_recovery(error, context, category, recovery_data)
        
        # Update error counts
        with self._lock:
            error_type = type(error).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Trigger callbacks
        self._trigger_callbacks(error_info)
        
        return recovery_success
    
    def error_boundary(self, 
                      context: str = "",
                      severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                      category: ErrorCategory = ErrorCategory.UNKNOWN,
                      user_message: str = None,
                      show_to_user: bool = None,
                      return_on_error: Any = None,
                      retry_attempts: int = 0):
        """Decorator for error boundary protection"""
        
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                max_attempts = retry_attempts + 1
                
                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        
                        # Handle the error
                        recovery_success = self.handle_error(
                            e, 
                            context or func.__name__,
                            severity,
                            category,
                            user_message,
                            show_to_user,
                            {'function': func.__name__, 'attempt': attempts}
                        )
                        
                        # If this is the last attempt or recovery failed, handle appropriately
                        if attempts >= max_attempts or not recovery_success:
                            if severity == ErrorSeverity.CRITICAL:
                                raise  # Re-raise critical errors
                            else:
                                if Logger:
                                    Logger.error(f"Error boundary: {func.__name__} failed after {attempts} attempts: {e}")
                                return return_on_error
                        
                        # Wait before retry
                        if attempts < max_attempts:
                            import time
                            time.sleep(self.config['retry_delay'] * attempts)
                
                return return_on_error
            
            return wrapper
        return decorator
    
    def safe_call(self, func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """Safely call a function and return (success, result)"""
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            self.handle_error(
                e, 
                context=f"safe_call:{func.__name__}",
                severity=ErrorSeverity.LOW,
                show_to_user=False
            )
            return False, None
    
    def register_recovery_strategy(self, 
                                 category: ErrorCategory, 
                                 strategy: Callable[[Exception, str, Dict], bool]):
        """Register a recovery strategy for an error category"""
        self.recovery_strategies[category] = strategy
    
    def register_error_callback(self, callback: Callable[[Dict], None]):
        """Register a callback to be triggered on errors"""
        callback_id = id(callback)
        self.error_callbacks[callback_id] = callback
        return callback_id
    
    def unregister_error_callback(self, callback_id: int):
        """Unregister an error callback"""
        self.error_callbacks.pop(callback_id, None)
    
    def get_error_statistics(self) -> Dict:
        """Get error statistics and trends"""
        with self._lock:
            recent_errors = [e for e in self.error_log if 
                           (datetime.now() - e['timestamp']).total_seconds() < 3600]  # Last hour
            
            return {
                'total_errors': len(self.error_log),
                'recent_errors': len(recent_errors),
                'error_counts': dict(self.error_counts),
                'top_errors': self._get_top_errors(),
                'error_rate_per_hour': len(recent_errors),
                'categories': self._get_error_categories_stats()
            }
    
    def clear_error_log(self):
        """Clear the error log"""
        with self._lock:
            self.error_log.clear()
            self.error_counts.clear()
            if Logger:
                Logger.info("ErrorHandler: Error log cleared")
    
    def _log_error(self, 
                   error: Exception, 
                   context: str, 
                   severity: ErrorSeverity, 
                   category: ErrorCategory,
                   recovery_data: Dict) -> Dict:
        """Log error details"""
        
        error_info = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'severity': severity.value,
            'category': category.value,
            'traceback': traceback.format_exc() if self.config['log_all_errors'] else None,
            'recovery_data': recovery_data or {},
            'thread': threading.current_thread().name
        }
        
        with self._lock:
            self.error_log.append(error_info)
            
            # Trim log if too large
            if len(self.error_log) > self.config['max_error_log']:
                self.error_log = self.error_log[-self.config['max_error_log']:]
        
        # Log to system logger
        if Logger:
            log_level = self._get_log_level(severity)
            Logger.log(log_level, f"Error [{severity.value}] in {context}: {error}")
            
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                Logger.log(log_level, f"Traceback: {traceback.format_exc()}")
        
        return error_info
    
    def _generate_user_message(self, 
                             error: Exception, 
                             category: ErrorCategory, 
                             severity: ErrorSeverity) -> str:
        """Generate user-friendly error message"""
        
        # Category-specific messages
        category_messages = {
            ErrorCategory.NETWORK: "Network connection issue. Please check your internet connection and try again.",
            ErrorCategory.CALCULATION: "Calculation error occurred. Some astronomical data may be temporarily unavailable.",
            ErrorCategory.UI: "Interface error. Please try refreshing or restarting the app.",
            ErrorCategory.IMPORT: "Module loading error. Some features may be temporarily unavailable.",
            ErrorCategory.DATA: "Data error. Please try refreshing the data or check your inputs.",
            ErrorCategory.PERMISSION: "Permission error. Please check app permissions in settings.",
            ErrorCategory.SYSTEM: "System error occurred. Please try restarting the app."
        }
        
        base_message = category_messages.get(category, "An unexpected error occurred.")
        
        # Add severity-specific guidance
        if severity == ErrorSeverity.CRITICAL:
            base_message += "\n\nThis is a critical error. Please restart the app."
        elif severity == ErrorSeverity.HIGH:
            base_message += "\n\nSome features may not work properly until resolved."
        
        return base_message
    
    def _show_error_popup(self, error_info: Dict, user_message: str):
        """Show error popup to user"""
        if not KIVY_AVAILABLE:
            return
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Title
        title = Label(
            text=f"Error: {error_info['error_type']}",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign='center',
            color=(1, 0.6, 0.6, 1)  # Light red
        )
        title.bind(size=title.setter('text_size'))
        layout.add_widget(title)
        
        # Message
        message = Label(
            text=user_message,
            size_hint_y=None,
            height=dp(100),
            halign='center',
            valign='middle',
            text_size=(dp(350), None)
        )
        layout.add_widget(message)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        # OK button
        ok_btn = Button(text='OK', size_hint_x=0.5)
        
        # Details button (for debugging)
        details_btn = Button(text='Details', size_hint_x=0.5)
        
        button_layout.add_widget(ok_btn)
        button_layout.add_widget(details_btn)
        layout.add_widget(button_layout)
        
        # Create popup
        popup = Popup(
            title='',
            content=layout,
            size_hint=(0.9, None),
            height=dp(250),
            auto_dismiss=True,
            separator_height=0
        )
        
        # Button actions
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        details_btn.bind(on_press=lambda x: self._show_error_details(error_info, popup))
        
        popup.open()
    
    def _show_error_details(self, error_info: Dict, parent_popup: Popup):
        """Show detailed error information"""
        if not KIVY_AVAILABLE:
            return
        
        parent_popup.dismiss()
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Details text
        details_text = f"""Error Type: {error_info['error_type']}
Message: {error_info['error_message']}
Context: {error_info['context']}
Severity: {error_info['severity']}
Category: {error_info['category']}
Time: {error_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
Thread: {error_info['thread']}

{error_info['traceback'] or 'No traceback available'}"""
        
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.textinput import TextInput
        
        text_input = TextInput(
            text=details_text,
            readonly=True,
            font_size='12sp'
        )
        
        scroll = ScrollView()
        scroll.add_widget(text_input)
        layout.add_widget(scroll)
        
        # Close button
        close_btn = Button(text='Close', size_hint_y=None, height=dp(40))
        layout.add_widget(close_btn)
        
        details_popup = Popup(
            title='Error Details',
            content=layout,
            size_hint=(0.95, 0.8)
        )
        
        close_btn.bind(on_press=lambda x: details_popup.dismiss())
        details_popup.open()
    
    def _attempt_recovery(self, 
                         error: Exception, 
                         context: str, 
                         category: ErrorCategory, 
                         recovery_data: Dict) -> bool:
        """Attempt to recover from error using registered strategies"""
        
        strategy = self.recovery_strategies.get(category)
        if strategy:
            try:
                return strategy(error, context, recovery_data or {})
            except Exception as recovery_error:
                if Logger:
                    Logger.error(f"Recovery strategy failed: {recovery_error}")
        
        return False
    
    def _trigger_callbacks(self, error_info: Dict):
        """Trigger registered error callbacks"""
        for callback in self.error_callbacks.values():
            try:
                callback(error_info)
            except Exception as callback_error:
                if Logger:
                    Logger.error(f"Error callback failed: {callback_error}")
    
    def _setup_default_strategies(self):
        """Set up default recovery strategies"""
        
        def network_recovery(error: Exception, context: str, data: Dict) -> bool:
            """Recovery strategy for network errors"""
            # For network errors, we could implement retry logic,
            # offline mode activation, cached data fallback, etc.
            if Logger:
                Logger.info("Attempting network error recovery")
            return False  # Placeholder
        
        def calculation_recovery(error: Exception, context: str, data: Dict) -> bool:
            """Recovery strategy for calculation errors"""
            # For calculation errors, we could use fallback algorithms,
            # cached results, default values, etc.
            if Logger:
                Logger.info("Attempting calculation error recovery")
            return False  # Placeholder
        
        def ui_recovery(error: Exception, context: str, data: Dict) -> bool:
            """Recovery strategy for UI errors"""
            # For UI errors, we could refresh widgets, reset state, etc.
            if Logger:
                Logger.info("Attempting UI error recovery")
            return False  # Placeholder
        
        self.register_recovery_strategy(ErrorCategory.NETWORK, network_recovery)
        self.register_recovery_strategy(ErrorCategory.CALCULATION, calculation_recovery)
        self.register_recovery_strategy(ErrorCategory.UI, ui_recovery)
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Convert severity to log level"""
        level_map = {
            ErrorSeverity.LOW: 20,      # INFO
            ErrorSeverity.MEDIUM: 30,   # WARNING
            ErrorSeverity.HIGH: 40,     # ERROR
            ErrorSeverity.CRITICAL: 50  # CRITICAL
        }
        return level_map.get(severity, 30)
    
    def _get_top_errors(self, limit: int = 10) -> List[Dict]:
        """Get most common errors"""
        return [
            {'error_type': error_type, 'count': count}
            for error_type, count in sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
        ]
    
    def _get_error_categories_stats(self) -> Dict:
        """Get error statistics by category"""
        category_counts = {}
        for error in self.error_log:
            category = error['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts

# Global error handler instance
error_handler = ErrorHandler()

# Convenience decorators and functions
def error_boundary(context: str = "", 
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  category: ErrorCategory = ErrorCategory.UNKNOWN,
                  **kwargs):
    """Decorator for error boundary protection"""
    return error_handler.error_boundary(context, severity, category, **kwargs)

def handle_error(error: Exception, **kwargs):
    """Handle an error"""
    return error_handler.handle_error(error, **kwargs)

def safe_call(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """Safely call a function"""
    return error_handler.safe_call(func, *args, **kwargs)

# Specific error boundary decorators
def ui_error_boundary(context: str = "", **kwargs):
    """Error boundary for UI operations"""
    return error_boundary(context, ErrorSeverity.MEDIUM, ErrorCategory.UI, **kwargs)

def calculation_error_boundary(context: str = "", **kwargs):
    """Error boundary for calculation operations"""
    return error_boundary(context, ErrorSeverity.MEDIUM, ErrorCategory.CALCULATION, **kwargs)

def network_error_boundary(context: str = "", **kwargs):
    """Error boundary for network operations"""
    return error_boundary(context, ErrorSeverity.MEDIUM, ErrorCategory.NETWORK, **kwargs)

def critical_error_boundary(context: str = "", **kwargs):
    """Error boundary for critical operations"""
    return error_boundary(context, ErrorSeverity.CRITICAL, ErrorCategory.SYSTEM, **kwargs) 