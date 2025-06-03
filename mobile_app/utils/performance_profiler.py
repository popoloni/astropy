"""
Performance Profiling Utilities
Monitor and analyze app performance bottlenecks
"""

import time
import functools
from collections import defaultdict, deque
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import weakref

try:
    from kivy.logger import Logger
    KIVY_AVAILABLE = True
except ImportError:
    import logging
    Logger = logging.getLogger(__name__)
    KIVY_AVAILABLE = False

class PerformanceProfiler:
    """Performance monitoring and profiling utility"""
    
    def __init__(self, max_samples=1000):
        self.max_samples = max_samples
        self.timing_data = defaultdict(lambda: deque(maxlen=max_samples))
        self.call_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.memory_snapshots = deque(maxlen=100)
        self.active_operations = {}
        self._lock = threading.Lock()
        
        # Performance thresholds (seconds)
        self.thresholds = {
            'critical': 5.0,    # > 5 seconds is critical
            'warning': 1.0,     # > 1 second is warning
            'info': 0.1         # > 0.1 second is notable
        }
        
        # Start memory monitoring
        self._start_memory_monitoring()
    
    def profile_function(self, name: Optional[str] = None, threshold: float = 0.0):
        """Decorator to profile function execution time"""
        def decorator(func: Callable):
            function_name = name or f"{func.__module__}.{func.__qualname__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                operation_id = f"{function_name}_{id(threading.current_thread())}"
                
                with self._lock:
                    self.active_operations[operation_id] = {
                        'name': function_name,
                        'start_time': start_time,
                        'thread': threading.current_thread().name
                    }
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    with self._lock:
                        # Record timing data
                        self.timing_data[function_name].append({
                            'duration': duration,
                            'timestamp': datetime.now(),
                            'success': success,
                            'error': error,
                            'thread': threading.current_thread().name
                        })
                        
                        self.call_counts[function_name] += 1
                        if not success:
                            self.error_counts[function_name] += 1
                        
                        # Remove from active operations
                        self.active_operations.pop(operation_id, None)
                    
                    # Log slow operations
                    if duration > threshold:
                        level = self._get_log_level(duration)
                        Logger.log(level, f"Performance: {function_name} took {duration:.3f}s")
                
                return result
            
            return wrapper
        return decorator
    
    def start_operation(self, name: str) -> str:
        """Start timing an operation manually"""
        operation_id = f"{name}_{time.time()}_{id(threading.current_thread())}"
        
        with self._lock:
            self.active_operations[operation_id] = {
                'name': name,
                'start_time': time.perf_counter(),
                'thread': threading.current_thread().name
            }
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error: Optional[str] = None):
        """End timing an operation manually"""
        end_time = time.perf_counter()
        
        with self._lock:
            if operation_id not in self.active_operations:
                Logger.warning(f"Performance: Unknown operation ID: {operation_id}")
                return
            
            operation = self.active_operations.pop(operation_id)
            duration = end_time - operation['start_time']
            name = operation['name']
            
            # Record timing data
            self.timing_data[name].append({
                'duration': duration,
                'timestamp': datetime.now(),
                'success': success,
                'error': error,
                'thread': operation['thread']
            })
            
            self.call_counts[name] += 1
            if not success:
                self.error_counts[name] += 1
        
        # Log slow operations
        if duration > 0.1:  # Log operations > 100ms
            level = self._get_log_level(duration)
            Logger.log(level, f"Performance: {name} took {duration:.3f}s")
    
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        with self._lock:
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': self._get_summary_stats(),
                'top_slowest': self._get_slowest_operations(10),
                'most_called': self._get_most_called_operations(10),
                'error_rates': self._get_error_rates(),
                'active_operations': len(self.active_operations),
                'memory_usage': self._get_memory_stats()
            }
        
        return report
    
    def get_bottlenecks(self, threshold: float = 0.5) -> List[Dict]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        with self._lock:
            for name, measurements in self.timing_data.items():
                if not measurements:
                    continue
                
                durations = [m['duration'] for m in measurements]
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                
                if avg_duration > threshold:
                    bottlenecks.append({
                        'name': name,
                        'avg_duration': avg_duration,
                        'max_duration': max_duration,
                        'call_count': self.call_counts[name],
                        'error_rate': self.error_counts[name] / self.call_counts[name] if self.call_counts[name] > 0 else 0,
                        'total_time': sum(durations),
                        'severity': self._classify_severity(avg_duration)
                    })
        
        # Sort by total time impact
        bottlenecks.sort(key=lambda x: x['total_time'], reverse=True)
        return bottlenecks
    
    def _get_log_level(self, duration: float) -> int:
        """Get appropriate log level based on duration"""
        if duration > self.thresholds['critical']:
            return 40  # ERROR
        elif duration > self.thresholds['warning']:
            return 30  # WARNING  
        elif duration > self.thresholds['info']:
            return 20  # INFO
        else:
            return 10  # DEBUG
    
    def _classify_severity(self, duration: float) -> str:
        """Classify performance issue severity"""
        if duration > self.thresholds['critical']:
            return 'critical'
        elif duration > self.thresholds['warning']:
            return 'warning'
        elif duration > self.thresholds['info']:
            return 'info'
        else:
            return 'normal'
    
    def _get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        total_calls = sum(self.call_counts.values())
        total_errors = sum(self.error_counts.values())
        
        all_durations = []
        for measurements in self.timing_data.values():
            all_durations.extend([m['duration'] for m in measurements])
        
        if all_durations:
            avg_duration = sum(all_durations) / len(all_durations)
            max_duration = max(all_durations)
        else:
            avg_duration = max_duration = 0
        
        return {
            'total_operations': len(self.timing_data),
            'total_calls': total_calls,
            'total_errors': total_errors,
            'error_rate': total_errors / total_calls if total_calls > 0 else 0,
            'avg_duration': avg_duration,
            'max_duration': max_duration
        }
    
    def _get_slowest_operations(self, limit: int) -> List[Dict]:
        """Get slowest operations"""
        operations = []
        
        for name, measurements in self.timing_data.items():
            if not measurements:
                continue
            
            durations = [m['duration'] for m in measurements]
            operations.append({
                'name': name,
                'avg_duration': sum(durations) / len(durations),
                'max_duration': max(durations),
                'call_count': len(measurements)
            })
        
        operations.sort(key=lambda x: x['avg_duration'], reverse=True)
        return operations[:limit]
    
    def _get_most_called_operations(self, limit: int) -> List[Dict]:
        """Get most frequently called operations"""
        operations = []
        
        for name, count in self.call_counts.items():
            if name in self.timing_data and self.timing_data[name]:
                durations = [m['duration'] for m in self.timing_data[name]]
                avg_duration = sum(durations) / len(durations)
            else:
                avg_duration = 0
            
            operations.append({
                'name': name,
                'call_count': count,
                'avg_duration': avg_duration
            })
        
        operations.sort(key=lambda x: x['call_count'], reverse=True)
        return operations[:limit]
    
    def _get_error_rates(self) -> List[Dict]:
        """Get operations with highest error rates"""
        error_rates = []
        
        for name in self.call_counts:
            if self.call_counts[name] > 0:
                error_rate = self.error_counts[name] / self.call_counts[name]
                if error_rate > 0:
                    error_rates.append({
                        'name': name,
                        'error_rate': error_rate,
                        'error_count': self.error_counts[name],
                        'total_calls': self.call_counts[name]
                    })
        
        error_rates.sort(key=lambda x: x['error_rate'], reverse=True)
        return error_rates
    
    def _start_memory_monitoring(self):
        """Start background memory monitoring"""
        def monitor_memory():
            try:
                import psutil
                process = psutil.Process()
                
                while True:
                    memory_info = process.memory_info()
                    self.memory_snapshots.append({
                        'timestamp': datetime.now(),
                        'rss': memory_info.rss,  # Resident set size
                        'vms': memory_info.vms   # Virtual memory size
                    })
                    time.sleep(30)  # Sample every 30 seconds
                    
            except ImportError:
                Logger.info("Performance: psutil not available, skipping memory monitoring")
            except Exception as e:
                Logger.error(f"Performance: Memory monitoring error: {e}")
        
        thread = threading.Thread(target=monitor_memory, daemon=True)
        thread.start()
    
    def _get_memory_stats(self) -> Dict:
        """Get memory usage statistics"""
        if not self.memory_snapshots:
            return {'available': False}
        
        recent_snapshots = list(self.memory_snapshots)[-10:]  # Last 10 snapshots
        
        rss_values = [s['rss'] for s in recent_snapshots]
        vms_values = [s['vms'] for s in recent_snapshots]
        
        return {
            'available': True,
            'current_rss_mb': rss_values[-1] / (1024 * 1024) if rss_values else 0,
            'current_vms_mb': vms_values[-1] / (1024 * 1024) if vms_values else 0,
            'avg_rss_mb': sum(rss_values) / len(rss_values) / (1024 * 1024) if rss_values else 0,
            'max_rss_mb': max(rss_values) / (1024 * 1024) if rss_values else 0,
            'samples': len(recent_snapshots)
        }
    
    def reset_stats(self):
        """Reset all performance statistics"""
        with self._lock:
            self.timing_data.clear()
            self.call_counts.clear()
            self.error_counts.clear()
            self.active_operations.clear()
            Logger.info("Performance: Statistics reset")

# Global profiler instance
profiler = PerformanceProfiler()

# Convenience decorators
def profile(name: Optional[str] = None, threshold: float = 0.0):
    """Decorator for profiling functions"""
    return profiler.profile_function(name, threshold)

def profile_slow(name: Optional[str] = None):
    """Decorator for profiling potentially slow functions (threshold: 0.5s)"""
    return profiler.profile_function(name, 0.5)

def profile_critical(name: Optional[str] = None):
    """Decorator for profiling critical functions (threshold: 0.1s)"""
    return profiler.profile_function(name, 0.1) 