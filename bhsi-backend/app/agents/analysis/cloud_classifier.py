#!/usr/bin/env python3
"""
Cloud Risk Classification Agent - D&O Risk Classification using Cloud Gemini Service
"""

import re
import json
import logging
import sys
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the app directory to the path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent  # Go up to bhsi-backend
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.crud.events import events
from app.models.events import RiskLabel
from app.core.keywords import KeywordManager

logger = logging.getLogger(__name__)


class CloudRiskClassifier:
    """D&O Risk Classification Agent using Cloud Gemini Service"""
    
    def __init__(self, gemini_service_url: Optional[str] = None):
        """Initialize the cloud risk classifier"""
        
        # Setup Gemini service URL
        self.gemini_service_url = gemini_service_url or "https://gemini-service-185303190462.europe-west1.run.app"
        self.gemini_available = False
        
        # Test Gemini service connection
        try:
            logger.info("🌟 Testing Gemini service connection...")
            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{self.gemini_service_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") == "healthy":
                        self.gemini_available = True
                        logger.info("✅ Gemini service is healthy and available")
                    else:
                        logger.warning(f"⚠️ Gemini service reports unhealthy: {health_data}")
                else:
                    logger.warning(f"⚠️ Gemini service returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Gemini service not available: {e}. Using keyword classification only.")
        
        # Initialize keyword manager as fallback
        self.keyword_manager = KeywordManager()
        
        # High-risk regulatory sections
        self.severe_sections = {
            "JUS": "Justicia - Criminal/civil proceedings",
            "CNMC": "Competencia - Market violations", 
            "AEPD": "Data Protection - Privacy violations",
            "CNMV": "Securities Regulator - Financial violations",
            "BDE": "Central Bank - Banking violations",
            "DGSFP": "Insurance Regulator - Insurance violations",
            "SEPBLAC": "Anti-Money Laundering - AML violations"
        }
    
    async def classify_event(self, event) -> Dict[str, Any]:
        """Main classification orchestrator with cloud fallback"""
        
        text = event.text or ""
        title = event.title or ""
        source = event.source or ""
        section = event.section or ""
        
        logger.info(f"🎯 Classifying event: {event.event_id}")
        
        # Layer 1: Section-based high-confidence classification
        section_result = self._section_classification(section, title, text)
        if section_result["confidence"] >= 0.9:
            logger.info(f"✅ High-confidence section classification: {section_result['label']}")
            return section_result
        
        # Layer 2: Cloud Gemini classification (if available)
        if self.gemini_available:
            try:
                gemini_result = await self._gemini_classification(text, title, source, section)
                if gemini_result and gemini_result["confidence"] >= 0.7:
                    logger.info(f"✅ Cloud Gemini classification: {gemini_result['label']}")
                    return gemini_result
            except Exception as e:
                logger.warning(f"⚠️ Gemini classification failed: {e}")
        
        # Layer 3: Keyword-based fallback
        keyword_result = self._keyword_classification(text, title)
        logger.info(f"🔤 Keyword fallback classification: {keyword_result['label']}")
        return keyword_result
    
    def _section_classification(self, section: str, title: str, text: str) -> Dict[str, Any]:
        """Layer 1: Section-based classification for high-confidence cases"""
        
        if not section:
            return {"label": "Unknown", "reason": "No section provided", "confidence": 0.0, "method": "section_none"}
        
        section_upper = section.upper()
        title_lower = title.lower()
        text_lower = text.lower()
        
        # High-risk sections with criminal/legal implications
        if section_upper in self.severe_sections:
            # Check for specific high-risk patterns
            criminal_patterns = [
                r"sentencia.*condenatoria", r"delito.*societario", r"inhabilitación.*director",
                r"concurso.*acreedores", r"administración.*judicial", r"responsabilidad.*penal"
            ]
            
            for pattern in criminal_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return {
                        "label": "High-Legal",
                        "reason": f"Criminal/legal proceedings in {self.severe_sections[section_upper]}",
                        "confidence": 0.95,
                        "method": "section_criminal"
                    }
            
            # General regulatory sanction
            regulatory_patterns = [r"sanción", r"multa", r"expediente.*sancionador", r"infracción.*grave"]
            
            for pattern in regulatory_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return {
                        "label": "Medium-Reg",
                        "reason": f"Regulatory sanction in {self.severe_sections[section_upper]}",
                        "confidence": 0.85,
                        "method": "section_regulatory"
                    }
        
        # Low-risk administrative sections
        admin_sections = ["PERSONAL", "NOMBRAMIENTOS", "ADMINISTRACIÓN"]
        if any(admin in section_upper for admin in admin_sections):
            return {
                "label": "Low-Other",
                "reason": "Administrative/routine section",
                "confidence": 0.8,
                "method": "section_admin"
            }
        
        return {"label": "Unknown", "reason": "Section not classified", "confidence": 0.0, "method": "section_unknown"}
    
    async def _gemini_classification(self, text: str, title: str, source: str, section: str) -> Optional[Dict[str, Any]]:
        """Layer 2: Cloud Gemini classification"""
        
        try:
            # Prepare request for Gemini service
            request_data = {
                "text": text,
                "title": title,
                "source": source,
                "section": section
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.gemini_service_url}/classify",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "label": result["label"],
                        "reason": result["reason"],
                        "confidence": result["confidence"],
                        "method": result["method"]
                    }
                else:
                    logger.warning(f"Gemini service returned status {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Gemini classification failed: {e}")
            return None
    
    def _keyword_classification(self, text: str, title: str) -> Dict[str, Any]:
        """Layer 3: Keyword-based classification (fallback)"""
        
        full_text = f"{title} {text}".lower()
        
        # High-risk keywords
        high_risk_keywords = [
            "concurso de acreedores", "administración judicial", "sentencia condenatoria",
            "delito societario", "responsabilidad penal", "inhabilitación", "prisión"
        ]
        
        for keyword in high_risk_keywords:
            if keyword in full_text:
                return {
                    "label": "High-Legal",
                    "reason": f"High-risk keyword detected: {keyword}",
                    "confidence": 0.7,
                    "method": "keyword_high"
                }
        
        # Medium-risk keywords
        medium_risk_keywords = [
            "sanción", "multa", "expediente sancionador", "infracción grave",
            "resolución sancionadora", "procedimiento disciplinario"
        ]
        
        for keyword in medium_risk_keywords:
            if keyword in full_text:
                return {
                    "label": "Medium-Reg",
                    "reason": f"Regulatory keyword detected: {keyword}",
                    "confidence": 0.6,
                    "method": "keyword_medium"
                }
        
        # Low-risk indicators
        low_risk_keywords = [
            "nombramiento", "designación", "cese", "dimisión", "renuncia",
            "constitución", "modificación estatutos", "junta general"
        ]
        
        for keyword in low_risk_keywords:
            if keyword in full_text:
                return {
                    "label": "Low-Other",
                    "reason": f"Administrative keyword detected: {keyword}",
                    "confidence": 0.5,
                    "method": "keyword_low"
                }
        
        # Default classification
        return {
            "label": "Unknown",
            "reason": "No matching keywords found",
            "confidence": 0.1,
            "method": "keyword_default"
        }
    
    async def classify_unclassified_events(self, batch_size: int = 50) -> Dict[str, Any]:
        """Classify all unclassified events in batches"""
        
        db = SessionLocal()
        stats = {
            "processed": 0,
            "classified": 0,
            "errors": 0,
            "gemini_used": 0,
            "keyword_fallback": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Get unclassified events
            unclassified = events.get_unclassified(db, limit=batch_size)
            
            logger.info(f"🎯 Processing {len(unclassified)} unclassified events")
            
            for event in unclassified:
                try:
                    stats["processed"] += 1
                    
                    # Classify event
                    result = await self.classify_event(event)
                    
                    # Track method used
                    if "gemini" in result.get("method", ""):
                        stats["gemini_used"] += 1
                    elif "keyword" in result.get("method", ""):
                        stats["keyword_fallback"] += 1
                    
                    # Update event in database
                    if result["label"] != "Unknown":
                        events.update_risk_classification(
                            db,
                            event.event_id,
                            RiskLabel(result["label"]),
                            result["confidence"],
                            result["reason"]
                        )
                        stats["classified"] += 1
                        
                        logger.debug(
                            f"✅ Classified {event.event_id}: {result['label']} "
                            f"(confidence: {result['confidence']:.2f}, method: {result['method']})"
                        )
                    
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Error classifying event {event.event_id}: {e}")
                    continue
            
            logger.info(
                f"✅ Classification complete: {stats['classified']}/{stats['processed']} events classified "
                f"({stats['gemini_used']} via Gemini, {stats['keyword_fallback']} via keywords)"
            )
            
        finally:
            db.close()
        
        return stats
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        db = SessionLocal()
        try:
            # Import Event model for direct queries
            from app.models.events import Event
            
            # Get classification breakdown
            total_events = db.query(Event).count()
            unclassified = len(events.get_unclassified(db, limit=1000))
            classified = total_events - unclassified
            
            # Get breakdown by risk level
            risk_breakdown = {}
            for risk_level in RiskLabel:
                count = db.query(Event).filter(Event.risk_label == risk_level).count()
                risk_breakdown[risk_level.value] = count
            
            return {
                "total_events": total_events,
                "classified_events": classified,
                "unclassified_events": unclassified,
                "gemini_service_available": self.gemini_available,
                "gemini_service_url": self.gemini_service_url,
                "risk_breakdown": risk_breakdown,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()


# CLI interface
if __name__ == "__main__":
    import asyncio
    import sys
    import json
    
    async def main():
        classifier = CloudRiskClassifier()
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "classify":
                batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
                stats = await classifier.classify_unclassified_events(batch_size)
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif command == "stats":
                stats = classifier.get_classification_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif command == "test":
                print("Testing Gemini service connection...")
                if classifier.gemini_available:
                    print("✅ Gemini service is available")
                else:
                    print("❌ Gemini service is not available")
        
        else:
            print("Cloud Risk Classification Agent")
            print("Usage:")
            print("  python cloud_classifier.py classify [batch_size]")
            print("  python cloud_classifier.py stats")
            print("  python cloud_classifier.py test")
    
    asyncio.run(main())


class CloudClassifier:
    """Simplified Cloud Classifier for search endpoints"""
    
    def __init__(self):
        """Initialize simplified cloud classifier"""
        self.classifier = CloudRiskClassifier()
    
    async def classify_document(self, 
                              text: str, 
                              title: str, 
                              source: str, 
                              section: str = "") -> Dict[str, Any]:
        """
        Classify a document using the cloud classifier
        
        Args:
            text: Document text content
            title: Document title
            source: Source of the document (BOE, News, etc.)
            section: Document section (for BOE documents)
            
        Returns:
            Dict with classification result
        """
        # Create a mock event object for the classifier
        class MockEvent:
            def __init__(self, text, title, source, section):
                self.text = text
                self.title = title
                self.source = source
                self.section = section
                self.event_id = "search_temp"
        
        mock_event = MockEvent(text, title, source, section)
        
        try:
            result = await self.classifier.classify_event(mock_event)
            return {
                "label": result.get("label", "Unknown"),
                "reason": result.get("reason", "Classification unavailable"),
                "confidence": result.get("confidence", 0.5),
                "method": result.get("method", "unknown")
            }
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                "label": "Unknown",
                "reason": f"Classification error: {str(e)}",
                "confidence": 0.3,
                "method": "error"
            } 