#!/usr/bin/env python3
"""
BOE Ingestion Agent - Fetches raw BOE data and stores in landing zone
"""

import json
import logging
import requests
from datetime import datetime, timedelta
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import aiohttp
from app.agents.search.base_agent import BaseSearchAgent
from app.core.config import settings
from app.agents.analysis.classifier import RiskClassifier
from app.agents.search.BOE import fetch_boe_summary, iter_items, full_text

# Add the backend directory to Python path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.crud.raw_docs import raw_docs

logger = logging.getLogger(__name__)


class BOEIngestionAgent(BaseSearchAgent):
    """BOE API integration for Spanish official gazette search (robust, decoupled)"""
    
    def __init__(self):
        super().__init__()
        self.classifier = RiskClassifier()
        self.source = "BOE"
    
    async def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = 7
    ) -> Dict[str, Any]:
        """
        Search for BOE documents about a company using robust, proven logic.
        """
        try:
            # Determine date range
            if not start_date or not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            results = []
            errors = []
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y%m%d")
                try:
                    summary = fetch_boe_summary(date_str)
                    for item in iter_items(summary):
                        try:
                            title = item.get("titulo", "")
                            # Check if company name appears in title or text
                            if query.lower() in title.lower():
                                text = full_text(item)
                                classification = await self.classifier.classify_text(
                                    text=text,
                                    title=title,
                                    source="BOE",
                                    section=item.get("seccion_codigo", "")
                                )
                                processed_doc = {
                                    "identificador": item.get("identificador", "Unknown"),
                                    "title": title,
                                    "section": item.get("seccion_codigo", ""),
                                    "date": item.get("fecha_publicacion", current_date.strftime("%Y-%m-%d")),
                                    "url": item.get("url_html", ""),
                                    "content": text,
                                    "risk_level": classification["label"],
                                    "confidence": classification["confidence"],
                                    "classification_reason": classification["reason"],
                                    "classification_method": classification["method"]
                                }
                                results.append(processed_doc)
                        except Exception as e:
                            logger.error(f"Error processing BOE item: {e}")
                            errors.append(str(e))
                except Exception as e:
                    logger.error(f"Error fetching/parsing BOE for {date_str}: {e}")
                    errors.append(f"{date_str}: {e}")
                current_date += timedelta(days=1)
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date} to {end_date}",
                    "total_results": len(results),
                    "errors": errors
                },
                "results": results
            }
        except Exception as e:
            logger.error(f"Error processing BOE results: {e}")
            return {
                "search_summary": {
                    "query": query,
                    "date_range": f"{start_date} to {end_date}",
                    "total_results": 0,
                    "errors": [str(e)]
                },
                "results": []
            }
    
    def ingest_boe_day(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest BOE documents for a specific day into raw_docs landing zone
        """
        if date_str is None:
            date_str = datetime.date.today().strftime("%Y%m%d")
        
        logger.info(f"🔄 Starting BOE ingestion for {date_str}")
        
        stats = {
            "date": date_str,
            "total_items": 0,
            "new_documents": 0,
            "duplicates": 0,
            "errors": 0
        }
        
        try:
            # Fetch BOE summary
            logger.info(f"📡 Fetching BOE summary for {date_str}")
            summary = fetch_boe_summary(date_str)
            
            db = SessionLocal()
            try:
                # Process each document
                for item in iter_items(summary):
                    stats["total_items"] += 1
                    
                    try:
                        # Prepare metadata
                        meta = {
                            "identificador": item.get("identificador", ""),
                            "titulo": item.get("titulo", ""),
                            "seccion_codigo": item.get("seccion_codigo", ""),
                            "seccion_nombre": item.get("seccion_nombre", ""),
                            "fecha_publicacion": item.get("fecha_publicacion", ""),
                            "url_html": item.get("url_html", ""),
                            "url_xml": item.get("url_xml", ""),
                            "pub_date": date_str
                        }
                        
                        # Convert document to bytes for storage
                        payload = json.dumps(item, ensure_ascii=False).encode('utf-8')
                        
                        # Store in landing zone with deduplication
                        raw_doc, is_new = raw_docs.create_with_dedup(
                            db,
                            source=self.source,
                            payload=payload,
                            meta=meta
                        )
                        
                        # Check if this is a newly created document or existing one
                        if is_new:
                            stats["new_documents"] += 1
                            logger.debug(f"📄 Stored: {item.get('identificador', 'Unknown')}")
                        else:
                            stats["duplicates"] += 1
                            logger.debug(f"🔄 Duplicate: {item.get('identificador', 'Unknown')}")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"❌ Error processing item {item.get('identificador', 'unknown')}: {e}")
                
                # Log final stats
                logger.info(f"✅ BOE ingestion complete: {stats}")
                
            finally:
                db.close()
                
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest BOE for {date_str}: {e}")
            stats["error"] = str(e)
            return stats
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics from landing zone"""
        db = SessionLocal()
        try:
            stats = raw_docs.get_stats(db)
            return stats
        finally:
            db.close()
    
    def vacuum_old_documents(self, days_old: int = 30) -> int:
        """Clean up old processed documents"""
        db = SessionLocal()
        try:
            deleted = raw_docs.vacuum_old(db, days_old)
            logger.info(f"🧹 Vacuumed {deleted} old documents")
            return deleted
        finally:
            db.close()


# CLI interface
if __name__ == "__main__":
    agent = BOEIngestionAgent()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "ingest":
            date_str = sys.argv[2] if len(sys.argv) > 2 else None
            stats = agent.ingest_boe_day(date_str)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "stats":
            stats = agent.get_ingestion_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "vacuum":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            deleted = agent.vacuum_old_documents(days)
            print(f"Deleted {deleted} old documents")
    
    else:
        print("BOE Ingestion Agent")
        print("Usage:")
        print("  python boe_agent.py ingest [date]")
        print("  python boe_agent.py stats")
        print("  python boe_agent.py vacuum [days_old]") 