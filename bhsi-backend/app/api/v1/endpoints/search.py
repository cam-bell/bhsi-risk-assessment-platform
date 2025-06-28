#!/usr/bin/env python3
"""
Search API Endpoints - Unified search across BOE and news sources
<<<<<<< HEAD

⚠️  DEPRECATED: This endpoint has been replaced by streamlined_search.py
    Use the streamlined search endpoint for better performance and features.
    This file is kept for reference and backward compatibility only.
=======
>>>>>>> origin/integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import datetime

from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier

router = APIRouter()


# Request/Response Models
class UnifiedSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True
<<<<<<< HEAD
    include_rss: bool = True  # Include RSS sources (El País, Expansión, El Mundo)
=======
>>>>>>> origin/integration


@router.post("/search")
async def unified_search(request: UnifiedSearchRequest):
    """
    Unified search endpoint with HYBRID PERFORMANCE OPTIMIZATION
    
    **Features:**
<<<<<<< HEAD
    - Searches BOE, NewsAPI, and RSS sources (El País, Expansión, El Mundo)
=======
    - Searches both BOE (Spanish official gazette) and news sources
>>>>>>> origin/integration
    - HYBRID CLASSIFICATION: Fast keyword gate (µ-seconds) + Smart LLM fallback
    - 80-90% performance improvement through intelligent keyword filtering
    - Intelligent rate limit handling (NewsAPI limited to 30 days)
    - Structured response format with confidence scores and performance stats
    
    **Parameters:**
    - **company_name**: Name of the company to search for
    - **start_date**: Start date in YYYY-MM-DD format (optional)
    - **end_date**: End date in YYYY-MM-DD format (optional)
    - **days_back**: Search last N days if dates not specified (default: 7)
    - **include_boe**: Whether to include BOE results (default: True)
<<<<<<< HEAD
    - **include_news**: Whether to include NewsAPI results (default: True)
    - **include_rss**: Whether to include RSS sources (default: True)
    
    **Returns:**
    Combined results from all sources with Cloud Gemini risk assessment
=======
    - **include_news**: Whether to include news results (default: True)
    
    **Returns:**
    Combined results from both sources with Cloud Gemini risk assessment
