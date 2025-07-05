#!/usr/bin/env python3
"""
Test script for search caching functionality
"""

import asyncio
import json
import time
from app.services.search_cache_service import search_cache_service

async def test_search_caching():
    """Test the search caching functionality"""
    
    print("🧪 Testing Search Caching Functionality")
    print("=" * 50)
    
    # Test parameters
    company_name = "Telefónica"
    active_agents = ["boe", "newsapi"]
    
    try:
        print(f"\n1️⃣ Testing fresh search for '{company_name}'...")
        start_time = time.time()
        
        # First search - should be fresh
        result1 = await search_cache_service.get_search_results(
            company_name=company_name,
            days_back=7,
            active_agents=active_agents,
            cache_age_hours=24,
            force_refresh=False
        )
        
        search_time1 = time.time() - start_time
        print(f"✅ First search completed in {search_time1:.2f}s")
        print(f"   Search method: {result1['search_method']}")
        print(f"   Total events: {result1.get('cache_info', {}).get('total_events', 0)}")
        print(f"   Sources: {result1.get('cache_info', {}).get('sources', [])}")
        
        print(f"\n2️⃣ Testing cached search for '{company_name}'...")
        start_time = time.time()
        
        # Second search - should use cache
        result2 = await search_cache_service.get_search_results(
            company_name=company_name,
            days_back=7,
            active_agents=active_agents,
            cache_age_hours=24,
            force_refresh=False
        )
        
        search_time2 = time.time() - start_time
        print(f"✅ Second search completed in {search_time2:.2f}s")
        print(f"   Search method: {result2['search_method']}")
        print(f"   Total events: {result2.get('cache_info', {}).get('total_events', 0)}")
        print(f"   Sources: {result2.get('cache_info', {}).get('sources', [])}")
        
        print(f"\n3️⃣ Testing force refresh for '{company_name}'...")
        start_time = time.time()
        
        # Third search - force refresh
        result3 = await search_cache_service.get_search_results(
            company_name=company_name,
            days_back=7,
            active_agents=active_agents,
            cache_age_hours=24,
            force_refresh=True
        )
        
        search_time3 = time.time() - start_time
        print(f"✅ Force refresh completed in {search_time3:.2f}s")
        print(f"   Search method: {result3['search_method']}")
        print(f"   Total events: {result3.get('cache_info', {}).get('total_events', 0)}")
        print(f"   Sources: {result3.get('cache_info', {}).get('sources', [])}")
        
        # Performance comparison
        print(f"\n📊 Performance Comparison:")
        print(f"   Fresh search: {search_time1:.2f}s")
        print(f"   Cached search: {search_time2:.2f}s")
        print(f"   Force refresh: {search_time3:.2f}s")
        
        if search_time2 < search_time1:
            print(f"   ✅ Caching improved performance by {((search_time1 - search_time2) / search_time1 * 100):.1f}%")
        else:
            print(f"   ⚠️  Caching did not improve performance")
        
        # Test cache key generation
        print(f"\n4️⃣ Testing cache key generation...")
        key1 = search_cache_service._generate_search_key(
            company_name, None, None, 7, active_agents
        )
        key2 = search_cache_service._generate_search_key(
            company_name, None, None, 7, active_agents
        )
        
        if key1 == key2:
            print(f"   ✅ Cache keys are consistent: {key1[:16]}...")
        else:
            print(f"   ❌ Cache keys are inconsistent")
        
        print(f"\n🎉 Search caching test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_cache_service_methods():
    """Test individual cache service methods"""
    
    print(f"\n🔧 Testing Cache Service Methods")
    print("=" * 30)
    
    try:
        company_name = "Repsol"
        active_agents = ["boe"]
        
        # Test cache key generation
        key = search_cache_service._generate_search_key(
            company_name, "2024-01-01", "2024-01-31", 30, active_agents
        )
        print(f"✅ Cache key generated: {key[:16]}...")
        
        # Test cached results retrieval
        cached_results = await search_cache_service.get_cached_results(
            company_name=company_name,
            days_back=7,
            active_agents=active_agents,
            cache_age_hours=24
        )
        
        if cached_results:
            print(f"✅ Found cached results: {cached_results['total_events']} events")
        else:
            print(f"ℹ️  No cached results found (expected for new company)")
        
        print(f"✅ Cache service methods test completed!")
        
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Search Caching Tests...")
    
    # Run tests
    asyncio.run(test_search_caching())
    asyncio.run(test_cache_service_methods())
    
    print("\n✨ All tests completed!") 