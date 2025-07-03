#!/usr/bin/env python3
"""
BigQuery Assessment Endpoints - FastAPI routes for D&O risk assessment with BigQuery storage
Demonstrates non-blocking BigQuery integration with background processing
"""

import logging
import uuid
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.bigquery_client_async import get_bigquery_client
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier
from app.agents.analytics.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter()


class CompanyAssessmentRequest(BaseModel):
    """Request model for company risk assessment"""
    company_name: str = Field(..., description="Company name to assess")
    company_vat: Optional[str] = Field(None, description="Company VAT number")
    user_id: str = Field(..., description="User ID performing assessment")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    days_back: int = Field(7, description="Days to look back if no date range")
    include_boe: bool = Field(True, description="Include BOE search")
    include_news: bool = Field(True, description="Include news search")
    include_rss: bool = Field(True, description="Include RSS feeds")
    include_financial: bool = Field(False, description="Include financial data")
    save_to_bigquery: bool = Field(True, description="Save results to BigQuery")


class CompanyAssessmentResponse(BaseModel):
    """Response model for company risk assessment"""
    assessment_id: str
    company_name: str
    company_vat: Optional[str]
    overall_risk: str
    risk_breakdown: Dict[str, str]
    financial_metrics: Optional[Dict[str, Any]]
    search_results: Dict[str, Any]
    analysis_summary: str
    key_findings: List[str]
    recommendations: List[str]
    processing_stats: Dict[str, Any]
    bigquery_status: Dict[str, Any]
    created_at: str


class BatchAssessmentRequest(BaseModel):
    """Request model for batch company assessment"""
    companies: List[Dict[str, str]] = Field(..., description="List of companies")
    user_id: str = Field(..., description="User ID performing assessment")
    assessment_config: Dict[str, Any] = Field(default_factory=dict)


class BatchAssessmentResponse(BaseModel):
    """Response model for batch assessment"""
    batch_id: str
    total_companies: int
    assessments: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
    bigquery_status: Dict[str, Any]


