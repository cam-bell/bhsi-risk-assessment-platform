#!/usr/bin/env python3
"""
Test Assessments Integration - Verify BigQuery assessments table integration
"""

import asyncio
import json
import time
from datetime import datetime
import httpx

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_USER = {
    "email": "admin@bhsi.com",
    "password": "admin123"
}

async def login_and_get_token():
    """Login and get JWT token"""
    async with httpx.AsyncClient() as client:
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
    """Test the assessment endpoint"""
    print("\n🧪 Testing Assessment Endpoint")
    print("=" * 50)
    
    # Login
    token = await login_and_get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # Test single company assessment
        assessment_request = {
            "company_name": "Banco Santander",
            "user_id": "admin",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "days_back": 30,
            "include_boe": True,
            "include_news": True,
            "include_rss": True,
            "include_financial": False,
            "save_to_bigquery": True
        }
        
        print("📊 Performing single company assessment...")
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
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Assessment completed in {assessment_time:.2f}s")
                print(f"   Assessment ID: {data['assessment_id']}")
                print(f"   Company: {data['company_name']}")
                print(f"   Overall Risk: {data['overall_risk']}")
                print(f"   Risk Breakdown: {data['risk_breakdown']}")
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
            import traceback
            traceback.print_exc()
            return False

async def test_batch_assessment():
    """Test batch assessment endpoint"""
    print("\n🧪 Testing Batch Assessment Endpoint")
    print("=" * 50)
    
    # Login
    token = await login_and_get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # Test batch assessment
        batch_request = {
            "companies": [
                {"company_name": "Repsol"},
                {"company_name": "Telefonica"}
            ],
            "user_id": "admin",
            "assessment_config": {
                "days_back": 30,
                "include_boe": True,
                "include_news": True,
                "include_rss": True,
                "include_financial": False
            }
        }
        
        print("📊 Performing batch assessment...")
        print(f"   Request: {batch_request}")
        start_time = time.time()
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/bigquery-assessment/batch-assess",
                json=batch_request,
                headers=headers
            )
            
            batch_time = time.time() - start_time
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Batch assessment completed in {batch_time:.2f}s")
                print(f"   Batch ID: {data['batch_id']}")
                print(f"   Total Companies: {data['total_companies']}")
                print(f"   Successful: {data['processing_stats']['successful']}")
                print(f"   Failed: {data['processing_stats']['failed']}")
                print(f"   Total Time: {data['processing_stats']['total_time']}s")
                
                for assessment in data['assessments']:
                    print(f"   - {assessment['company_name']}: {assessment['overall_risk']} ({assessment['status']})")
                
                return True
            else:
                print(f"❌ Batch assessment failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Batch assessment test crashed: {e}")
            import traceback
            traceback.print_exc()
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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/bigquery-assessment/bigquery/status",
                headers=headers
            )
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text}")
            
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
            import traceback
            traceback.print_exc()
            return False

async def test_assessment_crud():
    """Test assessment CRUD operations directly"""
    print("\n🧪 Testing Assessment CRUD Operations")
    print("=" * 50)
    
    try:
        from app.crud.bigquery_assessment import bigquery_assessment
        
        # Test creating an assessment
        test_assessment = {
            "company_vat": "A12345678",
            "user_id": "test-user",
            "turnover_risk": "green",
            "shareholding_risk": "orange",
            "bankruptcy_risk": "green",
            "legal_risk": "red",
            "corruption_risk": "green",
            "overall_risk": "orange",
            "financial_score": 0.3,
            "legal_score": 0.7,
            "press_score": 0.2,
            "composite_score": 0.4,
            "search_date_range_start": "2024-01-01",
            "search_date_range_end": "2024-12-31",
            "sources_searched": ["BOE", "NewsAPI"],
            "total_results_found": 25,
            "high_risk_results": 3,
            "medium_risk_results": 8,
            "low_risk_results": 14,
            "analysis_summary": "Test assessment for CRUD operations",
            "key_findings": ["Legal risk identified", "Financial stability good"],
            "recommendations": ["Monitor legal developments", "Continue current practices"],
            "classification_method": "hybrid_classifier",
            "processing_time_seconds": 5.2
        }
        
        print("📝 Creating test assessment...")
        result = await bigquery_assessment.create_assessment(test_assessment)
        print(f"✅ Assessment created: {result.get('assessment_id', 'Unknown')}")
        
        # Test getting assessments by company
        print("🔍 Getting assessments by company...")
        company_assessments = await bigquery_assessment.get_by_company("A12345678")
        print(f"✅ Found {len(company_assessments)} assessments for company")
        
        # Test getting assessments by user
        print("👤 Getting assessments by user...")
        user_assessments = await bigquery_assessment.get_by_user("test-user")
        print(f"✅ Found {len(user_assessments)} assessments for user")
        
        # Test getting assessment stats
        print("📊 Getting assessment statistics...")
        stats = await bigquery_assessment.get_assessment_stats()
        print(f"✅ Assessment stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_streamlined_search_with_assessment():
    """Test streamlined search and verify it works with assessment data"""
    print("\n🧪 Testing Streamlined Search with Assessment Integration")
    print("=" * 50)
    
    # Login
    token = await login_and_get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # Test streamlined search
        search_request = {
            "company_name": "Banco Santander",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "days_back": 30,
            "include_boe": True,
            "include_news": True,
            "include_rss": True,
            "force_refresh": False,
            "cache_age_hours": 24
        }
        
        print("🔍 Performing streamlined search...")
        print(f"   Request: {search_request}")
        start_time = time.time()
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/streamlined/search",
                json=search_request,
                headers=headers
            )
            
            search_time = time.time() - start_time
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text[:500]}...")  # Truncate long responses
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Streamlined search completed in {search_time:.2f}s")
                print(f"   Company: {data['company_name']}")
                print(f"   Total Results: {data['metadata']['total_results']}")
                print(f"   BOE Results: {data['metadata']['boe_results']}")
                print(f"   News Results: {data['metadata']['news_results']}")
                print(f"   RSS Results: {data['metadata']['rss_results']}")
                print(f"   High Risk Results: {data['metadata']['high_risk_results']}")
                print(f"   Overall Risk: {data['overall_risk']}")
                print(f"   Cache Info: {data['cache_info']['search_method']}")
                print(f"   Performance: {data['performance']['total_time_seconds']}s")
                
                # Check if results have risk_color
                results_with_color = [r for r in data['results'] if r.get('risk_color')]
                print(f"   Results with risk_color: {len(results_with_color)}/{len(data['results'])}")
                
                return True
            else:
                print(f"❌ Streamlined search failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Streamlined search test crashed: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting Assessments Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Assessment Endpoint", test_assessment_endpoint),
        ("Batch Assessment", test_batch_assessment),
        ("BigQuery Status", test_bigquery_status),
        ("Assessment CRUD", test_assessment_crud),
        ("Streamlined Search", test_streamlined_search_with_assessment)
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
        print("🎉 All tests passed! Assessments integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 