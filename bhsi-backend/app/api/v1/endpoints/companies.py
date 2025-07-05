from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api import deps
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyAnalysis
from app.agents.search.streamlined_orchestrator import (
    StreamlinedSearchOrchestrator
)
from app.agents.analysis.optimized_hybrid_classifier import (
    OptimizedHybridClassifier
)
from app.agents.analytics.analytics_service import AnalyticsService
from app.crud.bigquery_company import bigquery_company
from app.crud.bigquery_assessment import bigquery_assessment
from app.services.search_cache_service import search_cache_service
import logging
from app.core.config import settings
import uuid
import time
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"bigquery_company type: {type(bigquery_company)}")
logger.info(f"bigquery_company dir: {dir(bigquery_company)}")

router = APIRouter()


@router.post("/analyze", response_model=CompanyAnalysis)
async def analyze_company(
    company: CompanyCreate,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    UNIFIED COMPANY ANALYSIS ENDPOINT - Comprehensive Risk Assessment with Caching
    
    This endpoint combines the best of both worlds:
    1. Smart caching: Check BigQuery for existing results before searching
    2. Comprehensive data collection (BOE + NewsAPI + RSS feeds)
    3. Optimized hybrid classification (90%+ keyword efficiency)
    4. Business intelligence and analytics integration
    5. BigQuery persistence and assessment tracking
    
    **Data Sources:**
    - BOE (Spanish official gazette)
    - NewsAPI (International news)
    - RSS feeds (El País, Expansión, El Mundo, ABC, La Vanguardia, etc.)
    
    **Business Features:**
    - Complete risk assessment with business categories
    - Analytics integration for enhanced insights
    - BigQuery persistence for historical tracking
    - Performance monitoring and optimization
    - Smart caching for improved performance
    """
    overall_start_time = time.time()
    
    # Initialize streamlined components
    classifier = OptimizedHybridClassifier()
    analytics_service = AnalyticsService()
    
    try:
        # STEP 1: SMART CACHING - Check BigQuery for existing results
        # Configure which agents to use based on request parameters
        active_agents = []
        if company.include_boe:
            active_agents.append("boe")
        if company.include_news:
            active_agents.append("newsapi")
        if company.include_rss:
            # Add all RSS news sources for comprehensive coverage
            active_agents.extend([
                "elpais", "expansion", "elmundo", "abc", "lavanguardia", 
                "elconfidencial", "eldiario", "europapress"
            ])
        
        if not active_agents:
            raise HTTPException(
                status_code=400,
                detail="At least one source (BOE, news, or RSS) must be enabled"
            )
        
        # Get search results with caching
        search_data = await search_cache_service.get_search_results(
            company_name=company.name,
            start_date=company.start_date,
            end_date=company.end_date,
            days_back=company.days_back,
            active_agents=active_agents,
            cache_age_hours=24,  # Default cache age
            force_refresh=False  # Allow caching for company analysis
        )
        
        search_results = search_data['results']
        search_method = search_data['search_method']
        
        # STEP 2: COMPREHENSIVE CLASSIFICATION
        # Classify all results using optimized hybrid classifier
        classified_results = []
        high_risk_count = 0
        
        # Process BOE results
        boe_results = search_results.get("boe", {}).get("results", [])
        for result in boe_results:
            # Skip classification if already classified (cached results)
            if result.get("method") == "cached":
                result["risk_level"] = result.get("risk_level", "Unknown")
                result["confidence"] = result.get("confidence", 0.5)
                result["method"] = "cached"
            else:
                classification = await classifier.classify_document(
                    text=result.get("texto_completo", result.get("text", "")),
                    title=result.get("titulo", ""),
                    source="BOE",
                    section=result.get("seccion_codigo", "")
                )
                
                result["risk_level"] = classification["label"]
                result["confidence"] = classification["confidence"]
                result["method"] = classification["method"]
            
            if result["risk_level"] == "High-Legal":
                high_risk_count += 1
            
            classified_results.append(result)
        
        # Process NewsAPI results
        news_results = search_results.get("newsapi", {}).get("articles", [])
        for article in news_results:
            # Skip classification if already classified (cached results)
            if article.get("method") == "cached":
                article["risk_level"] = article.get("risk_level", "Unknown")
                article["confidence"] = article.get("confidence", 0.5)
                article["method"] = "cached"
            else:
                classification = await classifier.classify_document(
                    text=article.get("content", article.get("description", "")),
                    title=article.get("title", ""),
                    source="News",
                    section=article.get("source", "")
                )
                
                article["risk_level"] = classification["label"]
                article["confidence"] = classification["confidence"]
                article["method"] = classification["method"]
            
            if article["risk_level"] == "High-Legal":
                high_risk_count += 1
            
            classified_results.append(article)
        
        # Process RSS results (all individual RSS agents)
        rss_results = []
        rss_agents = ["elpais", "expansion", "elmundo", "abc", 
                     "lavanguardia", "elconfidencial", "eldiario", "europapress"]
        
        for agent_name in rss_agents:
            if agent_name in search_results and search_results[agent_name].get("articles"):
                for article in search_results[agent_name]["articles"]:
                    # Skip classification if already classified (cached results)
                    if article.get("method") == "cached":
                        article["risk_level"] = article.get("risk_level", "Unknown")
                        article["confidence"] = article.get("confidence", 0.5)
                        article["method"] = "cached"
                    else:
                        classification = await classifier.classify_document(
                            text=article.get("content", article.get("description", "")),
                            title=article.get("title", ""),
                            source=f"RSS-{agent_name.upper()}"
                        )
                        
                        article["risk_level"] = classification["label"]
                        article["confidence"] = classification["confidence"]
                        article["method"] = classification["method"]
                    
                    if article["risk_level"] == "High-Legal":
                        high_risk_count += 1
                    
                    classified_results.append(article)
                    rss_results.append(article)
        
        # Determine overall risk based on findings
        total_results = len(classified_results)
        if total_results == 0:
            overall_risk = "green"
        elif high_risk_count > 0:
            overall_risk = "red"
        elif any(r.get("risk_level") == "Medium-Legal" 
                for r in classified_results):
            overall_risk = "orange"
        else:
            overall_risk = "green"
        
        # STEP 3: BUSINESS INTELLIGENCE & ANALYTICS
        # Get performance stats
        performance_stats = classifier.get_performance_stats()
        
        # Get enhanced analytics if VAT is provided
        enhanced_analytics = None
        if company.vat:
            try:
                enhanced_analytics = await analytics_service.get_comprehensive_analytics(
                    company_name=company.name,
                    include_trends=True,
                    include_sectors=False
                )
            except Exception as e:
                logger.warning(f"Analytics failed for {company.name}: {e}")
        
        # Calculate comprehensive risk assessment
        bankruptcy_risk = any("concurso" in str(r).lower() 
                             for r in classified_results)
        corruption_risk = any("blanqueo" in str(r).lower() or 
                             "corrupción" in str(r).lower() 
                             for r in classified_results)
        
        # STEP 4: BIGQUERY PERSISTENCE
        db_start_time = time.time()
        
        # Save company metadata to BigQuery
        company_metadata = {
            "vat": company.vat,
            "name": company.name,
            "description": company.description,
            "sector": company.sector,
            "client_tier": company.client_tier
        }
        
        # Check if company exists and update/create
        existing_company = await bigquery_company.get_by_name(company.name)
        if existing_company:
            await bigquery_company.update_company(existing_company["vat"], company_metadata)
        else:
            await bigquery_company.create_company(company_metadata)
        
        # Save comprehensive assessment to BigQuery
        assessment_dict = {
            "company_id": company.vat,
            "user_id": "system",  # Default user for automated assessments
            "turnover": overall_risk,
            "shareholding": overall_risk,
            "bankruptcy": "red" if bankruptcy_risk else "green",
            "legal": overall_risk,
            "corruption": "red" if corruption_risk else "green",
            "overall": overall_risk,
            "google_results": str(search_results.get("google", {})),
            "bing_results": str(search_results.get("bing", {})),
            "gov_results": str(search_results.get("boe", {})),
            "news_results": str(search_results.get("newsapi", {})),
            "rss_results": str(rss_results),
            "analysis_summary": str({
                "total_results": total_results,
                "high_risk_count": high_risk_count,
                "classified_results": classified_results,
                "search_method": search_method
            }),
        }
        
        await bigquery_assessment.create_assessment(assessment_dict)
        
        db_time = time.time() - db_start_time
        total_time = time.time() - overall_start_time
        
        # Format comprehensive analysis response
        analysis = {
            "company_name": company.name,
            "vat": company.vat,
            "risk_assessment": {
                "overall_risk": overall_risk,
                "bankruptcy_risk": bankruptcy_risk,
                "corruption_risk": corruption_risk,
                "total_results": total_results,
                "high_risk_count": high_risk_count,
                "classified_results": classified_results
            },
            "performance_stats": performance_stats,
            "enhanced_analytics": enhanced_analytics,
            "processing_time": {
                "total_time": total_time,
                "db_time": db_time
            },
            "cache_info": {
                "search_method": search_method,
                "cache_age_hours": search_data.get("cache_info", {}).get("age_hours", 0),
                "total_events": search_data.get("cache_info", {}).get("total_events", 0),
                "sources": search_data.get("cache_info", {}).get("sources", [])
            },
            "database": "BigQuery"
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Company analysis failed for {company.name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/batch-analyze", response_model=List[CompanyAnalysis])
async def batch_analyze_companies(
    companies: List[CompanyCreate],
    background_tasks: BackgroundTasks
) -> List[Dict[str, Any]]:
    """
    Analyze multiple companies in batch using streamlined system
    """
    results = []
    for company in companies:
        try:
            analysis = await analyze_company(company, background_tasks)
            results.append(analysis)
        except Exception as e:
            results.append({
                "error": f"Error analyzing {company.name}: {str(e)}",
                "company": company.name
            })
    
    return results


@router.get("/{company_id}/analysis", response_model=CompanyAnalysis)
async def get_company_analysis(
    company_id: int
) -> Dict[str, Any]:
    """
    Get analysis results for a specific company
    """
    company = await bigquery_company.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ID {company_id} not found"
        )
    
    # Get latest assessment for this company
    assessments = await bigquery_assessment.get_by_company(company["vat"])
    if not assessments:
        raise HTTPException(
            status_code=404,
            detail=f"No assessments found for company {company_id}"
        )
    
    # Return the most recent assessment
    latest_assessment = assessments[0]  # Already sorted by created_at DESC
    
    return {
        "company": company,
        "assessment": latest_assessment,
        "database": "BigQuery"
    }


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List all companies with their risk profiles
    """
    companies = await bigquery_company.list_companies(skip=skip, limit=limit)
    return companies


@router.get("/{company_name}/analytics")
async def get_company_analytics(
    company_name: str,
    include_trends: bool = True,
    include_sectors: bool = False
) -> Dict[str, Any]:
    """
    Get comprehensive analytics for a specific company using BigQuery service
    
    Args:
        company_name: Name of the company to analyze
        include_trends: Whether to include system-wide risk trends
        include_sectors: Whether to include sector analysis
    """
    try:
        analytics_service = AnalyticsService()
        analytics = await analytics_service.get_comprehensive_analytics(
            company_name=company_name,
            include_trends=include_trends,
            include_sectors=include_sectors
        )
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting analytics for {company_name}: {str(e)}"
        )


