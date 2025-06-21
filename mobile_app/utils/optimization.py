"""
Performance Optimization Utilities
Lazy imports, object pooling, and basic optimization strategies
"""

import importlib
import sys
import weakref
from typing import Dict, Any, Optional, Callable, Type, List
from functools import wraps
import threading
import time
from collections import defaultdict, deque

try:
    from kivy.logger import Logger
    KIVY_AVAILABLE = True
except ImportError:
    import logging
    Logger = logging.getLogger(__name__)
    KIVY_AVAILABLE = False

class LazyImporter:
    """Lazy import system to reduce startup time"""
    
    def __init__(self):
        self._modules = {}
        self._import_cache = {}
        self._import_times = {}
        self._failed_imports = set()
        self._lock = threading.Lock()
    
    def lazy_import(self, module_name: str, attribute: str = None, 
                   fallback: Any = None, required: bool = False):
        """Lazily import a module or attribute"""
        
        cache_key = f"{module_name}.{attribute}" if attribute else module_name
        
        # Check cache first
        with self._lock:
            if cache_key in self._import_cache:
                return self._import_cache[cache_key]
            
            if cache_key in self._failed_imports and not required:
                return fallback
        
        try:
            start_time = time.perf_counter()
            
            # Import the module
            if module_name not in sys.modules:
                module = importlib.import_module(module_name)
            else:
                module = sys.modules[module_name]
            
            # Get the attribute if specified
            if attribute:
                result = getattr(module, attribute)
            else:
                result = module
            
            import_time = time.perf_counter() - start_time
            
            with self._lock:
                self._import_cache[cache_key] = result
                self._import_times[cache_key] = import_time
            
            if Logger:
                Logger.debug(f"LazyImport: {cache_key} loaded in {import_time:.3f}s")
            
            return result
            
        except (ImportError, AttributeError) as e:
            with self._lock:
                self._failed_imports.add(cache_key)
            
            if required:
                raise
            
            if Logger:
                Logger.warning(f"LazyImport: Failed to import {cache_key}: {e}")
            
            return fallback
    
    def preload_modules(self, module_list: List[str]):
        """Preload a list of modules in background"""
        def preload():
            for module_name in module_list:
                try:
                    self.lazy_import(module_name)
                except Exception as e:
                    if Logger:
                        Logger.error(f"LazyImport: Preload failed for {module_name}: {e}")
        
        thread = threading.Thread(target=preload, daemon=True)
        thread.start()
    
    def get_import_stats(self) -> Dict:
        """Get import performance statistics"""
        with self._lock:
            total_time = sum(self._import_times.values())
            return {
                'cached_modules': len(self._import_cache),
                'failed_imports': len(self._failed_imports),
                'total_import_time': total_time,
                'slowest_imports': sorted(
                    [(k, v) for k, v in self._import_times.items()],
                    key=lambda x: x[1], reverse=True
                )[:10]
            }

class ObjectPool:
    """Generic object pool for expensive-to-create objects"""
    
    def __init__(self, factory: Callable, max_size: int = 50, cleanup_interval: int = 300):
        self.factory = factory
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self._pool = deque()
        self._active_objects = weakref.WeakSet()
        self._lock = threading.Lock()
        self._stats = {
            'created': 0,
            'reused': 0,
            'cleaned': 0,
            'peak_size': 0
        }
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def get(self) -> Any:
        """Get an object from the pool"""
        with self._lock:
            if self._pool:
                obj = self._pool.popleft()
                self._active_objects.add(obj)
                self._stats['reused'] += 1
                return obj
            else:
                # Create new object
                obj = self.factory()
                self._active_objects.add(obj)
                self._stats['created'] += 1
                return obj
    
    def release(self, obj: Any):
        """Return an object to the pool"""
        with self._lock:
            if len(self._pool) < self.max_size:
                # Reset object state if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset()
                
                self._pool.append(obj)
                self._stats['peak_size'] = max(self._stats['peak_size'], len(self._pool))
            
            # Remove from active set
            self._active_objects.discard(obj)
    
    def clear(self):
        """Clear the pool"""
        with self._lock:
            self._pool.clear()
            self._active_objects.clear()
            self._stats['cleaned'] += 1
    
    def get_stats(self) -> Dict:
        """Get pool statistics"""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'active_objects': len(self._active_objects),
                'max_size': self.max_size,
                **self._stats
            }
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup():
            while True:
                time.sleep(self.cleanup_interval)
                with self._lock:
                    # Clear half the pool periodically to prevent memory leaks
                    if len(self._pool) > self.max_size // 2:
                        half_size = len(self._pool) // 2
                        for _ in range(half_size):
                            self._pool.popleft()
                        self._stats['cleaned'] += half_size
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

