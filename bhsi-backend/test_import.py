#!/usr/bin/env python3
"""
Test the import directly to see what company_crud is
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from app.crud import company as company_crud
    print(f"✅ Import successful")
    print(f"Type of company_crud: {type(company_crud)}")
    print(f"Dir of company_crud: {dir(company_crud)}")
    
    # Try to access the company instance
    if hasattr(company_crud, 'company'):
        print(f"✅ company_crud.company exists: {company_crud.company}")
        print(f"Type of company_crud.company: {type(company_crud.company)}")
        print(f"Dir of company_crud.company: {dir(company_crud.company)}")
    else:
        print("❌ company_crud.company does not exist")
        
    # Try to access methods directly
    if hasattr(company_crud, 'get_by_name'):
        print("✅ get_by_name exists on company_crud")
    else:
        print("❌ get_by_name does not exist on company_crud")
        
except Exception as e:
    print(f"❌ Import failed: {e}")

print("\nTrying direct import...")
try:
    from app.crud.company import company
    print(f"✅ Direct import successful")
    print(f"Type of company: {type(company)}")
    print(f"Dir of company: {dir(company)}")
    
    if hasattr(company, 'get_by_name'):
        print("✅ get_by_name exists on company")
    else:
        print("❌ get_by_name does not exist on company")
        
except Exception as e:
    print(f"❌ Direct import failed: {e}") 