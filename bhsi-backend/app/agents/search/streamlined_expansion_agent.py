#!/usr/bin/env python3
"""
Streamlined Expansión RSS Agent - Fast data fetching only, no classification
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import feedparser
import re
from app.agents.search.base_agent import BaseSearchAgent
import ssl

logger = logging.getLogger(__name__)


class StreamlinedExpansionAgent(BaseSearchAgent):
    """Ultra-fast Expansión RSS search - fetches data only, classification later"""
    
    def __init__(self):
        super().__init__()
        self.source = "Expansión"
        self.feeds = [
            # Empresas
            {"category": "empresas-nombramientos", 
             "url": "https://e00-expansion.uecdn.es/rss/empresas/nombramientos.xml"},
            {"category": "empresas-distribucion", 
             "url": "https://e00-expansion.uecdn.es/rss/empresas/distribucion.xml"},
            {"category": "empresas-banca", 
             "url": "https://e00-expansion.uecdn.es/rss/empresasbanca.xml"},
            {"category": "empresas-pymes", 
             "url": "https://e00-expansion.uecdn.es/rss/pymes.xml"},
            # Economía
            {"category": "economia-politica", 
             "url": "https://e00-expansion.uecdn.es/rss/economia/politica.xml"},
            {"category": "economia-portada", 
             "url": "https://e00-expansion.uecdn.es/rss/economia.xml"},
            # Mercados
            {"category": "mercados-cronica-bolsa", 
             "url": "https://e00-expansion.uecdn.es/rss/mercados/cronica-bolsa.xml"},
            # Jurídico
            {"category": "juridico-sentencias", 
             "url": "https://e00-expansion.uecdn.es/rss/juridicosentencias.xml"},
            {"category": "juridico-actualidad-tendencias", 
             "url": "https://e00-expansion.uecdn.es/rss/juridico/actualidad-tendencias.xml"},
            # Fiscal
            {"category": "fiscal-tribunales", 
             "url": "https://e00-expansion.uecdn.es/rss/fiscal/tribunales.xml"},
            # Economía Sostenible
            {"category": "economia-sostenible", 
             "url": "https://e00-expansion.uecdn.es/rss/economia-sostenible.xml"},
            # Expansión y Empleo
            {"category": "expansion-empleo", 
             "url": "https://e00-expansion.uecdn.es/rss/expansion-empleo/empleo.xml"},
            # Economía Digital
            {"category": "economia-digital-innovacion", 
             "url": "https://e00-expansion.uecdn.es/rss/economia-digital/innovacion.xml"}
        ]
    
    def _fix_encoding_declaration(self, content: str) -> str:
        """
        Fix UTF-8 encoding declaration issues in Expansión RSS feeds
        """
        try:
            # Check if content declares us-ascii but contains UTF-8 characters
            if 'encoding="us-ascii"' in content or 'encoding="US-ASCII"' in content:
                # Replace us-ascii declaration with utf-8
                content = re.sub(
                    r'encoding=["\']us-ascii["\']', 
                    'encoding="utf-8"', 
                    content, 
                    flags=re.IGNORECASE
                )
                logger.debug("Fixed encoding declaration from us-ascii to utf-8")
            
            # Also handle charset declarations
            if 'charset=us-ascii' in content or 'charset=US-ASCII' in content:
                content = re.sub(
                    r'charset=us-ascii', 
                    'charset=utf-8', 
                    content, 
                    flags=re.IGNORECASE
                )
                logger.debug("Fixed charset declaration from us-ascii to utf-8")
            
            return content
            
        except Exception as e:
            logger.warning(f"Error fixing encoding declaration: {e}")
            return content
    
    def _parse_feed_safely(self, content: str) -> feedparser.FeedParserDict:
        """
        Parse RSS feed with proper encoding handling
        """
        try:
            # Fix encoding declarations
            fixed_content = self._fix_encoding_declaration(content)
            
            # Parse with feedparser
            parsed_feed = feedparser.parse(fixed_content)
            
            # Check if parsing was successful
            if parsed_feed.bozo and parsed_feed.bozo_exception:
                logger.warning(f"Feed parsing warning: {parsed_feed.bozo_exception}")
                # Continue anyway as the content might still be usable
            
            return parsed_feed
            
        except Exception as e:
            logger.error(f"Error parsing feed: {e}")
            # Return empty feed structure
            return feedparser.FeedParserDict()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Handle different date formats from Expansión RSS
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
        FAST Expansión RSS search - just fetch and filter, no classification
        """
        try:
            logger.info(f"📰 Expansión RSS search: '{query}'")
            
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
                        logger.debug(f"Fetching Expansión feed: {feed['category']}")
                        
                        async with session.get(feed["url"]) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Use custom parser to handle encoding issues
                                parsed_feed = self._parse_feed_safely(content)
                                
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
                                                "source": "Expansión",
                                                "category": feed["category"],
                                                "author": entry.get("author", ""),
                                                "content": description,  # Use description as content
                                                "summary": (description[:300] + "..." 
                                                          if len(description) > 300 
                                                          else description)
                                            }
                                            results.append(result)
                                            logger.debug(f"✅ Expansión match: {title[:50]}...")
                                            
                                    except Exception as e:
                                        logger.error(f"Error processing Expansión entry: {e}")
                                        continue
                                        
                            elif response.status == 404:
                                logger.error(f"Expansión feed not found: {feed['url']}")
                                errors.append(f"Feed not found: {feed['category']}")
                            elif response.status == 403:
                                logger.error(f"Access forbidden to Expansión feed: {feed['url']}")
                                errors.append(f"Access forbidden: {feed['category']}")
                            else:
                                logger.error(f"Unexpected status {response.status} for Expansión feed: {feed['url']}")
                                errors.append(f"HTTP {response.status}: {feed['category']}")
                                
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error fetching Expansión {feed['category']}: {e}")
                        errors.append(f"Network error: {feed['category']}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing Expansión {feed['category']}: {e}")
                        errors.append(f"Processing error: {feed['category']}")
                        continue
            
            logger.info(f"✅ Expansión search done: {len(results)} results")
            
            return {
                "search_summary": {
                    "query": query,
                    "source": "Expansión",
                    "total_results": len(results),
                    "feeds_searched": len(self.feeds),
                    "errors": errors[:5]  # Limit error list
                },
                "articles": results
            }
            
        except Exception as e:
            logger.error(f"Expansión search failed: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "source": "Expansión",
                    "total_results": 0,
                    "feeds_searched": 0,
                    "errors": [str(e)]
                },
                "articles": []
            } 