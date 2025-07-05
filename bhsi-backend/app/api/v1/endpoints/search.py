#!/usr/bin/env python3
"""
Search API Endpoints - Unified search across BOE and news sources

⚠️  DEPRECATED: This endpoint has been replaced by streamlined_search.py
    Use the streamlined search endpoint for better performance and features.
    This file is kept for reference and backward compatibility only.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import datetime

from app.agents.search.streamlined_orchestrator import get_search_orchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier

router = APIRouter()

# Request/Response Models
class SearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True
    include_rss: bool = True  # Include RSS news sources
    rss_feeds: Optional[list[str]] = None  # List of selected RSS feeds


@router.post("/search")
async def search(
    request: SearchRequest
):
    """
    MULTI-SOURCE SEARCH ENDPOINT
    
    **Features:**
    - BOE (Spanish official gazette) and news sources
    - Intelligent rate limit handling (NewsAPI 30-day limit)
    - Performance monitoring and statistics
    - Structured response format with confidence scores
    - Database persistence of search results
    
    **Expected Performance:**
    - Total response time: 3-10 seconds
    - Hybrid classification with keyword gate efficiency
    """
    
    overall_start_time = time.time()
    
    try:
        # Initialize components using factory
        orchestrator = get_search_orchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Configure which agents to use
        active_agents = []
        if request.include_boe:
            active_agents.append("boe")
        if request.include_news:
            active_agents.append("newsapi")
        if request.include_rss:
            # Use selected RSS feeds if provided, else all
            rss_agents = request.rss_feeds if request.rss_feeds else [
                "elpais", "expansion", "elmundo", "abc",
                "lavanguardia", "elconfidencial", "eldiario",
                "europapress"
            ]
            active_agents.extend(rss_agents)
            
        if not active_agents:
            raise HTTPException(
                status_code=400,
                detail="At least one source (BOE, news, or RSS) must be enabled"
            )
        
        # STEP 1: SEARCH
        search_start_time = time.time()
        search_results = await orchestrator.search_all(
            query=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            active_agents=active_agents
        )
        search_time = time.time() - search_start_time
        
        # STEP 2: DATABASE INTEGRATION - Save raw results
        db_start_time = time.time()
        # Since we're using BigQuery only, skip database integration for now
        db_stats = {
            "raw_docs_saved": 0,
            "events_created": 0,
            "total_processed": 0,
            "errors": []
        }
        db_time = time.time() - db_start_time
        
        # STEP 3: CLASSIFICATION
        classification_start_time = time.time()
        classified_results = []
        
        # Process BOE results
        if "boe" in search_results and search_results["boe"].get("results"):
            for result in search_results["boe"]["results"]:
                try:
                    classification = await classifier.classify_document(
                        text=result.get("text", result.get("summary", "")),
                        title=result.get("titulo", ""),
                        source="BOE",
                        section=result.get("seccion_codigo", "")
                    )
                    
                    classified_result = {
                        "source": "BOE",
                        "date": result.get("fechaPublicacion"),
                        "title": result.get("titulo", ""),
                        "summary": result.get("summary"),
                        "risk_level": classification.get("label", "Unknown"),
                        "confidence": classification.get("confidence", 0.5),
                        "method": classification.get("method", "unknown"),
                        "processing_time_ms": classification.get("processing_time_ms", 0),
                        "url": result.get("url_html", ""),
                        "identificador": result.get("identificador"),
                        "seccion": result.get("seccion_codigo"),
                        "seccion_nombre": result.get("seccion_nombre")
                    }
                    classified_results.append(classified_result)
                    
                except Exception as e:
                    classified_result = {
                        "source": "BOE",
                        "date": result.get("fechaPublicacion"),
                        "title": result.get("titulo", ""),
                        "summary": result.get("summary"),
                        "risk_level": "Unknown",
                        "confidence": 0.3,
                        "method": "error_fallback",
                        "processing_time_ms": 0,
                        "url": result.get("url_html", ""),
                        "identificador": result.get("identificador"),
                        "seccion": result.get("seccion_codigo"),
                        "seccion_nombre": result.get("seccion_nombre"),
                        "error": str(e)
                    }
                    classified_results.append(classified_result)
        
        # Process News results
        if "newsapi" in search_results and search_results["newsapi"].get("articles"):
            for article in search_results["newsapi"]["articles"]:
                try:
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
                        "confidence": classification.get("confidence", 0.5),
                        "method": classification.get("method", "unknown"),
                        "processing_time_ms": classification.get("processing_time_ms", 0),
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "source_name": article.get("source", "Unknown")
                    }
                    classified_results.append(classified_result)
                    
                except Exception as e:
                    classified_result = {
                        "source": "News",
                        "date": article.get("publishedAt"),
                        "title": article.get("title", ""),
                        "summary": article.get("description"),
                        "risk_level": "Unknown",
                        "confidence": 0.3,
                        "method": "error_fallback",
                        "processing_time_ms": 0,
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "source_name": article.get("source", "Unknown"),
                        "error": str(e)
                    }
                    classified_results.append(classified_result)
        
        # Process RSS results
        for agent_name in rss_agents:
            if agent_name in search_results and search_results[agent_name].get("articles"):
                for article in search_results[agent_name]["articles"]:
                    try:
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
                            "confidence": classification.get("confidence", 0.5),
                            "method": classification.get("method", "unknown"),
                            "processing_time_ms": classification.get("processing_time_ms", 0),
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": article.get("source_name", f"RSS-{agent_name.upper()}")
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        classified_result = {
                            "source": f"RSS-{agent_name.upper()}",
                            "date": article.get("publishedAt"),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
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
        
        # STEP 4: RESPONSE PREPARATION
        valid_results = []
        
        # Validate and format dates
        for result in classified_results:
            date_val = result.get("date")
            if date_val:
                try:
                    if isinstance(date_val, str):
                        if "T" in date_val:
                            result["date"] = date_val
                        else:
                            parsed_date = datetime.datetime.strptime(date_val, "%Y-%m-%d")
                            result["date"] = parsed_date.isoformat() + "Z"
                    valid_results.append(result)
                except Exception:
                    result["date_parse_error"] = True
                    valid_results.append(result)
        
        # Sort by date, most recent first
        valid_results.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Calculate total time
        total_time = time.time() - overall_start_time
        
        # Build response with database stats
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
                "search_time_seconds": f"{search_time:.2f}",
                "classification_time_seconds": f"{classification_time:.2f}",
                "database_time_seconds": f"{db_time:.2f}"
            },
            "database_stats": {
                "raw_docs_saved": db_stats["raw_docs_saved"],
                "events_created": db_stats["events_created"],
                "total_processed": db_stats["total_processed"],
                "errors": db_stats["errors"][:5]
            }
        }
        
        return response
        
    except Exception as e:
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
            "error": f"Search failed: {str(e)}",
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
            "database_stats": {
                "raw_docs_saved": 0,
                "events_created": 0,
                "total_processed": 0,
                "errors": [str(e)]
            }
        }
        
        return error_response


@router.get("/search/health")
async def search_health():
    """
    Health check for search system
    """
    try:
        orchestrator = get_search_orchestrator()
        classifier = OptimizedHybridClassifier()
        
        return {
            "status": "healthy",
            "message": "Search system is operational",
            "orchestrator_type": type(orchestrator).__name__,
            "classifier_type": type(classifier).__name__,
            "features": [
                "Multi-source search",
                "Hybrid classification",
                "Rate limit handling",
                "Performance monitoring",
                "Database persistence"
            ],
            "sources_available": [
                "BOE (Spanish Official Gazette)",
                "NewsAPI (International news)",
                "RSS feeds (Spanish news sources)"
            ]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Search system is not operational"
        }


@router.get("/search/database-stats")
async def get_database_stats():
    """
    Get database statistics for search results
    """
    try:
        # Since we're using BigQuery only, return a placeholder response
        return {
            "status": "success",
            "message": "Database statistics retrieved successfully",
            "statistics": {
                "database_type": "BigQuery",
                "total_companies": "N/A - BigQuery",
                "total_assessments": "N/A - BigQuery",
                "total_raw_docs": "N/A - BigQuery",
                "total_events": "N/A - BigQuery"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve database stats: {str(e)}"
        } 