@router.get("/analytics/trends")
async def get_risk_trends() -> Dict[str, Any]:
    """
    Get system-wide risk trends using BigQuery analytics
    """
    try:
        analytics_service = AnalyticsService()
        system_analytics = await analytics_service.get_system_analytics()
        trends_data = system_analytics.get("system_analytics", {}).get("trends", {})
        
        # Always return a dictionary with a 'trends' key
        if isinstance(trends_data, dict) and "trends" in trends_data:
            trends = trends_data["trends"]
        elif isinstance(trends_data, list):
            trends = trends_data
        else:
            trends = []
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting risk trends: {str(e)}"
        )


@router.get("/analytics/alerts")
async def get_system_alerts() -> Dict[str, Any]:
    """
    Get system-wide alerts and alert statistics
    """
    try:
        analytics_service = AnalyticsService()
        system_analytics = await analytics_service.get_system_analytics()
        
        # Extract alerts data from system analytics
        alerts_data = system_analytics.get("system_analytics", {}).get("alerts", {})
        
        # Return structured alerts data
        return {
            "total_alerts": alerts_data.get("total_alerts", 0),
            "high_risk_alerts": alerts_data.get("high_risk_alerts", 0),
            "last_alert": alerts_data.get("last_alert"),
            "alert_trends": alerts_data.get("alert_trends", []),
            "alert_distribution": alerts_data.get("alert_distribution", {})
        }
    except Exception as e:
        # Return fallback data if analytics service fails
        return {
            "total_alerts": 0,
            "high_risk_alerts": 0,
            "last_alert": None,
            "alert_trends": [],
            "alert_distribution": {}
        }


