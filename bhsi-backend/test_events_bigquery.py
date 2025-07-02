#!/usr/bin/env python3
"""
Test script to verify events are being written to BigQuery
"""

from datetime import date

from app.db.session import SessionLocal
from app.crud.events import events
from app.core.config import settings


def test_event_creation():
    """Test creating an event and verify it goes to BigQuery"""
    print("🧪 Testing event creation with BigQuery...")
    
    db = SessionLocal()
    try:
        # Test data
        test_raw_id = "test_raw_123"
        test_source = "TEST_SOURCE"
        test_title = "Test Event Title"
        test_text = "This is a test event for BigQuery verification"
        test_section = "TEST_SECTION"
        test_pub_date = date(2024, 1, 15)
        test_url = "https://example.com/test"
        
        print(f"📝 Creating event with ID: {test_source}:{test_raw_id}")
        
        # Create event
        event = events.create_from_raw(
            db=db,
            raw_id=test_raw_id,
            source=test_source,
            title=test_title,
            text=test_text,
            section=test_section,
            pub_date=test_pub_date,
            url=test_url
        )
        
        print(f"✅ Event created: {event}")
        
        # Verify in BigQuery
        if settings.is_bigquery_enabled():
            try:
                from google.cloud import bigquery
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE event_id = '{test_source}:{test_raw_id}' "
                    f"LIMIT 1"
                )
                
                job = client.query(query)
                rows = list(job)
                
                if rows:
                    row = dict(rows[0])
                    print("🎯 Event found in BigQuery:")
                    print(f"   Event ID: {row.get('event_id')}")
                    print(f"   Title: {row.get('title')}")
                    print(f"   Source: {row.get('source')}")
                    print(f"   Created: {row.get('created_at')}")
                    print(f"   Risk Label: {row.get('risk_label')}")
                    return True
                else:
                    print("❌ Event not found in BigQuery")
                    return False
                    
            except Exception as e:
                print(f"❌ Error querying BigQuery: {e}")
                return False
        else:
            print("ℹ️ BigQuery not enabled, event saved to SQLite")
            return True
            
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return False
    finally:
        db.close()


def test_event_retrieval():
    """Test retrieving events from BigQuery"""
    print("\n🔍 Testing event retrieval from BigQuery...")
    
    if not settings.is_bigquery_enabled():
        print("ℹ️ BigQuery not enabled, skipping retrieval test")
        return True
    
    try:
        from google.cloud import bigquery
        client = bigquery.Client()
        table_id = f"{settings.BIGQUERY_PROJECT}.{settings.BIGQUERY_DATASET}.events"
        
        # Get recent events
        query = f"""
        SELECT event_id, title, source, created_at, risk_label
        FROM `{table_id}` 
        ORDER BY created_at DESC 
        LIMIT 5
        """
        
        job = client.query(query)
        rows = list(job)
        
        print(f"📊 Found {len(rows)} recent events in BigQuery:")
        for row in rows:
            row_dict = dict(row)
            print(f"   - {row_dict.get('event_id')}: {row_dict.get('title')} ({row_dict.get('source')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error retrieving events: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Events BigQuery Integration")
    print("=" * 50)
    
    # Test 1: Create event
    success1 = test_event_creation()
    
    # Test 2: Retrieve events
    success2 = test_event_retrieval()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed! Events are working with BigQuery.")
    else:
        print("❌ Some tests failed. Check the output above.") 