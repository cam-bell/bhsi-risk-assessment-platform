#!/usr/bin/env python3
"""
Real Company Vector Search Test
Tests both traditional search and semantic vector search with real company data
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.vector_performance_optimizer import VectorPerformanceOptimizer
from app.agents.analysis.cloud_embedder import CloudEmbeddingAgent
from app.agents.analysis.embedder import BOEEmbeddingAgent
from app.agents.search.streamlined_orchestrator import get_search_orchestrator

async def test_real_company_search():
    """Test search with a real company"""
    
    print("🏢 Testing Real Company Search")
    print("=" * 50)
    
    # Test company
    company_name = "Banco Santander"
    print(f"🎯 Testing company: {company_name}")
    
    # Test 1: Traditional Search (keyword-based)
    print(f"\n1️⃣ Traditional Search (Keyword-based)")
    print("-" * 40)
    
    try:
        orchestrator = get_search_orchestrator()
        
        start_time = time.time()
        traditional_results = await orchestrator.search_all(
            query=company_name,
            days_back=30,
            active_agents=["boe", "newsapi"]
        )
        traditional_time = time.time() - start_time
        
        print(f"   ⏱️ Traditional search time: {traditional_time:.2f}s")
        
        # Count results
        total_traditional = 0
        for source, data in traditional_results.items():
            if isinstance(data, dict):
                if 'articles' in data:
                    count = len(data['articles'])
                    total_traditional += count
                    print(f"   📰 {source}: {count} articles")
                elif 'results' in data:
                    count = len(data['results'])
                    total_traditional += count
                    print(f"   📄 {source}: {count} results")
        
        print(f"   📊 Total traditional results: {total_traditional}")
        
    except Exception as e:
        print(f"   ❌ Traditional search failed: {e}")
    
    # Test 2: Semantic Vector Search
    print(f"\n2️⃣ Semantic Vector Search")
    print("-" * 40)
    
    try:
        vector_optimizer = VectorPerformanceOptimizer()
        
        start_time = time.time()
        semantic_results = await vector_optimizer.optimized_semantic_search(
            query=company_name,
            k=10,
            use_cache=True
        )
        semantic_time = time.time() - start_time
        
        print(f"   ⏱️ Semantic search time: {semantic_time:.2f}s")
        print(f"   📊 Source: {semantic_results['source']}")
        print(f"   🔍 Results found: {len(semantic_results['results'])}")
        
        # Show top results
        for i, result in enumerate(semantic_results['results'][:3]):
            print(f"   📄 Result {i+1}:")
            print(f"      Title: {result.get('metadata', {}).get('titulo', 'No title')}")
            print(f"      Score: {result.get('score', 0):.3f}")
            print(f"      Source: {result.get('metadata', {}).get('source', 'Unknown')}")
            print(f"      Text: {result.get('document', '')[:100]}...")
        
        # Show performance metrics
        perf_metrics = semantic_results['performance_metrics']
        print(f"   📈 Performance:")
        print(f"      Response time: {perf_metrics['response_time_ms']:.2f}ms")
        print(f"      Cache hit: {perf_metrics.get('cache_hit', False)}")
        
    except Exception as e:
        print(f"   ❌ Semantic search failed: {e}")
    
    # Test 3: Cloud vs Local Vector Search
    print(f"\n3️⃣ Cloud vs Local Vector Search Comparison")
    print("-" * 40)
    
    try:
        # Test cloud vector search
        cloud_agent = CloudEmbeddingAgent()
        if cloud_agent.vector_service_available:
            start_time = time.time()
            cloud_results = cloud_agent.semantic_search(company_name, k=5)
            cloud_time = time.time() - start_time
            
            print(f"   ☁️ Cloud vector search:")
            print(f"      Time: {cloud_time:.2f}s")
            print(f"      Results: {len(cloud_results)}")
            print(f"      Available: {cloud_agent.vector_service_available}")
        else:
            print(f"   ❌ Cloud vector service unavailable")
        
        # Test local vector search
        local_agent = BOEEmbeddingAgent()
        start_time = time.time()
        local_results = local_agent.semantic_search(company_name, k=5)
        local_time = time.time() - start_time
        
        print(f"   🏠 Local vector search:")
        print(f"      Time: {local_time:.2f}s")
        print(f"      Results: {len(local_results)}")
        
    except Exception as e:
        print(f"   ❌ Vector comparison failed: {e}")
    
    # Test 4: Different Search Queries
    print(f"\n4️⃣ Testing Different Search Queries")
    print("-" * 40)
    
    test_queries = [
        "Banco Santander",
        "Santander bank",
        "concurso de acreedores",
        "financial risk",
        "bankruptcy proceedings"
    ]
    
    for query in test_queries:
        try:
            print(f"   🔍 Query: '{query}'")
            
            # Semantic search
            semantic_results = await vector_optimizer.optimized_semantic_search(
                query=query,
                k=3,
                use_cache=True
            )
            
            print(f"      Results: {len(semantic_results['results'])}")
            print(f"      Time: {semantic_results['performance_metrics']['response_time_ms']:.2f}ms")
            
            # Show top result
            if semantic_results['results']:
                top_result = semantic_results['results'][0]
                print(f"      Top result: {top_result.get('metadata', {}).get('titulo', 'No title')[:50]}...")
                print(f"      Score: {top_result.get('score', 0):.3f}")
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Real Company Search Test Complete")

async def test_api_endpoints_with_real_company():
    """Test API endpoints with real company"""
    
    print("\n🌐 Testing API Endpoints with Real Company")
    print("=" * 50)
    
    import httpx
    
    base_url = "http://localhost:8000"
    company_name = "Repsol"
    
    print(f"🎯 Testing company: {company_name}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Traditional search endpoint
            print(f"\n1️⃣ Testing traditional search endpoint...")
            
            # Login first
            login_response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "email": "admin@bhsi.com",
                    "password": "admin123"
                }
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test traditional search
                search_response = await client.post(
                    f"{base_url}/api/v1/streamlined/search",
                    headers=headers,
                    json={
                        "company_name": company_name,
                        "days_back": 30
                    }
                )
                
                if search_response.status_code == 200:
                    result = search_response.json()
                    print(f"   ✅ Traditional search successful")
                    print(f"   📊 Results: {len(result.get('results', []))}")
                    print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                else:
                    print(f"   ❌ Traditional search failed: {search_response.status_code}")
                    print(f"   📄 Response: {search_response.text}")
            
            # Test 2: Semantic search endpoint
            print(f"\n2️⃣ Testing semantic search endpoint...")
            
            semantic_response = await client.post(
                f"{base_url}/api/v1/search/semantic-search",
                headers=headers,
                json={
                    "company_name": company_name,
                    "limit": 5
                }
            )
            
            if semantic_response.status_code == 200:
                result = semantic_response.json()
                print(f"   ✅ Semantic search successful")
                print(f"   📊 Results: {len(result.get('search_results', []))}")
                print(f"   🔧 Source: {result.get('source', 'Unknown')}")
                print(f"   ⏱️ Response time: {result.get('performance_metrics', {}).get('response_time_ms', 0):.2f}ms")
                
                # Show top results
                for i, res in enumerate(result.get('search_results', [])[:2]):
                    print(f"   📄 Result {i+1}: {res.get('metadata', {}).get('titulo', 'No title')[:50]}...")
                    print(f"      Score: {res.get('score', 0):.3f}")
            else:
                print(f"   ❌ Semantic search failed: {semantic_response.status_code}")
                print(f"   📄 Response: {semantic_response.text}")
            
            # Test 3: Vector stats endpoint
            print(f"\n3️⃣ Testing vector stats endpoint...")
            
            stats_response = await client.get(
                f"{base_url}/api/v1/search/vector-stats",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                result = stats_response.json()
                print(f"   ✅ Vector stats retrieved")
                print(f"   📊 Stats: {json.dumps(result.get('vector_performance', {}), indent=2)}")
            else:
                print(f"   ❌ Vector stats failed: {stats_response.status_code}")
                
    except Exception as e:
        print(f"   ❌ API test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Real Company Vector Search Tests")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test core functionality with real company
    await test_real_company_search()
    
    # Test API endpoints (if backend is running)
    await test_api_endpoints_with_real_company()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 