"""
🧠 Strategic Recommendation

Best Next Steps:
    1. Drop El Mundo RSS for now — too unstable for clean automation (see probe_elmundo_feeds.py results).
    2. Double down on:
        • El País (well-formed feeds)
        • Expansión (industry-specific feeds)

Note: As of latest test (see quick_test_expansion.py), Expansión RSS feeds return entries but trigger a feedparser warning: 'document declared as us-ascii, but parsed as utf-8'. Despite this, the feeds are accessible and usable for automation, but monitor for future format changes.
"""
import feedparser
from typing import List, Dict, Any
import aiohttp
from datetime import datetime, timedelta
import logging
from app.core.config import settings
from .base_agent import BaseSearchAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAgencyAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.sources = [
            {
                "name": "El País",
                "type": "rss",
                "feeds": [
                    {
                        "category": "espana",
                        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
                    },
                    {
                        "category": "economia",
                        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada"
                    },
                    {
                        "category": "negocios",
                        "url": "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/economia/subsection/negocios"
                    },
                    {
                        "category": "tecnologia",
                        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada"
                    },
                    {
                        "category": "clima",
                        "url": "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/clima-y-medio-ambiente"
                    }
                ],
                "api_key": settings.ELPAIS_API_KEY
            },
            # {
            #     "name": "El Mundo",
            #     "type": "rss",
            #     "feeds": [
            #         {
            #             "category": "economia",
            #             "url": "https://www.elmundo.es/rss/economia.xml"
            #         },
            #         {
            #             "category": "empresas",
            #             "url": "https://www.elmundo.es/rss/empresas.xml"
            #         },
            #         {
            #             "category": "mercados",
            #             "url": "https://www.elmundo.es/rss/mercados.xml"
            #         },
            #         {
            #             "category": "sociedad",
            #             "url": "https://www.elmundo.es/rss/sociedad.xml"
            #         }
            #     ],
            #     "api_key": settings.ELMUNDO_API_KEY
            # },
            {
                "name": "Expansión",
                "type": "rss",
                "feeds": [
                    # Empresas
                    {"category": "empresas-nombramientos", "url": "https://e00-expansion.uecdn.es/rss/empresas/nombramientos.xml"},
                    {"category": "empresas-distribucion", "url": "https://e00-expansion.uecdn.es/rss/empresas/distribucion.xml"},
                    {"category": "empresas-banca", "url": "https://e00-expansion.uecdn.es/rss/empresasbanca.xml"},
                    {"category": "empresas-pymes", "url": "https://e00-expansion.uecdn.es/rss/pymes.xml"},
                    # Economía
                    {"category": "economia-politica", "url": "https://e00-expansion.uecdn.es/rss/economia/politica.xml"},
                    {"category": "economia-portada", "url": "https://e00-expansion.uecdn.es/rss/economia.xml"},
                    # Mercados
                    {"category": "mercados-cronica-bolsa", "url": "https://e00-expansion.uecdn.es/rss/mercados/cronica-bolsa.xml"},
                    # Jurídico
                    {"category": "juridico-sentencias", "url": "https://e00-expansion.uecdn.es/rss/juridicosentencias.xml"},
                    {"category": "juridico-actualidad-tendencias", "url": "https://e00-expansion.uecdn.es/rss/juridico/actualidad-tendencias.xml"},
                    # Fiscal
                    {"category": "fiscal-tribunales", "url": "https://e00-expansion.uecdn.es/rss/fiscal/tribunales.xml"},
                    # Economía Sostenible
                    {"category": "economia-sostenible", "url": "https://e00-expansion.uecdn.es/rss/economia-sostenible.xml"},
                    # Expansión y Empleo
                    {"category": "expansion-empleo", "url": "https://e00-expansion.uecdn.es/rss/expansion-empleo/empleo.xml"},
                    # Economía Digital
                    {"category": "economia-digital-innovacion", "url": "https://e00-expansion.uecdn.es/rss/economia-digital/innovacion.xml"}
                ],
                "api_key": settings.EXPANSION_API_KEY
            }
        ]
    
    async def _validate_mrss_feed(self, feed: feedparser.FeedParserDict) -> bool:
        """
        Validate the structure and content of an MRSS feed
        """
        if not feed:
            logger.error("Empty feed received")
            return False

        if hasattr(feed, 'bozo') and feed.bozo:
            logger.error(f"Feed parsing error: {feed.bozo_exception}")
            return False

        if not feed.entries:
            logger.warning("Feed contains no entries")
            return False

        # Check for required MRSS fields in the first entry
        first_entry = feed.entries[0]
        required_fields = ['title', 'link', 'published']
        missing_fields = [field for field in required_fields if not hasattr(first_entry, field)]
        
        if missing_fields:
            logger.error(f"Missing required fields in feed: {missing_fields}")
            return False

        return True

    async def _search_rss_feeds(self, source: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Search through RSS feeds for a specific news source with enhanced error handling
        """
        results = []
        query_terms = query.lower().split()

        for feed in source["feeds"]:
            logger.info(f"Fetching {feed['url']} for {source['name']} - {feed['category']}")
            try:
                async with self.session.get(feed["url"]) as response:
                    if response.status == 200:
                        content = await response.text()
                        parsed_feed = feedparser.parse(content)
                        
                        # Validate MRSS feed structure
                        if not await self._validate_mrss_feed(parsed_feed):
                            logger.error(f"Invalid MRSS feed structure for {source['name']} - {feed['category']}")
                            continue

                        for entry in parsed_feed.entries:
                            try:
                                # Extract and validate entry data
                                title = entry.get("title", "").strip()
                                description = entry.get("description", "").strip()
                                link = entry.get("link", "").strip()
                                published = entry.get("published", datetime.now().isoformat())

                                # Skip entries with missing critical data
                                if not all([title, link]):
                                    logger.warning(f"Skipping entry with missing critical data in {source['name']} - {feed['category']}")
                                    continue

                                # Check if any query term is in title or description
                                if any(term in title.lower() or term in description.lower() for term in query_terms):
                                    results.append({
                                        "title": title,
                                        "snippet": description,
                                        "url": link,
                                        "timestamp": published,
                                        "source": source["name"],
                                        "category": feed["category"]
                                    })
                            except Exception as entry_error:
                                logger.error(f"Error processing entry in {source['name']} - {feed['category']}: {str(entry_error)}")
                                continue

                    elif response.status == 404:
                        logger.error(f"Feed not found: {feed['url']}")
                    elif response.status == 403:
                        logger.error(f"Access forbidden to feed: {feed['url']}")
                    elif response.status == 429:
                        logger.error(f"Rate limit exceeded for feed: {feed['url']}")
                    else:
                        logger.error(f"Unexpected status code {response.status} for feed: {feed['url']}")

            except aiohttp.ClientError as e:
                logger.error(f"Network error fetching {source['name']} {feed['category']} feed: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error processing {source['name']} {feed['category']} feed: {str(e)}")
                continue

        return results
    
    async def search(self, query: str) -> Dict[str, Any]:
        """
        Search across Spanish news agencies using RSS feeds with enhanced error handling
        """
        results = []
        total_articles = 0
        errors = []

        for source in self.sources:
            if not source["api_key"]:
                error_msg = f"No API key configured for {source['name']}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue

            try:
                if source["type"] == "rss":
                    source_results = await self._search_rss_feeds(source, query)
                    results.extend(source_results)
                    total_articles += len(source_results)
                
            except Exception as e:
                error_msg = f"Error searching {source['name']}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue
        
        return {
            "results": self.clean_results(results),
            "total": total_articles,
            "sources": [source["name"] for source in self.sources],
            "errors": errors if errors else None
        }

    async def fetch_url(self, url: str) -> str:
        """
        Override fetch_url to add specific headers for news sites with error handling
        """
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        headers = {
            "User-Agent": "BHSI-Risk-Assessment/1.0",
            "Accept": "application/rss+xml, application/xml",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching URL {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching URL {url}: {str(e)}")
            raise 