#!/usr/bin/env python3
"""
BigQuery CRUD operations for Raw Documents model
"""

import logging
import hashlib
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import bigquery
from app.crud.bigquery_crud import BigQueryCRUDBase

logger = logging.getLogger(__name__)


class BigQueryRawDocsCRUD(BigQueryCRUDBase):
    """BigQuery CRUD operations for Raw Documents model"""
    
    def __init__(self):
        super().__init__(table_name="raw_docs")
    
    def generate_raw_id(self, payload: bytes) -> str:
        """Generate SHA-256 hash for deduplication"""
        return hashlib.sha256(payload).hexdigest()
    
    async def create_with_dedup(
        self, 
        source: str,
        payload: bytes,
        meta: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Create raw doc with deduplication
        Returns:
            tuple: (RawDoc, is_new) where is_new=True if document was just created
        """
        try:
            raw_id = self.generate_raw_id(payload)
            meta = meta or {}
            fetched_at = datetime.utcnow().isoformat()
            
            # Check if document already exists
            existing = await self.get_by_id(raw_id, id_field="raw_id")
            if existing:
                logger.debug(f"Raw document {raw_id} already exists")
                return existing, False  # Existing document, not new
            
            # Create new document - map to actual BigQuery table schema
            doc_data = {
                "raw_id": raw_id,  # Use raw_id as primary key (matches existing table)
                "source": source,
                "payload": payload,  # Keep as bytes - BigQuery will handle base64 encoding
                "meta": json.dumps(meta) if meta else "{}",  # Store as JSON string
                "fetched_at": fetched_at,
                "retries": 0,
                "status": None,  # Use status field (matches existing table)
            }
            
            result = await self.create(doc_data)
            logger.info(f"✅ Created new raw document: {raw_id}")
            return result, True  # New document created
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_with_dedup failed: {e}")
            return None, False
    
    async def get_unparsed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unparsed documents (status IS NULL)"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE status IS NULL
            ORDER BY fetched_at ASC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_unparsed failed: {e}")
            return []
    
    async def mark_parsed(self, raw_id: str) -> bool:
        """Mark document as parsed"""
        try:
            update_data = {
                "status": "parsed",
            }
            
            result = await self.update(raw_id, update_data, id_field="raw_id")
            if result:
                logger.info(f"✅ Marked document as parsed: {raw_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery mark_parsed failed: {e}")
            return False
    
    async def mark_error(self, raw_id: str) -> bool:
        """Mark document as error and increment retry count"""
        try:
            # Get current document
            doc = await self.get_by_id(raw_id, id_field="raw_id")
            if not doc:
                logger.warning(f"Document {raw_id} not found for error marking")
                return False
            
            # Increment retry count
            current_retries = doc.get('retries', 0)
            new_retries = current_retries + 1
            
            update_data = {
                "retries": new_retries,
                "status": "error" if new_retries < 5 else "dlq",
            }
            
            result = await self.update(raw_id, update_data, id_field="raw_id")
            if result:
                logger.info(f"✅ Marked document as error: {raw_id} (retries: {new_retries})")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery mark_error failed: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        try:
            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status IS NULL THEN 1 END) as unparsed,
                COUNT(CASE WHEN status = 'parsed' THEN 1 END) as parsed,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as errors,
                COUNT(CASE WHEN status = 'dlq' THEN 1 END) as dlq
            FROM `{self.table_id}`
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                return {
                    "total": row.total,
                    "unparsed": row.unparsed,
                    "parsed": row.parsed,
                    "errors": row.errors,
                    "dlq": row.dlq
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_stats failed: {e}")
            return {}
    
    async def vacuum_old(self, days_old: int = 30) -> int:
        """Delete old parsed documents"""
        try:
            query = f"""
            DELETE FROM `{self.table_id}`
            WHERE status = 'parsed'
              AND fetched_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days_old)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            result = query_job.result()
            
            # Get the number of deleted rows
            deleted_count = result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
            logger.info(f"✅ Vacuumed {deleted_count} old documents from {self.table_name}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ BigQuery vacuum_old failed: {e}")
            return 0
    
    async def get_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get documents by source"""
        try:
            return await self.get_multi(filters={"source": source}, limit=limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_source failed: {e}")
            return []
    
    async def get_error_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get documents with errors"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE status = 'error'
            ORDER BY fetched_at DESC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_error_documents failed: {e}")
            return []


# Global instance
bigquery_raw_docs = BigQueryRawDocsCRUD() 