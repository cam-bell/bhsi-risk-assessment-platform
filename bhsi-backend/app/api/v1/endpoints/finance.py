from fastapi import APIRouter, HTTPException, Query
from app.services.yahoo_finance_service import StreamlinedYahooFinanceAgent
from app.agents.search.streamlined_yfinance_agent import StreamlinedYahooNewsAgent
from app.agents.analysis.yfinance_risk_engine import assess_risk
from app.services.yfinance_summary import (
    generate_yfinance_summary,
    generate_financial_insights,
    generate_risk_assessment_summary
)
import re

router = APIRouter()

yahoo_agent = StreamlinedYahooFinanceAgent()


@router.get("/financials")
async def get_financial_info(
    query: str = Query(..., description="Ticker or company name"),
    include_insights: bool = Query(
        False, description="Include AI-generated financial insights"
    )
):
    yahoo_agent = StreamlinedYahooFinanceAgent()
    # If query looks like a ticker, use it directly
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        if not ticker:
            raise HTTPException(
                status_code=404, 
                detail="Could not resolve ticker for company name"
            )
    
    # Get raw financial info (already cleaned by the service)
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    if "error" in financial_data:
        raise HTTPException(status_code=500, detail=financial_data["error"])
    
    # Add AI insights if requested
    if include_insights:
        try:
            company_name = (
                financial_data.get("longName") or 
                financial_data.get("company_name") or 
                ticker
            )
            insights = await generate_financial_insights(
                financial_data, company_name, ticker
            )
            financial_data["ai_insights"] = insights
        except Exception as e:
            financial_data["ai_insights"] = f"Failed to generate insights: {str(e)}"
    
    return financial_data


@router.get("/risk")
async def get_risk_report(
    query: str = Query(..., description="Ticker or company name"),
    include_summary: bool = Query(
        False, description="Include AI-generated risk summary"
    )
):
    yahoo_agent = StreamlinedYahooFinanceAgent()
    # If query looks like a ticker, use it directly
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        if not ticker:
            raise HTTPException(
                status_code=404, 
                detail="Could not resolve ticker for company name"
            )
    
    # Now proceed as before (data already cleaned by service)
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    if "error" in financial_data:
        raise HTTPException(status_code=500, detail=financial_data["error"])
    
    company_name = (
        financial_data.get("longName") or 
        financial_data.get("company_name") or 
        ticker
    )
    
    news_agent = StreamlinedYahooNewsAgent()
    news_result = await news_agent.search(ticker=ticker)
    news = news_result.get("articles", [])
    
    risk_result = assess_risk(financial_data, news)
    risk_level = risk_result.get("riskLevel", "Unknown")
    
    score_factors = {
        "debtToEquity": financial_data.get("debtToEquity"),
        "totalRevenue": financial_data.get("financials", {}).get("Total Revenue"),
        "cashflow": financial_data.get("cashflow"),
        "red_news_count": sum(1 for n in news if n.get("sentiment") == "Red")
    }
    
    response = {
        "company": company_name,
        "ticker": ticker,
        "riskLevel": risk_level,
        "financials": financial_data,
        "news": news,
        "scoreFactors": score_factors
    }
    
    # Add AI risk summary if requested
    if include_summary:
        try:
            risk_summary = await generate_risk_assessment_summary(
                financial_data, news, risk_level, company_name, ticker
            )
            response["ai_risk_summary"] = risk_summary
        except Exception as e:
            response["ai_risk_summary"] = f"Failed to generate risk summary: {str(e)}"
    
    return response


@router.get("/summary")
async def get_gemini_summary(
    query: str = Query(..., description="Ticker or company name")
):
    yahoo_agent = StreamlinedYahooFinanceAgent()
    # Ticker resolution logic (same as /risk)
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        if not ticker:
            raise HTTPException(
                status_code=404, 
                detail="Could not resolve ticker for company name"
            )
    
    # Fetch data (already cleaned by service)
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    if "error" in financial_data:
        raise HTTPException(status_code=500, detail=financial_data["error"])
    
    news_agent = StreamlinedYahooNewsAgent()
    news_result = await news_agent.search(ticker=ticker)
    news = news_result.get("articles", [])
    
    company_name = (
        financial_data.get("longName") or 
        financial_data.get("company_name") or 
        ticker
    )
    
    # Generate summary using the new service
    try:
        summary = await generate_yfinance_summary(
            financial_data, news, company_name, ticker
        )
        return {
            "company": company_name, 
            "ticker": ticker, 
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Gemini summary failed: {e}"
        ) 