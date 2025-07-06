#!/usr/bin/env python3
"""
BigQuery Analytics Client - Direct BigQuery Integration
Provides analytics capabilities for company risk assessment
"""

import logging
import traceback
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
        """
        try:
            if not self.client:
                return self._get_fallback_analytics(company_name)

            # Fetch company info for metadata
            company_query = f"""
            SELECT id, name, vat_number, sector
            FROM `{self.project_id}.{self.dataset_id}.companies`
            WHERE LOWER(name) LIKE LOWER(@company_name)
            LIMIT 1
            """
            company_job = self.client.query(
                company_query,
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
            company_results = list(company_job.result())
            company = company_results[0] if company_results else None

            # Query events by text search
            events_query = f"""
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
                classifier_ts,
                alerted
            FROM `{self.project_id}.{self.dataset_id}.events`
            WHERE pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
            AND (
                LOWER(title) LIKE LOWER(@company_name_search)
                OR LOWER(text) LIKE LOWER(@company_name_search)
            )
            ORDER BY pub_date DESC, classifier_ts DESC
            LIMIT 100
            """
            events_job = self.client.query(
                events_query,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("days", "INT64", days_back),
                        bigquery.ScalarQueryParameter(
                            "company_name_search",
                            "STRING",
                            f"%{company_name}%"
                        ),
                    ]
                )
            )
            events_results = list(events_job.result())

            # Aggregate risk counts and alerts
            high_risk_count = sum(1 for e in events_results if e.risk_label == 'HIGH')
            medium_risk_count = sum(1 for e in events_results if e.risk_label == 'MEDIUM')
            low_risk_count = sum(1 for e in events_results if e.risk_label == 'LOW')
            total_alerts = sum(1 for e in events_results if getattr(e, 'alerted', False))
            alerted_events = [e for e in events_results if getattr(e, 'alerted', False)]
            last_alert = max(
                (e.pub_date.isoformat() for e in alerted_events if e.pub_date),
                default=None
            )

            latest_events = [{
                "event_id": event.event_id,
                "title": event.title,
                "text": (event.text[:500] if event.text else ""),
                "source": event.source,
                "section": event.section,
                "pub_date": event.pub_date.isoformat() if event.pub_date else None,
                "url": event.url,
                "risk_label": event.risk_label,
                "rationale": event.rationale,
                "confidence": (float(event.confidence) if event.confidence else None),
                "classifier_ts": (
                    event.classifier_ts.isoformat() if event.classifier_ts else None
                ),
                "alerted": (bool(event.alerted) if event.alerted is not None else False)
            } for event in events_results[:10]]

            # Get assessment data if available with timestamps
            assessment_query = f"""
            SELECT 
                turnover,
                shareholding,
                bankruptcy,
                legal,
                corruption,
                overall,
                analysis_summary,
                created_at
            FROM `{self.project_id}.{self.dataset_id}.assessment` a
            WHERE company_id = @company_id
            ORDER BY created_at DESC
            LIMIT 1
            """
            assessment_job = self.client.query(
                assessment_query,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter(
                            "company_id",
                            "STRING",
                            company.id if company else None
                        ),
                    ]
                )
            )
            assessment_results = list(assessment_job.result())
            assessment = assessment_results[0] if assessment_results else None

            return {
                "company_name": company.name if company else company_name,
                "company_id": company.id if company else None,
                "vat_number": company.vat_number if company else None,
                "sector": company.sector if company else None,
                "total_events": len(events_results),
                "risk_distribution": {
                    "HIGH": high_risk_count,
                    "MEDIUM": medium_risk_count,
                    "LOW": low_risk_count
                },
                "latest_events": latest_events,
                "alert_summary": {
                    "total_alerts": total_alerts,
                    "high_risk_events": high_risk_count,
                    "last_alert": last_alert
                },
                "assessment": {
                    "turnover": assessment.turnover if assessment else None,
                    "shareholding": assessment.shareholding if assessment else None,
                    "bankruptcy": assessment.bankruptcy if assessment else None,
                    "legal": assessment.legal if assessment else None,
                    "corruption": assessment.corruption if assessment else None,
                    "overall": assessment.overall if assessment else None,
                    "summary": (
                        assessment.analysis_summary if assessment else None
                    ),
                    "last_updated": (
                        assessment.created_at.isoformat() 
                        if assessment and assessment.created_at else None
                    )
                } if assessment else None
            }
        except Exception as e:
            logger.error(f"BigQuery analytics error for {company_name}: {e}")
            traceback.print_exc()  # Enhanced error debugging
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
            WHERE pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
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
        try:
            from .mock_analytics import generate_mock_analytics
            return generate_mock_analytics(company_name)
        except ImportError:
            # Simple fallback if mock_analytics not available
            return {
                "company_name": company_name,
                "vat": None,
                "sector": "Unknown",
                "total_events": 0,
                "risk_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "latest_events": [],
                "alert_summary": {
                    "total_alerts": 0,
                    "high_risk_events": 0,
                    "last_alert": None
                },
                "assessment": None,
                "fallback": True,
                "message": "Using fallback data - BigQuery service unavailable"
            }
    
    def _get_fallback_trends(self) -> Dict[str, Any]:
        """Enhanced fallback trends with realistic mock data"""
        try:
            from .mock_analytics import generate_mock_risk_trends
            return generate_mock_risk_trends()
        except ImportError:
            # Simple fallback if mock_analytics not available
            return {
                "period": "last_90_days",
                "trends": [],
                "fallback": True,
                "message": "Using fallback data - BigQuery service unavailable"
            }