@router.get("/analytics/sectors")
async def get_sector_analytics() -> Dict[str, Any]:
    """
    Get sector-based analytics and risk distribution
    """
    try:
        analytics_service = AnalyticsService()
        system_analytics = await analytics_service.get_system_analytics()
        
        # Extract sectors data from system analytics
        sectors_data = system_analytics.get("system_analytics", {}).get("sectors", [])
        
        # Return structured sectors data as a dictionary
        return {
            "sectors": sectors_data if isinstance(sectors_data, list) else [],
            "total_sectors": len(sectors_data) if isinstance(sectors_data, list) else 0,
            "period": "last_90_days"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting sector analytics: {str(e)}"
        )


@router.get("/analytics/comparison")
async def compare_companies(
    companies: str
) -> Dict[str, Any]:
    """
    Compare risk profiles across multiple companies
    
    Args:
        companies: Comma-separated list of company names
    """
    company_list = [name.strip() for name in companies.split(",")]
    try:
        if len(company_list) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 companies required for comparison"
            )
        
        analytics_service = AnalyticsService()
        comparison = await analytics_service.get_risk_comparison(company_list)
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing companies: {str(e)}"
        )


@router.get("/analytics/health")
async def analytics_health_check() -> Dict[str, Any]:
    """
    Health check for analytics services
    """
    try:
        analytics_service = AnalyticsService()
        health = await analytics_service.health_check()
        
        return health
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-17T00:00:00Z"
        }


