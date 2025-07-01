import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.agents.search.base_agent import BaseSearchAgent
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class GoogleNewsSearchAgent(BaseSearchAgent):
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not configured - Google search will be disabled")
        if not self.search_engine_id:
            logger.warning("GOOGLE_SEARCH_ENGINE_ID not configured - Google search will be disabled")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await super().__aenter__()  # Call parent's context manager
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await super().__aexit__(exc_type, exc_val, exc_tb) 
    
    async def search(self, query: str, start_date: str = None, end_date: str = None, 
                    days_back: int = None, max_results: int = 10) -> Dict[str, Any]:
        
        # Validate dates to prevent crashes
        def validate_date(date_str):
            if not date_str or date_str == "string":
                return None
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}, ignoring")
                return None
        
        # Clean the dates
        start_date = validate_date(start_date)
        end_date = validate_date(end_date)
        
        if not self.api_key or not self.search_engine_id:
            return self._create_disabled_response(query)
        
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        try:
            # Smart date handling to avoid generic results
            use_date_filter = False
            date_filter = None
            
            if days_back and not start_date:
                if days_back <= 30:
                    date_filter = f"d{days_back}"
                    use_date_filter = True
                    logger.info(f"Using days_back filter: {date_filter}")
                else:
                    logger.info(f"days_back too long ({days_back}), searching without date filter")
                    use_date_filter = False
            
            elif start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days_diff = (end - start).days
                
                if days_diff <= 30:
                    date_filter = self._create_date_filter(start_date, end_date)
                    use_date_filter = True
                    logger.info(f"Using custom date filter: {date_filter}")
                else:
                    logger.info(f"Date range too long ({days_diff} days), searching without date filter")
                    use_date_filter = False
            
            logger.info(f"Google News search: {query}")
            
            # API parameters
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": f"{query} site:news.google.com",
                "num": min(max_results, 10),
                "gl": "es",
                "hl": "es",
                "safe": "medium"
            }
            
            if use_date_filter and date_filter:
                params["dateRestrict"] = date_filter
                logger.info(f"Date filter applied: {date_filter}")
            else:
                logger.info(f"No date filter applied")
            
            # Make API request
            async with self.session.get(self.base_url, params=params) as response:
                logger.info(f"API Response Status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google CSE HTTP Error {response.status}: {error_text}")
                    return self._create_error_response(query, f"HTTP {response.status}: {error_text}")
                
                data = await response.json()
                
                if "error" in data:
                    error_details = data["error"]
                    error_msg = error_details.get("message", "Unknown API error")
                    error_code = error_details.get("code", "Unknown")
                    logger.error(f"Google CSE API Error {error_code}: {error_msg}")
                    return self._create_error_response(query, f"API Error {error_code}: {error_msg}")
                
                search_info = data.get("searchInformation", {})
                items = data.get("items", [])
                
                logger.info(f"Google News: Found {len(items)} results")
                logger.info(f"Total results available: {search_info.get('totalResults', 0)}")
                
                # Convert to BHSI format
                results = []
                for i, item in enumerate(items, 1):
                    processed_result = self._convert_to_bhsi_format(item, i)
                    if processed_result:
                        results.append(processed_result)
                
                return {
                    "search_summary": {
                        "query": query,
                        "source": "Google News",
                        "total_results": int(search_info.get("totalResults", 0)),
                        "results_returned": len(results),
                        "search_time": float(search_info.get("searchTime", 0)),
                        "date_range": f"{start_date} to {end_date}" if start_date else f"Last {days_back} days" if days_back else "No date filter",
                        "date_filter_applied": use_date_filter,
                        "errors": []
                    },
                    "results": results,
                    "raw_api_response": data
                }
                
        except Exception as e:
            logger.error(f"Google News search failed: {str(e)}")
            return self._create_error_response(query, str(e))
    
    def _convert_to_bhsi_format(self, item: Dict, index: int) -> Optional[Dict]:
        try:
            logger.info(f"Processing result {index}: {item.get('title', 'No title')[:50]}...")
            
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            url = item.get("link", "")
            
            source_info = self._extract_source_info(item)
            published_date = self._extract_published_date(item)
            
            result = {
                "source": "Google News",
                "date": published_date or datetime.now().strftime("%Y-%m-%d"),
                "title": title,
                "summary": snippet,
                "url": url,
                "text": f"{title} {snippet}",
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("formattedUrl", ""),
                "publisher": source_info.get("publisher", ""),
                "news_source": source_info.get("source", "Unknown"),
                "search_timestamp": datetime.now().isoformat(),
                "raw_google_data": item
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Error converting Google result {index}: {e}")
            return None
    
    def _extract_published_date(self, item: Dict) -> Optional[str]:
        try:
            if "pagemap" in item:
                pagemap = item["pagemap"]
                
                for data_type in ["newsarticle", "article", "webpage"]:
                    if data_type in pagemap:
                        for entry in pagemap[data_type]:
                            for date_field in ["datepublished", "datePublished", "publishdate"]:
                                if date_field in entry and entry[date_field]:
                                    return self._standardize_date(entry[date_field])
                
                if "metatags" in pagemap:
                    for meta in pagemap["metatags"]:
                        for date_field in ["article:published_time", "datePublished", "publishedDate", "og:article:published_time"]:
                            if date_field in meta and meta[date_field]:
                                return self._standardize_date(meta[date_field])
        except Exception as e:
            logger.debug(f"Error extracting date: {e}")
        
        return None
    
    def _standardize_date(self, date_str: str) -> str:
        try:
            if "T" in date_str:
                return date_str.split("T")[0]
            
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(date_str[:10], fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_source_info(self, item: Dict) -> Dict:
        source_info = {
            "source": "Unknown",
            "publisher": "",
        }
        
        try:
            display_link = item.get("displayLink", "")
            if display_link:
                source_info["source"] = display_link
            
            if "pagemap" in item:
                pagemap = item["pagemap"]
                
                if "metatags" in pagemap:
                    for meta in pagemap["metatags"]:
                        for pub_field in ["og:site_name", "publisher", "article:publisher"]:
                            if pub_field in meta and meta[pub_field]:
                                source_info["publisher"] = meta[pub_field]
                                break
        except Exception as e:
            logger.debug(f"Error extracting source info: {e}")
        
        return source_info
    
    def _create_date_filter(self, start_date: str, end_date: str) -> Optional[str]:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days_diff = (end - start).days
            
            if days_diff > 180:
                return None
            
            if days_diff <= 1:
                filter_val = "d1"
            elif days_diff <= 7:
                filter_val = f"d{days_diff}"
            elif days_diff <= 30:
                filter_val = f"d{days_diff}"
            elif days_diff <= 90:
                weeks = max(1, days_diff // 7)
                filter_val = f"w{weeks}"
            else:
                months = min(6, max(1, days_diff // 30))
                filter_val = f"m{months}"
            
            return filter_val
            
        except Exception as e:
            logger.warning(f"Error creating date filter: {e}")
            return "d7"
    
    def _create_disabled_response(self, query: str) -> Dict:
        return {
            "search_summary": {
                "query": query,
                "source": "Google News",
                "total_results": 0,
                "results_returned": 0,
                "search_time": 0,
                "date_range": "N/A",
                "errors": ["Google Custom Search not configured"]
            },
            "results": []
        }
    
    def _create_error_response(self, query: str, error_message: str) -> Dict:
        return {
            "search_summary": {
                "query": query,
                "source": "Google News",
                "total_results": 0,
                "results_returned": 0,
                "search_time": 0,
                "date_range": "Error",
                "errors": [error_message]
            },
            "results": []
        }
    
    async def fetch_full_content(self, url: str) -> Optional[str]:
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._extract_text_from_html(content)
                else:
                    logger.warning(f"Failed to fetch content from {url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def _extract_text_from_html(self, html_content: str) -> str:
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000] if text else ""