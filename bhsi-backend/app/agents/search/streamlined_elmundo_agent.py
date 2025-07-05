#!/usr/bin/env python3
"""
Streamlined El Mundo RSS Agent - Fast data fetching only, no classification
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import feedparser
from app.agents.search.base_agent import BaseSearchAgent
import ssl

logger = logging.getLogger(__name__)


class StreamlinedElMundoAgent(BaseSearchAgent):
    """Ultra-fast El Mundo RSS search - fetches data only, classification later"""
    
    def __init__(self):
        super().__init__()
        self.source = "El Mundo"
        self.feeds = [
            # Economy (main business focus)
            {
                "category": "economia",
                "url": "https://e00-elmundo.uecdn.es/rss/economia.xml"
            },
            # Main news (includes business content)
            {
                "category": "portada",
                "url": "https://e00-elmundo.uecdn.es/rss/portada.xml"
            },
            # Technology (business tech news)
            {
                "category": "tecnologia",
                "url": "https://e00-elmundo.uecdn.es/rss/tecnologia.xml"
            },
            # Society (regulatory and social business impact)
            {
                "category": "sociedad",
                "url": "https://e00-elmundo.uecdn.es/rss/sociedad.xml"
            },
            # International (global business news)
            {
                "category": "internacional",
                "url": "https://e00-elmundo.uecdn.es/rss/internacional.xml"
            }
        ]
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Handle different date formats from El Mundo RSS
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
        FAST El Mundo RSS search - just fetch and filter, no classification
        """
        try:
            logger.info(f"📰 El Mundo RSS search: '{query}'")
            
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
            
            # Create SSL context that doesn't verify certificates (for testing only)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers, connector=connector) as session:
                for feed in self.feeds:
                    try:
                        logger.debug(f"Fetching El Mundo feed: {feed['category']}")
                        
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
                                                "source": "El Mundo",
                                                "category": feed["category"],
                                                "author": entry.get("author", ""),
                                                "content": description,  # Use description as content
                                                "summary": (description[:300] + "..." 
                                                          if len(description) > 300 
                                                          else description)
                                            }
                                            results.append(result)
                                            logger.debug(f"✅ El Mundo match: {title[:50]}...")
                                            
                                    except Exception as e:
                                        logger.error(f"Error processing El Mundo entry: {e}")
                                        continue
                                        
                            elif response.status == 404:
                                logger.error(f"El Mundo feed not found: {feed['url']}")
                                errors.append(f"Feed not found: {feed['category']}")
                            elif response.status == 403:
                                logger.error(f"Access forbidden to El Mundo feed: {feed['url']}")
                                errors.append(f"Access forbidden: {feed['category']}")
                            else:
                                logger.error(f"Unexpected status {response.status} for El Mundo feed: {feed['url']}")
                                errors.append(f"HTTP {response.status}: {feed['category']}")
                                
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error fetching El Mundo {feed['category']}: {e}")
                        errors.append(f"Network error: {feed['category']}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing El Mundo {feed['category']}: {e}")
                        errors.append(f"Processing error: {feed['category']}")
                        continue
            
            logger.info(f"✅ El Mundo search done: {len(results)} results")
            
            return {
                "search_summary": {
                    "query": query,
                    "source": "El Mundo",
                    "total_results": len(results),
                    "feeds_searched": len(self.feeds),
                    "errors": errors[:5]  # Limit error list
                },
                "articles": results
            }
            
        except Exception as e:
            logger.error(f"El Mundo search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "source": "El Mundo",
                    "total_results": 0,
                    "feeds_searched": 0,
                    "errors": [str(e)]
                },
                "articles": []
            } 