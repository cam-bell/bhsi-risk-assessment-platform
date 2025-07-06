import random
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def generate_mock_analytics(company_name: str) -> Dict[str, Any]:
    """Generate realistic mock analytics data for fallback scenarios"""
    
    # Generate realistic risk distribution based on company name
    company_risk_profile = _get_company_risk_profile(company_name)
    
    # Generate realistic event counts
    total_events = random.randint(5, 25)
    high_risk_events = int(total_events * company_risk_profile["high_risk_ratio"])
    medium_risk_events = int(total_events * company_risk_profile["medium_risk_ratio"])
    low_risk_events = total_events - high_risk_events - medium_risk_events
    
    # Generate recent events
    latest_events = _generate_mock_events(company_name, total_events)
    
    return {
        "company_name": company_name,
        "vat": _generate_mock_vat(),
        "sector": _get_random_sector(),
        "total_events": total_events,
        "risk_distribution": {
            "HIGH": high_risk_events,
            "MEDIUM": medium_risk_events,
            "LOW": low_risk_events
        },
        "latest_events": latest_events,
        "assessment": _generate_mock_assessment(company_risk_profile),
        "fallback": True,
        "message": "Using enhanced fallback data - BigQuery service unavailable",
        "generated_at": datetime.utcnow().isoformat()
    }

def _get_company_risk_profile(company_name: str) -> Dict[str, Any]:
    """Generate realistic risk profile based on company name"""
    name_lower = company_name.lower()
    
    # High-risk indicators
    high_risk_keywords = ["banco", "bank", "financiera", "financial", "seguros", "insurance"]
    medium_risk_keywords = ["energia", "energy", "telecom", "construccion", "construction"]
    
    if any(keyword in name_lower for keyword in high_risk_keywords):
        return {
            "overall_risk": "red",
            "high_risk_ratio": 0.4,
            "medium_risk_ratio": 0.4,
            "low_risk_ratio": 0.2
        }
    elif any(keyword in name_lower for keyword in medium_risk_keywords):
        return {
            "overall_risk": "orange",
            "high_risk_ratio": 0.2,
            "medium_risk_ratio": 0.5,
            "low_risk_ratio": 0.3
        }
    else:
        return {
            "overall_risk": "green",
            "high_risk_ratio": 0.1,
            "medium_risk_ratio": 0.3,
            "low_risk_ratio": 0.6
        }

def _generate_mock_events(company_name: str, count: int) -> List[Dict[str, Any]]:
    """Generate realistic mock events"""
    events = []
    event_types = [
        "regulatory_investigation", "legal_proceeding", "financial_report", 
        "management_change", "market_announcement", "compliance_issue"
    ]
    
    sources = ["BOE", "NewsAPI", "El País", "Expansión", "El Mundo"]
    risk_levels = ["HIGH", "MEDIUM", "LOW"]
    
    for i in range(min(count, 10)):  # Limit to 10 most recent
        event_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        event = {
            "event_id": f"mock_event_{i}_{random.randint(1000, 9999)}",
            "title": _generate_mock_event_title(company_name, event_types[random.randint(0, len(event_types)-1)]),
            "text": f"Mock event description for {company_name}",
            "source": sources[random.randint(0, len(sources)-1)],
            "section": "Legal" if random.random() > 0.7 else "General",
            "pub_date": event_date.isoformat(),
            "url": f"https://example.com/mock-event-{i}",
            "risk_label": risk_levels[random.randint(0, len(risk_levels)-1)],
            "rationale": "Mock event generated for fallback data",
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "classifier_ts": event_date.isoformat()
        }
        events.append(event)
    
    # Sort by date descending
    events.sort(key=lambda x: x["pub_date"], reverse=True)
    return events

def _generate_mock_event_title(company_name: str, event_type: str) -> str:
    """Generate realistic event titles"""
    titles = {
        "regulatory_investigation": f"Investigación regulatoria sobre {company_name}",
        "legal_proceeding": f"Procedimiento legal iniciado contra {company_name}",
        "financial_report": f"Informe financiero trimestral de {company_name}",
        "management_change": f"Cambio en la dirección de {company_name}",
        "market_announcement": f"Anuncio de mercado de {company_name}",
        "compliance_issue": f"Problema de cumplimiento detectado en {company_name}"
    }
    return titles.get(event_type, f"Evento relacionado con {company_name}")

