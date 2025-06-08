#!/usr/bin/env python3
"""
BOE Processing Pipeline - Orchestrates the complete multi-agent workflow
Ingestion → Landing → Normalization → Embedding → Classification
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the backend directory to Python path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.agents.search.boe_agent import BOEIngestionAgent
from app.agents.analysis.processor import BOEDocumentProcessor
from app.agents.analysis.embedder import BOEEmbeddingAgent
from app.agents.analysis.classifier import BOERiskClassifier

logger = logging.getLogger(__name__)


class BOEProcessingPipeline:
    """Complete BOE processing pipeline following Goal Architecture"""
    
    def __init__(self, use_ollama: bool = True, chroma_path: str = "./boe_chroma"):
        """Initialize all agents in the pipeline"""
        
        logger.info("🚀 Initializing BOE Processing Pipeline...")
        
        # Initialize all agents
        self.ingestion_agent = BOEIngestionAgent()
        self.processor = BOEDocumentProcessor()
        self.embedder = BOEEmbeddingAgent(chroma_path=chroma_path)
        self.classifier = BOERiskClassifier(use_ollama=use_ollama)
        
        logger.info("✅ BOE Pipeline initialized successfully!")
    
    def run_daily_cycle(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete daily processing cycle
        
        Flow: BOE API → raw_docs → events → embeddings → risk classification
        """
        
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        logger.info(f"🚀 Starting daily BOE cycle for {date_str}")
        
        pipeline_stats = {
            "date": date_str,
            "start_time": datetime.utcnow().isoformat(),
            "stages": {},
            "total_processed": 0,
            "high_risk_found": 0,
            "errors": []
        }
        
        try:
            # Stage 1: Ingestion (BOE API → raw_docs)
            logger.info("📡 Stage 1: BOE Ingestion")
            ingestion_stats = self.ingestion_agent.ingest_boe_day(date_str)
            pipeline_stats["stages"]["ingestion"] = ingestion_stats
            
            if "error" in ingestion_stats:
                pipeline_stats["errors"].append(f"Ingestion failed: {ingestion_stats['error']}")
                return pipeline_stats
            
            logger.info(f"✅ Ingested {ingestion_stats['new_documents']} new documents")
            
            # Stage 2: Processing (raw_docs → events)
            logger.info("🔄 Stage 2: Document Processing")
            processing_stats = self.processor.process_unparsed_documents(batch_size=100)
            pipeline_stats["stages"]["processing"] = processing_stats
            
            if processing_stats["errors"] > 0:
                pipeline_stats["errors"].append(f"Processing errors: {processing_stats['errors']}")
            
            logger.info(f"✅ Processed {processing_stats['created_events']} events")
            
            # Stage 3: Embedding (events → ChromaDB vectors)
            logger.info("🧠 Stage 3: Vector Embedding")
            embedding_stats = self.embedder.process_unembedded_events(batch_size=100)
            pipeline_stats["stages"]["embedding"] = embedding_stats
            
            if embedding_stats["errors"] > 0:
                pipeline_stats["errors"].append(f"Embedding errors: {embedding_stats['errors']}")
            
            logger.info(f"✅ Embedded {embedding_stats['embedded']} events")
            
            # Stage 4: Classification (events → risk labels)
            logger.info("🎯 Stage 4: Risk Classification")
            classification_stats = self.classifier.classify_unclassified_events(batch_size=100)
            pipeline_stats["stages"]["classification"] = classification_stats
            
            if classification_stats["errors"] > 0:
                pipeline_stats["errors"].append(f"Classification errors: {classification_stats['errors']}")
            
            # Summary stats
            pipeline_stats["total_processed"] = classification_stats["processed"]
            pipeline_stats["high_risk_found"] = classification_stats["high_legal"] + classification_stats["medium_reg"]
            
            logger.info(f"✅ Classified {classification_stats['processed']} events")
            logger.info(f"🚨 Found {pipeline_stats['high_risk_found']} high-risk items")
            
            # Stage 5: Summary Report
            pipeline_stats["summary"] = self._generate_pipeline_summary(pipeline_stats)
            
            pipeline_stats["end_time"] = datetime.utcnow().isoformat()
            pipeline_stats["success"] = True
            
            logger.info("🎉 Daily cycle completed successfully!")
            return pipeline_stats
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            pipeline_stats["error"] = str(e)
            pipeline_stats["success"] = False
            pipeline_stats["end_time"] = datetime.utcnow().isoformat()
            return pipeline_stats
    
    def run_incremental_processing(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Run incremental processing for existing unprocessed data
        """
        
        logger.info("🔄 Starting incremental processing")
        
        stats = {
            "start_time": datetime.utcnow().isoformat(),
            "stages": {},
            "errors": []
        }
        
        try:
            # Process any unparsed raw docs
            processing_stats = self.processor.process_unparsed_documents(batch_size)
            stats["stages"]["processing"] = processing_stats
            
            # Embed any unembedded events
            embedding_stats = self.embedder.process_unembedded_events(batch_size)
            stats["stages"]["embedding"] = embedding_stats
            
            # Classify any unclassified events
            classification_stats = self.classifier.classify_unclassified_events(batch_size)
            stats["stages"]["classification"] = classification_stats
            
            stats["end_time"] = datetime.utcnow().isoformat()
            stats["success"] = True
            
            logger.info("✅ Incremental processing complete")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Incremental processing failed: {e}")
            stats["error"] = str(e)
            stats["success"] = False
            stats["end_time"] = datetime.utcnow().isoformat()
            return stats
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        
        try:
            # Get stats from each agent
            ingestion_stats = self.ingestion_agent.get_ingestion_stats()
            processing_stats = self.processor.get_processing_stats()
            embedding_stats = self.embedder.get_embedding_stats()
            classification_stats = self.classifier.get_classification_stats()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "ingestion": ingestion_stats,
                "processing": processing_stats,
                "embedding": embedding_stats,
                "classification": classification_stats,
                "pipeline_health": self._assess_pipeline_health(
                    ingestion_stats, processing_stats, embedding_stats, classification_stats
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {"error": str(e)}
    
    def search_semantic(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Semantic search across all processed documents"""
        try:
            results = self.embedder.semantic_search(query, k=k)
            return {
                "query": query,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"error": str(e)}
    
    def get_risk_report(self, days_back: int = 7) -> Dict[str, Any]:
        """Generate risk report for recent documents"""
        try:
            classification_stats = self.classifier.get_classification_stats()
            
            # Get high-risk events from database
            from app.db.session import SessionLocal
            from app.crud.events import events
            
            db = SessionLocal()
            try:
                high_risk_events = events.get_high_risk(db, days_back=days_back)
                
                risk_report = {
                    "period": f"Last {days_back} days",
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": classification_stats,
                    "high_risk_events": [
                        {
                            "event_id": event.event_id,
                            "title": event.title,
                            "risk_label": event.risk_label,
                            "confidence": event.confidence,
                            "pub_date": event.pub_date.isoformat() if event.pub_date else None,
                            "section": event.section
                        }
                        for event in high_risk_events[:10]  # Top 10
                    ]
                }
                
                return risk_report
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Risk report generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_pipeline_summary(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable pipeline summary"""
        
        stages = stats.get("stages", {})
        
        return {
            "documents_ingested": stages.get("ingestion", {}).get("new_documents", 0),
            "events_created": stages.get("processing", {}).get("created_events", 0),
            "vectors_created": stages.get("embedding", {}).get("embedded", 0),
            "classifications_made": stages.get("classification", {}).get("processed", 0),
            "high_legal_risks": stages.get("classification", {}).get("high_legal", 0),
            "medium_reg_risks": stages.get("classification", {}).get("medium_reg", 0),
            "keyword_matches": stages.get("classification", {}).get("keyword_matches", 0),
            "llm_classifications": stages.get("classification", {}).get("llm_calls", 0),
            "total_errors": sum(
                stages.get(stage, {}).get("errors", 0) 
                for stage in ["ingestion", "processing", "embedding", "classification"]
            )
        }
    
    def _assess_pipeline_health(self, ingestion, processing, embedding, classification) -> Dict[str, Any]:
        """Assess overall pipeline health"""
        
        health = {
            "status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check for backlogs
        if processing.get("raw_docs", {}).get("unparsed", 0) > 100:
            health["issues"].append("Large backlog of unparsed documents")
            health["recommendations"].append("Run processor more frequently")
        
        if embedding.get("unembedded_events", 0) > 50:
            health["issues"].append("Large backlog of unembedded events")
            health["recommendations"].append("Run embedder more frequently")
        
        if classification.get("unclassified", 0) > 50:
            health["issues"].append("Large backlog of unclassified events")
            health["recommendations"].append("Run classifier more frequently")
        
        # Check for errors
        total_errors = (
            processing.get("raw_docs", {}).get("errors", 0) +
            processing.get("raw_docs", {}).get("dlq", 0)
        )
        
        if total_errors > 10:
            health["issues"].append(f"High error count: {total_errors}")
            health["recommendations"].append("Investigate processing errors")
        
        # Set overall status
        if len(health["issues"]) > 2:
            health["status"] = "degraded"
        elif len(health["issues"]) > 0:
            health["status"] = "warning"
        
        return health


# CLI interface
if __name__ == "__main__":
    import sys
    
    pipeline = BOEProcessingPipeline()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "daily":
            date_str = sys.argv[2] if len(sys.argv) > 2 else None
            stats = pipeline.run_daily_cycle(date_str)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "incremental":
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            stats = pipeline.run_incremental_processing(batch_size)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "status":
            status = pipeline.get_pipeline_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif command == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "concurso de acreedores"
            results = pipeline.search_semantic(query)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        elif command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            report = pipeline.get_risk_report(days)
            print(json.dumps(report, indent=2, ensure_ascii=False))
    
    else:
        print("BOE Processing Pipeline")
        print("Usage:")
        print("  python boe_pipeline.py daily [date]")
        print("  python boe_pipeline.py incremental [batch_size]")
        print("  python boe_pipeline.py status")
        print("  python boe_pipeline.py search [query]")
        print("  python boe_pipeline.py report [days_back]") 