#!/usr/bin/env python3
"""
Async BigQuery Client for BHSI D&O Risk Assessment System
Handles background processing and batch operations without blocking API responses
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading

from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class BigQueryWriteRequest:
    """Represents a write request to BigQuery"""
    table_name: str
    data: List[Dict[str, Any]]
    operation: str = "insert"  # insert, update, upsert
    priority: int = 1  # 1=high, 2=medium, 3=low


class AsyncBigQueryClient:
    """Async BigQuery client with background processing"""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        
        # Background processing
        self.write_queue: List[BigQueryWriteRequest] = []
        self.queue_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="BigQuery")
        self.running = True
        
        # Start background processor
        self._start_background_processor()
    
    def _start_background_processor(self):
        """Start background thread for processing write queue"""
        def background_worker():
            while self.running:
                try:
                    # Process queue every 5 seconds
                    asyncio.run(self._process_write_queue())
                    asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Background BigQuery processor error: {e}")
                    asyncio.sleep(10)  # Wait longer on error
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        logger.info("🚀 BigQuery background processor started")
    
    async def _process_write_queue(self):
        """Process pending write requests"""
        with self.queue_lock:
            if not self.write_queue:
                return
            
            # Sort by priority (lower number = higher priority)
            self.write_queue.sort(key=lambda x: x.priority)
            
            # Process high priority items first
            high_priority = [req for req in self.write_queue if req.priority == 1]
            medium_priority = [req for req in self.write_queue if req.priority == 2]
            low_priority = [req for req in self.write_queue if req.priority == 3]
            
            # Process in priority order
            for requests in [high_priority, medium_priority, low_priority]:
                if requests:
                    await self._process_batch(requests)
                    # Remove processed requests
                    self.write_queue = [req for req in self.write_queue if req not in requests]
    
    async def _process_batch(self, requests: List[BigQueryWriteRequest]):
        """Process a batch of write requests"""
        for request in requests:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    self._execute_write_request,
                    request
                )
                logger.debug(f"✅ Processed BigQuery write: {request.table_name}")
            except Exception as e:
                logger.error(f"❌ BigQuery write failed for {request.table_name}: {e}")
    
    def _execute_write_request(self, request: BigQueryWriteRequest):
        """Execute a write request in a thread"""
        table_id = f"{self.project_id}.{self.dataset_id}.{request.table_name}"
        
        try:
            if request.operation == "insert":
                errors = self.client.insert_rows_json(table_id, request.data)
                if errors:
                    raise Exception(f"Insert errors: {errors}")
            elif request.operation == "upsert":
                # Use MERGE for upsert operations
                self._execute_upsert(table_id, request.data)
            else:
                raise ValueError(f"Unsupported operation: {request.operation}")
                
        except Exception as e:
            logger.error(f"BigQuery write execution failed: {e}")
            raise
    
    def _execute_upsert(self, table_id: str, data: List[Dict[str, Any]]):
        """Execute upsert operation using MERGE"""
        if not data:
            return
        
        # Build MERGE statement
        temp_table = f"temp_{uuid.uuid4().hex[:8]}"
        temp_table_id = f"{self.project_id}.{self.dataset_id}.{temp_table}"
        
        try:
            # Create temporary table
            schema = self.client.get_table(table_id).schema
            temp_table_obj = bigquery.Table(temp_table_id, schema=schema)
            self.client.create_table(temp_table_obj, exists_ok=True)
            
            # Insert data into temp table
            errors = self.client.insert_rows_json(temp_table_id, data)
            if errors:
                raise Exception(f"Temp table insert errors: {errors}")
            
            # Build MERGE statement
            merge_sql = self._build_merge_sql(table_id, temp_table_id, data[0].keys())
            
            # Execute MERGE
            query_job = self.client.query(merge_sql)
            query_job.result()  # Wait for completion
            
        finally:
            # Clean up temp table
            try:
                self.client.delete_table(temp_table_id, not_found_ok=True)
            except Exception as e:
                logger.warning(f"Failed to clean up temp table: {e}")
    
    def _build_merge_sql(self, target_table: str, source_table: str, columns: List[str]) -> str:
        """Build MERGE SQL statement for upsert"""
        # Assume first column is the primary key
        primary_key = list(columns)[0]
        
        update_set = ", ".join([
            f"{col} = S.{col}" for col in columns if col != primary_key
        ])
        
        insert_columns = ", ".join(columns)
        insert_values = ", ".join([f"S.{col}" for col in columns])
        
        return f"""
        MERGE `{target_table}` T
        USING `{source_table}` S
        ON T.{primary_key} = S.{primary_key}
        WHEN MATCHED THEN
            UPDATE SET {update_set}
        WHEN NOT MATCHED THEN
            INSERT ({insert_columns})
            VALUES ({insert_values})
        """
    
    async def queue_write(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        operation: str = "insert",
        priority: int = 2
    ) -> str:
        """
        Queue a write operation for background processing
        
        Args:
            table_name: Target table name
            data: Data to write
            operation: insert, update, or upsert
            priority: 1=high, 2=medium, 3=low
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        
        # Add timestamps if not present
        for row in data:
            if "created_at" not in row:
                row["created_at"] = datetime.utcnow().isoformat()
            if "updated_at" not in row:
                row["updated_at"] = datetime.utcnow().isoformat()
        
        request = BigQueryWriteRequest(
            table_name=table_name,
            data=data,
            operation=operation,
            priority=priority
        )
        
        with self.queue_lock:
            self.write_queue.append(request)
        
        logger.debug(f"📝 Queued BigQuery write: {table_name} ({len(data)} rows)")
        return request_id
    
    async def save_assessment(
        self,
        assessment_data: Dict[str, Any],
        priority: int = 1
    ) -> str:
        """Save assessment data to BigQuery"""
        # Prepare assessment data
        assessment_row = {
            "assessment_id": assessment_data.get("assessment_id", str(uuid.uuid4())),
            "company_vat": assessment_data["company_vat"],
            "user_id": assessment_data["user_id"],
            "turnover_risk": assessment_data["turnover_risk"],
            "shareholding_risk": assessment_data["shareholding_risk"],
            "bankruptcy_risk": assessment_data["bankruptcy_risk"],
            "legal_risk": assessment_data["legal_risk"],
            "corruption_risk": assessment_data["corruption_risk"],
            "overall_risk": assessment_data["overall_risk"],
            "financial_score": assessment_data.get("financial_score"),
            "legal_score": assessment_data.get("legal_score"),
            "press_score": assessment_data.get("press_score"),
            "composite_score": assessment_data.get("composite_score"),
            "search_date_range_start": assessment_data.get("search_date_range_start"),
            "search_date_range_end": assessment_data.get("search_date_range_end"),
            "sources_searched": json.dumps(assessment_data.get("sources_searched", [])),
            "total_results_found": assessment_data.get("total_results_found"),
            "high_risk_results": assessment_data.get("high_risk_results"),
            "medium_risk_results": assessment_data.get("medium_risk_results"),
            "low_risk_results": assessment_data.get("low_risk_results"),
            "analysis_summary": assessment_data.get("analysis_summary"),
            "key_findings": json.dumps(assessment_data.get("key_findings", [])),
            "recommendations": json.dumps(assessment_data.get("recommendations", [])),
            "classification_method": assessment_data.get("classification_method"),
            "processing_time_seconds": assessment_data.get("processing_time_seconds"),
        }
        
        return await self.queue_write("assessments", [assessment_row], priority=priority)
    
    async def save_events(
        self,
        events_data: List[Dict[str, Any]],
        priority: int = 2
    ) -> str:
        """Save events data to BigQuery"""
        # Prepare events data
        events_rows = []
        for event in events_data:
            event_row = {
                "event_id": event.get("event_id", str(uuid.uuid4())),
                "company_vat": event.get("company_vat"),
                "company_name": event.get("company_name"),
                "title": event["title"],
                "summary": event.get("summary"),
                "source": event["source"],
                "source_name": event.get("source_name"),
                "section": event.get("section"),
                "url": event.get("url"),
                "author": event.get("author"),
                "risk_level": event["risk_level"],
                "risk_category": event.get("risk_category"),
                "confidence": event.get("confidence"),
                "classification_method": event.get("classification_method"),
                "rationale": event.get("rationale"),
                "event_date": event.get("event_date"),
                "publication_date": event.get("publication_date"),
                "processing_time_ms": event.get("processing_time_ms"),
                "embedding_status": event.get("embedding_status"),
                "embedding_model": event.get("embedding_model"),
            }
            events_rows.append(event_row)
        
        return await self.queue_write("events", events_rows, priority=priority)
    
    async def save_raw_docs(
        self,
        raw_docs_data: List[Dict[str, Any]],
        priority: int = 3
    ) -> str:
        """Save raw documents to BigQuery"""
        # Prepare raw docs data
        docs_rows = []
        for doc in raw_docs_data:
            doc_row = {
                "doc_id": doc.get("doc_id", str(uuid.uuid4())),
                "source": doc["source"],
                "source_name": doc.get("source_name"),
                "raw_payload": json.dumps(doc["raw_payload"]),
                "document_type": doc.get("document_type"),
                "identificador": doc.get("identificador"),
                "title": doc.get("title"),
                "url": doc.get("url"),
                "publication_date": doc.get("publication_date"),
                "section": doc.get("section"),
                "author": doc.get("author"),
                "processing_status": doc.get("processing_status", "pending"),
                "processing_attempts": doc.get("processing_attempts", 0),
                "error_message": doc.get("error_message"),
            }
            docs_rows.append(doc_row)
        
        return await self.queue_write("raw_docs", docs_rows, priority=priority)
    
    async def save_company(
        self,
        company_data: Dict[str, Any],
        priority: int = 1
    ) -> str:
        """Save or update company data to BigQuery"""
        company_row = {
            "vat": company_data["vat"],
            "company_name": company_data["company_name"],
            "sector": company_data.get("sector"),
            "industry": company_data.get("industry"),
            "client_tier": company_data.get("client_tier"),
            "country": company_data.get("country"),
            "region": company_data.get("region"),
            "employee_count": company_data.get("employee_count"),
            "revenue_range": company_data.get("revenue_range"),
            "last_assessment_date": company_data.get("last_assessment_date"),
            "total_assessments": company_data.get("total_assessments"),
            "overall_risk_level": company_data.get("overall_risk_level"),
            "risk_score": company_data.get("risk_score"),
        }
        
        return await self.queue_write("companies", [company_row], operation="upsert", priority=priority)
    
    async def save_financial_metrics(
        self,
        metrics_data: List[Dict[str, Any]],
        priority: int = 2
    ) -> str:
        """Save financial metrics to BigQuery"""
        metrics_rows = []
        for metric in metrics_data:
            metric_row = {
                "metric_id": metric.get("metric_id", str(uuid.uuid4())),
                "company_vat": metric["company_vat"],
                "source": metric["source"],
                "metric_date": metric["metric_date"],
                "revenue": metric.get("revenue"),
                "net_income": metric.get("net_income"),
                "total_assets": metric.get("total_assets"),
                "total_liabilities": metric.get("total_liabilities"),
                "cash_flow": metric.get("cash_flow"),
                "debt_ratio": metric.get("debt_ratio"),
                "profit_margin": metric.get("profit_margin"),
                "current_ratio": metric.get("current_ratio"),
                "quick_ratio": metric.get("quick_ratio"),
                "market_cap": metric.get("market_cap"),
                "stock_price": metric.get("stock_price"),
                "pe_ratio": metric.get("pe_ratio"),
                "dividend_yield": metric.get("dividend_yield"),
            }
            metrics_rows.append(metric_row)
        
        return await self.queue_write("financial_metrics", metrics_rows, priority=priority)
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get status of the write queue"""
        with self.queue_lock:
            queue_stats = {
                "total_pending": len(self.write_queue),
                "high_priority": len([req for req in self.write_queue if req.priority == 1]),
                "medium_priority": len([req for req in self.write_queue if req.priority == 2]),
                "low_priority": len([req for req in self.write_queue if req.priority == 3]),
                "tables": {}
            }
            
            # Count by table
            for request in self.write_queue:
                table = request.table_name
                if table not in queue_stats["tables"]:
                    queue_stats["tables"][table] = 0
                queue_stats["tables"][table] += len(request.data)
        
        return queue_stats
    
    async def flush_queue(self) -> Dict[str, Any]:
        """Force flush the write queue"""
        logger.info("🔄 Flushing BigQuery write queue...")
        
        with self.queue_lock:
            pending_requests = self.write_queue.copy()
            self.write_queue.clear()
        
        if pending_requests:
            await self._process_batch(pending_requests)
        
        return {"flushed_requests": len(pending_requests)}
    
    def shutdown(self):
        """Shutdown the background processor"""
        logger.info("🛑 Shutting down BigQuery client...")
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("✅ BigQuery client shutdown complete")


# Global BigQuery client instance
_bigquery_client: Optional[AsyncBigQueryClient] = None


def get_bigquery_client() -> AsyncBigQueryClient:
    """Get or create global BigQuery client instance"""
    global _bigquery_client
    
    if _bigquery_client is None:
        _bigquery_client = AsyncBigQueryClient(
            project_id=settings.BIGQUERY_PROJECT,
            dataset_id=settings.BIGQUERY_DATASET
        )
    
    return _bigquery_client


def shutdown_bigquery_client():
    """Shutdown the global BigQuery client"""
    global _bigquery_client
    
    if _bigquery_client:
        _bigquery_client.shutdown()
        _bigquery_client = None 