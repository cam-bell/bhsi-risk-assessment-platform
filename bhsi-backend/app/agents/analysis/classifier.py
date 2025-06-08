#!/usr/bin/env python3
"""
BOE Risk Classification Agent - D&O Risk Classification for Events
"""

import re
import json
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
from app.models.events import RiskLabel

# LLM imports with error handling
try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("Warning: LangChain not installed. LLM classification will be disabled.")
    print("To enable: pip install langchain langchain-community langchain-core")
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class BOERiskClassifier:
    """D&O Risk Classification Agent for BOE Events"""
    
    def __init__(self, use_ollama: bool = True):
        """Initialize the risk classifier"""
        
        # Setup LLM classifier with robust fallback
        self.use_ollama = use_ollama and OLLAMA_AVAILABLE
        self.llm_available = False
        
        if self.use_ollama:
            try:
                logger.info("🦙 Initializing Ollama Llama3 classifier...")
                self.llm = Ollama(model="llama3:latest", temperature=0, timeout=120)
                # Test LLM connection
                test_response = self.llm.invoke("Test: classify this as Low-Other")
                self.llm_available = True
                logger.info("✅ LLM classifier initialized and tested successfully")
            except Exception as e:
                logger.warning(f"⚠️ Ollama not available: {e}. Using keyword classification only.")
                self.use_ollama = False
                self.llm_available = False
        else:
            logger.info("🔤 LLM disabled. Using keyword classification only.")
        
        # D&O Risk keyword patterns (from BOE_Advanced.py)
        self.risk_patterns = {
            RiskLabel.HIGH_LEGAL: [
                # Bankruptcy & Insolvency (very specific)
                r"concurso\s+de\s+acreedores.*declarado",
                r"concurso\s+voluntario.*sociedad",
                r"concurso\s+necesario.*empresa",
                r"liquidación\s+judicial.*sociedad",
                r"administración\s+concursal.*nombramiento",
                r"quebrado|quiebra.*empresa",
                r"insolvencia.*declarada",
                r"suspensión\s+de\s+pagos.*aprobada",
                
                # Legal sentences and criminal sanctions
                r"sentencia\s+firme.*condenatoria",
                r"sentencia\s+del\s+tribunal\s+supremo.*anula",
                r"condena\s+firme.*directivos",
                r"sanción\s+penal.*definitiva",
                r"delito\s+societario.*condena",
                r"inhabilitación\s+de\s+directivos.*años",
                r"inhabilitación\s+para\s+ejercer.*cargos",
                r"prohibición\s+de\s+administrar.*sociedades",
                
                # Financial Crimes
                r"condena.*estafa.*millones",
                r"apropiación\s+indebida.*sentencia",
                r"alzamiento\s+de\s+bienes.*condena",
                r"blanqueo\s+de\s+capitales.*sanción"
            ],
            RiskLabel.MEDIUM_REG: [
                # Administrative sanctions
                r"multa\s+administrativa.*euros",
                r"sanción\s+administrativa.*grave",
                r"expediente\s+sancionador.*resolución",
                r"resolución\s+sancionadora.*cnmv",
                r"incumplimiento\s+normativa.*sanción",
                r"infracción\s+muy\s+grave.*multa",
                
                # Regulatory compliance
                r"inhabilitación\s+temporal.*meses",
                r"suspensión\s+de\s+actividades.*resolución",
                r"revocación\s+de\s+autorización.*definitiva",
                
                # Financial regulations
                r"cnmv.*sanción.*euros",
                r"banco\s+de\s+españa.*multa.*euros",
                r"dgsfp.*sanción.*administrativa",
                r"sepblac.*multa.*blanqueo"
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for risk_level, patterns in self.risk_patterns.items():
            self.compiled_patterns[risk_level] = [
                re.compile(pattern, re.IGNORECASE | re.UNICODE) for pattern in patterns
            ]
        
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
    
    def classify_unclassified_events(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Classify unclassified events for risk level
        """
        logger.info(f"🔄 Starting risk classification (batch size: {batch_size})")
        
        stats = {
            "processed": 0,
            "high_legal": 0,
            "medium_reg": 0,
            "low_other": 0,
            "unknown": 0,
            "keyword_matches": 0,
            "llm_calls": 0,
            "errors": 0
        }
        
        db = SessionLocal()
        try:
            # Get unclassified events
            unclassified = events.get_unclassified(db, limit=batch_size)
            logger.info(f"📋 Found {len(unclassified)} unclassified events")
            
            for event in unclassified:
                try:
                    stats["processed"] += 1
                    
                    # Perform risk classification
                    classification = self._classify_single_event(event)
                    
                    # Update database
                    success = events.update_classification(
                        db,
                        event.event_id,
                        classification["label"],
                        classification["reason"],
                        classification["confidence"]
                    )
                    
                    if success:
                        # Update stats
                        stats[classification["label"].lower().replace("-", "_")] += 1
                        
                        if "keyword" in classification["method"]:
                            stats["keyword_matches"] += 1
                        if "llm" in classification["method"]:
                            stats["llm_calls"] += 1
                        
                        # Log high-risk items
                        if classification["label"] in [RiskLabel.HIGH_LEGAL, RiskLabel.MEDIUM_REG]:
                            logger.info(f"🚨 RISK DETECTED: {event.event_id} - {classification['label']} (confidence: {classification['confidence']:.2f}) - {classification['reason'][:100]}...")
                        else:
                            logger.debug(f"✅ Classified: {event.event_id} - {classification['label']}")
                    else:
                        stats["errors"] += 1
                        logger.error(f"Failed to update classification for {event.event_id}")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"❌ Error classifying {event.event_id}: {e}")
            
            logger.info(f"✅ Classification complete: {stats}")
            return stats
            
        finally:
            db.close()
    
    def _classify_single_event(self, event) -> Dict[str, Any]:
        """Classify a single event using multi-layer approach"""
        
        # Layer 1: Keyword matching
        keyword_result = self._keyword_classification(event.title, event.section)
        if keyword_result:
            return keyword_result
        
        # Layer 2: LLM classification (if available)
        if self.llm_available and event.text:
            llm_result = self._llm_classification(event)
            if llm_result:
                return llm_result
        
        # Default: Low-Other
        return {
            "label": RiskLabel.LOW_OTHER.value,
            "reason": "No high-risk patterns detected",
            "confidence": 0.6,
            "method": "default"
        }
    
    def _keyword_classification(self, title: str, section: Optional[str]) -> Optional[Dict[str, Any]]:
        """Layer 1: High-precision keyword matching"""
        
        if not title:
            return None
        
        combined_text = f"{title} {section or ''}"
        
        # Check each risk level
        for risk_level, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(combined_text)
                if match:
                    return {
                        "label": risk_level.value,
                        "reason": f"Critical keyword pattern: '{pattern.pattern}' matched '{match.group()}'",
                        "confidence": 0.95,
                        "method": "keyword_high"
                    }
        
        # Check severe sections (medium confidence)
        if section and section in self.severe_sections:
            # Only if combined with some keywords
            if any(keyword in title.lower() for keyword in ["sanción", "multa", "expediente", "resolución"]):
                return {
                    "label": RiskLabel.MEDIUM_REG.value,
                    "reason": f"Severe section '{section}' with regulatory keywords",
                    "confidence": 0.8,
                    "method": "keyword_section"
                }
        
        return None
    
    def _llm_classification(self, event) -> Optional[Dict[str, Any]]:
        """Layer 2: LLM contextual classification"""
        
        if not self.llm_available:
            return None
        
        try:
            # Prepare prompt for Spanish D&O analysis
            prompt = f"""Analiza este documento del BOE español para riesgos D&O:

TÍTULO: {event.title}
SECCIÓN: {event.section or 'N/A'}
TEXTO: {event.text[:1500] if event.text else 'N/A'}

Clasifica el riesgo para directivos/administradores españoles:

- High-Legal: Concurso acreedores, sentencia penal firme, inhabilitación directivos, delitos societarios
- Medium-Reg: Sanción administrativa, multa regulatoria, expediente sancionador, infracciones graves  
- Low-Other: Nombramientos, procedimientos rutinarios, administración general
- Unknown: Información insuficiente

Responde SOLO en formato JSON:
{{"label": "High-Legal|Medium-Reg|Low-Other|Unknown", "reason": "explicación breve", "confidence": 0.0-1.0}}"""

            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Extract JSON
            result = self._extract_json_from_response(response)
            
            if result and self._validate_llm_result(result):
                result["method"] = "llm_analysis"
                return result
            else:
                logger.warning(f"Invalid LLM response for {event.event_id}: {response[:200]}...")
                return None
                
        except Exception as e:
            logger.error(f"LLM classification failed for {event.event_id}: {e}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response using multiple methods"""
        
        try:
            # Method 1: Direct JSON parsing
            if response.strip().startswith('{'):
                return json.loads(response.strip())
            
            # Method 2: Regex JSON extraction
            json_match = re.search(r'\{[^{}]*"label"[^{}]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            
            # Method 3: Code block extraction
            code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if code_match:
                return json.loads(code_match.group(1))
            
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _validate_llm_result(self, result: Dict[str, Any]) -> bool:
        """Validate LLM classification result"""
        
        required_fields = ["label", "reason", "confidence"]
        valid_labels = [label.value for label in RiskLabel]
        
        # Check required fields
        if not all(field in result for field in required_fields):
            return False
        
        # Check valid label
        if result["label"] not in valid_labels:
            return False
        
        # Check confidence range
        try:
            confidence = float(result["confidence"])
            if not 0.0 <= confidence <= 1.0:
                return False
        except (ValueError, TypeError):
            return False
        
        return True
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        db = SessionLocal()
        try:
            stats = events.get_risk_summary(db, days_back=30)
            return stats
        finally:
            db.close()
    
    def reclassify_all(self, force: bool = False) -> Dict[str, Any]:
        """Reclassify all events (dangerous - use with caution)"""
        if not force:
            logger.warning("Reclassify requires force=True parameter")
            return {"error": "Reclassify requires force=True parameter"}
        
        logger.warning("🚨 Reclassifying ALL events!")
        
        db = SessionLocal()
        try:
            # Reset all classifications
            from app.models.events import Event
            all_events = db.query(Event).all()
            
            for event in all_events:
                event.risk_label = None
                event.rationale = None
                event.confidence = None
                event.classifier_ts = None
            
            db.commit()
            
            # Reclassify all
            stats = self.classify_unclassified_events(batch_size=100)
            stats["reclassified"] = True
            
            return stats
            
        finally:
            db.close()


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    
    classifier = BOERiskClassifier()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "classify":
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            stats = classifier.classify_unclassified_events(batch_size)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "stats":
            stats = classifier.get_classification_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        elif command == "reclassify":
            if len(sys.argv) > 2 and sys.argv[2] == "--force":
                stats = classifier.reclassify_all(force=True)
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("Reclassify requires --force flag: python classifier.py reclassify --force")
    
    else:
        print("BOE Risk Classifier")
        print("Usage:")
        print("  python classifier.py classify [batch_size]")
        print("  python classifier.py stats")
        print("  python classifier.py reclassify --force") 