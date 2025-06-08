from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CompanyBase(BaseModel):
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    turnover: Optional[str] = None
    shareholding: Optional[str] = None
    bankruptcy: Optional[str] = None
    legal: Optional[str] = None
    corruption: Optional[str] = None
    overall: Optional[str] = None
    google_results: Optional[str] = None
    bing_results: Optional[str] = None
    gov_results: Optional[str] = None
    news_results: Optional[str] = None
    analysis_summary: Optional[str] = None


class CompanyInDBBase(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    turnover: Optional[str] = None
    shareholding: Optional[str] = None
    bankruptcy: Optional[str] = None
    legal: Optional[str] = None
    corruption: Optional[str] = None
    overall: Optional[str] = None
    google_results: Optional[str] = None
    bing_results: Optional[str] = None
    gov_results: Optional[str] = None
    news_results: Optional[str] = None
    analysis_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CompanyResponse(CompanyInDBBase):
    pass


class RiskScores(BaseModel):
    turnover: str
    shareholding: str
    bankruptcy: str
    legal: str
    corruption: str
    overall: str


class ProcessedResults(BaseModel):
    google_results: Optional[str] = None
    bing_results: Optional[str] = None
    gov_results: Optional[str] = None
    news_results: Optional[str] = None
    analysis_summary: Optional[str] = None


class CompanyAnalysis(BaseModel):
    risk_scores: RiskScores
    processed_results: ProcessedResults
    analysis_summary: Dict[str, Any] 