#!/usr/bin/env python3
"""
Test script to verify if cloud services are actually connected and working
"""

import sys
import httpx
import asyncio
import json
from datetime import datetime

# Test URLs from config
CLOUD_SERVICES = {
    "gemini": "https://gemini-service-185303190462.europe-west1.run.app",
    "embedder": "https://embedder-service-185303190462.europe-west1.run.app", 
    "vector_search": "https://vector-search-185303190462.europe-west1.run.app",
    "bigquery": "https://bigquery-analytics-185303190462.europe-west1.run.app"
}

async def test_service_health(service_name: str, base_url: str):
    """Test if a cloud service is accessible and healthy"""
    print(f"\n🔍 Testing {service_name.upper()} Service...")
    print(f"   URL: {base_url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            health_url = f"{base_url}/health"
            response = await client.get(health_url)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health check: PASSED")
                print(f"   📊 Response: {json.dumps(health_data, indent=6)}")
                return True
            else:
                print(f"   ❌ Health check: FAILED (Status: {response.status_code})")
                print(f"   📄 Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print(f"   ⏰ Health check: TIMEOUT (service unreachable)")
        return False
    except Exception as e:
        print(f"   💥 Health check: ERROR - {str(e)}")
        return False

async def test_gemini_classification():
    """Test Gemini service with actual classification request"""
    print(f"\n🧠 Testing GEMINI Classification...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{CLOUD_SERVICES['gemini']}/classify"
            
            test_data = {
                "text": "Banco Santander ha sido objeto de una investigación por presunto blanqueo de capitales",
                "title": "Investigación regulatoria",
                "source": "BOE",
                "section": "JUS"
            }
            
            response = await client.post(url, json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Classification: SUCCESS")
                print(f"   📊 Result: {json.dumps(result, indent=6)}")
                return True
            else:
                print(f"   ❌ Classification: FAILED (Status: {response.status_code})")
                print(f"   📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   💥 Classification: ERROR - {str(e)}")
        return False

async def test_embedder_service():
    """Test Embedder service with actual embedding request"""
    print(f"\n🔍 Testing EMBEDDER Service...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{CLOUD_SERVICES['embedder']}/embed"
            
            # Fix: Use 'text' (singular) as expected by the API
            test_data = {
                "text": "Banco Santander análisis de riesgo"
            }
            
            response = await client.post(url, json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Embedding: SUCCESS")
                print(f"   📊 Embedding generated successfully")
                print(f"   📏 Dimensions: {len(result.get('embedding', [])) if result.get('embedding') else 0}")
                return True
            else:
                print(f"   ❌ Embedding: FAILED (Status: {response.status_code})")
                print(f"   📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   💥 Embedding: ERROR - {str(e)}")
        return False

async def test_bigquery_analytics():
    """Test BigQuery analytics service"""
    print(f"\n📊 Testing BIGQUERY Analytics...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test company analytics
            url = f"{CLOUD_SERVICES['bigquery']}/analytics/company/Banco%20Santander"
            
            response = await client.get(url)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Analytics: SUCCESS")
                print(f"   📊 Result: {json.dumps(result, indent=6)}")
                return True
            else:
                print(f"   ❌ Analytics: FAILED (Status: {response.status_code})")
                print(f"   📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   💥 Analytics: ERROR - {str(e)}")
        return False

async def test_local_imports():
    """Test if local backend components can import and initialize"""
    print(f"\n🏠 Testing LOCAL Backend Components...")
    
    try:
        # Test basic imports
        sys.path.insert(0, '.')
        
        from app.core.config import settings
        print(f"   ✅ Config: imported successfully")
        
        from app.agents.analysis.cloud_classifier import CloudRiskClassifier
        classifier = CloudRiskClassifier()
        print(f"   ✅ Cloud Classifier: initialized")
        
        from app.agents.analysis.management_summarizer import ManagementSummarizer
        summarizer = ManagementSummarizer()
        print(f"   ✅ Management Summarizer: initialized")
        
        from app.agents.analytics.analytics_service import AnalyticsService
        analytics = AnalyticsService()
        print(f"   ✅ Analytics Service: initialized")
        
        return True
        
    except Exception as e:
        print(f"   💥 Local Import: ERROR - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🧪 BHSI CLOUD SERVICES REALITY CHECK")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now()}")
    
    results = {}
    
    # Test local components first
    results['local'] = await test_local_imports()
    
    # Test each cloud service health
    for service_name, url in CLOUD_SERVICES.items():
        results[f'{service_name}_health'] = await test_service_health(service_name, url)
    
    # Test actual functionality if health checks pass
    if results.get('gemini_health'):
        results['gemini_classify'] = await test_gemini_classification()
    
    if results.get('embedder_health'):
        results['embedder_embed'] = await test_embedder_service()
    
    if results.get('bigquery_health'):
        results['bigquery_analytics'] = await test_bigquery_analytics()
    
    # Summary
    print(f"\n🏁 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {test_name:20} {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL CLOUD SERVICES ARE WORKING!")
    elif passed >= total * 0.5:
        print("⚠️  SOME SERVICES ARE DOWN - PARTIAL FUNCTIONALITY")
    else:
        print("💥 MAJOR ISSUES - MOST SERVICES NOT WORKING")

if __name__ == "__main__":
    asyncio.run(main()) 