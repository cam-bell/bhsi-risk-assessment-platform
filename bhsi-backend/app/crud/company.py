from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from pydantic import BaseModel

# Import BigQuery client
try:
    from google.cloud import bigquery  # type: ignore
except ImportError:
    bigquery = None
from app.core.config import settings
import logging
logger = logging.getLogger(__name__)


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
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError("BigQuery is enabled but google-cloud-bigquery is not installed.")
            try:
                client = bigquery.Client()
                table_id = f"{settings.BIGQUERY_PROJECT}.{settings.BIGQUERY_DATASET}.companies"
                row = {
                    "vat": obj_in.get("vat"),
                    "company_name": obj_in.get("company_name") or obj_in.get("name"),
                    "sector": obj_in.get("sector"),
                    "client_tier": obj_in.get("client_tier"),
                    "created_at": obj_in.get("created_at"),
                }
                errors = client.insert_rows_json(table_id, [row])
                if errors:
                    logger.error(f"BigQuery insert errors: {errors}. Falling back to SQLite.")
                    raise Exception(f"BigQuery insert errors: {errors}")
                return row
            except Exception as e:
                logger.error(f"BigQuery create failed: {e}. Falling back to SQLite.")
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
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError("BigQuery is enabled but google-cloud-bigquery is not installed.")
            try:
                client = bigquery.Client()
                table_id = f"{settings.BIGQUERY_PROJECT}.{settings.BIGQUERY_DATASET}.companies"
                set_clauses = []
                query_parameters = []
                for key, value in obj_in.items():
                    set_clauses.append(f"{key} = @{key}")
                    param_type = "STRING" if key != "created_at" else "TIMESTAMP"
                    query_parameters.append(
                        bigquery.ScalarQueryParameter(key, param_type, value)
                    )
                set_clause = ", ".join(set_clauses)
                query = (
                    f"UPDATE `{table_id}` SET {set_clause}, "
                    f"updated_at = CURRENT_TIMESTAMP() "
                    f"WHERE vat = @vat"
                )
                query_parameters.append(
                    bigquery.ScalarQueryParameter("vat", "STRING", db_obj.vat)
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=query_parameters
                    )
                )
                job.result()
                return True
            except Exception as e:
                logger.error(f"BigQuery update failed: {e}. Falling back to SQLite.")
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == id).first()


company = CRUDCompany(Company) 