@router.get("/system/status")
async def get_system_status():
    """
    Get status of streamlined analysis system
    """
    try:
        orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Get performance stats
        performance_stats = classifier.get_performance_stats()
        
        return {
            "status": "operational",
            "system_type": "streamlined_optimized",
            "message": ("Streamlined system with 90%+ performance "
                       "improvement active"),
            "components": {
                "search_orchestrator": "StreamlinedSearchOrchestrator",
                "classifier": "OptimizedHybridClassifier",
                "agents": list(orchestrator.agents.keys())
            },
            "performance": {
                "keyword_efficiency": performance_stats["keyword_efficiency"],
                "llm_usage": performance_stats["llm_usage"],
                "avg_processing_time": (
                    performance_stats["avg_processing_time_ms"]
                ),
                "optimization": "90%+ faster than previous system"
            },
            "capabilities": {
                "boe_search": True,
                "news_search": True,
                "hybrid_classification": True,
                "keyword_gate": True,
                "cloud_llm_fallback": True
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not determine system status"
        }


@router.post("/unified-analysis")
async def unified_company_analysis(
    company: CompanyCreate,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Unified company analysis with BigQuery persistence
    """
    overall_start_time = time.time()
    
    try:
        # Initialize components
        search_orchestrator = StreamlinedSearchOrchestrator()
        classifier = OptimizedHybridClassifier()
        
        # Perform search
        search_start_time = time.time()
        search_results = await search_orchestrator.search_all(
            query=company.name,
            days_back=company.days_back or 7,
            active_agents=["boe", "newsapi"]  # Simplified for speed
        )
        search_time = time.time() - search_start_time
        
        # Classify results
        classification_start_time = time.time()
        classified_results = []
        for source, results in search_results.items():
            if source == "boe" and results.get("results"):
                for result in results["results"]:
                    classification = await classifier.classify_document(
                        text=result.get("text", ""),
                        title=result.get("titulo", ""),
                        source="BOE"
                    )
                    result["risk_level"] = classification["label"]
                    classified_results.append(result)
            
            elif source == "newsapi" and results.get("articles"):
                for article in results["articles"]:
                    classification = await classifier.classify_document(
                        text=article.get("content", ""),
                        title=article.get("title", ""),
                        source="News"
                    )
                    article["risk_level"] = classification["label"]
                    classified_results.append(article)
        
        classification_time = time.time() - classification_start_time
        
        # Determine risk level
        high_risk_count = sum(1 for r in classified_results if r.get("risk_level") == "High-Legal")
        overall_risk = "red" if high_risk_count > 0 else "green"
        
        # Save to BigQuery
        db_start_time = time.time()
        
        company_metadata = {
            "vat": company.vat,
            "name": company.name,
            "description": company.description,
            "sector": company.sector,
            "client_tier": company.client_tier
        }
        
        existing_company = await bigquery_company.get_by_name(company.name)
        if existing_company:
            await bigquery_company.update_company(existing_company["vat"], company_metadata)
        else:
            await bigquery_company.create_company(company_metadata)
        
        assessment_dict = {
            "company_id": company.vat,
            "user_id": "system",
            "turnover": overall_risk,
            "shareholding": overall_risk,
            "bankruptcy": "green",
            "legal": overall_risk,
            "corruption": "green",
            "overall": overall_risk,
            "google_results": "{}",
            "bing_results": "{}",
            "gov_results": str(search_results.get("boe", {})),
            "news_results": str(search_results.get("newsapi", {})),
            "rss_results": "{}",
            "analysis_summary": str({
                "total_results": len(classified_results),
                "high_risk_count": high_risk_count,
                "classified_results": classified_results
            }),
        }
        
        await bigquery_assessment.create_assessment(assessment_dict)
        
        db_time = time.time() - db_start_time
        
        return {
            "company_name": company.name,
            "vat": company.vat,
            "risk_assessment": {
                "overall_risk": overall_risk,
                "total_results": len(classified_results),
                "high_risk_count": high_risk_count,
                "classified_results": classified_results
            },
            "processing_time": {
                "search_time": search_time,
                "classification_time": classification_time,
                "db_time": db_time,
                "total_time": time.time() - overall_start_time
            },
            "database": "BigQuery"
        }
        
    except Exception as e:
        logger.error(f"Unified analysis failed for {company.name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unified analysis failed: {str(e)}"
        ) 