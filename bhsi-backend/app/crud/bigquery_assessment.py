#!/usr/bin/env python3
"""
BigQuery CRUD operations for Assessment model
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.crud.bigquery_crud import BigQueryCRUDBase

logger = logging.getLogger(__name__)


class BigQueryAssessmentCRUD(BigQueryCRUDBase):
    """BigQuery CRUD operations for Assessment model"""
    
    def __init__(self):
        super().__init__(table_name="assessment")
    
    async def create_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assessment"""
        try:
            # Generate ID if not provided
            if 'id' not in assessment_data:
                assessment_data['id'] = str(uuid.uuid4())
            
            # Ensure required fields
            if 'company_id' not in assessment_data:
                raise ValueError("company_id is required")
            if 'user_id' not in assessment_data:
                raise ValueError("user_id is required")
            
            # Create assessment
            result = await self.create(assessment_data)
            logger.info(f"✅ Created assessment: {assessment_data.get('id', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_assessment failed: {e}")
            raise
    
    async def get_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all assessments for a company"""
        try:
            return await self.get_multi(filters={"company_id": company_id})
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_company failed: {e}")
            return []
    
    async def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all assessments by a user"""
        try:
            return await self.get_multi(filters={"user_id": user_id})
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_user failed: {e}")
            return []
    
    async def get_recent_assessments(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent assessments"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            ORDER BY created_at DESC
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_recent_assessments failed: {e}")
            return []
    
    async def get_high_risk_assessments(self) -> List[Dict[str, Any]]:
        """Get assessments with high risk levels"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE overall = 'red'
               OR legal = 'red'
               OR bankruptcy = 'red'
               OR corruption = 'red'
            ORDER BY created_at DESC
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_high_risk_assessments failed: {e}")
            return []
    
    async def update_assessment(self, assessment_id: str, assessment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update assessment"""
        try:
            result = await self.update(assessment_id, assessment_data)
            logger.info(f"✅ Updated assessment: {assessment_id}")
            return result
        except Exception as e:
            logger.error(f"❌ BigQuery update_assessment failed: {e}")
            return None
    
    async def get_assessment_stats(self) -> Dict[str, Any]:
        """Get assessment statistics"""
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_assessments,
                COUNT(CASE WHEN overall = 'red' THEN 1 END) as high_risk,
                COUNT(CASE WHEN overall = 'orange' THEN 1 END) as medium_risk,
                COUNT(CASE WHEN overall = 'green' THEN 1 END) as low_risk,
                COUNT(CASE WHEN created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY) THEN 1 END) as last_week,
                COUNT(CASE WHEN created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) THEN 1 END) as last_month
            FROM `{self.table_id}`
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                return {
                    "total_assessments": row.total_assessments,
                    "high_risk": row.high_risk,
                    "medium_risk": row.medium_risk,
                    "low_risk": row.low_risk,
                    "last_week": row.last_week,
                    "last_month": row.last_month
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_assessment_stats failed: {e}")
            return {}


# Global instance
bigquery_assessment = BigQueryAssessmentCRUD() 