#!/usr/bin/env python3
"""
BigQuery Analytics Service - Cloud analytics replacement for SQLite
Handles analytics queries using the actual risk_monitoring dataset schema
"""

import os
import logging
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
client = None
project_id = None
dataset_id = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize BigQuery client on startup"""
    global client, project_id, dataset_id
    
    try:
        from google.cloud import bigquery
        
        project_id = os.getenv("PROJECT_ID", "solid-topic-443216-b2")
        dataset_id = os.getenv("DATASET_ID", "risk_monitoring")  # Updated to match actual dataset
        
        client = bigquery.Client(project=project_id)
        
        # Verify dataset exists
        dataset_ref = client.dataset(dataset_id)
        try:
            client.get_dataset(dataset_ref)
            logger.info(f"✅ Connected to BigQuery dataset: {project_id}.{dataset_id}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to dataset {project_id}.{dataset_id}: {e}")
            raise
        
        logger.info("🚀 BigQuery service initialized successfully")
        
    except ImportError:
        logger.warning("⚠️ google-cloud-bigquery not installed. Using mock mode.")
        client = MockBigQueryClient()
    except Exception as e:
        logger.error(f"❌ Failed to initialize BigQuery: {e}")
        client = MockBigQueryClient()
    
    yield
    
    # Cleanup
    logger.info("Shutting down BigQuery service...")

app = FastAPI(lifespan=lifespan, title="BigQuery Analytics Service")

class CompanyAnalyticsRequest(BaseModel):
    company_name: Optional[str] = None
    vat: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    risk_level: Optional[str] = None

class CompanyAnalyticsResponse(BaseModel):
    company_name: str
    vat: Optional[str] = None
    total_events: int
    risk_distribution: Dict[str, int]
    latest_events: List[Dict[str, Any]]
    risk_trend: List[Dict[str, Any]]
    alert_summary: Dict[str, Any]

class MockBigQueryClient:
    """Mock BigQuery client for local development"""
    
    def __init__(self):
        self.data = {
            "raw_docs": [],
            "events": [],
            "companies": []
        }
    
    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Mock query execution"""
        logger.info(f"Mock query: {sql[:100]}...")
        
        # Return sample data based on query type
        if "FROM events" in sql:
            return [
                {
                    "event_id": "NEWS:12345",
                    "title": "Financial irregularities detected - Empresa XYZ",
                    "risk_label": "HIGH",
                    "pub_date": "2024-01-15",
                    "vat": "ES123456789A",
                    "alerted": True
                }
            ]
        elif "FROM companies" in sql:
            return [
                {
                    "vat": "ES123456789A",
                    "company_name": "Empresa XYZ S.L.",
                    "sector": "Financial Services",
                    "client_tier": "Gold"
                }
            ]
        elif "COUNT" in sql:
            return [{"count": 42}]
        else:
            return []

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BigQuery Analytics Service",
        "version": "2.0.0",
        "description": "Cloud analytics service using risk_monitoring dataset",
        "dataset": f"{project_id}.{dataset_id}",
        "tables": ["raw_docs", "events", "companies"],
        "endpoints": {
            "health": "/health",
            "company_analytics": "/analytics/company/{identifier}",
            "vat_analytics": "/analytics/vat/{vat}",
            "risk_trends": "/analytics/risk-trends",
            "alert_summary": "/analytics/alerts",
            "sector_analysis": "/analytics/sectors",
            "raw_docs_stats": "/stats/raw-docs",
            "events_stats": "/stats/events"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if hasattr(client, 'query'):
            # Test query on actual tables
            test_queries = [
                f"SELECT COUNT(*) as count FROM `{project_id}.{dataset_id}.events` LIMIT 1",
                f"SELECT COUNT(*) as count FROM `{project_id}.{dataset_id}.companies` LIMIT 1",
                f"SELECT COUNT(*) as count FROM `{project_id}.{dataset_id}.raw_docs` LIMIT 1"
            ]
            
            results = {}
            for i, query in enumerate(test_queries):
                try:
                    result = list(client.query(query))
                    table_name = ["events", "companies", "raw_docs"][i]
                    # BigQuery returns Row objects, convert to dict for consistent access
                    if result:
                        row_dict = dict(result[0]) if hasattr(result[0], '_fields') else result[0]
                        results[table_name] = row_dict.get('count', 0)
                    else:
                        results[table_name] = 0
                except Exception as e:
                    results[f"table_{i}_error"] = str(e)
            
            return {
                "status": "healthy",
                "bigquery_connected": True,
                "dataset": f"{project_id}.{dataset_id}",
                "table_counts": results
            }
        else:
            return {
                "status": "healthy",
                "bigquery_connected": False,
                "mode": "mock"
            }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }

