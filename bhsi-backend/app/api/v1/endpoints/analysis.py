from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.analysis.management_summarizer import ManagementSummarizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ManagementSummaryRequest(BaseModel):
    company_name: str
    classification_results: List[Dict[str, Any]]
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
        logger.info(f"Generating management summary for {request.company_name}")
        
        # Initialize management summarizer
        summarizer = ManagementSummarizer()
        
        # Generate comprehensive summary
        summary = await summarizer.generate_summary(
            company_name=request.company_name,
            classification_results=request.classification_results,
            include_evidence=request.include_evidence,
            language=request.language
        )
        
        logger.info("✅ Management summary generated successfully")
        
        return ManagementSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(
            f"Failed to generate management summary for "
            f"{request.company_name}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating management summary: {str(e)}"
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