async def _perform_risk_assessment(
    company_name: str,
    company_vat: Optional[str],
    user_id: str,
    start_date: Optional[str],
    end_date: Optional[str],
    days_back: int,
    include_boe: bool,
    include_news: bool,
    include_rss: bool,
    include_financial: bool
) -> Dict[str, Any]:
    """
    Perform comprehensive risk assessment for a company
    
    This function handles the core assessment logic without BigQuery operations
    to ensure fast API response times.
    """
    start_time = datetime.utcnow()
    
    # Initialize components
    search_orchestrator = StreamlinedSearchOrchestrator()
    classifier = OptimizedHybridClassifier()
    analytics_service = AnalyticsService()
    
    # Step 1: Data Collection
    logger.info(f"🔍 Starting search for {company_name}")
    search_start = datetime.utcnow()
    
    search_results = await search_orchestrator.search_all(
        query=company_name,
        start_date=start_date,
        end_date=end_date,
        days_back=days_back,
        include_boe=include_boe,
        include_news=include_news,
        include_rss=include_rss
    )
    
    search_time = (datetime.utcnow() - search_start).total_seconds()
    
    # Step 2: Risk Classification
    logger.info(f"🏷️ Classifying {len(search_results)} results for {company_name}")
    classification_start = datetime.utcnow()
    
    classified_results = []
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    for result in search_results:
        classification = classifier.classify_document(
            text=result.get("text", result.get("summary", "")),
            title=result.get("title", ""),
            source=result.get("source", ""),
            section=result.get("section", "")
        )
        
        result["risk_level"] = classification["risk_level"]
        result["confidence"] = classification["confidence"]
        result["classification_method"] = classification["method"]
        result["processing_time_ms"] = classification.get("processing_time_ms", 0)
        
        classified_results.append(result)
        
        # Count risk levels
        if "High" in classification["risk_level"]:
            high_risk_count += 1
        elif "Medium" in classification["risk_level"]:
            medium_risk_count += 1
        else:
            low_risk_count += 1
    
    classification_time = (datetime.utcnow() - classification_start).total_seconds()
    
    # Step 3: Risk Scoring
    logger.info(f"📊 Calculating risk scores for {company_name}")
    
    # Calculate composite risk scores
    financial_score = _calculate_financial_score(classified_results)
    legal_score = _calculate_legal_score(classified_results)
    press_score = _calculate_press_score(classified_results)
    
    # Determine overall risk level
    overall_risk = _determine_overall_risk(financial_score, legal_score, press_score)
    
    # Step 4: Generate Analysis
    analysis_summary = _generate_analysis_summary(
        company_name, classified_results, overall_risk
    )
    
    key_findings = _extract_key_findings(classified_results)
    recommendations = _generate_recommendations(classified_results, overall_risk)
    
    # Step 5: Compile Results
    total_time = (datetime.utcnow() - start_time).total_seconds()
    
    assessment_data = {
        "assessment_id": str(uuid.uuid4()),
        "company_name": company_name,
        "company_vat": company_vat,
        "user_id": user_id,
        "overall_risk": overall_risk,
        "risk_breakdown": {
            "turnover_risk": _map_score_to_risk(financial_score),
            "shareholding_risk": _map_score_to_risk(financial_score),
            "bankruptcy_risk": _map_score_to_risk(legal_score),
            "legal_risk": _map_score_to_risk(legal_score),
            "corruption_risk": _map_score_to_risk(legal_score),
        },
        "financial_metrics": {
            "financial_score": financial_score,
            "legal_score": legal_score,
            "press_score": press_score,
            "composite_score": (financial_score + legal_score + press_score) / 3
        },
        "search_results": {
            "total_results": len(classified_results),
            "high_risk_results": high_risk_count,
            "medium_risk_results": medium_risk_count,
            "low_risk_results": low_risk_count,
            "results_by_source": _group_results_by_source(classified_results)
        },
        "analysis_summary": analysis_summary,
        "key_findings": key_findings,
        "recommendations": recommendations,
        "processing_stats": {
            "total_time_seconds": total_time,
            "search_time_seconds": search_time,
            "classification_time_seconds": classification_time,
            "keyword_efficiency": classifier.stats.get("keyword_hits", 0) / max(len(classified_results), 1) * 100,
            "llm_usage_percent": classifier.stats.get("llm_calls", 0) / max(len(classified_results), 1) * 100
        },
        "classified_results": classified_results,
        "search_date_range_start": start_date,
        "search_date_range_end": end_date,
        "sources_searched": _get_sources_searched(include_boe, include_news, include_rss)
    }
    
    return assessment_data