@app.get("/analytics/company/{identifier}")
async def get_company_analytics(identifier: str) -> CompanyAnalyticsResponse:
    """
    Get comprehensive analytics for a company by name or VAT
    
    Args:
        identifier: Company name or VAT number
    """
    
    try:
        # Determine if identifier is VAT (starts with country code) or company name
        is_vat = len(identifier) > 8 and identifier[:2].isalpha()
        
        if is_vat:
            # Search by VAT
            company_query = f"""
            SELECT vat, company_name, sector, client_tier
            FROM `{project_id}.{dataset_id}.companies`
            WHERE vat = '{identifier}'
            """
            
            events_filter = f"vat = '{identifier}'"
        else:
            # Search by company name
            company_query = f"""
            SELECT vat, company_name, sector, client_tier
            FROM `{project_id}.{dataset_id}.companies`
            WHERE LOWER(company_name) LIKE LOWER('%{identifier}%')
            LIMIT 1
            """
            
            events_filter = f"LOWER(title) LIKE LOWER('%{identifier}%') OR LOWER(text) LIKE LOWER('%{identifier}%')"
        
        # Get company information
        company_info = None
        if hasattr(client, 'query'):
            company_results = list(client.query(company_query))
            if company_results:
                # BigQuery returns Row objects, convert to dict for consistent access
                company_info = dict(company_results[0]) if hasattr(company_results[0], '_fields') else company_results[0]
        
        if not company_info and not hasattr(client, 'query'):
            # Mock company data
            company_info = {
                "vat": "ES123456789A",
                "company_name": identifier,
                "sector": "Unknown",
                "client_tier": "Standard"
            }
        
        # Events analytics query
        events_query = f"""
        SELECT 
            risk_label,
            COUNT(*) as count,
            AVG(CASE WHEN embedding_model IS NOT NULL THEN 1.0 ELSE 0.5 END) as avg_confidence
        FROM `{project_id}.{dataset_id}.events`
        WHERE {events_filter}
        GROUP BY risk_label
        ORDER BY count DESC
        """
        
        risk_distribution = {}
        total_events = 0
        
        if hasattr(client, 'query'):
            for row in client.query(events_query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                risk_level = row_dict.get('risk_label') or "UNKNOWN"
                count = row_dict.get('count', 0)
                risk_distribution[risk_level] = count
                total_events += count
        else:
            # Mock data
            risk_distribution = {"HIGH": 3, "MEDIUM": 8, "LOW": 15}
            total_events = 26
        
        # Latest events
        latest_query = f"""
        SELECT 
            event_id,
            title,
            risk_label,
            pub_date,
            url,
            source,
            vat,
            alerted,
            rationale
        FROM `{project_id}.{dataset_id}.events`
        WHERE {events_filter}
        ORDER BY pub_date DESC, classifier_ts DESC
        LIMIT 10
        """
        
        latest_events = []
        if hasattr(client, 'query'):
            for row in client.query(latest_query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                latest_events.append({
                    "event_id": row_dict.get("event_id"),
                    "title": row_dict.get("title"),
                    "risk_label": row_dict.get("risk_label"),
                    "pub_date": row_dict.get("pub_date").isoformat() if row_dict.get("pub_date") else None,
                    "url": row_dict.get("url"),
                    "source": row_dict.get("source"),
                    "vat": row_dict.get("vat"),
                    "alerted": row_dict.get("alerted"),
                    "rationale": row_dict.get("rationale")
                })
        else:
            # Mock data
            latest_events = [
                {
                    "event_id": "NEWS:12345",
                    "title": f"Financial investigation - {identifier}",
                    "risk_label": "HIGH",
                    "pub_date": "2024-01-15",
                    "url": "https://example.com/news/12345",
                    "source": "Financial Times",
                    "vat": company_info.get("vat") if company_info else None,
                    "alerted": True,
                    "rationale": "Regulatory investigation indicates high risk"
                }
            ]
        
        # Risk trend (last 30 days)
        trend_query = f"""
        SELECT 
            DATE(pub_date) as date,
            risk_label,
            COUNT(*) as count,
            SUM(CASE WHEN alerted THEN 1 ELSE 0 END) as alerts_triggered
        FROM `{project_id}.{dataset_id}.events`
        WHERE {events_filter}
          AND pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY DATE(pub_date), risk_label
        ORDER BY date DESC
        """
        
        risk_trend = []
        if hasattr(client, 'query'):
            for row in client.query(trend_query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                risk_trend.append({
                    "date": row_dict.get("date").isoformat() if row_dict.get("date") else None,
                    "risk_label": row_dict.get("risk_label"),
                    "count": row_dict.get("count", 0),
                    "alerts_triggered": row_dict.get("alerts_triggered", 0)
                })
        else:
            # Mock data
            risk_trend = [
                {"date": "2024-01-15", "risk_label": "HIGH", "count": 2, "alerts_triggered": 1},
                {"date": "2024-01-10", "risk_label": "MEDIUM", "count": 3, "alerts_triggered": 0}
            ]
        
        # Alert summary
        alert_summary = {
            "total_alerts": sum(1 for e in latest_events if e.get("alerted")),
            "high_risk_alerts": sum(
                1 for e in latest_events if e.get("risk_label") == "High-Legal" and e.get("alerted")
            ),
            "last_alert": max(
                (e.get("pub_date") for e in latest_events if e.get("alerted")), default=None
            )
        }
        
        return CompanyAnalyticsResponse(
            company_name=company_info.get("company_name", identifier) if company_info else identifier,
            vat=company_info.get("vat") if company_info else None,
            total_events=total_events,
            risk_distribution=risk_distribution,
            latest_events=latest_events,
            risk_trend=risk_trend,
            alert_summary=alert_summary
        )
        
    except Exception as e:
        logger.error(f"Company analytics query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/vat/{vat}")
async def get_vat_analytics(vat: str):
    """Get analytics specifically by VAT number"""
    return await get_company_analytics(vat)

@app.get("/analytics/risk-trends")
async def get_risk_trends():
    """Get overall risk trends across all companies and sectors"""
    
    try:
        query = f"""
        SELECT 
            DATE(pub_date) as date,
            risk_label,
            source,
            COUNT(*) as event_count,
            COUNT(DISTINCT vat) as unique_companies,
            COUNTIF(alerted = TRUE) as alerts_triggered
        FROM `{project_id}.{dataset_id}.events`
        WHERE pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY DATE(pub_date), risk_label, source
        ORDER BY date DESC, risk_label
        """
        
        trends = []
        if hasattr(client, 'query'):
            for row in client.query(query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                trends.append({
                    "date": row_dict.get("date").isoformat() if row_dict.get("date") else None,
                    "risk_label": row_dict.get("risk_label"),
                    "source": row_dict.get("source"),
                    "event_count": row_dict.get("event_count", 0),
                    "unique_companies": row_dict.get("unique_companies", 0),
                    "alerts_triggered": row_dict.get("alerts_triggered", 0)
                })
        else:
            # Mock data
            trends = [
                {
                    "date": "2024-01-15", 
                    "risk_label": "HIGH", 
                    "source": "NEWS_API",
                    "event_count": 15, 
                    "unique_companies": 8,
                    "alerts_triggered": 5
                }
            ]
        
        return {
            "period": "last_90_days",
            "trends": trends,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk trends query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/alerts")
async def get_alert_summary():
    """Get summary of all alerts across the system"""
    
    try:
        query = f"""
        SELECT 
            risk_label,
            source,
            COUNT(*) as total_events,
            SUM(CASE WHEN alerted THEN 1 ELSE 0 END) as alerts_triggered,
            MAX(alerted_at) as last_alert_time
        FROM `{project_id}.{dataset_id}.events`
        WHERE pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY risk_label, source
        ORDER BY alerts_triggered DESC
        """
        
        alerts = []
        if hasattr(client, 'query'):
            for row in client.query(query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                alerts.append({
                    "risk_label": row_dict.get("risk_label"),
                    "source": row_dict.get("source"),
                    "total_events": row_dict.get("total_events", 0),
                    "alerts_triggered": row_dict.get("alerts_triggered", 0),
                    "alert_rate": row_dict.get("alerts_triggered", 0) / row_dict.get("total_events", 1) if row_dict.get("total_events", 0) > 0 else 0,
                    "last_alert_time": row_dict.get("last_alert_time").isoformat() if row_dict.get("last_alert_time") else None
                })
        else:
            # Mock data
            alerts = [
                {
                    "risk_label": "HIGH",
                    "source": "NEWS_API",
                    "total_events": 25,
                    "alerts_triggered": 8,
                    "alert_rate": 0.32,
                    "last_alert_time": "2024-01-15T10:30:00Z"
                }
            ]
        
        return {
            "period": "last_30_days",
            "alert_summary": alerts,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Alert summary query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/sectors")
async def get_sector_analysis():
    """Get risk analysis by industry sector"""
    
    try:
        query = f"""
        SELECT 
            c.sector,
            c.client_tier,
            COUNT(DISTINCT c.vat) as total_companies,
            COUNT(e.event_id) as total_events,
            SUM(CASE WHEN e.risk_label = 'HIGH' THEN 1 ELSE 0 END) as high_risk_events,
            SUM(CASE WHEN e.alerted THEN 1 ELSE 0 END) as alerts_triggered
        FROM `{project_id}.{dataset_id}.companies` c
        LEFT JOIN `{project_id}.{dataset_id}.events` e ON c.vat = e.vat
        WHERE e.pub_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) OR e.pub_date IS NULL
        GROUP BY c.sector, c.client_tier
        ORDER BY high_risk_events DESC, total_events DESC
        """
        
        sectors = []
        if hasattr(client, 'query'):
            for row in client.query(query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                sectors.append({
                    "sector": row_dict.get("sector"),
                    "client_tier": row_dict.get("client_tier"),
                    "total_companies": row_dict.get("total_companies", 0),
                    "total_events": row_dict.get("total_events", 0),
                    "high_risk_events": row_dict.get("high_risk_events", 0),
                    "alerts_triggered": row_dict.get("alerts_triggered", 0),
                    "risk_ratio": row_dict.get("high_risk_events", 0) / row_dict.get("total_events", 1) if row_dict.get("total_events", 0) > 0 else 0
                })
        else:
            # Mock data
            sectors = [
                {
                    "sector": "Financial Services",
                    "client_tier": "Gold",
                    "total_companies": 15,
                    "total_events": 45,
                    "high_risk_events": 8,
                    "alerts_triggered": 3,
                    "risk_ratio": 0.18
                }
            ]
        
        return {
            "period": "last_90_days",
            "sector_analysis": sectors,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Sector analysis query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/raw-docs")
async def get_raw_docs_stats():
    """Get statistics for raw documents ingestion"""
    
    try:
        query = f"""
        SELECT 
            source,
            status,
            DATE(fetched_at) as fetch_date,
            COUNT(*) as document_count,
            SUM(CASE WHEN retries > 0 THEN 1 ELSE 0 END) as retry_count,
            AVG(retries) as avg_retries
        FROM `{project_id}.{dataset_id}.raw_docs`
        WHERE fetched_at >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY source, status, DATE(fetched_at)
        ORDER BY fetch_date DESC, document_count DESC
        """
        
        stats = []
        if hasattr(client, 'query'):
            for row in client.query(query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                stats.append({
                    "source": row_dict.get("source"),
                    "status": row_dict.get("status"),
                    "fetch_date": row_dict.get("fetch_date").isoformat() if row_dict.get("fetch_date") else None,
                    "document_count": row_dict.get("document_count", 0),
                    "retry_count": row_dict.get("retry_count", 0),
                    "avg_retries": float(row_dict.get("avg_retries", 0)) if row_dict.get("avg_retries") else 0
                })
        else:
            # Mock data
            stats = [
                {
                    "source": "NEWS_API",
                    "status": "success",
                    "fetch_date": "2024-01-15",
                    "document_count": 150,
                    "retry_count": 5,
                    "avg_retries": 0.03
                }
            ]
        
        return {
            "period": "last_7_days",
            "raw_docs_stats": stats,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Raw docs stats query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/events")
async def get_events_stats():
    """Get statistics for processed events"""
    
    try:
        query = f"""
        SELECT 
            source,
            risk_label,
            embedding_model,
            DATE(classifier_ts) as classification_date,
            COUNT(*) as event_count,
            AVG(CASE WHEN embedding_id IS NOT NULL THEN 1.0 ELSE 0.0 END) as embedding_rate,
            SUM(CASE WHEN alerted THEN 1 ELSE 0 END) as alert_count
        FROM `{project_id}.{dataset_id}.events`
        WHERE classifier_ts >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY source, risk_label, embedding_model, DATE(classifier_ts)
        ORDER BY classification_date DESC, event_count DESC
        """
        
        stats = []
        if hasattr(client, 'query'):
            for row in client.query(query):
                # BigQuery returns Row objects, convert to dict for consistent access
                row_dict = dict(row) if hasattr(row, '_fields') else row
                stats.append({
                    "source": row_dict.get("source"),
                    "risk_label": row_dict.get("risk_label"),
                    "embedding_model": row_dict.get("embedding_model"),
                    "classification_date": row_dict.get("classification_date").isoformat() if row_dict.get("classification_date") else None,
                    "event_count": row_dict.get("event_count", 0),
                    "embedding_rate": float(row_dict.get("embedding_rate", 0)) if row_dict.get("embedding_rate") else 0,
                    "alert_count": row_dict.get("alert_count", 0)
                })
        else:
            # Mock data
            stats = [
                {
                    "source": "NEWS_API",
                    "risk_label": "HIGH",
                    "embedding_model": "text-embedding-004",
                    "classification_date": "2024-01-15",
                    "event_count": 25,
                    "embedding_rate": 0.95,
                    "alert_count": 8
                }
            ]
        
        return {
            "period": "last_7_days",
            "events_stats": stats,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Events stats query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# CLI interface
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 