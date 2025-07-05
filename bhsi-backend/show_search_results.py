#!/usr/bin/env python3
"""
Script to show complete search results structure
"""

import requests
import json

def get_token():
    """Get JWT token"""
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "admin@bhsi.com", "password": "admin123"}
    )
    return response.json()["access_token"]

def search_company(token, company_name="Repsol"):
    """Search for a company"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "http://localhost:8000/api/v1/streamlined/search",
        headers=headers,
        json={
            "company_name": company_name,
            "days_back": 7,
            "include_boe": True,
            "include_news": True,
            "include_rss": True
        }
    )
    return response.json()

def show_results(data):
    """Show the complete results structure"""
    print("📋 COMPLETE SEARCH RESPONSE STRUCTURE")
    print("=" * 50)
    
    print("\n🎯 MAIN FIELDS:")
    print(f"  - company_name: {data.get('company_name')}")
    print(f"  - search_date: {data.get('search_date')}")
    print(f"  - overall_risk: {data.get('overall_risk')}")
    print(f"  - total_results: {len(data.get('results', []))}")
    
    print("\n📊 RISK SUMMARY:")
    risk_summary = data.get('risk_summary', {})
    print(f"  - overall_risk: {risk_summary.get('overall_risk')}")
    print(f"  - risk_distribution: {risk_summary.get('risk_distribution')}")
    print(f"  - total_articles: {risk_summary.get('total_articles')}")
    print(f"  - high_risk_articles: {risk_summary.get('high_risk_articles')}")
    print(f"  - medium_risk_articles: {risk_summary.get('medium_risk_articles')}")
    print(f"  - low_risk_articles: {risk_summary.get('low_risk_articles')}")
    
    print("\n⚡ PERFORMANCE:")
    perf = data.get('performance', {})
    print(f"  - total_time_seconds: {perf.get('total_time_seconds')}")
    print(f"  - cache_time_seconds: {perf.get('cache_time_seconds')}")
    print(f"  - classification_time_seconds: {perf.get('classification_time_seconds')}")
    
    print("\n📰 SAMPLE RESULTS (first 5):")
    results = data.get('results', [])
    for i, result in enumerate(results[:5]):
        print(f"\n  {i+1}. {result.get('source', 'Unknown')}")
        print(f"     Title: {result.get('title', 'No title')}")
        print(f"     Risk Level: {result.get('risk_level', 'Unknown')}")
        print(f"     Risk Color: {result.get('risk_color', 'Unknown')}")
        print(f"     Confidence: {result.get('confidence', 'Unknown')}")
        print(f"     Method: {result.get('method', 'Unknown')}")
        print(f"     Date: {result.get('date', 'Unknown')}")
        print(f"     URL: {result.get('url', 'No URL')}")
        if result.get('summary'):
            print(f"     Summary: {result.get('summary', '')[:100]}...")
    
    print(f"\n📈 COMPLETE RESULTS COUNT: {len(results)}")
    print("=" * 50)

if __name__ == "__main__":
    try:
        print("🔐 Getting JWT token...")
        token = get_token()
        print("✅ Token obtained successfully")
        
        print("\n🔍 Searching for Repsol...")
        data = search_company(token)
        print("✅ Search completed successfully")
        
        show_results(data)
        
    except Exception as e:
        print(f"❌ Error: {e}") 