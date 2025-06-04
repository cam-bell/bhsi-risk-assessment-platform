from typing import List, Dict, Any
import asyncio
from .search.google_agent import GoogleSearchAgent
from .search.bing_agent import BingSearchAgent
from .search.spanish_gov_agent import SpanishGovAgent
from .search.news_agent import NewsAgencyAgent


class SearchOrchestrator:
    def __init__(self):
        self.agents = [
            GoogleSearchAgent(),
            BingSearchAgent(),
            SpanishGovAgent(),
            NewsAgencyAgent()
        ]
    
    async def search_all(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute search across all agents in parallel
        """
        async def search_with_agent(agent):
            try:
                async with agent as a:
                    return agent.__class__.__name__, await a.search(query)
            except Exception as e:
                print(f"Error with {agent.__class__.__name__}: {str(e)}")
                return agent.__class__.__name__, []
        
        # Run all searches in parallel
        tasks = [search_with_agent(agent) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        
        # Organize results by agent
        return {
            agent_name: agent_results
            for agent_name, agent_results in results
        }
    
    async def search_company(self, company_name: str, vat_number: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for company information using both name and VAT number
        """
        # Construct search queries
        queries = [company_name]
        if vat_number:
            queries.append(vat_number)
        
        # Search for each query
        all_results = {}
        for query in queries:
            results = await self.search_all(query)
            
            # Merge results
            for agent_name, agent_results in results.items():
                if agent_name not in all_results:
                    all_results[agent_name] = []
                all_results[agent_name].extend(agent_results)
        
        return all_results 