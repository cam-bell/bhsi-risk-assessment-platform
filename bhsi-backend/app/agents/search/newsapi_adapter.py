import json
from typing import Dict, Any

def newsapi_article_to_rawdoc(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a NewsAPI article dict to a dict suitable for RawDoc insertion.
    """
    payload_bytes = json.dumps(article, sort_keys=True).encode("utf-8")
    meta = {
        "url": article.get("url"),
        "publishedAt": article.get("publishedAt"),
        "source": article.get("source", {}).get("name"),
        "title": article.get("title"),
        "author": article.get("author"),
        "description": article.get("description"),
        "urlToImage": article.get("urlToImage"),
    }
    return {
        "source": "NewsAPI",
        "payload": payload_bytes,
        "meta": meta
    }
