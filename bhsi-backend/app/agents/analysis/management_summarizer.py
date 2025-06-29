#!/usr/bin/env python3
"""
Management Summarizer - Executive-level risk analysis summaries
Combines cloud AI and template-based approaches for comprehensive business intelligence
"""

import logging
import httpx
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ManagementSummarizer:
    """Generate executive management summaries for company risk assessments"""
    
    def __init__(self):
        """Initialize the management summarizer"""
        
        # Cloud service URLs
        self.gemini_service_url = (
            "https://gemini-service-185303190462.europe-west1.run.app"
        )
        
        # Risk level mappings
        self.risk_colors = {
            "High-Legal": "red", 
            "Medium-Legal": "orange",
            "Low-Legal": "green",
            "No-Legal": "green"
        }
        
        # Spanish templates for different risk scenarios
        self.spanish_templates = {
            "high_risk": {
                "summary": (
                    "Se han identificado riesgos significativos que requieren "
                    "atención inmediata de la dirección."
                ),
                "recommendations": [
                    "Revisar inmediatamente los procedimientos de cumplimiento",
                    "Consultar con el departamento legal",
                    "Implementar medidas de monitoreo adicionales"
                ]
            },
            "medium_risk": {
                "summary": (
                    "Se han detectado algunas irregularidades que requieren "
                    "seguimiento y supervisión."
                ),
                "recommendations": [
                    "Establecer monitoreo regular de la situación",
                    "Revisar políticas internas relacionadas",
                    "Mantener comunicación con asesores legales"
                ]
            },
            "low_risk": {
                "summary": (
                    "No se han identificado riesgos significativos en el "
                    "análisis actual."
                ),
                "recommendations": [
                    "Continuar con el monitoreo rutinario",
                    "Mantener actualizadas las políticas de cumplimiento"
                ]
            }
        }
    
    async def generate_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool = True,
        language: str = "es"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive management summary
        
        Args:
            company_name: Name of the company
            classification_results: List of classified documents/results
            include_evidence: Whether to include evidence details
            language: Language for the summary (es/en)
            
        Returns:
            Dict containing the management summary
        """
        
        try:
            # Try cloud-based summary first
            logger.info(f"Attempting cloud summary for {company_name}")
            summary = await self._cloud_gemini_summary(
                company_name, classification_results, include_evidence, language
            )
            summary["method"] = "cloud_gemini_analysis"
            return summary
            
        except Exception as e:
            logger.warning(
                f"Cloud summary failed for {company_name}: {e}, "
                "falling back to template"
            )
            
            # Fallback to template-based summary
            summary = self._template_summary(
                company_name, classification_results, include_evidence, language
            )
            summary["method"] = "template_analysis"
            return summary
    
    async def _cloud_gemini_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using Cloud Gemini service"""
        
        # Prepare data for Gemini analysis
        company_data = {
            "company_name": company_name,
            "classification_results": classification_results,
            "total_documents": len(classification_results),
            "risk_distribution": self._calculate_risk_distribution(
                classification_results
            )
        }
        
        # Call Gemini service for company analysis
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.gemini_service_url}/analyze_company",
                json={
                    "company_name": company_name,
                    "company_data": company_data,
                    "analysis_type": "management_summary"
                }
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Gemini service returned {response.status_code}: "
                    f"{response.text}"
                )
            
            gemini_result = response.json()
            
            # Transform Gemini result to our format
            return self._transform_gemini_result(
                gemini_result, classification_results, include_evidence
            )
    
    def _template_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using templates"""
        
        # Analyze risk distribution
        risk_analysis = self._analyze_risk_levels(classification_results)
        overall_risk = risk_analysis["overall_risk"]
        
        # Get template based on risk level
        if overall_risk == "red":
            template = self.spanish_templates["high_risk"]
        elif overall_risk == "orange":
            template = self.spanish_templates["medium_risk"] 
        else:
            template = self.spanish_templates["low_risk"]
        
        # Build risk breakdown
        risk_breakdown = {}
        for category in ["legal", "financial", "regulatory", "operational"]:
            risk_breakdown[category] = self._analyze_category_risk(
                classification_results, category, include_evidence
            )
        
        # Generate key findings
        key_findings = self._extract_key_findings(classification_results)
        
        return {
            "company_name": company_name,
            "overall_risk": overall_risk,
            "executive_summary": (
                f"Análisis de riesgo para {company_name}: {template['summary']}"
            ),
            "risk_breakdown": risk_breakdown,
            "key_findings": key_findings,
            "recommendations": template["recommendations"],
            "generated_at": datetime.utcnow().isoformat(),
            "method": "template_analysis"
        }
    
    def _calculate_risk_distribution(
        self, classification_results: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of risk levels"""
        
        distribution = {
            "High-Legal": 0, "Medium-Legal": 0, 
            "Low-Legal": 0, "No-Legal": 0
        }
        
        for result in classification_results:
            risk_level = result.get("risk_level", "No-Legal")
            if risk_level in distribution:
                distribution[risk_level] += 1
        
        return distribution
    
    def _analyze_risk_levels(
        self, classification_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze overall risk levels"""
        
        distribution = self._calculate_risk_distribution(classification_results)
        total_docs = len(classification_results)
        
        # Determine overall risk
        if distribution["High-Legal"] > 0:
            overall_risk = "red"
        elif distribution["Medium-Legal"] > 0:
            overall_risk = "orange"
        else:
            overall_risk = "green"
        
        return {
            "overall_risk": overall_risk,
            "distribution": distribution,
            "total_documents": total_docs,
            "risk_percentage": {
                level: (count / total_docs * 100) if total_docs > 0 else 0 
                for level, count in distribution.items()
            }
        }
    
    def _analyze_category_risk(
        self, 
        classification_results: List[Dict[str, Any]], 
        category: str,
        include_evidence: bool
    ) -> Dict[str, Any]:
        """Analyze risk for a specific category"""
        
        # Define category keywords
        category_keywords = {
            "legal": [
                "sanción", "sentencia", "procedimiento", "tribunal", "delito"
            ],
            "financial": [
                "concurso", "insolvencia", "pérdidas", "facturación"
            ],
            "regulatory": [
                "cnmv", "banco de españa", "cnmc", "aepd"
            ],
            "operational": [
                "cese", "nombramiento", "fusión", "adquisición"
            ]
        }
        
        keywords = category_keywords.get(category, [])
        relevant_docs = []
        high_risk_count = 0
        
        # Find relevant documents
        for result in classification_results:
            text = result.get("title", "") + " " + result.get("summary", "")
            if any(keyword in text.lower() for keyword in keywords):
                relevant_docs.append(result)
                if result.get("risk_level") == "High-Legal":
                    high_risk_count += 1
        
        # Determine category risk level
        if high_risk_count > 0:
            level = "red"
            reasoning = (
                f"Se encontraron {high_risk_count} documentos de alto "
                f"riesgo relacionados con {category}"
            )
        elif len(relevant_docs) > 0:
            level = "orange"
            reasoning = (
                f"Se identificaron {len(relevant_docs)} documentos "
                f"relevantes para {category}"
            )
        else:
            level = "green"
            reasoning = f"No se detectaron riesgos significativos en {category}"
        
        # Prepare evidence
        evidence = []
        if include_evidence and relevant_docs:
            evidence = [
                doc.get("title", "Documento sin título")[:100] 
                for doc in relevant_docs[:3]
            ]
        
        return {
            "level": level,
            "reasoning": reasoning,
            "evidence": evidence,
            "confidence": 0.85 if relevant_docs else 0.95
        }
    
    def _extract_key_findings(
        self, classification_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract key findings from classification results"""
        
        findings = []
        distribution = self._calculate_risk_distribution(classification_results)
        
        # High-risk findings
        if distribution["High-Legal"] > 0:
            findings.append(
                f"Se identificaron {distribution['High-Legal']} "
                "documentos de alto riesgo legal"
            )
        
        # Medium-risk findings
        if distribution["Medium-Legal"] > 0:
            findings.append(
                f"Se detectaron {distribution['Medium-Legal']} "
                "documentos de riesgo medio"
            )
        
        # Source analysis
        sources = {}
        for result in classification_results:
            source = result.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        for source, count in sources.items():
            if count > 5:  # Significant number of documents from one source
                findings.append(
                    f"Alta actividad regulatoria detectada en {source} "
                    f"({count} documentos)"
                )
        
        # Default finding if none found
        if not findings:
            findings.append(
                "No se detectaron hallazgos significativos en el "
                "período analizado"
            )
        
        return findings[:5]  # Limit to top 5 findings
    
    def _transform_gemini_result(
        self, 
        gemini_result: Dict[str, Any], 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool
    ) -> Dict[str, Any]:
        """Transform Gemini result to our standard format"""
        
        risk_assessment = gemini_result.get("risk_assessment", {})
        
        # Map Gemini risk levels to our format
        risk_breakdown = {}
        for category in ["legal", "financial", "regulatory", "operational"]:
            gemini_level = risk_assessment.get(category, "green")
            risk_breakdown[category] = {
                "level": gemini_level,
                "reasoning": f"Análisis automático de {category} mediante IA",
                "evidence": [],
                "confidence": 0.92
            }
        
        return {
            "company_name": gemini_result.get("company_name", ""),
            "overall_risk": risk_assessment.get("overall", "green"),
            "executive_summary": gemini_result.get("analysis_summary", ""),
            "risk_breakdown": risk_breakdown,
            "key_findings": self._extract_key_findings(classification_results),
            "recommendations": [
                "Revisar el análisis detallado con el equipo legal",
                "Implementar medidas de seguimiento continuo",
                "Evaluar el impacto en la estrategia de negocio"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of management summarizer components"""
        
        status = {
            "template_fallback_ready": True,
            "cloud_gemini_available": False
        }
        
        try:
            # Test cloud Gemini connectivity
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.gemini_service_url}/health"
                )
                status["cloud_gemini_available"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Cloud Gemini health check failed: {e}")
        
        return status 