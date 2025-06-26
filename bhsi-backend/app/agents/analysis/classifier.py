#!/usr/bin/env python3
"""
Risk Classification Agent - D&O Risk Classification for Events from multiple sources
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
from app.core.keywords import KeywordManager

# LLM imports with error handling
try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("Warning: LangChain not installed. LLM classification will be disabled.")
    print("To enable: pip install langchain langchain-community langchain-core")
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class RiskClassifier:
    """D&O Risk Classification Agent for Events from multiple sources"""
    
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
        
        # Initialize keyword manager
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
    
    async def classify_text(self, text: str, title: str = "", source: str = "", section: str = "") -> Dict[str, Any]:
        """
        Classify text content using multi-layer approach
        
        Args:
            text: Main text content to classify
            title: Title or headline (optional)
            source: Source of the content (e.g., "BOE", "NewsAPI")
            section: Section or category (optional)
            
        Returns:
            Dict with classification results
        """
        # Layer 1: Keyword matching
        keyword_result = self._keyword_classification(f"{title} {text}", section)
        if keyword_result:
            return keyword_result
        
        # Layer 2: LLM classification (if available)
        if self.llm_available:
            llm_result = await self._llm_classification(text, title, source, section)
            if llm_result:
                return llm_result
        
        # Default: Low-Other
        return {
            "label": RiskLabel.LOW_OTHER.value,
            "reason": "No high-risk patterns detected",
            "confidence": 0.6,
            "method": "default"
        }
    
    def _keyword_classification(self, text: str, section: str = "") -> Optional[Dict[str, Any]]:
        """Layer 1: Keyword-based classification"""
        
        # Check for severe regulatory sections
        if section in self.severe_sections:
            return {
                "label": RiskLabel.HIGH_LEGAL.value,
                "reason": f"Severe regulatory section: {self.severe_sections[section]}",
                "confidence": 0.9,
                "method": "keyword_section"
            }
        
        # Use keyword manager for classification
        risk_level, confidence = self.keyword_manager.get_risk_level(text)
        
        if risk_level != RiskLabel.LOW_OTHER.value:
            return {
                "label": risk_level,
                "reason": "High-risk keywords detected",
                "confidence": confidence,
                "method": "keyword_match"
            }
        
        return None
    
    async def _llm_classification(self, text: str, title: str, source: str, section: str) -> Optional[Dict[str, Any]]:
        """Layer 2: LLM contextual classification"""
        
        if not self.llm_available:
            return None
        
        try:
            # Prepare prompt for Spanish D&O analysis
            prompt = f"""Analiza este documento para riesgos D&O:

FUENTE: {source}
SECCIÓN: {section or 'N/A'}
TÍTULO: {title}
TEXTO: {text[:1500] if text else 'N/A'}

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
                logger.warning(f"Invalid LLM response: {response[:200]}...")
                return None
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
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


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    
    classifier = RiskClassifier()
    
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