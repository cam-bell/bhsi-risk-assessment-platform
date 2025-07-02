from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session  # noqa: F401
from sqlalchemy import func  # noqa: F401
import hashlib
from datetime import datetime
import base64
import json
import logging

from app.models.raw_docs import RawDoc
from app.core.config import settings

# Import BigQuery client
try:
    from google.cloud import bigquery  # type: ignore
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)

class CRUDRawDoc:
    def generate_raw_id(self, payload: bytes) -> str:
        """Generate SHA-256 hash for deduplication"""
        return hashlib.sha256(payload).hexdigest()

    def create_with_dedup(
        self, 
        db: Session = None, 
        *,
        source: str,
        payload: bytes,
        meta: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[Any], bool]:
        """Create raw doc with deduplication (INSERT OR IGNORE)
        Returns:
            tuple: (RawDoc, is_new) where is_new=True if document was just created
        """
        raw_id = self.generate_raw_id(payload)
        meta = meta or {}
        fetched_at = datetime.utcnow()

        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                # Check for existing
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE raw_id = @raw_id LIMIT 1"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "raw_id", "STRING", raw_id
                            )
                        ]
                    )
                )
                rows = list(job)
                if rows:
                    return dict(rows[0]), False
                # Insert new
                row = {
                    "raw_id": raw_id,
                    "source": source,
                    "payload": base64.b64encode(payload).decode("utf-8"),
                    "meta": json.dumps(meta) if meta else None,
                    "fetched_at": fetched_at.isoformat(),
                    "retries": 0,
                    "status": None
                }
                errors = client.insert_rows_json(table_id, [row])
                if errors:
                    logger.error(
                        f"BigQuery insert errors: {errors}. Falling back to SQLite."
                    )
                    raise Exception(
                        f"BigQuery insert errors: {errors}"
                    )
                return row, True
            except Exception as e:
                logger.error(f"BigQuery operation failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            existing = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            if existing:
                return existing, False  # Existing document, not new
            db_obj = RawDoc(
                raw_id=raw_id,
                source=source,
                payload=payload,
                meta=meta,
                fetched_at=fetched_at
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj, True  # New document created
        except Exception as e:
            logger.error(f"SQLite operation failed: {e}")
            db.rollback()
            existing_after_rollback = (
                db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            )
            return existing_after_rollback, False

    def get_unparsed(self, db: Session = None, limit: int = 100) -> List[Any]:
        """Get unparsed documents (status IS NULL)"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE status IS NULL LIMIT @limit"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "limit", "INT64", limit
                            )
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery get_unparsed failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            return (
                db.query(RawDoc)
                .filter(RawDoc.status.is_(None))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"SQLite get_unparsed failed: {e}")
            return []

    def mark_parsed(self, db: Session, raw_id: str) -> bool:
        """Mark document as parsed"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                query = (
                    f"UPDATE `{table_id}` SET status = 'parsed', updated_at = CURRENT_TIMESTAMP() "
                    f"WHERE raw_id = @raw_id"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "raw_id", "STRING", raw_id
                            )
                        ]
                    )
                )
                job.result()
                return True
            except Exception as e:
                logger.error(f"BigQuery mark_parsed failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            if db_obj:
                db_obj.status = "parsed"
                db_obj.updated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"SQLite mark_parsed failed: {e}")
            db.rollback()
            return False

    def mark_error(self, db: Session, raw_id: str) -> bool:
        """Mark document as error and increment retry count"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                # Increment retries and set status
                query = (
                    f"UPDATE `{table_id}` SET retries = IFNULL(retries, 0) + 1, "
                    f"status = CASE WHEN IFNULL(retries, 0) + 1 < 5 THEN 'error' ELSE 'dlq' END, "
                    f"updated_at = CURRENT_TIMESTAMP() WHERE raw_id = @raw_id"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "raw_id", "STRING", raw_id
                            )
                        ]
                    )
                )
                job.result()
                return True
            except Exception as e:
                logger.error(f"BigQuery mark_error failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            db_obj = db.query(RawDoc).filter(RawDoc.raw_id == raw_id).first()
            if db_obj:
                db_obj.retries += 1
                db_obj.status = "error" if db_obj.retries < 5 else "dlq"
                db_obj.updated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"SQLite mark_error failed: {e}")
            db.rollback()
            return False

    def get_stats(self, db: Session) -> Dict[str, int]:
        """Get processing statistics"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                stats = {}
                for status in [None, "parsed", "error", "dlq"]:
                    if status is None:
                        query = (
                            f"SELECT COUNT(*) as count FROM `{table_id}` "
                            f"WHERE status IS NULL"
                        )
                        key = "unparsed"
                    else:
                        query = (
                            f"SELECT COUNT(*) as count FROM `{table_id}` "
                            f"WHERE status = '{status}'"
                        )
                        key = status if status else "unparsed"
                    job = client.query(query)
                    row = list(job)[0]
                    stats[key] = row["count"]
                # Total
                query = f"SELECT COUNT(*) as count FROM `{table_id}`"
                job = client.query(query)
                row = list(job)[0]
                stats["total"] = row["count"]
                return stats
            except Exception as e:
                logger.error(f"BigQuery get_stats failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            stats = {}
            stats["total"] = db.query(RawDoc).count()
            stats["unparsed"] = db.query(RawDoc).filter(RawDoc.status.is_(None)).count()
            stats["parsed"] = db.query(RawDoc).filter(RawDoc.status == "parsed").count()
            stats["errors"] = db.query(RawDoc).filter(RawDoc.status == "error").count()
            stats["dlq"] = db.query(RawDoc).filter(RawDoc.status == "dlq").count()
            return stats
        except Exception as e:
            logger.error(f"SQLite get_stats failed: {e}")
            return {}

    def vacuum_old(self, db: Session, days_old: int = 30) -> int:
        """Delete old parsed documents"""
        if settings.is_bigquery_enabled():
            if bigquery is None:
                logger.error("BigQuery is enabled but google-cloud-bigquery is not installed.")
                raise RuntimeError(
                    "BigQuery is enabled but google-cloud-bigquery is not installed."
                )
            try:
                client = bigquery.Client()
                table_id = (
                    f"{settings.BIGQUERY_PROJECT}."
                    f"{settings.BIGQUERY_DATASET}."
                    f"{settings.BIGQUERY_RAW_DOCS_TABLE}"
                )
                from datetime import timedelta
                cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).date().isoformat()
                query = (
                    f"DELETE FROM `{table_id}` WHERE status = 'parsed' AND DATE(fetched_at) < @cutoff_date"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "cutoff_date", "DATE", cutoff_date
                            )
                        ]
                    )
                )
                result = job.result()
                return result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
            except Exception as e:
                logger.error(f"BigQuery vacuum_old failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        try:
            cutoff_date = datetime.utcnow().date()
            from datetime import timedelta
            cutoff_date = cutoff_date - timedelta(days=days_old)
            deleted = (
                db.query(RawDoc)
                .filter(RawDoc.status == "parsed")
                .filter(func.date(RawDoc.fetched_at) < cutoff_date)
                .delete()
            )
            db.commit()
            return deleted
        except Exception as e:
            logger.error(f"SQLite vacuum_old failed: {e}")
            db.rollback()
            return 0


def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


raw_docs = CRUDRawDoc() 