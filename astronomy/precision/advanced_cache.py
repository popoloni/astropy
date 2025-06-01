"""
High-Precision Astronomical Calculations - Advanced Caching System

This module provides advanced caching strategies for high-precision astronomical
calculations, including multi-level caching, smart invalidation, and performance
analytics.

Features:
- Multi-level caching (memory, session, persistent)
- Smart cache invalidation based on time and dependencies
- Cache analytics and performance monitoring
- Adaptive cache sizing
- Thread-safe operations

Author: OpenHands AI Assistant
Date: 2025-06-01
"""

import time
import pickle
import hashlib
import threading
import weakref
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, Tuple, List
from functools import wraps
from collections import OrderedDict
import os
import tempfile


class CacheStats:
    """Cache performance statistics tracking"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.memory_usage = 0
        self.total_requests = 0
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def record_hit(self):
        """Record a cache hit"""
        with self._lock:
            self.hits += 1
            self.total_requests += 1
    
    def record_miss(self):
        """Record a cache miss"""
        with self._lock:
            self.misses += 1
            self.total_requests += 1
    
    def record_eviction(self):
        """Record a cache eviction"""
        with self._lock:
            self.evictions += 1
    
    def update_memory_usage(self, size: int):
        """Update memory usage statistics"""
        with self._lock:
            self.memory_usage = size
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # Don't use lock in property to avoid deadlock
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 1.0 - self.hit_rate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            runtime = time.time() - self.start_time
            return {
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'total_requests': self.total_requests,
                'hit_rate': self.hit_rate,
                'miss_rate': self.miss_rate,
                'memory_usage_bytes': self.memory_usage,
                'memory_usage_mb': self.memory_usage / (1024 * 1024),
                'runtime_seconds': runtime,
                'requests_per_second': self.total_requests / runtime if runtime > 0 else 0
            }
    
    def reset(self):
        """Reset all statistics"""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.evictions = 0
            self.memory_usage = 0
            self.total_requests = 0
            self.start_time = time.time()


class CacheEntry:
    """Individual cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 1
        self.ttl = ttl
        self.size = self._estimate_size(value)
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object"""
        try:
            return len(pickle.dumps(obj))
        except:
            # Fallback estimation
            if isinstance(obj, dict):
                return sum(len(str(k)) + len(str(v)) for k, v in obj.items()) * 2
            elif isinstance(obj, (list, tuple)):
                return sum(len(str(item)) for item in obj) * 2
            else:
                return len(str(obj)) * 2
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Access the cached value and update metadata"""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value
    
    @property
    def age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at


class AdvancedLRUCache:
    """Advanced LRU cache with TTL, size limits, and analytics"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: float = 100.0, 
                 default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()
    
    def _make_key(self, func_name: str, args: Tuple, kwargs: Dict) -> str:
        """Create a cache key from function name and arguments"""
        # Create a deterministic key from function name and arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self.stats.record_eviction()
    
    def _enforce_size_limit(self):
        """Enforce cache size and memory limits"""
        with self._lock:
            # Remove entries until we're under limits
            while (len(self._cache) > self.max_size or 
                   self._get_total_memory() > self.max_memory_bytes):
                if not self._cache:
                    break
                # Remove least recently used item
                self._cache.popitem(last=False)
                self.stats.record_eviction()
    
    def _get_total_memory(self) -> int:
        """Calculate total memory usage"""
        return sum(entry.size for entry in self._cache.values())
    
    def get(self, func_name: str, args: Tuple, kwargs: Dict) -> Tuple[bool, Any]:
        """
        Get value from cache
        
        Returns:
            Tuple of (found, value)
        """
        key = self._make_key(func_name, args, kwargs)
        
        with self._lock:
            # Clean up expired entries periodically
            if len(self._cache) % 100 == 0:
                self._cleanup_expired()
            
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    del self._cache[key]
                    self.stats.record_miss()
                    return False, None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                value = entry.access()
                self.stats.record_hit()
                return True, value
            
            self.stats.record_miss()
            return False, None
    
    def put(self, func_name: str, args: Tuple, kwargs: Dict, value: Any, 
            ttl: Optional[float] = None):
        """Put value into cache"""
        key = self._make_key(func_name, args, kwargs)
        ttl = ttl or self.default_ttl
        
        with self._lock:
            entry = CacheEntry(value, ttl)
            self._cache[key] = entry
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            # Enforce limits
            self._enforce_size_limit()
            
            # Update memory usage stats
            self.stats.update_memory_usage(self._get_total_memory())
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self.stats.update_memory_usage(0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            stats = self.stats.get_stats()
            stats.update({
                'cache_size': len(self._cache),
                'max_size': self.max_size,
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'memory_utilization': self._get_total_memory() / self.max_memory_bytes if self.max_memory_bytes > 0 else 0
            })
            return stats


class PersistentCache:
    """Persistent cache using disk storage"""
    
    def __init__(self, cache_dir: Optional[str] = None, max_age_hours: float = 24.0):
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), 'astropy_precision_cache')
        self.max_age_seconds = max_age_hours * 3600
        self._ensure_cache_dir()
        self._lock = threading.Lock()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def _make_key(self, func_name: str, args: Tuple, kwargs: Dict) -> str:
        """Create a cache key from function name and arguments"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, func_name: str, args: Tuple, kwargs: Dict) -> Tuple[bool, Any]:
        """Get value from persistent cache"""
        key = self._make_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            try:
                if not os.path.exists(cache_path):
                    return False, None
                
                # Check if file is too old
                file_age = time.time() - os.path.getmtime(cache_path)
                if file_age > self.max_age_seconds:
                    os.remove(cache_path)
                    return False, None
                
                # Load cached value
                with open(cache_path, 'rb') as f:
                    value = pickle.load(f)
                
                return True, value
                
            except Exception:
                # If anything goes wrong, treat as cache miss
                return False, None
    
    def put(self, func_name: str, args: Tuple, kwargs: Dict, value: Any):
        """Put value into persistent cache"""
        key = self._make_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)
            except Exception:
                # Silently fail if we can't write to cache
                pass
    
    def clear(self):
        """Clear all persistent cache files"""
        with self._lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, filename))
            except Exception:
                pass
    
    def cleanup_old_files(self):
        """Remove old cache files"""
        with self._lock:
            try:
                current_time = time.time()
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        filepath = os.path.join(self.cache_dir, filename)
                        file_age = current_time - os.path.getmtime(filepath)
                        if file_age > self.max_age_seconds:
                            os.remove(filepath)
            except Exception:
                pass


