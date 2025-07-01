import json
from typing import Dict, Any

def rss_article_to_rawdoc(article: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Convert a generic RSS article dict to a dict suitable for RawDoc insertion.
    """
    payload_bytes = json.dumps(article, sort_keys=True).encode("utf-8")
    meta = {
        "url": article.get("url"),
        "publishedAt": article.get("publishedAt"),
        "source": source,
        "title": article.get("title"),
        "author": article.get("author"),
        "category": article.get("category"),
    }
    return {
        "source": source,
        "payload": payload_bytes,
        "meta": meta
    } 