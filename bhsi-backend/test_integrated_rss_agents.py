#!/usr/bin/env python3
"""
Test integrated RSS agents in orchestrator
"""

import asyncio
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator

async def test_integrated_rss_agents():
    print("🧪 Testing Integrated RSS Agents")
    print("=" * 50)
    
    orchestrator = StreamlinedSearchOrchestrator()
    
    # Test with RSS agents only
    rss_agents = ["eldiario", "europapress"]
    test_query = "España"
    
    print(f"🔍 Testing query: '{test_query}' with RSS agents: {rss_agents}")
    print("-" * 60)
    
    try:
        results = await orchestrator.search_all(
            query=test_query,
            days_back=7,
            active_agents=rss_agents
        )
        
        print("✅ Search completed successfully")
        print(f"📊 Results summary:")
        
        total_articles = 0
        for agent_name, agent_results in results.items():
            if "articles" in agent_results:
                article_count = len(agent_results["articles"])
                total_articles += article_count
                print(f"  {agent_name}: {article_count} articles")
                
                if article_count > 0:
                    print(f"    Sample: {agent_results['articles'][0]['title'][:80]}...")
            else:
                print(f"  {agent_name}: No articles (error or empty)")
        
        print(f"\n📈 Total articles found: {total_articles}")
        
        # Test individual agent performance
        print(f"\n🔍 Testing individual agents:")
        for agent_name in rss_agents:
            print(f"\n  Testing {agent_name}:")
            try:
                agent_results = await orchestrator.agents[agent_name].search(
                    query=test_query,
                    days_back=7
                )
                article_count = len(agent_results.get("articles", []))
                print(f"    Articles: {article_count}")
                if article_count > 0:
                    print(f"    Sample: {agent_results['articles'][0]['title'][:60]}...")
            except Exception as e:
                print(f"    Error: {e}")
        
    except Exception as e:
        print(f"❌ Error testing integrated RSS agents: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Integrated RSS agents test completed")

if __name__ == "__main__":
    asyncio.run(test_integrated_rss_agents()) 