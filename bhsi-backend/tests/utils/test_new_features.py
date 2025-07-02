#!/usr/bin/env python3
"""
Test Script for New BHSI Features
Tests all the new analytics and management summary functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return {"success": True, "data": response.json(), "status_code": response.status_code}
        else:
            return {"success": False, "error": response.text, "status_code": response.status_code}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def print_test_result(test_name: str, result: Dict[str, Any]):
    """Print test result in a formatted way"""
    if result.get("success"):
        print(f"✅ {test_name}: PASSED")
        if "data" in result:
            print(f"   Response: {json.dumps(result['data'], indent=2)[:200]}...")
    else:
        print(f"❌ {test_name}: FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    print()

def main():
    """Run all tests"""
    print("🚀 Testing BHSI New Features")
    print("=" * 50)
    
    # Test 1: System Health
    print("1️⃣ Testing System Health...")
    result = test_endpoint("/companies/system/status")
    print_test_result("System Status", result)
    
    # Test 2: Analytics Health
    print("2️⃣ Testing Analytics Health...")
    result = test_endpoint("/companies/analytics/health")
    print_test_result("Analytics Health", result)
    
    # Test 3: Management Summary Templates
    print("3️⃣ Testing Management Summary Templates...")
    result = test_endpoint("/analysis/summary-templates")
    print_test_result("Summary Templates", result)
    
    # Test 4: Management Summary Generation
    print("4️⃣ Testing Management Summary Generation...")
    test_data = {
        "company_name": "Banco Santander",
        "classification_results": [
            {
                "title": "Regulatory investigation opened",
                "risk_level": "High-Legal",
                "confidence": 0.95,
                "source": "BOE",
                "method": "keyword_gate"
            },
            {
                "title": "Financial results positive",
                "risk_level": "Low-Legal", 
                "confidence": 0.85,
                "source": "News",
                "method": "keyword_gate"
            }
        ],
        "include_evidence": True,
        "language": "es"
    }
    result = test_endpoint("/analysis/management-summary", "POST", test_data)
    print_test_result("Management Summary", result)
    
    # Test 5: Company Analytics
    print("5️⃣ Testing Company Analytics...")
    result = test_endpoint("/companies/Banco%20Santander/analytics")
    print_test_result("Company Analytics", result)
    
    # Test 6: Risk Trends
    print("6️⃣ Testing Risk Trends...")
    result = test_endpoint("/companies/analytics/trends")
    print_test_result("Risk Trends", result)
    
    # Test 7: Company Comparison
    print("7️⃣ Testing Company Comparison...")
    result = test_endpoint("/companies/analytics/comparison?companies=Banco%20Santander,BBVA,CaixaBank")
    print_test_result("Company Comparison", result)
    
    # Test 8: Company Analysis
    print("8️⃣ Testing Company Analysis...")
    analysis_data = {
        "name": "Test Company Ltd",
        "description": "A test company for analysis"
    }
    result = test_endpoint("/companies/analyze", "POST", analysis_data)
    print_test_result("Company Analysis", result)
    
    # Test 9: List Companies
    print("9️⃣ Testing List Companies...")
    result = test_endpoint("/companies/")
    print_test_result("List Companies", result)
    
    print("🎉 Testing Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main() 