async def _save_to_bigquery_background(assessment_data: Dict[str, Any]):
    """
    Background task to save assessment data to BigQuery
    
    This function runs asynchronously and doesn't block the API response.
    """
    try:
        bigquery_client = get_bigquery_client()
        
        # Save company data (upsert)
        if assessment_data.get("company_vat"):
            await bigquery_client.save_company({
                "vat": assessment_data["company_vat"],
                "company_name": assessment_data["company_name"],
                "last_assessment_date": datetime.utcnow().isoformat(),
                "overall_risk_level": assessment_data["overall_risk"],
                "risk_score": assessment_data["financial_metrics"]["composite_score"]
            }, priority=1)
        
        # Save assessment data
        assessment_row = {
            "assessment_id": assessment_data["assessment_id"],
            "company_vat": assessment_data["company_vat"],
            "user_id": assessment_data["user_id"],
            "turnover_risk": assessment_data["risk_breakdown"]["turnover_risk"],
            "shareholding_risk": assessment_data["risk_breakdown"]["shareholding_risk"],
            "bankruptcy_risk": assessment_data["risk_breakdown"]["bankruptcy_risk"],
            "legal_risk": assessment_data["risk_breakdown"]["legal_risk"],
            "corruption_risk": assessment_data["risk_breakdown"]["corruption_risk"],
            "overall_risk": assessment_data["overall_risk"],
            "financial_score": assessment_data["financial_metrics"]["financial_score"],
            "legal_score": assessment_data["financial_metrics"]["legal_score"],
            "press_score": assessment_data["financial_metrics"]["press_score"],
            "composite_score": assessment_data["financial_metrics"]["composite_score"],
            "search_date_range_start": assessment_data.get("search_date_range_start"),
            "search_date_range_end": assessment_data.get("search_date_range_end"),
            "sources_searched": assessment_data.get("sources_searched"),
            "total_results_found": assessment_data["search_results"]["total_results"],
            "high_risk_results": assessment_data["search_results"]["high_risk_results"],
            "medium_risk_results": assessment_data["search_results"]["medium_risk_results"],
            "low_risk_results": assessment_data["search_results"]["low_risk_results"],
            "analysis_summary": assessment_data["analysis_summary"],
            "key_findings": assessment_data["key_findings"],
            "recommendations": assessment_data["recommendations"],
            "classification_method": "hybrid_classifier",
            "processing_time_seconds": assessment_data["processing_stats"]["total_time_seconds"]
        }
        
        await bigquery_client.save_assessment(assessment_row, priority=1)
        
        # Save events data
        events_data = []
        for result in assessment_data.get("classified_results", []):
            event_data = {
                "company_vat": assessment_data["company_vat"],
                "company_name": assessment_data["company_name"],
                "title": result.get("title", ""),
                "summary": result.get("summary", ""),
                "source": result.get("source", ""),
                "source_name": result.get("source_name"),
                "section": result.get("section"),
                "url": result.get("url"),
                "author": result.get("author"),
                "risk_level": result.get("risk_level", ""),
                "confidence": result.get("confidence"),
                "classification_method": result.get("classification_method"),
                "publication_date": result.get("date"),
                "processing_time_ms": result.get("processing_time_ms")
            }
            events_data.append(event_data)
        
        if events_data:
            await bigquery_client.save_events(events_data, priority=2)
        
        logger.info(f"✅ BigQuery save completed for {assessment_data['company_name']}")
        
    except Exception as e:
        logger.error(f"❌ BigQuery save failed for {assessment_data['company_name']}: {e}")


