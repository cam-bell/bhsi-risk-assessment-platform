"""
NOTE: Expansión RSS feeds return entries but trigger a feedparser warning:
'document declared as us-ascii, but parsed as utf-8'.
Despite this, the feeds are accessible and usable for automation, but monitor for future format changes.
"""
import feedparser

feeds = [
    # Empresas
    ("Expansión - Nombramientos", "https://e00-expansion.uecdn.es/rss/empresas/nombramientos.xml"),
    ("Expansión - Distribución y Consumo", "https://e00-expansion.uecdn.es/rss/empresas/distribucion.xml"),
    ("Expansión - Banca", "https://e00-expansion.uecdn.es/rss/empresasbanca.xml"),
    ("Expansión - Pymes", "https://e00-expansion.uecdn.es/rss/pymes.xml"),
    # Economía
    ("Expansión - Economía Política", "https://e00-expansion.uecdn.es/rss/economia/politica.xml"),
    ("Expansión - Economía Portada", "https://e00-expansion.uecdn.es/rss/economia.xml"),
    # Mercados
    ("Expansión - Crónica de Bolsa", "https://e00-expansion.uecdn.es/rss/mercados/cronica-bolsa.xml"),
    # Jurídico
    ("Expansión - Sentencias", "https://e00-expansion.uecdn.es/rss/juridicosentencias.xml"),
    ("Expansión - Actualidad y tendencias", "https://e00-expansion.uecdn.es/rss/juridico/actualidad-tendencias.xml"),
    # Fiscal
    ("Expansión - Tribunales", "https://e00-expansion.uecdn.es/rss/fiscal/tribunales.xml"),
    # Economía Sostenible
    ("Expansión - Economía Sostenible", "https://e00-expansion.uecdn.es/rss/economia-sostenible.xml"),
    # Expansión y Empleo
    ("Expansión - Empleo", "https://e00-expansion.uecdn.es/rss/expansion-empleo/empleo.xml"),
    # Economía Digital
    ("Expansión - Innovación", "https://e00-expansion.uecdn.es/rss/economia-digital/innovacion.xml"),
]

for name, url in feeds:
    feed = feedparser.parse(url)
    print(f"[{name}] {url} -> {len(feed.entries)} entries")
    if feed.bozo:
        print(f"  ❌ Invalid feed: {feed.bozo_exception}")
    else:
        print("  ✅ Valid")
