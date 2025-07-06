#!/usr/bin/env python3
"""
Simple Search Test
Quick test with minimal sources and shorter timeout
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

async def test_simple_search():
    """Test with minimal configuration"""
    
    print("🚀 Simple Search Test")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Login
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
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authentication successful")
            
            # Step 2: Test with minimal search
            print("\n2️⃣ Testing minimal search...")
            search_response = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": "Banco Santander",
                    "days_back": 7,  # Shorter period
                    "include_boe": True,
                    "include_news": False,  # Disable for speed
                    "include_rss": False,   # Disable for speed
                    "force_refresh": False,
                    "cache_age_hours": 24
                }
            )
            
            if search_response.status_code == 200:
                result = search_response.json()
                print(f"   ✅ Search successful!")
                print(f"   📊 Total results: {len(result.get('results', []))}")
                print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                print(f"   🔧 Search method: {result.get('cache_info', {}).get('search_method', 'N/A')}")
                
                # Show risk distribution
                risk_summary = result.get('risk_summary', {})
                print(f"   🎨 Risk distribution:")
                print(f"      Red (High risk): {risk_summary.get('high_risk_articles', 0)}")
                print(f"      Orange (Medium risk): {risk_summary.get('medium_risk_articles', 0)}")
                print(f"      Green (Low risk): {risk_summary.get('low_risk_articles', 0)}")
                
                # Show top 2 results
                results = result.get('results', [])
                if results:
                    print(f"   📄 Top 2 results:")
                    for i, res in enumerate(results[:2]):
                        print(f"      {i+1}. {res.get('source', 'Unknown')} - {res.get('title', 'No title')[:50]}...")
                        print(f"         Risk: {res.get('risk_level', 'Unknown')} ({res.get('risk_color', 'gray')})")
                
            else:
                print(f"   ❌ Search failed: {search_response.status_code}")
                print(f"   📄 Response: {search_response.text}")
            
            # Step 3: Test health endpoint
            print("\n3️⃣ Testing health endpoint...")
            health_response = await client.get(
                f"{base_url}/api/v1/streamlined/search/health",
                headers=headers
            )
            
            if health_response.status_code == 200:
                result = health_response.json()
                print(f"   ✅ Health check successful")
                print(f"   📊 Status: {result.get('status', 'Unknown')}")
                print(f"   💬 Message: {result.get('message', 'No message')}")
            else:
                print(f"   ❌ Health check failed: {health_response.status_code}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the simple search test"""
    print("🚀 Starting Simple Search Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_simple_search()
    
    print(f"\n🎉 Simple Search Test Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 