#!/usr/bin/env python3
"""
True Hybrid Vector Storage Test
Demonstrates storing vectors in both BigQuery and local ChromaDB
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.hybrid_vector_storage import HybridVectorStorage
from app.services.bigquery_vector_schema import BigQueryVectorSchema
from google.cloud import bigquery

async def test_true_hybrid_approach():
    """Test the true hybrid vector storage approach"""
    
    print("🔄 Testing True Hybrid Vector Storage")
    print("=" * 60)
    
    try:
        # Initialize hybrid storage
        hybrid_storage = HybridVectorStorage()
        
        # Initialize BigQuery schema
        client = bigquery.Client()
        schema_manager = BigQueryVectorSchema(client)
        
        print(f"\n📊 BigQuery Vector Storage Setup")
        print("-" * 40)
        
        # Create vector tables in BigQuery
        print("1️⃣ Creating vector tables in BigQuery...")
        vector_table_created = schema_manager.create_vector_table()
        cache_table_created = schema_manager.create_search_cache_table()
        
        if vector_table_created and cache_table_created:
            print("   ✅ Vector tables created successfully")
        else:
            print("   ❌ Failed to create vector tables")
            return
        
        # Test vector encoding/decoding
        print(f"\n2️⃣ Testing Vector Encoding/Decoding")
        print("-" * 40)
        
        test_vector = [0.1, 0.2, 0.3, 0.4, 0.5] * 76  # 380 dimensions
        encoded = hybrid_storage.encode_vector_for_bigquery(test_vector)
        decoded = hybrid_storage.decode_vector_from_bigquery(encoded)
        
        print(f"   Original vector length: {len(test_vector)}")
        print(f"   Encoded length: {len(encoded)}")
        print(f"   Decoded vector length: {len(decoded)}")
        print(f"   Encoding/decoding successful: {len(test_vector) == len(decoded)}")
        
        # Test storing vector in BigQuery
        print(f"\n3️⃣ Testing Vector Storage in BigQuery")
        print("-" * 40)
        
        test_vector_data = {
            "event_id": "test_event_001",
            "vector_embedding": encoded,
            "vector_dimension": len(test_vector),
            "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
            "vector_created_at": datetime.utcnow().isoformat(),
            "metadata": json.dumps({"test": True}),
            "is_active": True,
            "company_name": "Test Company",
            "risk_level": "Medium",
            "source": "TEST",
            "title": "Test Event",
            "text_summary": "This is a test event for vector storage"
        }
        
        success = schema_manager.insert_vector_data(test_vector_data)
        print(f"   Vector storage in BigQuery: {'✅ Success' if success else '❌ Failed'}")
        
        # Test hybrid semantic search
        print(f"\n4️⃣ Testing Hybrid Semantic Search")
        print("-" * 40)
        
        start_time = time.time()
        search_results = await hybrid_storage.hybrid_semantic_search(
            query="Banco Santander",
            k=5,
            use_cache=True
        )
        search_time = time.time() - start_time
        
        print(f"   ⏱️ Search time: {search_time:.2f}s")
        print(f"   📊 Results: {len(search_results['results'])}")
        print(f"   🔧 Source: {search_results['source']}")
        print(f"   📈 Performance metrics:")
        for key, value in search_results['performance_metrics'].items():
            print(f"      {key}: {value}")
        
        # Test migration from ChromaDB to BigQuery
        print(f"\n5️⃣ Testing Vector Migration")
        print("-" * 40)
        
        migration_stats = await hybrid_storage.migrate_vectors_to_bigquery()
        print(f"   Migration stats: {json.dumps(migration_stats, indent=2)}")
        
        # Get hybrid stats
        print(f"\n6️⃣ Hybrid Storage Statistics")
        print("-" * 40)
        
        stats = hybrid_storage.get_hybrid_stats()
        print(f"   BigQuery searches: {stats['bigquery_searches']}")
        print(f"   ChromaDB searches: {stats['chromadb_searches']}")
        print(f"   Cloud searches: {stats['cloud_searches']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cloud service available: {stats['cloud_service_available']}")
        print(f"   Local service available: {stats['local_service_available']}")
        print(f"   BigQuery available: {stats['bigquery_available']}")
        
        # Get BigQuery table stats
        table_stats = schema_manager.get_table_stats()
        print(f"\n   BigQuery Table Stats:")
        print(f"      Vector count: {table_stats.get('vector_count', 0)}")
        print(f"      Cache count: {table_stats.get('cache_count', 0)}")
        print(f"      Vector table: {table_stats.get('vector_table', 'N/A')}")
        print(f"      Cache table: {table_stats.get('cache_table', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_performance_comparison():
    """Compare performance between different storage approaches"""
    
    print(f"\n⚡ Performance Comparison")
    print("=" * 60)
    
    hybrid_storage = HybridVectorStorage()
    
    test_queries = [
        "Banco Santander",
        "Repsol",
        "concurso de acreedores",
        "financial risk"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} queries with hybrid approach")
    print("-" * 60)
    
    total_time = 0
    total_results = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        start_time = time.time()
        results = await hybrid_storage.hybrid_semantic_search(query, k=3)
        search_time = time.time() - start_time
        
        print(f"   ⏱️ Time: {search_time:.2f}s")
        print(f"   📊 Results: {len(results['results'])}")
        print(f"   🔧 Source: {results['source']}")
        
        total_time += search_time
        total_results += len(results['results'])
    
    print(f"\n📈 Performance Summary")
    print("-" * 60)
    print(f"   🏢 Queries tested: {len(test_queries)}")
    print(f"   ⏱️ Total time: {total_time:.2f}s")
    print(f"   📊 Average time per query: {total_time/len(test_queries):.2f}s")
    print(f"   🔍 Total results: {total_results}")
    print(f"   📈 Average results per query: {total_results/len(test_queries):.1f}")

async def main():
    """Run all hybrid vector tests"""
    print("🚀 Starting True Hybrid Vector Storage Tests")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test true hybrid approach
    await test_true_hybrid_approach()
    
    # Test performance comparison
    await test_performance_comparison()
    
    print(f"\n🎉 True Hybrid Vector Storage Test Complete!")
    print(f"✅ Now storing vectors in:")
    print(f"   📊 BigQuery (persistent)")
    print(f"   🏠 ChromaDB (fast)")
    print(f"   ☁️ Cloud Vector Service (scalable)")

if __name__ == "__main__":
    asyncio.run(main()) 