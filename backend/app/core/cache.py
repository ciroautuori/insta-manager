import redis
import json
import pickle
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
from functools import wraps

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager for API responses and data."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
        self.default_ttl = 300  # 5 minutes
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage."""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)):
                return json.dumps(data, default=str).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Cache serialization error: {e}")
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        try:
            # Try JSON first (more efficient)
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Cache deserialization error: {e}")
                return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.redis_client.get(key)
            if data is None:
                return None
            
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized_data = self._serialize(value)
            
            return self.redis_client.setex(key, ttl, serialized_data)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1, ttl: int = None) -> int:
        """Increment counter in cache."""
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key, amount)
            if ttl:
                pipe.expire(key, ttl)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0


# Global cache instance
cache = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(ttl: int = 300, key_prefix: str = "api"):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key_str}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key_str}")
            result = await func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key_str, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_analytics_data(account_id: int, days: int = 30) -> str:
    """Generate cache key for analytics data."""
    return f"analytics:account:{account_id}:days:{days}"


def cache_instagram_insights(account_id: int, period: str = "day") -> str:
    """Generate cache key for Instagram insights."""
    return f"instagram:insights:account:{account_id}:period:{period}"


def cache_dashboard_stats(admin_id: int) -> str:
    """Generate cache key for dashboard statistics."""
    return f"dashboard:stats:admin:{admin_id}"


def cache_account_posts(account_id: int, page: int = 1) -> str:
    """Generate cache key for account posts."""
    return f"posts:account:{account_id}:page:{page}"


def invalidate_account_cache(account_id: int) -> None:
    """Invalidate all cache entries for an account."""
    patterns = [
        f"analytics:account:{account_id}:*",
        f"instagram:insights:account:{account_id}:*",
        f"posts:account:{account_id}:*"
    ]
    
    for pattern in patterns:
        cleared = cache.clear_pattern(pattern)
        if cleared > 0:
            logger.info(f"Cleared {cleared} cache entries for pattern: {pattern}")


def invalidate_admin_cache(admin_id: int) -> None:
    """Invalidate all cache entries for an admin."""
    patterns = [
        f"dashboard:stats:admin:{admin_id}:*",
        f"api:*:admin:{admin_id}:*"
    ]
    
    for pattern in patterns:
        cleared = cache.clear_pattern(pattern)
        if cleared > 0:
            logger.info(f"Cleared {cleared} cache entries for pattern: {pattern}")


class RateLimitCache:
    """Rate limiting using Redis cache."""
    
    @staticmethod
    def check_rate_limit(key: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (e.g., user ID, IP address)
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        try:
            current_count = cache.increment(key, 1, window)
            
            if current_count <= limit:
                return True, limit - current_count
            else:
                return False, 0
                
        except Exception as e:
            logger.error(f"Rate limit check error for key {key}: {e}")
            # Fail open - allow request if cache is down
            return True, limit
    
    @staticmethod
    def get_reset_time(key: str) -> Optional[datetime]:
        """Get when rate limit resets for a key."""
        try:
            ttl = cache.redis_client.ttl(key)
            if ttl > 0:
                return datetime.utcnow() + timedelta(seconds=ttl)
            return None
        except Exception as e:
            logger.error(f"Rate limit reset time error for key {key}: {e}")
            return None


# Rate limiting instances
api_rate_limiter = RateLimitCache()
instagram_api_rate_limiter = RateLimitCache()
