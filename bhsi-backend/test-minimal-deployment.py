#!/usr/bin/env python3
"""
Test script for minimal deployment
Verifies that core functionality works without heavy ML dependencies
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_core_imports():
    """Test that core imports work"""
    print("Testing core imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import google.cloud.bigquery
        print("✅ Google Cloud BigQuery imported successfully")
    except ImportError as e:
        print(f"❌ Google Cloud BigQuery import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    return True

def test_ml_imports():
    """Test ML imports (optional)"""
    print("\nTesting ML imports (optional)...")
    
    ml_available = True
    missing_ml = []
    
    try:
        import torch
        print("✅ PyTorch available")
    except ImportError:
        print("⚠️ PyTorch not available")
        missing_ml.append('torch')
        ml_available = False
    
    try:
        import transformers
        print("✅ Transformers available")
    except ImportError:
        print("⚠️ Transformers not available")
        missing_ml.append('transformers')
        ml_available = False
    
    try:
        import spacy
        print("✅ spaCy available")
    except ImportError:
        print("⚠️ spaCy not available")
        missing_ml.append('spacy')
        ml_available = False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers available")
    except ImportError:
        print("⚠️ Sentence Transformers not available")
        missing_ml.append('sentence-transformers')
        ml_available = False
    
    try:
        import chromadb
        print("✅ ChromaDB available")
    except ImportError:
        print("⚠️ ChromaDB not available")
        missing_ml.append('chromadb')
        ml_available = False
    
    if ml_available:
        print("✅ All ML dependencies available")
    else:
        print(f"⚠️ Missing ML dependencies: {missing_ml}")
        print("⚠️ Running in minimal mode - ML features will be disabled")
    
    return ml_available

def test_app_creation():
    """Test that the FastAPI app can be created"""
    print("\nTesting app creation...")
    
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        
        # Test health endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        print(f"✅ Health endpoint returns: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing minimal deployment...")
    
    # Test core imports
    if not test_core_imports():
        print("❌ Core imports failed")
        sys.exit(1)
    
    # Test ML imports (optional)
    test_ml_imports()
    
    # Test app creation
    if not test_app_creation():
        print("❌ App creation failed")
        sys.exit(1)
    
    print("\n✅ All tests passed! Minimal deployment is ready.")

if __name__ == "__main__":
    main() 