#!/usr/bin/env python3
"""
Test Hybrid Vector Implementation
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.vector_performance_optimizer import VectorPerformanceOptimizer
from app.agents.analysis.cloud_embedder import CloudEmbeddingAgent
from app.agents.analysis.embedder import BOEEmbeddingAgent

async def test_hybrid_vector_implementation():
    """Test the hybrid vector implementation"""
    
    print("🧪 Testing Hybrid Vector Implementation")
    print("=" * 50)
    
    # Test 1: Cloud Embedding Agent
    print("\n1️⃣ Testing Cloud Embedding Agent...")
    try:
        cloud_agent = CloudEmbeddingAgent()
        print(f"   ✅ Cloud agent initialized")
        print(f"   📊 Vector service available: {cloud_agent.vector_service_available}")
        print(f"   📊 Embedder service available: {cloud_agent.embedder_service_available}")
        
        # Test semantic search
        test_query = "concurso de acreedores"
        results = cloud_agent.semantic_search(test_query, k=3)
        print(f"   🔍 Semantic search results: {len(results)} found")
        
        for i, result in enumerate(results[:2]):
            print(f"      Result {i+1}: {result.get('metadata', {}).get('titulo', 'No title')}")
            print(f"         Score: {result.get('score', 0):.3f}")
            print(f"         Source: {result.get('metadata', {}).get('source', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Cloud agent test failed: {e}")
    
    # Test 2: Local Embedding Agent (fallback)
    print("\n2️⃣ Testing Local Embedding Agent...")
    try:
        local_agent = BOEEmbeddingAgent()
        print(f"   ✅ Local agent initialized")
        
        # Test semantic search
        test_query = "banco santander"
        results = local_agent.semantic_search(test_query, k=3)
        print(f"   🔍 Local semantic search results: {len(results)} found")
        
        for i, result in enumerate(results[:2]):
            print(f"      Result {i+1}: {result.get('metadata', {}).get('titulo', 'No title')}")
            print(f"         Score: {result.get('score', 0):.3f}")
            print(f"         Source: {result.get('metadata', {}).get('source', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Local agent test failed: {e}")
    
    # Test 3: Vector Performance Optimizer
    print("\n3️⃣ Testing Vector Performance Optimizer...")
    try:
        optimizer = VectorPerformanceOptimizer()
        print(f"   ✅ Vector performance optimizer initialized")
        
        # Test optimized semantic search
        test_query = "repsol"
        search_results = await optimizer.optimized_semantic_search(
            query=test_query,
            k=5,
            use_cache=True
        )
        
        print(f"   🔍 Optimized search results: {len(search_results['results'])} found")
        print(f"   📊 Source: {search_results['source']}")
        print(f"   ⏱️ Response time: {search_results['performance_metrics']['response_time_ms']:.2f}ms")
        
        # Show performance metrics
        metrics = optimizer.get_performance_metrics()
        print(f"   📈 Performance metrics:")
        print(f"      Total searches: {metrics['total_searches']}")
        print(f"      Cache hit rate: {metrics['cache_hit_rate_percent']}%")
        print(f"      Average vector time: {metrics['average_vector_generation_time_ms']:.2f}ms")
        
    except Exception as e:
        print(f"   ❌ Vector optimizer test failed: {e}")
    
    # Test 4: Vector Storage Optimization
    print("\n4️⃣ Testing Vector Storage Optimization...")
    try:
        optimizer = VectorPerformanceOptimizer()
        stats = await optimizer.optimize_vector_storage()
        print(f"   ✅ Vector storage optimization complete")
        print(f"   📊 Stats: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        print(f"   ❌ Vector storage optimization failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Hybrid Vector Implementation Test Complete")

async def test_api_endpoints():
    """Test the new API endpoints"""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    import httpx
    
    base_url = "http://localhost:8000"
    
    # Test semantic search endpoint
    print("\n1️⃣ Testing /api/v1/search/semantic-search...")
    try:
        async with httpx.AsyncClient() as client:
            # First login to get token
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
                
                # Test semantic search
                search_response = await client.post(
                    f"{base_url}/api/v1/search/semantic-search",
                    headers=headers,
                    json={
                        "company_name": "Banco Santander",
                        "limit": 5
                    }
                )
                
                if search_response.status_code == 200:
                    result = search_response.json()
                    print(f"   ✅ Semantic search successful")
                    print(f"   📊 Results: {len(result['search_results'])} found")
                    print(f"   🔧 Source: {result['source']}")
                    print(f"   ⏱️ Response time: {result['performance_metrics']['response_time_ms']:.2f}ms")
                else:
                    print(f"   ❌ Semantic search failed: {search_response.status_code}")
                    print(f"   📄 Response: {search_response.text}")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    # Test vector stats endpoint
    print("\n2️⃣ Testing /api/v1/search/vector-stats...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/v1/search/vector-stats",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Vector stats retrieved")
                print(f"   📊 Stats: {json.dumps(result['vector_performance'], indent=2)}")
            else:
                print(f"   ❌ Vector stats failed: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Vector stats test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Hybrid Vector Implementation Tests")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test core functionality
    await test_hybrid_vector_implementation()
    
    # Test API endpoints (if backend is running)
    await test_api_endpoints()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 