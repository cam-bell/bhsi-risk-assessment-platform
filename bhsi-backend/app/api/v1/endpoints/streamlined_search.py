#!/usr/bin/env python3
"""
STREAMLINED Search API Endpoints - Ultra-fast search with optimized hybrid classification
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import datetime
import time
from sqlalchemy.orm import Session

from app.agents.search.orchestrator_factory import get_search_orchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier
from app.services.database_integration import db_integration
from app.api import deps

router = APIRouter()


# Request/Response Models
class StreamlinedSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True
    include_rss: bool = False  # Include RSS news sources


@router.post("/search")
async def streamlined_search(
    request: StreamlinedSearchRequest,
    db: Session = Depends(deps.get_db)
):
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
    - Database persistence of search results
    
    **Expected Performance:**
    - 90%+ results classified in µ-seconds via keyword gate
    - Only 10% or less require expensive LLM analysis
    - Total response time: 3-10 seconds (vs previous 2+ minutes)
    """
    
    overall_start_time = time.time()
    
    try:
        # Initialize streamlined components using factory
        orchestrator = get_search_orchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Configure which agents to use
        active_agents = []
        if request.include_boe:
            active_agents.append("boe")
        if request.include_news:
            active_agents.append("newsapi")
        # RSS disabled for demo performance
        # if request.include_rss:
        #     # Only include El Pais and Expansion for demo speed
        #     active_agents.extend([
        #         "elpais", 
        #         "expansion"
        #         # "elmundo",  # Disabled for demo
        #         # "abc",      # Disabled for demo
        #         # "lavanguardia", # Disabled for demo
        #         # "elconfidencial", # Disabled for demo
        #         # "eldiario", # Disabled for demo
        #         # "europapress" # Disabled for demo
        #     ])
            
        if not active_agents:
            raise HTTPException(
                status_code=400,
                detail="At least one source (BOE, news, or RSS) must be enabled"
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
        
        # STEP 2: DATABASE INTEGRATION - Save raw results
        db_start_time = time.time()
        db_stats = db_integration.save_search_results(
            db, search_results, request.company_name, request.company_name
        )
        db_time = time.time() - db_start_time
        
        # STEP 3: BULK CLASSIFICATION (optimized hybrid approach)
        classification_start_time = time.time()
        classified_results = []
        
        # Process BOE results
        if "boe" in search_results and search_results["boe"].get("results"):
            for boe_result in search_results["boe"]["results"]:
                try:
                    # Optimized hybrid classification
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
        
        # RSS processing disabled for demo performance
        # # Process RSS results (only El Pais and Expansion for demo)
        # rss_agents = [
        #     "elpais", 
        #     "expansion"
        #     # "elmundo",  # Disabled for demo
        #     # "abc",      # Disabled for demo
        #     # "lavanguardia", # Disabled for demo
        #     # "elconfidencial", # Disabled for demo
        #     # "eldiario", # Disabled for demo
        #     # "europapress" # Disabled for demo
        # ]
        # for agent_name in rss_agents:
        #     if agent_name in search_results and search_results[agent_name].get("articles"):
        #         for article in search_results[agent_name]["articles"]:
        #             try:
        #                 # Optimized hybrid classification
        #                 classification = await classifier.classify_document(
        #                     text=article.get("content", article.get("description", "")),
        #                     title=article.get("title", ""),
        #                     source=f"RSS-{agent_name.upper()}"
        #                 )
        #                 
        #                 classified_result = {
        #                     "source": f"RSS-{agent_name.upper()}",
        #                     "date": article.get("publishedAt"),
        #                     "title": article.get("title", ""),
        #                     "summary": article.get("description"),
        #                     "risk_level": classification.get("label", "Unknown"),
        #                     "confidence": classification.get("confidence", 0.5),
        #                     "method": classification.get("method", "unknown"),
        #                     "processing_time_ms": classification.get("processing_time_ms", 0),
        #                     "url": article.get("url", ""),
        #                     # RSS-specific fields
        #                     "author": article.get("author"),
        #                     "category": article.get("category"),
        #                     "source_name": article.get("source_name", f"RSS-{agent_name.upper()}")
        #                 }
        #                 classified_results.append(classified_result)
        #                 
        #             except Exception as e:
        #                 # Simple fallback
        #                 classified_result = {
        #                     "source": f"RSS-{agent_name.upper()}",
        #                     "date": article.get("publishedAt"),
        #                     "title": article.get("title", ""),
        #                     "summary": article.get("description"),
        #                     "risk_level": "Unknown",
        #                     "confidence": 0.3,
        #                     "method": "error_fallback",
        #                     "processing_time_ms": 0,
        #                     "url": article.get("url", ""),
        #                     "author": article.get("author"),
        #                     "category": article.get("category"),
        #                     "source_name": article.get("source_name", f"RSS-{agent_name.upper()}"),
        #                     "error": str(e)
        #                 }
        #                 classified_results.append(classified_result)
        
        classification_time = time.time() - classification_start_time
        
        # STEP 4: RESPONSE PREPARATION
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
        
        # Calculate total time
        total_time = time.time() - overall_start_time
        
        # Build optimized response with database stats
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
                "rss_results": 0,  # RSS disabled for demo
                "high_risk_results": len([r for r in valid_results if r["risk_level"] == "High-Legal"]),
                "sources_searched": active_agents
            },
            "performance": {
                **classifier.get_performance_stats(),
                "total_time_seconds": f"{total_time:.2f}",
                "search_time_seconds": f"{search_time:.2f}",
                "classification_time_seconds": f"{classification_time:.2f}",
                "database_time_seconds": f"{db_time:.2f}",
                "optimization": "Streamlined search + optimized hybrid classifier"
            },
            "database_stats": {
                "raw_docs_saved": db_stats["raw_docs_saved"],
                "events_created": db_stats["events_created"],
                "total_processed": db_stats["total_processed"],
                "errors": db_stats["errors"][:5]  # Limit error list
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
async def streamlined_search_health():
    """
    Health check for streamlined search system
    """
    try:
        orchestrator = get_search_orchestrator()
        classifier = OptimizedHybridClassifier()
        
        return {
            "status": "healthy",
            "message": "Streamlined search system is operational",
            "orchestrator_type": type(orchestrator).__name__,
            "classifier_type": type(classifier).__name__,
            "features": [
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
            ]
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
    Get detailed performance statistics for the OPTIMIZED hybrid classifier
    """
    try:
        classifier = OptimizedHybridClassifier()
        stats = classifier.get_performance_stats()
        
        return {
            "status": "success", 
            "message": "Performance statistics for OPTIMIZED STREAMLINED search system",
            "architecture": {
                "search_stage": "Streamlined agents - Fast data fetching only",
                "classification_stage_1": "Optimized keyword gate (µ-seconds) - 90%+ efficiency",
                "classification_stage_2": "Smart LLM routing (only for truly ambiguous cases)",
                "optimization": "Removed classification loops + optimized patterns"
            },
            "statistics": stats,
            "improvements": {
                "search_optimization": "No classification during search loops",
                "keyword_patterns": "Enhanced patterns for Spanish D&O risks",
                "smart_routing": "Only legal-looking ambiguous content sent to LLM",
                "expected_performance": "90%+ improvement over previous system"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve performance stats: {str(e)}"
        }


@router.get("/search/database-stats")
async def get_database_stats(db: Session = Depends(deps.get_db)):
    """
    Get database statistics for search results
    """
    try:
        stats = db_integration.get_database_stats(db)
        
        return {
            "status": "success",
            "message": "Database statistics retrieved successfully",
            "statistics": stats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not retrieve database stats: {str(e)}"
        } 