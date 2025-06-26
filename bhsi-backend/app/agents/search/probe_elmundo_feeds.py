import feedparser

EL_MUNDO_FEEDS = [
    ("National", "https://e00-elmundo.uecdn.es/elmundo/rss/espana.xml"),
    ("Economy", "https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml"),
    ("Business", "https://e00-elmundo.uecdn.es/elmundo/rss/empresas.xml"),
    ("World", "https://e00-elmundo.uecdn.es/elmundo/rss/sucesos.xml"),
    ("Opinion", "https://e00-elmundo.uecdn.es/elmundo/rss/opinion.xml"),
    ("Sports", "https://e00-elmundo.uecdn.es/elmundo/rss/deportes.xml"),
    ("Culture", "https://e00-elmundo.uecdn.es/elmundo/rss/cultura.xml"),
    ("Science", "https://e00-elmundo.uecdn.es/elmundo/rss/ciencia.xml"),
    ("Technology", "https://e00-elmundo.uecdn.es/elmundo/rss/tecnologia.xml"),
    ("Health", "https://e00-elmundo.uecdn.es/elmundo/rss/salud.xml"),
    ("Travel", "https://e00-elmundo.uecdn.es/elmundo/rss/viajes.xml"),
    ("Food", "https://e00-elmundo.uecdn.es/elmundo/rss/cocina.xml"),
]

def probe_feeds():
    print("Probing El Mundo RSS feeds...\n")
    for name, url in EL_MUNDO_FEEDS:
        feed = feedparser.parse(url)
        print(f"[{name}] {url} -> {len(feed.entries)} entries")
        if feed.bozo:
            print(f"  ❌ Invalid feed: {feed.bozo_exception}")
        else:
            print("  ✅ Valid")

if __name__ == "__main__":
    probe_feeds() 