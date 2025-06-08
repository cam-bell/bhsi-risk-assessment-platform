#!/usr/bin/env python3
"""
Database Initialization Script
Creates all tables for the BOE Risk Monitoring System
"""

from sqlalchemy import create_engine
from app.db.session import engine
from app.db.base import Base

# Import all models to register them with Base
from app.models.user import User
from app.models.company import Company, Assessment
from app.models.raw_docs import RawDoc
from app.models.events import Event


def init_database():
    """Initialize database by creating all tables"""
    print("🏗️ Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {tables}")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise


if __name__ == "__main__":
    init_database() 