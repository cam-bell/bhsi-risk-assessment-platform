#!/usr/bin/env python3
"""
Backend Reality Check - Test what's actually working
"""

import sys
import traceback
sys.path.insert(0, '.')

def test_basic_imports():
    """Test if basic imports work"""
    print("🧪 TESTING BASIC IMPORTS")
    print("=" * 50)
    
    tests = [
        ("Config", lambda: __import__('app.core.config', fromlist=['settings'])),
        ("FastAPI", lambda: __import__('fastapi')),
        ("SQLAlchemy", lambda: __import__('sqlalchemy')),
        ("Requests", lambda: __import__('requests')),
        ("FeedParser", lambda: __import__('feedparser')),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name} - OK")
        except Exception as e:
            print(f"❌ {name} - FAILED: {e}")

def test_app_creation():
    """Test if we can create the FastAPI app"""
    print("\n🚀 TESTING APP CREATION")
    print("=" * 50)
    
    try:
        from fastapi import FastAPI
        from app.api.v1.router import api_router
        
        app = FastAPI(title="Test App")
        app.include_router(api_router, prefix="/api/v1")
        
        print(f"✅ App created successfully")
        print(f"📋 Total routes: {len(app.routes)}")
        
        # List actual endpoints
        from fastapi.routing import APIRoute
        print(f"\n📍 ACTUAL ENDPOINTS:")
        for route in app.routes:
            if isinstance(route, APIRoute):
                methods = ', '.join(route.methods)
                print(f"  {methods:12} {route.path}")
                
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def test_cloud_services():
    """Test if cloud services are reachable"""
    print("\n☁️ TESTING CLOUD SERVICES")
    print("=" * 50)
    
    import requests
    
    services = [
        ("Gemini Service", "https://gemini-service-185303190462.europe-west1.run.app/health"),
        ("Embedder Service", "https://embedder-service-185303190462.europe-west1.run.app/health"),
        ("Vector Search", "https://vector-search-185303190462.europe-west1.run.app/health"),
        ("BigQuery Analytics", "https://bigquery-analytics-185303190462.europe-west1.run.app/health"),
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} - ONLINE ({response.status_code})")
                try:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    print(f"   Status: {status}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"⚠️ {name} - HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"❌ {name} - TIMEOUT")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} - CONNECTION ERROR")
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")

def test_database():
    """Test database connectivity"""
    print("\n🗄️ TESTING DATABASE")
    print("=" * 50)
    
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        
        print(f"Database URL: {settings.DATABASE_URL}")
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection - OK")
            
            # Check if tables exist
            tables_query = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = conn.execute(tables_query).fetchall()
            print(f"📊 Tables found: {[t[0] for t in tables]}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def test_data_sources():
    """Test actual data source connectivity"""
    print("\n📡 TESTING DATA SOURCES")
    print("=" * 50)
    
    # Test BOE
    try:
        import requests
        response = requests.get("https://www.boe.es/boe/dias/2024/12/20/", timeout=10)
        if response.status_code == 200:
            print("✅ BOE API - REACHABLE")
        else:
            print(f"⚠️ BOE API - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ BOE API - ERROR: {e}")
    
    # Test NewsAPI
    try:
        from app.core.config import settings
        if settings.NEWS_API_KEY:
            news_url = f"https://newsapi.org/v2/everything?q=test&apiKey={settings.NEWS_API_KEY}&pageSize=1"
            response = requests.get(news_url, timeout=10)
            if response.status_code == 200:
                print("✅ NewsAPI - CONNECTED")
            else:
                print(f"⚠️ NewsAPI - HTTP {response.status_code}")
        else:
            print("⚠️ NewsAPI - NO API KEY")
    except Exception as e:
        print(f"❌ NewsAPI - ERROR: {e}")

if __name__ == "__main__":
    print("🔍 BHSI BACKEND REALITY CHECK")
    print("=" * 60)
    
    test_basic_imports()
    
    if test_app_creation():
        test_cloud_services()
        test_database()
        test_data_sources()
    
    print("\n🎯 REALITY CHECK COMPLETE!")
    print("=" * 60) 