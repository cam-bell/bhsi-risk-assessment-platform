#!/usr/bin/env python3
"""
Cloud Embedding Agent - Uses cloud vector search service instead of ChromaDB
Maintains full API compatibility with original BOEEmbeddingAgent
"""

import logging
import httpx
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the app directory to the path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.crud.events import events

logger = logging.getLogger(__name__)


class CloudEmbeddingAgent:
    """
    Cloud-based embedding agent using vector search service
    
    Maintains 100% API compatibility with original BOEEmbeddingAgent
    """
    
    def __init__(self, 
                 vector_service_url: Optional[str] = None,
                 embedder_service_url: Optional[str] = None):
        """Initialize the cloud embedding agent"""
        
        # Service URLs
        self.vector_service_url = vector_service_url or "https://vector-search-185303190462.europe-west1.run.app"
        self.embedder_service_url = embedder_service_url or "https://embedder-service-185303190462.europe-west1.run.app"
        
        # Service health
        self.vector_service_available = False
        self.embedder_service_available = False
        
        # Model info for compatibility
        self.embedding_model = 'cloud-text-embedding-004'
        
        # Check service health
        self._check_services()
        
        # Initialize local fallback if cloud services unavailable
        self.local_agent = None
        if not (self.vector_service_available and self.embedder_service_available):
            try:
                from .embedder import BOEEmbeddingAgent
                self.local_agent = BOEEmbeddingAgent()
                logger.info("✅ Local embedding fallback initialized")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize local fallback: {e}")
    
    def _check_services(self):
        """Check health of cloud services"""
        
        # Check vector search service
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.vector_service_url}/health")
                if response.status_code == 200:
                    self.vector_service_available = True
                    logger.info("✅ Vector search service is healthy")
        except Exception as e:
            logger.warning(f"⚠️ Vector search service health check failed: {e}")
        
        # Check embedder service
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.embedder_service_url}/health")
                if response.status_code == 200:
                    self.embedder_service_available = True
                    logger.info("✅ Embedder service is healthy")
        except Exception as e:
            logger.warning(f"⚠️ Embedder service health check failed: {e}")
        
        logger.info(f"🌟 Cloud services status: Vector={self.vector_service_available}, Embedder={self.embedder_service_available}")
    
    def process_unembedded_events(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Process unembedded events using cloud services
        
        Maintains exact same API as original BOEEmbeddingAgent
        """
        
        # Try cloud processing first
        if self.vector_service_available and self.embedder_service_available:
            try:
                return self._cloud_process_events(batch_size)
            except Exception as e:
                logger.error(f"❌ Cloud processing failed: {e}")
                if self.local_agent:
                    logger.info("🔄 Falling back to local processing")
                    return self.local_agent.process_unembedded_events(batch_size)
                else:
                    raise
        
        # Fall back to local processing
        if self.local_agent:
            logger.info("🏠 Using local embedding processing")
            return self.local_agent.process_unembedded_events(batch_size)
        
        # No processing available
        raise RuntimeError("No embedding processing method available")
    
    def _cloud_process_events(self, batch_size: int) -> Dict[str, Any]:
        """Process events using cloud services"""
        
        db = SessionLocal()
        stats = {
            "processed": 0,
            "embedded": 0,
            "errors": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "method": "cloud_vector_search"
        }
        
        try:
            # Get unembedded events
            unembedded = events.get_unembedded(db, limit=batch_size)
            
            logger.info(f"🌟 Processing {len(unembedded)} events with cloud services")
            
            for event in unembedded:
                try:
                    stats["processed"] += 1
                    
                    # Embed single event
                    if self._cloud_embed_single_event(db, event):
                        stats["embedded"] += 1
                    
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Error processing event {event.event_id}: {e}")
                    continue
            
            logger.info(f"✅ Cloud processing complete: {stats['embedded']}/{stats['processed']} events embedded")
            
        finally:
            db.close()
        
        return stats
    
    def _cloud_embed_single_event(self, db, event) -> bool:
        """Embed single event using cloud services"""
        
        try:
            # Prepare text for embedding
            text_for_embedding = f"{event.title} {event.text[:1000]}"
            
            # Skip if text too short
            if len(text_for_embedding.strip()) < 20:
                logger.debug(f"Skipping event with insufficient text: {event.event_id}")
                return False
            
            # Prepare document for vector service
            document = {
                "id": event.event_id,
                "text": text_for_embedding,
                "metadata": {
                    "event_id": event.event_id,
                    "titulo": event.title[:500] if event.title else "",
                    "seccion": event.section[:50] if event.section else "",
                    "fecha": event.pub_date.strftime("%Y-%m-%d") if event.pub_date else "",
                    "url": event.url[:500] if event.url else "",
                    "source": event.source,
                    "risk_label": event.risk_label or "Unknown",
                    "confidence": float(event.confidence or 0.0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Send to vector service
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.vector_service_url}/embed",
                    json={"documents": [document]}
                )
                
                if response.status_code == 200:
                    # Mark as embedded in database
                    events.mark_embedded(db, event.event_id, self.embedding_model)
                    return True
                else:
                    logger.error(f"Vector service returned {response.status_code}: {response.text}")
                    return False
            
        except Exception as e:
            logger.error(f"Failed to embed event {event.event_id}: {e}")
            raise
    
    def semantic_search(self, query: str, k: int = 5, risk_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using cloud services
        
        Maintains exact same API as original BOEEmbeddingAgent
        """
        
        # Try cloud search first
        if self.vector_service_available:
            try:
                return self._cloud_semantic_search(query, k, risk_filter)
            except Exception as e:
                logger.error(f"❌ Cloud search failed: {e}")
                if self.local_agent:
                    logger.info("🔄 Falling back to local search")
                    return self.local_agent.semantic_search(query, k, risk_filter)
                else:
                    return []
        
        # Fall back to local search
        if self.local_agent:
            logger.info("🏠 Using local semantic search")
            return self.local_agent.semantic_search(query, k, risk_filter)
        
        # No search available
        return []
    
    def _cloud_semantic_search(self, query: str, k: int, risk_filter: Optional[str]) -> List[Dict[str, Any]]:
        """Perform semantic search using cloud service"""
        
        try:
            # Prepare search request
            search_request = {
                "query": query,
                "k": k
            }
            
            # Add filter if specified
            if risk_filter:
                search_request["filter"] = {"risk_label": risk_filter}
            
            # Send search request
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.vector_service_url}/search",
                    json=search_request
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Convert to expected format
                    formatted_results = []
                    for res in result["results"]:
                        formatted_results.append({
                            "id": res["id"],
                            "score": res["score"],
                            "metadata": res["metadata"],
                            "document": res["document"]
                        })
                    
                    return formatted_results
                else:
                    logger.error(f"Vector service search returned {response.status_code}: {response.text}")
                    return []
            
        except Exception as e:
            logger.error(f"Cloud search failed: {e}")
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get embedding statistics
        
        Maintains exact same API as original BOEEmbeddingAgent
        """
        
        db = SessionLocal()
        try:
            # Import Event model for direct queries
            from app.models.events import Event
            
            # Database stats (same as original)
            unembedded_count = len(events.get_unembedded(db, limit=1000))
            total_events = db.query(Event).count()
            
            # Cloud service stats
            vector_stats = {}
            try:
                if self.vector_service_available:
                    with httpx.Client(timeout=10.0) as client:
                        response = client.get(f"{self.vector_service_url}/stats")
                        if response.status_code == 200:
                            vector_stats = response.json()
            except Exception as e:
                logger.warning(f"Could not get vector service stats: {e}")
            
            return {
                "total_events": total_events,
                "embedded_events": total_events - unembedded_count,
                "unembedded_events": unembedded_count,
                "vector_service_documents": vector_stats.get("vector_store", {}).get("total_documents", 0),
                "embedding_model": self.embedding_model,
                "cloud_services": {
                    "vector_service_available": self.vector_service_available,
                    "embedder_service_available": self.embedder_service_available
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
    
    def rebuild_embeddings(self, force: bool = False) -> Dict[str, Any]:
        """
        Rebuild all embeddings (dangerous - use with caution)
        
        Maintains exact same API as original BOEEmbeddingAgent
        """
        
        if not force:
            logger.warning("Rebuild requires force=True parameter")
            return {"error": "Rebuild requires force=True parameter"}
        
        logger.warning("🚨 Rebuilding ALL embeddings using cloud services!")
        
        # Fall back to local agent for rebuild if cloud not available
        if not (self.vector_service_available and self.embedder_service_available):
            if self.local_agent:
                logger.info("🏠 Using local agent for rebuild")
                return self.local_agent.rebuild_embeddings(force=True)
            else:
                return {"error": "No rebuild method available"}
        
        db = SessionLocal()
        try:
            # Import Event model for direct queries
            from app.models.events import Event
            
            # Reset all embedding status
            all_events = db.query(Event).all()
            
            for event in all_events:
                event.embedding = None
                event.embedding_model = None
            
            db.commit()
            
            # Note: In production, you would also clear the vector service data
            # For now, we'll just reprocess all events
            
            # Reprocess all events
            stats = self.process_unembedded_events(batch_size=100)
            stats["rebuild"] = True
            
            return stats
            
        finally:
            db.close()


# CLI interface
if __name__ == "__main__":
    import asyncio
    import sys
    import json
    
    def main():
        agent = CloudEmbeddingAgent()
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "process":
                batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
                stats = agent.process_unembedded_events(batch_size)
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif command == "search":
                query = sys.argv[2] if len(sys.argv) > 2 else "concurso de acreedores"
                results = agent.semantic_search(query)
                for result in results:
                    print(f"Score: {result['score']:.3f} | {result['metadata']['titulo']}")
            
            elif command == "stats":
                stats = agent.get_embedding_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif command == "rebuild":
                if len(sys.argv) > 2 and sys.argv[2] == "--force":
                    stats = agent.rebuild_embeddings(force=True)
                    print(json.dumps(stats, indent=2, ensure_ascii=False))
                else:
                    print("Rebuild requires --force flag: python cloud_embedder.py rebuild --force")
        
        else:
            print("Cloud Embedding Agent")
            print("Usage:")
            print("  python cloud_embedder.py process [batch_size]")
            print("  python cloud_embedder.py search [query]")
            print("  python cloud_embedder.py stats")
            print("  python cloud_embedder.py rebuild --force")
    
    main() 