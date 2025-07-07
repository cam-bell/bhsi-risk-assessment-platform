#!/usr/bin/env python3
"""
Yahoo Finance Summary Service - Gemini-powered financial analysis summaries
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.gemini.main import generate_text

logger = logging.getLogger(__name__)


async def generate_yfinance_summary(
    financial_data: Dict[str, Any], 
    news_data: List[Dict[str, Any]], 
    company_name: str,
    ticker: str
) -> str:
    """
    Generate a comprehensive D&O risk summary using Gemini.
    
    Args:
        financial_data: Financial metrics and data from Yahoo Finance
        news_data: News headlines with sentiment analysis
        company_name: Company name
        ticker: Stock ticker symbol
    
    Returns:
        Generated summary text
    """
    try:
        # Extract key financial metrics for the prompt
        key_metrics = {
            "market_cap": financial_data.get("marketCap"),
            "debt_to_equity": financial_data.get("debtToEquity"),
            "profit_margins": financial_data.get("profitMargins"),
            "beta": financial_data.get("beta"),
            "total_revenue": financial_data.get("totalRevenue"),
            "sector": financial_data.get("sector"),
            "industry": financial_data.get("industry"),
        }
        
        # Extract news sentiment summary
        red_news = [n for n in news_data if n.get("sentiment") == "Red"]
        orange_news = [n for n in news_data if n.get("sentiment") == "Orange"]
        green_news = [n for n in news_data if n.get("sentiment") == "Green"]
        
        # Build a structured prompt
        prompt = f"""
Analyze the following financial and news data for {company_name} ({ticker}) and provide a concise summary focused on D&O (Directors & Officers) insurance risk assessment.

COMPANY: {company_name} ({ticker})
SECTOR: {key_metrics.get('sector', 'N/A')}
INDUSTRY: {key_metrics.get('industry', 'N/A')}

KEY FINANCIAL METRICS:
- Market Cap: {key_metrics.get('market_cap', 'N/A')}
- Debt-to-Equity Ratio: {key_metrics.get('debt_to_equity', 'N/A')}
- Profit Margins: {key_metrics.get('profit_margins', 'N/A')}
- Beta (Volatility): {key_metrics.get('beta', 'N/A')}
- Total Revenue: {key_metrics.get('total_revenue', 'N/A')}

RECENT NEWS SENTIMENT:
- High Risk (Red): {len(red_news)} headlines
- Medium Risk (Orange): {len(orange_news)} headlines  
- Low Risk (Green): {len(green_news)} headlines

RECENT NEWS HIGHLIGHTS:
{chr(10).join([f"- {n.get('headline', 'N/A')}" for n in news_data[:5]])}

Please provide a 2-3 paragraph summary that:
1. Identifies key D&O risk factors
2. Highlights any regulatory or legal concerns
3. Assesses financial stability and governance risks
4. Provides actionable insights for insurance underwriting

Focus on factors that would impact D&O policy pricing and coverage decisions.
"""
        
        summary = await generate_text(prompt, max_tokens=512)
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Failed to generate summary for {ticker}: {e}")
        return f"Summary generation failed for {company_name} ({ticker}): {str(e)}"


async def generate_financial_insights(
    financial_data: Dict[str, Any],
    company_name: str,
    ticker: str
) -> str:
    """
    Generate focused financial insights for investment/risk analysis.
    
    Args:
        financial_data: Financial metrics and data from Yahoo Finance
        company_name: Company name
        ticker: Stock ticker symbol
    
    Returns:
        Generated insights text
    """
    try:
        # Extract comprehensive financial metrics
        metrics = {
            "market_cap": financial_data.get("marketCap"),
            "enterprise_value": financial_data.get("enterpriseValue"),
            "trailing_pe": financial_data.get("trailingPE"),
            "debt_to_equity": financial_data.get("debtToEquity"),
            "return_on_assets": financial_data.get("returnOnAssets"),
            "return_on_equity": financial_data.get("returnOnEquity"),
            "profit_margins": financial_data.get("profitMargins"),
            "beta": financial_data.get("beta"),
            "total_cash": financial_data.get("totalCash"),
            "total_revenue": financial_data.get("totalRevenue"),
            "ebitda": financial_data.get("ebitda"),
        }
        
        prompt = f"""
