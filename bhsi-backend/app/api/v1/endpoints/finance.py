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
import logging

router = APIRouter()

yahoo_agent = StreamlinedYahooFinanceAgent()
logger = logging.getLogger(__name__)


@router.get("/financials")
async def get_financial_info(
    query: str = Query(..., description="Ticker or company name"),
    include_insights: bool = Query(
        False, description="Include AI-generated financial insights"
    )
):
    yahoo_agent = StreamlinedYahooFinanceAgent()
    
    # Enhanced ticker resolution with better error handling
    ticker = None
    company_name = query.strip()
    
    # If query looks like a ticker, use it directly
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        # Try LLM-based resolution first
        try:
            ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        except Exception as e:
            logger.warning(f"LLM ticker resolution failed for {query}: {e}")
        
        # Fallback to basic resolution
        if not ticker:
            ticker = yahoo_agent._get_ticker_symbol(query)
    
    # If still no ticker found, provide informative response
    if not ticker:
        return {
            "longName": company_name,
            "ticker": query.upper(),
            "error": f"Could not resolve ticker symbol for '{query}'",
            "data_note": f"Unable to find financial data for '{query}'. This company may not be publicly traded or may be listed under a different name.",
            "data_availability": {
                "has_financial_data": False,
                "has_detailed_financials": False,
                "has_balance_sheet": False,
                "has_cashflow": False,
                "has_recommendations": False,
                "data_completeness": 0
            },
            "suggestions": [
                "Try using the stock ticker symbol instead (e.g., TSLA for Tesla)",
                "Check if the company name is spelled correctly",
                "Verify that the company is publicly traded"
            ]
        }
    
    # Get raw financial info (already cleaned by the service)
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    
    # Even if there's an error, try to provide useful fallback information
    if "error" in financial_data:
        financial_data.update({
            "query": query,
            "attempted_ticker": ticker,
            "suggestions": [
                f"Verify that {ticker} is the correct ticker symbol",
                "Check if the company is actively traded",
                "Try searching by company name instead of ticker"
            ]
        })
    
    # Add AI insights if requested and data is available
    if include_insights and not financial_data.get("error"):
        try:
            company_name_for_insights = (
                financial_data.get("longName") or 
                financial_data.get("company_name") or 
                ticker
            )
            insights = await generate_financial_insights(
                financial_data, company_name_for_insights, ticker
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
    
    # Enhanced ticker resolution (same as financials endpoint)
    ticker = None
    company_name = query.strip()
    
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        try:
            ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        except Exception as e:
            logger.warning(f"LLM ticker resolution failed for {query}: {e}")
        
        if not ticker:
            ticker = yahoo_agent._get_ticker_symbol(query)
    
    # If no ticker found, provide risk assessment based on available info
    if not ticker:
        return {
            "company": company_name,
            "ticker": query.upper(),
            "riskLevel": "Unknown",
            "error": f"Could not resolve ticker symbol for '{query}'",
            "data_note": f"Risk assessment unavailable for '{query}' due to lack of financial data.",
            "scoreFactors": {
                "debtToEquity": None,
                "totalRevenue": None,
                "netIncome": None,
                "currentRatio": None,
                "returnOnEquity": None,
                "red_news_count": 0,
                "freeCashFlow": None,
            },
            "news": [],
            "suggestions": [
                "Try using the stock ticker symbol instead",
                "Verify the company name spelling",
                "Check if the company is publicly traded"
            ]
        }
    
    # Get financial data with error handling
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    
    company_name_final = (
        financial_data.get("longName") or 
        financial_data.get("company_name") or 
        company_name or
        ticker
    )
    
    # Get news data
    news_agent = StreamlinedYahooNewsAgent()
    try:
        news_result = await news_agent.search(ticker=ticker)
        news = news_result.get("articles", [])
    except Exception as e:
        logger.warning(f"News search failed for {ticker}: {e}")
        news = []
    
    # Assess risk even with limited data
    try:
        risk_result = assess_risk(financial_data, news)
        risk_level = risk_result.get("riskLevel", "Unknown")
    except Exception as e:
        logger.warning(f"Risk assessment failed for {ticker}: {e}")
        risk_level = "Unknown"

    # --- Extract latest available values for score factors ---
    def get_latest(dct, key):
        """Get the latest (most recent) value for a key in a dict of years."""
        if not isinstance(dct, dict):
            return None
        if key in dct:
            return dct[key]
        try:
            latest = sorted(dct.keys(), reverse=True)[0]
            val = dct[latest]
            if isinstance(val, dict) and key in val:
                return val[key]
            if key is None:
                return val
        except Exception:
            pass
        return None

    # Get latest values for each metric with fallbacks
    debt_to_equity = financial_data.get("debtToEquity")
    total_revenue = get_latest(financial_data.get("financials", {}), "Total Revenue")
    net_income = get_latest(financial_data.get("financials", {}), "Net Income")
    current_ratio = financial_data.get("currentRatio")
    return_on_equity = financial_data.get("returnOnEquity")
    free_cash_flow = get_latest(financial_data.get("cashflow", {}), "Free Cash Flow")

    score_factors = {
        "debtToEquity": debt_to_equity,
        "totalRevenue": total_revenue,
        "netIncome": net_income,
        "currentRatio": current_ratio,
        "returnOnEquity": return_on_equity,
        "red_news_count": sum(1 for n in news if n.get("sentiment") == "Red"),
        "freeCashFlow": free_cash_flow,
        "cashflow": financial_data.get("cashflow"),
    }

    response = {
        "company": company_name_final,
        "ticker": ticker,
        "riskLevel": risk_level,
        "financials": financial_data,
        "news": news,
        "scoreFactors": score_factors
    }
    
    # Add error information if present
    if financial_data.get("error"):
        response["data_note"] = financial_data.get("data_note", "Limited financial data available")
        response["data_availability"] = financial_data.get("data_availability", {})
    
    # Add AI risk summary if requested
    if include_summary:
        try:
            risk_summary = await generate_risk_assessment_summary(
                financial_data, news, risk_level, company_name_final, ticker
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
    
    # Enhanced ticker resolution (same as other endpoints)
    ticker = None
    company_name = query.strip()
    
    if re.match(r'^[A-Z0-9.]{1,7}$', query.strip().upper()):
        ticker = query.strip().upper()
    else:
        try:
            ticker = await yahoo_agent.get_ticker_symbol_llm(query)
        except Exception as e:
            logger.warning(f"LLM ticker resolution failed for {query}: {e}")
        
        if not ticker:
            ticker = yahoo_agent._get_ticker_symbol(query)
    
    # If no ticker found, provide general summary
    if not ticker:
        return {
            "company": company_name, 
            "ticker": query.upper(), 
            "summary": f"Unable to generate financial summary for '{query}' due to unavailable market data. This company may not be publicly traded or may be listed under a different name. For publicly traded companies, try using the official stock ticker symbol.",
            "error": "Ticker resolution failed",
            "suggestions": [
                "Try using the stock ticker symbol instead",
                "Verify the company name spelling",
                "Check if the company is publicly traded"
            ]
        }
    
    # Fetch data with error handling
    financial_data = yahoo_agent.get_company_financial_data(ticker)
    
    # Get news data
    try:
        news_agent = StreamlinedYahooNewsAgent()
        news_result = await news_agent.search(ticker=ticker)
        news = news_result.get("articles", [])
    except Exception as e:
        logger.warning(f"News search failed for {ticker}: {e}")
        news = []
    
    company_name_final = (
        financial_data.get("longName") or 
        financial_data.get("company_name") or 
        company_name or
        ticker
    )
    
    # Generate summary with available data
    try:
        summary = await generate_yfinance_summary(
            financial_data, news, company_name_final, ticker
        )
        return {
            "company": company_name_final, 
            "ticker": ticker, 
            "summary": summary,
            "data_availability": financial_data.get("data_availability", {}),
            "data_note": financial_data.get("data_note")
        }
    except Exception as e:
        logger.error(f"Summary generation failed for {ticker}: {e}")
        return {
            "company": company_name_final,
            "ticker": ticker,
            "summary": f"Summary generation failed for {company_name_final}. This may be due to limited available data or service connectivity issues.",
            "error": str(e),
            "data_availability": financial_data.get("data_availability", {})
        } 