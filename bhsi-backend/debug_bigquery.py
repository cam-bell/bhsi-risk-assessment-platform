#!/usr/bin/env python3
"""
Debug script for BigQuery analytics issue
"""

import asyncio
import httpx
import traceback

async def debug_bigquery_analytics():
    """Debug the BigQuery analytics call in detail"""
    
    print("🔍 Debugging BigQuery Analytics Issue...")
    print("=" * 60)
    
    # Test the specific failing endpoint
    url = "https://bigquery-analytics-185303190462.europe-west1.run.app/analytics/company/Banco%20Santander"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"📞 Calling: {url}")
            
            response = await client.get(url)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success Response:")
                print(f"   📊 Company: {result.get('company_name')}")
                print(f"   📊 Total Events: {result.get('total_events')}")
                print(f"   📊 Risk Distribution: {result.get('risk_distribution')}")
                print(f"   📊 Latest Events: {len(result.get('latest_events', []))}")
                
            else:
                print(f"❌ Error Response:")
                print(f"   📄 Text: {response.text}")
                
                # Try to parse as JSON for more details
                try:
                    error_data = response.json()
                    print(f"   📊 Error Data: {error_data}")
                except:
                    print("   📄 Could not parse error as JSON")
    
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        traceback.print_exc()

async def test_health_endpoint():
    """Test the health endpoint"""
    
    print("\n🏥 Testing Health Endpoint...")
    print("=" * 60)
    
    url = "https://bigquery-analytics-185303190462.europe-west1.run.app/health"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health Response: {result}")
            else:
                print(f"❌ Health Error: {response.text}")
    
    except Exception as e:
        print(f"💥 Health Exception: {e}")

async def test_other_endpoints():
    """Test other BigQuery endpoints"""
    
    endpoints = [
        "/analytics/risk-trends",
        "/analytics/alerts", 
        "/analytics/sectors",
        "/stats/events"
    ]
    
    base_url = "https://bigquery-analytics-185303190462.europe-west1.run.app"
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}...")
        print("=" * 40)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{base_url}{endpoint}")
                
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success: {type(result)} with {len(str(result))} chars")
                else:
                    print(f"❌ Error: {response.text[:200]}...")
        
        except Exception as e:
            print(f"💥 Exception: {e}")

async def main():
    """Run all debug tests"""
    
    print("🧪 BIGQUERY ANALYTICS DEBUG SESSION")
    print("=" * 80)
    
    # Test health first
    await test_health_endpoint()
    
    # Test the failing analytics endpoint
    await debug_bigquery_analytics()
    
    # Test other endpoints
    await test_other_endpoints()
    
    print(f"\n🏁 Debug session complete")

if __name__ == "__main__":
    asyncio.run(main()) 