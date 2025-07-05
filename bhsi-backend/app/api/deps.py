#!/usr/bin/env python3
"""
API Dependencies - BigQuery-only version
"""

from typing import Generator
from app.core.config import settings

# BigQuery doesn't need session management like SQLite
# All operations are async and handled by BigQuery client

def get_bigquery_client():
    """Get BigQuery client for database operations"""
    from app.services.bigquery_client_async import get_bigquery_client as get_client
    return get_client()

# Legacy function for backward compatibility (returns None for BigQuery)
def get_db():
    """Legacy function - returns None for BigQuery operations"""
    return None 