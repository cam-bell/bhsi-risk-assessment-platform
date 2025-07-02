#!/usr/bin/env python3
"""
Script to test real BigQuery save with Banco Santander data.
This will actually save data to the BigQuery raw_docs table.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.database_integration import DatabaseIntegrationService
from app.db.session import SessionLocal
from app.core.config import settings

def main():
    """Test real BigQuery save with Banco Santander data"""
    
    # Enable BigQuery
    os.environ["USE_BIGQUERY"] = "1"
    
    print("🔧 Setting up BigQuery test...")
    print(f"BigQuery enabled: {settings.is_bigquery_enabled()}")
    print(f"Project: {settings.BIGQUERY_PROJECT}")
    print(f"Dataset: {settings.BIGQUERY_DATASET}")
    print(f"Table: {settings.BIGQUERY_RAW_DOCS_TABLE}")
    
    # Create database session
    db = SessionLocal()
    integration_service = DatabaseIntegrationService()
    
    try:
        # Create test payload for Banco Santander (30 days back)
        test_date = datetime.now() - timedelta(days=30)
        
        payload_data = {
            "title": "Banco Santander Test Article",
            "description": "Test article about Banco Santander for BigQuery integration testing",
            "content": "This is a test article content for Banco Santander. Testing BigQuery save functionality.",
            "publishedAt": test_date.isoformat(),
            "url": "https://example.com/test-santander-article",
            "source": "Test Source"
        }
        
        payload_bytes = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
        
        test_payload = {
            "source": "Banco Santander",
            "payload": payload_bytes,
            "meta": {
                "company": "Banco Santander",
                "test_type": "real_bigquery_save",
                "test_date": datetime.now().isoformat(),
                "original_url": payload_data["url"],
                "search_query": "Banco Santander 30 days"
            }
        }
        
        print("\n📝 Test payload created:")
        print(f"   Source: {test_payload['source']}")
        print(f"   Payload size: {len(test_payload['payload'])} bytes")
        print(f"   Meta: {test_payload['meta']}")
        
        # Save to BigQuery
        print("\n💾 Saving to BigQuery...")
        raw_doc, is_new = integration_service.raw_docs_crud.create_with_dedup(
            db, **test_payload
        )
        
        if is_new:
            print("✅ SUCCESS: New document saved!")
            # Handle both dict (BigQuery) and SQLAlchemy model (SQLite)
            if hasattr(raw_doc, 'raw_id'):
                # SQLAlchemy model
                print(f"   Raw ID: {raw_doc.raw_id}")
                print(f"   Source: {raw_doc.source}")
                print(f"   Fetched at: {raw_doc.fetched_at}")
            else:
                # Dict (BigQuery)
                print(f"   Raw ID: {raw_doc.get('raw_id', 'N/A')}")
                print(f"   Source: {raw_doc.get('source', 'N/A')}")
                print(f"   Fetched at: {raw_doc.get('fetched_at', 'N/A')}")
        else:
            print("ℹ️  Document already exists (deduplication working)")
            if hasattr(raw_doc, 'raw_id'):
                print(f"   Raw ID: {raw_doc.raw_id}")
            else:
                print(f"   Raw ID: {raw_doc.get('raw_id', 'N/A')}")
        
        print("\n🔍 Check your BigQuery console:")
        print("   https://console.cloud.google.com/bigquery")
        print(f"   Project: {settings.BIGQUERY_PROJECT}")
        print(f"   Dataset: {settings.BIGQUERY_DATASET}")
        print(f"   Table: {settings.BIGQUERY_RAW_DOCS_TABLE}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main() 