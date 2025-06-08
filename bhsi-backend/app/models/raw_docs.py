from sqlalchemy import Column, String, DateTime, Integer, LargeBinary, JSON, Text
from sqlalchemy.sql import func
from app.db.base import Base


class RawDoc(Base):
    """Landing zone for raw BOE documents with deduplication and retry logic"""
    __tablename__ = "raw_docs"
    
    raw_id = Column(String, primary_key=True, index=True)  # SHA-256(payload)
    source = Column(String, nullable=False, index=True)   # "BOE"
    fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    payload = Column(LargeBinary, nullable=False)         # raw bytes (optionally compressed)
    meta = Column(JSON)                                   # {"url":..,"pub_date":..}
    retries = Column(Integer, default=0)                  # retry counter
    status = Column(String, default=None, index=True)     # NULL | 'parsed' | 'error' | 'dlq'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RawDoc(raw_id={self.raw_id}, source={self.source}, status={self.status})>" 