Provide a comprehensive financial analysis for {company_name} ({ticker}) based on the following metrics:

FINANCIAL METRICS:
- Market Cap: {metrics.get('market_cap', 'N/A')}
- Enterprise Value: {metrics.get('enterprise_value', 'N/A')}
- P/E Ratio: {metrics.get('trailing_pe', 'N/A')}
- Debt-to-Equity: {metrics.get('debt_to_equity', 'N/A')}
- Return on Assets: {metrics.get('return_on_assets', 'N/A')}
- Return on Equity: {metrics.get('return_on_equity', 'N/A')}
- Profit Margins: {metrics.get('profit_margins', 'N/A')}
- Beta (Volatility): {metrics.get('beta', 'N/A')}
- Total Cash: {metrics.get('total_cash', 'N/A')}
- Total Revenue: {metrics.get('total_revenue', 'N/A')}
- EBITDA: {metrics.get('ebitda', 'N/A')}

Please provide insights on:
1. Financial health and stability
2. Valuation metrics and ratios
3. Risk factors and concerns
4. Competitive positioning
5. Investment attractiveness

Format as a clear, professional analysis suitable for business decision-making.
"""
        
        insights = await generate_text(prompt, max_tokens=512)
        return insights.strip()
        
    except Exception as e:
        logger.error(f"Failed to generate financial insights for {ticker}: {e}")
        return f"Financial insights generation failed for {company_name} ({ticker}): {str(e)}"


async def generate_risk_assessment_summary(
    financial_data: Dict[str, Any],
    news_data: List[Dict[str, Any]],
    risk_level: str,
    company_name: str,
    ticker: str
) -> str:
    """
    Generate a focused risk assessment summary.
    
    Args:
        financial_data: Financial metrics and data
        news_data: News headlines with sentiment
        risk_level: Calculated risk level (Green/Orange/Red)
        company_name: Company name
        ticker: Stock ticker symbol
    
    Returns:
        Generated risk assessment text
    """
    try:
        # Count news by sentiment
        red_count = sum(1 for n in news_data if n.get("sentiment") == "Red")
        orange_count = sum(1 for n in news_data if n.get("sentiment") == "Orange")
        
        # Key risk factors
        debt_equity = financial_data.get("debtToEquity")
        profit_margins = financial_data.get("profitMargins")
        beta = financial_data.get("beta")
        
        prompt = f"""
RISK ASSESSMENT SUMMARY for {company_name} ({ticker})

OVERALL RISK LEVEL: {risk_level}

KEY RISK FACTORS:
- Debt-to-Equity Ratio: {debt_equity}
- Profit Margins: {profit_margins}
- Beta (Volatility): {beta}
- High-Risk News Items: {red_count}
- Medium-Risk News Items: {orange_count}

RECENT HIGH-RISK NEWS:
{chr(10).join([f"- {n.get('headline', 'N/A')}" for n in news_data if n.get('sentiment') == 'Red'][:3])}

Provide a concise risk assessment that:
1. Explains the {risk_level} risk rating
2. Identifies primary risk drivers
3. Highlights any emerging concerns
4. Suggests risk mitigation strategies

Focus on factors relevant to insurance and investment decision-making.
"""
        
        assessment = await generate_text(prompt, max_tokens=400)
        return assessment.strip()
        
    except Exception as e:
        logger.error(f"Failed to generate risk assessment for {ticker}: {e}")
        return f"Risk assessment generation failed for {company_name} ({ticker}): {str(e)}"
