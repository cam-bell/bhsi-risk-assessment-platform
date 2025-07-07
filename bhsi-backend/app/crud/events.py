from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging
from app.core.config import settings
from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

# Global instance (or inject as needed)
bq_writer = BigQueryWriter()

class CRUDEvent:
    async def create_from_raw(
        self,
        *,
        raw_id: str,
        source: str,
        title: str,
        text: str,
        section: Optional[str] = None,
        pub_date: Optional[date] = None,
        url: Optional[str] = None,
        alerted: Optional[bool] = None,
        company_name: Optional[str] = None
    ) -> Any:
        """Create event from raw document data - BigQuery only"""
        event_id = f"{source}:{raw_id}"
        
        # BigQuery only - no SQLite fallback
        try:
            from app.crud.bigquery_events import bigquery_events
            
            # Check if event already exists
            existing = await bigquery_events.get_by_id(event_id, id_field="event_id")
            if existing:
                return existing
            
            # Create event data
            event_data = {
                "event_id": event_id,
                "title": title,
                "text": text,
                "source": source,
                "section": section,
                "pub_date": pub_date.isoformat() if pub_date else None,
                "url": url,
                "alerted": alerted,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await bigquery_events.create_event(event_data)
            logger.info(f"✅ Created event in BigQuery: {event_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_from_raw failed: {e}")
            return None

    async def get_unembedded_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events that need embedding - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.get_unembedded_events(limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_unembedded_events failed: {e}")
            return []

    async def mark_embedded(
        self, 
        event_id: str, 
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ) -> bool:
        """Mark event as embedded - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.mark_embedded(event_id, embedding_model)
        except Exception as e:
            logger.error(f"❌ BigQuery mark_embedded failed: {e}")
            return False

    async def get_unclassified_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events that need risk classification - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.get_unclassified_events(limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_unclassified_events failed: {e}")
            return []

    async def update_risk_classification(
        self,
        event_id: str,
        risk_label: str,
        confidence: float,
        rationale: str
    ) -> bool:
        """Update risk classification fields for an event - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.update_risk_classification(
                event_id, risk_label, confidence, rationale
            )
        except Exception as e:
            logger.error(f"❌ BigQuery update_risk_classification failed: {e}")
            return False

    async def get_high_risk_events(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get high-risk events for notifications - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.get_high_risk_events(days_back)
        except Exception as e:
            logger.error(f"❌ BigQuery get_high_risk_events failed: {e}")
            return []

    async def get_risk_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """Get risk statistics for recent events - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.get_risk_summary(days_back)
        except Exception as e:
            logger.error(f"❌ BigQuery get_risk_summary failed: {e}")
            return {}

    async def search_by_company(self, company_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search events mentioning a specific company - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.search_by_company(company_name, limit)
        except Exception as e:
            logger.error(f"❌ BigQuery search_by_company failed: {e}")
            return []

    async def get_by_section(self, section: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by BOE section - BigQuery only"""
        try:
            from app.crud.bigquery_events import bigquery_events
            return await bigquery_events.get_by_section(section, limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_section failed: {e}")
            return []


# Global instance
events = CRUDEvent() 