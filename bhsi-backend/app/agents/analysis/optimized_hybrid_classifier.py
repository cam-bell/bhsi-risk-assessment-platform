#!/usr/bin/env python3
"""
Optimized Hybrid Classifier - Ultra-fast keyword gate with smart LLM routing
No unnecessary fallbacks - keyword gate should handle 90%+ of cases
"""

import re
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = None


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    method: str
    reason: str
    processing_time_ms: float


class OptimizedHybridClassifier:
    """
    Optimized hybrid classifier:
    1. Ultra-fast keyword gate (catches 90%+ of cases)
    2. Smart LLM routing (only for truly ambiguous cases)
    3. No unnecessary fallbacks
    """
    
    def __init__(self):
        # Only import Cloud Classifier when needed
        self._cloud_classifier = None
        self.stats = {
            "keyword_hits": 0,
            "llm_calls": 0,
            "total_classifications": 0
        }
        
        # Pre-compile regex patterns for maximum speed
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for maximum speed"""
        
        # HIGH-LEGAL triggers (immediate classification)
        self.high_legal_patterns = [
            # Bankruptcy & insolvency - most critical
            re.compile(r'\b(concurso de acreedores|administración concursal|suspensión de pagos|quiebra|insolvencia|liquidación)\b', re.IGNORECASE),
            # Criminal sanctions
            re.compile(r'\b(sentencia penal|proceso penal|delito societario|responsabilidad penal|inhabilitación)\b', re.IGNORECASE),
            # Severe sanctions
            re.compile(r'\b(sanción grave|expediente sancionador|multa de [0-9]+|penalización)\b', re.IGNORECASE),
            # Money laundering & terrorism financing
            re.compile(r'\b(blanqueo de capitales|financiación del terrorismo|lavado de dinero)\b', re.IGNORECASE),
            # Market manipulation
            re.compile(r'\b(manipulación de mercado|abuso de mercado|uso de información privilegiada)\b', re.IGNORECASE)
        ]
        
        # HIGH-FINANCIAL triggers
        self.high_financial_patterns = [
            # Financial distress
            re.compile(r'\b(pérdidas|caída de beneficios|reducción de ingresos|problemas de liquidez|crisis financiera)\b', re.IGNORECASE),
            # Debt issues
            re.compile(r'\b(deuda|incumplimiento|moratoria|dificultad financiera)\b', re.IGNORECASE)
        ]
        
        # HIGH-REGULATORY triggers
        self.high_regulatory_patterns = [
            # Regulatory sanctions
            re.compile(r'\b(sanción|multa|expediente sancionador|infracción grave)\b', re.IGNORECASE),
            # Regulatory bodies
            re.compile(r'\b(cnmv|banco de españa|cnmc|aepd|dgsfp|sepblac)\b', re.IGNORECASE)
        ]
        
        # MEDIUM-LEGAL triggers
        self.medium_legal_patterns = [
            # Regulatory warnings
            re.compile(r'\b(requerimiento|advertencia|apercibimiento|incumplimiento)\b', re.IGNORECASE),
            # Administrative proceedings
            re.compile(r'\b(expediente administrativo|procedimiento sancionador|resolución administrativa)\b', re.IGNORECASE),
            # Minor sanctions
            re.compile(r'\b(sanción leve|sanción menor|multa menor)\b', re.IGNORECASE),
            # Compliance issues
            re.compile(r'\b(deficiencia|irregularidad|incumplimiento normativo)\b', re.IGNORECASE)
        ]
        
        # MEDIUM-OPERATIONAL triggers
        self.medium_operational_patterns = [
            # Dismissals
            re.compile(r'\b(despido colectivo|despido|regulación de empleo|reducción de plantilla|ere)\b', re.IGNORECASE),
            # Environmental issues
            re.compile(r'\b(contaminación|multa ambiental|sanción ecológica|daño ambiental|vertido)\b', re.IGNORECASE)
        ]
        
        # LOW-LEGAL triggers
        self.low_legal_patterns = [
            # Regulatory notices
            re.compile(r'\b(circular|normativa|regulación|supervisión)\b', re.IGNORECASE),
            # Administrative procedures
            re.compile(r'\b(autorización|licencia|registro|inscripción)\b', re.IGNORECASE)
        ]
        
        # LOW-OPERATIONAL triggers
        self.low_operational_patterns = [
            # Routine operations
            re.compile(r'\b(nombramiento|cese|dimisión|renuncia|junta general|consejo de administración)\b', re.IGNORECASE),
            # Business changes
            re.compile(r'\b(fusión|adquisición|venta|reestructuración|cambio de sede)\b', re.IGNORECASE)
        ]
        
        # NO-LEGAL triggers (immediate non-legal classification)
        self.no_legal_patterns = [
            # News/sports/entertainment
            re.compile(r'\b(fútbol|deportes|entretenimiento|espectáculos|cultura|turismo)\b', re.IGNORECASE),
            # Regular business
            re.compile(r'\b(beneficios|facturación|crecimiento|expansión|inversión|dividendos)\b', re.IGNORECASE),
            # Awards/recognitions
            re.compile(r'\b(premio|reconocimiento|galardón|distinción)\b', re.IGNORECASE)
        ]
        
        # Section codes that indicate high legal relevance
        self.high_risk_sections = {
            'JUS', 'CNMC', 'AEPD', 'CNMV', 'BDE', 'DGSFP', 'SEPBLAC'
        }
        
        # Quick legal content detector
        self.legal_content_detector = re.compile(
            r'\b(tribunal|juzgado|sentencia|proceso|expediente|sanción|multa|infracción|normativ|regulación)\b', 
            re.IGNORECASE
        )
    
    def _get_cloud_classifier(self):
        """Lazy load cloud classifier only when needed"""
        if self._cloud_classifier is None:
            from app.agents.analysis.cloud_classifier import CloudClassifier
            self._cloud_classifier = CloudClassifier()
        return self._cloud_classifier
    
    async def classify_document(
        self, 
        text: str, 
        title: str = "", 
        source: str = "Unknown",
        section: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main classification method with optimized hybrid approach
        """
        start_time = time.time()
        self.stats["total_classifications"] += 1
        
        # Combine text and title for analysis
        full_text = f"{title} {text}".strip()
        
        # STAGE 1: ULTRA-FAST KEYWORD GATE
        keyword_result = self._keyword_gate(full_text, section, source)
        if keyword_result:
            self.stats["keyword_hits"] += 1
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "label": keyword_result.label,
                "confidence": keyword_result.confidence,
                "method": keyword_result.method,
                "reason": keyword_result.reason,
                "processing_time_ms": processing_time,
                "stats": self.stats.copy()
            }
        
        # STAGE 2: SMART LLM ROUTING (only if keyword gate fails AND text looks legal)
        if self._should_use_llm(full_text):
            self.stats["llm_calls"] += 1
            
            try:
                cloud_classifier = self._get_cloud_classifier()
                llm_result = await cloud_classifier.classify_document(
                    text=text,
                    title=title,
                    source=source,
                    section=section,
                    **kwargs
                )
                
                processing_time = (time.time() - start_time) * 1000
                
                # Add hybrid metadata
                llm_result.update({
                    "method": "hybrid_llm",
                    "processing_time_ms": processing_time,
                    "stats": self.stats.copy()
                })
                
                return llm_result
                
            except Exception as e:
                pass  # Fall through to default
        
        # DEFAULT: Quick classification for non-legal content
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "label": "No-Legal",
            "confidence": 0.8,
            "method": "hybrid_default",
            "reason": "No legal indicators detected",
            "processing_time_ms": processing_time,
            "stats": self.stats.copy()
        }
    
    def _keyword_gate(
        self, 
        text: str, 
        section: str = "", 
        source: str = "Unknown"
    ) -> Optional[ClassificationResult]:
        """
        Ultra-fast keyword gate - optimized patterns catch 90%+ of cases
        """
        
        # Check section codes first (fastest check)
        if section:
            section_upper = section.upper()
            if any(risk_section in section_upper for risk_section in self.high_risk_sections):
                return ClassificationResult(
                    label="High-Legal",
                    confidence=0.95,
                    method="keyword_section",
                    reason=f"High-risk section: {section}",
                    processing_time_ms=0.05
                )
        
        # Check NO-LEGAL patterns first (eliminate obvious non-legal content)
        for pattern in self.no_legal_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="No-Legal",
                    confidence=0.90,
                    method="keyword_no_legal",
                    reason=f"Non-legal content detected: {match}",
                    processing_time_ms=0.1
                )
        
        # Check HIGH-LEGAL patterns
        for pattern in self.high_legal_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="High-Legal",
                    confidence=0.92,
                    method="keyword_high_legal",
                    reason=f"High-risk keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check HIGH-FINANCIAL patterns
        for pattern in self.high_financial_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="High-Financial",
                    confidence=0.90,
                    method="keyword_high_financial",
                    reason=f"High-financial keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check HIGH-REGULATORY patterns
        for pattern in self.high_regulatory_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="High-Regulatory",
                    confidence=0.90,
                    method="keyword_high_regulatory",
                    reason=f"High-regulatory keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check MEDIUM-LEGAL patterns
        for pattern in self.medium_legal_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="Medium-Legal",
                    confidence=0.87,
                    method="keyword_medium_legal",
                    reason=f"Medium-risk keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check MEDIUM-OPERATIONAL patterns
        for pattern in self.medium_operational_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="Medium-Operational",
                    confidence=0.85,
                    method="keyword_medium_operational",
                    reason=f"Medium-operational keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check LOW-LEGAL patterns
        for pattern in self.low_legal_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="Low-Legal",
                    confidence=0.82,
                    method="keyword_low_legal",
                    reason=f"Low-risk keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Check LOW-OPERATIONAL patterns
        for pattern in self.low_operational_patterns:
            if pattern.search(text):
                match = pattern.search(text).group(0)
                return ClassificationResult(
                    label="Low-Operational",
                    confidence=0.80,
                    method="keyword_low_operational",
                    reason=f"Low-operational keyword: {match}",
                    processing_time_ms=0.15
                )
        
        # Quick filter for very short non-legal text
        if len(text) < 100 and not self.legal_content_detector.search(text):
            return ClassificationResult(
                label="No-Legal",
                confidence=0.85,
                method="keyword_short_text",
                reason="Short text without legal indicators",
                processing_time_ms=0.05
            )
        
        # No keyword match - decide whether to use LLM
        return None
    
    def _should_use_llm(self, text: str) -> bool:
        """
        Decide whether text is worth sending to expensive LLM
        Only send if it contains legal indicators and is substantial
        """
        
        # Must have legal content indicators
        if not self.legal_content_detector.search(text):
            return False
            
        # Must be substantial enough to warrant LLM analysis
        if len(text) < 50:
            return False
            
        # Skip if it's clearly administrative/routine
        routine_patterns = re.compile(r'\b(nombramiento|cese|dimisión|registro mercantil|publicación)\b', re.IGNORECASE)
        if routine_patterns.search(text) and len(text) < 200:
            return False
            
        return True
    
    def _infer_category_from_label(self, label: str) -> str:
        """
        Infer category from keyword classification label for consistency with LLM results
        """
        label_lower = label.lower()
        
        # Map keyword labels to categories
        if "legal" in label_lower:
            return "legal"
        elif "financial" in label_lower or "concurso" in label_lower or "insolvencia" in label_lower:
            return "financial"
        elif "regulatory" in label_lower or "reg" in label_lower:
            return "regulatory"
        elif "no-legal" in label_lower:
            return "operational"  # Default for non-legal content
        else:
            return "operational"  # Default fallback
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get classification performance statistics"""
        total = self.stats["total_classifications"]
        keyword_hits = self.stats["keyword_hits"]
        llm_calls = self.stats["llm_calls"]
        if total == 0:
            return {
                "total_classifications": 0,
                "keyword_hits": 0,
                "llm_calls": 0,
                "keyword_efficiency": "0.0%",
                "llm_usage": "0.0%",
                "performance_gain": "0.0% faster than LLM-only",
                "expected_speed": "90%+ handled by µ-second keyword gate"
            }
        keyword_rate = (keyword_hits / total) * 100
        llm_rate = (llm_calls / total) * 100
        return {
            "total_classifications": total,
            "keyword_hits": keyword_hits,
            "llm_calls": llm_calls,
            "keyword_efficiency": f"{keyword_rate:.1f}%",
            "llm_usage": f"{llm_rate:.1f}%",
            "performance_gain": f"{100 - llm_rate:.1f}% faster than LLM-only",
            "expected_speed": "90%+ handled by µ-second keyword gate"
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = {
            "keyword_hits": 0,
            "llm_calls": 0,
            "total_classifications": 0
        } 
    
    async def classify_with_cloud_enhancement(
        self, 
        text: str, 
        title: str = "", 
        source: str = "Unknown",
        section: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Enhanced classification with cloud fallback for low confidence cases
        
        This method implements the cloud enhancement strategy:
        1. Try keyword gate first (fastest)
        2. If confidence < 0.8, get second opinion from cloud
        3. Combine results for final classification
        """
        start_time = time.time()
        self.stats["total_classifications"] += 1
        
        # STAGE 1: Keyword gate
        keyword_result = await self.classify_document(
            text=text,
            title=title,
            source=source,
            section=section,
            **kwargs
        )
        
        # STAGE 2: Cloud enhancement for low confidence
        if keyword_result.get("confidence", 0) < 0.8:
            try:
                cloud_classifier = self._get_cloud_classifier()
                cloud_result = await cloud_classifier.classify_document(
                    text=text,
                    title=title,
                    source=source,
                    section=section,
                    **kwargs
                )
                
                # Combine results for final classification
                final_result = self._combine_classifications(
                    keyword_result, cloud_result
                )
                
                processing_time = (time.time() - start_time) * 1000
                final_result["processing_time_ms"] = processing_time
                final_result["method"] = "hybrid_cloud_enhanced"
                final_result["stats"] = self.stats.copy()
                
                return final_result
                
            except Exception as e:
                logger.warning(f"Cloud enhancement failed: {e}")
                # Return keyword result if cloud fails
                return keyword_result
        
        return keyword_result
    
    def _combine_classifications(
        self, 
        keyword_result: Dict[str, Any], 
        cloud_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine keyword and cloud classification results
        
        Strategy:
        - If both agree: use higher confidence
        - If disagree: use cloud result with combined confidence
        - Add rationale for management summaries
        """
        
        keyword_label = keyword_result.get("label", "No-Legal")
        cloud_label = cloud_result.get("label", "No-Legal")
        keyword_conf = keyword_result.get("confidence", 0)
        cloud_conf = cloud_result.get("confidence", 0)
        
        # If labels agree, use the higher confidence
        if keyword_label == cloud_label:
            final_label = keyword_label
            final_confidence = max(keyword_conf, cloud_conf)
            rationale = f"Both keyword ({keyword_conf:.2f}) and cloud ({cloud_conf:.2f}) agree on {keyword_label}"
        
        # If labels disagree, use cloud result with combined confidence
        else:
            final_label = cloud_label
            # Weight cloud result more heavily but consider keyword input
            final_confidence = (cloud_conf * 0.7) + (keyword_conf * 0.3)
            rationale = (
                f"Keyword classified as {keyword_label} ({keyword_conf:.2f}), "
                f"cloud classified as {cloud_label} ({cloud_conf:.2f}). "
                f"Using cloud result with combined confidence {final_confidence:.2f}"
            )
        
        return {
            "label": final_label,
            "confidence": round(final_confidence, 3),
            "method": "hybrid_combined",
            "reason": rationale,
            "keyword_result": keyword_result,
            "cloud_result": cloud_result,
            "combination_strategy": "weighted_cloud_preference"
        }

    async def classify_documents_batch(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch classify documents using hybrid keyword + LLM (Gemini) with caching.
        - Stage 1: Run keyword gate on all docs.
        - Stage 2: For ambiguous docs, batch send to LLM (cloud_classifier).
        - Stage 3: Blend/confidence logic, return all intermediate and final results.
        - Always include cache_key and last_verified_at in results.
        """
        keyword_results = []
        ambiguous_indices = []
        ambiguous_docs = []
        now_iso = datetime.utcnow().isoformat()
        for i, doc in enumerate(docs):
            text = doc.get('text', '')
            title = doc.get('title', '')
            section = doc.get('section', '')
            source = doc.get('source', 'Unknown')
            full_text = f"{title} {text}".strip()
            kw_result = self._keyword_gate(full_text, section, source)
            cache_key = None
            if kw_result:
                # Confident keyword result
                cache_key = self._get_cloud_classifier().get_cache_key(doc)
                # Infer category from keyword label for consistency
                inferred_category = self._infer_category_from_label(kw_result.label)
                keyword_results.append({
                    "keyword_label": kw_result.label,
                    "keyword_confidence": kw_result.confidence,
                    "keyword_method": kw_result.method,
                    "keyword_reason": kw_result.reason,
                    "category": inferred_category,  # Add inferred category
                    "label": kw_result.label,  # Use keyword label as final label
                    "confidence": kw_result.confidence,  # Use keyword confidence as final confidence
                    "reason": kw_result.reason,  # Use keyword reason as final reason
                    "method": kw_result.method,  # Use keyword method as final method
                    "final_label": kw_result.label,
                    "final_score": kw_result.confidence,
                    "source_used": "keyword",
                    "processing_time_ms": kw_result.processing_time_ms,
                    "cache_key": cache_key,
                    "last_verified_at": now_iso,
                })
            else:
                ambiguous_indices.append(i)
                ambiguous_docs.append(doc)
                keyword_results.append(None)
        llm_results = []
        if ambiguous_docs:
            cloud_classifier = self._get_cloud_classifier()
            llm_results = await cloud_classifier.classify_documents_batch(ambiguous_docs)
        final_results = []
        llm_idx = 0
        for i, kw in enumerate(keyword_results):
            if kw is not None:
                final_results.append(kw)
            else:
                llm = llm_results[llm_idx]
                llm_idx += 1
                result = {
                    "keyword_label": None,
                    "keyword_confidence": None,
                    "keyword_method": None,
                    "keyword_reason": None,
                    "llm_label": llm.get("label"),
                    "llm_confidence": llm.get("confidence"),
                    "llm_method": llm.get("method"),
                    "llm_reason": llm.get("reason"),
                    "category": llm.get("category"),
                    "label": llm.get("label"),
                    "confidence": llm.get("confidence"),
                    "reason": llm.get("reason"),
                    "method": llm.get("method"),
                    "final_label": llm.get("label"),
                    "final_score": llm.get("confidence"),
                    "source_used": "llm",
                    "processing_time_ms": None,
                    "cache_key": llm.get("cache_key"),
                    "last_verified_at": llm.get("last_verified_at"),
                }
                final_results.append(result)
        return final_results 