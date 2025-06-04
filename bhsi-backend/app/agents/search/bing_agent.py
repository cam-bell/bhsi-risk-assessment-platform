from typing import List, Dict, Any
import aiohttp
from app.core.config import settings
from .base_agent import BaseSearchAgent


class BingSearchAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.api_key = settings.BING_API_KEY
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json"
        }
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a Bing Web Search API query
        """
        if not self.api_key:
            raise ValueError("Bing API key must be configured")
        
        params = {
            "q": query,
            "count": 10,  # Number of results
            "responseFilter": "Webpages",
            "mkt": "es-ES"  # Spanish market
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            results = []
            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("url", ""),
                    "timestamp": item.get("datePublished", "")
                })
            
            return self.clean_results(results) 