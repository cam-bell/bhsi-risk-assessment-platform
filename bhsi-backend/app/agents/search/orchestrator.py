from typing import Dict, Any, List
from app.agents.search.google_agent import GoogleSearchAgent
from app.agents.search.bing_agent import BingSearchAgent
from app.agents.search.spanish_gov_agent import SpanishGovAgent
from app.agents.search.news_agent import NewsAgencyAgent

class SearchOrchestrator:
    def __init__(self):
        self.agents = {
            'google': GoogleSearchAgent(),
            'bing': BingSearchAgent(),
            'gov': SpanishGovAgent(),
            'news': NewsAgencyAgent()
        }
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Search for company information using all available search agents
        """
        results = {}
        for name, agent in self.agents.items():
            try:
                results[name] = await agent.search(company_name)
            except Exception as e:
                results[name] = {"error": str(e)}
        
        return results 