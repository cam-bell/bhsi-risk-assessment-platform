from typing import List, Dict, Any
import aiohttp
from datetime import datetime, timedelta
from app.core.config import settings
from .base_agent import BaseSearchAgent


class NewsAgencyAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.sources = [
            {
                "name": "El País",
                "url": "https://elpais.com/buscar/",
                "api_key": settings.ELPAIS_API_KEY
            },
            {
                "name": "El Mundo",
                "url": "https://www.elmundo.es/buscador.html",
                "api_key": settings.ELMUNDO_API_KEY
            },
            {
                "name": "Expansión",
                "url": "https://www.expansion.com/busqueda.html",
                "api_key": settings.EXPANSION_API_KEY
            }
        ]
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search across Spanish news agencies
        """
        results = []
        for source in self.sources:
            try:
                # In a real implementation, you would:
                # 1. Use each news agency's API if available
                # 2. Implement proper rate limiting
                # 3. Handle different response formats
                # 4. Add more sophisticated content extraction
                
                # Example for El País
                if source["name"] == "El País":
                    params = {
                        "q": query,
                        "api_key": source["api_key"],
                        "from_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                        "to_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    async with self.session.get(source["url"], params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        for article in data.get("articles", []):
                            results.append({
                                "title": article.get("title", ""),
                                "snippet": article.get("summary", ""),
                                "url": article.get("url", ""),
                                "timestamp": article.get("published_at", "")
                            })
                
                # Add similar processing for other news sources
                
            except Exception as e:
                # Log the error but continue with other sources
                print(f"Error searching {source['name']}: {str(e)}")
                continue
        
        return self.clean_results(results)
    
    async def fetch_url(self, url: str) -> str:
        """
        Override fetch_url to add specific headers for news sites
        """
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        headers = {
            "User-Agent": "BHSI-Risk-Assessment/1.0",
            "Accept": "application/json",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text() 