@router.post("/assess", response_model=CompanyAssessmentResponse)
async def assess_company_risk(
    request: CompanyAssessmentRequest,
    background_tasks: BackgroundTasks
) -> CompanyAssessmentResponse:
    """
    Perform comprehensive D&O risk assessment for a company
    
    This endpoint demonstrates non-blocking BigQuery integration:
    - Fast API response with assessment results
    - Background BigQuery storage without blocking
    - Real-time processing statistics
    """
    
    try:
        # Perform risk assessment (fast, no BigQuery operations)
        assessment_data = await _perform_risk_assessment(
            company_name=request.company_name,
            company_vat=request.company_vat,
            user_id=request.user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            include_boe=request.include_boe,
            include_news=request.include_news,
            include_rss=request.include_rss,
            include_financial=request.include_financial
        )
        
        # Add BigQuery status
        bigquery_client = get_bigquery_client()
        queue_status = await bigquery_client.get_queue_status()
        
        assessment_data["bigquery_status"] = {
            "queue_status": queue_status,
            "save_enabled": request.save_to_bigquery,
            "estimated_save_time": "background"
        }
        
        # Queue BigQuery save in background (non-blocking)
        if request.save_to_bigquery:
            background_tasks.add_task(
                _save_to_bigquery_background,
                assessment_data
            )
            assessment_data["bigquery_status"]["save_queued"] = True
        else:
            assessment_data["bigquery_status"]["save_queued"] = False
        
        # Return response immediately
        return CompanyAssessmentResponse(
            assessment_id=assessment_data["assessment_id"],
            company_name=assessment_data["company_name"],
            company_vat=assessment_data["company_vat"],
            overall_risk=assessment_data["overall_risk"],
            risk_breakdown=assessment_data["risk_breakdown"],
            financial_metrics=assessment_data["financial_metrics"],
            search_results=assessment_data["search_results"],
            analysis_summary=assessment_data["analysis_summary"],
            key_findings=assessment_data["key_findings"],
            recommendations=assessment_data["recommendations"],
            processing_stats=assessment_data["processing_stats"],
            bigquery_status=assessment_data["bigquery_status"],
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Assessment failed for {request.company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/batch-assess", response_model=BatchAssessmentResponse)
async def batch_assess_companies(
    request: BatchAssessmentRequest,
    background_tasks: BackgroundTasks
) -> BatchAssessmentResponse:
    """
    Perform batch risk assessment for multiple companies
    
    Demonstrates efficient batch processing with BigQuery integration.
    """
    
    batch_id = str(uuid.uuid4())
    assessments = []
    total_start_time = datetime.utcnow()
    
    # Process companies in parallel (limited concurrency)
    import asyncio
    semaphore = asyncio.Semaphore(3)  # Limit concurrent assessments
    
    async def assess_single_company(company_data: Dict[str, str]):
        async with semaphore:
            try:
                assessment = await _perform_risk_assessment(
                    company_name=company_data["company_name"],
                    company_vat=company_data.get("vat"),
                    user_id=request.user_id,
                    start_date=request.assessment_config.get("start_date"),
                    end_date=request.assessment_config.get("end_date"),
                    days_back=request.assessment_config.get("days_back", 7),
                    include_boe=request.assessment_config.get("include_boe", True),
                    include_news=request.assessment_config.get("include_news", True),
                    include_rss=request.assessment_config.get("include_rss", True),
                    include_financial=request.assessment_config.get("include_financial", False)
                )
                
                # Queue BigQuery save
                if request.assessment_config.get("save_to_bigquery", True):
                    background_tasks.add_task(
                        _save_to_bigquery_background,
                        assessment
                    )
                
                return assessment
                
            except Exception as e:
                logger.error(f"❌ Batch assessment failed for {company_data['company_name']}: {e}")
                return {
                    "company_name": company_data["company_name"],
                    "error": str(e),
                    "status": "failed"
                }
    
    # Execute batch assessments
    assessment_tasks = [
        assess_single_company(company) 
        for company in request.companies
    ]
    
    assessment_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
    
    # Compile results
    for result in assessment_results:
        if isinstance(result, dict) and "error" not in result:
            assessments.append({
                "company_name": result["company_name"],
                "overall_risk": result["overall_risk"],
                "assessment_id": result["assessment_id"],
                "status": "completed"
            })
        else:
            assessments.append({
                "company_name": "Unknown",
                "error": str(result),
                "status": "failed"
            })
    
    total_time = (datetime.utcnow() - total_start_time).total_seconds()
    
    # Get BigQuery status
    bigquery_client = get_bigquery_client()
    queue_status = await bigquery_client.get_queue_status()
    
    return BatchAssessmentResponse(
        batch_id=batch_id,
        total_companies=len(request.companies),
        assessments=assessments,
        processing_stats={
            "total_time_seconds": total_time,
            "average_time_per_company": total_time / len(request.companies),
            "successful_assessments": len([a for a in assessments if a["status"] == "completed"]),
            "failed_assessments": len([a for a in assessments if a["status"] == "failed"])
        },
        bigquery_status={
            "queue_status": queue_status,
            "batch_save_enabled": request.assessment_config.get("save_to_bigquery", True)
        }
    )


@router.get("/bigquery/status")
async def get_bigquery_status() -> Dict[str, Any]:
    """Get BigQuery client status and queue information"""
    try:
        bigquery_client = get_bigquery_client()
        queue_status = await bigquery_client.get_queue_status()
        
        return {
            "status": "healthy",
            "project_id": settings.BIGQUERY_PROJECT,
            "dataset_id": settings.BIGQUERY_DATASET,
            "queue_status": queue_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/bigquery/flush")
async def flush_bigquery_queue() -> Dict[str, Any]:
    """Force flush the BigQuery write queue"""
    try:
        bigquery_client = get_bigquery_client()
        result = await bigquery_client.flush_queue()
        
        return {
            "status": "success",
            "message": "BigQuery queue flushed successfully",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Helper functions for risk assessment logic

def _calculate_financial_score(results: List[Dict[str, Any]]) -> float:
    """Calculate financial risk score based on search results"""
    # Implementation would analyze financial indicators
    # For now, return a score based on risk level distribution
    high_risk = sum(1 for r in results if "High" in r.get("risk_level", ""))
    medium_risk = sum(1 for r in results if "Medium" in r.get("risk_level", ""))
    total = len(results) if results else 1
    
    # Score from 0-100, higher = more risky
    score = (high_risk * 0.8 + medium_risk * 0.4) / total * 100
    return min(score, 100.0)


def _calculate_legal_score(results: List[Dict[str, Any]]) -> float:
    """Calculate legal risk score based on search results"""
    # Similar to financial score but focused on legal indicators
    legal_high = sum(1 for r in results if "High-Legal" in r.get("risk_level", ""))
    legal_medium = sum(1 for r in results if "Medium-Legal" in r.get("risk_level", ""))
    total = len(results) if results else 1
    
    score = (legal_high * 0.9 + legal_medium * 0.5) / total * 100
    return min(score, 100.0)


def _calculate_press_score(results: List[Dict[str, Any]]) -> float:
    """Calculate press/media risk score"""
    # Analyze negative press coverage
    negative_press = sum(1 for r in results if r.get("source") in ["NewsAPI", "RSS"])
    total = len(results) if results else 1
    
    score = (negative_press * 0.6) / total * 100
    return min(score, 100.0)


def _determine_overall_risk(financial: float, legal: float, press: float) -> str:
    """Determine overall risk level based on component scores"""
    composite = (financial + legal + press) / 3
    
    if composite >= 70:
        return "red"
    elif composite >= 40:
        return "orange"
    else:
        return "green"


def _map_score_to_risk(score: float) -> str:
    """Map numerical score to risk level"""
    if score >= 70:
        return "red"
    elif score >= 40:
        return "orange"
    else:
        return "green"


def _generate_analysis_summary(company_name: str, results: List[Dict[str, Any]], overall_risk: str) -> str:
    """Generate analysis summary"""
    high_risk_count = sum(1 for r in results if "High" in r.get("risk_level", ""))
    
    if overall_risk == "red":
        return f"Análisis de {company_name} revela riesgo ALTO con {high_risk_count} eventos de alto riesgo. Se requiere atención inmediata del consejo de administración."
    elif overall_risk == "orange":
        return f"Análisis de {company_name} muestra riesgo MEDIO con {high_risk_count} eventos de alto riesgo. Se recomienda monitoreo continuo."
    else:
        return f"Análisis de {company_name} indica riesgo BAJO. No se detectaron eventos críticos que requieran acción inmediata."


def _extract_key_findings(results: List[Dict[str, Any]]) -> List[str]:
    """Extract key findings from search results"""
    findings = []
    high_risk_results = [r for r in results if "High" in r.get("risk_level", "")]
    
    for result in high_risk_results[:5]:  # Top 5 findings
        findings.append(f"Evento de alto riesgo: {result.get('title', '')}")
    
    return findings


def _generate_recommendations(results: List[Dict[str, Any]], overall_risk: str) -> List[str]:
    """Generate recommendations based on risk level"""
    recommendations = []
    
    if overall_risk == "red":
        recommendations.extend([
            "Revisar inmediatamente las políticas de D&O",
            "Consultar con asesores legales especializados",
            "Implementar medidas de mitigación de riesgo urgentes"
        ])
    elif overall_risk == "orange":
        recommendations.extend([
            "Monitorear continuamente los indicadores de riesgo",
            "Actualizar políticas de compliance",
            "Realizar auditoría de gobernanza corporativa"
        ])
    else:
        recommendations.extend([
            "Mantener políticas de D&O actualizadas",
            "Continuar con el monitoreo regular"
        ])
    
    return recommendations


def _group_results_by_source(results: List[Dict[str, Any]]) -> Dict[str, int]:
    """Group results by source"""
    source_counts = {}
    for result in results:
        source = result.get("source", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
    return source_counts


def _get_sources_searched(include_boe: bool, include_news: bool, include_rss: bool) -> List[str]:
    """Get list of sources that were searched"""
    sources = []
    if include_boe:
        sources.append("BOE")
    if include_news:
        sources.append("NewsAPI")
    if include_rss:
        sources.extend(["El País", "Expansión", "El Mundo", "ABC", "La Vanguardia"])
    return sources 