from typing import Dict, Any, List, Optional
from app.agents.search.base_agent import BaseSearchAgent
from app.agents.search.boe_agent import BOEIngestionAgent
from app.agents.search.newsapi_agent import NewsAPIAgent
import logging

logger = logging.getLogger(__name__)

class SearchOrchestrator:
    """Orchestrates multiple search agents"""
    
    def __init__(self):
        """Initialize search agents"""
        self.agents = {
            "boe": BOEIngestionAgent(),
            "newsapi": NewsAPIAgent()
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
        Search across all active agents
        
        Args:
            query: Search query
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            days_back: Number of days to look back if dates not specified
            active_agents: List of agent names to use (default: all agents)
            
        Returns:
            Dict containing results from all agents
        """
        results = {}
        
        # Determine which agents to use
        if active_agents is None:
            active_agents = list(self.agents.keys())
        
        # Search with each active agent
        for agent_name in active_agents:
            if agent_name not in self.agents:
                logger.warning(f"Unknown agent: {agent_name}")
                continue
                
            try:
                agent = self.agents[agent_name]
                agent_results = await agent.search(
                    query=query,
                    start_date=start_date,
                    end_date=end_date,
                    days_back=days_back
                )
                results[agent_name] = agent_results
                logger.info(f"✅ {agent_name} search completed successfully")
            except Exception as e:
                logger.error(f"❌ {agent_name} search failed: {e}")
                results[agent_name] = {
                    "error": str(e),
                    "search_summary": {
                        "query": query,
                        "date_range": f"{start_date} to {end_date}",
                        "total_results": 0
                    }
                }
        
        return results 