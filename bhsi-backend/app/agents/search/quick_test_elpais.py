import feedparser

# Use one or more El País RSS URLs
feeds = [
    ("El País - Nacional", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ("El País - Economía", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada"),
    ("El País - Negocios", "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/economia/subsection/negocios"),
    ("El País - Tecnología", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada"),
    ("El País - Clima", "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/clima-y-medio-ambiente"),
]

for name, url in feeds:
    feed = feedparser.parse(url)
    print(f"[{name}] {url} -> {len(feed.entries)} entries")
    if feed.bozo:
        print(f"  ❌ Invalid feed: {feed.bozo_exception}")
    else:
        print("  ✅ Valid")
