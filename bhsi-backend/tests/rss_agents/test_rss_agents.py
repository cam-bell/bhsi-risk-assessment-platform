#!/usr/bin/env python3
"""
Test script for RSS agents - verify they work correctly
"""

import asyncio
import logging
from app.agents.search.streamlined_elpais_agent import StreamlinedElPaisAgent
from app.agents.search.streamlined_expansion_agent import StreamlinedExpansionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_elpais_agent():
    """Test El País RSS agent"""
    print("\n" + "="*50)
    print("TESTING EL PAÍS RSS AGENT")
    print("="*50)
    
    agent = StreamlinedElPaisAgent()
    
    # Test with a common Spanish company
    test_query = "Banco Santander"
    
    try:
        result = await agent.search(query=test_query)
        
        print(f"✅ El País Search Results:")
        print(f"   Query: {test_query}")
        print(f"   Total Results: {result['search_summary']['total_results']}")
        print(f"   Feeds Searched: {result['search_summary']['feeds_searched']}")
        
        if result['search_summary']['errors']:
            print(f"   Errors: {result['search_summary']['errors']}")
        
        # Show first few results
        articles = result.get('articles', [])
        if articles:
            print(f"\n📰 Sample Articles:")
            for i, article in enumerate(articles[:3]):
                print(f"   {i+1}. {article['title'][:60]}...")
                print(f"      Category: {article['category']}")
                print(f"      Date: {article['publishedAt']}")
                print(f"      URL: {article['url']}")
                print()
        else:
            print("   No matching articles found")
            
    except Exception as e:
        print(f"❌ El País test failed: {e}")


async def test_expansion_agent():
    """Test Expansión RSS agent"""
    print("\n" + "="*50)
    print("TESTING EXPANSIÓN RSS AGENT")
    print("="*50)
    
    agent = StreamlinedExpansionAgent()
    
    # Test with a common Spanish company
    test_query = "Banco Santander"
    
    try:
        result = await agent.search(query=test_query)
        
        print(f"✅ Expansión Search Results:")
        print(f"   Query: {test_query}")
        print(f"   Total Results: {result['search_summary']['total_results']}")
        print(f"   Feeds Searched: {result['search_summary']['feeds_searched']}")
        
        if result['search_summary']['errors']:
            print(f"   Errors: {result['search_summary']['errors']}")
        
        # Show first few results
        articles = result.get('articles', [])
        if articles:
            print(f"\n📰 Sample Articles:")
            for i, article in enumerate(articles[:3]):
                print(f"   {i+1}. {article['title'][:60]}...")
                print(f"      Category: {article['category']}")
                print(f"      Date: {article['publishedAt']}")
                print(f"      URL: {article['url']}")
                print()
        else:
            print("   No matching articles found")
            
    except Exception as e:
        print(f"❌ Expansión test failed: {e}")


async def test_generic_query():
    """Test with a generic business term"""
    print("\n" + "="*50)
    print("TESTING GENERIC BUSINESS QUERY")
    print("="*50)
    
    elpais_agent = StreamlinedElPaisAgent()
    expansion_agent = StreamlinedExpansionAgent()
    
    test_query = "economía"
    
    try:
        # Test El País
        elpais_result = await elpais_agent.search(query=test_query)
        print(f"El País results for '{test_query}': {elpais_result['search_summary']['total_results']}")
        
        # Test Expansión
        expansion_result = await expansion_agent.search(query=test_query)
        print(f"Expansión results for '{test_query}': {expansion_result['search_summary']['total_results']}")
        
        total_results = (elpais_result['search_summary']['total_results'] + 
                        expansion_result['search_summary']['total_results'])
        print(f"Total combined results: {total_results}")
        
    except Exception as e:
        print(f"❌ Generic query test failed: {e}")


async def main():
    """Run all tests"""
    print("🚀 TESTING RSS AGENTS")
    print("This will verify that the new RSS agents work correctly")
    
    await test_elpais_agent()
    await test_expansion_agent()
    await test_generic_query()
    
    print("\n" + "="*50)
    print("TESTING COMPLETE")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main()) 