from sqlalchemy import Column, String, DateTime, Date, Text, Float, Boolean
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class RiskLabel(str, enum.Enum):
    """D&O Insurance Risk Labels"""
    HIGH_LEGAL = "High-Legal"
    MEDIUM_REG = "Medium-Reg"
    LOW_OTHER = "Low-Other"
    UNKNOWN = "Unknown"


class Event(Base):
    """Canonical normalized BOE events for analysis"""
    __tablename__ = "events"
    
    event_id = Column(String, primary_key=True, index=True)  # source:raw_id
    title = Column(Text)                                     # Document title
    text = Column(Text)                                      # Full document text
    source = Column(String, nullable=False, index=True)      # "BOE"
    section = Column(String, index=True)                     # BOE section code
    pub_date = Column(Date, index=True)                      # Publication date
    url = Column(String)                                     # Original document URL
    
    # Embedding status
    embedding = Column(String, default=None, index=True)     # 'vectorised' marker
    embedding_model = Column(String, default=None)           # Model used for embedding
    
    # Risk classification
    risk_label = Column(String, default=None, index=True)    # High-Legal/Medium-Reg/Low-Other/Unknown
    rationale = Column(Text, default=None)                   # Classification reasoning
    confidence = Column(Float, default=None)                 # Classification confidence (0.0-1.0)
    classifier_ts = Column(DateTime(timezone=True), default=None)  # When classified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Alert status
    alerted = Column(Boolean, default=None)
    
    def __repr__(self):
        return f"<Event(event_id={self.event_id}, risk_label={self.risk_label}, title={self.title[:50]}...)>" 