#!/usr/bin/env python3
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
    
    async def search(self, query: str, start_date: str = None, end_date: str = None, 
                    days_back: int = None, max_results: int = 10) -> Dict[str, Any]:
        
        # ADD THESE DEBUG LINES
        print(f"\n=== GOOGLE AGENT DEBUG ===")
        print(f"Query: {query}")
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        print(f"Days back: {days_back}")
        print(f"Max results: {max_results}")
        print(f"API Key present: {bool(self.api_key)}")
        print(f"Search Engine ID: {self.search_engine_id}")
        print(f"=========================\n")
        
        if not self.api_key or not self.search_engine_id:
            return self._create_disabled_response(query)
        
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        try:
            # CRITICAL FIX: Smart date handling to avoid generic results
            use_date_filter = False
            date_filter = None
            
            # Handle date range logic with intelligence
            if days_back and not start_date:
                # Use days_back parameter
                if days_back <= 30:
                    # Good range for Google Custom Search
                    date_filter = f"d{days_back}"
                    use_date_filter = True
                    logger.info(f"Using days_back filter: {date_filter}")
                else:
                    # Too long - don't use date filter for better results
                    logger.info(f"days_back too long ({days_back}), searching without date filter")
                    use_date_filter = False
            
            elif start_date and end_date:
                # Custom date range
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days_diff = (end - start).days
                
                if days_diff <= 30:
                    # Good range
                    date_filter = self._create_date_filter(start_date, end_date)
                    use_date_filter = True
                    logger.info(f"Using custom date filter: {date_filter}")
                else:
                    # CRITICAL FIX: Don't use date filter for long ranges
                    logger.info(f"Date range too long ({days_diff} days), searching without date filter for better results")
                    use_date_filter = False
            
            logger.info(f"Google News search: {query}")
            
            # Use the EXACT same parameters as your working standalone version
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": f"{query} site:news.google.com",  # Exact match to standalone
                "num": min(max_results, 10),  # Google CSE max per request
                "gl": "es",  # Spain - exact match to standalone
                "hl": "es",  # Spanish language - exact match to standalone
                "safe": "medium"  # Exact match to standalone
            }

            print(f"Final API params: {params}")
            
            # CRITICAL: Only add date filter if it's reasonable (<=30 days)
            if use_date_filter and date_filter:
                params["dateRestrict"] = date_filter
                logger.info(f"Date filter applied: {date_filter}")
            else:
                logger.info(f"No date filter applied - searching all dates (like working debug test)")
            
            # DEBUG: Log the exact API call being made
            logger.info(f"API URL: {self.base_url}")
            logger.info(f"API Params: {params}")
            
            # Make API request (exact match to standalone)
            async with self.session.get(self.base_url, params=params) as response:
                logger.info(f"API Response Status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google CSE HTTP Error {response.status}: {error_text}")
                    return self._create_error_response(query, f"HTTP {response.status}: {error_text}")
                
                data = await response.json()

                print(f"Raw API response total results: {data.get('searchInformation', {}).get('totalResults', 0)}")
                print(f"Raw API response items count: {len(data.get('items', []))}")
                if data.get('items'):
                    first_item = data.get('items', [])[0]
                    print(f"First item title: {first_item.get('title', 'No title')}")
                    print(f"First item URL: {first_item.get('link', 'No URL')}")
                
                # Check for API errors (exact match to standalone)
                if "error" in data:
                    error_details = data["error"]
                    error_msg = error_details.get("message", "Unknown API error")
                    error_code = error_details.get("code", "Unknown")
                    logger.error(f"Google CSE API Error {error_code}: {error_msg}")
                    return self._create_error_response(query, f"API Error {error_code}: {error_msg}")
                
                # Process successful response (exact match to standalone)
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
                
                # Filter results by date if no date filter was applied but dates were requested
                if not use_date_filter and (start_date or days_back):
                    original_count = len(results)
                    results = self._filter_results_by_date(results, start_date, end_date, days_back)
                    logger.info(f"Post-search date filtering: {original_count} -> {len(results)} results")
                
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
                    "raw_api_response": data  # Include raw response for debugging
                }
                
        except Exception as e:
            logger.error(f"Google News search failed: {str(e)}")
            return self._create_error_response(query, str(e))
    
    def _convert_to_bhsi_format(self, item: Dict, index: int) -> Optional[Dict]:
        """
        Convert that matches standalone processing
        """
        try:
            logger.info(f"Processing result {index}: {item.get('title', 'No title')[:50]}...")
            
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
            logger.warning(f"Error converting Google result {index}: {e}")
            return None
    
    def _extract_published_date(self, item: Dict) -> Optional[str]:
        """Extract publication date from Google CSE result (exact match to standalone)"""
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
                        for date_field in ["article:published_time", "datePublished", "publishedDate", "og:article:published_time"]:
                            if date_field in meta and meta[date_field]:
                                return self._standardize_date(meta[date_field])
        except Exception as e:
            logger.debug(f"Error extracting date: {e}")
        
        return None
    
    def _standardize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD (exact match to standalone)"""
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
        """Extract source/publisher information (exact match to standalone)"""
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
        """Create Google CSE date filter with IMPROVED logic"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days_diff = (end - start).days
            
            logger.info(f"Date range: {start_date} to {end_date} ({days_diff} days)")
            
            # CRITICAL FIX: Don't use date filters for long ranges
            if days_diff > 180:  # More than 6 months
                logger.warning(f"Date range too long ({days_diff} days), returning None for no date filter")
                return None
            
            # Optimize date filter selection
            if days_diff <= 1:
                filter_val = "d1"
            elif days_diff <= 7:
                filter_val = f"d{days_diff}"
            elif days_diff <= 30:
                filter_val = f"d{days_diff}"
            elif days_diff <= 90:
                # Use weeks for 1-3 month ranges
                weeks = max(1, days_diff // 7)
                filter_val = f"w{weeks}"
            else:
                # For 3-6 month ranges, use months but cap at 6
                months = min(6, max(1, days_diff // 30))
                filter_val = f"m{months}"
            
            logger.info(f"Applied date filter: {filter_val}")
            return filter_val
            
        except Exception as e:
            logger.warning(f"Error creating date filter: {e}")
            # FALLBACK: Use last 7 days if date parsing fails
            logger.info("Fallback: Using last 7 days")
            return "d7"
    
    def _filter_results_by_date(self, results: List[Dict], start_date: str = None, 
                              end_date: str = None, days_back: int = None) -> List[Dict]:
        """
        Filter results by date when no API date filter was applied
        """
        if not (start_date or days_back):
            return results
        
        try:
            filtered_results = []
            
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
            else:
                cutoff_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
            
            for result in results:
                result_date_str = result.get("date")
                if not result_date_str:
                    # Include results without dates
                    filtered_results.append(result)
                    continue
                
                try:
                    # Parse result date
                    if "T" in result_date_str:
                        result_date = datetime.fromisoformat(result_date_str.replace("Z", ""))
                    else:
                        result_date = datetime.strptime(result_date_str, "%Y-%m-%d")
                    
                    # Check if within date range
                    if cutoff_date and result_date >= cutoff_date and result_date <= end_date_obj:
                        filtered_results.append(result)
                    elif not cutoff_date:
                        filtered_results.append(result)
                        
                except Exception as e:
                    # Include results with date parsing errors
                    logger.debug(f"Date parsing error for result: {e}")
                    filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            logger.warning(f"Error filtering results by date: {e}")
            return results
    
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
        """Create standardized error response (exact match to standalone)"""
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
        """Basic HTML text extraction (exact match to standalone)"""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length for classification
        return text[:5000] if text else ""