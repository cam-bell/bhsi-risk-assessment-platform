#!/usr/bin/env python3
"""
Test script for analytics endpoints used by the frontend
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_analytics_endpoints():
    """Test all analytics endpoints that the frontend will use"""
    
    print("🧪 Testing Analytics Endpoints for Frontend Integration")
    print("=" * 60)
    
    # Test 1: Analytics Health Check
    print("\n1. Testing Analytics Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/companies/analytics/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data.get('status', 'unknown')}")
            print(f"   Services: {health_data.get('services', {})}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 2: System Status
    print("\n2. Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/companies/system/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ System Status: {status_data.get('status', 'unknown')}")
            print(f"   System Type: {status_data.get('system_type', 'unknown')}")
            print(f"   Performance: {status_data.get('performance', {})}")
        else:
            print(f"❌ System Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System Status error: {e}")
    
    # Test 3: Risk Trends
    print("\n3. Testing Risk Trends...")
    try:
        response = requests.get(f"{BASE_URL}/companies/analytics/trends")
        if response.status_code == 200:
            trends_data = response.json()
            print(f"✅ Risk Trends: Retrieved successfully")
            if 'system_wide_trends' in trends_data:
                distribution = trends_data['system_wide_trends'].get('overall_risk_distribution', {})
                print(f"   Risk Distribution: Green={distribution.get('green', 0)}, Orange={distribution.get('orange', 0)}, Red={distribution.get('red', 0)}")
        else:
            print(f"❌ Risk Trends failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Risk Trends error: {e}")
    
    # Test 4: Company Analytics (using a test company)
    test_company = "Banco Santander"
    print(f"\n4. Testing Company Analytics for '{test_company}'...")
    try:
        response = requests.get(f"{BASE_URL}/companies/{test_company}/analytics")
        if response.status_code == 200:
            analytics_data = response.json()
            print(f"✅ Company Analytics: Retrieved successfully")
            if 'risk_profile' in analytics_data:
                risk_profile = analytics_data['risk_profile']
                print(f"   Risk Profile: Overall={risk_profile.get('overall', 'unknown')}")
        else:
            print(f"❌ Company Analytics failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Company Analytics error: {e}")
    
    # Test 5: Company Comparison
    print("\n5. Testing Company Comparison...")
    try:
        companies = "Banco Santander,BBVA,CaixaBank"
        response = requests.get(f"{BASE_URL}/companies/analytics/comparison", params={"companies": companies})
        if response.status_code == 200:
            comparison_data = response.json()
            print(f"✅ Company Comparison: Retrieved successfully")
            if 'comparison_data' in comparison_data:
                print(f"   Companies compared: {len(comparison_data['comparison_data'])}")
        else:
            print(f"❌ Company Comparison failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Company Comparison error: {e}")
    
    # Test 6: Management Summary
    print(f"\n6. Testing Management Summary for '{test_company}'...")
    try:
        response = requests.post(f"{BASE_URL}/analysis/management-summary", json={"company_name": test_company})
        if response.status_code == 200:
            summary_data = response.json()
            print(f"✅ Management Summary: Retrieved successfully")
            if 'summary' in summary_data:
                print(f"   Executive Summary: {len(summary_data['summary'].get('executive_summary', ''))} characters")
        else:
            print(f"❌ Management Summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Management Summary error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Frontend Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Start the frontend: cd bhsi-frontend && npm run dev")
    print("2. Navigate to http://localhost:5173/analytics")
    print("3. Test the analytics features in the UI")

if __name__ == "__main__":
    test_analytics_endpoints() 