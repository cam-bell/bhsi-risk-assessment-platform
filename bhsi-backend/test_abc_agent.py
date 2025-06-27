#!/usr/bin/env python3
"""
Test ABC RSS Agent (Updated Feeds)
"""

import asyncio
from app.agents.search.streamlined_abc_agent import StreamlinedABCAgent

async def test_abc_agent():
    print("🧪 Testing ABC RSS Agent (Updated Feeds)")
    print("=" * 50)
    agent = StreamlinedABCAgent()
    test_queries = ["Banco Santander", "economía", "internacional", "sociedad"]
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        try:
            results = await agent.search(query=query, days_back=7)
            print(f"✅ Search completed successfully")
            print(f"📊 Total results: {results['search_summary']['total_results']}")
            print(f"📰 Feeds searched: {results['search_summary']['feeds_searched']}")
            if results['search_summary']['errors']:
                print(f"⚠️  Errors: {results['search_summary']['errors']}")
            articles = results.get('articles', [])
            if articles:
                print(f"\n📄 Sample results:")
                for i, article in enumerate(articles[:3]):
                    print(f"  {i+1}. {article['title'][:80]}...")
                    print(f"     Category: {article['category']}")
                    print(f"     Date: {article['publishedAt']}")
                    print(f"     URL: {article['url']}")
                    print()
            else:
                print("❌ No articles found")
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
    print("\n" + "=" * 50)
    print("✅ ABC agent test completed")

if __name__ == "__main__":
    asyncio.run(test_abc_agent()) 