#!/usr/bin/env python3
"""
Management Summarizer - Executive-level risk analysis summaries
Combines cloud AI and template-based approaches for comprehensive business intelligence
"""

import logging
import httpx
from typing import Dict, Any, List
from datetime import datetime
from app.agents.search.streamlined_yahoo_finance_agent import StreamlinedYahooFinanceAgent
import hashlib
import json
from app.agents.analytics.cache_manager import AnalyticsCacheManager

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
                logger.info(f"Returning cached management summary for {company_name} [{language}]")
                return cached

        financial_health = await self._get_financial_health(company_name)
        try:
            logger.info(f"Attempting cloud summary for {company_name}")
            summary = await self._cloud_gemini_summary(
                company_name, classification_results, include_evidence, language
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
            summary = self._template_summary(
                company_name, classification_results, include_evidence, language
            )
            summary["method"] = "template_analysis"
            logger.info("Template summary generated.")

        # Ensure all fields are present in the summary dict
        summary["financial_health"] = financial_health
        summary["key_risks"] = self._extract_key_risks(classification_results)
        summary["compliance_status"] = self._default_compliance_status()
        return summary
    
    async def _cloud_gemini_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using Cloud Gemini service for all major output sections"""
        # Build structured risk breakdown
        risk_breakdown = self._build_risk_breakdown(classification_results, include_evidence)
        # Compose system-level prompt
        system_prompt = (
            "You are a risk analyst generating executive summaries for companies based on automated risk classification data. "
            "Given the risk breakdown (legal, financial, etc.), with level, reasoning, and evidence, generate:\n"
            "1. A concise executive summary.\n"
            "2. A list of key findings (bullet points).\n"
            "3. A list of recommendations tailored to the company's risk profile.\n\n"
            "IMPORTANT: You MUST respond with ONLY a valid JSON object. No additional text before or after the JSON.\n\n"
            "Required JSON structure:\n"
            "{\n"
            '  "executive_summary": "A concise summary of the risk assessment in the specified language",\n'
            '  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],\n'
            '  "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]\n'
            "}\n\n"
            f"Language: {language}\n"
            "Example for Spanish:\n"
            "{\n"
            '  "executive_summary": "Análisis de riesgo ejecutivo para la empresa",\n'
            '  "key_findings": ["Hallazgo 1", "Hallazgo 2"],\n'
            '  "recommendations": ["Recomendación 1", "Recomendación 2"]\n'
            "}\n\n"
            "Respond ONLY with the JSON object, no other text."
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
            gemini_response = response.json()
            
            # Extract the text from Gemini response
            generated_text = gemini_response.get("text", "")
            if not generated_text:
                raise Exception("Gemini returned empty response")
            
            # Try to extract JSON from the generated text
            try:
                # Look for JSON in the response text
                gemini_result = self._extract_json_from_text(generated_text)
                if not gemini_result:
                    logger.warning(f"Could not extract JSON from Gemini response for {company_name}")
                    logger.debug(f"Raw Gemini response: {generated_text[:500]}...")
                    raise Exception("Could not extract JSON from Gemini response")
                
                # Validate required fields
                required_fields = ["executive_summary", "key_findings", "recommendations"]
                missing_fields = [field for field in required_fields if field not in gemini_result]
                if missing_fields:
                    logger.warning(f"Gemini response for {company_name} missing fields: {missing_fields}")
                    logger.debug(f"Available fields: {list(gemini_result.keys())}")
                    raise Exception(f"Gemini response missing required fields: {missing_fields}")
                
                logger.info(f"Successfully parsed Gemini response for {company_name}")
                return {
                    "company_name": company_name,
                    "overall_risk": self._analyze_risk_levels(classification_results)["overall_risk"],
                    "executive_summary": gemini_result["executive_summary"],
                    "risk_breakdown": risk_breakdown,
                    "key_findings": gemini_result["key_findings"],
                    "recommendations": gemini_result["recommendations"],
                    "generated_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.warning(f"Failed to parse Gemini JSON response for {company_name}: {e}")
                logger.debug(f"Raw Gemini response: {generated_text[:500]}...")
                raise Exception(f"Gemini response parsing failed: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from text response"""
        import re
        
        # Try to find JSON object in the text
        # Look for content between { and }
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        logger.debug(f"Found {len(matches)} potential JSON matches in Gemini response")
        
        for i, match in enumerate(matches):
            try:
                # Clean up the JSON string
                cleaned_json = match.strip()
                # Remove any markdown formatting
                if cleaned_json.startswith('```json'):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith('```'):
                    cleaned_json = cleaned_json[:-3]
                cleaned_json = cleaned_json.strip()
                
                logger.debug(f"Attempting to parse JSON match {i+1}: {cleaned_json[:100]}...")
                result = json.loads(cleaned_json)
                
                # Validate that it has the expected structure
                if isinstance(result, dict) and any(key in result for key in ["executive_summary", "key_findings", "recommendations"]):
                    logger.debug(f"Successfully parsed valid JSON with keys: {list(result.keys())}")
                    return result
                else:
                    logger.debug(f"JSON parsed but missing expected keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                    
            except json.JSONDecodeError as e:
                logger.debug(f"JSON decode error for match {i+1}: {e}")
                continue
        
        # If no JSON found, try to parse the entire text as JSON
        try:
            logger.debug("Attempting to parse entire text as JSON")
            result = json.loads(text.strip())
            if isinstance(result, dict) and any(key in result for key in ["executive_summary", "key_findings", "recommendations"]):
                logger.debug(f"Successfully parsed entire text as JSON with keys: {list(result.keys())}")
                return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse entire text as JSON: {e}")
        
        logger.warning(f"No valid JSON found in response. Text preview: {text[:200]}...")
        return None
    
    def _template_summary(
        self, 
        company_name: str, 
        classification_results: List[Dict[str, Any]],
        include_evidence: bool,
        language: str
    ) -> Dict[str, Any]:
        """Generate summary using templates (fallback only)"""
        risk_analysis = self._analyze_risk_levels(classification_results)
        overall_risk = risk_analysis["overall_risk"]
        # Select template set based on language
        if language == "es":
            templates = self.spanish_templates
        elif language == "en":
            templates = self.english_templates
        else:
            raise ValueError(f"Unsupported language: {language}")
        if overall_risk == "red":
            template = templates["high_risk"]
        elif overall_risk == "orange":
            template = templates["medium_risk"]
        else:
            template = templates["low_risk"]
        risk_breakdown = self._build_risk_breakdown(classification_results, include_evidence)
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
    
    def _build_risk_breakdown(self, classification_results, include_evidence):
        # Build risk breakdown for all categories
        risk_breakdown = {}
        for category in ["legal", "financial", "regulatory", "operational"]:
            risk_breakdown[category] = self._analyze_category_risk(
                classification_results, category, include_evidence
            )
        return risk_breakdown
    
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