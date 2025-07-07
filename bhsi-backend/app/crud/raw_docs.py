from typing import List, Optional, Dict, Any
import hashlib
from datetime import datetime
import json
import logging

from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

# Global instance (or inject as needed)
bq_writer = BigQueryWriter()

class CRUDRawDoc:
    def generate_raw_id(self, payload: bytes, company_name: str) -> str:
        """Generate SHA-256 hash for deduplication"""
        return hashlib.sha256(payload + company_name.encode('utf-8')).hexdigest()

    async def create_with_dedup(
        self, 
        *,
        source: str,
        payload: bytes,
        meta: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[Any], bool]:
        """Create raw doc with deduplication (BigQuery only)
        Returns:
            tuple: (RawDoc, is_new) where is_new=True if document was just created
        """
        raw_id = self.generate_raw_id(payload, source)
        meta = meta or {}
        fetched_at = datetime.utcnow()

        # BigQuery only - no SQLite fallback
        try:
            # Check if document already exists in BigQuery
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            existing = await bigquery_raw_docs.get_by_id(raw_id, id_field="raw_id")
            if existing:
                return existing, False  # Existing document, not new
            
            # Create new document in BigQuery
            doc_data = {
                "raw_id": raw_id,
                "source": source,
                "payload": payload,
                "meta": meta,
                "fetched_at": fetched_at.isoformat(),
                "created_at": fetched_at.isoformat(),
                "updated_at": fetched_at.isoformat()
            }
            
            result = await bigquery_raw_docs.create(doc_data)
            logger.info(f"✅ Created raw doc in BigQuery: {raw_id}")
            return result, True  # New document created
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_with_dedup failed: {e}")
            return None, False

    async def get_unparsed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unparsed documents (status IS NULL) - BigQuery only"""
        try:
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            return await bigquery_raw_docs.get_unparsed_docs(limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_unparsed failed: {e}")
            return []

    async def mark_parsed(self, raw_id: str) -> bool:
        """Mark document as parsed - BigQuery only"""
        try:
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            update_data = {
                "status": "parsed",
                "updated_at": datetime.utcnow().isoformat()
            }
            result = await bigquery_raw_docs.update(raw_id, update_data, id_field="raw_id")
            return result is not None
        except Exception as e:
            logger.error(f"❌ BigQuery mark_parsed failed: {e}")
            return False

    async def mark_error(self, raw_id: str) -> bool:
        """Mark document as error and increment retry count - BigQuery only"""
        try:
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            
            # Get current document to check retries
            doc = await bigquery_raw_docs.get_by_id(raw_id, id_field="raw_id")
            if not doc:
                return False
            
            current_retries = doc.get("retries", 0)
            new_retries = current_retries + 1
            status = "error" if new_retries < 5 else "dlq"
            
            update_data = {
                "retries": new_retries,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await bigquery_raw_docs.update(raw_id, update_data, id_field="raw_id")
            return result is not None
        except Exception as e:
            logger.error(f"❌ BigQuery mark_error failed: {e}")
            return False

    async def get_stats(self) -> Dict[str, int]:
        """Get processing statistics - BigQuery only"""
        try:
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            return await bigquery_raw_docs.get_stats()
        except Exception as e:
            logger.error(f"❌ BigQuery get_stats failed: {e}")
            return {}

    async def vacuum_old(self, days_old: int = 30) -> int:
        """Delete old parsed documents - BigQuery only"""
        try:
            from app.crud.bigquery_raw_docs import bigquery_raw_docs
            return await bigquery_raw_docs.vacuum_old_docs(days_old)
        except Exception as e:
            logger.error(f"❌ BigQuery vacuum_old failed: {e}")
            return 0


# Global instance
raw_docs = CRUDRawDoc() 