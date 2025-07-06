#!/usr/bin/env python3
"""
Database Integration Service - BigQuery Only
Handles saving search results to BigQuery
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from app.crud.raw_docs import raw_docs
from app.crud.events import events
from app.agents.analysis.processor import EventNormalizer

logger = logging.getLogger(__name__)


class DatabaseIntegrationService:
    """Service to integrate search results with BigQuery persistence"""
    
    def __init__(self):
        self.raw_docs_crud = raw_docs
        self.events_crud = events
        self.normalizer = EventNormalizer()
    
    async def save_search_results(
        self,
        search_results: Dict[str, Any],
        query: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Save search results to BigQuery
        
        Args:
            search_results: Search results from orchestrator
            query: Original search query
            company_name: Company name being searched
            
        Returns:
            Dictionary with save statistics
        """
        stats = {
            "raw_docs_saved": 0,
            "events_created": 0,
            "total_processed": 0,
            "errors": []
        }
        
        logger.info(f"💾 Saving search results for '{company_name}' to BigQuery...")
        
        try:
            # Process BOE results
            if "boe" in search_results and search_results["boe"].get("results"):
                boe_stats = await self._process_boe_results(
                    search_results["boe"]["results"], company_name
                )
                stats["raw_docs_saved"] += boe_stats["raw_docs_saved"]
                stats["events_created"] += boe_stats["events_created"]
                stats["total_processed"] += boe_stats["total_processed"]
                stats["errors"].extend(boe_stats["errors"])
            
            # Process NewsAPI results
            if "newsapi" in search_results and search_results["newsapi"].get("articles"):
                news_stats = await self._process_news_results(
                    search_results["newsapi"]["articles"], company_name
                )
                stats["raw_docs_saved"] += news_stats["raw_docs_saved"]
                stats["events_created"] += news_stats["events_created"]
                stats["total_processed"] += news_stats["total_processed"]
                stats["errors"].extend(news_stats["errors"])
            
            # Process RSS results
            rss_sources = [
                "elpais", "expansion", "elmundo", "abc", "lavanguardia",
                "elconfidencial", "eldiario", "europapress"
            ]
            
            for source in rss_sources:
                if source in search_results and search_results[source].get("articles"):
                    rss_stats = await self._process_rss_results(
                        search_results[source]["articles"], source, company_name
                    )
                    stats["raw_docs_saved"] += rss_stats["raw_docs_saved"]
                    stats["events_created"] += rss_stats["events_created"]
                    stats["total_processed"] += rss_stats["total_processed"]
                    stats["errors"].extend(rss_stats["errors"])
            
            logger.info(f"✅ Saved {stats['total_processed']} items to BigQuery")
            return stats
            
        except Exception as e:
            error_msg = f"❌ Database integration failed: {e}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
    
    def build_rawdoc_dict(self, source: str, payload_bytes: bytes, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Build raw document dictionary for BigQuery"""
        return {
            "source": source,
            "payload": payload_bytes,
            "meta": meta
        }
    
    async def _process_boe_results(
        self, 
        boe_results: List[Dict[str, Any]], 
        company_name: str
    ) -> Dict[str, Any]:
        """Process and save BOE results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        
        for result in boe_results:
            try:
                # Create payload for raw_docs
                payload_bytes = json.dumps(result, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": result.get("url_html", ""),
                    "pub_date": result.get("fechaPublicacion", ""),
                    "source_name": "BOE",
                    "seccion": result.get("seccion_codigo", "")
                }
                
                rawdoc_dict = self.build_rawdoc_dict("BOE", payload_bytes, meta)
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(**rawdoc_dict)
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if result.get("fechaPublicacion"):
                            try:
                                pub_str = result["fechaPublicacion"].split("T")[0]
                                pub_date = datetime.strptime(pub_str, "%Y-%m-%d").date()
                            except Exception:
                                pass
                        
                        event = await self.events_crud.create_from_raw(
                            raw_id=raw_doc["raw_id"],
                            source="BOE",
                            title=result.get("titulo", ""),
                            text=result.get("text", ""),
                            section=result.get("seccion_codigo", ""),
                            pub_date=pub_date,
                            url=result.get("url_html", "")
                        )
                        
                        if event:
                            stats["events_created"] += 1
                            
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"BOE result processing error: {str(e)}")
        
        return stats
    
    async def _process_news_results(
        self, 
        news_results: List[Dict[str, Any]], 
        company_name: str
    ) -> Dict[str, Any]:
        """Process and save NewsAPI results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        
        for article in news_results:
            try:
                # Type check to prevent 'str' object has no attribute 'get' errors
                if not isinstance(article, dict):
                    logger.warning(f"Skipping non-dict NewsAPI article: {type(article)} - {article}")
                    stats["errors"].append(f"Non-dict article skipped: {type(article)}")
                    continue
                
                # Create payload for raw_docs
                payload_data = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "url": article.get("url", ""),
                    "source": (article.get("source") or {}).get("name", "Unknown")
                }
                payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": article.get("url", ""),
                    "pub_date": article.get("publishedAt", ""),
                    "source_name": (article.get("source") or {}).get("name", "Unknown"),
                    "author": article.get("author", "")
                }
                
                rawdoc_dict = self.build_rawdoc_dict("NewsAPI", payload_bytes, meta)
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(**rawdoc_dict)
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("publishedAt"):
                            try:
                                pub_str = article["publishedAt"].split("T")[0]
                                pub_date = datetime.strptime(pub_str, "%Y-%m-%d").date()
                            except Exception:
                                pass
                        
                        event = await self.events_crud.create_from_raw(
                            raw_id=raw_doc["raw_id"],
                            source="NewsAPI",
                            title=article.get("title", ""),
                            text=article.get("content", article.get("description", "")),
                            section=(article.get("source") or {}).get("name", ""),
                            pub_date=pub_date,
                            url=article.get("url", "")
                        )
                        
                        if event:
                            stats["events_created"] += 1
                            
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"News result processing error: {str(e)}")
        
        return stats
    
    async def _process_rss_results(
        self, 
        rss_results: List[dict], 
        source_name: str, 
        company_name: str
    ) -> dict:
        """Process and save RSS results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        
        for article in rss_results:
            try:
                # Use the generic RSS adapter
                payload_bytes = json.dumps(article, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": article.get("url", ""),
                    "pub_date": article.get("publishedAt", ""),
                    "source_name": source_name.upper(),
                    "author": article.get("author", "")
                }
                
                rawdoc_dict = self.build_rawdoc_dict(source_name.upper(), payload_bytes, meta)
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(**rawdoc_dict)
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("publishedAt"):
                            try:
                                pub_str = article["publishedAt"].split("T")[0]
                                pub_date = datetime.strptime(pub_str, "%Y-%m-%d").date()
                            except Exception:
                                pass
                        
                        event = await self.events_crud.create_from_raw(
                            raw_id=raw_doc["raw_id"],
                            source=source_name.upper(),
                            title=article.get("title", ""),
                            text=article.get("content", article.get("description", "")),
                            section=article.get("category", ""),
                            pub_date=pub_date,
                            url=article.get("url", "")
                        )
                        
                        if event:
                            stats["events_created"] += 1
                            
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"RSS result processing error: {str(e)}")
        
        return stats


# Global instance
db_integration = DatabaseIntegrationService() 