#!/usr/bin/env python3
"""
Analytics Service - Orchestrates analytics operations for BHSI
Combines BigQuery analytics with local data for comprehensive insights
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from .bigquery_client import BigQueryClient
from .cache_manager import analytics_cache

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Orchestrates analytics operations for the BHSI system"""
    
    def __init__(self):
        """Initialize analytics service"""
        self.bigquery_client = BigQueryClient()
        
    async def get_comprehensive_analytics(
        self, 
        company_name: str,
        include_trends: bool = True,
        include_sectors: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a company including trends and sectors
        
        Args:
            company_name: Name of the company to analyze
            include_trends: Whether to include risk trends
            include_sectors: Whether to include sector analysis
            use_cache: Whether to use caching
            
        Returns:
            Dict containing comprehensive analytics
        """
        # Check cache first
        if use_cache:
            cached_data = analytics_cache.get(
                "comprehensive_analytics",
                company_name=company_name,
                include_trends=include_trends,
                include_sectors=include_sectors
            )
            if cached_data:
                logger.info(f"Cache hit for {company_name} analytics")
                return cached_data
        
        try:
            # Get company-specific analytics
            company_analytics = await self.bigquery_client.get_company_analytics(
                company_name
            )
            
            # Get system-wide trends if requested
            trends = None
            if include_trends:
                trends = await self.bigquery_client.get_risk_trends()
            
            # Note: Sector analysis and alert summary are not available in 
            # BigQueryClient - they would need to be implemented or called via 
            # HTTP to the BigQuery service
            
            # Combine all analytics
            comprehensive_analytics = {
                "company": company_analytics,
                "generated_at": datetime.utcnow().isoformat(),
                "analytics_version": "2.0.0"
            }
            
            if trends:
                comprehensive_analytics["trends"] = trends
                
            # Add placeholder for sectors if requested
            if include_sectors:
                comprehensive_analytics["sectors"] = {
                    "message": ("Sector analysis not yet implemented in "
                               "BigQueryClient"),
                    "fallback": True
                }
            
            # Cache the result
            if use_cache:
                analytics_cache.set(
                    "comprehensive_analytics",
                    comprehensive_analytics,
                    company_name=company_name,
                    include_trends=include_trends,
                    include_sectors=include_sectors
                )
            
            return comprehensive_analytics
            
        except Exception as e:
            logger.error(f"Comprehensive analytics failed for {company_name}: {e}")
            return {
                "error": f"Analytics failed: {str(e)}",
                "company_name": company_name,
                "fallback": True
            }
    
    async def get_system_analytics(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get system-wide analytics including trends, alerts, and sectors
        
        Args:
            use_cache: Whether to use caching
            
        Returns:
            Dict containing system analytics
        """
        # Check cache first
        if use_cache:
            cached_data = analytics_cache.get("system_analytics")
            if cached_data:
                logger.info("Cache hit for system analytics")
                return cached_data
        
        try:
            # Get all system analytics in parallel
            trends = await self.bigquery_client.get_risk_trends()
            
            # Note: Alert summary and sector analysis are not available in 
            # BigQueryClient - they would need to be implemented or called via 
            # HTTP to the BigQuery service
            alerts = {
                "message": ("Alert summary not yet implemented in "
                           "BigQueryClient"),
                "fallback": True
            }
            sectors = {
                "message": ("Sector analysis not yet implemented in "
                           "BigQueryClient"), 
                "fallback": True
            }
            
            system_analytics = {
                "system_analytics": {
                    "trends": trends,
                    "alerts": alerts,
                    "sectors": sectors
                },
                "generated_at": datetime.utcnow().isoformat(),
                "analytics_version": "2.0.0"
            }
            
            # Cache the result
            if use_cache:
                analytics_cache.set("system_analytics", system_analytics)
            
            return system_analytics
            
        except Exception as e:
            logger.error(f"System analytics failed: {e}")
            return {
                "error": f"System analytics failed: {str(e)}",
                "fallback": True
            }
    
    async def get_risk_comparison(
        self, 
        companies: List[str],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Compare risk profiles across multiple companies
        
        Args:
            companies: List of company names to compare
            use_cache: Whether to use caching
            
        Returns:
            Dict containing risk comparison
        """
        # Check cache first
        if use_cache:
            cached_data = analytics_cache.get(
                "risk_comparison",
                companies=tuple(sorted(companies))  # Sort for consistent cache key
            )
            if cached_data:
                logger.info("Cache hit for risk comparison")
                return cached_data
        
        try:
            company_analytics = []
            
            for company_name in companies:
                analytics = await self.bigquery_client.get_company_analytics(
                    company_name
                )
                company_analytics.append(analytics)
            
            # Calculate comparison metrics
            comparison = self._calculate_risk_comparison(company_analytics)
            
            result = {
                "companies": company_analytics,
                "comparison": comparison,
                "generated_at": datetime.utcnow().isoformat(),
                "analytics_version": "2.0.0"
            }
            
            # Cache the result
            if use_cache:
                analytics_cache.set(
                    "risk_comparison",
                    result,
                    companies=tuple(sorted(companies))
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Risk comparison failed: {e}")
            return {
                "error": f"Risk comparison failed: {str(e)}",
                "companies": companies,
                "fallback": True
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all analytics services"""
        try:
            bigquery_health = await self.bigquery_client.health_check()
            cache_stats = analytics_cache.get_stats()
            
            return {
                "status": "healthy" if bigquery_health.get("status") == "healthy" else "degraded",
                "services": {
                    "bigquery": bigquery_health,
                    "cache": cache_stats
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_risk_comparison(
        self, 
        company_analytics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate risk comparison metrics across companies"""
        
        if not company_analytics:
            return {}
        
        # Extract risk distributions
        risk_distributions = []
        total_events = []
        
        for analytics in company_analytics:
            if "risk_distribution" in analytics:
                risk_distributions.append(analytics["risk_distribution"])
                total_events.append(analytics.get("total_events", 0))
        
        # Calculate averages
        avg_high_risk = 0
        avg_medium_risk = 0
        avg_low_risk = 0
        
        if risk_distributions:
            avg_high_risk = sum(
                dist.get("HIGH", 0) for dist in risk_distributions
            ) / len(risk_distributions)
            avg_medium_risk = sum(
                dist.get("MEDIUM", 0) for dist in risk_distributions
            ) / len(risk_distributions)
            avg_low_risk = sum(
                dist.get("LOW", 0) for dist in risk_distributions
            ) / len(risk_distributions)
        
        return {
            "average_risk_distribution": {
                "HIGH": round(avg_high_risk, 2),
                "MEDIUM": round(avg_medium_risk, 2),
                "LOW": round(avg_low_risk, 2)
            },
            "total_companies": len(company_analytics),
            "total_events": sum(total_events),
            "average_events_per_company": (
                sum(total_events) / len(company_analytics) 
                if company_analytics else 0
            )
        } 