#!/usr/bin/env python3
"""
BigQuery Analytics Client - Integration with BigQuery Analytics Service
Provides analytics capabilities for company risk assessment
"""

import logging
import httpx
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class BigQueryClient:
    """Client for BigQuery Analytics Service integration"""
    
    def __init__(self):
        """Initialize BigQuery client"""
        self.base_url = settings.BIGQUERY_ANALYTICS_SERVICE_URL
        self.timeout = 30.0
        
    async def health_check(self) -> Dict[str, Any]:
        """Check BigQuery service health"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "unhealthy", "error": response.text}
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
            
        Returns:
            Dict containing company analytics
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/analytics/company/{company_name}"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"BigQuery analytics failed for {company_name}: "
                        f"{response.status_code}"
                    )
                    return self._get_fallback_analytics(company_name)
                    
        except Exception as e:
            logger.error(f"BigQuery analytics error for {company_name}: {e}")
            return self._get_fallback_analytics(company_name)
    
    async def get_risk_trends(
        self, 
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Get overall risk trends across the system
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dict containing risk trends
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/analytics/risk-trends"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"BigQuery risk trends failed: {response.status_code}"
                    )
                    return self._get_fallback_trends()
                    
        except Exception as e:
            logger.error(f"BigQuery risk trends error: {e}")
            return self._get_fallback_trends()
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get summary of all alerts across the system
        
        Returns:
            Dict containing alert summary
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/analytics/alerts"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"BigQuery alert summary failed: {response.status_code}"
                    )
                    return self._get_fallback_alerts()
                    
        except Exception as e:
            logger.error(f"BigQuery alert summary error: {e}")
            return self._get_fallback_alerts()
    
    async def get_sector_analysis(self) -> Dict[str, Any]:
        """
        Get risk analysis by industry sector
        
        Returns:
            Dict containing sector analysis
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/analytics/sectors"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"BigQuery sector analysis failed: "
                        f"{response.status_code}"
                    )
                    return self._get_fallback_sectors()
                    
        except Exception as e:
            logger.error(f"BigQuery sector analysis error: {e}")
            return self._get_fallback_sectors()
    
    def _get_fallback_analytics(self, company_name: str) -> Dict[str, Any]:
        """Fallback analytics when BigQuery service is unavailable"""
        return {
            "company_name": company_name,
            "vat": None,
            "total_events": 0,
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
            "latest_events": [],
            "risk_trend": [],
            "alert_summary": {
                "total_alerts": 0,
                "high_risk_events": 0,
                "last_alert": None
            },
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        }
    
    def _get_fallback_trends(self) -> Dict[str, Any]:
        """Fallback trends when BigQuery service is unavailable"""
        return {
            "period": "last_90_days",
            "trends": [],
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        }
    
    def _get_fallback_alerts(self) -> Dict[str, Any]:
        """Fallback alerts when BigQuery service is unavailable"""
        return {
            "period": "last_30_days",
            "alert_summary": [],
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        }
    
    def _get_fallback_sectors(self) -> Dict[str, Any]:
        """Fallback sectors when BigQuery service is unavailable"""
        return {
            "period": "last_90_days",
            "sector_analysis": [],
            "fallback": True,
            "message": "Using fallback data - BigQuery service unavailable"
        } 