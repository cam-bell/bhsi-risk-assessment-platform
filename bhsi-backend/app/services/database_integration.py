#!/usr/bin/env python3
"""
Database Integration Service - Save search results to database
Integrates with existing CRUD operations to persist search data
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.crud.raw_docs import raw_docs
from app.crud.events import events
from app.agents.analysis.processor import EventNormalizer
from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

bigquery_writer = BigQueryWriter(batch_size=1)

class DatabaseIntegrationService:
    """Service to integrate search results with database persistence"""
    
    def __init__(self):
        self.raw_docs_crud = raw_docs
        self.events_crud = events
        self.normalizer = EventNormalizer()
    
    def save_search_results(
        self,
        db: Session,
        search_results: Dict[str, Any],
        query: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Save search results to database using existing CRUD operations
        
        Args:
            db: Database session
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
                boe_stats = self._process_boe_results(
                    db, search_results["boe"]["results"], company_name
                )
                stats["raw_docs_saved"] += boe_stats["raw_docs_saved"]
                stats["events_created"] += boe_stats["events_created"]
                stats["total_processed"] += boe_stats["total_processed"]
                stats["errors"].extend(boe_stats["errors"])
            
            # DEBUG: Log NewsAPI structure
            if "newsapi" in search_results:
                logger.debug(f"NewsAPI result keys: {list(search_results['newsapi'].keys())}")
                articles = search_results["newsapi"].get("articles")
                if articles and isinstance(articles, list) and len(articles) > 0:
                    logger.debug(f"First article sample: {articles[0]}")
                else:
                    logger.debug("No articles found or articles is not a list.")
            
            # Process NewsAPI results
            if "newsapi" in search_results and search_results["newsapi"].get("articles"):
                news_stats = self._process_news_results(
                    db, search_results["newsapi"]["articles"], company_name
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
                    rss_stats = self._process_rss_results(
                        db,
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
                yahoo_stats = self._process_yahoo_finance_results(
                    db,
                    search_results["yahoo_finance"]["financial_data"],
                    company_name
                )
                stats["raw_docs_saved"] += yahoo_stats["raw_docs_saved"]
                stats["events_created"] += yahoo_stats["events_created"]
                stats["total_processed"] += yahoo_stats["total_processed"]
                stats["errors"].extend(yahoo_stats["errors"])
            
            logger.info(
                f"Database integration complete for '{company_name}': "
                f"{stats['raw_docs_saved']} raw docs, {stats['events_created']} events"
            )
            
            # Process embeddings for events
            from app.agents.analysis.cloud_embedder import CloudEmbeddingAgent
            embedding_agent = CloudEmbeddingAgent()
            embedding_stats = embedding_agent.process_unembedded_events(batch_size=50)
            logger.info(f"Embedding processing complete: {embedding_stats}")
            
            bigquery_writer.flush()
            
        except Exception as e:
            logger.error(f"Database integration failed: {e}")
            stats["errors"].append(f"Integration error: {str(e)}")
        
        return stats
    
    def build_rawdoc_dict(self, source, payload_bytes, meta):
        return {
            "source": source,
            "payload": payload_bytes,
            "meta": meta
        }
    
    def _process_boe_results(
        self, 
        db: Session, 
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
                rawdoc_dict = self.build_rawdoc_dict("BOE", payload_bytes, meta)
                logger.info(f"Attempting to create raw doc for article: {payload_data.get('titulo', '')}")
                raw_doc, is_new = self.raw_docs_crud.create_with_dedup(
                    db,
                    **rawdoc_dict
                )
                logger.info(f"Raw doc created: {is_new}, Source: BOE, Title: {payload_data.get('titulo', '')}")
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
                        event = self.normalizer.normalize_and_create_event(db, raw_doc, "BOE", company_name)
                        if event:
                            stats["events_created"] += 1
                            bigquery_writer.queue("solid-topic-443216-b2.risk_monitoring.events", event)
                            logger.info(f"Queued event {getattr(event, 'event_id', None)} for BigQuery: {getattr(event, 'title', None)}")
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                stats["total_processed"] += 1
            except Exception as e:
                stats["errors"].append(f"BOE result processing error: {str(e)}")
        return stats
    
    def _process_news_results(
        self, 
        db: Session, 
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
                logger.info(f"Attempting to create raw doc for article: {payload_data.get('title', '')}")
                raw_doc, is_new = self.raw_docs_crud.create_with_dedup(
                    db,
                    **rawdoc_dict
                )
                logger.info(f"Raw doc created: {is_new}, Source: NewsAPI, Title: {payload_data.get('title', '')}")
                if is_new:
                    stats["raw_docs_saved"] += 1
                    
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("publishedAt"):
                            try:
                                pub_str = article["publishedAt"].split("T")[0]
                                pub_date = datetime.strptime(
                                    pub_str, "%Y-%m-%d"
                                ).date()
                            except Exception:
                                pass
                        event = self.normalizer.normalize_and_create_event(db, raw_doc, "NewsAPI", company_name)
                        if event:
                            stats["events_created"] += 1
                            bigquery_writer.queue("solid-topic-443216-b2.risk_monitoring.events", event)
                            logger.info(f"Queued event {getattr(event, 'event_id', None)} for BigQuery: {getattr(event, 'title', None)}")
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                stats["total_processed"] += 1
            except Exception as e:
                stats["errors"].append(f"News result processing error: {str(e)}")
        return stats
    
    def _process_rss_results(
        self, 
        db: Session, 
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
                raw_doc, is_new = self.raw_docs_crud.create_with_dedup(
                    db,
                    **rawdoc_dict
                )
                logger.info(f"Raw doc created: {is_new}, Source: {source_name}, Title: {article.get('title', '')}")
                if is_new:
                    stats["raw_docs_saved"] += 1
                    # Create event from raw doc
                    try:
                        pub_date = None
                        if article.get("publishedAt"):
                            try:
                                pub_str = article["publishedAt"].split("T")[0]
                                pub_date = datetime.strptime(
                                    pub_str, "%Y-%m-%d"
                                ).date()
                            except Exception:
                                pass
                        event = self.normalizer.normalize_and_create_event(db, raw_doc, source_name.upper(), company_name)
                        if event:
                            stats["events_created"] += 1
                            bigquery_writer.queue("solid-topic-443216-b2.risk_monitoring.events", event)
                            logger.info(f"Queued event {getattr(event, 'event_id', None)} for BigQuery: {getattr(event, 'title', None)}")
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                stats["total_processed"] += 1
            except Exception as e:
                stats["errors"].append(f"RSS result processing error: {str(e)}")
        return stats
    
    def _process_yahoo_finance_results(
        self,
        db: Session,
        financial_data_list: list,
        company_name: str
    ) -> dict:
        """Process and save Yahoo Finance results"""
        stats = {"raw_docs_saved": 0, "events_created": 0, "total_processed": 0, "errors": []}
        for financial_data in financial_data_list:
            try:
                payload_bytes = json.dumps(financial_data, ensure_ascii=False).encode('utf-8')
                meta = {
                    "company_name": company_name,
                    "url": financial_data.get("url", ""),
                    "ticker": financial_data.get("ticker", ""),
                    "risk_level": financial_data.get("risk_level", ""),
                    "market_cap": financial_data.get("market_cap", ""),
                }
                rawdoc_dict = self.build_rawdoc_dict("YAHOO_FINANCE", payload_bytes, meta)
                raw_doc, is_new = self.raw_docs_crud.create_with_dedup(
                    db,
                    **rawdoc_dict
                )
                logger.info(f"Raw doc created: {is_new}, Source: YAHOO_FINANCE, Title: {financial_data.get('ticker', '')}")
                if is_new:
                    stats["raw_docs_saved"] += 1
                    # Create event from raw doc
                    try:
                        event = self.normalizer.normalize_and_create_event(db, raw_doc, "YAHOO_FINANCE", company_name)
                        if event:
                            stats["events_created"] += 1
                            bigquery_writer.queue("solid-topic-443216-b2.risk_monitoring.events", event)
                            logger.info(f"Queued event {getattr(event, 'event_id', None)} for BigQuery: {getattr(event, 'title', None)}")
                    except Exception as e:
                        stats["errors"].append(f"Event creation error: {str(e)}")
                stats["total_processed"] += 1
            except Exception as e:
                stats["errors"].append(f"Yahoo Finance result processing error: {str(e)}")
        return stats
    
    def get_database_stats(self, db: Session) -> Dict[str, Any]:
        """Get database statistics"""
        raw_docs_stats = self.raw_docs_crud.get_stats(db)
        events_stats = self.events_crud.get_risk_summary(db, days_back=30)
        
        return {
            "raw_docs": raw_docs_stats,
            "events": events_stats,
            "total_documents": raw_docs_stats["total"] + events_stats["total"]
        }


# Global instance
db_integration = DatabaseIntegrationService() 