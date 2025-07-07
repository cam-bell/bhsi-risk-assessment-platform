#!/usr/bin/env python3
"""
Management Summarizer - Executive-level risk analysis summaries
Combines cloud AI and template-based approaches for comprehensive business intelligence
"""

import logging
import httpx
from typing import Dict, Any, List
from datetime import datetime
from app.services.yahoo_finance_service import StreamlinedYahooFinanceAgent
import hashlib
import json
from app.agents.analytics.cache_manager import AnalyticsCacheManager
import re

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
                    "Implementar medidas de monitoreo adicionales",
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
        
        # English templates for different risk scenarios
        self.english_templates = {
            "high_risk": {
                "summary": (
                    "Significant risks have been identified that require immediate "
                    "attention from management."
                ),
                "recommendations": [
                    "Immediately review compliance procedures",
                    "Consult with the legal department",
                    "Implement additional monitoring measures"
                ]
            },
            "medium_risk": {
                "summary": (
                    "Some irregularities have been detected that require "
                    "follow-up and supervision."
                ),
                "recommendations": [
                    "Establish regular monitoring of the situation",
                    "Review related internal policies",
                    "Maintain communication with legal advisors"
                ]
            },
            "low_risk": {
                "summary": (
                    "No significant risks have been identified in the "
                    "current analysis."
                ),
                "recommendations": [
                    "Continue routine monitoring",
                    "Keep compliance policies up to date"
                ]
            }
        }
        
        # Initialize cache manager (in-memory, 24h TTL)
        self.cache_manager = AnalyticsCacheManager(default_ttl_hours=24)
    
    async def generate_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool = True,
        language: str = "es",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive management summary using Gemini for all major output sections.
        Fallback to templates only if Gemini fails.
        """
        # --- Caching logic ---
        input_hash = hashlib.sha256(json.dumps({
            "company_name": company_name,
            "classification_results": classification_results,
            "include_evidence": include_evidence,
            "language": language
        }, sort_keys=True, default=str).encode()).hexdigest()
        cache_key_args = {
            "company_name": company_name,
            "language": language,
            "include_evidence": include_evidence,
            "input_hash": input_hash
        }
        if not force_refresh:
            cached = self.cache_manager.get("management_summary", **cache_key_args)
            if cached:
                logger.info(
                    f"Returning cached management summary for {company_name} "
                    f"[{language}]"
                )
                return cached

        # Log the classification results for debugging
        logger.info(
            f"Classification results for {company_name}: "
            f"{len(classification_results)} items"
        )
        if len(classification_results) == 0:
            logger.warning(
                f"No classification results for {company_name}. "
                f"Defaulting to template summary."
            )
        else:
            # Optionally, log a sample of the results
            logger.debug(
                f"Sample classification result: "
                f"{classification_results[0] if classification_results else 'N/A'}"
            )

        financial_health = await self._get_financial_health(company_name)
        fallback_reason = None
        try:
            logger.info(f"Attempting cloud summary for {company_name}")
            summary = await self._cloud_gemini_summary(
                company_name,
                classification_results,
                include_evidence,
                language
            )
            summary["method"] = "cloud_gemini_analysis"
            self.cache_manager.set(
                "management_summary", summary, **cache_key_args
            )
            logger.info("Gemini summary generated and cached.")
        except Exception as e:
            logger.warning(
                f"Cloud summary failed for {company_name}: {e}, "
                "falling back to template"
            )
            fallback_reason = (
                f"Gemini service failed: {str(e)}"
            )
            summary = self._template_summary(
                company_name,
                classification_results,
                include_evidence,
                language
            )
            summary["method"] = "template_analysis"
            logger.info("Template summary generated.")

        # Ensure all fields are present in the summary dict
        summary["financial_health"] = financial_health
        summary["key_risks"] = self._extract_key_risks(classification_results)
        summary["compliance_status"] = self._default_compliance_status()
        if fallback_reason:
            summary["fallback_reason"] = fallback_reason
        if len(classification_results) == 0:
            prev_reason = summary.get("fallback_reason", "")
            extra_reason = " | No classification results."
            summary["fallback_reason"] = prev_reason + extra_reason
        return summary
    
    async def _cloud_gemini_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using Cloud Gemini service for all major output sections"""
        # Build structured risk breakdown using modular fields
        risk_breakdown = self._build_risk_breakdown(classification_results, include_evidence)
        overall_risk = self._compute_overall_risk_from_breakdown(risk_breakdown)
        # Compose system-level prompt
        system_prompt = (
            f"Actúa como un analista de riesgos D&O para la empresa {company_name}. "
            f"Analiza los siguientes documentos clasificados y genera: "
            f"1. Un resumen ejecutivo claro y conciso sobre el riesgo global de la empresa. "
            f"2. Una lista de hallazgos clave (key_findings) sobre riesgos legales, "
            f"financieros, regulatorios u operativos. "
            f"3. Una lista de recomendaciones para la dirección o aseguradores. "
            f"Incluye evidencia si se solicita. "
            f"Responde SOLO en JSON estricto con los campos: executive_summary, "
            f"key_findings, recommendations. "
            f"Idioma: {language}. "
            f"\n\nDOCUMENTOS:\n" + "\n".join(
                f"- {doc.get('title', '')}: {doc.get('summary', '')}"
                for doc in classification_results[:10]
            )
        )
        payload = {
            "company_name": company_name,
            "language": language,
            "risk_breakdown": risk_breakdown
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.gemini_service_url}/generate",
                json={
                    "prompt": system_prompt + json.dumps(payload, ensure_ascii=False),
                    "max_tokens": 1200,
                    "temperature": 0.2
                }
            )
            if response.status_code != 200:
                raise Exception(
                    f"Gemini service returned {response.status_code}: "
                    f"{response.text}"
                )
            gemini_result = response.json()
            # If the response is wrapped in a 'text' field, extract and parse the JSON
            if 'text' in gemini_result:
                text_content = gemini_result['text']
                text_content = re.sub(r'^```json\n?|^```|```$', '', text_content.strip(), flags=re.MULTILINE)
                text_content = re.sub(r'^json\s*', '', text_content.strip(), flags=re.IGNORECASE)
                try:
                    gemini_result = json.loads(text_content)
                except Exception as parse_exc:
                    logger.error(
                        "Failed to parse Gemini 'text' field as JSON. Content was: %s",
                        text_content
                    )
                    # Try to fix common JSON issues before giving up
                    try:
                        # Fix specific issues seen in the logs
                        # Fix missing colons after field names
                        text_content = re.sub(r'(\w+)\s+"([^"]+)"\s*([^,}\]]+)', r'\1: "\2", \3', text_content)
                        # Fix missing colons in nested objects
                        text_content = re.sub(r'(\w+)\s*{', r'\1: {', text_content)
                        # Remove trailing commas
                        text_content = re.sub(r',\s*}', '}', text_content)
                        text_content = re.sub(r',\s*]', ']', text_content)
                        # Fix common Gemini formatting issues
                        text_content = re.sub(r'}\s*,\s*"([^"]+)"\s*{', r'}, "\1": {', text_content)
                        
                        gemini_result = json.loads(text_content)
                        logger.info("Successfully fixed and parsed malformed JSON from Gemini")
                    except Exception as fix_exc:
                        logger.error(
                            "Failed to fix malformed JSON from Gemini: %s",
                            fix_exc
                        )
                        # As a last resort, try to extract just the required fields manually
                        try:
                            logger.info("Attempting manual field extraction as fallback")
                            manual_result = {
                                "executive_summary": "Análisis de riesgo generado automáticamente debido a errores de formato.",
                                "key_findings": ["Se requiere revisión manual del análisis"],
                                "recommendations": ["Consultar con el equipo técnico para análisis detallado"]
                            }
                            gemini_result = manual_result
                            logger.info("Using manual fallback fields")
                        except Exception as manual_exc:
                            logger.error("All JSON parsing attempts failed")
                            raise Exception(f"Failed to parse Gemini 'text' field as JSON: {parse_exc}")
            required_fields = ["executive_summary", "key_findings", "recommendations"]
            if not all(k in gemini_result for k in required_fields):
                logger.error(
                    "Gemini response missing required fields. "
                    "Response was: %s",
                    gemini_result
                )
                raise Exception("Gemini response missing required fields")
            
            # Log the structure for debugging
            logger.debug(f"Gemini response structure: {list(gemini_result.keys())}")
            if "key_findings" in gemini_result:
                logger.debug(f"Key findings type: {type(gemini_result['key_findings'])}, length: {len(gemini_result['key_findings']) if isinstance(gemini_result['key_findings'], list) else 'not a list'}")
            if "recommendations" in gemini_result:
                logger.debug(f"Recommendations type: {type(gemini_result['recommendations'])}, length: {len(gemini_result['recommendations']) if isinstance(gemini_result['recommendations'], list) else 'not a list'}")
            # Extract and process key findings and recommendations with better error handling
            try:
                key_findings = self._ensure_list_of_strings(gemini_result["key_findings"], key="description")
                logger.debug(f"Processed {len(key_findings)} key findings")
            except Exception as e:
                logger.warning(f"Error processing key_findings: {e}")
                key_findings = ["Error processing key findings"]
            
            try:
                recommendations = self._ensure_list_of_strings(gemini_result["recommendations"], key="recommendation")
                logger.debug(f"Processed {len(recommendations)} recommendations")
            except Exception as e:
                logger.warning(f"Error processing recommendations: {e}")
                recommendations = ["Error processing recommendations"]
            return {
                "company_name": company_name,
                "overall_risk": overall_risk,
                "executive_summary": gemini_result["executive_summary"],
                "risk_breakdown": risk_breakdown,
                "key_findings": key_findings,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _template_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using templates (fallback only)"""
        # Use modular risk breakdown and overall risk for template as well
        risk_breakdown = self._build_risk_breakdown(classification_results, include_evidence)
        overall_risk = self._compute_overall_risk_from_breakdown(risk_breakdown)
        if language == "es":
            templates = self.spanish_templates
        elif language == "en":
            templates = self.english_templates
        else:
            raise ValueError(f"Unsupported language: {language}")
        if overall_risk == "red":
            template = templates["high_risk"]
        elif overall_risk in ("amber", "orange", "yellow"):
            template = templates["medium_risk"]
        else:
            template = templates["low_risk"]
        key_findings = self._extract_key_findings(classification_results)
        return {
            "company_name": company_name,
            "overall_risk": overall_risk,
            "executive_summary": (
                (f"Análisis de riesgo para {company_name}: {template['summary']}" if language == "es"
                 else f"Risk analysis for {company_name}: {template['summary']}")
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
                "concurso", "insolvencia", "pérdidas", "facturación", "deuda"
            ],
            "regulatory": [
                "cnmv", "banco de españa", "cnmc", "aepd", "dgsfp", "sepblac"
            ],
            "operational": [
                "cese", "nombramiento", "fusión", "adquisición", "despido"
            ],
            "dismissals": [
                "despido", "regulación de empleo", "reducción de plantilla", "ere"
            ],
            "environmental": [
                "contaminación", "multa ambiental", "sanción ecológica", "vertido"
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
    
    def _build_risk_breakdown(self, classification_results, include_evidence):
        # Build risk breakdown for all categories using modular Gemini fields
        # Collect all unique categories from results
        categories = set()
        for result in classification_results:
            if "category" in result:
                categories.add(result["category"])
        # Fallback to default categories if none found
        if not categories:
            categories = {"legal", "financial", "regulatory", "shareholding", "dismissals", "environmental", "operational"}
        risk_breakdown = {}
        for category in categories:
            # Gather all results for this category
            cat_results = [r for r in classification_results if r.get("category") == category]
            if not cat_results:
                # No results for this category, mark as green/low
                risk_breakdown[category] = {
                    "level": "green",
                    "reasoning": f"No risks detected in {category}",
                    "evidence": [],
                    "confidence": 1.0
                }
                continue
            # Compute most severe label (red > amber > green)
            label_priority = {"red": 3, "amber": 2, "orange": 2, "yellow": 2, "green": 1}
            most_severe = max(cat_results, key=lambda r: label_priority.get(r.get("label", "green"), 1))
            # Aggregate reasoning and evidence
            reasonings = [r.get("reason", "") for r in cat_results if r.get("reason")]
            evidence = [r.get("title", r.get("summary", "")) for r in cat_results if r.get("title") or r.get("summary")]
            avg_conf = sum(r.get("confidence", 1.0) for r in cat_results) / len(cat_results)
            risk_breakdown[category] = {
                "level": most_severe.get("label", "green"),
                "reasoning": "; ".join(reasonings)[:300],
                "evidence": evidence[:3] if include_evidence else [],
                "confidence": round(avg_conf, 3)
            }
        return risk_breakdown

    def _compute_overall_risk_from_breakdown(self, risk_breakdown):
        # Compute overall risk as max severity across all categories
        label_priority = {"red": 3, "amber": 2, "orange": 2, "yellow": 2, "green": 1}
        max_label = "green"
        for cat, breakdown in risk_breakdown.items():
            label = breakdown.get("level", "green")
            if label_priority.get(label, 1) > label_priority.get(max_label, 1):
                max_label = label
        return max_label
    
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

    async def _get_financial_health(self, company_name: str) -> dict:
        agent = StreamlinedYahooFinanceAgent()
        try:
            result = await agent.search(company_name)
            if result.get("financial_data"):
                data = result["financial_data"][0]
                status_map = {"High": "critical", "Medium": "concerning", "Low": "healthy"}
                status = status_map.get(data.get("risk_level", "Low"), "healthy")
                indicators = []
                if "price_change_7d" in data:
                    indicators.append({
                        "indicator": "7d Price Change",
                        "value": f"{data['price_change_7d']['percentage']:.2f}%",
                        "status": "negative" if data['price_change_7d']['percentage'] < -5 else "positive"
                    })
                if "revenue_change_yoy" in data:
                    indicators.append({
                        "indicator": "YoY Revenue Change",
                        "value": f"{data['revenue_change_yoy']['percentage']:.2f}%",
                        "status": "negative" if data['revenue_change_yoy']['percentage'] < 0 else "positive"
                    })
                for ri in data.get("risk_indicators", []):
                    indicators.append({
                        "indicator": ri["type"].replace("_", " ").title(),
                        "value": ri["description"],
                        "status": "negative" if ri["severity"] == "high" else "neutral"
                    })
                return {"status": status, "indicators": indicators}
            else:
                return {"status": "healthy", "indicators": []}
        except Exception as e:
            logger.warning(f"Yahoo Finance agent failed: {e}")
            return {"status": "healthy", "indicators": []}

    def _extract_key_risks(self, classification_results: List[Dict[str, Any]]) -> list:
        # Example: Extract high/medium risk results as key risks
        key_risks = []
        for result in classification_results:
            if result.get("risk_level") in ("High-Legal", "Medium-Legal"):
                key_risks.append({
                    "risk_type": result.get("risk_level", "Unknown"),
                    "description": result.get("summary", result.get("title", "-")),
                    "severity": "high" if result.get("risk_level") == "High-Legal" else "medium",
                    "recommendations": ["Review with legal team"]
                })
        return key_risks

    def _default_compliance_status(self) -> dict:
        # Placeholder: always return compliant with no areas
        return {
            "overall": "compliant",
            "areas": []
        }

    def _ensure_list_of_strings(self, lst, key=None):
        if not isinstance(lst, list):
            return []
        result = []
        for item in lst:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Try to extract a main field, or join all values
                if key and key in item:
                    result.append(str(item[key]))
                elif "description" in item:
                    # Common field name for descriptions
                    result.append(str(item["description"]))
                elif "action" in item:
                    # Common field name for recommendations
                    result.append(str(item["action"]))
                elif "type" in item and "description" in item:
                    # Combine type and description
                    result.append(f"{item['type']}: {item['description']}")
                else:
                    # Join all values for a readable string, but be more selective
                    important_fields = []
                    for k, v in item.items():
                        if isinstance(v, str) and len(v) > 0:
                            important_fields.append(f"{k}: {v}")
                    if important_fields:
                        result.append(' | '.join(important_fields))
                    else:
                        result.append(' - '.join(str(v) for v in item.values() if v))
        return result 