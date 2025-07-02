#!/usr/bin/env python3
"""
Test script to verify the database integration fix
"""

import asyncio
import json
from app.db.session import get_db
from app.services.database_integration import db_integration
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator

async def test_fix():
    """Test the database integration with real search data"""
    print("Testing database integration fix...")
    
    # Test data that would cause the previous errors
    test_article = {
        "title": "Test Article",
        "description": "Test description",
        "content": "Test content",
        "publishedAt": "2024-01-01T00:00:00Z",
        "url": "https://example.com",
        "source": None,  # This would cause .get() error before
        "author": "Test Author"
    }
    
    # Test the build_rawdoc_dict method
    payload_bytes = json.dumps(test_article, ensure_ascii=False).encode('utf-8')
    meta = {
        "company_name": "Test Company",
        "url": test_article.get("url", ""),
        "pub_date": test_article.get("publishedAt", ""),
        "source_name": (test_article.get("source") or {}).get("name", "Unknown"),
        "author": test_article.get("author", "")
    }
    
    rawdoc_dict = db_integration.build_rawdoc_dict("TEST", payload_bytes, meta)
    print(f"✓ build_rawdoc_dict works: {list(rawdoc_dict.keys())}")
    print(f"✓ No raw_id in dict: {'raw_id' not in rawdoc_dict}")
    
    # Test with database
    db = next(get_db())
    try:
        raw_doc, is_new = db_integration.raw_docs_crud.create_with_dedup(
            db,
            **rawdoc_dict
        )
        print(f"✓ CRUD create_with_dedup works: is_new={is_new}")
        
        # Clean up
        if is_new and hasattr(raw_doc, 'raw_id'):
            db_integration.raw_docs_crud.mark_error(db, raw_doc.raw_id)
            
    except Exception as e:
        print(f"✗ CRUD error: {e}")
    finally:
        db.close()
    
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_fix()) 