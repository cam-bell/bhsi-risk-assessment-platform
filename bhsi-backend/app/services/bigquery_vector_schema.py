#!/usr/bin/env python3
"""
BigQuery Vector Schema - Schema for storing vector embeddings in BigQuery
"""

from google.cloud import bigquery
from typing import List, Dict, Any
import json

# BigQuery Vector Table Schema
VECTOR_TABLE_SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("vector_embedding", "STRING", mode="REQUIRED"),  # Base64 encoded
    bigquery.SchemaField("vector_dimension", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("embedding_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("vector_created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("metadata", "STRING", mode="NULLABLE"),  # JSON string
    bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("company_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("publication_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("text_summary", "STRING", mode="NULLABLE"),
]

# BigQuery Search Cache Table Schema
SEARCH_CACHE_SCHEMA = [
    bigquery.SchemaField("cache_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("query", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("query_vector", "STRING", mode="REQUIRED"),  # Base64 encoded
    bigquery.SchemaField("results_count", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("search_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("top_results", "STRING", mode="NULLABLE"),  # JSON string
    bigquery.SchemaField("cache_hit_count", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("last_accessed", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
]

class BigQueryVectorSchema:
    """BigQuery schema management for vector storage"""
    
    def __init__(self, client: bigquery.Client, dataset_id: str = "bhsi_dataset"):
        self.client = client
        self.dataset_id = dataset_id
        self.vector_table_id = f"{dataset_id}.vectors"
        self.search_cache_table_id = f"{dataset_id}.search_cache"
    
    def create_vector_table(self) -> bool:
        """Create the vectors table in BigQuery"""
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "europe-west1"
                self.client.create_dataset(dataset)
            
            # Create vectors table
            table_ref = self.client.dataset(self.dataset_id).table("vectors")
            table = bigquery.Table(table_ref, schema=VECTOR_TABLE_SCHEMA)
            
            # Set clustering for better performance
            table.clustering_fields = ["company_name", "risk_level", "source"]
            
            # Create the table
            self.client.create_table(table, exists_ok=True)
            
            print(f"✅ Created vectors table: {self.vector_table_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create vectors table: {e}")
            return False
    
    def create_search_cache_table(self) -> bool:
        """Create the search cache table in BigQuery"""
        try:
            # Create search cache table
            table_ref = self.client.dataset(self.dataset_id).table("search_cache")
            table = bigquery.Table(table_ref, schema=SEARCH_CACHE_SCHEMA)
            
            # Set clustering for better performance
            table.clustering_fields = ["query", "search_timestamp"]
            
            # Create the table
            self.client.create_table(table, exists_ok=True)
            
            print(f"✅ Created search cache table: {self.search_cache_table_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create search cache table: {e}")
            return False
    
    def get_vector_search_query(self, query_vector: List[float], k: int = 5) -> str:
        """Generate BigQuery SQL for vector similarity search"""
        
        # Convert vector to string for SQL
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"
        
        query = f"""
        WITH vector_similarity AS (
            SELECT 
                event_id,
                vector_embedding,
                metadata,
                company_name,
                risk_level,
                publication_date,
                source,
                title,
                text_summary,
                -- Compute cosine similarity
                (
                    SELECT SUM(a * b) / (SQRT(SUM(a * a)) * SQRT(SUM(b * b)))
                    FROM UNNEST(JSON_EXTRACT_ARRAY(vector_embedding)) AS a WITH OFFSET pos
                    JOIN UNNEST({vector_str}) AS b WITH OFFSET pos
                    USING (pos)
                ) AS similarity_score
            FROM `{self.vector_table_id}`
            WHERE is_active = TRUE
        )
        SELECT 
            event_id,
            similarity_score,
            metadata,
            company_name,
            risk_level,
            publication_date,
            source,
            title,
            text_summary
        FROM vector_similarity
        WHERE similarity_score IS NOT NULL
        ORDER BY similarity_score DESC
        LIMIT {k}
        """
        
        return query
    
    def insert_vector_data(self, vector_data: Dict[str, Any]) -> bool:
        """Insert vector data into BigQuery"""
        try:
            # Prepare the row data
            row = {
                "event_id": vector_data["event_id"],
                "vector_embedding": vector_data["vector_embedding"],
                "vector_dimension": vector_data["vector_dimension"],
                "embedding_model": vector_data["embedding_model"],
                "vector_created_at": vector_data["vector_created_at"],
                "metadata": vector_data.get("metadata", "{}"),
                "is_active": vector_data.get("is_active", True),
                "company_name": vector_data.get("company_name"),
                "risk_level": vector_data.get("risk_level"),
                "publication_date": vector_data.get("publication_date"),
                "source": vector_data.get("source"),
                "title": vector_data.get("title"),
                "text_summary": vector_data.get("text_summary"),
            }
            
            # Insert into BigQuery
            errors = self.client.insert_rows_json(self.vector_table_id, [row])
            
            if errors:
                print(f"❌ Failed to insert vector data: {errors}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to insert vector data: {e}")
            return False
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector tables"""
        try:
            # Get vectors table stats
            vectors_query = f"SELECT COUNT(*) as vector_count FROM `{self.vector_table_id}` WHERE is_active = TRUE"
            vectors_job = self.client.query(vectors_query)
            vectors_result = vectors_job.result()
            vector_count = next(vectors_result).vector_count
            
            # Get search cache stats
            cache_query = f"SELECT COUNT(*) as cache_count FROM `{self.search_cache_table_id}` WHERE is_active = TRUE"
            cache_job = self.client.query(cache_query)
            cache_result = cache_job.result()
            cache_count = next(cache_result).cache_count
            
            return {
                "vector_count": vector_count,
                "cache_count": cache_count,
                "vector_table": self.vector_table_id,
                "cache_table": self.search_cache_table_id,
                "dataset": self.dataset_id
            }
            
        except Exception as e:
            print(f"❌ Failed to get table stats: {e}")
            return {"error": str(e)} 