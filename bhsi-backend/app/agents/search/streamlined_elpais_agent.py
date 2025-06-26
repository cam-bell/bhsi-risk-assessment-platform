#!/usr/bin/env python3
"""
Streamlined El País RSS Agent - Fast data fetching only, no classification
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import feedparser
from app.agents.search.base_agent import BaseSearchAgent

logger = logging.getLogger(__name__)


class StreamlinedElPaisAgent(BaseSearchAgent):
    """Ultra-fast El País RSS search - fetches data only, classification later"""
    
    def __init__(self):
        super().__init__()
        self.source = "El País"
        self.feeds = [
            {
                "category": "portada",
                "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
            },
            {
                "category": "economia",
                "url": ("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/"
                       "section/economia/portada")
            },
            {
                "category": "negocios",
                "url": ("https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/"
                       "section/economia/subsection/negocios")
            },
            {
                "category": "tecnologia",
                "url": ("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/"
                       "section/tecnologia/portada")
            },
            {
                "category": "clima",
                "url": ("https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/"
                       "section/clima-y-medio-ambiente")
            }
        ]
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Handle different date formats from El País RSS
            if "T" in date_str:
                # Already ISO format
                return date_str
            else:
                # Try parsing common formats
                formats = [
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d"
                ]
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        return parsed.isoformat() + "Z"
                    except ValueError:
                        continue
                # Fallback to current date
                return datetime.now().isoformat() + "Z"
        except Exception as e:
            logger.warning(f"Date parsing error for '{date_str}': {e}")
            return datetime.now().isoformat() + "Z"
    
    async def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = 7
    ) -> Dict[str, Any]:
        """
        FAST El País RSS search - just fetch and filter, no classification
        """
        try:
            logger.info(f"📰 El País RSS search: '{query}'")
            
            results = []
            errors = []
            query_lower = query.lower()
            query_terms = query_lower.split()
            
            # Set up HTTP session with appropriate headers
            headers = {
                "User-Agent": "BHSI-Risk-Assessment/1.0",
                "Accept": "application/rss+xml, application/xml",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                for feed in self.feeds:
                    try:
                        logger.debug(f"Fetching El País feed: {feed['category']}")
                        
                        async with session.get(feed["url"]) as response:
                            if response.status == 200:
                                content = await response.text()
                                parsed_feed = feedparser.parse(content)
                                
                                # Validate feed structure
                                if not parsed_feed.entries:
                                    logger.warning(f"Empty feed: {feed['category']}")
                                    continue
                                
                                for entry in parsed_feed.entries:
                                    try:
                                        # Extract entry data
                                        title = entry.get("title", "").strip()
                                        description = entry.get("description", "").strip()
                                        link = entry.get("link", "").strip()
                                        published = entry.get("published", "")
                                        
                                        # Skip entries with missing critical data
                                        if not title or not link:
                                            continue
                                        
                                        # Simple string matching - very fast
                                        if any(term in title.lower() or 
                                               term in description.lower() 
                                               for term in query_terms):
                                            # Create result without classification
                                            result = {
                                                "title": title,
                                                "description": description,
                                                "url": link,
                                                "publishedAt": self._parse_date(published),
                                                "source": "El País",
                                                "category": feed["category"],
                                                "author": entry.get("author", ""),
                                                "content": description,  # Use description as content
                                                "summary": (description[:300] + "..." 
                                                          if len(description) > 300 
                                                          else description)
                                            }
                                            results.append(result)
                                            logger.debug(f"✅ El País match: {title[:50]}...")
                                            
                                    except Exception as e:
                                        logger.error(f"Error processing El País entry: {e}")
                                        continue
                                        
                            elif response.status == 404:
                                logger.error(f"El País feed not found: {feed['url']}")
                                errors.append(f"Feed not found: {feed['category']}")
                            elif response.status == 403:
                                logger.error(f"Access forbidden to El País feed: {feed['url']}")
                                errors.append(f"Access forbidden: {feed['category']}")
                            else:
                                logger.error(f"Unexpected status {response.status} for El País feed: {feed['url']}")
                                errors.append(f"HTTP {response.status}: {feed['category']}")
                                
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error fetching El País {feed['category']}: {e}")
                        errors.append(f"Network error: {feed['category']}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing El País {feed['category']}: {e}")
                        errors.append(f"Processing error: {feed['category']}")
                        continue
            
            logger.info(f"✅ El País search done: {len(results)} results")
            
            return {
                "search_summary": {
                    "query": query,
                    "source": "El País",
                    "total_results": len(results),
                    "feeds_searched": len(self.feeds),
                    "errors": errors[:5]  # Limit error list
                },
                "articles": results
            }
            
        except Exception as e:
            logger.error(f"El País search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "source": "El País",
                    "total_results": 0,
                    "feeds_searched": 0,
                    "errors": [str(e)]
                },
                "articles": []
            } 