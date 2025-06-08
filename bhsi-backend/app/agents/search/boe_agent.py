#!/usr/bin/env python3
"""
BOE Ingestion Agent - Fetches raw BOE data and stores in landing zone
"""

import json
import logging
import requests
import datetime
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Add the backend directory to Python path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.crud.raw_docs import raw_docs

# Import BOE functions - use absolute import to work when run directly
try:
    from app.agents.search.BOE import fetch_boe_summary, iter_items
except ImportError:
    # Fallback for when running script directly
    from BOE import fetch_boe_summary, iter_items

logger = logging.getLogger(__name__)


class BOEIngestionAgent:
    """Focused BOE ingestion agent - fetch and store raw documents"""
    
    def __init__(self):
        self.source = "BOE"
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database tables exist"""
        try:
            from app.db.init_db import init_database
            # Try to create tables if they don't exist
            init_database()
        except Exception as e:
            logger.warning(f"Database initialization check: {e}")
            # Continue anyway - tables might already exist
    
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