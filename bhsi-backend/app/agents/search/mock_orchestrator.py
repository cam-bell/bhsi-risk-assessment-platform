#!/usr/bin/env python3
"""
Mock Search Orchestrator - Comprehensive mock data for demo purposes
Provides realistic search results for all sources without external API dependencies
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class MockSearchOrchestrator:
    """Mock search orchestrator with comprehensive demo data"""
    
    def __init__(self):
        """Initialize mock data sources"""
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate comprehensive mock data for all sources"""
        
        # Spanish company names for realistic results
        spanish_companies = [
            "Banco Santander", "BBVA", "CaixaBank", "Banco Sabadell", "Bankia",
            "Iberdrola", "Telefónica", "Repsol", "Inditex", "Ferrovial",
            "ACS", "Abertis", "Endesa", "Gas Natural", "Mapfre",
            "Amadeus", "Grifols", "Cellnex", "Enagás", "Red Eléctrica"
        ]
        
        # Risk-related keywords for realistic content
        risk_keywords = [
            "multa", "sanción", "investigación", "irregularidad", "fraude",
            "quiebra", "concurso", "liquidación", "auditoría", "inspección",
            "demanda", "litigio", "arbitraje", "penalización", "suspensión",
            "regulatorio", "compliance", "gobernanza", "transparencia", 
            "corrupción"
        ]
        
        # Generate BOE mock data
        boe_results = []
        for i in range(random.randint(3, 8)):
            company = random.choice(spanish_companies)
            risk_keyword = random.choice(risk_keywords)
            
            boe_results.append({
                "identificador": f"BOE-A-2024-{random.randint(1000, 9999)}",
                "titulo": f"Resolución de la Dirección General de "
                          f"{risk_keyword.title()} sobre {company}",
                "seccion_codigo": random.choice(["I", "II", "III", "IV", "V"]),
                "seccion_nombre": random.choice([
                    "Disposiciones Generales", "Autoridades y Personal", 
                    "Otras Disposiciones", "Administración de Justicia",
                    "Administración General del Estado"
                ]),
                "fechaPublicacion": (
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ).strftime("%Y-%m-%d"),
                "url_html": f"https://www.boe.es/diario_boe/txt.php?"
                           f"id=BOE-A-2024-{random.randint(1000, 9999)}",
                "url_xml": f"https://www.boe.es/diario_boe/xml.php?"
                          f"id=BOE-A-2024-{random.randint(1000, 9999)}",
                "text": f"La Dirección General de {risk_keyword.title()} ha "
                        f"resuelto iniciar procedimiento sancionador contra "
                        f"{company} por presuntas irregularidades en materia "
                        f"de {risk_keyword}. El expediente se tramita con el "
                        f"número {random.randint(100000, 999999)}/2024.",
                "summary": f"Procedimiento sancionador contra {company} "
                           f"por {risk_keyword}",
                "section": random.choice(["I", "II", "III", "IV", "V"])
            })
        
        # Generate NewsAPI mock data
        news_articles = []
        news_sources = [
            "El País", "El Mundo", "ABC", "La Vanguardia", 
            "Expansión", "Cinco Días"
        ]
        
        for i in range(random.randint(5, 15)):
            company = random.choice(spanish_companies)
            risk_keyword = random.choice(risk_keywords)
            source = random.choice(news_sources)
            
            news_articles.append({
                "title": f"{company} enfrenta {risk_keyword} regulatorio",
                "source": {"name": source},
                "author": random.choice([
                    "Redacción", "Agencias", "Carlos López", "María García"
                ]),
                "publishedAt": (
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ).isoformat() + "Z",
                "url": f"https://www.{source.lower().replace(' ', '')}.es/"
                       f"noticias/{random.randint(1000, 9999)}",
                "urlToImage": f"https://via.placeholder.com/400x300/"
                             f"0066cc/ffffff?text={company.replace(' ', '+')}",
                "description": f"La empresa {company} se enfrenta a un nuevo "
                              f"desafío regulatorio relacionado con {risk_keyword}. "
                              f"Los analistas consideran que esto podría afectar "
                              f"su valoración en el mercado.",
                "content": f"La compañía {company} ha confirmado que está siendo "
                           f"investigada por posibles irregularidades en materia "
                           f"de {risk_keyword}. Según fuentes cercanas al proceso, "
                           f"la investigación se centra en prácticas comerciales "
                           f"que podrían no cumplir con la normativa vigente. "
                           f"Los expertos consideran que este tipo de "
                           f"procedimientos pueden tener un impacto significativo "
                           f"en la reputación y valoración de la empresa."
            })
        
        # Generate RSS mock data for each source
        rss_data = {}
        rss_sources = {
            "elpais": "El País",
            "expansion": "Expansión", 
            "elmundo": "El Mundo",
            "abc": "ABC",
            "lavanguardia": "La Vanguardia",
            "elconfidencial": "El Confidencial",
            "eldiario": "El Diario",
            "europapress": "Europa Press"
        }
        
        for source_key, source_name in rss_sources.items():
            articles = []
            for i in range(random.randint(2, 6)):
                company = random.choice(spanish_companies)
                risk_keyword = random.choice(risk_keywords)
                
                articles.append({
                    "title": f"{company}: Nuevo escándalo de {risk_keyword}",
                    "description": f"La empresa {company} se ve envuelta en un "
                                  f"nuevo escándalo relacionado con {risk_keyword}. "
                                  f"Los inversores están preocupados por el "
                                  f"impacto en el valor de las acciones.",
                    "content": f"La compañía {company} ha confirmado que está "
                               f"siendo investigada por posibles irregularidades "
                               f"en materia de {risk_keyword}. Según fuentes "
                               f"cercanas al proceso, la investigación se centra "
                               f"en prácticas comerciales que podrían no cumplir "
                               f"con la normativa vigente.",
                    "url": f"https://www.{source_name.lower().replace(' ', '')}.es/"
                           f"noticias/{random.randint(1000, 9999)}",
                    "publishedAt": (
                        datetime.now() - timedelta(days=random.randint(1, 30))
                    ).isoformat() + "Z",
                    "author": random.choice([
                        "Redacción", "Agencias", "Carlos López", "María García"
                    ]),
                    "category": random.choice([
                        "Economía", "Empresas", "Mercados", "Regulación"
                    ]),
                    "source_name": source_name
                })
            
            rss_data[source_key] = {"articles": articles}
        
        return {
            "boe": {
                "search_summary": {
                    "query": "mock_query",
                    "date_range": "2024-01-01 to 2024-12-31",
                    "total_results": len(boe_results),
                    "errors": []
                },
                "results": boe_results
            },
            "newsapi": {
                "search_summary": {
                    "query": "mock_query",
                    "date_range": "2024-01-01 to 2024-12-31", 
                    "total_results": len(news_articles),
                    "page": 1,
                    "page_size": 20,
                    "has_more": False,
                    "errors": []
                },
                "articles": news_articles
            },
            **rss_data
        }
    
    async def search_all(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: Optional[int] = 7,
        active_agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Mock search across all active agents
        Returns realistic data based on the query
        """
        results = {}
        
        # Determine which agents to use
        if active_agents is None:
            active_agents = [
                "boe", "newsapi", "elpais", "expansion", "elmundo", 
                "abc", "lavanguardia", "elconfidencial", "eldiario", 
                "europapress"
            ]
        
        logger.info(f"🎭 Mock search: '{query}' using {active_agents}")
        
        # Filter mock data based on query
        query_lower = query.lower()
        
        for agent_name in active_agents:
            if agent_name not in self.mock_data:
                logger.warning(f"Unknown mock agent: {agent_name}")
                continue
            
            try:
                # Get base mock data for this agent
                agent_data = self.mock_data[agent_name].copy()
                
                # Filter results based on query (simulate real search)
                if agent_name == "boe":
                    filtered_results = [
                        result for result in agent_data["results"]
                        if query_lower in result["titulo"].lower() or 
                           query_lower in result["text"].lower()
                    ]
                    agent_data["results"] = filtered_results[:random.randint(2, 5)]
                    agent_data["search_summary"]["total_results"] = len(
                        agent_data["results"]
                    )
                    
                elif agent_name == "newsapi":
                    filtered_articles = [
                        article for article in agent_data["articles"]
                        if query_lower in article["title"].lower() or
                           query_lower in article["description"].lower()
                    ]
                    agent_data["articles"] = filtered_articles[:random.randint(3, 8)]
                    agent_data["search_summary"]["total_results"] = len(
                        agent_data["articles"]
                    )
                    
                else:  # RSS sources
                    filtered_articles = [
                        article for article in agent_data["articles"]
                        if query_lower in article["title"].lower() or
                           query_lower in article["description"].lower()
                    ]
                    agent_data["articles"] = filtered_articles[:random.randint(1, 4)]
                
                # Update search summary
                agent_data["search_summary"]["query"] = query
                if start_date and end_date:
                    agent_data["search_summary"]["date_range"] = f"{start_date} to {end_date}"
                
                results[agent_name] = agent_data
                
                # Log results
                result_count = 0
                if agent_name == "boe":
                    result_count = len(agent_data["results"])
                else:
                    result_count = len(agent_data["articles"])
                
                logger.info(f"✅ Mock {agent_name}: {result_count} results")
                
            except Exception as e:
                logger.error(f"❌ Mock {agent_name} failed: {e}")
                results[agent_name] = {
                    "error": str(e),
                    "search_summary": {
                        "query": query,
                        "date_range": f"{start_date} to {end_date}",
                        "total_results": 0,
                        "errors": [str(e)]
                    }
                }
        
        return results 