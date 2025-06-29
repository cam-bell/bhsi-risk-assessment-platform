from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from pydantic import BaseModel


class CompanyAnalysisCreate(BaseModel):
    name: str
    description: Optional[str] = None
    turnover: Optional[str] = None
    shareholding: Optional[str] = None
    bankruptcy: Optional[str] = None
    legal: Optional[str] = None
    corruption: Optional[str] = None
    overall: Optional[str] = None
    analysis_summary: Optional[str] = None
    google_results: Optional[str] = None
    bing_results: Optional[str] = None
    gov_results: Optional[str] = None
    news_results: Optional[str] = None


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> Company:
        db_obj = Company(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Company,
        obj_in: Dict[str, Any]
    ) -> Company:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == id).first()


company = CRUDCompany(Company) 