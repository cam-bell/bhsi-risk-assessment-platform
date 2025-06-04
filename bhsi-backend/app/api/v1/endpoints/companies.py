from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyAnalysis
from app.agents.search.orchestrator import SearchOrchestrator
from app.agents.analysis.orchestrator import AnalysisOrchestrator
from app.crud import company as company_crud
from app.core.config import settings

router = APIRouter()

@router.post("/analyze", response_model=CompanyAnalysis)
async def analyze_company(
    company: CompanyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> Dict[str, Any]:
    """
    Analyze a company's risk profile
    """
    # Initialize orchestrators
    search_orchestrator = SearchOrchestrator()
    analysis_orchestrator = AnalysisOrchestrator()
    
    try:
        # Perform search
        search_results = await search_orchestrator.search_company(company.name)
        
        # Perform analysis
        analysis = await analysis_orchestrator.analyze_company(search_results)
        
        # Format for database
        formatted_results = analysis_orchestrator.format_for_database(analysis)
        
        # Create or update company record
        db_company = company_crud.get_by_name(db, name=company.name)
        if db_company:
            company_crud.update(db, db_obj=db_company, obj_in=formatted_results)
        else:
            company_crud.create(db, obj_in=formatted_results)
        
        return analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing company: {str(e)}"
        )

@router.post("/batch-analyze", response_model=List[CompanyAnalysis])
async def batch_analyze_companies(
    companies: List[CompanyCreate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> List[Dict[str, Any]]:
    """
    Analyze multiple companies in batch
    """
    results = []
    for company in companies:
        try:
            analysis = await analyze_company(company, background_tasks, db)
            results.append(analysis)
        except Exception as e:
            results.append({
                "error": f"Error analyzing {company.name}: {str(e)}",
                "company": company.name
            })
    
    return results

@router.get("/{company_id}/analysis", response_model=CompanyAnalysis)
async def get_company_analysis(
    company_id: int,
    db: Session = Depends(deps.get_db)
) -> Dict[str, Any]:
    """
    Get analysis results for a specific company
    """
    company = company_crud.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    return {
        "risk_scores": {
            "turnover": company.turnover,
            "shareholding": company.shareholding,
            "bankruptcy": company.bankruptcy,
            "legal": company.legal,
            "corruption": company.corruption,
            "overall": company.overall
        },
        "processed_results": {
            "google_results": company.google_results,
            "bing_results": company.bing_results,
            "gov_results": company.gov_results,
            "news_results": company.news_results,
            "analysis_summary": company.analysis_summary
        }
    }

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
) -> List[Company]:
    """
    List all companies with their risk profiles
    """
    companies = company_crud.get_multi(db, skip=skip, limit=limit)
    return companies 