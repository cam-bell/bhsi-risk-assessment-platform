#!/usr/bin/env python3
"""
Test real search data flow to BigQuery.
This script runs a real search for Banco Santander and saves results to BigQuery.
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.bigquery_database_integration import BigQueryDatabaseIntegrationService
from app.core.config import settings
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator

async def main():
    """Test real search to BigQuery flow"""
    
    # Enable BigQuery
    os.environ["USE_BIGQUERY"] = "1"
    
    print("🔧 Setting up real search to BigQuery test...")
    print(f"BigQuery enabled: {settings.is_bigquery_enabled()}")
    print(f"Project: {settings.BIGQUERY_PROJECT}")
    print(f"Dataset: {settings.BIGQUERY_DATASET}")
    print(f"Table: {settings.BIGQUERY_RAW_DOCS_TABLE}")
    
    integration_service = BigQueryDatabaseIntegrationService()
    
    try:
        # Search parameters
        company_name = "BBVA"
        days_back = 30
        search_date = datetime.now() - timedelta(days=days_back)
        
        print(f"\n🔍 Running real search for '{company_name}' ({days_back} days back)...")
        print(f"Search date: {search_date.strftime('%Y-%m-%d')}")
        
        # Create search orchestrator
        orchestrator = StreamlinedSearchOrchestrator()
        
        # Run the search
        search_results = await orchestrator.search_all(
            query=company_name,
            days_back=days_back
        )
        
        print(f"\n📊 Search results summary:")
        total_articles = 0
        for source, data in search_results.items():
            if isinstance(data, dict):
                if 'articles' in data:
                    count = len(data['articles'])
                    total_articles += count
                    print(f"   {source}: {count} articles")
                elif 'results' in data:
                    count = len(data['results'])
                    total_articles += count
                    print(f"   {source}: {count} results")
                elif 'financial_data' in data:
                    count = len(data['financial_data'])
                    total_articles += count
                    print(f"   {source}: {count} financial records")
        
        print(f"   Total: {total_articles} items")
        
        if total_articles == 0:
            print("❌ No search results found. Check your API keys and search parameters.")
            return
        
        # Save to BigQuery
        print(f"\n💾 Saving search results to BigQuery...")
        save_stats = await integration_service.save_search_results(
            search_results=search_results,
            query=company_name,
            company_name=company_name
        )
        
        print(f"\n✅ Save results:")
        print(f"   Raw docs saved: {save_stats['raw_docs_saved']}")
        print(f"   Events created: {save_stats['events_created']}")
        print(f"   Total processed: {save_stats['total_processed']}")
        if save_stats['errors']:
            print(f"   Errors: {len(save_stats['errors'])}")
            for error in save_stats['errors'][:3]:  # Show first 3 errors
                print(f"     - {error}")
        
        # Verify in BigQuery
        print(f"\n🔍 Verifying data in BigQuery...")
        await verify_bigquery_data(company_name)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def verify_bigquery_data(company_name):
    """Verify that data was saved to BigQuery"""
    try:
        import subprocess
        
        # Query BigQuery for recent data
        query = f"""
        SELECT 
            source,
            COUNT(*) as count,
            MIN(fetched_at) as earliest,
            MAX(fetched_at) as latest
        FROM `{settings.BIGQUERY_PROJECT}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_RAW_DOCS_TABLE}`
        WHERE DATE(fetched_at) = CURRENT_DATE()
        GROUP BY source
        ORDER BY count DESC
        """
        
        print(f"   Running BigQuery verification query...")
        result = subprocess.run(
            ['bq', 'query', '--use_legacy_sql=false', '--format=prettyjson', query],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ BigQuery query successful!")
            print(f"   📊 Today's data summary:")
            
            # Parse the JSON output
            import json
            data = json.loads(result.stdout)
            
            if data:
                for row in data:
                    source = row['source']
                    count = row['count']
                    earliest = row['earliest']
                    latest = row['latest']
                    print(f"     {source}: {count} records ({earliest} to {latest})")
            else:
                print(f"     No data found for today")
        else:
            print(f"   ❌ BigQuery query failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 