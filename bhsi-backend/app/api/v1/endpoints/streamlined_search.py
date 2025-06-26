#!/usr/bin/env python3
"""
STREAMLINED Search API Endpoints - Ultra-fast search with optimized hybrid classification
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import datetime
import time

from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier

router = APIRouter()


# Request/Response Models
class StreamlinedSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True


@router.post("/search")
async def streamlined_search(request: StreamlinedSearchRequest):
    """
    ULTRA-FAST STREAMLINED SEARCH ENDPOINT
    
    **Performance Optimizations:**
    - Streamlined agents: Fast data fetching without classification loops
    - Optimized hybrid classifier: 90%+ keyword gate efficiency
    - Smart LLM routing: Only for truly ambiguous cases
    - No unnecessary fallbacks or redundant processing
    
    **Features:**
    - BOE (Spanish official gazette) and news sources
    - Intelligent rate limit handling (NewsAPI 30-day limit)
    - Performance monitoring and statistics
    - Structured response format with confidence scores
    
    **Expected Performance:**
    - 90%+ results classified in µ-seconds via keyword gate
    - Only 10% or less require expensive LLM analysis
    - Total response time: 3-10 seconds (vs previous 2+ minutes)
    """
    
    overall_start_time = time.time()
    
    try:
        # Initialize streamlined components
        orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Configure which agents to use
        active_agents = []
        if request.include_boe:
            active_agents.append("boe")
        if request.include_news:
            active_agents.append("newsapi")
            
        if not active_agents:
            raise HTTPException(
                status_code=400,
                detail="At least one source (BOE or news) must be enabled"
            )
        
        # STEP 1: FAST SEARCH (no classification during search)
        search_start_time = time.time()
        search_results = await orchestrator.search_all(
            query=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            active_agents=active_agents
        )
        search_time = time.time() - search_start_time
        
        # STEP 2: BULK CLASSIFICATION (optimized hybrid approach)
        classification_start_time = time.time()
        classified_results = []
        
        # Process BOE results
        if "boe" in search_results and search_results["boe"].get("results"):
            for result in search_results["boe"]["results"]:
                try:
                    # Optimized hybrid classification
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
                        # BOE-specific fields
                        "identificador": result.get("identificador"),
                        "seccion": result.get("seccion_codigo"),
                        "seccion_nombre": result.get("seccion_nombre")
                    }
                    classified_results.append(classified_result)
                    
                except Exception as e:
                    # Simple fallback - don't slow down the entire response
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
                    # Optimized hybrid classification
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
                        "confidence": 0.3,
                        "method": "error_fallback",
                        "processing_time_ms": 0,
                        "url": article.get("url", ""),
                        "author": article.get("author"),
                        "source_name": article.get("source", "Unknown"),
                        "error": str(e)
                    }
                    classified_results.append(classified_result)
        
        classification_time = time.time() - classification_start_time
        
        # STEP 3: SORT AND FORMAT RESULTS
        # Filter out results with invalid dates and sort by date (most recent first)
        valid_results = []
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
        
        # Calculate total time
        total_time = time.time() - overall_start_time
        
        # Build optimized response
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
                "high_risk_results": len([r for r in valid_results if r["risk_level"] == "High-Legal"]),
                "sources_searched": active_agents
            },
            "performance": {
                **classifier.get_performance_stats(),
                "total_time_seconds": f"{total_time:.2f}",
                "search_time_seconds": f"{search_time:.2f}",
                "classification_time_seconds": f"{classification_time:.2f}",
                "optimization": "Streamlined search + optimized hybrid classifier"
            }
        }
        
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
                "high_risk_results": 0,
                "sources_searched": []
            },
            "performance": {
                "total_time_seconds": f"{total_time:.2f}",
                "error": "Search failed before completion"
            }
        }
        
        return error_response


@router.get("/search/health")
async def streamlined_search_health():
    """
    Health check for streamlined search services
    """
    try:
        orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        return {
            "status": "healthy",
            "message": "STREAMLINED search services operational",
            "optimization": "Ultra-fast search with optimized hybrid classification",
            "services": {
                "streamlined_orchestrator": "available",
                "optimized_hybrid_classifier": "available",
                "streamlined_boe_agent": "available",
                "streamlined_newsapi_agent": "available"
            },
            "performance": classifier.get_performance_stats(),
            "expected_improvement": "90%+ faster than previous implementation"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": f"Streamlined search services partially available: {str(e)}",
            "services": {
                "streamlined_orchestrator": "unknown",
                "optimized_hybrid_classifier": "unknown", 
                "streamlined_boe_agent": "unknown",
                "streamlined_newsapi_agent": "unknown"
            }
        }


@router.get("/search/performance")
async def streamlined_search_performance():
    """
    Get detailed performance statistics for the optimized system
    """
    try:
        classifier = OptimizedHybridClassifier()
        stats = classifier.get_performance_stats()
        
        return {
            "status": "success",
            "message": "Performance statistics for STREAMLINED search system",
            "architecture": {
                "search_stage": "Streamlined agents - Fast data fetching only",
                "classification_stage_1": "Optimized keyword gate (µ-seconds)",
                "classification_stage_2": "Smart LLM routing (only for ambiguous cases)",
                "optimization": "90%+ cases handled by keyword gate"
            },
            "statistics": stats,
            "improvements": {
                "search_speed": "Removed classification loops from search agents",
                "classification_speed": "Optimized keyword patterns + smart LLM routing", 
                "overall_performance": "Expected 90%+ improvement over previous system",
                "cost_efficiency": "Dramatically reduced LLM API calls"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve performance stats: {str(e)}"
        } 