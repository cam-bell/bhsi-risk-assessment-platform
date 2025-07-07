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
        Comprehensive mapping of company names to ticker symbols
        Includes major global companies, automotive, tech, finance, and Spanish companies
        """
        return {
            # === TECHNOLOGY GIANTS ===
            "tesla": "TSLA",
            "tesla motors": "TSLA",
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "meta": "META",
            "facebook": "META",
            "netflix": "NFLX",
            "nvidia": "NVDA",
            "intel": "INTC",
            "oracle": "ORCL",
            "salesforce": "CRM",
            "adobe": "ADBE",
            "ibm": "IBM",
            "cisco": "CSCO",
            "qualcomm": "QCOM",
            "broadcom": "AVGO",
            "advanced micro devices": "AMD",
            "amd": "AMD",
            
            # === AUTOMOTIVE COMPANIES ===
            "ford": "F",
            "ford motor": "F",
            "general motors": "GM",
            "gm": "GM",
            "toyota": "TM",
            "toyota motor": "TM",
            "volkswagen": "VWAGY",
            "bmw": "BMWYY",
            "mercedes": "DDAIF",
            "mercedes benz": "DDAIF",
            "daimler": "DDAIF",
            "ferrari": "RACE",
            "porsche": "POAHY",
            "stellantis": "STLA",
            "nissan": "NSANY",
            "honda": "HMC",
            "hyundai": "HYMTF",
            "lucid": "LCID",
            "lucid motors": "LCID",
            "rivian": "RIVN",
            "nio": "NIO",
            "xpeng": "XPEV",
            "li auto": "LI",
            
            # === FINANCIAL SERVICES ===
            "jpmorgan": "JPM",
            "jp morgan": "JPM",
            "jpmorgan chase": "JPM",
            "bank of america": "BAC",
            "wells fargo": "WFC",
            "goldman sachs": "GS",
            "morgan stanley": "MS",
            "american express": "AXP",
            "citigroup": "C",
            "visa": "V",
            "mastercard": "MA",
            "paypal": "PYPL",
            "berkshire hathaway": "BRK-A",
            "berkshire": "BRK-A",
            
            # === AIRLINES & LOGISTICS ===
            "dhl": "DPSGY",
            "deutsche post": "DPSGY",
            "fedex": "FDX",
            "ups": "UPS",
            "american airlines": "AAL",
            "delta": "DAL",
            "delta air lines": "DAL",
            "united airlines": "UAL",
            "southwest": "LUV",
            "southwest airlines": "LUV",
            "lufthansa": "DLAKY",
            "boeing": "BA",
            "airbus": "EADSY",
            
            # === ENERGY & OIL ===
            "exxon": "XOM",
            "exxon mobil": "XOM",
            "chevron": "CVX",
            "shell": "SHEL",
            "royal dutch shell": "SHEL",
            "bp": "BP",
            "british petroleum": "BP",
            "totalenergies": "TTE",
            "conocophillips": "COP",
            "schlumberger": "SLB",
            "halliburton": "HAL",
            
            # === HEALTHCARE & PHARMA ===
            "johnson & johnson": "JNJ",
            "jnj": "JNJ",
            "pfizer": "PFE",
            "moderna": "MRNA",
            "abbott": "ABT",
            "merck": "MRK",
            "bristol myers": "BMY",
            "bristol myers squibb": "BMY",
            "eli lilly": "LLY",
            "novartis": "NVS",
            "roche": "RHHBY",
            "astrazeneca": "AZN",
            "glaxosmithkline": "GSK",
            "gsk": "GSK",
            
            # === CONSUMER GOODS & RETAIL ===
            "coca cola": "KO",
            "cocacola": "KO",
            "pepsi": "PEP",
            "pepsico": "PEP",
            "procter gamble": "PG",
            "pg": "PG",
            "unilever": "UL",
            "nestle": "NSRGY",
            "walmart": "WMT",
            "amazon": "AMZN",
            "target": "TGT",
            "costco": "COST",
            "home depot": "HD",
            "mcdonalds": "MCD",
            "starbucks": "SBUX",
            "nike": "NKE",
            "adidas": "ADDYY",
            
            # === TELECOMMUNICATIONS ===
            "verizon": "VZ",
            "at&t": "T",
            "att": "T",
            "vodafone": "VOD",
            "deutsche telekom": "DTEGY",
            "orange": "ORAN",
            "comcast": "CMCSA",
            "charter": "CHTR",
            
            # === ENTERTAINMENT & MEDIA ===
            "disney": "DIS",
            "walt disney": "DIS",
            "warner bros": "WBD",
            "discovery": "WBD",
            "paramount": "PARA",
            "sony": "SONY",
            "nintendo": "NTDOY",
            
            # === SEMICONDUCTORS ===
            "nvidia": "NVDA",
            "intel": "INTC",
            "amd": "AMD",
            "advanced micro devices": "AMD",
            "qualcomm": "QCOM",
            "broadcom": "AVGO",
            "taiwan semiconductor": "TSM",
            "tsmc": "TSM",
            "micron": "MU",
            "micron technology": "MU",
            "applied materials": "AMAT",
            
            # === INDUSTRIAL & AEROSPACE ===
            "caterpillar": "CAT",
            "boeing": "BA",
            "lockheed martin": "LMT",
            "raytheon": "RTX",
            "general electric": "GE",
            "ge": "GE",
            "honeywell": "HON",
            "3m": "MMM",
            
            # === REAL ESTATE & REITS ===
            "american tower": "AMT",
            "prologis": "PLD",
            "crown castle": "CCI",
            
            # === SPANISH COMPANIES ===
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
        Dynamically search for ticker symbol using multiple strategies
        Updated to handle international companies with better fallbacks
        """
        try:
            # Try direct ticker creation first (most reliable approach)
            potential_tickers = [
                company_name.upper(),  # Exact match
                company_name.upper().replace(" ", ""),  # Remove spaces
            ]
            
            # Add common ticker variations for known companies
            name_lower = company_name.lower()
            ticker_variations = {
                "tesla": ["TSLA"],
                "tesla motors": ["TSLA"], 
                "apple": ["AAPL"],
                "microsoft": ["MSFT"],
                "google": ["GOOGL", "GOOG"],
                "alphabet": ["GOOGL", "GOOG"],
                "amazon": ["AMZN"],
                "meta": ["META"],
                "facebook": ["META"],
                "netflix": ["NFLX"],
                "nvidia": ["NVDA"],
                "mercedes": ["DDAIF", "MBG.DE"],
                "mercedes benz": ["DDAIF", "MBG.DE"],
                "ferrari": ["RACE"],
                "bmw": ["BMWYY", "BMW.DE"],
                "volkswagen": ["VWAGY", "VOW.DE"],
                "toyota": ["TM", "7203.T"],
                "ford": ["F"],
                "general motors": ["GM"],
                "dhl": ["DPSGY", "DPW.DE"],
                "deutsche post": ["DPSGY", "DPW.DE"],
                "boeing": ["BA"],
                "airbus": ["EADSY", "AIR.PA"],
                "coca cola": ["KO"],
                "pepsi": ["PEP"],
                "mcdonalds": ["MCD"],
                "walmart": ["WMT"],
                "disney": ["DIS"],
                "nike": ["NKE"],
                "visa": ["V"],
                "mastercard": ["MA"],
                "johnson & johnson": ["JNJ"],
                "pfizer": ["PFE"],
                "exxon": ["XOM"],
                "chevron": ["CVX"],
                "shell": ["SHEL"],
                "bp": ["BP"],
                # Spanish companies
                "santander": ["SAN"],
                "banco santander": ["SAN"],
                "bbva": ["BBVA"],
                "telefonica": ["TEF"],
                "iberdrola": ["IBE"],
                "repsol": ["REP"],
                "inditex": ["IDEXY", "ITX.MC"],
            }
            
            for key, tickers in ticker_variations.items():
                if key in name_lower:
                    potential_tickers.extend(tickers)
            
            # Test each potential ticker
            for ticker_symbol in potential_tickers:
                try:
                    ticker_obj = yf.Ticker(ticker_symbol)
                    info = ticker_obj.info
                    
                    # Check if this is a valid stock with basic info
                    if info and (info.get("longName") or info.get("marketCap") or info.get("regularMarketPrice")):
                        logger.info(f"Found valid ticker {ticker_symbol} for {company_name}")
                        return ticker_symbol
                        
                except Exception as e:
                    continue
            
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

        # 2. Try direct mapping (case-insensitive, normalized) - improved matching
        ticker_mapping = self._get_expanded_ticker_mapping()
        company_normalized = company_name_or_ticker.strip().lower()
        
        # First try exact matches
        for key, ticker in ticker_mapping.items():
            if company_normalized == key:
                logger.debug(f"Exact match '{company_normalized}' to '{key}' -> {ticker}")
                return ticker
        
        # Then try partial matches (both ways)
        for key, ticker in ticker_mapping.items():
            if (key in company_normalized or company_normalized in key) and len(company_normalized) >= 3:
                logger.debug(f"Partial match '{company_normalized}' to '{key}' -> {ticker}")
                return ticker

        # 3. Fuzzy matching
        fuzzy_match = self._fuzzy_match_company_name(company_name_or_ticker)
        if fuzzy_match:
            logger.debug(f"Fuzzy matched '{company_name_or_ticker}' to '{fuzzy_match}'")
            return fuzzy_match

        # 4. Dynamic search - use simple implementation to avoid async issues
        try:
            # Try some common variations first
            variations = [
                company_name_or_ticker.upper(),
                company_name_or_ticker.upper().replace(" ", ""),
                company_name_or_ticker.upper().replace(" ", "-"),
            ]
            
            for variation in variations:
                try:
                    ticker_obj = yf.Ticker(variation)
                    info = ticker_obj.info
                    if info and (info.get("longName") or info.get("marketCap") or info.get("regularMarketPrice")):
                        logger.debug(f"Found ticker {variation} for {company_name_or_ticker}")
                        return variation
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"Ticker variation search failed for '{company_name_or_ticker}': {e}")

        logger.debug(f"No ticker found for '{company_name_or_ticker}'")
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
        Provides fallback data when information is not available.
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
            
            # Get company name fallbacks
            company_name = (
                info.get("longName") or 
                info.get("shortName") or
                info.get("displayName") or
                ticker
            )
            
            # Build comprehensive data with fallbacks
            raw_data = {
                "longName": company_name,
                "shortName": info.get("shortName", ticker),
                "ticker": ticker,
                "country": info.get("country", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
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
                "currentPrice": info.get("regularMarketPrice") or info.get("previousClose"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "Unknown"),
                "website": info.get("website"),
                "business_summary": info.get("longBusinessSummary", f"No business summary available for {company_name}."),
                "financials": safe_to_dict(stock.financials),
                "balance_sheet": safe_to_dict(stock.balance_sheet),
                "cashflow": safe_to_dict(stock.cashflow),
                "recommendations": safe_to_dict(stock.recommendations),
            }
            
            # Add data availability flags for frontend
            raw_data["data_availability"] = {
                "has_financial_data": bool(raw_data["marketCap"] or raw_data["totalRevenue"]),
                "has_detailed_financials": bool(raw_data["financials"]),
                "has_balance_sheet": bool(raw_data["balance_sheet"]),
                "has_cashflow": bool(raw_data["cashflow"]),
                "has_recommendations": bool(raw_data["recommendations"]),
                "data_completeness": self._calculate_data_completeness(raw_data)
            }
            
            # If no financial data is available, provide estimated/placeholder data
            if not raw_data["data_availability"]["has_financial_data"]:
                raw_data["data_note"] = f"Limited financial data available for {company_name}. This may be due to the company being private, unlisted, or having restricted data access."
                
            # Clean data for JSON serialization before returning
            return self._clean_for_json(raw_data)
            
        except Exception as e:
            logger.error(f"Failed to fetch company financial data for {ticker}: {e}")
            # Return structured error with fallback company info
            return {
                "error": str(e),
                "ticker": ticker,
                "longName": ticker,
                "shortName": ticker,
                "data_note": f"Unable to fetch financial data for {ticker}. The company may not be publicly traded or the ticker symbol may be incorrect.",
                "data_availability": {
                    "has_financial_data": False,
                    "has_detailed_financials": False,
                    "has_balance_sheet": False,
                    "has_cashflow": False,
                    "has_recommendations": False,
                    "data_completeness": 0
                }
            }
    
    def _calculate_data_completeness(self, data: dict) -> float:
        """Calculate completeness score as percentage"""
        key_fields = ["marketCap", "totalRevenue", "debtToEquity", "profitMargins", "beta"]
        available_fields = sum(1 for field in key_fields if data.get(field) is not None)
        return round((available_fields / len(key_fields)) * 100, 1)

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