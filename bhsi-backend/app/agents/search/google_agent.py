from typing import List, Dict, Any
import aiohttp
from app.core.config import settings
from .base_agent import BaseSearchAgent


class GoogleSearchAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.headers = {
            "Accept": "application/json"
        }
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a Google Custom Search API query
        """
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google API key and Search Engine ID must be configured")
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": 10  # Number of results
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "timestamp": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", "")
                })
            
            return self.clean_results(results) 