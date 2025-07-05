#!/usr/bin/env python3
"""
BigQuery CRUD operations for Events model
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from google.cloud import bigquery
from app.crud.bigquery_crud import BigQueryCRUDBase

logger = logging.getLogger(__name__)


class BigQueryEventsCRUD(BigQueryCRUDBase):
    """BigQuery CRUD operations for Events model"""
    
    def __init__(self):
        super().__init__(table_name="events")
    
    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
        try:
            # Ensure event_id is present
            if 'event_id' not in event_data:
                raise ValueError("event_id is required")
            
            # Check if event already exists
            existing = await self.get_by_id(event_data['event_id'], id_field="event_id")
            if existing:
                logger.warning(f"Event with ID {event_data['event_id']} already exists")
                return existing
            
            # Create event
            result = await self.create(event_data)
            logger.info(f"✅ Created event: {event_data.get('event_id', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_event failed: {e}")
            raise
    
    async def get_unembedded_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events that need embedding"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE embedding_status IS NULL
            ORDER BY created_at ASC
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
            logger.error(f"❌ BigQuery get_unembedded_events failed: {e}")
            return []
    
    async def get_unclassified_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events that need risk classification"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE risk_level IS NULL
            ORDER BY created_at ASC
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
            logger.error(f"❌ BigQuery get_unclassified_events failed: {e}")
            return []
    
    async def mark_embedded(self, event_id: str, embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2") -> bool:
        """Mark event as embedded"""
        try:
            update_data = {
                "embedding_status": "vectorised",
                "embedding_model": embedding_model,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await self.update(event_id, update_data, id_field="event_id")
            if result:
                logger.info(f"✅ Marked event as embedded: {event_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery mark_embedded failed: {e}")
            return False
    
    async def update_risk_classification(
        self, 
        event_id: str, 
        risk_label: str, 
        confidence: float, 
        rationale: str
    ) -> bool:
        """Update risk classification for an event"""
        try:
            update_data = {
                "risk_level": risk_label,
                "confidence": confidence,
                "rationale": rationale,
                "classifier_ts": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await self.update(event_id, update_data, id_field="event_id")
            if result:
                logger.info(f"✅ Updated risk classification for event: {event_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery update_risk_classification failed: {e}")
            return False
    
    async def get_high_risk_events(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get high-risk events for notifications"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE risk_level = 'High-Legal'
              AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            ORDER BY confidence DESC
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days_back)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_high_risk_events failed: {e}")
            return []
    
    async def get_risk_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get risk statistics for recent events"""
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN risk_level = 'High-Legal' THEN 1 END) as high_legal,
                COUNT(CASE WHEN risk_level = 'Medium-Reg' THEN 1 END) as medium_reg,
                COUNT(CASE WHEN risk_level = 'Low-Other' THEN 1 END) as low_other,
                COUNT(CASE WHEN risk_level = 'Unknown' THEN 1 END) as unknown,
                COUNT(CASE WHEN embedding_status IS NULL THEN 1 END) as unembedded,
                COUNT(CASE WHEN risk_level IS NULL THEN 1 END) as unclassified
            FROM `{self.table_id}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days_back)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return {
                    "total_events": row.total_events,
                    "high_legal": row.high_legal,
                    "medium_reg": row.medium_reg,
                    "low_other": row.low_other,
                    "unknown": row.unknown,
                    "unembedded": row.unembedded,
                    "unclassified": row.unclassified
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_risk_summary failed: {e}")
            return {}
    
    async def search_by_company(self, company_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search events mentioning a specific company"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE LOWER(title) LIKE LOWER(@company_name)
               OR LOWER(text) LIKE LOWER(@company_name)
            ORDER BY pub_date DESC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("company_name", "STRING", f"%{company_name}%"),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery search_by_company failed: {e}")
            return []
    
    async def get_by_section(self, section: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by BOE section"""
        try:
            return await self.get_multi(filters={"section": section}, limit=limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_section failed: {e}")
            return []
    
    async def get_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by source"""
        try:
            return await self.get_multi(filters={"source": source}, limit=limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_source failed: {e}")
            return []


# Global instance
bigquery_events = BigQueryEventsCRUD() 