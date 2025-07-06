#!/usr/bin/env python3
"""
Simple Vector Test - Test basic vector components
"""

import os
import sys
import asyncio

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if we can import the vector components"""
    
    print("🧪 Testing Vector Component Imports")
    print("=" * 40)
    
    # Test 1: Cloud Embedding Agent
    print("\n1️⃣ Testing Cloud Embedding Agent import...")
    try:
        from app.agents.analysis.cloud_embedder import CloudEmbeddingAgent
        print("   ✅ CloudEmbeddingAgent imported successfully")
        
        # Test initialization
        agent = CloudEmbeddingAgent()
        print(f"   ✅ Cloud agent initialized")
        print(f"   📊 Vector service available: {agent.vector_service_available}")
        print(f"   📊 Embedder service available: {agent.embedder_service_available}")
        
    except Exception as e:
        print(f"   ❌ Cloud agent import failed: {e}")
    
    # Test 2: Local Embedding Agent
    print("\n2️⃣ Testing Local Embedding Agent import...")
    try:
        from app.agents.analysis.embedder import BOEEmbeddingAgent
        print("   ✅ BOEEmbeddingAgent imported successfully")
        
        # Test initialization
        agent = BOEEmbeddingAgent()
        print(f"   ✅ Local agent initialized")
        
    except Exception as e:
        print(f"   ❌ Local agent import failed: {e}")
    
    # Test 3: Vector Performance Optimizer
    print("\n3️⃣ Testing Vector Performance Optimizer import...")
    try:
        from app.services.vector_performance_optimizer import VectorPerformanceOptimizer
        print("   ✅ VectorPerformanceOptimizer imported successfully")
        
        # Test initialization
        optimizer = VectorPerformanceOptimizer()
        print(f"   ✅ Vector optimizer initialized")
        
    except Exception as e:
        print(f"   ❌ Vector optimizer import failed: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Import Tests Complete")

def test_cloud_services():
    """Test cloud services connectivity"""
    
    print("\n🌐 Testing Cloud Services Connectivity")
    print("=" * 40)
    
    import httpx
    
    # Test vector search service
    print("\n1️⃣ Testing Vector Search Service...")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://vector-search-185303190462.europe-west1.run.app/health")
            if response.status_code == 200:
                print("   ✅ Vector search service is healthy")
                print(f"   📄 Response: {response.json()}")
            else:
                print(f"   ❌ Vector search service returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Vector search service test failed: {e}")
    
    # Test embedder service
    print("\n2️⃣ Testing Embedder Service...")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://embedder-service-185303190462.europe-west1.run.app/health")
            if response.status_code == 200:
                print("   ✅ Embedder service is healthy")
                print(f"   📄 Response: {response.json()}")
            else:
                print(f"   ❌ Embedder service returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Embedder service test failed: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Cloud Services Tests Complete")

def main():
    """Run all tests"""
    print("🚀 Starting Simple Vector Tests")
    
    # Test imports
    test_imports()
    
    # Test cloud services
    test_cloud_services()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 