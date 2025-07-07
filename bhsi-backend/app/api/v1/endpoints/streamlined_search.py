#!/usr/bin/env python3
"""
STREAMLINED Search API Endpoints - Ultra-fast search with optimized hybrid classification and caching
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from google.cloud import bigquery
import json
import datetime
import time
import logging
import json
from fastapi.responses import JSONResponse

from app.agents.search.streamlined_orchestrator import get_search_orchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier
from app.services.search_cache_service import SearchCacheService
from app.services.bigquery_database_integration import bigquery_db_integration
from app.services.hybrid_vector_storage import HybridVectorStorage
from app.api import deps
from app.dependencies.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
search_cache_service = SearchCacheService()
hybrid_vector_storage = HybridVectorStorage()

async def save_search_json_to_bigquery(company_name: str, search_json: dict, table_id: str):
    client = bigquery.Client()
    row = {
        "company name": company_name,
        "search result": json.dumps(search_json)  # Store as string, or use JSON column type
    }
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")

def map_risk_level_to_color(risk_level: str) -> str:
    """Map risk level to color (green, orange, red)"""
    if risk_level.startswith("High"):
        return "red"
    elif risk_level.startswith("Medium"):
        return "orange"
    elif risk_level.startswith("Low") or risk_level == "No-Legal":
        return "green"
    else:
        return "gray"  # For Unknown or other cases

# Request/Response Models
class StreamlinedSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True
    include_rss: bool = True  # Include RSS news sources
    rss_feeds: Optional[list] = None  # List of RSS feeds to include
    force_refresh: bool = False  # Force new search even if cached results exist
    cache_age_hours: int = 24  # Maximum age of cached results in hours
    

class SemanticSearchRequest(BaseModel):
    query: str
    k: Optional[int] = 5
    risk_filter: Optional[str] = None
    use_cache: bool = True
    include_metadata: bool = True

@router.post("/search")
async def streamlined_search(
    request: StreamlinedSearchRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    ULTRA-FAST STREAMLINED SEARCH ENDPOINT WITH CACHING
    
    **Performance Optimizations:**
    - Smart caching: Check BigQuery for existing results before searching
    - Streamlined agents: Fast data fetching without classification loops
    - Optimized hybrid classifier: 90%+ keyword gate efficiency
    - Smart LLM routing: Only for truly ambiguous cases
    - No unnecessary fallbacks or redundant processing
    
    **Caching Features:**
    - Check BigQuery for existing search results
    - Return cached results if available and fresh
    - Only search external sources if no cache or force refresh
    - Configurable cache age (default: 24 hours)
    
    **Features:**
    - BOE (Spanish official gazette) and news sources
    - Intelligent rate limit handling (NewsAPI 30-day limit)
    - Performance monitoring and statistics
    - Structured response format with confidence scores
    - Database persistence of search results
    
    **Expected Performance:**
    - Cached results: < 1 second response time
    - Fresh searches: 3-10 seconds (vs previous 2+ minutes)
    - 90%+ results classified in µ-seconds via keyword gate
    - Only 10% or less require expensive LLM analysis
    """
    
    overall_start_time = time.time()
    
    try:
        # Initialize streamlined components using factory
        classifier = OptimizedHybridClassifier()
        
        # Configure which agents to use
        active_agents = []
        if request.include_boe:
            active_agents.append("boe")
        if request.include_news:
            active_agents.append("newsapi")
        # Enable RSS feeds if requested
        if request.include_rss:
            # Use only selected RSS feeds if provided, else default to demo feeds
            selected_rss_feeds = getattr(request, 'rss_feeds', None)
            if selected_rss_feeds:
                active_agents.extend(selected_rss_feeds)
            else:
                active_agents.extend([
                    "elpais",
                    "expansion",
                    "elmundo",  # Disabled for demo
                    "abc",      # Disabled for demo
                    "lavanguardia", # Disabled for demo
                    "elconfidencial", # Disabled for demo
                    "eldiario", # Disabled for demo
                    "europapress" # Disabled for demo
                ])
        
        if not active_agents:
            raise HTTPException(
                status_code=400,
                detail="At least one source (BOE, news, or RSS) must be enabled"
            )
        
        # STEP 1: SMART CACHING - Check BigQuery for existing results
        cache_start_time = time.time()
        search_data = await search_cache_service.get_search_results(
            company_name=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            active_agents=active_agents,
            cache_age_hours=request.cache_age_hours,
            force_refresh=request.force_refresh
        )
        cache_time = time.time() - cache_start_time
        
        search_results = search_data['results']
        search_method = search_data['search_method']
        cache_info = search_data.get('cache_info', {})
        
        # STEP 2: BULK CLASSIFICATION (optimized hybrid approach)
        classification_start_time = time.time()
        classified_results = []
        
        # Process BOE results
        if "boe" in search_results and search_results["boe"].get("results"):
            for boe_result in search_results["boe"]["results"]:
                try:
                    # Skip classification if already classified (cached results)
                    if boe_result.get("method") == "cached":
                        classified_result = {
                            "source": "BOE",
                            "date": boe_result.get("fechaPublicacion"),
                            "title": boe_result.get("titulo", ""),
                            "summary": boe_result.get("summary"),
                            "risk_level": boe_result.get("risk_level", "Unknown"),
                            "risk_color": map_risk_level_to_color(boe_result.get("risk_level", "Unknown")),
                            "confidence": boe_result.get("confidence", 0.5),
                            "method": "cached",
                            "processing_time_ms": 0,
                            "url": boe_result.get("url_html", ""),
                            # BOE-specific fields
                            "identificador": boe_result.get("identificador"),
                            "seccion": boe_result.get("seccion_codigo"),
                            "seccion_nombre": boe_result.get("seccion_nombre")
                        }
                        classified_results.append(classified_result)
                    else:
                        # Optimized hybrid classification for fresh results
                        classification = await classifier.classify_document(
                            text=boe_result.get("text", boe_result.get("summary", "")),
                            title=boe_result.get("titulo", ""),
                            source="BOE",
                            section=boe_result.get("seccion_codigo", "")
                        )
                        classified_result = {
                            "source": "BOE",
                            "date": boe_result.get("fechaPublicacion"),
                            "title": boe_result.get("titulo", ""),
                            "summary": boe_result.get("summary"),
                            "risk_level": classification.get("label", "Unknown"),
                            "risk_color": map_risk_level_to_color(classification.get("label", "Unknown")),
                            "confidence": classification.get("confidence", 0.5),
                            "method": classification.get("method", "unknown"),
                            "processing_time_ms": classification.get("processing_time_ms", 0),
                            "url": boe_result.get("url_html", ""),
                            # BOE-specific fields
                            "identificador": boe_result.get("identificador"),
                            "seccion": boe_result.get("seccion_codigo"),
                            "seccion_nombre": boe_result.get("seccion_nombre")
                        }
                        classified_results.append(classified_result)
                except Exception as e:
                    # Simple fallback - don't slow down the entire response
                    classified_result = {
                        "source": "BOE",
                        "date": boe_result.get("fechaPublicacion"),
                        "title": boe_result.get("titulo", ""),
                        "summary": boe_result.get("summary"),
                        "risk_level": "Unknown",
                        "risk_color": map_risk_level_to_color("Unknown"),
                        "confidence": 0.3,
                        "method": "error_fallback",
                        "processing_time_ms": 0,
                        "url": boe_result.get("url_html", ""),
                        "identificador": boe_result.get("identificador"),
                        "seccion": boe_result.get("seccion_codigo"),
                        "seccion_nombre": boe_result.get("seccion_nombre"),
                        "error": str(e)
                    }
                    classified_results.append(classified_result)
        
        # Process News results
        if "newsapi" in search_results and search_results["newsapi"].get("articles"):
            for article in search_results["newsapi"]["articles"]:
                try:
                    # Type check to prevent 'str' object has no attribute 'get' errors
                    if not isinstance(article, dict):
                        logger.warning(f"Skipping non-dict NewsAPI article: {type(article)} - {article}")
                        continue
                    
                    # Skip classification if already classified (cached results)
                    if article.get("method") == "cached":
                        classified_result = {
                            "source": "News",
                            "date": article.get("publishedAt"),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": article.get("risk_level", "Unknown"),
                            "risk_color": map_risk_level_to_color(article.get("risk_level", "Unknown")),
                            "confidence": article.get("confidence", 0.5),
                            "method": "cached",
                            "processing_time_ms": 0,
                            "url": article.get("url", ""),
                            # News-specific fields
                            "author": article.get("author"),
                            "source_name": article.get("source", "Unknown")
                        }
                        classified_results.append(classified_result)
                    else:
                        # Optimized hybrid classification for fresh results
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="News"
                        )
                        classified_result = {
                            "source": "News",
                            "date": article.get("publishedAt"),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "risk_color": map_risk_level_to_color(classification.get("label", "Unknown")),
                            "confidence": classification.get("confidence", 0.5),
                            "method": classification.get("method", "unknown"),
                            "processing_time_ms": classification.get("processing_time_ms", 0),
                            "url": article.get("url", ""),
                            # News-specific fields
                            "author": article.get("author"),
                            "source_name": article.get("source", "Unknown")
                        }
                        classified_results.append(classified_result)
                except Exception as e:
                    # Simple fallback
                    classified_result = {
                        "source": "News",
                        "date": article.get("publishedAt"),
                        "title": article.get("title", ""),
                        "summary": article.get("description"),
                        "risk_level": "Unknown",
                        "risk_color": map_risk_level_to_color("Unknown"),
                        "confidence": 0.3,
                        "method": "error_fallback",
                        "processing_time_ms": 0,
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "source_name": article.get("source", "Unknown"),
                        "error": str(e)
                    }
                    classified_results.append(classified_result)
        
        # Process RSS results (only selected feeds)
        rss_agents = (
            selected_rss_feeds if (request.include_rss and selected_rss_feeds)
            else [
                "elpais",
                "expansion"
                "elmundo",  # Disabled for demo
                "abc",      # Disabled for demo
                "lavanguardia", # Disabled for demo
                "elconfidencial", # Disabled for demo
                "eldiario", # Disabled for demo
                "europapress" # Disabled for demo
            ]
        )
        if request.include_rss:
            for agent_name in rss_agents:
                if agent_name in search_results and search_results[agent_name].get("articles"):
                    for article in search_results[agent_name]["articles"]:
                        try:
                            # Optimized hybrid classification
                            if article.get("method") == "cached":
                                classified_result = {
                                    "source": f"RSS-{agent_name.upper()}",
                                    "date": article.get("publishedAt"),
                                    "title": article.get("title", ""),
                                    "summary": article.get("description"),
                                    "risk_level": article.get("risk_level", "Unknown"),
                                    "risk_color": map_risk_level_to_color(article.get("risk_level", "Unknown")),
                                    "confidence": article.get("confidence", 0.5),
                                    "method": "cached",
                                    "processing_time_ms": 0,
                                    "url": article.get("url", ""),
                                    # RSS-specific fields
                                    "author": article.get("author"),
                                    "category": article.get("category"),
                                    "source_name": article.get("source_name", f"RSS-{agent_name.upper()}")
                                }
                                classified_results.append(classified_result)
                            else:
                                # Optimized hybrid classification for fresh results
                                classification = await classifier.classify_document(
                                    text=article.get("content", article.get("description", "")),
                                    title=article.get("title", ""),
                                    source=f"RSS-{agent_name.upper()}"
                                )
                                classified_result = {
                                    "source": f"RSS-{agent_name.upper()}",
                                    "date": article.get("publishedAt"),
                                    "title": article.get("title", ""),
                                    "summary": article.get("description"),
                                    "risk_level": classification.get("label", "Unknown"),
                                    "risk_color": map_risk_level_to_color(classification.get("label", "Unknown")),
                                    "confidence": classification.get("confidence", 0.5),
                                    "method": classification.get("method", "unknown"),
                                    "processing_time_ms": classification.get("processing_time_ms", 0),
                                    "url": article.get("url", ""),
                                    # RSS-specific fields
                                    "author": article.get("author"),
                                    "category": article.get("category"),
                                    "source_name": article.get("source_name", f"RSS-{agent_name.upper()}")
                                }
                                classified_results.append(classified_result)
                        except Exception as e:
                            # Simple fallback
                            classified_result = {
                                "source": f"RSS-{agent_name.upper()}",
                                "date": article.get("publishedAt"),
                                "title": article.get("title", ""),
                                "summary": article.get("description"),
                                "risk_level": "Unknown",
                                "risk_color": map_risk_level_to_color("Unknown"),
                                "confidence": 0.3,
                                "method": "error_fallback",
                                "processing_time_ms": 0,
                                "url": article.get("url", ""),
                                "author": article.get("author"),
                                "category": article.get("category"),
                                "source_name": article.get("source_name", f"RSS-{agent_name.upper()}"),
                                "error": str(e)
                            }
                            classified_results.append(classified_result)
        
        classification_time = time.time() - classification_start_time
        
        # STEP 3: RESPONSE PREPARATION
        valid_results = []
        
        # Validate and format dates
        for result in classified_results:
            date_val = result.get("date")
            if date_val:
                try:
                    if isinstance(date_val, str):
                        # Handle different date formats
                        if "T" in date_val:
                            result["date"] = date_val  # Already ISO format
                        else:
                            # Convert YYYY-MM-DD to ISO
                            parsed_date = datetime.datetime.strptime(date_val, "%Y-%m-%d")
                            result["date"] = parsed_date.isoformat() + "Z"
                    valid_results.append(result)
                except Exception:
                    # Include results with date parsing errors but mark them
                    result["date_parse_error"] = True
                    valid_results.append(result)
        
        # Sort by date, most recent first
        valid_results.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Ensure every result has a risk_color
        for result in valid_results:
            if "risk_color" not in result or not result["risk_color"]:
                result["risk_color"] = map_risk_level_to_color(result.get("risk_level", "Unknown"))
                logger.info(f"Added risk_color '{result['risk_color']}' to result with risk_level '{result.get('risk_level', 'Unknown')}'")
        
        # Debug: Log the first few results to verify risk_color is present
        for i, result in enumerate(valid_results[:3]):
            logger.info(f"Result {i}: source={result.get('source')}, risk_level={result.get('risk_level')}, risk_color={result.get('risk_color')}")
        
        # Calculate overall risk summary
        risk_counts = {"red": 0, "orange": 0, "green": 0, "gray": 0}
        for result in valid_results:
            color = result.get("risk_color", "gray")
            risk_counts[color] += 1
        
        # Determine overall risk level
        if risk_counts["red"] > 0:
            overall_risk = "red"
        elif risk_counts["orange"] > 0:
            overall_risk = "orange"
        else:
            overall_risk = "green"
        
        # Calculate total time
        total_time = time.time() - overall_start_time
        
        # Build optimized response with cache information
        response = {
            "company_name": request.company_name,
            "search_date": datetime.datetime.now().isoformat(),
            "date_range": {
                "start": request.start_date,
                "end": request.end_date,
                "days_back": request.days_back
            },
            "results": valid_results,
            "metadata": {
                "total_results": len(valid_results),
                "boe_results": len([r for r in valid_results if r["source"] == "BOE"]),
                "news_results": len([r for r in valid_results if r["source"] == "News"]),
                "rss_results": len([r for r in valid_results if r["source"].startswith("RSS-")]),
                "high_risk_results": len([r for r in valid_results if r["risk_level"] == "High-Legal"]),
                "sources_searched": active_agents
            },
            "performance": {
                **classifier.get_performance_stats(),
                "total_time_seconds": f"{total_time:.2f}",
                "cache_time_seconds": f"{cache_time:.2f}",
                "classification_time_seconds": f"{classification_time:.2f}",
                "optimization": "Smart caching + streamlined search + optimized hybrid classifier"
            },
            "cache_info": {
                "search_method": search_method,
                "cache_age_hours": cache_info.get("age_hours", 0),
                "total_events": cache_info.get("total_events", 0),
                "sources": cache_info.get("sources", []),
                "force_refresh": request.force_refresh
            },
            "database_stats": search_data.get("db_stats", {
                "raw_docs_saved": 0,
                "events_created": 0,
                "total_processed": 0,
                "errors": []
            }),
            "overall_risk": overall_risk,
            "risk_summary": {
                "overall_risk": overall_risk,
                "risk_distribution": risk_counts,
                "total_articles": len(valid_results),
                "high_risk_articles": risk_counts["red"],
                "medium_risk_articles": risk_counts["orange"],
                "low_risk_articles": risk_counts["green"]
            }
        }
        table_id = "solid-topic-443216-b2.risk_monitoring.risk_assessment"
        await save_search_json_to_bigquery(request.company_name, response, table_id)
        return response
        
    except Exception as e:
        # Return error response with timing information
        total_time = time.time() - overall_start_time
        
        error_response = {
            "company_name": request.company_name,
            "search_date": datetime.datetime.now().isoformat(),
            "date_range": {
                "start": request.start_date,
                "end": request.end_date,
                "days_back": request.days_back
            },
            "results": [],
            "error": f"Streamlined search failed: {str(e)}",
            "metadata": {
                "total_results": 0,
                "boe_results": 0,
                "news_results": 0,
                "rss_results": 0,
                "high_risk_results": 0,
                "sources_searched": []
            },
            "performance": {
                "total_time_seconds": f"{total_time:.2f}",
                "error": "Search failed before completion"
            },
            "cache_info": {
                "search_method": "error",
                "cache_age_hours": 0,
                "total_events": 0,
                "sources": [],
                "force_refresh": request.force_refresh
            },
            "database_stats": {
                "raw_docs_saved": 0,
                "events_created": 0,
                "total_processed": 0,
                "errors": [str(e)]
            }
        }
        
        return error_response