>>>>>>> origin/integration
    """
    try:
        orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Configure which agents to use
        active_agents = []
        if request.include_boe:
            active_agents.append("boe")
        if request.include_news:
            active_agents.append("newsapi")
<<<<<<< HEAD
        if request.include_rss:
            active_agents.extend([
                "elpais", "expansion", "elmundo",
                "abc", "lavanguardia", "elconfidencial"
            ])
=======
>>>>>>> origin/integration
            
        if not active_agents:
            raise HTTPException(
                status_code=400,
<<<<<<< HEAD
                detail="At least one source must be enabled"
=======
                detail="At least one source (BOE or news) must be enabled"
>>>>>>> origin/integration
            )
        
        # Perform search across selected sources
        search_results = await orchestrator.search_all(
            query=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            active_agents=active_agents
        )
        
        # Process and classify results
        classified_results = []
        
        for source_name, source_data in search_results.items():
            if source_name == "boe" and source_data.get("results"):
                for result in source_data["results"]:
                    try:
                        # Classify with Cloud Gemini
                        classification = await classifier.classify_document(
                            text=result.get("text", result.get("summary", "")),
                            title=result.get("title", ""),
                            source="BOE",
                            section=result.get("section", "")
                        )
                        
                        classified_result = {
                            "source": "BOE",
                            "date": result.get("fechaPublicacion", result.get("date")),
                            "title": result.get("titulo", result.get("title", "")),
                            "summary": result.get("summary"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": result.get("url_html", result.get("url", "")),
                            # BOE-specific fields
                            "identificador": result.get("identificador"),
                            "seccion": result.get("seccion_codigo"),
                            "seccion_nombre": result.get("seccion_nombre")
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        print(f"Error classifying BOE result: {e}")
                        # Fallback classification
                        classified_result = {
                            "source": "BOE",
                            "date": result.get("fechaPublicacion", result.get("date")),
                            "title": result.get("titulo", result.get("title", "")),
                            "summary": result.get("summary"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": result.get("url_html", result.get("url", "")),
                            "identificador": result.get("identificador"),
                            "seccion": result.get("seccion_codigo"),
                            "seccion_nombre": result.get("seccion_nombre")
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "newsapi" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        # Classify with Cloud Gemini
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="News"
                        )
                        
                        classified_result = {
                            "source": "News",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            # News-specific fields
                            "author": article.get("author"),
                            "source_name": article.get("source", {}).get("name") if isinstance(article.get("source"), dict) else article.get("source")
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        print(f"Error classifying news result: {e}")
                        # Fallback classification
                        classified_result = {
                            "source": "News",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "source_name": article.get("source", {}).get("name") if isinstance(article.get("source"), dict) else article.get("source")
                        }
                        classified_results.append(classified_result)
<<<<<<< HEAD
            
            elif source_name == "elpais" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        # Classify with Cloud Gemini
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="El País"
                        )
                        
                        classified_result = {
                            "source": "El País",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            # El País-specific fields
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El País"
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        print(f"Error classifying El País result: {e}")
                        # Fallback classification
                        classified_result = {
                            "source": "El País",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El País"
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "expansion" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        # Classify with Cloud Gemini
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="Expansión"
                        )
                        
                        classified_result = {
                            "source": "Expansión",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            # Expansión-specific fields
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "Expansión"
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        print(f"Error classifying Expansión result: {e}")
                        # Fallback classification
                        classified_result = {
                            "source": "Expansión",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "Expansión"
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "elmundo" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        # Classify with Cloud Gemini
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="El Mundo"
                        )
                        
                        classified_result = {
                            "source": "El Mundo",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            # El Mundo-specific fields
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El Mundo"
                        }
                        classified_results.append(classified_result)
                        
                    except Exception as e:
                        print(f"Error classifying El Mundo result: {e}")
                        # Fallback classification
                        classified_result = {
                            "source": "El Mundo",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El Mundo"
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "abc" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="ABC"
                        )
                        classified_result = {
                            "source": "ABC",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "ABC"
                        }
                        classified_results.append(classified_result)
                    except Exception as e:
                        print(f"Error classifying ABC result: {e}")
                        classified_result = {
                            "source": "ABC",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "ABC"
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "lavanguardia" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="La Vanguardia"
                        )
                        classified_result = {
                            "source": "La Vanguardia",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "La Vanguardia"
                        }
                        classified_results.append(classified_result)
                    except Exception as e:
                        print(f"Error classifying La Vanguardia result: {e}")
                        classified_result = {
                            "source": "La Vanguardia",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "La Vanguardia"
                        }
                        classified_results.append(classified_result)
            
            elif source_name == "elconfidencial" and source_data.get("articles"):
                for article in source_data["articles"]:
                    try:
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source="El Confidencial"
                        )
                        classified_result = {
                            "source": "El Confidencial",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": classification.get("label", "Unknown"),
                            "confidence": classification.get("confidence", 0.5),
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El Confidencial"
                        }
                        classified_results.append(classified_result)
                    except Exception as e:
                        print(f"Error classifying El Confidencial result: {e}")
                        classified_result = {
                            "source": "El Confidencial",
                            "date": article.get("publishedAt", article.get("published_at")),
                            "title": article.get("title", ""),
                            "summary": article.get("description"),
                            "risk_level": "Unknown",
                            "confidence": 0.3,
                            "url": article.get("url", ""),
                            "author": article.get("author"),
                            "category": article.get("category"),
                            "source_name": "El Confidencial"
                        }
                        classified_results.append(classified_result)
=======
>>>>>>> origin/integration
        
        # Filter out results with None/invalid dates and sort by date (most recent first)
        valid_results = []
        for result in classified_results:
            date_val = result.get("date")
            if date_val:
                # Ensure consistent ISO format
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
                except Exception as e:
                    print(f"Error parsing date {date_val}: {e}")
                    continue
        
        # Sort by date, most recent first
        valid_results.sort(key=lambda x: x["date"], reverse=True)
        
        # Build response according to exact specifications
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
<<<<<<< HEAD
                "elpais_results": len([r for r in valid_results if r["source"] == "El País"]),
                "expansion_results": len([r for r in valid_results if r["source"] == "Expansión"]),
                "elmundo_results": len([r for r in valid_results if r["source"] == "El Mundo"]),
                "abc_results": len([r for r in valid_results if r["source"] == "ABC"]),
                "lavanguardia_results": len([r for r in valid_results if r["source"] == "La Vanguardia"]),
                "elconfidencial_results": len([r for r in valid_results if r["source"] == "El Confidencial"]),
=======
>>>>>>> origin/integration
                "high_risk_results": len([r for r in valid_results if r["risk_level"] == "High-Legal"]),
                "sources_searched": active_agents
            },
            "performance": classifier.get_performance_stats()
        }
        
        return response
        
    except Exception as e:
        # Return error response with partial results if possible
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
<<<<<<< HEAD
                "elpais_results": 0,
                "expansion_results": 0,
                "elmundo_results": 0,
                "abc_results": 0,
                "lavanguardia_results": 0,
                "elconfidencial_results": 0,
=======
>>>>>>> origin/integration
                "high_risk_results": 0,
                "sources_searched": []
            }
        }
        
        return error_response


@router.get("/search/health")
async def search_health():
    """
    Health check for search services
    """
    try:
        orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        return {
            "status": "healthy",
            "message": "Search services operational (HYBRID PERFORMANCE MODE)",
            "services": {
                "orchestrator": "available",
                "hybrid_classifier": "available",
                "boe_agent": "available",
<<<<<<< HEAD
                "newsapi_agent": "available",
                "elpais_agent": "available",
                "expansion_agent": "available",
                "elmundo_agent": "available",
                "abc_agent": "available",
                "lavanguardia_agent": "available",
                "elconfidencial_agent": "available"
=======
                "newsapi_agent": "available"
>>>>>>> origin/integration
            },
            "performance": classifier.get_performance_stats()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": f"Search services partially available: {str(e)}",
            "services": {
                "orchestrator": "unknown",
                "hybrid_classifier": "unknown",
                "boe_agent": "unknown", 
<<<<<<< HEAD
                "newsapi_agent": "unknown",
                "elpais_agent": "unknown",
                "expansion_agent": "unknown",
                "elmundo_agent": "unknown",
                "abc_agent": "unknown",
                "lavanguardia_agent": "unknown",
                "elconfidencial_agent": "unknown"
=======
                "newsapi_agent": "unknown"
>>>>>>> origin/integration
            }
        }


@router.get("/search/performance")
async def search_performance():
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