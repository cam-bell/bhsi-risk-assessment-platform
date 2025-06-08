#!/usr/bin/env python3
"""
Initialize the queue database with raw_docs and events tables
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.db.base import Base
from app.models.raw_docs import RawDoc
from app.models.events import Event

def init_queue_database():
    """Initialize the queue database"""
    # Create the database file
    db_path = Path(__file__).parent.parent / "app" / "db" / "queue.db"
    db_path.parent.mkdir(exist_ok=True)
    
    # Create engine
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    print("🗄️ Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Queue database initialized successfully!")
    print(f"📁 Database location: {db_path}")
    print("\n📋 Created tables:")
    print("  - raw_docs (landing zone)")
    print("  - events (canonical documents)")
    print("  - company (existing)")
    print("  - assessment (existing)")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Verified tables: {tables}")
    
    return str(db_path)

if __name__ == "__main__":
    init_queue_database() 