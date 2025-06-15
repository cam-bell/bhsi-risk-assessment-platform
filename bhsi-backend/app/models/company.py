from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class RiskLevel(str, enum.Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


class Company(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    vat = Column(String, index=True)
    vat_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Assessment(Base):
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
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
    
    # Analysis
    analysis_summary = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 