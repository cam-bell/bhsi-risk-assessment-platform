#!/usr/bin/env python3
"""
BOE Embedding Agent - Generates vectors for events and stores in ChromaDB
"""

import logging
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

# ML/AI imports with error handling
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not installed. Embedding features will be disabled.")
    print("To enable: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    print("Warning: chromadb not installed. Vector storage features will be disabled.")
    print("To enable: pip install chromadb")
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)


class BOEEmbeddingAgent:
    """Generates vector embeddings for BOE events and stores in ChromaDB"""
    
    def __init__(self, chroma_path: str = "./boe_chroma"):
        """Initialize the embedding agent"""
        
        # Check if ML dependencies are available
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ML dependencies not available. Running in minimal mode.")
            self.embedder = None
            self.client = None
            self.collection = None
            self.embedding_model = None
            return
        
        # Load multilingual embedder (supports Spanish)
        logger.info("🤖 Loading sentence transformer model...")
        try:
            self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ Sentence transformer loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load sentence transformer: {e}")
            self.embedder = None
            self.embedding_model = None
        
        # Setup ChromaDB with error handling
        logger.info(f"🗄️ Initializing ChromaDB at {chroma_path}")
        try:
            self.client = chromadb.PersistentClient(chroma_path)
            self.collection = self.client.get_or_create_collection(
                name="boe_events",
                metadata={"description": "BOE events with D&O risk classifications"}
            )
            logger.info("✅ ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
        
        self.embedding_model = 'paraphrase-multilingual-MiniLM-L12-v2'
    
    def process_unembedded_events(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Process unembedded events and create vector embeddings
        """
        if not self.embedder or not self.collection:
            logger.warning("⚠️ Embedding features disabled - ML dependencies not available")
            return {
                "processed": 0,
                "embedded": 0,
                "errors": 0,
                "skipped": 0,
                "status": "disabled"
            }
        
        logger.info(f"🔄 Starting embedding processing (batch_size: {batch_size})")
        
        stats = {
            "processed": 0,
            "embedded": 0,
            "errors": 0,
            "skipped": 0
        }
        
        db = SessionLocal()
        try:
            # Get unembedded events
            unembedded = events.get_unembedded(db, limit=batch_size)
            logger.info(f"📋 Found {len(unembedded)} unembedded events")
            
            for event in unembedded:
                try:
                    stats["processed"] += 1
                    
                    # Create embedding
                    success = self._embed_single_event(db, event)
                    
                    if success:
                        stats["embedded"] += 1
                        logger.debug(f"✅ Embedded: {event.event_id}")
                    else:
                        stats["skipped"] += 1
                        logger.debug(f"⏭️ Skipped: {event.event_id}")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Error embedding {event.event_id}: {e}")
            
            logger.info(f"✅ Embedding complete: {stats}")
            return stats
            
        finally:
            db.close()
    
    def _embed_single_event(self, db, event) -> bool:
        """Create embedding for a single event"""
        if not self.embedder or not self.collection:
            return False
            
        try:
            # Prepare text for embedding (title + first part of content)
            text_for_embedding = f"{event.title} {event.text[:1000]}"
            
            # Skip if text too short
            if len(text_for_embedding.strip()) < 20:
                logger.debug(f"Skipping event with insufficient text: {event.event_id}")
                return False
            
            # Generate embedding
            embedding_vector = self.embedder.encode(text_for_embedding).tolist()
            
            # Prepare metadata for ChromaDB
            metadata = {
                "event_id": event.event_id,
                "titulo": event.title[:500] if event.title else "",  # Limit length
                "seccion": event.section[:50] if event.section else "",
                "fecha": event.pub_date.strftime("%Y-%m-%d") if event.pub_date else "",
                "url": event.url[:500] if event.url else "",
                "source": event.source,
                "risk_label": event.risk_label or "Unknown",
                "confidence": float(event.confidence or 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in ChromaDB
            self.collection.upsert(
                ids=[event.event_id],
                embeddings=[embedding_vector],
                metadatas=[metadata],
                documents=[event.text[:3000] if event.text else ""]  # Limit document length
            )
            
            # Mark as embedded in database
            events.mark_embedded(db, event.event_id, self.embedding_model)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to embed event {event.event_id}: {e}")
            raise
    
    def semantic_search(self, query: str, k: int = 5, risk_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Semantic search across embedded events"""
        if not self.embedder or not self.collection:
            logger.warning("⚠️ Semantic search disabled - ML dependencies not available")
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Prepare filter
            where_filter = {}
            if risk_filter:
                where_filter["risk_label"] = risk_filter
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_filter if where_filter else None
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "metadata": results['metadatas'][0][i],
                        "document": results['documents'][0][i][:500] + "..." if len(results['documents'][0][i]) > 500 else results['documents'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding statistics"""
        db = SessionLocal()
        try:
            # Import Event model for direct queries
            from app.models.events import Event
            
            # Database stats
            unembedded_count = len(events.get_unembedded(db, limit=1000))
            total_events = db.query(Event).count()
            
            # ChromaDB stats
            chroma_count = self.collection.count() if self.collection else 0
            
            return {
                "total_events": total_events,
                "embedded_events": total_events - unembedded_count,
                "unembedded_events": unembedded_count,
                "chromadb_documents": chroma_count,
                "embedding_model": self.embedding_model or "disabled",
                "ml_available": SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
    
    def rebuild_embeddings(self, force: bool = False) -> Dict[str, Any]:
        """Rebuild all embeddings (dangerous - use with caution)"""
        if not force:
            logger.warning("Rebuild requires force=True parameter")
            return {"error": "Rebuild requires force=True parameter"}
        
        logger.warning("🚨 Rebuilding ALL embeddings - this will take time!")
        
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
            
            # Clear ChromaDB collection
            self.collection.delete()
            
            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name="boe_events",
                metadata={"description": "BOE events with D&O risk classifications"}
            )
            
            # Reprocess all events
            stats = self.process_unembedded_events(batch_size=100)
            stats["rebuild"] = True
            
            return stats
            
        finally:
            db.close()


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    
    agent = BOEEmbeddingAgent()
    
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
                print("Rebuild requires --force flag: python embedder.py rebuild --force")
    
    else:
        print("BOE Embedding Agent")
        print("Usage:")
        print("  python embedder.py process [batch_size]")
        print("  python embedder.py search [query]")
        print("  python embedder.py stats")
        print("  python embedder.py rebuild --force") 