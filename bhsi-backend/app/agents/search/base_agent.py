from abc import ABC, abstractmethod
from typing import List, Dict, Any
import aiohttp
import asyncio
from app.core.config import settings


class BaseSearchAgent(ABC):
    def __init__(self):
        self.session = None
        self.headers = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform a search query and return results
        """
        pass
    
    async def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL
        """
        if not self.session:
            raise RuntimeError("Agent must be used as an async context manager")
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    def clean_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and standardize search results
        """
        cleaned = []
        for result in results:
            cleaned.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "url": result.get("url", ""),
                "source": self.__class__.__name__,
                "timestamp": result.get("timestamp", "")
            })
        return cleaned 