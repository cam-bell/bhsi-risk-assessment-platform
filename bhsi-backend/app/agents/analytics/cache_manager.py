#!/usr/bin/env python3
"""
Cache Manager for Analytics Responses
Provides caching for expensive analytics operations to improve performance
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None


class AnalyticsCacheManager:
    """Manages caching for analytics responses"""
    
    def __init__(self, default_ttl_hours: int = 24):
        """Initialize cache manager"""
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl_hours = default_ttl_hours
        self.max_cache_size = 1000  # Maximum number of cache entries
        
    def _generate_cache_key(self, operation: str, **kwargs) -> str:
        """Generate a unique cache key for the operation"""
        # Create a deterministic string representation
        key_data = {
            "operation": operation,
            **kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        
        # Generate hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(
        self, 
        operation: str, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached data for an operation
        
        Args:
            operation: Name of the operation (e.g., 'company_analytics')
            **kwargs: Operation parameters
            
        Returns:
            Cached data if available and not expired, None otherwise
        """
        cache_key = self._generate_cache_key(operation, **kwargs)
        
        if cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        
        # Check if expired
        if datetime.utcnow() > entry.expires_at:
            logger.debug(f"Cache entry expired for {operation}")
            del self.cache[cache_key]
            return None
        
        # Update access metadata
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        
        logger.debug(f"Cache hit for {operation}")
        return entry.data
    
    def set(
        self, 
        operation: str, 
        data: Dict[str, Any], 
        ttl_hours: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Cache data for an operation
        
        Args:
            operation: Name of the operation
            data: Data to cache
            ttl_hours: Time to live in hours (uses default if None)
            **kwargs: Operation parameters
        """
        cache_key = self._generate_cache_key(operation, **kwargs)
        
        # Use default TTL if not specified
        if ttl_hours is None:
            ttl_hours = self.default_ttl_hours
        
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=ttl_hours)
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            data=data,
            created_at=now,
            expires_at=expires_at,
            access_count=1,
            last_accessed=now
        )
        
        # Check cache size limit
        if len(self.cache) >= self.max_cache_size:
            self._evict_oldest()
        
        self.cache[cache_key] = entry
        logger.debug(f"Cached data for {operation}")
    
    def invalidate(self, operation: str, **kwargs) -> bool:
        """
        Invalidate cache entry for an operation
        
        Args:
            operation: Name of the operation
            **kwargs: Operation parameters
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        cache_key = self._generate_cache_key(operation, **kwargs)
        
        if cache_key in self.cache:
            del self.cache[cache_key]
            logger.debug(f"Invalidated cache for {operation}")
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Analytics cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        
        # Count expired entries
        expired_count = sum(
            1 for entry in self.cache.values() 
            if now > entry.expires_at
        )
        
        # Calculate average access count
        total_access = sum(entry.access_count for entry in self.cache.values())
        avg_access = total_access / len(self.cache) if self.cache else 0
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "max_size": self.max_cache_size,
            "utilization_percent": (len(self.cache) / self.max_cache_size) * 100,
            "total_accesses": total_access,
            "average_accesses_per_entry": round(avg_access, 2),
            "default_ttl_hours": self.default_ttl_hours
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if now > entry.expires_at
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry (LRU strategy)"""
        if not self.cache:
            return
        
        # Find entry with oldest last_accessed time
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or datetime.min
        )
        
        del self.cache[oldest_key]
        logger.debug("Evicted oldest cache entry due to size limit")


# Global cache instance
analytics_cache = AnalyticsCacheManager() 