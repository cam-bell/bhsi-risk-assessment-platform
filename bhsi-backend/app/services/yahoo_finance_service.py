#!/usr/bin/env python3
"""
Streamlined Yahoo Finance Agent - Financial data analysis for risk assessment
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
from app.agents.search.base_agent import BaseSearchAgent
import re
from difflib import SequenceMatcher
import asyncio
from app.services.gemini.main import generate_text  # Import your Gemini text generation function
import math

logger = logging.getLogger(__name__)


class StreamlinedYahooFinanceAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.source = "Yahoo Finance"
        # Cache for ticker lookups to avoid repeated API calls
        self._ticker_cache = {}
        
    def _clean_for_json(self, obj):
        """
        Clean Yahoo Finance data for JSON serialization by replacing inf/nan values with None
        """
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        else:
            return obj
        
    def _get_expanded_ticker_mapping(self) -> Dict[str, str]:
        """
        Expanded mapping of Spanish company names to ticker symbols
        Includes major Spanish companies across different sectors
        """
        return {
            # Banking & Financial Services
            "santander": "SAN",
            "banco santander": "SAN",
            "banco de santander": "SAN",
            "bbva": "BBVA", 
            "banco bilbao": "BBVA",
            "banco bilbao vizcaya": "BBVA",
            "caixabank": "CABK",
            "banco sabadell": "SAB",
            "sabadell": "SAB",
            "bankinter": "BKT",
            "unicaja": "UNI",
            "ibercaja": "IBE",
            
            # Telecommunications
            "telefonica": "TEF",
            "telefónica": "TEF",
            "movistar": "TEF",
            "orange españa": "ORA",
            "vodafone españa": "VOD",
            
            # Energy & Utilities
            "iberdrola": "IBE",
            "endesa": "ELE",
            "naturgy": "NTGY",
            "gas natural": "NTGY",
            "red electrica": "REE",
            "red eléctrica": "REE",
            "enagas": "ENG",
            "acciona": "ANA",
            "acciona energia": "ANA",
            
            # Oil & Gas
            "repsol": "REP",
            "cepsa": "CEPSA",
            
            # Retail & Consumer
            "inditex": "IDEXY",
            "zara": "IDEXY",
            "mango": "MANGO",
            "el corte ingles": "ELC",
            "corte ingles": "ELC",
            "mercadona": "MERCADONA",
            "dia": "DIA",
            
            # Construction & Infrastructure
            "acs": "ACS",
            "ferrovial": "FER",
            "sacyr": "SCYR",
            "ohla": "OHLA",
            "fcc": "FCC",
            "acciona": "ANA",
            
            # Real Estate
            "merlin": "MRL",
            "merlin properties": "MRL",
            "colonial": "COL",
            "realia": "RLIA",
            "urbas": "URB",
            
            # Technology & Media
            "amadeus": "AMS",
            "indra": "IDR",
            "telefonica": "TEF",
            "mediaset": "TL5",
            "atresmedia": "A3M",
            
            # Healthcare & Pharma
            "grifols": "GRF",
            "rovi": "ROVI",
            "almirall": "ALM",
            "faes farma": "FAE",
            
            # Automotive & Transport
            "seat": "SEAT",
            "iberia": "IBLA",
            "air europa": "AEA",
            
            # Food & Beverage
            "damm": "DAMM",
            "mahou": "MAHOU",
            "estrellas galicia": "ESTRELLAS",
            
            # Industrial & Manufacturing
            "arcelormittal": "MT",
            "tubacex": "TUB",
            "sidenor": "SIDENOR",
            
            # Telecommunications Infrastructure
            "cellnex": "CLNX",
            "masmovil": "MAS",
            "mas móvil": "MAS",
            
            # Insurance
            "mapfre": "MAP",
            "mutua madrileña": "MUTUA",
            "linea directa": "LDA",
            
            # Additional major companies
            "iberostar": "IBEROSTAR",
            "melia": "MEL",
            "nh hoteles": "NH",
            "sol melia": "MEL",
            "barceló": "BAR",
            "iberostar": "IBEROSTAR",
        }
    
    def _clean_company_name(self, company_name: str) -> str:
        """
        Clean and normalize company name for better matching
        """
        # Remove common suffixes and prefixes
        suffixes_to_remove = [
            "s.a.", "sa", "s.l.", "sl", "sociedad anonima",
            "sociedad limitada", "corporation", "corp", "incorporated",
            "inc", "limited", "ltd", "company", "co", "group", "grupo",
            "holding", "holdings"
        ]
        
        prefixes_to_remove = [
            "the", "el", "la", "los", "las"
        ]
        
        # Convert to lowercase and remove extra spaces
        cleaned = company_name.lower().strip()
        
        # Remove suffixes
        for suffix in suffixes_to_remove:
            cleaned = re.sub(rf'\b{suffix}\b', '', cleaned)
        
        # Remove prefixes
        for prefix in prefixes_to_remove:
            cleaned = re.sub(rf'^{prefix}\s+', '', cleaned)
        
        # Remove extra spaces and punctuation
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _fuzzy_match_company_name(self, company_name: str, threshold: float = 0.8) -> Optional[str]:
        """
        Use fuzzy matching to find the best ticker match
        """
        cleaned_name = self._clean_company_name(company_name)
        ticker_mapping = self._get_expanded_ticker_mapping()
        
        best_match = None
        best_score = 0
        
        for key, ticker in ticker_mapping.items():
            # Exact match
            if cleaned_name == key:
                return ticker
            
            # Partial match
            if key in cleaned_name or cleaned_name in key:
                cleaned_words = set(cleaned_name.split())
                key_words = set(key.split())
                score = len(cleaned_words & key_words) / max(
                    len(cleaned_words), len(key_words)
                )
                if score > best_score:
                    best_score = score
                    best_match = ticker
            
            # Fuzzy match using SequenceMatcher
            similarity = SequenceMatcher(None, cleaned_name, key).ratio()
            if similarity > best_score:
                best_score = similarity
                best_match = ticker
        
        return best_match if best_score >= threshold else None
    
    async def _search_ticker_dynamically(self, company_name: str) -> Optional[str]:
        """
        Dynamically search for ticker symbol using yfinance search
        """
        try:
            # Use yfinance's search functionality
            search_results = yf.Tickers(company_name)
            
            # Get the first result that looks like a valid ticker
            for ticker in search_results.tickers:
                ticker_symbol = ticker.ticker
                info = ticker.info
                
                # Check if this is a valid stock with basic info
                if (info.get("regularMarketPrice") and 
                    info.get("longName") and 
                    not ticker_symbol.endswith('.TO') and  # Avoid Canadian stocks
                    not ticker_symbol.endswith('.L') and   # Avoid London stocks
                    len(ticker_symbol) <= 5):  # Most major stocks have short symbols
                    
                    # Verify it's a Spanish company by checking country or name
                    long_name = info.get("longName", "").lower()
                    country = info.get("country", "").lower()
                    
                    if ("spain" in country or 
                        "españa" in country or 
                        "madrid" in long_name or 
                        "barcelona" in long_name or
                        any(spanish_word in long_name for spanish_word in ["banco", "telefónica", "iberdrola", "repsol"])):
                        return ticker_symbol
            
            return None
            
        except Exception as e:
            logger.warning(f"Dynamic ticker search failed for '{company_name}': {e}")
            return None
    
    def _get_ticker_symbol(self, company_name_or_ticker: str) -> Optional[str]:
        """
        Enhanced ticker symbol lookup with multiple fallback strategies.
        If the input is already a valid ticker, use it directly.
        """
        # Clean input
        query = company_name_or_ticker.strip().upper()

        # 1. If the query looks like a ticker (letters, numbers, dots, up to 7 chars), use it directly
        if re.fullmatch(r"[A-Z0-9\\.]{1,7}", query):
            try:
                ticker_obj = yf.Ticker(query)
                info = ticker_obj.info
                if info and (info.get("longName") or info.get("marketCap")):
                    return query
            except Exception:
                pass

        # 2. Try direct mapping (case-insensitive, normalized)
        ticker_mapping = self._get_expanded_ticker_mapping()
        company_normalized = company_name_or_ticker.strip().lower()
        for key, ticker in ticker_mapping.items():
            if key in company_normalized:
                print(f"[DEBUG] Matched '{company_normalized}' to '{key}' -> {ticker}")
                return ticker

        # 3. Fuzzy matching
        fuzzy_match = self._fuzzy_match_company_name(company_name_or_ticker)
        if fuzzy_match:
            print(f"[DEBUG] Fuzzy matched '{company_name_or_ticker}' to '{fuzzy_match}'")
            return fuzzy_match

        # 4. Dynamic search (async, run synchronously here)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            dynamic_match = loop.run_until_complete(self._search_ticker_dynamically(company_name_or_ticker))
            loop.close()
            if dynamic_match:
                print(f"[DEBUG] Dynamically matched '{company_name_or_ticker}' to '{dynamic_match}'")
                return dynamic_match
        except Exception:
            pass

        print(f"[DEBUG] No ticker found for '{company_name_or_ticker}'")
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

    def get_company_financial_data(self, ticker: str) -> dict:
        """
        Fetches comprehensive financial data for a company using yfinance.
        Returns a dictionary with info, financials, balance sheet, cashflow, and recommendations.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            # Convert DataFrames to dicts if possible
            def safe_to_dict(df):
                try:
                    return df.to_dict() if hasattr(df, 'to_dict') else {}
                except Exception:
                    return {}
            
            raw_data = {
                "longName": info.get("longName"),
                "country": info.get("country"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": info.get("marketCap"),
                "totalRevenue": info.get("totalRevenue"),
                "ebitda": info.get("ebitda"),
                "debtToEquity": info.get("debtToEquity"),
                "returnOnAssets": info.get("returnOnAssets"),
                "returnOnEquity": info.get("returnOnEquity"),
                "profitMargins": info.get("profitMargins"),
                "beta": info.get("beta"),
                "enterpriseValue": info.get("enterpriseValue"),
                "trailingPE": info.get("trailingPE"),
                "totalCash": info.get("totalCash"),
                "financials": safe_to_dict(stock.financials),
                "balance_sheet": safe_to_dict(stock.balance_sheet),
                "cashflow": safe_to_dict(stock.cashflow),
                "recommendations": safe_to_dict(stock.recommendations),
            }
            
            # Clean data for JSON serialization before returning
            return self._clean_for_json(raw_data)
            
        except Exception as e:
            logger.error(f"Failed to fetch company financial data for {ticker}: {e}")
            return {"error": str(e)}

    # --- Gemini-powered ticker lookup with hybrid fallback ---
    async def get_ticker_symbol_llm(self, company_name: str) -> str:
        """
        Use Gemini LLM to resolve a company name to its primary stock ticker symbol.
        Falls back to the existing logic if Gemini fails or returns an invalid ticker.
        """
        prompt = (
            f"Given the company name '{company_name}', return the primary stock ticker symbol "
            "for this company (preferably from the Madrid or NYSE exchanges). Only return the ticker symbol."
        )
        try:
            ticker = await generate_text(prompt, max_tokens=10)
            ticker = ticker.strip().upper()
            if re.match(r'^[A-Z0-9.]{1,7}$', ticker):
                return ticker
        except Exception:
            pass
        # Fallback to existing logic
        return self._get_ticker_symbol(company_name)

    # Example usage in your class:
    # ticker = await self.get_ticker_symbol_llm(company_name) 