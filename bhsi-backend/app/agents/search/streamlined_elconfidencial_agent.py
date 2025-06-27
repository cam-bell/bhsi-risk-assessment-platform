#!/usr/bin/env python3
"""
Streamlined El Confidencial RSS Agent - Fast data fetching only, no classification
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import feedparser
from app.agents.search.base_agent import BaseSearchAgent

logger = logging.getLogger(__name__)

class StreamlinedElConfidencialAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.source = "El Confidencial"
        self.feeds = [
            {"category": "economia", "url": "https://www.elconfidencial.com/rss/economia.xml"},
            {"category": "empresas", "url": "https://www.elconfidencial.com/rss/empresas.xml"},
            {"category": "portada", "url": "https://www.elconfidencial.com/rss/espana.xml"}
        ]

    def _parse_date(self, date_str: str) -> str:
        try:
            if "T" in date_str:
                return date_str
            formats = ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.isoformat() + "Z"
                except ValueError:
                    continue
            return datetime.now().isoformat() + "Z"
        except Exception as e:
            logger.warning(f"Date parsing error for '{date_str}': {e}")
            return datetime.now().isoformat() + "Z"

    async def search(self, query: str, start_date: Optional[str] = None, end_date: Optional[str] = None, days_back: Optional[int] = 7) -> Dict[str, Any]:
        try:
            logger.info(f"📰 El Confidencial RSS search: '{query}'")
            results = []
            errors = []
            query_lower = query.lower()
            query_terms = query_lower.split()
            headers = {"User-Agent": "BHSI-Risk-Assessment/1.0", "Accept": "application/rss+xml, application/xml", "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                for feed in self.feeds:
                    try:
                        logger.debug(f"Fetching El Confidencial feed: {feed['category']}")
                        async with session.get(feed["url"]) as response:
                            if response.status == 200:
                                content = await response.text()
                                parsed_feed = feedparser.parse(content)
                                if not parsed_feed.entries:
                                    logger.warning(f"Empty feed: {feed['category']}")
                                    continue
                                for entry in parsed_feed.entries:
                                    try:
                                        title = entry.get("title", "").strip()
                                        description = entry.get("description", "").strip()
                                        link = entry.get("link", "").strip()
                                        published = entry.get("published", "")
                                        if not title or not link:
                                            continue
                                        if any(term in title.lower() or term in description.lower() for term in query_terms):
                                            result = {
                                                "title": title,
                                                "description": description,
                                                "url": link,
                                                "publishedAt": self._parse_date(published),
                                                "source": "El Confidencial",
                                                "category": feed["category"],
                                                "author": entry.get("author", ""),
                                                "content": description,
                                                "summary": (description[:300] + "..." if len(description) > 300 else description)
                                            }
                                            results.append(result)
                                            logger.debug(f"✅ El Confidencial match: {title[:50]}...")
                                    except Exception as e:
                                        logger.error(f"Error processing El Confidencial entry: {e}")
                                        continue
                            elif response.status == 404:
                                logger.error(f"El Confidencial feed not found: {feed['url']}")
                                errors.append(f"Feed not found: {feed['category']}")
                            elif response.status == 403:
                                logger.error(f"Access forbidden to El Confidencial feed: {feed['url']}")
                                errors.append(f"Access forbidden: {feed['category']}")
                            else:
                                logger.error(f"Unexpected status {response.status} for El Confidencial feed: {feed['url']}")
                                errors.append(f"HTTP {response.status}: {feed['category']}")
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error fetching El Confidencial {feed['category']}: {e}")
                        errors.append(f"Network error: {feed['category']}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing El Confidencial {feed['category']}: {e}")
                        errors.append(f"Processing error: {feed['category']}")
                        continue
            logger.info(f"✅ El Confidencial search done: {len(results)} results")
            return {"search_summary": {"query": query, "source": "El Confidencial", "total_results": len(results), "feeds_searched": len(self.feeds), "errors": errors[:5]}, "articles": results}
        except Exception as e:
            logger.error(f"El Confidencial search failed: {e}")
            return {"search_summary": {"query": query, "source": "El Confidencial", "total_results": 0, "feeds_searched": 0, "errors": [str(e)]}, "articles": []} 