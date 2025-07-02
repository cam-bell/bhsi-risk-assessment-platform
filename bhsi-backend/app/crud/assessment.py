from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.core.config import settings
from app.models.company import Assessment

# Import BigQuery client
try:
    from google.cloud import bigquery  # type: ignore
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)


class CRUDAssessment:
    def create(
        self,
        db: Session,
        *,
        obj_in: Dict[str, Any]
    ) -> Any:
        """Create a new assessment (BigQuery + SQLite fallback)"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.assessment"
                )
                # Insert new
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
                    "analysis_summary": obj_in.get("analysis_summary"),
                    "created_at": obj_in.get("created_at", datetime.utcnow().isoformat()),
                    "updated_at": obj_in.get("updated_at"),
                }
                errors = client.insert_rows_json(table_id, [row])
                if errors:
                    logger.error(
                        f"BigQuery insert errors: {errors}. "
                        f"Falling back to SQLite."
                    )
                    raise Exception(f"BigQuery insert errors: {errors}")
                return row
            except Exception as e:
                logger.error(f"BigQuery create failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
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
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.assessment"
                )
                set_clauses = []
                query_parameters = []
                for key, value in obj_in.items():
                    set_clauses.append(f"{key} = @{key}")
                    param_type = "STRING" if not key.endswith("_at") else "TIMESTAMP"
                    query_parameters.append(
                        bigquery.ScalarQueryParameter(key, param_type, value)
                    )
                set_clause = ", ".join(set_clauses)
                query = (
                    f"UPDATE `{table_id}` SET {set_clause}, "
                    f"updated_at = CURRENT_TIMESTAMP() "
                    f"WHERE id = @assessment_id"
                )
                query_parameters.append(
                    bigquery.ScalarQueryParameter(
                        "assessment_id", "STRING", assessment_id
                    )
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
        # Fallback to SQLite
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
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.assessment"
                )
                query = (
                    f"SELECT * FROM `{table_id}` WHERE id = @assessment_id LIMIT 1"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "assessment_id", "STRING", assessment_id
                            )
                        ]
                    )
                )
                rows = list(job)
                if rows:
                    return dict(rows[0])
            except Exception as e:
                logger.error(f"BigQuery get_by_id failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_by_company(self, db: Session, company_id: str) -> List[Any]:
        """Get all assessments for a company (BigQuery + SQLite fallback)"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.assessment"
                )
                query = (
                    f"SELECT * FROM `{table_id}` WHERE company_id = @company_id"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "company_id", "STRING", company_id
                            )
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery get_by_company failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return db.query(Assessment).filter(Assessment.company_id == company_id).all()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get multiple assessments (BigQuery + SQLite fallback)"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}.assessment"
                )
                query = (
                    f"SELECT * FROM `{table_id}` LIMIT @limit OFFSET @skip"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter("limit", "INT64", limit),
                            bigquery.ScalarQueryParameter("skip", "INT64", skip)
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery get_multi failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return db.query(Assessment).offset(skip).limit(limit).all()

assessment = CRUDAssessment() 