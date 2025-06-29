#!/usr/bin/env python3
"""
Simple test to see the logging output
"""

import requests
import json

def test_company_analysis():
    """Test the company analysis endpoint to trigger logging"""
    url = "http://localhost:8000/api/v1/companies/analyze"
    
    data = {
        "name": "Test Company",
        "description": "A test company"
    }
    
    try:
        print("Making request to trigger logging...")
        response = requests.post(url, json=data, timeout=30)
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_company_analysis() 