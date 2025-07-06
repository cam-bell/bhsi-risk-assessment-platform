from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class CompanyBase(BaseModel):
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    sector: Optional[str] = Field(None, description="Company sector")
    client_tier: Optional[str] = Field(None, description="Client tier")
    vat_number: Optional[str] = Field(
        None, description="Company VAT number (unique)")


class CompanyCreate(CompanyBase):
    # Search parameters for comprehensive data collection
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    days_back: Optional[int] = Field(30, description="Days to look back")
    include_boe: bool = Field(True, description="Include BOE search")
    include_news: bool = Field(True, description="Include NewsAPI search")
    include_rss: bool = Field(True, description="Include RSS news sources")


class CompanyUpdate(CompanyBase):
    pass


class CompanyInDBBase(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class CompanyResponse(CompanyInDBBase):
    pass


class RiskLevel(str, Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


class AssessmentBase(BaseModel):
    company_id: str = Field(..., description="Company ID (FK)")
    user_id: str
    turnover: RiskLevel
    shareholding: RiskLevel
    bankruptcy: RiskLevel
    legal: RiskLevel
    corruption: RiskLevel
    overall: RiskLevel
    google_results: Optional[str] = None
    bing_results: Optional[str] = None
    gov_results: Optional[str] = None
    news_results: Optional[str] = None
    rss_results: Optional[str] = None
    analysis_summary: Optional[str] = None


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentInDBBase(AssessmentBase):
    id: str
    created_at: datetime
    updated_at: datetime


class AssessmentResponse(AssessmentInDBBase):
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
    rss_results: Optional[str] = None
    analysis_summary: Optional[str] = None


class CompanyAnalysis(BaseModel):
    risk_scores: RiskScores
    processed_results: ProcessedResults
    analysis_summary: Optional[dict] = None 