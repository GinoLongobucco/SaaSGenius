import hashlib
import time
import threading
from typing import Dict, Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """In-memory cache manager for analysis results"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        
        # Configure logging
        self.logger = logging.getLogger('cache')
        
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a unique key for given arguments"""
        # Create unique string based on arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            current_time = time.time()
            
            # Check TTL
            if current_time > entry['expires_at']:
                del self.cache[key]
                del self.access_times[key]
                return None
            
            # Update access time
            self.access_times[key] = current_time
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in cache"""
        with self.lock:
            current_time = time.time()
            ttl = ttl or self.default_ttl
            
            # Check if we need to make space
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = {
                'value': value,
                'created_at': current_time,
                'expires_at': current_time + ttl
            }
            self.access_times[key] = current_time
    
    def _evict_lru(self) -> None:
        """Remove least recently used item"""
        if not self.access_times:
            return
        
        # Find key with oldest access time
        lru_key = min(self.access_times, key=self.access_times.get)
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            current_time = time.time()
            valid_entries = 0
            expired_entries = 0
            
            for entry in self.cache.values():
                if current_time <= entry['expires_at']:
                    valid_entries += 1
                else:
                    expired_entries += 1
            
            return {
                'total_entries': len(self.cache),
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'usage_percent': (len(self.cache) / self.max_size) * 100
            }
    
    def cleanup_expired(self) -> int:
        """Clean expired entries and return number of removed entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if current_time > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                del self.access_times[key]
            
            return len(expired_keys)

# Global cache manager instance
cache_manager = CacheManager()

def cached_analysis(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache analysis results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_prefix + cache_manager._generate_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator