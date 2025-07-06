#!/usr/bin/env python3
"""
Advanced Cache Service - Multi-layer caching for optimal performance
"""

import logging
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from app.services.search_cache_service import SearchCacheService
from app.crud.bigquery_events import bigquery_events

logger = logging.getLogger(__name__)


class AdvancedCacheService:
    """
    Multi-layer caching system:
    - L1: In-memory cache (fastest)
    - L2: Redis cache (fast)
    - L3: BigQuery cache (persistent)
    """
    
    def __init__(self):
        self.search_cache = SearchCacheService()
        self.events_crud = bigquery_events
        
        # In-memory cache (L1)
        self.memory_cache = {}
        self.memory_cache_ttl = 300  # 5 minutes
        
        # Cache statistics
        self.l1_hits = 0
        self.l1_misses = 0
        self.l2_hits = 0
        self.l2_misses = 0
        self.l3_hits = 0
        self.l3_misses = 0
    
    async def get_cached_search(
        self,
        company_name: str,
        days_back: int = 30,
        use_memory_cache: bool = True,
        use_redis_cache: bool = True,
        use_bigquery_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Multi-layer cache lookup
        """
        cache_key = self._generate_cache_key(company_name, days_back)
        
        # L1: In-memory cache (fastest)
        if use_memory_cache:
            l1_result = self._get_from_memory_cache(cache_key)
            if l1_result:
                self.l1_hits += 1
                logger.info(f"🎯 L1 cache hit for {company_name}")
                return l1_result
            self.l1_misses += 1
        
        # L2: Redis cache (fast)
        if use_redis_cache:
            l2_result = await self._get_from_redis_cache(cache_key)
            if l2_result:
                self.l2_hits += 1
                logger.info(f"🎯 L2 cache hit for {company_name}")
                # Update L1 cache
                self._set_memory_cache(cache_key, l2_result)
                return l2_result
            self.l2_misses += 1
        
        # L3: BigQuery cache (persistent)
        if use_bigquery_cache:
            l3_result = await self._get_from_bigquery_cache(company_name, days_back)
            if l3_result:
                self.l3_hits += 1
                logger.info(f"🎯 L3 cache hit for {company_name}")
                # Update L1 and L2 caches
                self._set_memory_cache(cache_key, l3_result)
                await self._set_redis_cache(cache_key, l3_result)
                return l3_result
            self.l3_misses += 1
        
        logger.info(f"❌ Cache miss for {company_name}")
        return None
    
    async def cache_search_results(
        self,
        company_name: str,
        search_results: Dict[str, Any],
        days_back: int = 30,
        ttl_hours: int = 24
    ):
        """
        Cache search results in all layers
        """
        cache_key = self._generate_cache_key(company_name, days_back)
        
        # Prepare cache data
        cache_data = {
            "company_name": company_name,
            "days_back": days_back,
            "search_results": search_results,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl_hours": ttl_hours
        }
        
        # L1: In-memory cache
        self._set_memory_cache(cache_key, cache_data)
        
        # L2: Redis cache
        await self._set_redis_cache(cache_key, cache_data, ttl_hours * 3600)
        
        # L3: BigQuery cache
        await self._set_bigquery_cache(company_name, cache_data)
        
        logger.info(f"💾 Cached search results for {company_name} in all layers")
    
    def _generate_cache_key(self, company_name: str, days_back: int) -> str:
        """Generate consistent cache key"""
        key_string = f"{company_name.lower()}_{days_back}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_memory_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get from L1 memory cache"""
        if cache_key in self.memory_cache:
            cached_data = self.memory_cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data["cached_at"])
            
            # Check TTL
            if datetime.utcnow() - cached_time < timedelta(seconds=self.memory_cache_ttl):
                return cached_data["search_results"]
            else:
                # Expired, remove from cache
                del self.memory_cache[cache_key]
        
        return None
    
    def _set_memory_cache(self, cache_key: str, data: Dict[str, Any]):
        """Set L1 memory cache"""
        self.memory_cache[cache_key] = {
            "search_results": data,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        # Limit memory cache size
        if len(self.memory_cache) > 1000:
            # Remove oldest entries
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]["cached_at"])
            del self.memory_cache[oldest_key]
    
    async def _get_from_redis_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get from L2 Redis cache"""
        try:
            cached_data = await self.search_cache.redis.get(f"search:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Redis cache get failed: {e}")
            return None
    
    async def _set_redis_cache(self, cache_key: str, data: Dict[str, Any], ttl: int = 3600):
        """Set L2 Redis cache"""
        try:
            await self.search_cache.redis.setex(
                f"search:{cache_key}",
                ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Redis cache set failed: {e}")
    
    async def _get_from_bigquery_cache(self, company_name: str, days_back: int) -> Optional[Dict[str, Any]]:
        """Get from L3 BigQuery cache"""
        try:
            # Look for recent searches in BigQuery
            recent_events = await self.events_crud.search_by_company(
                company_name=company_name,
                limit=50
            )
            
            if recent_events:
                # Convert to search results format
                search_results = {
                    "boe": {
                        "results": [
                            {
                                "titulo": event.get("title", ""),
                                "text": event.get("text", ""),
                                "fechaPublicacion": event.get("publication_date"),
                                "url_html": event.get("url", ""),
                                "risk_level": event.get("risk_level"),
                                "confidence": event.get("confidence")
                            }
                            for event in recent_events
                            if event.get("source") == "BOE"
                        ]
                    },
                    "newsapi": {
                        "articles": [
                            {
                                "title": event.get("title", ""),
                                "description": event.get("summary", ""),
                                "publishedAt": event.get("publication_date"),
                                "url": event.get("url", ""),
                                "risk_level": event.get("risk_level"),
                                "confidence": event.get("confidence")
                            }
                            for event in recent_events
                            if event.get("source") == "NewsAPI"
                        ]
                    }
                }
                
                return search_results
            
            return None
            
        except Exception as e:
            logger.error(f"BigQuery cache get failed: {e}")
            return None
    
    async def _set_bigquery_cache(self, company_name: str, cache_data: Dict[str, Any]):
        """Set L3 BigQuery cache (already handled by search results storage)"""
        # BigQuery cache is handled by the existing search results storage
        # This method is for future implementation of dedicated cache table
        pass
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_l1 = self.l1_hits + self.l1_misses
        total_l2 = self.l2_hits + self.l2_misses
        total_l3 = self.l3_hits + self.l3_misses
        
        l1_hit_rate = (self.l1_hits / total_l1 * 100) if total_l1 > 0 else 0
        l2_hit_rate = (self.l2_hits / total_l2 * 100) if total_l2 > 0 else 0
        l3_hit_rate = (self.l3_hits / total_l3 * 100) if total_l3 > 0 else 0
        
        return {
            "l1_cache": {
                "hits": self.l1_hits,
                "misses": self.l1_misses,
                "hit_rate_percent": round(l1_hit_rate, 2),
                "size": len(self.memory_cache)
            },
            "l2_cache": {
                "hits": self.l2_hits,
                "misses": self.l2_misses,
                "hit_rate_percent": round(l2_hit_rate, 2)
            },
            "l3_cache": {
                "hits": self.l3_hits,
                "misses": self.l3_misses,
                "hit_rate_percent": round(l3_hit_rate, 2)
            },
            "overall": {
                "total_requests": total_l1,
                "overall_hit_rate_percent": round(
                    (self.l1_hits + self.l2_hits + self.l3_hits) / 
                    max(total_l1, 1) * 100, 2
                )
            }
        }
    
    async def clear_cache(self, cache_type: str = "all"):
        """Clear specified cache layer"""
        if cache_type in ["all", "l1", "memory"]:
            self.memory_cache.clear()
            logger.info("🧹 Cleared L1 memory cache")
        
        if cache_type in ["all", "l2", "redis"]:
            try:
                # Clear all search cache keys
                keys = await self.search_cache.redis.keys("search:*")
                if keys:
                    await self.search_cache.redis.delete(*keys)
                logger.info("🧹 Cleared L2 Redis cache")
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")
        
        if cache_type in ["all", "l3", "bigquery"]:
            logger.info("🧹 L3 BigQuery cache cleared (data persists)")
    
    async def warm_cache(self, company_names: List[str], days_back: int = 30):
        """Warm up cache with common searches"""
        logger.info(f"🔥 Warming cache for {len(company_names)} companies")
        
        for company_name in company_names:
            try:
                # Try to get from cache first
                cached_result = await self.get_cached_search(company_name, days_back)
                
                if not cached_result:
                    # Perform search and cache results
                    search_results = await self.search_cache.perform_search_and_cache(
                        company_name=company_name,
                        days_back=days_back
                    )
                    
                    if search_results:
                        await self.cache_search_results(company_name, search_results, days_back)
                        logger.info(f"🔥 Warmed cache for {company_name}")
                
            except Exception as e:
                logger.error(f"Failed to warm cache for {company_name}: {e}")
        
        logger.info("🔥 Cache warming complete")


# Cache performance monitoring
class CachePerformanceMonitor:
    """Monitor cache performance metrics"""
    
    def __init__(self):
        self.cache_operations = []
    
    def log_cache_operation(
        self,
        operation: str,
        cache_layer: str,
        company_name: str,
        duration_ms: float,
        success: bool
    ):
        """Log cache operation performance"""
        self.cache_operations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "cache_layer": cache_layer,
            "company_name": company_name,
            "duration_ms": duration_ms,
            "success": success
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get cache performance summary"""
        if not self.cache_operations:
            return {"error": "No cache operations logged"}
        
        # Calculate statistics by cache layer
        layer_stats = {}
        for op in self.cache_operations:
            layer = op["cache_layer"]
            if layer not in layer_stats:
                layer_stats[layer] = {
                    "operations": 0,
                    "successful": 0,
                    "total_duration_ms": 0,
                    "durations": []
                }
            
            layer_stats[layer]["operations"] += 1
            layer_stats[layer]["total_duration_ms"] += op["duration_ms"]
            layer_stats[layer]["durations"].append(op["duration_ms"])
            
            if op["success"]:
                layer_stats[layer]["successful"] += 1
        
        # Calculate averages and success rates
        for layer, stats in layer_stats.items():
            stats["success_rate_percent"] = (
                stats["successful"] / stats["operations"] * 100
            )
            stats["average_duration_ms"] = (
                stats["total_duration_ms"] / stats["operations"]
            )
            stats["min_duration_ms"] = min(stats["durations"])
            stats["max_duration_ms"] = max(stats["durations"])
        
        return {
            "total_operations": len(self.cache_operations),
            "layer_statistics": layer_stats,
            "overall_success_rate_percent": (
                sum(1 for op in self.cache_operations if op["success"]) / 
                len(self.cache_operations) * 100
            )
        } 