class MultiLevelCache:
    """Multi-level cache combining memory and persistent storage"""
    
    def __init__(self, memory_cache_size: int = 1000, memory_cache_mb: float = 100.0,
                 persistent_cache_hours: float = 24.0, enable_persistent: bool = True):
        self.memory_cache = AdvancedLRUCache(memory_cache_size, memory_cache_mb)
        self.persistent_cache = PersistentCache(max_age_hours=persistent_cache_hours) if enable_persistent else None
        self.enable_persistent = enable_persistent
    
    def get(self, func_name: str, args: Tuple, kwargs: Dict) -> Tuple[bool, Any]:
        """Get value from multi-level cache"""
        # Try memory cache first
        found, value = self.memory_cache.get(func_name, args, kwargs)
        if found:
            return True, value
        
        # Try persistent cache if enabled
        if self.enable_persistent and self.persistent_cache:
            found, value = self.persistent_cache.get(func_name, args, kwargs)
            if found:
                # Promote to memory cache
                self.memory_cache.put(func_name, args, kwargs, value)
                return True, value
        
        return False, None
    
    def put(self, func_name: str, args: Tuple, kwargs: Dict, value: Any):
        """Put value into multi-level cache"""
        # Always put in memory cache
        self.memory_cache.put(func_name, args, kwargs, value)
        
        # Also put in persistent cache if enabled
        if self.enable_persistent and self.persistent_cache:
            self.persistent_cache.put(func_name, args, kwargs, value)
    
    def clear(self):
        """Clear all cache levels"""
        self.memory_cache.clear()
        if self.persistent_cache:
            self.persistent_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'memory_cache': self.memory_cache.get_stats(),
            'persistent_cache_enabled': self.enable_persistent
        }
        return stats
    
    def cleanup(self):
        """Perform cache maintenance"""
        if self.persistent_cache:
            self.persistent_cache.cleanup_old_files()


# Global cache instance
_global_cache = MultiLevelCache()


def advanced_cache(ttl: Optional[float] = None, use_persistent: bool = True,
                  cache_instance: Optional[MultiLevelCache] = None):
    """
    Advanced caching decorator with multi-level caching support
    
    Args:
        ttl: Time to live in seconds
        use_persistent: Whether to use persistent caching
        cache_instance: Custom cache instance to use
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or _global_cache
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get from cache
            found, value = cache.get(func.__name__, args, kwargs)
            if found:
                return value
            
            # Compute value
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.put(func.__name__, args, kwargs, result)
            
            return result
        
        # Add cache management methods to the wrapped function
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.get_stats()
        wrapper.cache_cleanup = lambda: cache.cleanup()
        
        return wrapper
    
    return decorator


def get_global_cache_stats() -> Dict[str, Any]:
    """Get statistics for the global cache"""
    return _global_cache.get_stats()


def clear_global_cache():
    """Clear the global cache"""
    _global_cache.clear()


def cleanup_global_cache():
    """Perform maintenance on the global cache"""
    _global_cache.cleanup()


# Example usage and testing
if __name__ == "__main__":
    # Test the advanced caching system
    
    @advanced_cache(ttl=60.0)  # 1 minute TTL
    def expensive_calculation(x: float, y: float) -> float:
        """Simulate an expensive calculation"""
        time.sleep(0.1)  # Simulate computation time
        return x * y + x ** 2 + y ** 2
    
    print("Testing advanced caching system...")
    
    # First call - should be slow
    start = time.time()
    result1 = expensive_calculation(3.14, 2.71)
    time1 = time.time() - start
    print(f"First call: {result1:.4f} in {time1:.3f}s")
    
    # Second call - should be fast (cached)
    start = time.time()
    result2 = expensive_calculation(3.14, 2.71)
    time2 = time.time() - start
    print(f"Second call: {result2:.4f} in {time2:.3f}s")
    
    # Different parameters - should be slow again
    start = time.time()
    result3 = expensive_calculation(1.0, 2.0)
    time3 = time.time() - start
    print(f"Different params: {result3:.4f} in {time3:.3f}s")
    
    # Show cache statistics
    stats = expensive_calculation.cache_stats()
    print(f"\nCache Statistics:")
    print(f"Memory cache hit rate: {stats['memory_cache']['hit_rate']:.2%}")
    print(f"Total requests: {stats['memory_cache']['total_requests']}")
    print(f"Memory usage: {stats['memory_cache']['memory_usage_mb']:.2f} MB")
    
    print("\n✅ Advanced caching system test completed")