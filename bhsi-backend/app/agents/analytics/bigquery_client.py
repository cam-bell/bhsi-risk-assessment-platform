#!/usr/bin/env python3
"""
BigQuery Analytics Client - Direct BigQuery Integration
Provides analytics capabilities for company risk assessment
"""

import logging
from typing import Dict, Any
from google.cloud import bigquery
from app.core.config import settings


logger = logging.getLogger(__name__)


class BigQueryClient:
    """Client for direct BigQuery integration"""
    
    def __init__(self):
        """Initialize BigQuery client"""
        try:
            self.client = bigquery.Client()
            self.project_id = settings.GCP_PROJECT_ID
            self.dataset_id = settings.BIGQUERY_DATASET_ID
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            self.client = None
            
    async def health_check(self) -> Dict[str, Any]:
        """Check BigQuery service health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "BigQuery client not initialized"
                }
                
            # Test query
            query = f"""
            SELECT COUNT(*) as count 
            FROM `{self.project_id}.{self.dataset_id}.events`
            LIMIT 1
            """
            query_job = self.client.query(query)
            results = query_job.result()
            rows = list(results)
            
            return {
                "status": "healthy",
                "event_count": rows[0].count if rows else 0
            }
        except Exception as e:
            logger.error(f"BigQuery health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_company_analytics(
        self, 
        company_name: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a company
        
        Args:
            company_name: Name of the company to analyze
            days_back: Number of days to look back for data
        """
        try:
            if not self.client:
                return self._get_fallback_analytics(company_name)
                
            # Query for company events using exact schema
            query = f"""
            WITH company_events AS (
                SELECT 
                    e.*,
                    c.name as company_name,
                    c.sector,
                    c.vat
                FROM `{self.project_id}.{self.dataset_id}.events` e
                LEFT JOIN `{self.project_id}.{self.dataset_id}.companies` c
                    ON e.vat = c.vat
                WHERE 
                    LOWER(c.name) LIKE LOWER(@company_name)
                    AND e.pub_date >= TIMESTAMP_SUB(
                        CURRENT_TIMESTAMP(), 
                        INTERVAL @days INTEGER DAY
                    )
            )
            SELECT
                ANY_VALUE(company_name) as company_name,
                ANY_VALUE(vat) as vat,
                ANY_VALUE(sector) as sector,
                COUNT(*) as total_events,
                COUNTIF(risk_label = 'HIGH') as high_risk_count,
                COUNTIF(risk_label = 'MEDIUM') as medium_risk_count,
                COUNTIF(risk_label = 'LOW') as low_risk_count
            FROM company_events
            GROUP BY vat
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "company_name", 
                        "STRING", 
                        f"%{company_name}%"
                    ),
                    bigquery.ScalarQueryParameter("days", "INT64", days_back),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                logger.warning(f"No data found for company: {company_name}")
                return self._get_fallback_analytics(company_name)
                
            row = results[0]
            
            # Get latest events in separate query
            latest_query = f"""
            SELECT 
                event_id,
                title,
                text,
                source,
                section,
                pub_date,
                url,
                embedding,
                embedding_model,
                risk_label,
                rationale,
                confidence,
                classifier_ts
            FROM `{self.project_id}.{self.dataset_id}.events` e
            JOIN `{self.project_id}.{self.dataset_id}.companies` c
                ON e.vat = c.vat
            WHERE LOWER(c.name) LIKE LOWER(@company_name)
            ORDER BY pub_date DESC, classifier_ts DESC
            LIMIT 10
            """
            
            latest_job = self.client.query(
                latest_query, 
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter(
                            "company_name", 
                            "STRING", 
                            f"%{company_name}%"
                        ),
                    ]
                )
            )
            
            latest_events = [{
                "event_id": event.event_id,
                "title": event.title,
                "text": event.text,
                "source": event.source,
                "section": event.section,
                "pub_date": event.pub_date.isoformat() if event.pub_date else None,
                "url": event.url,
                "risk_label": event.risk_label,
                "rationale": event.rationale,
                "confidence": event.confidence,
                "classifier_ts": (
                    event.classifier_ts.isoformat() 
                    if event.classifier_ts else None
                )
            } for event in latest_job.result()]
            
            # Get assessment data if available
            assessment_query = f"""
            SELECT 
                turnover,
                shareholding,
                bankruptcy,
                legal,
                corruption,
                overall,
                analysis_summary
            FROM `{self.project_id}.{self.dataset_id}.assessment` a
            WHERE company_id = @vat
            ORDER BY created_at DESC
            LIMIT 1
            """
            
            assessment_job = self.client.query(
                assessment_query,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("vat", "STRING", row.vat),
                    ]
                )
            )
            
            assessment_results = list(assessment_job.result())
            assessment = assessment_results[0] if assessment_results else None
            
            return {
                "company_name": row.company_name,
                "vat": row.vat,
                "sector": row.sector,
                "total_events": row.total_events,
                "risk_distribution": {
                    "HIGH": row.high_risk_count,
                    "MEDIUM": row.medium_risk_count,
                    "LOW": row.low_risk_count
                },
                "latest_events": latest_events,
                "assessment": {
                    "turnover": assessment.turnover if assessment else None,
                    "shareholding": assessment.shareholding if assessment else None,
                    "bankruptcy": assessment.bankruptcy if assessment else None,
                    "legal": assessment.legal if assessment else None,
                    "corruption": assessment.corruption if assessment else None,
                    "overall": assessment.overall if assessment else None,
                    "summary": (
                        assessment.analysis_summary if assessment else None
                    )
                } if assessment else None
            }
                    
        except Exception as e:
            logger.error(f"BigQuery analytics error for {company_name}: {e}")
            return self._get_fallback_analytics(company_name)
    
    async def get_risk_trends(self, days_back: int = 90) -> Dict[str, Any]:
        """Get overall risk trends across the system"""
        try:
            if not self.client:
                return self._get_fallback_trends()
                
            query = f"""
            SELECT 
                DATE(pub_date) as date,
                risk_label,
                source,
                COUNT(*) as event_count,
                COUNT(DISTINCT vat) as company_count,
                AVG(confidence) as avg_confidence
            FROM `{self.project_id}.{self.dataset_id}.events`
            WHERE pub_date >= TIMESTAMP_SUB(
                CURRENT_TIMESTAMP(), 
                INTERVAL @days INTEGER DAY
            )
            GROUP BY date, risk_label, source
            ORDER BY date DESC
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("days", "INT64", days_back),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            trends = [{
                "date": row.date.isoformat(),
                "risk_label": row.risk_label,
                "source": row.source,
                "event_count": row.event_count,
                "company_count": row.company_count,
                "avg_confidence": float(row.avg_confidence) if row.avg_confidence else None
            } for row in results]
            
            return {
                "period": f"last_{days_back}_days",
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"BigQuery risk trends error: {e}")
            return self._get_fallback_trends()
    
    def _get_fallback_analytics(self, company_name: str) -> Dict[str, Any]:
        """Enhanced fallback analytics with realistic mock data"""
        return {
            "company_name": company_name,
            "vat": None,
            "sector": "Unknown",
            "total_events": 0,
            "risk_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "latest_events": [],
            "assessment": None,
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        }
    
    def _get_fallback_trends(self) -> Dict[str, Any]:
        """Enhanced fallback trends with realistic mock data"""
        return {
            "period": "last_90_days",
            "trends": [],
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        }