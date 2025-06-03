"""
Application Logging System
Comprehensive logging for mobile astronomy app with error tracking and debugging support
"""

import os
import sys
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class AppLogger:
    """Comprehensive application logger with error tracking"""
    
    def __init__(self, app_name: str = "AstroScope", log_dir: str = "logs"):
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Error tracking
        self.error_count = 0
        self.recent_errors = []
        self.error_categories = {}
        self.performance_metrics = {}
        
        # Setup loggers
        self._setup_loggers()
        
        # Log session start
        self.info("=" * 50)
        self.info(f"{app_name} Application Started")
        self.info(f"Session ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.info("=" * 50)
    
    def _setup_loggers(self):
        """Setup multiple loggers for different purposes"""
        
        # Main application logger
        self.logger = logging.getLogger(f"{self.app_name}_main")
        self.logger.setLevel(logging.DEBUG)
        
        # Error logger
        self.error_logger = logging.getLogger(f"{self.app_name}_errors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Performance logger  
        self.perf_logger = logging.getLogger(f"{self.app_name}_performance")
        self.perf_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for logger in [self.logger, self.error_logger, self.perf_logger]:
            logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handlers
        today = datetime.now().strftime('%Y%m%d')
        
        # Main log file
        main_handler = logging.FileHandler(self.log_dir / f"{self.app_name}_{today}.log")
        main_handler.setFormatter(detailed_formatter)
        main_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(main_handler)
        
        # Error log file
        error_handler = logging.FileHandler(self.log_dir / f"{self.app_name}_errors_{today}.log")
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        self.error_logger.addHandler(error_handler)
        
        # Performance log file
        perf_handler = logging.FileHandler(self.log_dir / f"{self.app_name}_performance_{today}.log")
        perf_handler.setFormatter(simple_formatter)
        perf_handler.setLevel(logging.INFO)
        self.perf_logger.addHandler(perf_handler)
        
        # Console handler (for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, context: Dict[str, Any] = None):
        """Log debug message"""
        full_message = self._format_message(message, context)
        self.logger.debug(full_message)
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """Log info message"""
        full_message = self._format_message(message, context)
        self.logger.info(full_message)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """Log warning message"""
        full_message = self._format_message(message, context)
        self.logger.warning(full_message)
        
    def error(self, message: str, exception: Exception = None, context: Dict[str, Any] = None):
        """Log error with detailed tracking"""
        full_message = self._format_message(message, context)
        
        # Add exception details if provided
        if exception:
            full_message += f"\nException: {type(exception).__name__}: {str(exception)}"
            full_message += f"\nTraceback: {traceback.format_exc()}"
        
        # Log to both main and error loggers
        self.logger.error(full_message)
        self.error_logger.error(full_message)
        
        # Track error statistics
        self._track_error(message, exception, context)
    
    def critical(self, message: str, exception: Exception = None, context: Dict[str, Any] = None):
        """Log critical error"""
        full_message = self._format_message(message, context)
        
        if exception:
            full_message += f"\nCRITICAL Exception: {type(exception).__name__}: {str(exception)}"
            full_message += f"\nTraceback: {traceback.format_exc()}"
        
        self.logger.critical(full_message)
        self.error_logger.critical(full_message)
        
        # Track critical error
        self._track_error(message, exception, context, critical=True)
    
    def performance(self, operation: str, duration: float, context: Dict[str, Any] = None):
        """Log performance metrics"""
        message = f"PERF | {operation} | {duration:.3f}s"
        if context:
            message += f" | {context}"
        
        self.perf_logger.info(message)
        
        # Track performance metrics
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        self.performance_metrics[operation].append(duration)
    
    def user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions for UX analysis"""
        message = f"USER_ACTION | {action}"
        if details:
            message += f" | {details}"
        self.logger.info(message)
    
    def screen_navigation(self, from_screen: str, to_screen: str, method: str = "button"):
        """Log screen navigation"""
        context = {
            'from': from_screen,
            'to': to_screen,
            'method': method,
            'timestamp': datetime.now().isoformat()
        }
        self.user_action("NAVIGATION", context)
    
    def data_operation(self, operation: str, success: bool, duration: float = None, count: int = None):
        """Log data operations (loading, saving, etc.)"""
        context = {
            'operation': operation,
            'success': success,
            'duration': duration,
            'count': count
        }
        
        if success:
            self.info(f"DATA_OP | {operation} | SUCCESS", context)
        else:
            self.error(f"DATA_OP | {operation} | FAILED", context=context)
    
    def _format_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Format message with optional context"""
        if context:
            return f"{message} | Context: {context}"
        return message
    
    def _track_error(self, message: str, exception: Exception = None, context: Dict[str, Any] = None, critical: bool = False):
        """Track error statistics"""
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception': str(exception) if exception else None,
            'exception_type': type(exception).__name__ if exception else None,
            'context': context,
            'critical': critical,
            'traceback': traceback.format_exc() if exception else None
        }
        
        # Add to recent errors (keep last 50)
        self.recent_errors.append(error_info)
        if len(self.recent_errors) > 50:
            self.recent_errors.pop(0)
        
        # Categorize error
        category = error_info['exception_type'] or 'Unknown'
        if category not in self.error_categories:
            self.error_categories[category] = 0
        self.error_categories[category] += 1
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for debugging"""
        recent_24h = [
            err for err in self.recent_errors 
            if datetime.fromisoformat(err['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            'total_errors': self.error_count,
            'errors_24h': len(recent_24h),
            'recent_errors': self.recent_errors[-10:],  # Last 10 errors
            'error_categories': self.error_categories,
            'critical_errors': [err for err in self.recent_errors if err.get('critical', False)]
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        for operation, durations in self.performance_metrics.items():
            summary[operation] = {
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'min_duration': min(durations)
            }
        return summary
    
    def export_logs(self, output_file: str = None) -> str:
        """Export logs to JSON for analysis"""
        if not output_file:
            output_file = f"{self.app_name}_debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'app_name': self.app_name,
            'export_timestamp': datetime.now().isoformat(),
            'error_summary': self.get_error_summary(),
            'performance_summary': self.get_performance_summary(),
            'session_info': {
                'total_errors': self.error_count,
                'log_files': [str(f) for f in self.log_dir.glob(f"{self.app_name}_*.log")]
            }
        }
        
        output_path = self.log_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.info(f"Debug logs exported to {output_path}")
        return str(output_path)
    
    def close(self):
        """Close logger and generate session summary"""
        self.info("=" * 50)
        self.info("Application Session Ending")
        self.info(f"Total Errors: {self.error_count}")
        
        if self.error_count > 0:
            self.info("Error Summary:")
            for category, count in self.error_categories.items():
                self.info(f"  {category}: {count}")
        
        if self.performance_metrics:
            self.info("Performance Summary:")
            for operation, durations in self.performance_metrics.items():
                avg_duration = sum(durations) / len(durations)
                self.info(f"  {operation}: {avg_duration:.3f}s avg ({len(durations)} calls)")
        
        self.info("=" * 50)
        
        # Export debug summary if there were errors
        if self.error_count > 0:
            self.export_logs()

# Global logger instance
app_logger = AppLogger()

# Convenience functions
def log_debug(message: str, context: Dict[str, Any] = None):
    app_logger.debug(message, context)

def log_info(message: str, context: Dict[str, Any] = None):
    app_logger.info(message, context)

def log_warning(message: str, context: Dict[str, Any] = None):
    app_logger.warning(message, context)

def log_error(message: str, exception: Exception = None, context: Dict[str, Any] = None):
    app_logger.error(message, exception, context)

def log_critical(message: str, exception: Exception = None, context: Dict[str, Any] = None):
    app_logger.critical(message, exception, context)

def log_performance(operation: str, duration: float, context: Dict[str, Any] = None):
    app_logger.performance(operation, duration, context)

def log_user_action(action: str, details: Dict[str, Any] = None):
    app_logger.user_action(action, details)

def log_navigation(from_screen: str, to_screen: str, method: str = "button"):
    app_logger.screen_navigation(from_screen, to_screen, method)

def log_data_operation(operation: str, success: bool, duration: float = None, count: int = None):
    app_logger.data_operation(operation, success, duration, count) 