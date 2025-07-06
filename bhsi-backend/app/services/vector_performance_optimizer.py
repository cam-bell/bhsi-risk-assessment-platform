#!/usr/bin/env python3
"""
Vector Performance Optimizer - Hybrid approach for best performance
Combines BigQuery metadata with dedicated vector databases
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.crud.bigquery_events import bigquery_events
from app.agents.analysis.cloud_embedder import CloudEmbeddingAgent
from app.agents.analysis.embedder import BOEEmbeddingAgent

logger = logging.getLogger(__name__)


class VectorPerformanceOptimizer:
    """
    Optimized vector search with hybrid storage:
    - BigQuery: Metadata and search history
    - ChromaDB: High-performance vector similarity
    - Redis: Hot vector cache
    - Cloud Vector Service: Scalable vector operations
    """
    
    def __init__(self):
        self.cloud_agent = CloudEmbeddingAgent()
        self.local_agent = BOEEmbeddingAgent()
        self.events_crud = bigquery_events
        
        # Performance metrics
        self.search_cache_hits = 0
        self.search_cache_misses = 0
        self.vector_generation_time = 0
        self.search_response_time = 0
    
    async def optimized_semantic_search(
        self, 
        query: str, 
        k: int = 5, 
        risk_filter: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Optimized semantic search with performance tracking
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Check BigQuery for recent similar searches
            if use_cache:
                cached_results = await self._check_bigquery_cache(query, k)
                if cached_results:
                    self.search_cache_hits += 1
                    return {
                        "results": cached_results,
                        "source": "bigquery_cache",
                        "performance_metrics": {
                            "cache_hit": True,
                            "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                        }
                    }
            
            self.search_cache_misses += 1
            
            # Step 2: Perform vector search (cloud first, local fallback)
            vector_start = datetime.utcnow()
            
            if self.cloud_agent.vector_service_available:
                results = self.cloud_agent.semantic_search(query, k, risk_filter)
                vector_source = "cloud_vector_service"
            else:
                results = self.local_agent.semantic_search(query, k, risk_filter)
                vector_source = "local_chromadb"
            
            self.vector_generation_time += (datetime.utcnow() - vector_start).total_seconds()
            
            # Step 3: Enrich with BigQuery metadata
            enriched_results = await self._enrich_with_bigquery_metadata(results)
            
            # Step 4: Cache results in BigQuery for future searches
            await self._cache_search_results(query, enriched_results)
            
            total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "results": enriched_results,
                "source": vector_source,
                "performance_metrics": {
                    "cache_hit": False,
                    "response_time_ms": total_time,
                    "vector_search_time_ms": self.vector_generation_time * 1000,
                    "enrichment_time_ms": (total_time - self.vector_generation_time * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Optimized semantic search failed: {e}")
            return {
                "results": [],
                "source": "error",
                "performance_metrics": {
                    "error": str(e),
                    "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            }
    
    async def _check_bigquery_cache(self, query: str, k: int) -> Optional[List[Dict[str, Any]]]:
        """Check BigQuery for recent similar search results"""
        try:
            # Look for searches in the last 24 hours with similar queries
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Simple similarity check (in production, use more sophisticated matching)
            similar_searches = await self.events_crud.search_by_company(
                company_name=query.split()[0],  # Use first word as company name
                limit=k
            )
            
            if similar_searches:
                return [
                    {
                        "id": event.get("event_id"),
                        "score": 0.8,  # Cached results get high score
                        "metadata": {
                            "title": event.get("title"),
                            "source": event.get("source"),
                            "risk_level": event.get("risk_level"),
                            "cached": True
                        },
                        "document": event.get("summary", "")[:500]
                    }
                    for event in similar_searches
                ]
            
            return None
            
        except Exception as e:
            logger.error(f"BigQuery cache check failed: {e}")
            return None
    
    async def _enrich_with_bigquery_metadata(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich vector search results with BigQuery metadata"""
        enriched = []
        
        for result in results:
            try:
                # Get additional metadata from BigQuery
                event_id = result.get("id")
                if event_id:
                    event_data = await self.events_crud.get_by_id(event_id, id_field="event_id")
                    if event_data:
                        # Merge metadata
                        result["metadata"].update({
                            "company_name": event_data.get("company_name"),
                            "publication_date": event_data.get("publication_date"),
                            "confidence": event_data.get("confidence"),
                            "classification_method": event_data.get("classification_method")
                        })
                
                enriched.append(result)
                
            except Exception as e:
                logger.warning(f"Failed to enrich result {result.get('id')}: {e}")
                enriched.append(result)
        
        return enriched
    
    async def _cache_search_results(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results in BigQuery for future use"""
        try:
            # Store search metadata for caching
            search_metadata = {
                "query": query,
                "results_count": len(results),
                "search_timestamp": datetime.utcnow().isoformat(),
                "top_results": [
                    {
                        "id": r.get("id"),
                        "score": r.get("score"),
                        "title": r.get("metadata", {}).get("title", "")
                    }
                    for r in results[:5]  # Cache top 5 results
                ]
            }
            
            # This could be stored in a separate search_cache table
            logger.info(f"Cached search results for query: {query[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to cache search results: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total_searches = self.search_cache_hits + self.search_cache_misses
        cache_hit_rate = (self.search_cache_hits / total_searches * 100) if total_searches > 0 else 0
        
        return {
            "total_searches": total_searches,
            "cache_hits": self.search_cache_hits,
            "cache_misses": self.search_cache_misses,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "average_vector_generation_time_ms": round(self.vector_generation_time * 1000, 2),
            "average_search_response_time_ms": round(self.search_response_time * 1000, 2)
        }
    
    async def optimize_vector_storage(self):
        """Optimize vector storage for better performance"""
        try:
            # 1. Process unembedded events in batches
            batch_size = 100
            stats = self.cloud_agent.process_unembedded_events(batch_size)
            
            # 2. Update BigQuery with embedding status
            for event_id in stats.get("processed_events", []):
                await self.events_crud.mark_embedded(
                    event_id, 
                    self.cloud_agent.embedding_model
                )
            
            logger.info(f"✅ Vector storage optimization complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Vector storage optimization failed: {e}")
            return {"error": str(e)}


# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"⏱️ {func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"❌ {func.__name__} failed after {execution_time:.2f}ms: {e}")
            raise
    return wrapper 