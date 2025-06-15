#!/usr/bin/env python3
"""
Focused BOE Company Search API
Search for specific companies across date ranges in BOE documents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import datetime
from app.agents.search.orchestrator import SearchOrchestrator

# Import the BOE search function directly
from app.agents.search.BOE import search_boe_for_company, fetch_boe_summary, iter_items, tag_risk, full_text, entities

app = FastAPI(
    title="BOE Company Risk Search",
    description="Search for companies in BOE documents across date ranges",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanySearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYYMMDD
    end_date: Optional[str] = None    # Format: YYYYMMDD
    days_back: Optional[int] = 7      # Alternative: search last N days

class NewsSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    page: Optional[int] = 1
    page_size: Optional[int] = 20

class UnifiedSearchRequest(BaseModel):
    company_name: str
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    days_back: Optional[int] = 7      # Alternative: search last N days
    include_boe: bool = True
    include_news: bool = True

@app.get("/")
async def root():
    return {
        "message": "BOE Company Risk Search API",
        "description": "Search for companies in BOE documents without limits",
        "endpoint": "/search/{company_name}",
        "docs": "/docs",
        "example": "/search/Banco%20Santander?days_back=30"
    }

@app.get("/search/{company_name}")
async def search_company_unlimited(
    company_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days_back: Optional[int] = 7
):
    """
    Search for a company across multiple dates in BOE documents - NO LIMITS
    
    - **company_name**: Name of the company to search for
    - **start_date**: Start date in YYYYMMDD format (optional)
    - **end_date**: End date in YYYYMMDD format (optional)
    - **days_back**: Search last N days if dates not specified (default: 7)
    
    Returns ALL occurrences found across the date range
    """
    try:
        # Determine date range
        if start_date and end_date:
            dates_to_search = generate_date_range(start_date, end_date)
        else:
            # Use days_back
            today = datetime.date.today()
            dates_to_search = [
                (today - datetime.timedelta(days=i)).strftime("%Y%m%d")
                for i in range(days_back)
            ]
        
        all_results = []
        search_summary = {
            "company_name": company_name,
            "dates_searched": len(dates_to_search),
            "date_range": f"{dates_to_search[-1]} to {dates_to_search[0]}" if dates_to_search else "none",
            "total_matches": 0,
            "high_risk_matches": 0,
            "dates_with_matches": [],
            "risk_breakdown": {
                "High-Legal": 0,
                "Low": 0
            }
        }
        
        # Search each date
        for date_str in dates_to_search:
            try:
                print(f"Searching BOE for {company_name} on {date_str}...")
                
                summary = fetch_boe_summary(date_str)
                date_matches = []
                
                for item in iter_items(summary):
                    # Check if company name appears in title or get full text
                    title = item.get("titulo", "").lower()
                    
                    if company_name.lower() in title:
                        # Get detailed information
                        try:
                            text = full_text(item)
                            ents = entities(text)
                            risk = tag_risk(item)
                            
                            match_info = {
                                "date": date_str,
                                "identificador": item.get("identificador", "Unknown"),
                                "titulo": item.get("titulo", ""),
                                "risk_level": risk,
                                "seccion": item.get("seccion_codigo", ""),
                                "seccion_nombre": item.get("seccion_nombre", ""),
                                "url_html": item.get("url_html", ""),
                                "url_xml": item.get("url_xml", ""),
                                "entities_found": ents,
                                "full_text_snippet": text[:500] + "..." if len(text) > 500 else text
                            }
                            
                            date_matches.append(match_info)
                            search_summary["total_matches"] += 1
                            search_summary["risk_breakdown"][risk] += 1
                            
                            if risk == "High-Legal":
                                search_summary["high_risk_matches"] += 1
                                
                        except Exception as e:
                            print(f"Error processing full text for {item.get('identificador', 'unknown')}: {e}")
                            # Still include basic info even if full text fails
                            match_info = {
                                "date": date_str,
                                "identificador": item.get("identificador", "Unknown"),
                                "titulo": item.get("titulo", ""),
                                "risk_level": tag_risk(item),
                                "seccion": item.get("seccion_codigo", ""),
                                "url_html": item.get("url_html", ""),
                                "error": "Could not extract full text"
                            }
                            date_matches.append(match_info)
                            search_summary["total_matches"] += 1
                
                if date_matches:
                    search_summary["dates_with_matches"].append({
                        "date": date_str,
                        "matches_count": len(date_matches)
                    })
                    all_results.extend(date_matches)
                    
            except Exception as e:
                print(f"Error searching date {date_str}: {e}")
                continue
        
        # Sort results by date (newest first) and risk level
        all_results.sort(key=lambda x: (x["date"], x["risk_level"] == "High-Legal"), reverse=True)
        
        return {
            "search_summary": search_summary,
            "results": all_results,
            "high_risk_results": [r for r in all_results if r["risk_level"] == "High-Legal"],
            "query_info": {
                "searched_dates": dates_to_search,
                "search_completed": datetime.datetime.now().isoformat(),
                "no_limits_applied": True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for {company_name}: {str(e)}")

@app.post("/search")
async def unified_search(request: UnifiedSearchRequest):
    """
    Unified search endpoint that combines BOE and news search
    
    - **company_name**: Name of the company to search for
    - **start_date**: Start date in YYYY-MM-DD format (optional)
    - **end_date**: End date in YYYY-MM-DD format (optional)
    - **days_back**: Search last N days if dates not specified (default: 7)
    - **include_boe**: Whether to include BOE results (default: True)
    - **include_news**: Whether to include news results (default: True)
    
    Returns combined results from both sources with risk assessment
    """
    try:
        orchestrator = SearchOrchestrator()
        
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
        
        results = await orchestrator.search_all(
            query=request.company_name,
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
            active_agents=active_agents
        )
        
        # Combine and sort results by date
        all_results = []
        for source, source_results in results.items():
            if source == "boe":
                for result in source_results.get("results", []):
                    all_results.append({
                        "source": "BOE",
                        "date": result.get("date"),
                        "title": result.get("title"),
                        "summary": result.get("summary"),
                        "risk_level": result.get("risk_level"),
                        "confidence": result.get("confidence"),
                        "url": result.get("url")
                    })
            elif source == "newsapi":
                for result in source_results.get("articles", []):
                    # Defensive: use published_at or fallback to today if missing
                    date_val = result.get("published_at") or datetime.datetime.now().strftime("%Y-%m-%d")
                    all_results.append({
                        "source": "News",
                        "date": date_val,
                        "title": result.get("title"),
                        "summary": result.get("description"),
                        "risk_level": result.get("risk_level"),
                        "confidence": result.get("confidence"),
                        "url": result.get("url")
                    })
        
        # Remove results with None dates (just in case)
        all_results = [r for r in all_results if r.get("date")]
        # Sort by date, most recent first
        all_results.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "company_name": request.company_name,
            "search_date": datetime.datetime.now().isoformat(),
            "date_range": {
                "start": request.start_date,
                "end": request.end_date,
                "days_back": request.days_back
            },
            "results": all_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in unified search: {str(e)}")

def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """Generate list of dates between start_date and end_date"""
    start = datetime.datetime.strptime(start_date, "%Y%m%d").date()
    end = datetime.datetime.strptime(end_date, "%Y%m%d").date()
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += datetime.timedelta(days=1)
    
    return dates

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "message": "BOE Company Search API is running"}

@app.get("/news/{company_name}")
async def search_company_news(
    company_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days_back: Optional[int] = 7,
    page: Optional[int] = 1,
    page_size: Optional[int] = 20
):
    """
    Search for news articles about a company
    
    - **company_name**: Name of the company to search for
    - **start_date**: Start date in YYYY-MM-DD format (optional)
    - **end_date**: End date in YYYY-MM-DD format (optional)
    - **days_back**: Search last N days if dates not specified (default: 7)
    - **page**: Page number for pagination (default: 1)
    - **page_size**: Number of results per page (default: 20, max: 100)
    
    Returns news articles with risk assessment
    """
    try:
        orchestrator = SearchOrchestrator()
        results = await orchestrator.search_all(
            query=company_name,
            start_date=start_date,
            end_date=end_date,
            days_back=days_back
        )
        
        return {
            "company_name": company_name,
            "search_date": datetime.datetime.now().isoformat(),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching news for {company_name}: {str(e)}")

@app.post("/news")
async def search_company_news_post(request: NewsSearchRequest):
    """
    Search for news articles via POST method
    """
    return await search_company_news(
        company_name=request.company_name,
        start_date=request.start_date,
        end_date=request.end_date,
        days_back=request.days_back,
        page=request.page,
        page_size=request.page_size
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 