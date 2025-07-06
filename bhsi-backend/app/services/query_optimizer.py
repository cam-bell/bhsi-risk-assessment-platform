#!/usr/bin/env python3
"""
Query Optimizer - Optimize BigQuery queries for better performance
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimize BigQuery queries for better performance"""
    
    def __init__(self, client: bigquery.Client):
        self.client = client
    
    def optimize_events_query(
        self,
        company_name: Optional[str] = None,
        risk_level: Optional[str] = None,
        date_range: Optional[Dict[str, str]] = None,
        limit: int = 100
    ) -> str:
        """
        Generate optimized BigQuery query for events
        """
        # Base query with clustering optimization
        query = f"""
        SELECT *
        FROM `{self._get_table_id('events')}`
        WHERE 1=1
        """
        
        # Add filters with proper indexing
        if company_name:
            query += f" AND LOWER(company_name) LIKE LOWER('%{company_name}%')"
        
        if risk_level:
            query += f" AND risk_level = '{risk_level}'"
        
        if date_range:
            start_date = date_range.get('start')
            end_date = date_range.get('end')
            if start_date:
                query += f" AND publication_date >= '{start_date}'"
            if end_date:
                query += f" AND publication_date <= '{end_date}'"
        
        # Order by clustering fields for better performance
        query += f"""
        ORDER BY company_vat, risk_level, publication_date DESC
        LIMIT {limit}
        """
        
        return query
    
    def optimize_analytics_query(
        self,
        days_back: int = 30,
        group_by: str = "company_vat"
    ) -> str:
        """
        Generate optimized analytics query
        """
        query = f"""
        SELECT 
            {group_by},
            COUNT(*) as total_events,
            COUNT(CASE WHEN risk_level = 'High-Legal' THEN 1 END) as high_risk_count,
            COUNT(CASE WHEN risk_level = 'Medium-Reg' THEN 1 END) as medium_risk_count,
            COUNT(CASE WHEN risk_level = 'Low-Other' THEN 1 END) as low_risk_count,
            AVG(confidence) as avg_confidence,
            MAX(publication_date) as latest_event_date
        FROM `{self._get_table_id('events')}`
        WHERE publication_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {days_back} DAY)
        GROUP BY {group_by}
        ORDER BY high_risk_count DESC, total_events DESC
        """
        
        return query
    
    def optimize_search_cache_query(self, query_text: str, hours_back: int = 24) -> str:
        """
        Generate optimized query for search cache
        """
        query = f"""
        SELECT 
            query,
            results_count,
            search_timestamp,
            top_results
        FROM `{self._get_table_id('search_cache')}`
        WHERE search_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours_back} HOUR)
        AND LOWER(query) LIKE LOWER('%{query_text}%')
        ORDER BY search_timestamp DESC
        LIMIT 5
        """
        
        return query
    
    def create_partitioned_table(self, table_name: str, partition_field: str = "publication_date"):
        """
        Create partitioned table for better query performance
        """
        try:
            table_id = self._get_table_id(table_name)
            
            # Create table with partitioning
            table = bigquery.Table(table_id)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field
            )
            
            # Add clustering for better performance
            if table_name == "events":
                table.clustering_fields = ["company_vat", "risk_level", "source"]
            elif table_name == "assessments":
                table.clustering_fields = ["company_vat", "overall_risk", "created_at"]
            
            # Create the table
            table = self.client.create_table(table, exists_ok=True)
            logger.info(f"✅ Created partitioned table: {table_id}")
            
            return table
            
        except Exception as e:
            logger.error(f"❌ Failed to create partitioned table {table_name}: {e}")
            raise
    
    def optimize_table_schema(self, table_name: str):
        """
        Optimize table schema for better performance
        """
        try:
            table_id = self._get_table_id(table_name)
            
            # Get current table
            table = self.client.get_table(table_id)
            
            # Update clustering if not set
            if not table.clustering_fields:
                if table_name == "events":
                    table.clustering_fields = ["company_vat", "risk_level", "publication_date"]
                elif table_name == "assessments":
                    table.clustering_fields = ["company_vat", "overall_risk", "created_at"]
                
                # Update the table
                table = self.client.update_table(table, ["clustering_fields"])
                logger.info(f"✅ Updated clustering for table: {table_id}")
            
            return table
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize schema for {table_name}: {e}")
            raise
    
    def get_query_performance_stats(self, query_job: bigquery.QueryJob) -> Dict[str, Any]:
        """
        Get performance statistics for a query job
        """
        try:
            # Get query statistics
            stats = {
                "total_bytes_processed": query_job.total_bytes_processed,
                "total_bytes_billed": query_job.total_bytes_billed,
                "slot_millis": query_job.slot_millis,
                "creation_time": query_job.created,
                "start_time": query_job.started,
                "end_time": query_job.ended,
                "state": query_job.state
            }
            
            # Calculate timing
            if query_job.started and query_job.ended:
                duration = (query_job.ended - query_job.started).total_seconds()
                stats["duration_seconds"] = duration
                stats["duration_ms"] = duration * 1000
            
            # Calculate cost (approximate)
            bytes_per_tb = 1024**4
            cost_per_tb = 5.0  # USD per TB processed
            stats["estimated_cost_usd"] = (query_job.total_bytes_processed / bytes_per_tb) * cost_per_tb
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get query performance stats: {e}")
            return {"error": str(e)}
    
    def _get_table_id(self, table_name: str) -> str:
        """Get fully qualified table ID"""
        project_id = "solid-topic-443216-b2"
        dataset_id = "bhsi_dataset"
        return f"{project_id}.{dataset_id}.{table_name}"
    
    def create_search_cache_table(self):
        """
        Create optimized search cache table
        """
        schema = [
            bigquery.SchemaField("cache_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("query", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("results_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("search_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("top_results", "STRING", mode="NULLABLE"),  # JSON
            bigquery.SchemaField("performance_metrics", "STRING", mode="NULLABLE"),  # JSON
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        table_id = self._get_table_id("search_cache")
        table = bigquery.Table(table_id, schema=schema)
        
        # Add clustering for better performance
        table.clustering_fields = ["query", "search_timestamp"]
        
        # Create the table
        table = self.client.create_table(table, exists_ok=True)
        logger.info(f"✅ Created search cache table: {table_id}")
        
        return table


# Performance monitoring utilities
class QueryPerformanceMonitor:
    """Monitor and log query performance"""
    
    def __init__(self):
        self.query_times = []
        self.query_costs = []
    
    def log_query_performance(self, query: str, stats: Dict[str, Any]):
        """Log query performance metrics"""
        self.query_times.append(stats.get("duration_ms", 0))
        self.query_costs.append(stats.get("estimated_cost_usd", 0))
        
        logger.info(f"📊 Query Performance:")
        logger.info(f"   Duration: {stats.get('duration_ms', 0):.2f}ms")
        logger.info(f"   Bytes Processed: {stats.get('total_bytes_processed', 0):,}")
        logger.info(f"   Estimated Cost: ${stats.get('estimated_cost_usd', 0):.4f}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.query_times:
            return {"error": "No queries logged"}
        
        return {
            "total_queries": len(self.query_times),
            "average_query_time_ms": sum(self.query_times) / len(self.query_times),
            "fastest_query_ms": min(self.query_times),
            "slowest_query_ms": max(self.query_times),
            "total_cost_usd": sum(self.query_costs),
            "average_cost_usd": sum(self.query_costs) / len(self.query_costs)
        } 