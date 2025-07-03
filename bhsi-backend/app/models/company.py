from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum
import uuid


class RiskLevel(str, enum.Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


class Company(Base):
    vat = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    client_tier = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Assessment(Base):
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("company.vat"), nullable=False)
    user_id = Column(String, nullable=False)
    
    # Risk scores
    turnover = Column(Enum(RiskLevel), nullable=False)
    shareholding = Column(Enum(RiskLevel), nullable=False)
    bankruptcy = Column(Enum(RiskLevel), nullable=False)
    legal = Column(Enum(RiskLevel), nullable=False)
    corruption = Column(Enum(RiskLevel), nullable=False)
    overall = Column(Enum(RiskLevel), nullable=False)
    
    # Search results
    google_results = Column(String)  # JSON string
    bing_results = Column(String)    # JSON string
    gov_results = Column(String)     # JSON string
    news_results = Column(String)    # JSON string
    rss_results = Column(String)    # JSON string for RSS results
    
    # Analysis
    analysis_summary = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 