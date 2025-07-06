from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.analysis.management_summarizer import ManagementSummarizer
from app.core.config import settings
import logging
from app.agents.search.orchestrator_factory import get_search_orchestrator
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier

logger = logging.getLogger(__name__)

router = APIRouter()


class ManagementSummaryRequest(BaseModel):
    company_name: str
    classification_results: List[Dict[str, Any]] = []
    include_evidence: bool = True
    language: str = "es"


class RiskBreakdown(BaseModel):
    level: str
    reasoning: str
    evidence: List[str]
    confidence: float


class ManagementSummaryResponse(BaseModel):
    company_name: str
    overall_risk: str
    executive_summary: str
    risk_breakdown: Dict[str, RiskBreakdown]
    key_findings: List[str]
    recommendations: List[str]
    generated_at: str
    method: str
    financial_health: Optional[Dict[str, Any]] = None
    key_risks: Optional[List[Dict[str, Any]]] = None
    compliance_status: Optional[Dict[str, Any]] = None


async def fetch_classification_results(company_name: str) -> List[Dict[str, Any]]:
    """
    Fetch and classify documents for a company using the orchestrator and classifier.
    Mirrors the logic from the streamlined_search endpoint, but only for BOE and NewsAPI for speed.
    """
    orchestrator = get_search_orchestrator()
    classifier = OptimizedHybridClassifier()
    # Only use BOE and NewsAPI for management summary
    active_agents = ["boe", "newsapi"]
    search_results = await orchestrator.search_all(
        query=company_name,
        days_back=7,
        active_agents=active_agents
    )
    classified_results = []
    # BOE
    if "boe" in search_results and search_results["boe"].get("results"):
        for boe_result in search_results["boe"]["results"]:
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
                "url": boe_result.get("url_html", "")
            }
            classified_results.append(classified_result)
    # NewsAPI
    if "newsapi" in search_results and search_results["newsapi"].get("articles"):
        for article in search_results["newsapi"]["articles"]:
            # Type check to prevent 'str' object has no attribute 'get' errors
            if not isinstance(article, dict):
                logger.warning(f"Skipping non-dict NewsAPI article: {type(article)} - {article}")
                continue
            
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
                "url": article.get("url", "")
            }
            classified_results.append(classified_result)
    return classified_results


@router.post("/management-summary", response_model=ManagementSummaryResponse)
async def generate_management_summary(
    request: ManagementSummaryRequest
) -> Dict[str, Any]:
    """
    Generate an executive management summary explaining company risk classification

    **Purpose**: Provide executive-level explanation of why a company was classified 
    with specific risk levels.

    **Input**: Classification results from the search endpoint
    **Output**: Executive summary with risk breakdown and recommendations
    """
    try:
        logger.info(
            f"Generating management summary for {request.company_name}"
        )
        summarizer = ManagementSummarizer()
        # If classification_results is empty, fetch them
        classification_results = request.classification_results
        if not classification_results:
            classification_results = await fetch_classification_results(request.company_name)
        summary = await summarizer.generate_summary(
            company_name=request.company_name,
            classification_results=classification_results,
            include_evidence=request.include_evidence,
            language=request.language
        )
        logger.info("✅ Management summary generated successfully")
        return ManagementSummaryResponse(**summary)
    except Exception as e:
        logger.error(
            "Failed to generate management summary for "
            f"{request.company_name}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Error generating management summary: "
                f"{str(e)}"
            )
        )


@router.get("/summary-templates")
async def get_summary_templates():
    """
    Get available summary templates and risk categories
    """
    
    return {
        "risk_categories": [
            "legal", "financial", "operational", "regulatory", "reputational"
        ],
        "risk_levels": [
            {"level": "green", "description": "Low risk - minimal concerns"},
            {"level": "orange", "description": "Medium risk - requires monitoring"},
            {"level": "red", "description": "High risk - immediate attention needed"}
        ],
        "languages_supported": ["es", "en"],
        "evidence_types": [
            "boe_documents", "news_articles", "regulatory_filings", 
            "court_proceedings"
        ]
    }


@router.get("/health")
async def analysis_health_check():
    """
    Health check for analysis services
    """
    
    try:
        summarizer = ManagementSummarizer()
        status = await summarizer.health_check()
        
        return {
            "status": "healthy",
            "management_summarizer": status,
            "cloud_services": {
                "gemini_available": status.get("cloud_gemini_available", False),
                "fallback_ready": status.get("template_fallback_ready", True)
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 