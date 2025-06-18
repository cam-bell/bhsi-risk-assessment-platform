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
    """
    Google Custom Search Agent integrated with BHSI architecture
    Searches news.google.com for company information
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not configured - Google search will be disabled")
        if not self.search_engine_id:
            logger.warning("GOOGLE_SEARCH_ENGINE_ID not configured - Google search will be disabled")
    
    async def search(self, query: str, start_date: str = None, end_date: str = None, 
                    days_back: int = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Search Google News for company information
        Follows BHSI's existing agent response format
        
        Args:
            query: Company name to search for
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format) 
            days_back: Alternative to date range - search last N days
            max_results: Maximum number of results to return
        
        Returns:
            Dict following BHSI's standardized search response format
        """
        if not self.api_key or not self.search_engine_id:
            return self._create_disabled_response(query)
        
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        try:
            # Handle date range logic (matching your other agents)
            if days_back and not start_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            logger.info(f"🔍 Google News search: {query}")
            
            # Build search parameters
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": f"{query} site:news.google.com",
                "num": min(max_results, 10),  # Google CSE max per request
                "gl": "es",  # Spain
                "hl": "es",  # Spanish language
                "safe": "medium"
            }
            
            # Add date filter if specified
            if start_date and end_date:
                date_filter = self._create_date_filter(start_date, end_date)
                if date_filter:
                    params["dateRestrict"] = date_filter
                    logger.info(f"📅 Date filter applied: {date_filter}")
            
            # Make API request
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"❌ Google CSE HTTP Error {response.status}: {error_text}")
                    return self._create_error_response(query, f"HTTP {response.status}")
                
                data = await response.json()
                
                # Check for API errors
                if "error" in data:
                    error_details = data["error"]
                    error_msg = error_details.get("message", "Unknown API error")
                    error_code = error_details.get("code", "Unknown")
                    logger.error(f"❌ Google CSE API Error {error_code}: {error_msg}")
                    return self._create_error_response(query, f"API Error {error_code}: {error_msg}")
                
                # Process successful response
                search_info = data.get("searchInformation", {})
                items = data.get("items", [])
                
                logger.info(f"✅ Google News: Found {len(items)} results")
                
                # Convert to BHSI format
                results = []
                for item in items:
                    processed_result = self._convert_to_bhsi_format(item)
                    if processed_result:
                        results.append(processed_result)
                
                return {
                    "search_summary": {
                        "query": query,
                        "source": "Google News",
                        "total_results": int(search_info.get("totalResults", 0)),
                        "results_returned": len(results),
                        "search_time": float(search_info.get("searchTime", 0)),
                        "date_range": f"{start_date} to {end_date}" if start_date else "No date filter",
                        "errors": []
                    },
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"❌ Google News search failed: {str(e)}")
            return self._create_error_response(query, str(e))
    
    def _convert_to_bhsi_format(self, item: Dict) -> Optional[Dict]:
        """
        Convert Google CSE result to BHSI's standardized format
        Matches the format used by BOE and NewsAPI agents
        """
        try:
            # Extract basic information
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            url = item.get("link", "")
            
            # Extract source information
            source_info = self._extract_source_info(item)
            
            # Extract publication date
            published_date = self._extract_published_date(item)
            
            # Create BHSI-format result
            result = {
                "source": "Google News",
                "date": published_date or datetime.now().strftime("%Y-%m-%d"),
                "title": title,
                "summary": snippet,
                "url": url,
                "text": f"{title} {snippet}",  # For classification
                
                # Google-specific fields
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("formattedUrl", ""),
                "publisher": source_info.get("publisher", ""),
                "news_source": source_info.get("source", "Unknown"),
                
                # Metadata
                "search_timestamp": datetime.now().isoformat(),
                "raw_google_data": item  # Keep for debugging
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"⚠️  Error converting Google result: {e}")
            return None
    
    def _extract_published_date(self, item: Dict) -> Optional[str]:
        """Extract publication date from Google CSE result"""
        try:
            # Try pagemap structured data
            if "pagemap" in item:
                pagemap = item["pagemap"]
                
                # Check news article structured data
                for data_type in ["newsarticle", "article", "webpage"]:
                    if data_type in pagemap:
                        for entry in pagemap[data_type]:
                            for date_field in ["datepublished", "datePublished", "publishdate"]:
                                if date_field in entry and entry[date_field]:
                                    # Try to standardize date format
                                    date_str = entry[date_field]
                                    return self._standardize_date(date_str)
                
                # Check meta tags
                if "metatags" in pagemap:
                    for meta in pagemap["metatags"]:
                        for date_field in ["article:published_time", "datePublished", "publishedDate"]:
                            if date_field in meta and meta[date_field]:
                                return self._standardize_date(meta[date_field])
        except Exception as e:
            logger.debug(f"Error extracting date: {e}")
        
        return None
    
    def _standardize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD"""
        try:
            # Handle ISO format (most common)
            if "T" in date_str:
                return date_str.split("T")[0]
            
            # Handle other common formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(date_str[:10], fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            
            # If all else fails, return today's date
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_source_info(self, item: Dict) -> Dict:
        """Extract source/publisher information"""
        source_info = {
            "source": "Unknown",
            "publisher": "",
        }
        
        try:
            # Get source from display link
            display_link = item.get("displayLink", "")
            if display_link:
                source_info["source"] = display_link
            
            # Try pagemap for better source info
            if "pagemap" in item:
                pagemap = item["pagemap"]
                
                if "metatags" in pagemap:
                    for meta in pagemap["metatags"]:
                        # Look for publisher info
                        for pub_field in ["og:site_name", "publisher", "article:publisher"]:
                            if pub_field in meta and meta[pub_field]:
                                source_info["publisher"] = meta[pub_field]
                                break
        except Exception as e:
            logger.debug(f"Error extracting source info: {e}")
        
        return source_info
    
    def _create_date_filter(self, start_date: str, end_date: str) -> Optional[str]:
        """Create Google CSE date filter"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days_diff = (end - start).days
            
            if days_diff <= 1:
                return "d1"
            elif days_diff <= 7:
                return f"d{days_diff}"
            elif days_diff <= 30:
                weeks = max(1, days_diff // 7)
                return f"w{weeks}"
            elif days_diff <= 365:
                months = max(1, days_diff // 30)
                return f"m{months}"
            else:
                years = max(1, days_diff // 365)
                return f"y{years}"
                
        except Exception as e:
            logger.warning(f"Error creating date filter: {e}")
            return None
    
    def _create_disabled_response(self, query: str) -> Dict:
        """Response when Google search is disabled due to missing config"""
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
        """Create standardized error response"""
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
        """
        Fetch full article content from URL
        Additional utility method for content analysis
        """
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
        """Basic HTML text extraction"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length for classification
        return text[:5000] if text else ""