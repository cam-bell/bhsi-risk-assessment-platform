from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

# Global instance (or inject as needed)
bigquery_writer = BigQueryWriter()

class CRUDAssessment:
    async def create(
        self,
        *,
        obj_in: Dict[str, Any]
    ) -> Any:
        """Create a new assessment (BigQuery only)"""
        try:
            from app.crud.bigquery_assessment import bigquery_assessment
            
            row = {
                "id": obj_in["id"],
                "company_id": obj_in["company_id"],
                "user_id": obj_in["user_id"],
                "turnover": obj_in.get("turnover"),
                "shareholding": obj_in.get("shareholding"),
                "bankruptcy": obj_in.get("bankruptcy"),
                "legal": obj_in.get("legal"),
                "corruption": obj_in.get("corruption"),
                "overall": obj_in.get("overall"),
                "google_results": obj_in.get("google_results"),
                "bing_results": obj_in.get("bing_results"),
                "gov_results": obj_in.get("gov_results"),
                "news_results": obj_in.get("news_results"),
                "rss_results": obj_in.get("rss_results"),
                "analysis_summary": obj_in.get("analysis_summary"),
                "created_at": obj_in.get("created_at", datetime.utcnow().isoformat()),
                "updated_at": obj_in.get("updated_at"),
            }
            
            result = await bigquery_assessment.create_assessment(row)
            logger.info(f"✅ Created assessment in BigQuery: {obj_in['id']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create assessment failed: {e}")
            return None

    async def update(
        self,
        *,
        assessment_id: str,
        obj_in: Dict[str, Any]
    ) -> Any:
        """Update an assessment (BigQuery only)"""
        try:
            from app.crud.bigquery_assessment import bigquery_assessment
            
            row = {"id": assessment_id}
            row.update(obj_in)
            row["updated_at"] = datetime.utcnow().isoformat()
            
            result = await bigquery_assessment.update_assessment(assessment_id, row)
            logger.info(f"✅ Updated assessment in BigQuery: {assessment_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery update assessment failed: {e}")
            return None

    async def get_by_id(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment by ID (BigQuery only)"""
        try:
            from app.crud.bigquery_assessment import bigquery_assessment
            return await bigquery_assessment.get_by_id(assessment_id)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_id assessment failed: {e}")
            return None

    async def get_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all assessments for a company (BigQuery only)"""
        try:
            from app.crud.bigquery_assessment import bigquery_assessment
            return await bigquery_assessment.get_by_company(company_id)
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_company assessment failed: {e}")
            return []

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get multiple assessments (BigQuery only)"""
        try:
            from app.crud.bigquery_assessment import bigquery_assessment
            return await bigquery_assessment.get_multi(skip, limit)
        except Exception as e:
            logger.error(f"❌ BigQuery get_multi assessment failed: {e}")
            return []


# Global instance
assessment = CRUDAssessment() 