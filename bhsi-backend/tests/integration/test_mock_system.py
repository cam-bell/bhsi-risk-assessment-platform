#!/usr/bin/env python3
"""
Test Mock System - Verify mock data system is working for demo
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_mock_search():
    """Test the mock search system"""
    print("🧪 Testing Mock Search System")
    print("=" * 50)
    
    # Test 1: Basic search
    print("\n1. Testing basic search...")
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json={
                "company_name": "Banco Santander",
                "include_boe": True,
                "include_news": True,
                "include_rss": True,
                "days_back": 7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"   Company: {data.get('company_name')}")
            print(f"   Total results: {data.get('metadata', {}).get('total_results', 0)}")
            print(f"   BOE results: {data.get('metadata', {}).get('boe_results', 0)}")
            print(f"   News results: {data.get('metadata', {}).get('news_results', 0)}")
            print(f"   High risk results: {data.get('metadata', {}).get('high_risk_results', 0)}")
            
            # Show first result
            if data.get('results'):
                first_result = data['results'][0]
                print(f"   Sample result: {first_result.get('title', 'N/A')[:50]}...")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 2: Streamlined search
    print("\n2. Testing streamlined search...")
    try:
        response = requests.post(
            f"{BASE_URL}/streamlined/search",
            json={
                "company_name": "BBVA",
                "include_boe": True,
                "include_news": True,
                "include_rss": True,
                "days_back": 14
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Streamlined search successful!")
            print(f"   Company: {data.get('company_name')}")
            print(f"   Total results: {data.get('metadata', {}).get('total_results', 0)}")
            print(f"   Performance: {data.get('performance', {}).get('total_time_seconds', 'N/A')}s")
        else:
            print(f"❌ Streamlined search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Streamlined search error: {e}")
    
    # Test 3: Health check
    print("\n3. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/search/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful!")
            print(f"   Status: {data.get('status')}")
            print(f"   Orchestrator: {data.get('orchestrator_type')}")
            print(f"   Classifier: {data.get('classifier_type')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 4: Performance stats
    print("\n4. Testing performance stats...")
    try:
        response = requests.get(f"{BASE_URL}/search/performance", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Performance stats successful!")
            print(f"   Keyword efficiency: {data.get('statistics', {}).get('keyword_efficiency', 'N/A')}")
            print(f"   LLM usage: {data.get('statistics', {}).get('llm_usage', 'N/A')}")
        else:
            print(f"❌ Performance stats failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Performance stats error: {e}")
    
    # Test 5: Company analytics
    print("\n5. Testing company analytics...")
    try:
        response = requests.post(
            f"{BASE_URL}/companies/analyze",
            json={"name": "CaixaBank"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Company analytics successful!")
            print(f"   Company: {data.get('company_name')}")
            print(f"   Overall risk: {data.get('risk_assessment', {}).get('overall', 'N/A')}")
        else:
            print(f"❌ Company analytics failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Company analytics error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Mock System Test Complete!")
    print("\nNext Steps:")
    print("1. Start the frontend: cd bhsi-frontend && npm run dev")
    print("2. Navigate to http://localhost:5173")
    print("3. Test the search functionality in the UI")

if __name__ == "__main__":
    test_mock_search() 