#!/usr/bin/env python3
"""
Streamlined Yahoo Finance Agent - Financial data analysis for risk assessment
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yfinance as yf
from app.agents.search.base_agent import BaseSearchAgent

logger = logging.getLogger(__name__)

class StreamlinedYahooFinanceAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.source = "Yahoo Finance"
        
    def _get_ticker_symbol(self, company_name: str) -> Optional[str]:
        """
        Convert company name to ticker symbol
        Common Spanish companies and their tickers
        """
        # Common Spanish company tickers
        ticker_mapping = {
            "santander": "SAN",
            "banco santander": "SAN", 
            "bbva": "BBVA",
            "banco bilbao": "BBVA",
            "telefonica": "TEF",
            "iberdrola": "IBE",
            "repsol": "REP",
            "inditex": "IDEXY",
            "ferrovial": "FER",
            "acs": "ACS",
            "caixabank": "CABK",
            "sabadell": "SAB",
            "mapfre": "MAP",
            "endesa": "ELE",
            "naturgy": "NTGY",
            "red electrica": "REE",
            "enagas": "ENG",
            "cellnex": "CLNX",
            "grifols": "GRF",
            "merlin": "MRL"
        }
        
        company_lower = company_name.lower()
        for key, ticker in ticker_mapping.items():
            if key in company_lower:
                return ticker
        return None

    def _analyze_stock_data(self, stock: yf.Ticker, company_name: str) -> Dict[str, Any]:
        """Analyze stock data for risk indicators"""
        try:
            info = stock.info
            
            # Basic stock info
            stock_data = {
                "company_name": company_name,
                "ticker": info.get("symbol"),
                "current_price": info.get("regularMarketPrice"),
                "currency": info.get("currency"),
                "market_cap": info.get("marketCap"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "dividend_yield": info.get("dividendYield"),
                "forward_pe": info.get("forwardPE"),
                "website": info.get("website"),
                "risk_indicators": []
            }
            
            # Share price drop analysis (7-day)
            today = datetime.today().date()
            last_week = today - timedelta(days=7)
            hist = stock.history(start=str(last_week), end=str(today))
            
            if not hist.empty:
                latest_close = hist['Close'].iloc[-1]
                week_ago_close = hist['Close'].iloc[0]
                drop_pct = ((week_ago_close - latest_close) / week_ago_close) * 100
                
                stock_data["price_change_7d"] = {
                    "from": week_ago_close,
                    "to": latest_close,
                    "percentage": drop_pct
                }
                
                if drop_pct > 5:
                    stock_data["risk_indicators"].append({
                        "type": "share_price_drop",
                        "severity": "high" if drop_pct > 10 else "medium",
                        "description": f"Significant share price drop: {drop_pct:.2f}% in 7 days",
                        "value": drop_pct
                    })
            
            # Revenue trend analysis
            try:
                income_stmt = stock.financials
                if not income_stmt.empty and "Total Revenue" in income_stmt.index:
                    revenue = income_stmt.loc["Total Revenue"]
                    if len(revenue) >= 2:
                        rev_latest = revenue.iloc[0]
                        rev_prev = revenue.iloc[1]
                        rev_change = ((rev_latest - rev_prev) / rev_prev) * 100
                        
                        stock_data["revenue_change_yoy"] = {
                            "from": rev_prev,
                            "to": rev_latest,
                            "percentage": rev_change
                        }
                        
                        if rev_change < -10:
                            stock_data["risk_indicators"].append({
                                "type": "revenue_decline",
                                "severity": "high" if rev_change < -20 else "medium",
                                "description": f"Revenue decline year-over-year: {rev_change:.2f}%",
                                "value": rev_change
                            })
            except Exception as e:
                logger.warning(f"Error analyzing revenue data: {e}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error analyzing stock data: {e}")
            return {"error": str(e)}

    async def search(self, query: str, start_date: Optional[str] = None, end_date: Optional[str] = None, days_back: Optional[int] = 7) -> Dict[str, Any]:
        """
        Search for financial data and risk indicators for a company
        """
        try:
            logger.info(f"📊 Yahoo Finance search: '{query}'")
            
            # Get ticker symbol for the company
            ticker_symbol = self._get_ticker_symbol(query)
            if not ticker_symbol:
                return {
                    "search_summary": {
                        "query": query,
                        "source": "Yahoo Finance",
                        "total_results": 0,
                        "feeds_searched": 0,
                        "errors": ["Company ticker symbol not found"]
                    },
                    "financial_data": []
                }
            
            # Get stock data
            stock = yf.Ticker(ticker_symbol)
            financial_data = self._analyze_stock_data(stock, query)
            
            if "error" in financial_data:
                return {
                    "search_summary": {
                        "query": query,
                        "source": "Yahoo Finance", 
                        "total_results": 0,
                        "feeds_searched": 1,
                        "errors": [financial_data["error"]]
                    },
                    "financial_data": []
                }
            
            # Calculate risk score based on indicators
            risk_score = 0
            if financial_data.get("risk_indicators"):
                for indicator in financial_data["risk_indicators"]:
                    if indicator["severity"] == "high":
                        risk_score += 3
                    elif indicator["severity"] == "medium":
                        risk_score += 1
            
            financial_data["risk_score"] = risk_score
            financial_data["risk_level"] = "High" if risk_score >= 3 else "Medium" if risk_score >= 1 else "Low"
            
            logger.info(f"✅ Yahoo Finance search done: {len(financial_data.get('risk_indicators', []))} risk indicators found")
            
            return {
                "search_summary": {
                    "query": query,
                    "source": "Yahoo Finance",
                    "total_results": 1,
                    "feeds_searched": 1,
                    "errors": []
                },
                "financial_data": [financial_data]
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "source": "Yahoo Finance",
                    "total_results": 0,
                    "feeds_searched": 0,
                    "errors": [str(e)]
                },
                "financial_data": []
            } 