@router.get("/search/health")
async def streamlined_search_health():
    """
    Health check for streamlined search system with caching
    """
    try:
        orchestrator = get_search_orchestrator()
        classifier = OptimizedHybridClassifier()
        
        return {
            "status": "healthy",
            "message": "Streamlined search system with caching is operational",
            "orchestrator_type": type(orchestrator).__name__,
            "classifier_type": type(classifier).__name__,
            "cache_service": "SearchCacheService",
            "features": [
                "Smart caching with BigQuery",
                "Ultra-fast search across multiple sources",
                "Optimized hybrid classification",
                "Intelligent rate limit handling",
                "Performance monitoring",
                "Database persistence"
            ],
            "sources_available": [
                "BOE (Spanish Official Gazette)",
                "NewsAPI (International news)"
                # "RSS feeds (Spanish news sources)" - Disabled for demo
            ],
            "caching": {
                "enabled": True,
                "cache_age_hours": 24,
                "force_refresh_option": True
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Streamlined search system is not operational"
        }


@router.get("/search/performance")
async def streamlined_search_performance():
    """
    Get detailed performance statistics for the OPTIMIZED hybrid classifier with caching
    """
    try:
        classifier = OptimizedHybridClassifier()
        stats = classifier.get_performance_stats()
        
        return {
            "status": "success", 
            "message": "Performance statistics for OPTIMIZED STREAMLINED search system with caching",
            "architecture": {
                "cache_stage": "Smart BigQuery cache check (µ-seconds)",
                "search_stage": "Streamlined agents - Fast data fetching only",
                "classification_stage_1": "Optimized keyword gate (µ-seconds) - 90%+ efficiency",
                "classification_stage_2": "Smart LLM routing (only for truly ambiguous cases)",
                "optimization": "Caching + Removed classification loops + optimized patterns"
            },
            "statistics": stats,
            "improvements": {
                "caching": "BigQuery cache check before external searches",
                "search_optimization": "No classification during search loops",
                "keyword_patterns": "Enhanced patterns for Spanish D&O risks",
                "smart_routing": "Only legal-looking ambiguous content sent to LLM",
                "expected_performance": "Cached: <1s, Fresh: 90%+ improvement over previous system"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve performance stats: {str(e)}"
        }


@router.get("/search/database-stats")
async def get_database_stats():
    """
    Get BigQuery database statistics
    """
    try:
        stats = await bigquery_db_integration.get_database_stats()
        
        return {
            "status": "success",
            "database": "BigQuery",
            "stats": stats,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database stats failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "database": "BigQuery"
        }


@router.get("/search/cache-stats")
async def get_cache_stats():
    """
    Get cache statistics and information
    """
    try:
        # Get database stats to show cache data
        db_stats = await bigquery_db_integration.get_database_stats()
        
        return {
            "status": "success",
            "cache_system": "BigQuery-based caching",
            "cache_configuration": {
                "default_cache_age_hours": 24,
                "force_refresh_option": True,
                "cache_sources": ["BOE", "NewsAPI", "RSS feeds"],
                "cache_storage": "BigQuery events table"
            },
            "database_stats": db_stats,
            "cache_benefits": {
                "performance": "Sub-second response for cached results",
                "cost_savings": "Reduced external API calls",
                "reliability": "Consistent results from BigQuery",
                "scalability": "No local cache limitations"
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "cache_system": "BigQuery-based caching"
        }


@router.post("/semantic-search")
async def streamlined_semantic_search(
    request: SemanticSearchRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    HYBRID SEMANTIC SEARCH ENDPOINT
    
    **Features:**
    - True hybrid vector storage (BigQuery + ChromaDB + Cloud)
    - Semantic similarity search across all stored vectors
    - Multi-layer caching for optimal performance
    - Risk filtering and metadata enrichment
    - Parallel search across multiple vector stores
    
    **Vector Storage:**
    - BigQuery: Persistent vector storage with metadata
    - ChromaDB: High-performance local similarity search
    - Cloud Vector Service: Scalable cloud-based search
    
    **Performance:**
    - Cached results: < 500ms response time
    - Fresh searches: 1-3 seconds
    - Parallel search across all vector stores
    """
    
    start_time = time.time()
    
    try:
        # Perform hybrid semantic search
        search_results = await hybrid_vector_storage.hybrid_semantic_search(
            query=request.query,
            k=request.k,
            risk_filter=request.risk_filter,
            use_cache=request.use_cache
        )
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Prepare response
        response = {
            "status": "success",
            "query": request.query,
            "search_results": search_results["results"],
            "source": search_results["source"],
            "performance_metrics": {
                **search_results["performance_metrics"],
                "total_time_seconds": f"{total_time:.2f}"
            },
            "hybrid_storage": {
                "bigquery_searches": search_results["performance_metrics"].get("bigquery_searches", 0),
                "chromadb_searches": search_results["performance_metrics"].get("chromadb_searches", 0),
                "cloud_searches": search_results["performance_metrics"].get("cloud_searches", 0),
                "cache_hits": search_results["performance_metrics"].get("cache_hits", 0)
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Semantic search failed: {e}")
        
        return {
            "status": "error",
            "query": request.query,
            "error": str(e),
            "performance_metrics": {
                "total_time_seconds": f"{total_time:.2f}",
                "error": "Semantic search failed"
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }


@router.get("/vector-stats")
async def get_vector_stats(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get hybrid vector storage statistics
    """
    try:
        stats = hybrid_vector_storage.get_hybrid_stats()
        
        return {
            "status": "success",
            "hybrid_vector_storage": {
                "bigquery_searches": stats["bigquery_searches"],
                "chromadb_searches": stats["chromadb_searches"],
                "cloud_searches": stats["cloud_searches"],
                "cache_hits": stats["cache_hits"],
                "cloud_service_available": stats["cloud_service_available"],
                "local_service_available": stats["local_service_available"],
                "bigquery_available": stats["bigquery_available"]
            },
            "storage_systems": {
                "bigquery": "Persistent vector storage with metadata",
                "chromadb": "High-performance local similarity search",
                "cloud_vector_service": "Scalable cloud-based search"
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vector stats failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/migrate-vectors")
async def migrate_vectors_to_bigquery(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Migrate existing vectors from ChromaDB to BigQuery
    """
    try:
        migration_stats = await hybrid_vector_storage.migrate_vectors_to_bigquery()
        
        return {
            "status": "success",
            "migration_stats": migration_stats,
            "message": "Vector migration completed",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vector migration failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        } 

@router.post("/embed-documents")
async def embed_documents(
    request: dict,
    current_user: dict = Depends(get_current_active_user)
):
    """
    🚀 CLOUD-NATIVE embedding endpoint
    
    Full microservice integration:
    1. Apply keyword gate filter
    2. Generate embeddings via CLOUD embedding service  
    3. Store vectors via CLOUD vector search service → BigQuery
    """
    start_time = time.time()
    
    try:
        documents = request.get("documents", [])
        company_name = request.get("company_name", "")
        
        if not documents:
            return {
                "status": "error",
                "error": "No documents provided",
                "results": []
            }
        
        # 🌐 CLOUD SERVICES: Use deployed microservices  
        from app.core.config import settings
        import httpx
        
        EMBEDDER_SERVICE_URL = settings.EMBEDDER_SERVICE_URL
        VECTOR_SEARCH_URL = settings.VECTOR_SEARCH_SERVICE_URL
        
        # Apply keyword gate filter (same logic as frontend)
        def applies_keyword_gate(document: dict, threshold: str = "medium") -> bool:
            risk_level = document.get("risk_level", "").lower()
            
            risk_hierarchy = {
                "low": 1, "medium": 2, "high": 3, "legal": 4, "financial": 4, "regulatory": 4
            }
            
            threshold_level = risk_hierarchy.get(threshold.lower(), 2)
            
            # Check risk level
            for risk_keyword, level in risk_hierarchy.items():
                if risk_keyword in risk_level and level >= threshold_level:
                    return True
            
            # Check D&O keywords
            do_keywords = [
                "director", "consejero", "administrador", "governance", 
                "corporate", "board", "junta", "responsabilidad",
                "legal", "regulatory", "compliance", "audit"
            ]
            
            text_content = f"{document.get('title', '')} {document.get('summary', '')}".lower()
            return any(keyword in text_content for keyword in do_keywords)
        
        # Filter documents
        filtered_docs = [doc for doc in documents if applies_keyword_gate(doc)]
        max_docs_to_embed = min(len(filtered_docs), 15)  # Limit for performance
        
        embedded_results = []
        vectors_created = 0
        
        # 🎯 PREPARE DOCUMENTS for cloud vector service
        cloud_documents = []
        
        for i, doc in enumerate(filtered_docs[:max_docs_to_embed]):
            text_content = doc.get("summary", doc.get("title", ""))
            
            if not text_content.strip():
                continue
                
            try:
                # Create unique document ID for cloud storage
                doc_id = f"doc_{company_name}_{i}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                # Parse publication date to proper format
                pub_date = None
                if doc.get("date"):
                    try:
                        # Handle various date formats
                        date_str = doc.get("date", "")
                        if "T" in date_str:
                            pub_date = datetime.datetime.fromisoformat(date_str.replace("Z", "")).date().isoformat()
                        else:
                            pub_date = date_str[:10]  # Take YYYY-MM-DD part
                    except:
                        pub_date = datetime.datetime.now().date().isoformat()
                
                # 📋 PREPARE metadata for BigQuery storage
                metadata = {
                    "company_name": company_name,
                    "risk_level": doc.get("risk_level", ""),
                    "publication_date": pub_date,
                    "source": doc.get("source", ""),
                    "title": doc.get("title", "")[:500] if doc.get("title") else "",
                    "text_summary": text_content[:1000],
                    "url": doc.get("url", ""),
                    "confidence": doc.get("confidence", 0),
                    "embedding_model": "text-embedding-004",  # Google's cloud model
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                
                cloud_documents.append({
                    "id": doc_id,
                    "text": text_content[:2000],  # Limit text length
                    "metadata": metadata
                })
                
                embedded_results.append({
                    "document_id": i,
                    "title": doc.get("title", ""),
                    "vector_id": doc_id,
                    "status": "prepared"
                })
                
            except Exception as e:
                logger.error(f"Document preparation error for document {i}: {e}")
                embedded_results.append({
                    "document_id": i,
                    "title": doc.get("title", ""),
                    "status": "error",
                    "error": str(e)
                })
        
        # 🚀 CALL CLOUD VECTOR SEARCH SERVICE for embedding + storage
        if cloud_documents:
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{VECTOR_SEARCH_URL}/embed",
                        json={"documents": cloud_documents}
                    )
                    
                    if response.status_code == 200:
                        cloud_result = response.json()
                        vectors_created = cloud_result.get("added_documents", 0)
                        
                        # Update results with success status
                        for result in embedded_results:
                            if result["status"] == "prepared":
                                result["status"] = "success"
                                
                        logger.info(f"✅ Cloud vector service stored {vectors_created} vectors for {company_name}")
                        
                    else:
                        logger.error(f"❌ Cloud vector service failed: {response.status_code} - {response.text}")
                        # Update results with failure status
                        for result in embedded_results:
                            if result["status"] == "prepared":
                                result["status"] = "cloud_service_failed"
                                result["error"] = f"Vector service returned {response.status_code}"
                        
            except Exception as e:
                logger.error(f"❌ Cloud vector service call failed: {e}")
                # Update results with failure status
                for result in embedded_results:
                    if result["status"] == "prepared":
                        result["status"] = "cloud_service_error"
                        result["error"] = str(e)
        
        total_time = time.time() - start_time
        
        return {
            "status": "success",
            "company_name": company_name,
            "cloud_integration": {
                "embedder_service": EMBEDDER_SERVICE_URL,
                "vector_search_service": VECTOR_SEARCH_URL,
                "embedding_model": "text-embedding-004"
            },
            "summary": {
                "total_documents": len(documents),
                "filtered_documents": len(filtered_docs),
                "processed_documents": len(cloud_documents),
                "vectors_created": vectors_created,
                "processing_time_seconds": f"{total_time:.2f}"
            },
            "results": embedded_results,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"🚀 Cloud-native document embedding failed: {e}")
        
        return {
            "status": "error",
            "error": str(e),
            "processing_time_seconds": f"{total_time:.2f}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

@router.get("/search/merged/{company_name}")
async def get_merged_search_results(company_name: str):
    """
    Retrieve and merge all search results for a company from BigQuery.
    """
    client = bigquery.Client()
    table_id = "solid-topic-443216-b2.risk_monitoring.risk_assessment"

    # 1. Query all rows for the company
    query = f"""
        SELECT `search result`
        FROM `{table_id}`
        WHERE `company name` = @company_name
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name)
        ]
    )
    merged_results = []
    meta = None
    search_date = None
    for row in client.query(query, job_config=job_config):
        try:
            result_json = json.loads(row['search result'])
            docs = result_json.get("results", [])
            merged_results.extend(docs)
            # Optionally, grab meta fields from the first row
            if not meta:
                meta = result_json.get("metadata")
            if not search_date:
                search_date = result_json.get("search_date")
        except Exception as e:
            continue

    # Remove duplicates by URL
    seen_urls = set()
    unique_results = []
    for doc in merged_results:
        url = doc.get("url")
        if url and url not in seen_urls:
            unique_results.append(doc)
            seen_urls.add(url)

    # Build merged JSON
    merged_json = {
        "company_name": company_name,
        "search_date": search_date,
        "results": unique_results,
        "metadata": meta,
        "total_results": len(unique_results)
    }

    # Print to console (for debugging)
    print(json.dumps(merged_json, indent=2, ensure_ascii=False))

    # Return as API response
    return JSONResponse(content=merged_json) 