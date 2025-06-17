import os
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize variables
embedder_service_url = None
project_id = None
location = None
endpoint_id = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    global embedder_service_url, project_id, location, endpoint_id
    
    # Get configuration
    embedder_service_url = os.getenv("EMBEDDER_SERVICE_URL", "https://embedder-service-185303190462.europe-west1.run.app")
    project_id = os.getenv("PROJECT_ID", "solid-topic-443216-b2")
    location = os.getenv("LOCATION", "europe-west1")
    endpoint_id = os.getenv("ENDPOINT_ID", "1947305461535473664")
    
    logger.info(f"Vector Search service initialized")
    logger.info(f"Embedder URL: {embedder_service_url}")
    logger.info(f"Project: {project_id}, Location: {location}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

class Document(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]

class EmbedRequest(BaseModel):
    documents: List[Document]

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    filter: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]
    document: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int

# In-memory vector store (fallback - in production this would use Vertex AI Vector Search)
class MemoryVectorStore:
    def __init__(self):
        self.documents = {}  # id -> {embedding, metadata, text}
    
    async def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Add documents to vector store"""
        
        added_count = 0
        errors = []
        
        for doc in documents:
            try:
                # Get embedding from embedder service
                embedding = await self._get_embedding(doc.text)
                
                # Store document
                self.documents[doc.id] = {
                    "embedding": embedding,
                    "metadata": doc.metadata,
                    "text": doc.text,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                added_count += 1
                logger.info(f"Added document {doc.id}")
                
            except Exception as e:
                error_msg = f"Failed to add document {doc.id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "added_documents": added_count,
            "total_documents": len(self.documents),
            "errors": errors
        }
    
    async def search(self, query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for similar documents"""
        
        try:
            # Get query embedding
            query_embedding = await self._get_embedding(query)
            
            # Calculate similarities
            similarities = []
            for doc_id, doc_data in self.documents.items():
                # Apply filter if specified
                if filter_dict:
                    match = True
                    for key, value in filter_dict.items():
                        if doc_data["metadata"].get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_data["embedding"])
                similarities.append({
                    "id": doc_id,
                    "score": similarity,
                    "metadata": doc_data["metadata"],
                    "text": doc_data["text"]
                })
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["score"], reverse=True)
            
            results = []
            for sim in similarities[:k]:
                results.append(SearchResult(
                    id=sim["id"],
                    score=sim["score"],
                    metadata=sim["metadata"],
                    document=sim["text"][:500] + "..." if len(sim["text"]) > 500 else sim["text"]
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from embedder service"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{embedder_service_url}/embed",
                json={"text": text}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["embedding"]
            else:
                raise Exception(f"Embedder service returned {response.status_code}: {response.text}")
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "store_type": "memory",
            "embedder_service": embedder_service_url
        }

# Initialize vector store
vector_store = MemoryVectorStore()

@app.post("/embed")
async def embed_documents(request: EmbedRequest):
    """Add documents to vector store"""
    try:
        result = await vector_store.add_documents(request.documents)
        return {
            "status": "success",
            "message": f"Added {result['added_documents']} documents",
            **result
        }
    except Exception as e:
        logger.error(f"Embed documents failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents"""
    try:
        results = await vector_store.search(
            query=request.query,
            k=request.k,
            filter_dict=request.filter
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get vector store statistics"""
    try:
        stats = vector_store.get_stats()
        return {
            "status": "healthy",
            "vector_store": stats,
            "endpoints": {
                "embed": "/embed",
                "search": "/search",
                "stats": "/stats"
            }
        }
    except Exception as e:
        logger.error(f"Stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test embedder service connectivity
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{embedder_service_url}/health")
            embedder_healthy = response.status_code == 200
        
        return {
            "status": "healthy",
            "embedder_service": embedder_healthy,
            "vector_store": "ready",
            "documents_count": len(vector_store.documents)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Vector Search Service",
        "version": "1.0.0",
        "description": "Cloud-based vector search using Vertex AI embeddings",
        "endpoints": {
            "health": "/health",
            "embed": "/embed",
            "search": "/search", 
            "stats": "/stats"
        }
    } 