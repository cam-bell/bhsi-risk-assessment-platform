#!/usr/bin/env python3
"""
Simple Assessment Test - Quick test of the assessment endpoint
"""

import asyncio
import httpx
import time

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_USER = {
    "email": "admin@bhsi.com",
    "password": "admin123"
}

async def login_and_get_token():
    """Login and get JWT token"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=ADMIN_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None

async def test_assessment_endpoint():
    """Test the assessment endpoint with a simple request"""
    print("\n🧪 Testing Assessment Endpoint (Simple)")
    print("=" * 50)
    
    # Login
    token = await login_and_get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test single company assessment with minimal sources
        assessment_request = {
            "company_name": "Banco Santander",
            "user_id": "admin",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "days_back": 7,  # Shorter time range
            "include_boe": True,
            "include_news": False,  # Disable news to speed up
            "include_rss": False,   # Disable RSS to speed up
            "include_financial": False,
            "save_to_bigquery": True
        }
        
        print("📊 Performing simple assessment...")
        print(f"   Request: {assessment_request}")
        start_time = time.time()
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/bigquery-assessment/assess",
                json=assessment_request,
                headers=headers
            )
            
            assessment_time = time.time() - start_time
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Time: {assessment_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Assessment completed successfully!")
                print(f"   Assessment ID: {data['assessment_id']}")
                print(f"   Company: {data['company_name']}")
                print(f"   Overall Risk: {data['overall_risk']}")
                print(f"   Total Results: {data['search_results']['total_results']}")
                print(f"   Processing Time: {data['processing_stats']['total_time_seconds']}s")
                print(f"   BigQuery Status: {data['bigquery_status']}")
                return True
            else:
                print(f"❌ Assessment failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Assessment test crashed: {e}")
            return False

async def test_bigquery_status():
    """Test BigQuery status endpoint"""
    print("\n🧪 Testing BigQuery Status Endpoint")
    print("=" * 50)
    
    # Login
    token = await login_and_get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/bigquery-assessment/bigquery/status",
                headers=headers
            )
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ BigQuery Status: {data['status']}")
                if 'tables' in data:
                    for table_name, table_info in data['tables'].items():
                        print(f"   Table: {table_name} - {table_info['status']}")
                        if 'stats' in table_info:
                            stats = table_info['stats']
                            print(f"     Total Assessments: {stats.get('total_assessments', 'N/A')}")
                            print(f"     High Risk: {stats.get('high_risk', 'N/A')}")
                            print(f"     Medium Risk: {stats.get('medium_risk', 'N/A')}")
                            print(f"     Low Risk: {stats.get('low_risk', 'N/A')}")
                return True
            else:
                print(f"❌ BigQuery status failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ BigQuery status test crashed: {e}")
            return False

async def main():
    """Run simple tests"""
    print("🚀 Starting Simple Assessment Tests")
    print("=" * 60)
    
    tests = [
        ("Assessment Endpoint", test_assessment_endpoint),
        ("BigQuery Status", test_bigquery_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Assessment integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 