def _generate_mock_assessment(risk_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic assessment data"""
    risk_levels = ["green", "orange", "red"]
    
    return {
        "turnover": risk_levels[random.randint(0, 2)],
        "shareholding": risk_levels[random.randint(0, 2)],
        "bankruptcy": risk_levels[random.randint(0, 2)],
        "legal": risk_profile["overall_risk"],
        "corruption": risk_levels[random.randint(0, 2)],
        "overall": risk_profile["overall_risk"],
        "summary": f"Evaluación de riesgo basada en datos históricos y patrones del sector"
    }

def _generate_mock_vat() -> str:
    """Generate realistic Spanish VAT number"""
    return f"ES{random.randint(10000000, 99999999)}"

def _get_random_sector() -> str:
    """Get random business sector"""
    sectors = [
        "Banking", "Energy", "Telecommunications", "Construction", 
        "Manufacturing", "Technology", "Healthcare", "Retail"
    ]
    return sectors[random.randint(0, len(sectors)-1)]

def generate_mock_management_summary(company_name: str) -> Dict[str, Any]:
    """Generate enhanced mock management summary with realistic data"""
    
    # Generate mock key risks based on company profile
    risk_profile = _get_company_risk_profile(company_name)
    key_risks = _generate_mock_key_risks(company_name, risk_profile)
    
    # Generate mock financial health
    financial_health = _generate_mock_financial_health(risk_profile)
    
    # Generate mock compliance status
    compliance_status = _generate_mock_compliance_status(risk_profile)
    
    # Generate mock key findings and recommendations
    key_findings = _generate_mock_key_findings(company_name, risk_profile)
    recommendations = _generate_mock_recommendations(risk_profile)

    response = {
        "company_name": company_name,
        "overall_risk": risk_profile["overall_risk"],
        "executive_summary": _generate_mock_executive_summary(company_name, risk_profile),
        "risk_breakdown": _generate_mock_risk_breakdown(risk_profile),
        "key_findings": key_findings,
        "recommendations": recommendations,
        "financial_health": financial_health,
        "key_risks": key_risks,
        "compliance_status": compliance_status,
        "generated_at": datetime.utcnow().isoformat(),
        "method": "enhanced_mock",
        "fallback": True,
        "message": "Using enhanced fallback data - BigQuery service unavailable"
    }
    
    logger.info(f"Generated enhanced mock management summary for {company_name}")
    return response

def _generate_mock_key_risks(company_name: str, risk_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate realistic key risks"""
    risk_types = [
        {
            "risk_type": "Regulatory",
            "description": f"Riesgo regulatorio alto debido a investigaciones en curso sobre {company_name}",
            "severity": "high" if risk_profile["overall_risk"] == "red" else "medium",
            "recommendations": [
                "Reforzar el departamento de compliance",
                "Actualizar políticas regulatorias",
                "Implementar auditorías internas adicionales"
            ]
        },
        {
            "risk_type": "Legal",
            "description": f"Exposición a litigios por prácticas comerciales de {company_name}",
            "severity": "high" if risk_profile["overall_risk"] == "red" else "medium",
            "recommendations": [
                "Revisar políticas de gobernanza",
                "Consultar con el departamento legal",
                "Evaluar exposición a litigios"
            ]
        },
        {
            "risk_type": "Financial",
            "description": f"Vulnerabilidades financieras detectadas en {company_name}",
            "severity": "medium",
            "recommendations": [
                "Análisis detallado de ratios financieros",
                "Evaluación de liquidez y solvencia",
                "Monitoreo de indicadores financieros clave"
            ]
        }
    ]
    
    return risk_types[:2] if risk_profile["overall_risk"] == "green" else risk_types

def _generate_mock_financial_health(risk_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic financial health indicators"""
    if risk_profile["overall_risk"] == "red":
        status = "concerning"
        indicators = [
            {"indicator": "Liquidity Ratio", "value": "1.2", "status": "negative"},
            {"indicator": "Debt to Equity", "value": "1.8", "status": "negative"},
            {"indicator": "Profit Margin", "value": "3.5%", "status": "negative"}
        ]
    elif risk_profile["overall_risk"] == "orange":
        status = "stable"
        indicators = [
            {"indicator": "Liquidity Ratio", "value": "1.5", "status": "neutral"},
            {"indicator": "Debt to Equity", "value": "1.2", "status": "neutral"},
            {"indicator": "Profit Margin", "value": "8.2%", "status": "neutral"}
        ]
    else:
        status = "healthy"
        indicators = [
            {"indicator": "Liquidity Ratio", "value": "2.1", "status": "positive"},
            {"indicator": "Debt to Equity", "value": "0.8", "status": "positive"},
            {"indicator": "Profit Margin", "value": "15.3%", "status": "positive"}
        ]
    
    return {"status": status, "indicators": indicators}

def _generate_mock_compliance_status(risk_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic compliance status"""
    if risk_profile["overall_risk"] == "red":
        overall = "partial"
        areas = [
            {"area": "AML Compliance", "status": "partial", "details": "Algunas áreas requieren mejora"},
            {"area": "Corporate Governance", "status": "partial", "details": "Políticas en proceso de actualización"},
            {"area": "Financial Reporting", "status": "compliant", "details": "Reportes presentados correctamente"}
        ]
    elif risk_profile["overall_risk"] == "orange":
        overall = "compliant"
        areas = [
            {"area": "AML Compliance", "status": "compliant", "details": "Cumple con los requisitos"},
            {"area": "Corporate Governance", "status": "compliant", "details": "Políticas actualizadas"},
            {"area": "Financial Reporting", "status": "compliant", "details": "Reportes a tiempo"}
        ]
    else:
        overall = "compliant"
        areas = [
            {"area": "AML Compliance", "status": "compliant", "details": "Excelente cumplimiento"},
            {"area": "Corporate Governance", "status": "compliant", "details": "Mejores prácticas implementadas"},
            {"area": "Financial Reporting", "status": "compliant", "details": "Reportes ejemplares"}
        ]
    
    return {"overall": overall, "areas": areas}

def _generate_mock_key_findings(company_name: str, risk_profile: Dict[str, Any]) -> List[str]:
    """Generate realistic key findings"""
    if risk_profile["overall_risk"] == "red":
        return [
            f"Riesgo regulatorio alto detectado en {company_name}",
            "Exposición significativa a litigios legales",
            "Indicadores financieros muestran deterioro",
            "Problemas de cumplimiento identificados"
        ]
    elif risk_profile["overall_risk"] == "orange":
        return [
            f"Riesgo moderado identificado en {company_name}",
            "Algunas áreas requieren monitoreo adicional",
            "Indicadores financieros estables",
            "Cumplimiento regulatorio adecuado"
        ]
    else:
        return [
            f"Perfil de riesgo favorable para {company_name}",
            "Indicadores financieros saludables",
            "Cumplimiento regulatorio excelente",
            "Gobernanza corporativa sólida"
        ]

def _generate_mock_recommendations(risk_profile: Dict[str, Any]) -> List[str]:
    """Generate realistic recommendations"""
    if risk_profile["overall_risk"] == "red":
        return [
            "Implementar medidas inmediatas de mitigación de riesgo",
            "Reforzar el departamento de compliance",
            "Realizar auditoría externa completa",
            "Establecer monitoreo continuo de indicadores clave"
        ]
    elif risk_profile["overall_risk"] == "orange":
        return [
            "Mantener monitoreo regular de indicadores de riesgo",
            "Actualizar políticas de gobernanza",
            "Implementar mejoras incrementales en compliance",
            "Establecer alertas tempranas para cambios de riesgo"
        ]
    else:
        return [
            "Mantener las buenas prácticas actuales",
            "Continuar con el monitoreo regular",
            "Considerar oportunidades de mejora continua",
            "Documentar mejores prácticas para referencia futura"
        ]

def _generate_mock_executive_summary(company_name: str, risk_profile: Dict[str, Any]) -> str:
    """Generate realistic executive summary"""
    if risk_profile["overall_risk"] == "red":
        return f"Análisis ejecutivo de {company_name} revela un perfil de riesgo alto que requiere atención inmediata del consejo de administración. Se han identificado múltiples factores de riesgo que justifican una revisión exhaustiva de las políticas y procedimientos corporativos."
    elif risk_profile["overall_risk"] == "orange":
        return f"Evaluación ejecutiva de {company_name} indica un perfil de riesgo moderado que requiere monitoreo continuo. Aunque la situación actual es manejable, se recomienda implementar medidas preventivas para mitigar riesgos potenciales."
    else:
        return f"Análisis ejecutivo de {company_name} muestra un perfil de riesgo favorable con indicadores sólidos de gobernanza y cumplimiento. La empresa mantiene buenas prácticas que contribuyen a su estabilidad operativa."

def _generate_mock_risk_breakdown(risk_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate realistic risk breakdown"""
    if risk_profile["overall_risk"] == "red":
        return {
            "legal": {
                "level": "high",
                "reasoning": "Litigios recientes y investigaciones regulatorias activas.",
                "evidence": ["Caso 123/2024", "Demanda civil 456/2024", "Investigación CNMV"],
                "confidence": 0.9
            },
            "financial": {
                "level": "high",
                "reasoning": "Indicadores financieros muestran deterioro significativo.",
                "evidence": ["Ratio de liquidez 1.2", "Margen de beneficio 3.5%"],
                "confidence": 0.85
            }
        }
    elif risk_profile["overall_risk"] == "orange":
        return {
            "legal": {
                "level": "medium",
                "reasoning": "Algunos procedimientos legales menores en curso.",
                "evidence": ["Procedimiento administrativo 789/2024"],
                "confidence": 0.75
            },
            "financial": {
                "level": "medium",
                "reasoning": "Indicadores financieros estables con algunas áreas de mejora.",
                "evidence": ["Ratio de liquidez 1.5", "Margen de beneficio 8.2%"],
                "confidence": 0.8
            }
        }
    else:
        return {
            "legal": {
                "level": "low",
                "reasoning": "Sin procedimientos legales significativos.",
                "evidence": ["Cumplimiento regulatorio verificado"],
                "confidence": 0.9
            },
            "financial": {
                "level": "low",
                "reasoning": "Indicadores financieros saludables.",
                "evidence": ["Ratio de liquidez 2.1", "Margen de beneficio 15.3%"],
                "confidence": 0.85
            }
        }

def generate_mock_risk_trends() -> Dict[str, Any]:
    """Generate enhanced mock risk trends with realistic patterns"""
    return {
        "trends": {
            "overall_risk_trend": random.choice(["increasing", "stable", "decreasing"]),
            "high_risk_companies": random.randint(15, 25),
            "medium_risk_companies": random.randint(40, 70),
            "low_risk_companies": random.randint(120, 180),
            "total_companies_assessed": random.randint(180, 250),
        },
        "recent_events": [
            {
                "company": "Banco Santander",
                "event_type": "regulatory_investigation",
                "risk_level": "high",
                "date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            },
            {
                "company": "BBVA",
                "event_type": "legal_proceeding",
                "risk_level": "medium",
                "date": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            },
            {
                "company": "Iberdrola",
                "event_type": "financial_report",
                "risk_level": "low",
                "date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            },
        ],
        "sector_analysis": {
            "banking": {"risk_level": "high", "trend": "increasing"},
            "energy": {"risk_level": "medium", "trend": "stable"},
            "telecommunications": {"risk_level": "low", "trend": "decreasing"},
            "construction": {"risk_level": "medium", "trend": "stable"},
            "technology": {"risk_level": "low", "trend": "decreasing"},
        },
        "fallback": True,
        "message": "Using enhanced fallback data - BigQuery service unavailable"
    }

def generate_mock_comparison(companies: List[str]) -> Dict[str, Any]:
    """Generate enhanced mock company comparison"""
    comparison_data = []
    
    for company in companies:
        risk_profile = _get_company_risk_profile(company)
        comparison_data.append({
            "company_name": company,
            "risk_assessment": {
                "turnover": random.choice(["green", "orange", "red"]),
                "shareholding": random.choice(["green", "orange", "red"]),
                "bankruptcy": random.choice(["green", "orange", "red"]),
                "legal": risk_profile["overall_risk"],
                "overall": risk_profile["overall_risk"],
            },
            "recent_events": random.randint(3, 15),
            "risk_score": random.randint(20, 80) if risk_profile["overall_risk"] != "red" else random.randint(70, 95),
            "trend": random.choice(["increasing", "stable", "decreasing"])
        })
    
    # Calculate comparison metrics
    risk_scores = [comp["risk_score"] for comp in comparison_data]
    highest_risk = max(comparison_data, key=lambda x: x["risk_score"])
    lowest_risk = min(comparison_data, key=lambda x: x["risk_score"])
    
    return {
        "comparison_data": comparison_data,
        "summary": {
            "highest_risk": highest_risk,
            "lowest_risk": lowest_risk,
            "average_risk_score": round(sum(risk_scores) / len(risk_scores), 1),
            "risk_correlation": round(random.uniform(0.3, 0.8), 2)
        },
        "fallback": True,
        "message": "Using enhanced fallback data - BigQuery service unavailable"
    } 