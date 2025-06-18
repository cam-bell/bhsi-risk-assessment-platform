#!/usr/bin/env python3
"""
Streamlined Search Orchestrator - Fast search without classification during search
Updated to include Google Custom Search integration
"""

import logging
from typing import Dict, Any, List, Optional
from app.agents.search.streamlined_boe_agent import StreamlinedBOEAgent
from app.agents.search.streamlined_newsapi_agent import StreamlinedNewsAPIAgent
from app.agents.search.google_news_agent import GoogleNewsSearchAgent

logger = logging.getLogger(__name__)


class StreamlinedSearchOrchestrator:
    """Ultra-fast search orchestrator - data fetching only, classification happens later"""
    
    def __init__(self):
        """Initialize streamlined search agents"""
        self.agents = {
            "boe": StreamlinedBOEAgent(),
            "newsapi": StreamlinedNewsAPIAgent(),
            "google": GoogleNewsSearchAgent()  # Added Google Custom Search
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
        Now includes Google Custom Search for news.google.com
        """
        results = {}
        
        # Determine which agents to use
        if active_agents is None:
            active_agents = list(self.agents.keys())
        
        logger.info(f"🔍 Streamlined search: '{query}' using {active_agents}")
        
        # Search with each active agent
        for agent_name in active_agents:
            if agent_name not in self.agents:
                logger.warning(f"Unknown agent: {agent_name}")
                continue
                
            try:
                agent = self.agents[agent_name]
                
                # Different agents have slightly different signatures
                if agent_name == "google":
                    # Google agent uses consistent parameter names
                    async with agent:  # Google agent requires context manager
                        agent_results = await agent.search(
                            query=query,
                            start_date=start_date,
                            end_date=end_date,
                            days_back=days_back
                        )
                else:
                    # BOE and NewsAPI agents
                    agent_results = await agent.search(
                        query=query,
                        start_date=start_date,
                        end_date=end_date,
                        days_back=days_back
                    )
                
                results[agent_name] = agent_results
                
                # Log results count for each agent type
                result_count = self._get_result_count(agent_name, agent_results)
                logger.info(f"✅ {agent_name}: {result_count} results")
                
            except Exception as e:
                logger.error(f"❌ {agent_name} search failed: {e}")
                results[agent_name] = {
                    "error": str(e),
                    "search_summary": {
                        "query": query,
                        "source": agent_name.title(),
                        "date_range": f"{start_date} to {end_date}",
                        "total_results": 0,
                        "errors": [str(e)]
                    }
                }
        
        return results
    
    def _get_result_count(self, agent_name: str, agent_results: Dict[str, Any]) -> int:
        """Get result count based on agent response format"""
        try:
            if agent_name == "boe":
                return len(agent_results.get("results", []))
            elif agent_name == "newsapi":
                return len(agent_results.get("articles", []))
            elif agent_name == "google":
                return len(agent_results.get("results", []))
            else:
                return 0
        except Exception:
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of all search agents
        """
        health_status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                if agent_name == "google":
                    # Check Google agent configuration
                    if hasattr(agent, 'api_key') and hasattr(agent, 'search_engine_id'):
                        if agent.api_key and agent.search_engine_id:
                            health_status[agent_name] = {
                                "status": "healthy",
                                "configured": True,
                                "message": "Google Custom Search configured"
                            }
                        else:
                            health_status[agent_name] = {
                                "status": "disabled",
                                "configured": False,
                                "message": "Google API credentials missing"
                            }
                    else:
                        health_status[agent_name] = {
                            "status": "error",
                            "configured": False,
                            "message": "Google agent configuration invalid"
                        }
                else:
                    # For other agents, assume healthy if they can be instantiated
                    health_status[agent_name] = {
                        "status": "healthy",
                        "configured": True,
                        "message": f"{agent_name.title()} agent available"
                    }
                    
            except Exception as e:
                health_status[agent_name] = {
                    "status": "error",
                    "configured": False,
                    "message": f"Agent error: {str(e)}"
                }
        
        return {
            "overall_status": "healthy" if all(
                status["status"] in ["healthy", "disabled"] 
                for status in health_status.values()
            ) else "degraded",
            "agents": health_status,
            "available_agents": [
                name for name, status in health_status.items() 
                if status["status"] == "healthy"
            ]
        }