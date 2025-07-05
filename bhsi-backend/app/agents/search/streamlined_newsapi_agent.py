#!/usr/bin/env python3
"""
Streamlined NewsAPI Agent - Fast data fetching only, no classification during search
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from app.agents.search.base_agent import BaseSearchAgent
from app.core.config import settings
import ssl

logger = logging.getLogger(__name__)


class StreamlinedNewsAPIAgent(BaseSearchAgent):
    """Ultra-fast NewsAPI search - fetches data only, classification happens later"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.headers = {"X-Api-Key": self.api_key}
        self.max_days_back = 30
        
    def _adjust_date_range(self, start_date: Optional[str], end_date: Optional[str], days_back: Optional[int]) -> tuple[str, str]:
        """Adjust date range for NewsAPI 30-day limit"""
        today = datetime.now()
        min_start = today - timedelta(days=self.max_days_back)
        
        if not start_date and not end_date:
            end_dt = today
            start_dt = today - timedelta(days=days_back or 7)
        else:
            # Parse end_date
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    if end_dt > today:
                        end_dt = today
                except Exception:
                    end_dt = today
            else:
                end_dt = today
                
            # Parse start_date
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    if start_dt < min_start:
                        start_dt = min_start
                        logger.warning(f"Start date adjusted to {start_dt.strftime('%Y-%m-%d')} due to NewsAPI 30-day limit")
                except Exception:
                    start_dt = min_start
            else:
                start_dt = min_start
                
            # Ensure start_dt is not after end_dt
            if start_dt > end_dt:
                start_dt = end_dt - timedelta(days=1)
                if start_dt < min_start:
                    start_dt = min_start
                    
        return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")

    async def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = 7,
        page_size: int = 20,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        FAST NewsAPI search - just fetch and return raw data
        """
        try:
            # Adjust date range for API limits
            start_date, end_date = self._adjust_date_range(start_date, end_date, days_back)
            logger.info(f"📰 NewsAPI search: '{query}' ({start_date} to {end_date})")
            
            params = {
                "q": query,
                "language": "es",
                "from": start_date,
                "to": end_date,
                "pageSize": min(page_size, 100),
                "page": page,
                "sortBy": "publishedAt"
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            # Create SSL context that doesn't verify certificates (for testing only)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(
                    f"{self.base_url}/everything",
                    params=params,
                    headers=self.headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"NewsAPI error: {error_text}")
                        return {
                            "search_summary": {
                                "query": query,
                                "date_range": f"{start_date} to {end_date}",
                                "total_results": 0,
                                "errors": [f"NewsAPI error: {error_text}"]
                            },
                            "articles": []
                        }
                    
                    data = await response.json()
                    
                    if data.get("status") != "ok":
                        logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                        return {
                            "search_summary": {
                                "query": query,
                                "date_range": f"{start_date} to {end_date}",
                                "total_results": 0,
                                "errors": [f"NewsAPI error: {data.get('message', 'Unknown error')}"]
                            },
                            "articles": []
                        }
                    
                    articles = data.get("articles", [])
                    logger.info(f"✅ NewsAPI: {len(articles)} articles")
                    
                    # Process articles without classification - just clean up the data
                    processed_articles = []
                    for article in articles:
                        processed_article = {
                            "title": article.get("title", ""),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "author": article.get("author", ""),
                            "publishedAt": article.get("publishedAt"),
                            "url": article.get("url", ""),
                            "urlToImage": article.get("urlToImage", ""),
                            "description": article.get("description", ""),
                            "content": article.get("content", "")
                        }
                        processed_articles.append(processed_article)
                    
                    return {
                        "search_summary": {
                            "query": query,
                            "date_range": f"{start_date} to {end_date}",
                            "total_results": data.get("totalResults", 0),
                            "page": page,
                            "page_size": page_size,
                            "has_more": (page * page_size) < data.get("totalResults", 0),
                            "errors": []
                        },
                        "articles": processed_articles
                    }
                    
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date or 'unknown'} to {end_date or 'unknown'}",
                    "total_results": 0,
                    "errors": [f"NewsAPI search failed: {e}"]
                },
                "articles": []
            } 