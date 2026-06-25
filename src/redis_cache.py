"""
SkyJames - Redis Cache for Performance
"""

import redis
import json
import time
from functools import wraps

class SkyJamesCache:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.enabled = self.redis.ping()
        except:
            self.enabled = False
            print("⚠️ Redis not available - caching disabled")
    
    def cache(self, key_prefix, expire_time=300):
        """Decorator to cache function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                # Generate cache key
                cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self.redis.setex(cache_key, expire_time, json.dumps(result))
                return result
            return wrapper
        return decorator
    
    def clear_cache(self, pattern=None):
        """Clear cache entries"""
        if pattern:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        else:
            self.redis.flushdb()
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            'enabled': self.enabled,
            'keys': self.redis.dbsize() if self.enabled else 0
        }

# Global cache instance
cache = SkyJamesCache()
