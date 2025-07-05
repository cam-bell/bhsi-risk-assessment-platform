#!/usr/bin/env python3
"""
BigQuery Database Integration Service - Save search results to BigQuery
Replaces SQLite operations with BigQuery as the primary database
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from app.crud.bigquery_raw_docs import bigquery_raw_docs
from app.crud.bigquery_events import bigquery_events
from app.agents.analysis.processor import EventNormalizer

logger = logging.getLogger(__name__)


class BigQueryDatabaseIntegrationService:
    """Service to integrate search results with BigQuery persistence"""
    
    def __init__(self):
        self.raw_docs_crud = bigquery_raw_docs
        self.events_crud = bigquery_events
        self.normalizer = EventNormalizer()
    
    async def save_search_results(
        self,
        search_results: Dict[str, Any],
        query: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Save search results to BigQuery using BigQuery CRUD operations
        
        Args:
            search_results: Results from search orchestrator
            query: Original search query
            company_name: Company being searched
            
        Returns:
            Dict with save statistics
        """
        stats = {
            "raw_docs_saved": 0,
            "events_created": 0,
            "total_processed": 0,
            "errors": []
        }
        
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
                if (
                    source in search_results and
                    search_results[source].get("articles")
                ):
                    rss_stats = await self._process_rss_results(
                        search_results[source]["articles"],
                        source,
                        company_name
                    )
                    stats["raw_docs_saved"] += rss_stats["raw_docs_saved"]
                    stats["events_created"] += rss_stats["events_created"]
                    stats["total_processed"] += rss_stats["total_processed"]
                    stats["errors"].extend(rss_stats["errors"])
            
            # Process Yahoo Finance results
            if (
                "yahoo_finance" in search_results and
                search_results["yahoo_finance"].get("financial_data")
            ):
                yahoo_stats = await self._process_yahoo_finance_results(
                    search_results["yahoo_finance"]["financial_data"],
                    company_name
                )
                stats["raw_docs_saved"] += yahoo_stats["raw_docs_saved"]
                stats["events_created"] += yahoo_stats["events_created"]
                stats["total_processed"] += yahoo_stats["total_processed"]
                stats["errors"].extend(yahoo_stats["errors"])
            
            logger.info(
                f"BigQuery integration complete for '{company_name}': "
                f"{stats['raw_docs_saved']} raw docs, {stats['events_created']} events"
            )
            
        except Exception as e:
            logger.error(f"BigQuery integration failed: {e}")
            stats["errors"].append(f"Integration error: {str(e)}")
        
        return stats
    
    def build_rawdoc_dict(self, source, payload_bytes, meta):
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
                payload_data = {
                    "identificador": result.get("identificador", ""),
                    "titulo": result.get("titulo", ""),
                    "text": result.get("text", ""),
                    "fechaPublicacion": result.get("fechaPublicacion", ""),
                    "url_html": result.get("url_html", ""),
                    "seccion_codigo": result.get("seccion_codigo", ""),
                    "seccion_nombre": result.get("seccion_nombre", "")
                }
                payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": result.get("url_html", ""),
                    "pub_date": result.get("fechaPublicacion", ""),
                    "section": result.get("seccion_codigo", ""),
                    "identificador": result.get("identificador", "")
                }
                
                # Save raw document
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(
                    source="BOE",
                    payload=payload_bytes,
                    meta=meta
                )
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if result.get("fechaPublicacion"):
                            try:
                                pub_date = datetime.strptime(
                                    result["fechaPublicacion"], "%Y-%m-%d"
                                ).date()
                            except Exception:
                                pass
                        
                        # Create event data
                        event_data = {
                            "event_id": f"BOE:{raw_doc['raw_id']}",
                            "title": result.get("titulo", ""),
                            "text": result.get("text", ""),
                            "source": "BOE",
                            "section": result.get("seccion_codigo", ""),
                            "pub_date": pub_date.isoformat() if pub_date else None,
                            "url": result.get("url_html", ""),
                            "alerted": False
                        }
                        
                        await self.events_crud.create_event(event_data)
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
                # Create payload for raw_docs
                payload_data = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "url": article.get("url", ""),
                    "author": article.get("author", ""),
                    "source": article.get("source", {}).get("name", "")
                }
                payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": article.get("url", ""),
                    "pub_date": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "")
                }
                
                # Save raw document
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(
                    source="NewsAPI",
                    payload=payload_bytes,
                    meta=meta
                )
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("publishedAt"):
                            try:
                                pub_date = datetime.strptime(
                                    article["publishedAt"][:10], "%Y-%m-%d"
                                ).date()
                            except Exception:
                                pass
                        
                        # Create event data
                        event_data = {
                            "event_id": f"NewsAPI:{raw_doc['raw_id']}",
                            "title": article.get("title", ""),
                            "text": article.get("content", article.get("description", "")),
                            "source": "NewsAPI",
                            "section": article.get("source", {}).get("name", ""),
                            "pub_date": pub_date.isoformat() if pub_date else None,
                            "url": article.get("url", ""),
                            "alerted": False
                        }
                        
                        await self.events_crud.create_event(event_data)
                        stats["events_created"] += 1
                        
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"News result processing error: {str(e)}")
        
        return stats
    
    async def _process_rss_results(
        self, 
        rss_results: List[Dict[str, Any]], 
        source_name: str, 
        company_name: str
    ) -> Dict[str, Any]:
        """Process and save RSS results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        
        for article in rss_results:
            try:
                # Create payload for raw_docs
                payload_data = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "published": article.get("published", ""),
                    "url": article.get("url", ""),
                    "author": article.get("author", ""),
                    "source": source_name.upper()
                }
                payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": article.get("url", ""),
                    "pub_date": article.get("published", ""),
                    "source": source_name.upper()
                }
                
                # Save raw document
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(
                    source=f"RSS-{source_name.upper()}",
                    payload=payload_bytes,
                    meta=meta
                )
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("published"):
                            try:
                                pub_date = datetime.strptime(
                                    article["published"][:10], "%Y-%m-%d"
                                ).date()
                            except Exception:
                                pass
                        
                        # Create event data
                        event_data = {
                            "event_id": f"RSS-{source_name.upper()}:{raw_doc['raw_id']}",
                            "title": article.get("title", ""),
                            "text": article.get("content", article.get("description", "")),
                            "source": f"RSS-{source_name.upper()}",
                            "section": source_name.upper(),
                            "pub_date": pub_date.isoformat() if pub_date else None,
                            "url": article.get("url", ""),
                            "alerted": False
                        }
                        
                        await self.events_crud.create_event(event_data)
                        stats["events_created"] += 1
                        
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"RSS result processing error: {str(e)}")
        
        return stats
    
    async def _process_yahoo_finance_results(
        self,
        financial_data_list: List[Dict[str, Any]],
        company_name: str
    ) -> Dict[str, Any]:
        """Process and save Yahoo Finance results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        
        for financial_data in financial_data_list:
            try:
                # Create payload for raw_docs
                payload_data = {
                    "symbol": financial_data.get("symbol", ""),
                    "company_name": financial_data.get("company_name", ""),
                    "financial_metrics": financial_data.get("financial_metrics", {}),
                    "market_data": financial_data.get("market_data", {}),
                    "timestamp": financial_data.get("timestamp", "")
                }
                payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "symbol": financial_data.get("symbol", ""),
                    "timestamp": financial_data.get("timestamp", "")
                }
                
                # Save raw document
                raw_doc, is_new = await self.raw_docs_crud.create_with_dedup(
                    source="YahooFinance",
                    payload=payload_bytes,
                    meta=meta
                )
                
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        # Create event data for financial metrics
                        event_data = {
                            "event_id": f"YahooFinance:{raw_doc['raw_id']}",
                            "title": f"Financial Data - {financial_data.get('symbol', 'Unknown')}",
                            "text": json.dumps(financial_data.get("financial_metrics", {})),
                            "source": "YahooFinance",
                            "section": "Financial",
                            "pub_date": financial_data.get("timestamp", ""),
                            "url": "",
                            "alerted": False
                        }
                        
                        await self.events_crud.create_event(event_data)
                        stats["events_created"] += 1
                        
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                stats["errors"].append(f"Yahoo Finance result processing error: {str(e)}")
        
        return stats
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get BigQuery database statistics"""
        try:
            # Get raw docs stats
            raw_docs_stats = await self.raw_docs_crud.get_stats()
            
            # Get events stats
            events_stats = await self.events_crud.get_risk_summary(days_back=7)
            
            return {
                "raw_docs": raw_docs_stats,
                "events": events_stats,
                "database": "BigQuery",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"BigQuery get_database_stats failed: {e}")
            return {"error": str(e)}


# Global instance
bigquery_db_integration = BigQueryDatabaseIntegrationService() 