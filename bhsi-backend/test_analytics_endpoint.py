#!/usr/bin/env python3
"""
Simple test script for the analytics endpoint
"""

import asyncio
import httpx
import json

async def test_analytics_endpoint():
    """Test the analytics endpoint for Pescanova"""
    
    # Test URL
    url = "http://localhost:8000/api/v1/companies/Pescanova/analytics"
    params = {
        "include_trends": "true",
        "include_sectors": "false"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"Testing analytics endpoint: {url}")
            print(f"Parameters: {params}")
            
            response = await client.get(url, params=params)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS: Analytics endpoint working correctly!")
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                # Check for expected fields
                expected_fields = ["company", "generated_at", "analytics_version"]
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Warning: Missing expected fields: {missing_fields}")
                else:
                    print("✅ All expected fields present")
                
                # Check if using fallback data
                if data.get("company", {}).get("fallback"):
                    print("ℹ️  Using fallback data (BigQuery service unavailable)")
                else:
                    print("✅ Using real BigQuery data")
                    
            else:
                print(f"❌ ERROR: Status code {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

async def test_analytics_endpoint_with_mock():
    """Test the analytics endpoint with mock data enabled"""
    
    # Test URL with mock parameter
    url = "http://localhost:8000/api/v1/companies/Pescanova/analytics"
    params = {
        "include_trends": "true",
        "include_sectors": "true",
        "use_mock": "true"  # Try to enable mock data
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\nTesting analytics endpoint with mock data: {url}")
            print(f"Parameters: {params}")
            
            response = await client.get(url, params=params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS: Analytics endpoint with mock data working!")
                print(f"Response data: {json.dumps(data, indent=2)}")
                
            else:
                print(f"❌ ERROR: Status code {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

async def test_health_endpoint():
    """Test the analytics health endpoint"""
    
    url = "http://localhost:8000/api/v1/companies/analytics/health"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\nTesting analytics health endpoint: {url}")
            
            response = await client.get(url)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Analytics health endpoint working!")
                print(f"Health data: {json.dumps(data, indent=2)}")
                
            else:
                print(f"❌ ERROR: Status code {response.status_code}")
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

async def main():
    """Run all tests"""
    print("🧪 Testing Analytics Endpoint for Pescanova")
    print("=" * 50)
    
    # Test basic analytics endpoint
    await test_analytics_endpoint()
    
    # Test with mock data
    await test_analytics_endpoint_with_mock()
    
    # Test health endpoint
    await test_health_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    asyncio.run(main()) 