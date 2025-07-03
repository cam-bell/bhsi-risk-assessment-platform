from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.models.company import Assessment
from app.services.bigquery_writer import BigQueryWriter

logger = logging.getLogger(__name__)

# Global instance (or inject as needed)
bigquery_writer = BigQueryWriter()

class CRUDAssessment:
    def create(
        self,
        db: Session,
        *,
        obj_in: Dict[str, Any]
    ) -> Any:
        """Create a new assessment (BigQuery + SQLite fallback)"""
        row = {
            "id": obj_in["id"],
            "company_id": obj_in["company_id"],
            "user_id": obj_in["user_id"],
            "turnover": obj_in.get("turnover"),
            "shareholding": obj_in.get("shareholding"),
            "bankruptcy": obj_in.get("bankruptcy"),
            "legal": obj_in.get("legal"),
            "corruption": obj_in.get("corruption"),
            "overall": obj_in.get("overall"),
            "google_results": obj_in.get("google_results"),
            "bing_results": obj_in.get("bing_results"),
            "gov_results": obj_in.get("gov_results"),
            "news_results": obj_in.get("news_results"),
            "rss_results": obj_in.get("rss_results"),
            "analysis_summary": obj_in.get("analysis_summary"),
            "created_at": obj_in.get("created_at", datetime.utcnow().isoformat()),
            "updated_at": obj_in.get("updated_at"),
        }
        # Use centralized BigQueryWriter (buffered, async, retry)
        bigquery_writer.queue("assessment", row)
        db_obj = Assessment(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        assessment_id: str,
        obj_in: Dict[str, Any]
    ) -> Any:
        """Update an assessment (BigQuery + SQLite fallback)"""
        row = {"id": assessment_id}
        row.update(obj_in)
        # Use centralized BigQueryWriter (buffered, async, retry)
        bigquery_writer.queue("assessment", row)
        db_obj = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            db_obj.updated_at = datetime.utcnow()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return None

    def get_by_id(self, db: Session, assessment_id: str) -> Optional[Any]:
        """Get assessment by ID (BigQuery + SQLite fallback)"""
        # BigQuery reads should be handled elsewhere or via analytics pipeline
        # Here, fallback to SQLite only
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_by_company(self, db: Session, company_id: str) -> List[Any]:
        """Get all assessments for a company (BigQuery + SQLite fallback)"""
        # BigQuery reads should be handled elsewhere or via analytics pipeline
        # Here, fallback to SQLite only
        return db.query(Assessment).filter(
            Assessment.company_id == company_id
        ).all()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get multiple assessments (BigQuery + SQLite fallback)"""
        # BigQuery reads should be handled elsewhere or via analytics pipeline
        # Here, fallback to SQLite only
        return db.query(Assessment).offset(skip).limit(limit).all()

assessment = CRUDAssessment() 