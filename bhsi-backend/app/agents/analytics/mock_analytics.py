import random
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def generate_mock_analytics(company_name: str) -> Dict[str, Any]:
    return {
        "company_name": company_name,
        "risk_profile": {
            "turnover": random.choice(["green", "orange", "red"]),
            "shareholding": random.choice(["green", "orange", "red"]),
            "bankruptcy": random.choice(["green", "orange", "red"]),
            "legal": random.choice(["green", "orange", "red"]),
            "corruption": random.choice(["green", "orange", "red"]),
            "overall": random.choice(["green", "orange", "red"]),
        },
        "analysis_summary": f"Análisis completo de {company_name} realizado con datos de múltiples fuentes. Se han identificado varios factores de riesgo que requieren atención.",
        "trends": {
            "risk_trend": random.choice(["increasing", "stable", "decreasing"]),
            "recent_events": random.randint(1, 10),
            "high_risk_events": random.randint(0, 5),
            "historical_comparison": {
                "current_period": random.randint(5, 20),
                "previous_period": random.randint(5, 20),
                "change_percentage": round(random.uniform(-10, 10), 1),
            },
        },
        "processed_results": {
            "google_results": [],
            "bing_results": [],
            "gov_results": [],
            "news_results": [],
        },
    }

def generate_mock_management_summary(company_name: str) -> Dict[str, Any]:
    # Generate mock key risks
    key_risks = [
        {
            "risk_type": "Regulatory",
            "description": "Riesgo regulatorio alto debido a investigaciones en curso",
            "severity": random.choice(["high", "medium", "low"]),
            "recommendations": [
                "Reforzar el departamento de compliance",
                "Actualizar políticas regulatorias"
            ]
        },
        {
            "risk_type": "Legal",
            "description": "Exposición a litigios por prácticas comerciales",
            "severity": random.choice(["high", "medium", "low"]),
            "recommendations": [
                "Revisar políticas de gobernanza",
                "Consultar con el departamento legal"
            ]
        },
        {
            "risk_type": "Governance",
            "description": "Vulnerabilidades en gobernanza corporativa",
            "severity": random.choice(["high", "medium", "low"]),
            "recommendations": [
                "Implementar auditorías internas adicionales",
                "Mejorar la transparencia en la gestión"
            ]
        }
    ]

    # Generate mock financial health
    financial_health = {
        "status": random.choice(["healthy", "concerning", "critical"]),
        "indicators": [
            {
                "indicator": "Liquidity Ratio",
                "value": f"{round(random.uniform(1.0, 2.5), 2)}",
                "status": random.choice(["positive", "neutral", "negative"])
            },
            {
                "indicator": "Debt to Equity",
                "value": f"{round(random.uniform(0.2, 1.5), 2)}",
                "status": random.choice(["positive", "neutral", "negative"])
            },
            {
                "indicator": "Profit Margin",
                "value": f"{round(random.uniform(5, 25), 1)}%",
                "status": random.choice(["positive", "neutral", "negative"])
            }
        ]
    }

    # Generate mock compliance status
    compliance_status = {
        "overall": random.choice(["compliant", "partial", "non_compliant"]),
        "areas": [
            {
                "area": "AML Compliance",
                "status": random.choice(["compliant", "partial", "non_compliant"]),
                "details": "Cumple con la mayoría de los requisitos de prevención de blanqueo de capitales."
            },
            {
                "area": "Corporate Governance",
                "status": random.choice(["compliant", "partial", "non_compliant"]),
                "details": "Algunas políticas de gobernanza requieren actualización."
            },
            {
                "area": "Financial Reporting",
                "status": random.choice(["compliant", "partial", "non_compliant"]),
                "details": "Reportes financieros presentados a tiempo, pero con observaciones menores."
            }
        ]
    }

    # Example mock values for required fields
    response = {
        "company_name": company_name,
        "overall_risk": "red",
        "executive_summary": f"Análisis ejecutivo completo de {company_name}. Se han identificado varios factores de riesgo que requieren atención inmediata del consejo de administración.",
        "risk_breakdown": {
            "legal": {
                "level": "high",
                "reasoning": "Litigios recientes detectados.",
                "evidence": ["Caso 123/2024", "Demanda civil 456/2024"],
                "confidence": 0.9
            },
            "financial": {
                "level": "medium",
                "reasoning": "Margen de beneficio reducido.",
                "evidence": ["Informe Q1 2024"],
                "confidence": 0.8
            }
        },
        "key_findings": [
            "Riesgo regulatorio alto debido a investigaciones en curso",
            "Exposición a litigios por prácticas comerciales"
        ],
        "recommendations": [
            "Reforzar el departamento de compliance",
            "Actualizar políticas regulatorias"
        ],
        "generated_at": "2024-06-01T12:00:00Z",
        "method": "mock"
    }
    logger.info("Returning mock management summary: %s", response)
    return response

def generate_mock_risk_trends() -> Dict[str, Any]:
    return {
        "trends": {
            "overall_risk_trend": random.choice(["increasing", "stable", "decreasing"]),
            "high_risk_companies": random.randint(10, 20),
            "medium_risk_companies": random.randint(30, 60),
            "low_risk_companies": random.randint(100, 150),
            "total_companies_assessed": random.randint(150, 200),
        },
        "recent_events": [
            {
                "company": "Banco Santander",
                "event_type": "regulatory_investigation",
                "risk_level": "high",
                "date": "2024-06-01T12:00:00Z",
            },
            {
                "company": "BBVA",
                "event_type": "legal_proceeding",
                "risk_level": "medium",
                "date": "2024-05-28T12:00:00Z",
            },
        ],
        "sector_analysis": {
            "banking": {"risk_level": "high", "trend": "increasing"},
            "energy": {"risk_level": "medium", "trend": "stable"},
            "telecommunications": {"risk_level": "low", "trend": "decreasing"},
        },
    }

def generate_mock_comparison(companies: List[str]) -> Dict[str, Any]:
    comparison_data = []
    for company in companies:
        comparison_data.append({
            "company_name": company,
            "risk_assessment": {
                "turnover": random.choice(["green", "orange", "red"]),
                "shareholding": random.choice(["green", "orange", "red"]),
                "bankruptcy": random.choice(["green", "orange", "red"]),
                "legal": random.choice(["green", "orange", "red"]),
                "overall": random.choice(["green", "orange", "red"]),
            },
            "recent_events": random.randint(1, 10),
            "risk_score": random.randint(0, 100),
        })
    return {
        "comparison_data": comparison_data,
        "summary": {
            "highest_risk": max(comparison_data, key=lambda x: x["risk_score"]),
            "lowest_risk": min(comparison_data, key=lambda x: x["risk_score"]),
            "average_risk_score": sum(x["risk_score"] for x in comparison_data) / len(comparison_data),
        },
    } 