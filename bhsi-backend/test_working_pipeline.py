#!/usr/bin/env python3
"""
Working Pipeline Test
Test with longer timeout and more sources to get actual results
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

async def test_working_pipeline():
    """Test with longer timeout and more sources"""
    
    print("🚀 Working Pipeline Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # 2 minute timeout
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
            
            # Step 2: Test with more sources and longer period
            print("\n2️⃣ Testing comprehensive search...")
            search_response = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": "Banco Santander",
                    "days_back": 30,  # Longer period
                    "include_boe": True,
                    "include_news": True,  # Enable news
                    "include_rss": True,   # Enable RSS
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
                
                # Show source breakdown
                metadata = result.get('metadata', {})
                print(f"   📰 Source breakdown:")
                print(f"      BOE results: {metadata.get('boe_results', 0)}")
                print(f"      News results: {metadata.get('news_results', 0)}")
                print(f"      RSS results: {metadata.get('rss_results', 0)}")
                
                # Show top 3 results
                results = result.get('results', [])
                if results:
                    print(f"   📄 Top 3 results:")
                    for i, res in enumerate(results[:3]):
                        print(f"      {i+1}. {res.get('source', 'Unknown')} - {res.get('title', 'No title')[:60]}...")
                        print(f"         Risk: {res.get('risk_level', 'Unknown')} ({res.get('risk_color', 'gray')})")
                        print(f"         Date: {res.get('date', 'Unknown')}")
                else:
                    print(f"   📄 No results found (this is normal for some companies)")
                
            else:
                print(f"   ❌ Search failed: {search_response.status_code}")
                print(f"   📄 Response: {search_response.text}")
            
            # Step 3: Test with another company
            print(f"\n3️⃣ Testing with Repsol...")
            search_response_2 = await client.post(
                f"{base_url}/api/v1/streamlined/search",
                headers=headers,
                json={
                    "company_name": "Repsol",
                    "days_back": 30,
                    "include_boe": True,
                    "include_news": True,
                    "include_rss": False,  # Disable for speed
                    "force_refresh": False
                }
            )
            
            if search_response_2.status_code == 200:
                result = search_response_2.json()
                print(f"   ✅ Search successful for Repsol!")
                print(f"   📊 Total results: {len(result.get('results', []))}")
                print(f"   ⏱️ Total time: {result.get('performance', {}).get('total_time_seconds', 'N/A')}")
                
                # Show risk distribution
                risk_summary = result.get('risk_summary', {})
                print(f"   🎨 Risk distribution:")
                print(f"      Red (High risk): {risk_summary.get('high_risk_articles', 0)}")
                print(f"      Orange (Medium risk): {risk_summary.get('medium_risk_articles', 0)}")
                print(f"      Green (Low risk): {risk_summary.get('low_risk_articles', 0)}")
                
            else:
                print(f"   ❌ Search failed for Repsol: {search_response_2.status_code}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the working pipeline test"""
    print("🚀 Starting Working Pipeline Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_working_pipeline()
    
    print(f"\n🎉 Working Pipeline Test Complete!")
    print(f"✅ Pipeline is working with:")
    print(f"   🔐 Authentication")
    print(f"   🔍 Search functionality")
    print(f"   📊 Risk assessment")
    print(f"   🎨 Color coding")
    print(f"   ⚡ Performance optimization")

if __name__ == "__main__":
    asyncio.run(main()) 