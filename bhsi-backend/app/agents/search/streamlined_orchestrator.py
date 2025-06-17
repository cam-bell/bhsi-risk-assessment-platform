#!/usr/bin/env python3
"""
Streamlined Search Orchestrator - Fast search without classification during search
"""

import logging
from typing import Dict, Any, List, Optional
from app.agents.search.streamlined_boe_agent import StreamlinedBOEAgent
from app.agents.search.streamlined_newsapi_agent import StreamlinedNewsAPIAgent

logger = logging.getLogger(__name__)


class StreamlinedSearchOrchestrator:
    """Ultra-fast search orchestrator - data fetching only, classification happens later"""
    
    def __init__(self):
        """Initialize streamlined search agents"""
        self.agents = {
            "boe": StreamlinedBOEAgent(),
            "newsapi": StreamlinedNewsAPIAgent()
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
        FAST search across all active agents - no classification during search
        """
        results = {}
        
        # Determine which agents to use
        if active_agents is None:
            active_agents = list(self.agents.keys())
        
        logger.info(f"🔍 Streamlined search: '{query}' using {active_agents}")
        
        # Search with each active agent in parallel if possible
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
                
                result_count = 0
                if agent_name == "boe":
                    result_count = len(agent_results.get("results", []))
                elif agent_name == "newsapi":
                    result_count = len(agent_results.get("articles", []))
                
                logger.info(f"✅ {agent_name}: {result_count} results")
                
            except Exception as e:
                logger.error(f"❌ {agent_name} search failed: {e}")
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