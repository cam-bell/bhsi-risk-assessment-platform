from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import hashlib
import json
from datetime import datetime

from app.models.raw_docs import RawDoc


class CRUDRawDoc:
    def generate_raw_id(self, payload: bytes) -> str:
        """Generate SHA-256 hash for deduplication"""
        return hashlib.sha256(payload).hexdigest()

    def create_with_dedup(
        self, 
        db: Session, 
        *,
        source: str,
        payload: bytes,
        meta: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[RawDoc], bool]:
        """Create raw doc with deduplication (INSERT OR IGNORE)
        
        Returns:
            tuple: (RawDoc, is_new) where is_new=True if document was just created
        """
        raw_id = self.generate_raw_id(payload)
        
        # Check if already exists
        existing = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
        if existing:
            return existing, False  # Existing document, not new
        
        # Create new record
        db_obj = RawDoc(
            raw_id=raw_id,
            source=source,
            payload=payload,
            meta=meta or {},
            fetched_at=datetime.utcnow()
        )
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj, True  # New document created
        except Exception:
            db.rollback()
            # Try to get existing record (race condition)
            existing_after_rollback = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            return existing_after_rollback, False  # Existing document, not new

    def get_unparsed(self, db: Session, limit: int = 100) -> List[RawDoc]:
        """Get unparsed documents (status IS NULL)"""
        return (
            db.query(RawDoc)
            .filter(RawDoc.status.is_(None))
            .limit(limit)
            .all()
        )

    def mark_parsed(self, db: Session, raw_id: str) -> bool:
        """Mark document as parsed"""
        db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
        if db_obj:
            db_obj.status = "parsed"
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def mark_error(self, db: Session, raw_id: str) -> bool:
        """Mark document as error and increment retry count"""
        db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
        if db_obj:
            db_obj.retries += 1
            db_obj.status = "error" if db_obj.retries < 5 else "dlq"
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_stats(self, db: Session) -> Dict[str, int]:
        """Get processing statistics"""
        stats = {}
        
        # Count by status
        stats["total"] = db.query(RawDoc).count()
        stats["unparsed"] = db.query(RawDoc).filter(RawDoc.status.is_(None)).count()
        stats["parsed"] = db.query(RawDoc).filter(RawDoc.status == "parsed").count()
        stats["errors"] = db.query(RawDoc).filter(RawDoc.status == "error").count()
        stats["dlq"] = db.query(RawDoc).filter(RawDoc.status == "dlq").count()
        
        return stats

    def vacuum_old(self, db: Session, days_old: int = 30) -> int:
        """Delete old parsed documents"""
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


raw_docs = CRUDRawDoc() 