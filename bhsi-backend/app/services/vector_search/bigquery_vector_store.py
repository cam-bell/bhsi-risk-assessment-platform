"""
BigQuery Vector Store
🎯 Replaces in-memory storage with persistent BigQuery vectors
📊 Uses exact BigQuery schema: bhsi_dataset.vectors, bhsi_dataset.search_cache
🔄 Enables persistent, scalable vector storage for RAG
"""

import json
import base64
import numpy as np
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from google.cloud import bigquery

class BigQueryVectorStore:
    """
    Vector store backed by BigQuery for enterprise persistence
    """
    
    def __init__(self):
        """Initialize BigQuery vector store"""
        self.client = bigquery.Client()
        self.dataset_id = "bhsi_dataset"
        self.vectors_table = f"solid-topic-443216-b2.{self.dataset_id}.vectors"
        self.cache_table = f"solid-topic-443216-b2.{self.dataset_id}.search_cache"
        print(f"🔗 BigQuery Vector Store initialized")
        print(f"   Vectors table: {self.vectors_table}")
        print(f"   Cache table: {self.cache_table}")
    
    def encode_vector(self, vector: List[float]) -> str:
        """Encode vector as base64 string for BigQuery storage"""
        try:
            vector_array = np.array(vector, dtype=np.float32)
            vector_bytes = vector_array.tobytes()
            return base64.b64encode(vector_bytes).decode('utf-8')
        except Exception as e:
            print(f"❌ Vector encoding failed: {e}")
            return ""
    
    def decode_vector(self, encoded_vector: str) -> List[float]:
        """Decode base64 encoded vector from BigQuery"""
        try:
            vector_bytes = base64.b64decode(encoded_vector.encode('utf-8'))
            vector_array = np.frombuffer(vector_bytes, dtype=np.float32)
            return vector_array.tolist()
        except Exception as e:
            print(f"❌ Vector decoding failed: {e}")
            return []
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    async def add_vector(
        self, 
        vector: List[float], 
        metadata: Dict[str, Any],
        vector_id: Optional[str] = None
    ) -> str:
        """
        Add vector to BigQuery storage
        
        Args:
            vector: The embedding vector
            metadata: Document metadata
            vector_id: Optional custom ID
            
        Returns:
            The event_id of the stored vector
        """
        try:
            event_id = vector_id or str(uuid.uuid4())
            
            # Prepare data matching exact BigQuery vectors schema
            vector_data = {
                "event_id": event_id,
                "vector_embedding": self.encode_vector(vector),
                "vector_dimension": len(vector),
                "embedding_model": metadata.get("embedding_model", "paraphrase-multilingual-MiniLM-L12-v2"),
                "vector_created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": json.dumps(metadata),
                "is_active": True,
                "company_name": metadata.get("company_name"),
                "risk_level": metadata.get("risk_level"),
                "publication_date": metadata.get("publication_date"),
                "source": metadata.get("source"),
                "title": metadata.get("title", "")[:500] if metadata.get("title") else None,
                "text_summary": metadata.get("text_summary", "")[:1000] if metadata.get("text_summary") else None
            }
            
            # Insert into BigQuery
            errors = self.client.insert_rows_json(self.vectors_table, [vector_data])
            
            if errors:
                print(f"❌ BigQuery insert error: {errors}")
                return ""
            
            print(f"   ✅ Vector stored in BigQuery: {event_id}")
            return event_id
            
        except Exception as e:
            print(f"❌ Failed to add vector to BigQuery: {e}")
            return ""
    
    async def search(
        self, 
        query_vector: List[float], 
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in BigQuery
        
        Args:
            query_vector: The query embedding vector
            k: Number of results to return
            filters: Optional filters (company_name, risk_level, etc.)
            
        Returns:
            List of similar documents with scores
        """
        try:
            print(f"🔍 Searching BigQuery vectors (k={k})...")
            
            # Build where clause
            where_clauses = ["is_active = TRUE"]
            
            if filters:
                if filters.get("company_name"):
                    where_clauses.append(f"company_name = '{filters['company_name']}'")
                if filters.get("risk_level"):
                    where_clauses.append(f"risk_level = '{filters['risk_level']}'")
                if filters.get("source"):
                    where_clauses.append(f"source = '{filters['source']}'")
            
            where_clause = " AND ".join(where_clauses)
            
            # Query BigQuery for all vectors (we'll calculate similarity in memory)
            # For production, consider using BigQuery's built-in vector functions
            bigquery_query = f"""
            SELECT 
                event_id,
                vector_embedding,
                company_name,
                title,
                text_summary,
                source,
                risk_level,
                publication_date,
                metadata,
                vector_created_at
            FROM `{self.vectors_table}`
            WHERE {where_clause}
            LIMIT 1000
            """
            
            query_job = self.client.query(bigquery_query)
            results = query_job.result()
            
            # Calculate similarities
            similarities = []
            for row in results:
                try:
                    stored_vector = self.decode_vector(row.vector_embedding)
                    if stored_vector:
                        similarity = self.cosine_similarity(query_vector, stored_vector)
                        
                        # Parse metadata
                        metadata = {}
                        try:
                            if row.metadata:
                                metadata = json.loads(row.metadata)
                        except:
                            pass
                        
                        similarities.append({
                            "id": row.event_id,
                            "score": similarity,
                            "metadata": {
                                "company": row.company_name,
                                "titulo": row.title,
                                "fecha": str(row.publication_date) if row.publication_date else "",
                                "source": row.source,
                                "risk_level": row.risk_level,
                                "created_at": str(row.vector_created_at),
                                **metadata
                            },
                            "document": row.text_summary or row.title or ""
                        })
                except Exception as e:
                    print(f"⚠️ Error processing vector: {e}")
                    continue
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["score"], reverse=True)
            top_results = similarities[:k]
            
            print(f"   📚 Found {len(similarities)} total vectors, returning top {len(top_results)}")
            
            # Cache the search for performance
            await self._cache_search(query_vector, top_results, filters)
            
            return top_results
            
        except Exception as e:
            print(f"❌ BigQuery vector search failed: {e}")
            return []
    
    async def _cache_search(
        self,
        query_vector: List[float],
        results: List[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]] = None
    ):
        """Cache search results in BigQuery search_cache table"""
        try:
            # Create cache key from filters
            filter_str = json.dumps(filters or {}, sort_keys=True)
            
            cache_data = {
                "cache_id": str(uuid.uuid4()),
                "query": filter_str,  # Store filters as query
                "query_vector": self.encode_vector(query_vector),
                "results_count": len(results),
                "search_timestamp": datetime.now(timezone.utc).isoformat(),
                "top_results": json.dumps(results[:5]),  # Store top 5 results
                "cache_hit_count": 1,
                "last_accessed": datetime.now(timezone.utc).isoformat(),
                "is_active": True
            }
            
            errors = self.client.insert_rows_json(self.cache_table, [cache_data])
            if not errors:
                print(f"   💾 Search cached in BigQuery")
                
        except Exception as e:
            print(f"⚠️ Search caching failed: {e}")
    
    async def get_vector_count(self) -> int:
        """Get total number of active vectors in BigQuery"""
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM `{self.vectors_table}`
            WHERE is_active = TRUE
            """
            
            job = self.client.query(query)
            result = list(job.result())[0]
            return result.count
            
        except Exception as e:
            print(f"❌ Failed to get vector count: {e}")
            return 0
    
    async def get_companies(self) -> List[str]:
        """Get list of companies with vectors in BigQuery"""
        try:
            query = f"""
            SELECT DISTINCT company_name
            FROM `{self.vectors_table}`
            WHERE is_active = TRUE 
            AND company_name IS NOT NULL
            ORDER BY company_name
            """
            
            job = self.client.query(query)
            companies = [row.company_name for row in job.result()]
            return companies
            
        except Exception as e:
            print(f"❌ Failed to get companies: {e}")
            return []
    
    async def delete_vectors(self, company_name: str) -> bool:
        """Soft delete vectors for a company"""
        try:
            query = f"""
            UPDATE `{self.vectors_table}`
            SET is_active = FALSE
            WHERE company_name = '{company_name}'
            """
            
            job = self.client.query(query)
            job.result()  # Wait for completion
            
            print(f"   🗑️ Soft deleted vectors for {company_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete vectors: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive BigQuery vector store statistics"""
        try:
            # Vector statistics
            vectors_query = f"""
            SELECT 
                COUNT(*) as total_vectors,
                COUNT(DISTINCT company_name) as unique_companies,
                COUNT(DISTINCT source) as unique_sources,
                COUNT(DISTINCT risk_level) as unique_risk_levels,
                AVG(vector_dimension) as avg_dimension,
                MIN(vector_created_at) as earliest_vector,
                MAX(vector_created_at) as latest_vector
            FROM `{self.vectors_table}`
            WHERE is_active = TRUE
            """
            
            # Cache statistics
            cache_query = f"""
            SELECT 
                COUNT(*) as total_cached_queries,
                SUM(cache_hit_count) as total_cache_hits,
                AVG(results_count) as avg_results_per_query,
                MIN(search_timestamp) as earliest_search,
                MAX(search_timestamp) as latest_search
            FROM `{self.cache_table}`
            WHERE is_active = TRUE
            """
            
            vectors_job = self.client.query(vectors_query)
            cache_job = self.client.query(cache_query)
            
            vectors_result = list(vectors_job.result())[0]
            cache_result = list(cache_job.result())[0]
            
            return {
                "vectors": {
                    "total": vectors_result.total_vectors,
                    "companies": vectors_result.unique_companies,
                    "sources": vectors_result.unique_sources,
                    "risk_levels": vectors_result.unique_risk_levels,
                    "avg_dimension": float(vectors_result.avg_dimension or 0),
                    "earliest": str(vectors_result.earliest_vector) if vectors_result.earliest_vector else None,
                    "latest": str(vectors_result.latest_vector) if vectors_result.latest_vector else None
                },
                "cache": {
                    "total_queries": cache_result.total_cached_queries,
                    "total_hits": cache_result.total_cache_hits,
                    "avg_results": float(cache_result.avg_results_per_query or 0),
                    "earliest": str(cache_result.earliest_search) if cache_result.earliest_search else None,
                    "latest": str(cache_result.latest_search) if cache_result.latest_search else None
                },
                "status": "BigQuery Vector Store Active"
            }
            
        except Exception as e:
            return {"error": str(e)}

# Compatibility wrapper for existing vector search service
class VectorSearchService:
    """
    Wrapper to maintain compatibility with existing vector search service
    while using BigQuery backend
    """
    
    def __init__(self):
        self.store = BigQueryVectorStore()
    
    async def search(
        self, 
        query_text: str,
        query_vector: List[float], 
        k: int = 5,
        company_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors (compatible with existing API)
        """
        filters = {}
        if company_filter:
            filters["company_name"] = company_filter
            
        return await self.store.search(query_vector, k, filters)
    
    async def add_document(
        self,
        text: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Add document to vector store (compatible with existing API)
        """
        return await self.store.add_vector(vector, metadata)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check returning BigQuery vector store stats
        """
        stats = await self.store.get_stats()
        return {
            "status": "healthy",
            "backend": "BigQuery",
            "vector_count": stats.get("vectors", {}).get("total", 0),
            "company_count": stats.get("vectors", {}).get("companies", 0),
            **stats
        } 