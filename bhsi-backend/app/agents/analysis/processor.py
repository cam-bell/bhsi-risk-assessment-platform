#!/usr/bin/env python3
"""
BOE Document Processor - Normalizes raw_docs to events
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

# Add the backend directory to Python path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.crud.raw_docs import raw_docs
from app.crud.events import events

logger = logging.getLogger(__name__)

# Import BOE functions with error handling
try:
    from app.agents.search.BOE import full_text
except ImportError as e:
    logger.warning(f"BOE module import issue: {e}")
    def full_text(item):
        """Fallback function if BOE module fails"""
        return item.get("texto", item.get("titulo", ""))


class BOEDocumentProcessor:
    """Normalizes raw BOE documents into canonical events"""
    
    def __init__(self):
        self.source = "BOE"
    
    def process_unparsed_documents(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Process unparsed documents from raw_docs to events
        """
        logger.info(f"🔄 Starting document processing (batch size: {batch_size})")
        
        stats = {
            "processed": 0,
            "created_events": 0,
            "errors": 0,
            "skipped": 0
        }
        
        db = SessionLocal()
        try:
            # Get unparsed documents
            unparsed = raw_docs.get_unparsed(db, limit=batch_size)
            logger.info(f"📋 Found {len(unparsed)} unparsed documents")
            
            for raw_doc in unparsed:
                try:
                    stats["processed"] += 1
                    
                    # Parse the raw document
                    event = self._process_single_document(db, raw_doc)
                    
                    if event:
                        stats["created_events"] += 1
                        # Mark as parsed
                        raw_docs.mark_parsed(db, raw_doc.raw_id)
                        logger.debug(f"✅ Processed: {event.event_id}")
                    else:
                        stats["skipped"] += 1
                        # Still mark as parsed to avoid reprocessing
                        raw_docs.mark_parsed(db, raw_doc.raw_id)
                        logger.debug(f"⏭️ Skipped: {raw_doc.raw_id}")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Error processing {raw_doc.raw_id}: {e}")
                    # Mark as error
                    raw_docs.mark_error(db, raw_doc.raw_id)
            
            logger.info(f"✅ Processing complete: {stats}")
            return stats
            
        finally:
            db.close()
    
    def _process_single_document(self, db: Session, raw_doc) -> Optional[Any]:
        """Process a single raw document into an event"""
        try:
            # Parse the payload
            payload_str = raw_doc.payload.decode('utf-8')
            item = json.loads(payload_str)
            
            # Extract basic fields
            title = item.get("titulo", "").strip()
            section = item.get("seccion_codigo", "").strip()
            
            # Skip if no title (invalid document)
            if not title:
                logger.debug(f"Skipping document with no title: {raw_doc.raw_id}")
                return None
            
            # Get full text content
            try:
                text = full_text(item)
                if not text or len(text.strip()) < 50:
                    # Use title as fallback if full text is too short
                    text = title
            except Exception as e:
                logger.warning(f"Failed to get full text for {raw_doc.raw_id}: {e}")
                text = title
            
            # Parse publication date
            pub_date = self._parse_pub_date(item.get("fecha_publicacion"))
            
            # Determine risk_label (you may need to add logic to extract or classify it)
            risk_label = item.get("risk_label")
            if not risk_label:
                # Fallback or classification logic here if needed
                risk_label = "Unknown"
            
            # Create event
            event = events.create_from_raw(
                db,
                raw_id=raw_doc.raw_id,
                source=self.source,
                title=title,
                text=text,
                section=section,
                pub_date=pub_date,
                url=item.get("url_html", ""),
                alerted=risk_label in ["High-Legal", "High-Reg"]
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to process document {raw_doc.raw_id}: {e}")
            raise
    
    def _parse_pub_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse publication date from various formats"""
        if not date_str:
            return None
        
        try:
            # Try YYYY-MM-DD format
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Try YYYYMMDD format
            elif len(date_str) == 8 and date_str.isdigit():
                return datetime.strptime(date_str, "%Y%m%d").date()
            
            # Try DD/MM/YYYY format
            elif '/' in date_str:
                return datetime.strptime(date_str, "%d/%m/%Y").date()
            
            else:
                logger.warning(f"Unknown date format: {date_str}")
                return None
                
        except ValueError as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        db = SessionLocal()
        try:
            raw_stats = raw_docs.get_stats(db)
            event_stats = events.get_risk_summary(db, days_back=30)
            
            return {
                "raw_docs": raw_stats,
                "events": event_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def reprocess_failed(self) -> Dict[str, Any]:
        """Reprocess documents that failed with errors"""
        logger.info("🔄 Reprocessing failed documents")
        
        db = SessionLocal()
        try:
            # Reset error status for retry
            from app.models.raw_docs import RawDoc
            failed_docs = db.query(RawDoc).filter(RawDoc.status == "error").all()
            
            stats = {"reset": 0, "processed": 0}
            
            for doc in failed_docs:
                if doc.retries < 3:  # Only retry if not too many attempts
                    doc.status = None  # Reset to unparsed
                    doc.retries += 1
                    stats["reset"] += 1
            
            db.commit()
            
            # Process the reset documents
            if stats["reset"] > 0:
                process_stats = self.process_unparsed_documents(batch_size=stats["reset"])
                stats["processed"] = process_stats["created_events"]
            
            logger.info(f"✅ Reprocessing complete: {stats}")
            return stats
            
        finally:
            db.close()


class DataProcessor:
    """Processes search results for company analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_search_results(self, search_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Process raw search results into structured data
        """
        processed = {
            "google_results": [],
            "bing_results": [],
            "gov_results": [],
            "news_results": [],
            "summary": {
                "total_results": 0,
                "date_range": None,
                "key_findings": []
            }
        }
        
        total_results = 0
        dates = []
        key_findings = []
        
        # Process each search source
        for source, results in search_results.items():
            if not results:
                continue
                
            processed_source_results = []
            
            for result in results:
                if isinstance(result, dict):
                    # Extract standard fields
                    processed_result = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", result.get("description", "")),
                        "source": source,
                        "date": result.get("date", result.get("published_date"))
                    }
                    
                    processed_source_results.append(processed_result)
                    total_results += 1
                    
                    # Collect dates
                    if processed_result["date"]:
                        dates.append(processed_result["date"])
                    
                    # Extract key findings
                    if processed_result["title"]:
                        key_findings.append(processed_result["title"])
            
            # Store results by source
            if source.lower() in ["google", "google_agent"]:
                processed["google_results"] = processed_source_results
            elif source.lower() in ["bing", "bing_agent"]:
                processed["bing_results"] = processed_source_results
            elif source.lower() in ["gov", "government", "boe"]:
                processed["gov_results"] = processed_source_results
            elif source.lower() in ["news", "news_agent"]:
                processed["news_results"] = processed_source_results
        
        # Generate summary
        processed["summary"]["total_results"] = total_results
        processed["summary"]["key_findings"] = key_findings[:10]  # Top 10 findings
        
        if dates:
            processed["summary"]["date_range"] = {
                "earliest": min(dates),
                "latest": max(dates)
            }
        
        return processed
    
    def format_for_storage(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format processed results for database storage
        """
        return {
            "google_results": json.dumps(processed_results.get("google_results", [])),
            "bing_results": json.dumps(processed_results.get("bing_results", [])),
            "gov_results": json.dumps(processed_results.get("gov_results", [])),
            "news_results": json.dumps(processed_results.get("news_results", [])),
            "analysis_summary": json.dumps(processed_results.get("summary", {}))
        }


class EventNormalizer:
    """Normalizes raw documents from any source into canonical events."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def normalize_and_create_event(self, db, raw_doc, source, company_name=None):
        # Parse payload
        try:
            payload_str = raw_doc.payload.decode('utf-8')
            item = json.loads(payload_str)
        except Exception as e:
            self.logger.error(f"Failed to decode payload for {raw_doc.raw_id}: {e}")
            return None

        # Extract fields based on source
        if source == "BOE":
            title = item.get("titulo", "").strip()
            section = item.get("seccion_codigo", "").strip()
            text = item.get("text", title)
            pub_date = item.get("fechaPublicacion") or item.get("fecha_publicacion")
            url = item.get("url_html", "")
        elif source == "NEWSAPI":
            title = item.get("title", "").strip()
            section = None
            text = item.get("content", item.get("description", title))
            pub_date = item.get("publishedAt")
            url = item.get("url", "")
        else:  # RSS and others
            title = item.get("title", "").strip()
            section = item.get("category", None)
            text = item.get("content", item.get("description", title))
            pub_date = item.get("publishedAt")
            url = item.get("url", "")

        # Parse date
        parsed_date = None
        if pub_date:
            try:
                if "T" in pub_date:
                    pub_date = pub_date.split("T")[0]
                parsed_date = datetime.strptime(pub_date, "%Y-%m-%d").date()
            except Exception:
                pass

        # Determine risk_label (you may need to add logic to extract or classify it)
        risk_label = item.get("risk_label")
        if not risk_label:
            # Fallback or classification logic here if needed
            risk_label = "Unknown"

        # Create event
        from app.crud.events import events
        event = events.create_from_raw(
            db,
            raw_id=raw_doc.raw_id,
            source=source,
            title=title,
            text=text,
            section=section,
            pub_date=parsed_date,
            url=url,
            alerted=risk_label in ["High-Legal", "High-Reg"],
            company_name=company_name
        )
        return event


# CLI interface
if __name__ == "__main__":
    processor = BOEDocumentProcessor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            stats = processor.process_unparsed_documents(batch_size)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "stats":
            stats = processor.get_processing_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "retry":
            stats = processor.reprocess_failed()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    else:
        print("BOE Document Processor")
        print("Usage:")
        print("  python processor.py process [batch_size]")
        print("  python processor.py stats")
        print("  python processor.py retry") 