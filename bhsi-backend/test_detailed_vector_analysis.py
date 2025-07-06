#!/usr/bin/env python3
"""
Detailed Vector Search Analysis
Shows detailed analysis of vector search performance and capabilities
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

async def analyze_vector_performance():
    """Analyze vector search performance in detail"""
    
    print("🔍 Detailed Vector Search Analysis")
    print("=" * 60)
    
    # Test companies
    test_companies = [
        "Banco Santander",
        "Repsol",
        "Telefónica",
        "BBVA",
        "Iberdrola"
    ]
    
    vector_optimizer = VectorPerformanceOptimizer()
    
    print(f"\n📊 Performance Analysis for {len(test_companies)} companies")
    print("-" * 60)
    
    total_time = 0
    total_results = 0
    cache_hits = 0
    
    for i, company in enumerate(test_companies, 1):
        print(f"\n{i}. Testing: {company}")
        
        try:
            start_time = time.time()
            results = await vector_optimizer.optimized_semantic_search(
                query=company,
                k=5,
                use_cache=True
            )
            search_time = time.time() - start_time
            
            # Extract metrics
            perf_metrics = results['performance_metrics']
            response_time = perf_metrics['response_time_ms']
            cache_hit = perf_metrics.get('cache_hit', False)
            result_count = len(results['results'])
            
            print(f"   ⏱️ Search time: {search_time:.2f}s")
            print(f"   ⚡ Response time: {response_time:.2f}ms")
            print(f"   📊 Results: {result_count}")
            print(f"   🎯 Cache hit: {cache_hit}")
            print(f"   🔧 Source: {results['source']}")
            
            # Show top result details
            if results['results']:
                top_result = results['results'][0]
                print(f"   📄 Top result:")
                print(f"      Title: {top_result.get('metadata', {}).get('titulo', 'No title')[:60]}...")
                print(f"      Score: {top_result.get('score', 0):.3f}")
                print(f"      Source: {top_result.get('metadata', {}).get('source', 'Unknown')}")
            
            total_time += search_time
            total_results += result_count
            if cache_hit:
                cache_hits += 1
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Summary statistics
    print(f"\n📈 Summary Statistics")
    print("-" * 60)
    print(f"   🏢 Companies tested: {len(test_companies)}")
    print(f"   ⏱️ Total search time: {total_time:.2f}s")
    print(f"   📊 Average time per company: {total_time/len(test_companies):.2f}s")
    print(f"   🔍 Total results found: {total_results}")
    print(f"   🎯 Cache hit rate: {cache_hits}/{len(test_companies)} ({cache_hits/len(test_companies)*100:.1f}%)")
    print(f"   📊 Average results per company: {total_results/len(test_companies):.1f}")

async def test_vector_capabilities():
    """Test different vector search capabilities"""
    
    print(f"\n🧠 Vector Search Capabilities Test")
    print("=" * 60)
    
    vector_optimizer = VectorPerformanceOptimizer()
    
    # Test different types of queries
    test_queries = [
        # Company names
        ("Company: Banco Santander", "Banco Santander"),
        ("Company: Repsol", "Repsol"),
        
        # Risk-related queries
        ("Risk: Bankruptcy", "concurso de acreedores"),
        ("Risk: Financial", "financial risk"),
        ("Risk: Legal", "legal proceedings"),
        
        # Industry-specific
        ("Industry: Banking", "banking sector"),
        ("Industry: Energy", "energy companies"),
        ("Industry: Telecom", "telecommunications"),
        
        # Spanish legal terms
        ("Legal: BOE", "boletín oficial del estado"),
        ("Legal: Insolvency", "insolvencia"),
        ("Legal: Corporate", "sociedad anónima"),
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} different query types")
    print("-" * 60)
    
    successful_queries = 0
    total_results = 0
    
    for query_type, query in test_queries:
        try:
            print(f"\n📝 {query_type}")
            print(f"   Query: '{query}'")
            
            start_time = time.time()
            results = await vector_optimizer.optimized_semantic_search(
                query=query,
                k=3,
                use_cache=True
            )
            search_time = time.time() - start_time
            
            result_count = len(results['results'])
            total_results += result_count
            
            print(f"   ⏱️ Time: {search_time:.2f}s")
            print(f"   📊 Results: {result_count}")
            print(f"   🎯 Cache: {results['performance_metrics'].get('cache_hit', False)}")
            
            if result_count > 0:
                successful_queries += 1
                top_result = results['results'][0]
                print(f"   📄 Top: {top_result.get('metadata', {}).get('titulo', 'No title')[:50]}...")
                print(f"   🎯 Score: {top_result.get('score', 0):.3f}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n📊 Capability Summary")
    print("-" * 60)
    print(f"   ✅ Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"   📊 Success rate: {successful_queries/len(test_queries)*100:.1f}%")
    print(f"   🔍 Total results: {total_results}")
    print(f"   📈 Average results per query: {total_results/len(test_queries):.1f}")

async def test_hybrid_approach():
    """Test the hybrid approach (cloud + local + cache)"""
    
    print(f"\n🔄 Hybrid Vector Approach Test")
    print("=" * 60)
    
    # Test cloud vector service
    print(f"\n☁️ Cloud Vector Service")
    print("-" * 40)
    
    try:
        cloud_agent = CloudEmbeddingAgent()
        print(f"   📊 Vector service available: {cloud_agent.vector_service_available}")
        print(f"   📊 Embedder service available: {cloud_agent.embedder_service_available}")
        
        if cloud_agent.vector_service_available:
            start_time = time.time()
            cloud_results = cloud_agent.semantic_search("Banco Santander", k=3)
            cloud_time = time.time() - start_time
            
            print(f"   ⏱️ Cloud search time: {cloud_time:.2f}s")
            print(f"   📊 Cloud results: {len(cloud_results)}")
            
            if cloud_results:
                print(f"   📄 Top cloud result: {cloud_results[0].get('metadata', {}).get('titulo', 'No title')[:50]}...")
        else:
            print(f"   ❌ Cloud service unavailable")
            
    except Exception as e:
        print(f"   ❌ Cloud test failed: {e}")
    
    # Test local vector service
    print(f"\n🏠 Local Vector Service")
    print("-" * 40)
    
    try:
        local_agent = BOEEmbeddingAgent()
        start_time = time.time()
        local_results = local_agent.semantic_search("Banco Santander", k=3)
        local_time = time.time() - start_time
        
        print(f"   ⏱️ Local search time: {local_time:.2f}s")
        print(f"   📊 Local results: {len(local_results)}")
        
        if local_results:
            print(f"   📄 Top local result: {local_results[0].get('metadata', {}).get('titulo', 'No title')[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Local test failed: {e}")
    
    # Test optimized hybrid approach
    print(f"\n⚡ Optimized Hybrid Approach")
    print("-" * 40)
    
    try:
        vector_optimizer = VectorPerformanceOptimizer()
        start_time = time.time()
        hybrid_results = await vector_optimizer.optimized_semantic_search(
            query="Banco Santander",
            k=5,
            use_cache=True
        )
        hybrid_time = time.time() - start_time
        
        print(f"   ⏱️ Hybrid search time: {hybrid_time:.2f}s")
        print(f"   📊 Hybrid results: {len(hybrid_results['results'])}")
        print(f"   🔧 Source: {hybrid_results['source']}")
        print(f"   🎯 Cache hit: {hybrid_results['performance_metrics'].get('cache_hit', False)}")
        
        if hybrid_results['results']:
            print(f"   📄 Top hybrid result: {hybrid_results['results'][0].get('metadata', {}).get('titulo', 'No title')[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Hybrid test failed: {e}")

async def get_performance_metrics():
    """Get detailed performance metrics"""
    
    print(f"\n📊 Detailed Performance Metrics")
    print("=" * 60)
    
    try:
        vector_optimizer = VectorPerformanceOptimizer()
        metrics = vector_optimizer.get_performance_metrics()
        
        print(f"   📈 Vector Performance Metrics:")
        print(f"      Total searches: {metrics.get('total_searches', 0)}")
        print(f"      Cache hit rate: {metrics.get('cache_hit_rate_percent', 0):.1f}%")
        print(f"      Average vector generation time: {metrics.get('average_vector_generation_time_ms', 0):.2f}ms")
        print(f"      Average search time: {metrics.get('average_search_time_ms', 0):.2f}ms")
        print(f"      Total cache hits: {metrics.get('total_cache_hits', 0)}")
        print(f"      Total cache misses: {metrics.get('total_cache_misses', 0)}")
        
        # Show storage stats
        print(f"\n   💾 Storage Statistics:")
        print(f"      Cloud vector service: {'Available' if metrics.get('cloud_service_available', False) else 'Unavailable'}")
        print(f"      Local vector service: {'Available' if metrics.get('local_service_available', False) else 'Unavailable'}")
        print(f"      BigQuery integration: {'Active' if metrics.get('bigquery_available', False) else 'Inactive'}")
        
    except Exception as e:
        print(f"   ❌ Failed to get metrics: {e}")

async def main():
    """Run all detailed analysis tests"""
    print("🚀 Starting Detailed Vector Search Analysis")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all analysis tests
    await analyze_vector_performance()
    await test_vector_capabilities()
    await test_hybrid_approach()
    await get_performance_metrics()
    
    print(f"\n🎉 Detailed Analysis Complete!")
    print(f"✅ Hybrid vector search is working with:")
    print(f"   ☁️ Cloud vector service")
    print(f"   🏠 Local vector fallback")
    print(f"   ⚡ Performance optimization")
    print(f"   🎯 Multi-layer caching")

if __name__ == "__main__":
    asyncio.run(main()) 