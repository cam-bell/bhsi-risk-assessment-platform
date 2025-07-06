from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session  # noqa: F401
from sqlalchemy import func  # noqa: F401
import hashlib
from datetime import datetime
import json
import logging

from app.models.raw_docs import RawDoc
from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

# Global instance (or inject as needed)
bq_writer = BigQueryWriter()

class CRUDRawDoc:
    def generate_raw_id(self, payload: bytes, company_name: str) -> str:
        """Generate SHA-256 hash for deduplication"""
        return hashlib.sha256(payload + company_name.encode('utf-8')).hexdigest()

    def create_with_dedup(
        self, 
        db: Session = None, 
        *,
        source: str,
        payload: bytes,
        meta: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[Any], bool]:
        """Create raw doc with deduplication (INSERT OR IGNORE)
        Returns:
            tuple: (RawDoc, is_new) where is_new=True if document was just created
        """
        raw_id = self.generate_raw_id(payload, source)
        meta = meta or {}
        fetched_at = datetime.utcnow()

        # Fallback to SQLite
        try:
            existing = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            logger.info(f"Dedup check: raw_id={raw_id}, exists={bool(existing)}")
            if existing:
                return existing, False  # Existing document, not new
            db_obj = RawDoc(
                raw_id=raw_id,
                source=source,
                payload=payload,
                meta=meta,
                fetched_at=fetched_at
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            # Use centralized BigQueryWriter (buffered, async, retry)
            bq_writer.queue("raw_docs", db_obj)
            return db_obj, True  # New document created
        except Exception as e:
            logger.error(f"SQLite operation failed: {e}")
            db.rollback()
            existing_after_rollback = (
                db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            )
            return existing_after_rollback, False

    def get_unparsed(self, db: Session = None, limit: int = 100) -> List[Any]:
        """Get unparsed documents (status IS NULL)"""
        try:
            return (
                db.query(RawDoc)
                .filter(RawDoc.status.is_(None))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"SQLite get_unparsed failed: {e}")
            return []

    def mark_parsed(self, db: Session, raw_id: str) -> bool:
        """Mark document as parsed"""
        try:
            db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            if db_obj:
                db_obj.status = "parsed"
                db_obj.updated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"SQLite mark_parsed failed: {e}")
            db.rollback()
            return False

    def mark_error(self, db: Session, raw_id: str) -> bool:
        """Mark document as error and increment retry count"""
        try:
            db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            if db_obj:
                db_obj.retries += 1
                db_obj.status = "error" if db_obj.retries < 5 else "dlq"
                db_obj.updated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"SQLite mark_error failed: {e}")
            db.rollback()
            return False

    def get_stats(self, db: Session) -> Dict[str, int]:
        """Get processing statistics"""
        try:
            stats = {}
            stats["total"] = db.query(RawDoc).count()
            stats["unparsed"] = db.query(RawDoc).filter(RawDoc.status.is_(None)).count()
            stats["parsed"] = db.query(RawDoc).filter(RawDoc.status == "parsed").count()
            stats["errors"] = db.query(RawDoc).filter(RawDoc.status == "error").count()
            stats["dlq"] = db.query(RawDoc).filter(RawDoc.status == "dlq").count()
            return stats
        except Exception as e:
            logger.error(f"SQLite get_stats failed: {e}")
            return {}

    def vacuum_old(self, db: Session, days_old: int = 30) -> int:
        """Delete old parsed documents"""
        try:
            cutoff_date = datetime.utcnow().date()
            from datetime import timedelta
            cutoff_date = cutoff_date - timedelta(days=days_old)
            deleted = (
                db.query(RawDoc)
                .filter(RawDoc.status == "parsed")
                .filter(func.date(RawDoc.fetched_at) < cutoff_date)
                .delete()
            )
            db.commit()
            return deleted
        except Exception as e:
            logger.error(f"SQLite vacuum_old failed: {e}")
            db.rollback()
            return 0

raw_docs = CRUDRawDoc() 