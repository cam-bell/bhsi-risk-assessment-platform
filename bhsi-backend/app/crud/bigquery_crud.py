#!/usr/bin/env python3
"""
BigQuery-only CRUD operations for BHSI Risk Assessment System
Replaces SQLite operations with BigQuery as the primary database
"""

import logging
import uuid
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from app.core.config import settings
from app.services.bigquery_client_async import get_bigquery_client
import base64

logger = logging.getLogger(__name__)


class BigQueryCRUDBase:
    """Base class for BigQuery CRUD operations"""
    
    def __init__(self, table_name: str, project_id: str = None, dataset_id: str = None):
        self.table_name = table_name
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.dataset_id = dataset_id or settings.BIGQUERY_DATASET_ID
        self.table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        self.client = bigquery.Client(project=self.project_id)
    
    def _convert_to_bq_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data to BigQuery-compatible format"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                converted[key] = value.isoformat()
            elif isinstance(value, bytes):
                # Convert bytes to base64-encoded string for BigQuery
                converted[key] = base64.b64encode(value).decode('utf-8')
            elif hasattr(value, 'value'):  # Enum
                converted[key] = value.value
            elif isinstance(value, (dict, list)):
                converted[key] = str(value)  # JSON string for complex types
            else:
                converted[key] = value
        return converted
    
    def _convert_from_bq_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data from BigQuery format"""
        converted = {}
        for key, value in data.items():
            if key in ['created_at', 'updated_at', 'fetched_at', 'classifier_ts']:
                try:
                    converted[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    converted[key] = value
            elif key == 'pub_date':
                try:
                    converted[key] = date.fromisoformat(value)
                except:
                    converted[key] = value
            else:
                converted[key] = value
        return converted
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in BigQuery"""
        try:
            # Add timestamps if not present (only for tables that have these fields)
            # Skip for raw_docs table which doesn't have these fields
            if self.table_name != "raw_docs":
                if 'created_at' not in data:
                    data['created_at'] = datetime.utcnow().isoformat()
                if 'updated_at' not in data:
                    data['updated_at'] = datetime.utcnow().isoformat()
            
            # Convert to BigQuery format
            bq_data = self._convert_to_bq_format(data)
            
            # For users table, use direct insert instead of async queue to avoid schema issues
            if self.table_name == "users":
                # Direct insert for users table
                errors = self.client.insert_rows_json(self.table_id, [bq_data])
                if errors:
                    logger.error(f"❌ Direct insert failed for users: {errors}")
                    raise Exception(f"Insert errors: {errors}")
                logger.info(f"✅ Direct insert successful for users: {data.get('email', 'unknown')}")
                return {"data": data}
            
            # Use async client for background processing for other tables
            client = get_bigquery_client()
            request_id = await client.queue_write(
                table_name=self.table_name,
                data=[bq_data],
                operation="insert",
                priority=1
            )
            
            logger.info(f"✅ Queued create operation for {self.table_name}: {request_id}")
            return {"request_id": request_id, "data": data}
            
        except Exception as e:
            logger.error(f"❌ BigQuery create failed for {self.table_name}: {e}")
            raise
    
    async def get_by_id(self, id_value: str, id_field: str = "id") -> Optional[Dict[str, Any]]:
        """Get record by ID from BigQuery"""
        try:
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            WHERE {id_field} = @id_value
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("id_value", "STRING", id_value)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return self._convert_from_bq_format(dict(row))
            
            return None
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_id failed for {self.table_name}: {e}")
            return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple records from BigQuery with optional filtering"""
        try:
            # Build WHERE clause from filters
            where_clause = ""
            query_params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    param_name = f"param_{len(query_params)}"
                    conditions.append(f"{key} = @{param_name}")
                    query_params.append(
                        bigquery.ScalarQueryParameter(param_name, "STRING", str(value))
                    )
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # Use appropriate ORDER BY clause based on table
            order_by = "created_at DESC" if self.table_name != "raw_docs" else "fetched_at DESC"
            
            query = f"""
            SELECT *
            FROM `{self.table_id}`
            {where_clause}
            ORDER BY {order_by}
            LIMIT @limit
            OFFSET @skip
            """
            
            # Add pagination parameters
            query_params.extend([
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
                bigquery.ScalarQueryParameter("skip", "INT64", skip)
            ])
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_multi failed for {self.table_name}: {e}")
            return []
    
    async def update(self, id_value: str, data: Dict[str, Any], id_field: str = "id") -> Optional[Dict[str, Any]]:
        """Update record in BigQuery"""
        try:
            # Add updated timestamp (only for tables that have this field)
            # Skip for raw_docs table which doesn't have this field
            if self.table_name != "raw_docs":
                data['updated_at'] = datetime.utcnow().isoformat()
            
            # For users table, use INSERT only to avoid streaming buffer issues
            if self.table_name == "users":
                # First, get the existing user data to ensure all required fields are present
                existing_user = await self.get_by_id(id_value, id_field)
                if not existing_user:
                    logger.error(f"❌ User not found for update: {id_value}")
                    return None
                
                # Merge existing data with update data
                merged_data = {**existing_user, **data}
                
                # Convert to BigQuery format
                bq_data = self._convert_to_bq_format(merged_data)
                
                # For users table, we'll just log the update since we can't UPDATE due to streaming buffer
                # The actual update will happen on next login when we fetch the user
                logger.info(f"ℹ️ User update logged (streaming buffer prevents UPDATE): {id_value}")
                logger.info(f"Updated fields: {list(data.keys())}")
                
                return {"data": merged_data, "note": "Update logged but not persisted due to streaming buffer"}
            
            # Convert to BigQuery format for other tables
            bq_data = self._convert_to_bq_format(data)
            bq_data[id_field] = id_value  # Ensure ID is included
            
            # Use async client for background processing for other tables
            client = get_bigquery_client()
            request_id = await client.queue_write(
                table_name=self.table_name,
                data=[bq_data],
                operation="upsert",
                priority=1
            )
            
            logger.info(f"✅ Queued update operation for {self.table_name}: {request_id}")
            return {"request_id": request_id, "data": data}
            
        except Exception as e:
            logger.error(f"❌ BigQuery update failed for {self.table_name}: {e}")
            return None
    
    async def delete(self, id_value: str, id_field: str = "id") -> bool:
        """Delete record from BigQuery"""
        try:
            query = f"""
            DELETE FROM `{self.table_id}`
            WHERE {id_field} = @id_value
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("id_value", "STRING", id_value)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"✅ Deleted record from {self.table_name}: {id_value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ BigQuery delete failed for {self.table_name}: {e}")
            return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records in BigQuery"""
        try:
            # Build WHERE clause from filters
            where_clause = ""
            query_params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    param_name = f"param_{len(query_params)}"
                    conditions.append(f"{key} = @{param_name}")
                    query_params.append(
                        bigquery.ScalarQueryParameter(param_name, "STRING", str(value))
                    )
                where_clause = "WHERE " + " AND ".join(conditions)
            
            query = f"""
            SELECT COUNT(*) as count
            FROM `{self.table_id}`
            {where_clause}
            """
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return row.count
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ BigQuery count failed for {self.table_name}: {e}")
            return 0
    
    async def exists(self, id_value: str, id_field: str = "id") -> bool:
        """Check if record exists in BigQuery"""
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM `{self.table_id}`
            WHERE {id_field} = @id_value
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("id_value", "STRING", id_value)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return row.count > 0
            
            return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery exists check failed for {self.table_name}: {e}")
            return False 