class CachedProperty:
    """Descriptor for cached properties that are expensive to compute"""
    
    def __init__(self, func: Callable, ttl: Optional[float] = None):
        self.func = func
        self.ttl = ttl  # Time to live in seconds
        self.name = func.__name__
        self.cache_attr = f'_cached_{self.name}'
        self.time_attr = f'_cached_time_{self.name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        # Check if cached value exists and is still valid
        if hasattr(obj, self.cache_attr):
            if self.ttl is None:  # No expiration
                return getattr(obj, self.cache_attr)
            
            # Check TTL
            cache_time = getattr(obj, self.time_attr, 0)
            if time.time() - cache_time < self.ttl:
                return getattr(obj, self.cache_attr)
        
        # Compute and cache the value
        value = self.func(obj)
        setattr(obj, self.cache_attr, value)
        setattr(obj, self.time_attr, time.time())
        
        return value
    
    def __delete__(self, obj):
        # Clear the cache
        if hasattr(obj, self.cache_attr):
            delattr(obj, self.cache_attr)
        if hasattr(obj, self.time_attr):
            delattr(obj, self.time_attr)

class MemoryOptimizer:
    """Memory optimization utilities"""
    
    def __init__(self):
        self._weak_refs = {}
        self._cache_sizes = defaultdict(int)
        self._cleanup_thresholds = {
            'small': 100,    # Objects < 1KB
            'medium': 50,    # Objects 1-10KB  
            'large': 10      # Objects > 10KB
        }
    
    def get_object_size(self, obj: Any) -> int:
        """Get approximate object size in bytes"""
        try:
            import sys
            return sys.getsizeof(obj)
        except:
            return 0
    
    def categorize_by_size(self, obj: Any) -> str:
        """Categorize object by size"""
        size = self.get_object_size(obj)
        if size < 1024:  # 1KB
            return 'small'
        elif size < 10240:  # 10KB
            return 'medium'
        else:
            return 'large'
    
    def smart_cache(self, key: str, value: Any, category: str = None) -> bool:
        """Smart caching based on object size and memory pressure"""
        if category is None:
            category = self.categorize_by_size(value)
        
        threshold = self._cleanup_thresholds.get(category, 50)
        
        if self._cache_sizes[category] >= threshold:
            # Memory pressure - don't cache
            return False
        
        # Cache with weak reference for automatic cleanup
        self._weak_refs[key] = weakref.ref(value)
        self._cache_sizes[category] += 1
        return True
    
    def force_garbage_collection(self):
        """Force garbage collection and cleanup weak references"""
        import gc
        
        # Clean up dead weak references
        dead_keys = []
        for key, ref in self._weak_refs.items():
            if ref() is None:
                dead_keys.append(key)
        
        for key in dead_keys:
            del self._weak_refs[key]
        
        # Reset cache sizes
        self._cache_sizes.clear()
        
        # Force garbage collection
        gc.collect()
        
        if Logger:
            Logger.info(f"MemoryOptimizer: Cleaned up {len(dead_keys)} dead references")

# Global instances
lazy_importer = LazyImporter()
memory_optimizer = MemoryOptimizer()

# Object pools for common expensive objects
calculation_pool = ObjectPool(lambda: {}, max_size=30)  # For calculation results
coordinate_pool = ObjectPool(lambda: {'ra': 0, 'dec': 0}, max_size=100)  # For coordinates

# Convenience functions and decorators
def lazy_import(module_name: str, attribute: str = None, **kwargs):
    """Convenience function for lazy importing"""
    return lazy_importer.lazy_import(module_name, attribute, **kwargs)

def cached_property(ttl: Optional[float] = None):
    """Decorator for cached properties"""
    def decorator(func):
        return CachedProperty(func, ttl)
    return decorator

def with_object_pool(pool: ObjectPool):
    """Decorator to use object pool for function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get object from pool
            obj = pool.get()
            try:
                # Call function with pooled object
                result = func(obj, *args, **kwargs)
                return result
            finally:
                # Return object to pool
                pool.release(obj)
        return wrapper
    return decorator

def memoize_with_ttl(ttl: float = 3600):
    """Memoization decorator with TTL"""
    def decorator(func):
        cache = {}
        cache_times = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check cache
            if key in cache:
                cache_time = cache_times.get(key, 0)
                if time.time() - cache_time < ttl:
                    return cache[key]
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = time.time()
            
            # Cleanup old entries periodically
            if len(cache) > 1000:  # Arbitrary limit
                current_time = time.time()
                expired_keys = [
                    k for k, t in cache_times.items()
                    if current_time - t > ttl
                ]
                for k in expired_keys:
                    cache.pop(k, None)
                    cache_times.pop(k, None)
            
            return result
        
        return wrapper
    return decorator

# Preloading configuration for common modules
PRELOAD_MODULES = [
    'datetime',
    'json',
    'math',
    'os',
    'sys'
]

def initialize_optimization():
    """Initialize optimization systems"""
    if Logger:
        Logger.info("Optimization: Initializing lazy import and object pools")
    
    # Preload common modules
    lazy_importer.preload_modules(PRELOAD_MODULES)
    
    # Force initial cleanup
    memory_optimizer.force_garbage_collection()

def get_optimization_stats() -> Dict:
    """Get comprehensive optimization statistics"""
    return {
        'lazy_imports': lazy_importer.get_import_stats(),
        'calculation_pool': calculation_pool.get_stats(),
        'coordinate_pool': coordinate_pool.get_stats(),
        'memory': {
            'weak_refs': len(memory_optimizer._weak_refs),
            'cache_sizes': dict(memory_optimizer._cache_sizes)
        }
    } 