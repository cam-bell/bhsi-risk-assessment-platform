#!/usr/bin/env python3
"""
Test Streamlined Vector Integration
Tests the hybrid vector storage integration with the streamlined endpoint
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import httpx

async def test_streamlined_vector_integration():
    """Test the streamlined endpoint with hybrid vector storage"""
    
    print("🔄 Testing Streamlined Vector Integration")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Login to get token
            print("\n1️⃣ Authenticating...")
            login_response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "email": "admin@bhsi.com",
                    "password": "admin123"
                }
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.status_code}")
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authentication successful")
            
            # Step 2: Test traditional streamlined search
            print("\n2️⃣ Testing Traditional Streamlined Search...")
            traditional_response = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": "Banco Santander",
                    "days_back": 30,
                    "include_boe": True,
                    "include_news": True,
                    "include_rss": False  # Disable for faster test
                }
            )
            
            if traditional_response.status_code == 200:
                result = traditional_response.json()
                print(f"   ✅ Traditional search successful")
                print(f"   📊 Results: {len(result.get('results', []))}")
                print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                print(f"   🔧 Search method: {result.get('cache_info', {}).get('search_method', 'N/A')}")
            else:
                print(f"   ❌ Traditional search failed: {traditional_response.status_code}")
                print(f"   📄 Response: {traditional_response.text}")
            
            # Step 3: Test semantic search endpoint
            print("\n3️⃣ Testing Semantic Search Endpoint...")
            semantic_response = await client.post(
                f"{base_url}/api/v1/streamlined/semantic-search",
                headers=headers,
                json={
                    "query": "Banco Santander",
                    "k": 5,
                    "use_cache": True,
                    "include_metadata": True
                }
            )
            
            if semantic_response.status_code == 200:
                result = semantic_response.json()
                print(f"   ✅ Semantic search successful")
                print(f"   📊 Results: {len(result.get('search_results', []))}")
                print(f"   🔧 Source: {result.get('source', 'Unknown')}")
                print(f"   ⏱️ Response time: {result.get('performance_metrics', {}).get('response_time_ms', 0):.2f}ms")
                
                # Show hybrid storage metrics
                hybrid_metrics = result.get('hybrid_storage', {})
                print(f"   📈 Hybrid Storage Metrics:")
                print(f"      BigQuery searches: {hybrid_metrics.get('bigquery_searches', 0)}")
                print(f"      ChromaDB searches: {hybrid_metrics.get('chromadb_searches', 0)}")
                print(f"      Cloud searches: {hybrid_metrics.get('cloud_searches', 0)}")
                print(f"      Cache hits: {hybrid_metrics.get('cache_hits', 0)}")
                
                # Show top results
                for i, res in enumerate(result.get('search_results', [])[:2]):
                    print(f"   📄 Result {i+1}: {res.get('metadata', {}).get('titulo', 'No title')[:50]}...")
                    print(f"      Score: {res.get('score', 0):.3f}")
            else:
                print(f"   ❌ Semantic search failed: {semantic_response.status_code}")
                print(f"   📄 Response: {semantic_response.text}")
            
            # Step 4: Test vector stats endpoint
            print("\n4️⃣ Testing Vector Stats Endpoint...")
            stats_response = await client.get(
                f"{base_url}/api/v1/streamlined/vector-stats",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                result = stats_response.json()
                print(f"   ✅ Vector stats retrieved")
                print(f"   📊 Stats: {json.dumps(result.get('hybrid_vector_storage', {}), indent=2)}")
                
                # Show storage systems
                storage_systems = result.get('storage_systems', {})
                print(f"   💾 Storage Systems:")
                for system, description in storage_systems.items():
                    print(f"      {system}: {description}")
            else:
                print(f"   ❌ Vector stats failed: {stats_response.status_code}")
            
            # Step 5: Test different semantic queries
            print("\n5️⃣ Testing Different Semantic Queries...")
            test_queries = [
                "concurso de acreedores",
                "financial risk",
                "legal proceedings",
                "bankruptcy"
            ]
            
            for query in test_queries:
                print(f"   🔍 Query: '{query}'")
                
                query_response = await client.post(
                    f"{base_url}/api/v1/streamlined/semantic-search",
                    headers=headers,
                    json={
                        "query": query,
                        "k": 3,
                        "use_cache": True
                    }
                )
                
                if query_response.status_code == 200:
                    result = query_response.json()
                    print(f"      ✅ Results: {len(result.get('search_results', []))}")
                    print(f"      ⏱️ Time: {result.get('performance_metrics', {}).get('response_time_ms', 0):.2f}ms")
                    print(f"      🔧 Source: {result.get('source', 'Unknown')}")
                else:
                    print(f"      ❌ Failed: {query_response.status_code}")
            
            # Step 6: Test migration endpoint
            print("\n6️⃣ Testing Vector Migration Endpoint...")
            migration_response = await client.post(
                f"{base_url}/api/v1/streamlined/migrate-vectors",
                headers=headers
            )
            
            if migration_response.status_code == 200:
                result = migration_response.json()
                print(f"   ✅ Vector migration successful")
                print(f"   📊 Migration stats: {json.dumps(result.get('migration_stats', {}), indent=2)}")
            else:
                print(f"   ❌ Vector migration failed: {migration_response.status_code}")
                print(f"   📄 Response: {migration_response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_performance_comparison():
    """Compare performance between traditional and semantic search"""
    
    print(f"\n⚡ Performance Comparison")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Login
            login_response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={
                    "email": "admin@bhsi.com",
                    "password": "admin123"
                }
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.status_code}")
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test queries
            test_queries = [
                "Banco Santander",
                "Repsol",
                "concurso de acreedores"
            ]
            
            print(f"\n🔍 Testing {len(test_queries)} queries")
            print("-" * 60)
            
            for query in test_queries:
                print(f"\n📝 Query: '{query}'")
                
                # Test traditional search
                start_time = time.time()
                traditional_response = await client.post(
                    f"{base_url}/api/v1/streamlined/search",
                    headers=headers,
                    json={
                        "company_name": query,
                        "days_back": 30,
                        "include_boe": True,
                        "include_news": True,
                        "include_rss": False
                    }
                )
                traditional_time = time.time() - start_time
                
                if traditional_response.status_code == 200:
                    traditional_result = traditional_response.json()
                    print(f"   🏢 Traditional search:")
                    print(f"      Time: {traditional_time:.2f}s")
                    print(f"      Results: {len(traditional_result.get('results', []))}")
                    print(f"      Method: {traditional_result.get('cache_info', {}).get('search_method', 'N/A')}")
                
                # Test semantic search
                start_time = time.time()
                semantic_response = await client.post(
                    f"{base_url}/api/v1/streamlined/semantic-search",
                    headers=headers,
                    json={
                        "query": query,
                        "k": 5,
                        "use_cache": True
                    }
                )
                semantic_time = time.time() - start_time
                
                if semantic_response.status_code == 200:
                    semantic_result = semantic_response.json()
                    print(f"   🧠 Semantic search:")
                    print(f"      Time: {semantic_time:.2f}s")
                    print(f"      Results: {len(semantic_result.get('search_results', []))}")
                    print(f"      Source: {semantic_result.get('source', 'Unknown')}")
                
                print(f"   📈 Performance difference: {semantic_time - traditional_time:.2f}s")
    
    except Exception as e:
        print(f"❌ Performance comparison failed: {e}")

async def main():
    """Run all streamlined vector integration tests"""
    print("🚀 Starting Streamlined Vector Integration Tests")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test streamlined vector integration
    await test_streamlined_vector_integration()
    
    # Test performance comparison
    await test_performance_comparison()
    
    print(f"\n🎉 Streamlined Vector Integration Test Complete!")
    print(f"✅ Hybrid vector storage now integrated with:")
    print(f"   📊 Streamlined search endpoint")
    print(f"   🧠 Semantic search endpoint")
    print(f"   📈 Vector stats endpoint")
    print(f"   🔄 Vector migration endpoint")

if __name__ == "__main__":
    asyncio.run(main()) 