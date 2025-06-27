#!/usr/bin/env python3
"""
Test Unified Search API for ABC, La Vanguardia, El Confidencial
"""

import asyncio
from app.api.v1.endpoints.search import unified_search, UnifiedSearchRequest

async def test_rss_sources():
    print("🧪 Testing Unified Search API (ABC, La Vanguardia, El Confidencial)")
    print("=" * 60)
    request = UnifiedSearchRequest(
        company_name="Banco Santander",
        days_back=7,
        include_boe=False,
        include_news=False,
        include_rss=True
    )
    response = await unified_search(request)
    print(f"\n✅ API call successful")
    print(f"📊 Total results: {response['metadata']['total_results']}")
    print(f"📰 Sources searched: {response['metadata']['sources_searched']}\n")

    for source, key in [
        ("ABC", "abc_results"),
        ("La Vanguardia", "lavanguardia_results"),
        ("El Confidencial", "elconfidencial_results"),
    ]:
        print(f"{source}: {response['metadata'][key]} results")
        sample = [r for r in response['results'] if r['source'] == source]
        if sample:
            print(f"  Sample: {sample[0]['title']} ({sample[0]['date']})")
        else:
            print("  No results found.")
        print()

    print("=" * 60)
    print("✅ RSS sources API integration test completed")

if __name__ == "__main__":
    asyncio.run(test_rss_sources()) 