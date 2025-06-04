from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CompanyCreate) -> Company:
        db_obj = Company(
            name=obj_in.name,
            description=obj_in.description
        )
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


company = CRUDCompany(Company) 