#!/usr/bin/env python3
"""
Test Real Company Pipeline
Comprehensive test of the streamlined search pipeline with a real company
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

async def test_real_company_pipeline():
    """Test the entire pipeline with a real company"""
    
    print("🚀 Testing Real Company Pipeline")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
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
                print(f"   📄 Response: {login_response.text}")
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authentication successful")
            
            # Step 2: Test with a real Spanish company - Banco Santander
            print("\n2️⃣ Testing with Banco Santander...")
            company_name = "Banco Santander"
            
            search_response = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": company_name,
                    "days_back": 30,
                    "include_boe": True,
                    "include_news": True,
                    "include_rss": True,
                    "force_refresh": False,
                    "cache_age_hours": 24
                }
            )
            
            if search_response.status_code == 200:
                result = search_response.json()
                print(f"   ✅ Search successful for {company_name}")
                print(f"   📊 Total results: {len(result.get('results', []))}")
                print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                print(f"   🔧 Search method: {result.get('cache_info', {}).get('search_method', 'N/A')}")
                
                # Show risk distribution
                risk_summary = result.get('risk_summary', {})
                print(f"   🎨 Risk distribution:")
                print(f"      Red (High risk): {risk_summary.get('high_risk_articles', 0)}")
                print(f"      Orange (Medium risk): {risk_summary.get('medium_risk_articles', 0)}")
                print(f"      Green (Low risk): {risk_summary.get('low_risk_articles', 0)}")
                
                # Show source breakdown
                metadata = result.get('metadata', {})
                print(f"   📰 Source breakdown:")
                print(f"      BOE results: {metadata.get('boe_results', 0)}")
                print(f"      News results: {metadata.get('news_results', 0)}")
                print(f"      RSS results: {metadata.get('rss_results', 0)}")
                
                # Show top 3 results
                results = result.get('results', [])
                if results:
                    print(f"   📄 Top 3 results:")
                    for i, res in enumerate(results[:3]):
                        print(f"      {i+1}. {res.get('source', 'Unknown')} - {res.get('title', 'No title')[:60]}...")
                        print(f"         Risk: {res.get('risk_level', 'Unknown')} ({res.get('risk_color', 'gray')})")
                        print(f"         Date: {res.get('date', 'Unknown')}")
                
            else:
                print(f"   ❌ Search failed: {search_response.status_code}")
                print(f"   📄 Response: {search_response.text}")
            
            # Step 3: Test semantic search for the same company
            print(f"\n3️⃣ Testing Semantic Search for {company_name}...")
            semantic_response = await client.post(
                f"{base_url}/api/v1/streamlined/semantic-search",
                headers=headers,
                json={
                    "query": company_name,
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
                
            else:
                print(f"   ❌ Semantic search failed: {semantic_response.status_code}")
                print(f"   📄 Response: {semantic_response.text}")
            
            # Step 4: Test with another company - Repsol
            print(f"\n4️⃣ Testing with Repsol...")
            company_name_2 = "Repsol"
            
            search_response_2 = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": company_name_2,
                    "days_back": 30,
                    "include_boe": True,
                    "include_news": True,
                    "include_rss": False,  # Disable for faster test
                    "force_refresh": False,
                    "cache_age_hours": 24
                }
            )
            
            if search_response_2.status_code == 200:
                result = search_response_2.json()
                print(f"   ✅ Search successful for {company_name_2}")
                print(f"   📊 Total results: {len(result.get('results', []))}")
                print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                
                # Show risk distribution
                risk_summary = result.get('risk_summary', {})
                print(f"   🎨 Risk distribution:")
                print(f"      Red (High risk): {risk_summary.get('high_risk_articles', 0)}")
                print(f"      Orange (Medium risk): {risk_summary.get('medium_risk_articles', 0)}")
                print(f"      Green (Low risk): {risk_summary.get('low_risk_articles', 0)}")
                
            else:
                print(f"   ❌ Search failed for {company_name_2}: {search_response_2.status_code}")
            
            # Step 5: Test vector stats
            print(f"\n5️⃣ Testing Vector Stats...")
            stats_response = await client.get(
                f"{base_url}/api/v1/streamlined/vector-stats",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                result = stats_response.json()
                print(f"   ✅ Vector stats retrieved")
                stats = result.get('hybrid_vector_storage', {})
                print(f"   📊 Vector Storage Status:")
                print(f"      BigQuery available: {stats.get('bigquery_available', False)}")
                print(f"      ChromaDB available: {stats.get('local_service_available', False)}")
                print(f"      Cloud service available: {stats.get('cloud_service_available', False)}")
                print(f"      Total searches: {stats.get('bigquery_searches', 0) + stats.get('chromadb_searches', 0) + stats.get('cloud_searches', 0)}")
                
            else:
                print(f"   ❌ Vector stats failed: {stats_response.status_code}")
            
            # Step 6: Test cache stats
            print(f"\n6️⃣ Testing Cache Stats...")
            cache_response = await client.get(
                f"{base_url}/api/v1/streamlined/search/cache-stats",
                headers=headers
            )
            
            if cache_response.status_code == 200:
                result = cache_response.json()
                print(f"   ✅ Cache stats retrieved")
                print(f"   💾 Cache system: {result.get('cache_system', 'Unknown')}")
                cache_config = result.get('cache_configuration', {})
                print(f"   ⚙️ Cache configuration:")
                print(f"      Default age: {cache_config.get('default_cache_age_hours', 0)} hours")
                print(f"      Force refresh: {cache_config.get('force_refresh_option', False)}")
                print(f"      Sources: {', '.join(cache_config.get('cache_sources', []))}")
                
            else:
                print(f"   ❌ Cache stats failed: {cache_response.status_code}")
            
            # Step 7: Performance comparison
            print(f"\n7️⃣ Performance Analysis...")
            companies = ["Banco Santander", "Repsol", "Telefonica"]
            
            print(f"   📊 Testing {len(companies)} companies for performance comparison")
            performance_data = []
            
            for company in companies:
                print(f"   🔍 Testing {company}...")
                start_time = time.time()
                
                perf_response = await client.post(
                    f"{base_url}/api/v1/streamlined/search",
                    headers=headers,
                    json={
                        "company_name": company,
                        "days_back": 7,  # Shorter period for faster test
                        "include_boe": True,
                        "include_news": True,
                        "include_rss": False,
                        "force_refresh": False
                    }
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if perf_response.status_code == 200:
                    result = perf_response.json()
                    performance_data.append({
                        "company": company,
                        "response_time": response_time,
                        "results_count": len(result.get('results', [])),
                        "search_method": result.get('cache_info', {}).get('search_method', 'unknown'),
                        "total_time": result.get('performance', {}).get('total_time_seconds', 'N/A')
                    })
                    print(f"      ✅ {response_time:.2f}s - {len(result.get('results', []))} results")
                else:
                    print(f"      ❌ Failed: {perf_response.status_code}")
            
            # Show performance summary
            if performance_data:
                print(f"   📈 Performance Summary:")
                avg_time = sum(p['response_time'] for p in performance_data) / len(performance_data)
                total_results = sum(p['results_count'] for p in performance_data)
                print(f"      Average response time: {avg_time:.2f}s")
                print(f"      Total results across companies: {total_results}")
                print(f"      Cache hits: {sum(1 for p in performance_data if 'cached' in p['search_method'])}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the real company pipeline test"""
    print("🚀 Starting Real Company Pipeline Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_real_company_pipeline()
    
    print(f"\n🎉 Real Company Pipeline Test Complete!")
    print(f"✅ Pipeline tested with:")
    print(f"   🏢 Real Spanish companies")
    print(f"   🔍 Traditional search")
    print(f"   🧠 Semantic search")
    print(f"   📊 Vector statistics")
    print(f"   💾 Cache performance")
    print(f"   ⚡ Performance analysis")

if __name__ == "__main__":
    asyncio.run(main()) 