from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
from app.agents.search.base_agent import BaseSearchAgent
from app.core.config import settings
from app.agents.analysis.classifier import RiskClassifier
import logging

logger = logging.getLogger(__name__)

class NewsAPIAgent(BaseSearchAgent):
    """NewsAPI integration for Spanish news search"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.headers = {"X-Api-Key": self.api_key}
        self.classifier = RiskClassifier()
        self.max_days_back = 30
        
    def _adjust_date_range(self, start_date: Optional[str], end_date: Optional[str], days_back: Optional[int]) -> tuple[str, str]:
        today = datetime.now()
        min_start = today - timedelta(days=self.max_days_back)
        logger.info(f"Adjusting date range: start_date={start_date}, end_date={end_date}, days_back={days_back}")
        # Defensive: if both are None, use days_back or default to last 7 days
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
                except Exception:
                    start_dt = min_start
            else:
                start_dt = min_start
            # Ensure start_dt is not after end_dt
            if start_dt > end_dt:
                start_dt = end_dt - timedelta(days=1)
                if start_dt < min_start:
                    start_dt = min_start
        logger.info(f"Adjusted date range: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
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
        try:
            # Defensive date handling
            start_date, end_date = self._adjust_date_range(start_date, end_date, days_back)
            logger.info(f"NewsAPI search for '{query}' from {start_date} to {end_date}")
            params = {
                "q": query,
                "language": "es",
                "from": start_date,
                "to": end_date,
                "pageSize": min(page_size, 100),
                "page": page,
                "sortBy": "publishedAt"
            }
            logger.info(f"Making NewsAPI request with params: {params}")
            timeout = aiohttp.ClientTimeout(total=10)
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(
                        f"{self.base_url}/everything",
                        params=params,
                        headers=self.headers
                    ) as response:
                        logger.info(f"NewsAPI HTTP status: {response.status}")
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
                        logger.info(f"NewsAPI response keys: {list(data.keys())}")
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
                        logger.info(f"NewsAPI returned {len(articles)} articles")
                        processed_articles = []
                        for i, article in enumerate(articles):
                            logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('title', '')}")
                            # Re-enable LLM classification
                            content = article.get("content", "") or article.get("description", "")
                            title = article.get("title", "")
                            classification = await self.classifier.classify_text(
                                text=content,
                                title=title,
                                source="NewsAPI",
                                section=article.get("source", {}).get("name", "")
                            )
                            processed_article = {
                                "title": title,
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "published_at": article.get("publishedAt"),
                                "url": article.get("url", ""),
                                "content": content,
                                "risk_level": classification["label"],
                                "confidence": classification["confidence"],
                                "classification_reason": classification["reason"],
                                "classification_method": classification["method"]
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
                logger.error(f"NewsAPI request failed: {e}")
                return {
                    "search_summary": {
                        "query": query,
                        "date_range": f"{start_date} to {end_date}",
                        "total_results": 0,
                        "errors": [f"NewsAPI request failed: {e}"]
                    },
                    "articles": []
                }
        except Exception as e:
            logger.error(f"Error processing NewsAPI results: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date} to {end_date}",
                    "total_results": 0,
                    "errors": [f"Error processing NewsAPI results: {e}"]
                },
                "articles": []
            }
    
    async def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch full article content from URL"""
        try:
            content = await self.fetch_url(url)
            return content
        except Exception as e:
            logger.error(f"Failed to fetch article content from {url}: {e}")
            return None 