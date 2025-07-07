import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.agents.search.base_agent import BaseSearchAgent
import anyio

KEYWORDS_RED = [
    "lawsuit", "investigation", "regulatory", "sec", "probe", "indictment"
]
KEYWORDS_ORANGE = [
    "acquisition", "merger", "executive departure", "resignation", "probe"
]


def tag_headline(headline: str) -> str:
    text = headline.lower()
    if any(word in text for word in KEYWORDS_RED):
        return "Red"
    if any(word in text for word in KEYWORDS_ORANGE):
        return "Orange"
    return "Green"


def scrape_company_news(ticker: str) -> List[Dict[str, Any]]:
    url = f"https://finance.yahoo.com/quote/{ticker}/news/"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    news_items = []
    for item in soup.select("li.stream-item.story-item"):
        # Find the headline link
        link_tag = item.find("a", class_="subtle-link")
        if not link_tag or not isinstance(link_tag, Tag):
            continue
        headline = link_tag.get_text(strip=True)
        link_url = link_tag.get("href", "")
        if not link_url:
            continue
        if not link_url.startswith("http"):
            link_url = "https://finance.yahoo.com" + link_url
        # Extract date if available
        date_tag = item.find("time")
        pub_date = None
        if date_tag and isinstance(date_tag, Tag):
            pub_date = date_tag.get("datetime")
        news_items.append({
            "headline": headline,
            "url": link_url,
            "date": pub_date,
            "sentiment": tag_headline(headline)
        })
        if len(news_items) >= 5:
            break
    return news_items


class StreamlinedYahooNewsAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.source = "Yahoo Finance News"

    async def search(
        self,
        query: str = "",
        ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Async search for Yahoo Finance news headlines for a ticker.
        Returns a dict with search_summary and articles.
        """
        if not ticker:
            return {
                "search_summary": {
                    "query": query,
                    "ticker": ticker,
                    "total_results": 0,
                    "errors": ["Ticker is required"]
                },
                "articles": []
            }
        try:
            news_items = await anyio.to_thread.run_sync(scrape_company_news, ticker)
            # Optionally filter by query
            if query:
                news_items = [item for item in news_items if query.lower() in item["headline"].lower()]
            # Optionally filter by date
            if start_date or end_date:
                def in_date_range(item):
                    if not item["date"]:
                        return True
                    try:
                        dt = datetime.fromisoformat(item["date"].replace("Z", ""))
                        if start_date and dt < datetime.fromisoformat(start_date):
                            return False
                        if end_date and dt > datetime.fromisoformat(end_date):
                            return False
                        return True
                    except Exception:
                        return True
                news_items = [item for item in news_items if in_date_range(item)]
            return {
                "search_summary": {
                    "query": query,
                    "ticker": ticker,
                    "total_results": len(news_items),
                    "errors": []
                },
                "articles": news_items
            }
        except Exception as e:
            return {
                "search_summary": {
                    "query": query,
                    "ticker": ticker,
                    "total_results": 0,
                    "errors": [str(e)]
                },
                "articles": []
            }
