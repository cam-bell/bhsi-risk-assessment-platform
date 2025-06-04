from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from app.core.config import settings
from .base_agent import BaseSearchAgent


class SpanishGovAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.sources = [
            "https://www.boe.es/",  # Official State Gazette
            "https://www.registradores.org/",  # Property and Commercial Registrars
            "https://www.cnmv.es/",  # National Securities Market Commission
            "https://www.igae.pap.hacienda.gob.es/",  # General Intervention of the State Administration
        ]
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search across Spanish government websites
        """
        results = []
        for source in self.sources:
            try:
                # Search the main page and relevant sections
                content = await self.fetch_url(source)
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract relevant information
                # This is a simplified version - in production, you'd want to:
                # 1. Handle each site's specific structure
                # 2. Implement proper rate limiting
                # 3. Add more sophisticated content extraction
                # 4. Handle different types of documents
                
                # Example for BOE
                if "boe.es" in source:
                    for article in soup.find_all('article'):
                        if query.lower() in article.text.lower():
                            results.append({
                                "title": article.find('h2').text if article.find('h2') else "BOE Article",
                                "snippet": article.find('p').text if article.find('p') else "",
                                "url": article.find('a')['href'] if article.find('a') else source,
                                "timestamp": article.find('time')['datetime'] if article.find('time') else ""
                            })
                
                # Add similar processing for other government sites
                
            except Exception as e:
                # Log the error but continue with other sources
                print(f"Error searching {source}: {str(e)}")
                continue
        
        return self.clean_results(results)
    
    async def fetch_url(self, url: str) -> str:
        """
        Override fetch_url to add specific headers for government sites
        """
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        headers = {
            "User-Agent": "BHSI-Risk-Assessment/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text() 