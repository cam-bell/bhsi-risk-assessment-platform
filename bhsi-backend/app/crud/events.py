from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
import logging
from app.core.config import settings

from app.models.events import Event, RiskLabel

# Import BigQuery client
try:
    from google.cloud import bigquery  # type: ignore
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)

class CRUDEvent:
    def create_from_raw(
        self,
        db: Session,
        *,
        raw_id: str,
        source: str,
        title: str,
        text: str,
        section: Optional[str] = None,
        pub_date: Optional[date] = None,
        url: Optional[str] = None
    ) -> Any:
        """Create event from raw document data"""
        event_id = f"{source}:{raw_id}"
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                # Check for existing
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE event_id = @event_id LIMIT 1"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "event_id", "STRING", event_id
                            )
                        ]
                    )
                )
                rows = list(job)
                if rows:
                    return dict(rows[0])
                # Insert new
                row = {
                    "event_id": event_id,
                    "title": title,
                    "text": text,
                    "source": source,
                    "section": section,
                    "pub_date": pub_date.isoformat() if pub_date else None,
                    "url": url,
                    "vat": None,
                    "embedding_id": None,
                    "embedding_model": None,
                    "risk_label": None,
                    "rationale": None,
                    "confidence": None,
                    "classifier_ts": None,
                    "alerted": False,
                    "alerted_at": None,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": None
                }
                errors = client.insert_rows_json(table_id, [row])
                if errors:
                    logger.error(f"BigQuery insert errors: {errors}. Falling back to SQLite.")
                    raise Exception(f"BigQuery insert errors: {errors}")
                return row
            except Exception as e:
                logger.error(f"BigQuery create_from_raw failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        existing = db.query(Event).filter(Event.event_id == event_id).first()
        if existing:
            return existing
        db_obj = Event(
            event_id=event_id,
            title=title,
            text=text,
            source=source,
            section=section,
            pub_date=pub_date,
            url=url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_unembedded(self, db: Session, limit: int = 100) -> List[Any]:
        """Get events that need embedding (embedding IS NULL)"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE embedding IS NULL LIMIT @limit"
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
                logger.error(f"BigQuery get_unembedded failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return (
            db.query(Event)
            .filter(Event.embedding.is_(None))
            .limit(limit)
            .all()
        )

    def mark_embedded(
        self, 
        db: Session, 
        event_id: str, 
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ) -> bool:
        """Mark event as embedded"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"UPDATE `{table_id}` SET embedding = 'vectorised', "
                    f"embedding_model = @embedding_model, "
                    f"updated_at = CURRENT_TIMESTAMP() "
                    f"WHERE event_id = @event_id"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "embedding_model", "STRING", embedding_model
                            ),
                            bigquery.ScalarQueryParameter(
                                "event_id", "STRING", event_id
                            )
                        ]
                    )
                )
                job.result()
                return True
            except Exception as e:
                logger.error(f"BigQuery mark_embedded failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        db_obj = db.query(Event).filter(Event.event_id == event_id).first()
        if db_obj:
            db_obj.embedding = "vectorised"
            db_obj.embedding_model = embedding_model
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_unclassified(self, db: Session, limit: int = 100) -> List[Any]:
        """Get events that need risk classification (risk_label IS NULL)"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE risk_label IS NULL LIMIT @limit"
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
                logger.error(f"BigQuery get_unclassified failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return (
            db.query(Event)
            .filter(Event.risk_label.is_(None))
            .limit(limit)
            .all()
        )

    def update_risk_classification(
        self,
        db: Session,
        event_id: str,
        risk_label: str,
        confidence: float,
        rationale: str
    ) -> bool:
        """Update risk classification fields for an event (BigQuery + SQLite fallback)"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"UPDATE `{table_id}` SET "
                    f"risk_label = @risk_label, "
                    f"rationale = @rationale, "
                    f"confidence = @confidence, "
                    f"classifier_ts = CURRENT_TIMESTAMP(), "
                    f"updated_at = CURRENT_TIMESTAMP() "
                    f"WHERE event_id = @event_id"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "risk_label", "STRING", risk_label
                            ),
                            bigquery.ScalarQueryParameter(
                                "rationale", "STRING", rationale
                            ),
                            bigquery.ScalarQueryParameter(
                                "confidence", "FLOAT64", confidence
                            ),
                            bigquery.ScalarQueryParameter(
                                "event_id", "STRING", event_id
                            )
                        ]
                    )
                )
                job.result()
                return True
            except Exception as e:
                logger.error(f"BigQuery update_risk_classification failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        db_obj = db.query(Event).filter(Event.event_id == event_id).first()
        if db_obj:
            db_obj.risk_label = risk_label
            db_obj.rationale = rationale
            db_obj.confidence = confidence
            db_obj.classifier_ts = datetime.utcnow()
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_high_risk(self, db: Session, days_back: int = 7) -> List[Any]:
        """Get high-risk events for notifications"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                from datetime import timedelta
                cutoff_date = (datetime.utcnow().date() - timedelta(days=days_back)).isoformat()
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE risk_label = @risk_label AND "
                    f"DATE(created_at) >= @cutoff_date "
                    f"ORDER BY confidence DESC"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "risk_label", "STRING", RiskLabel.HIGH_LEGAL.value
                            ),
                            bigquery.ScalarQueryParameter(
                                "cutoff_date", "DATE", cutoff_date
                            )
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery get_high_risk failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        cutoff_date = datetime.utcnow().date()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=days_back)
        return (
            db.query(Event)
            .filter(Event.risk_label == RiskLabel.HIGH_LEGAL.value)
            .filter(func.date(Event.created_at) >= cutoff_date)
            .order_by(Event.confidence.desc())
            .all()
        )

    def get_risk_summary(self, db: Session, days_back: int = 7) -> Dict[str, Any]:
        """Get risk statistics for recent events"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                from datetime import timedelta
                cutoff_date = (datetime.utcnow().date() - timedelta(days=days_back)).isoformat()
                stats = {}
                for risk_level in RiskLabel:
                    query = (
                        f"SELECT COUNT(*) as count FROM `{table_id}` "
                        f"WHERE risk_label = @risk_label AND "
                        f"DATE(created_at) >= @cutoff_date"
                    )
                    job = client.query(
                        query,
                        job_config=bigquery.QueryJobConfig(
                            query_parameters=[
                                bigquery.ScalarQueryParameter(
                                    "risk_label", "STRING", risk_level.value
                                ),
                                bigquery.ScalarQueryParameter(
                                    "cutoff_date", "DATE", cutoff_date
                                )
                            ]
                        )
                    )
                    row = list(job)[0]
                    stats[risk_level.value] = row["count"]
                # Total events
                query = (
                    f"SELECT COUNT(*) as count FROM `{table_id}` "
                    f"WHERE DATE(created_at) >= @cutoff_date"
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
                row = list(job)[0]
                stats["total"] = row["count"]
                # Processing status
                query = (
                    f"SELECT COUNT(*) as count FROM `{table_id}` "
                    f"WHERE embedding IS NULL"
                )
                job = client.query(query)
                row = list(job)[0]
                stats["unembedded"] = row["count"]
                query = (
                    f"SELECT COUNT(*) as count FROM `{table_id}` "
                    f"WHERE risk_label IS NULL"
                )
                job = client.query(query)
                row = list(job)[0]
                stats["unclassified"] = row["count"]
                return stats
            except Exception as e:
                logger.error(f"BigQuery get_risk_summary failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        cutoff_date = datetime.utcnow().date()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=days_back)
        stats = {}
        for risk_level in RiskLabel:
            count = (
                db.query(Event)
                .filter(Event.risk_label == risk_level.value)
                .filter(func.date(Event.created_at) >= cutoff_date)
                .count()
            )
            stats[risk_level.value] = count
        stats["total"] = (
            db.query(Event)
            .filter(func.date(Event.created_at) >= cutoff_date)
            .count()
        )
        stats["unembedded"] = db.query(Event).filter(Event.embedding.is_(None)).count()
        stats["unclassified"] = db.query(Event).filter(Event.risk_label.is_(None)).count()
        return stats

    def search_by_company(self, db: Session, company_name: str, limit: int = 50) -> List[Any]:
        """Search events mentioning a specific company"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE LOWER(title) LIKE LOWER(@company) OR "
                    f"LOWER(text) LIKE LOWER(@company) "
                    f"ORDER BY pub_date DESC LIMIT @limit"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "company", "STRING", f"%{company_name}%"
                            ),
                            bigquery.ScalarQueryParameter(
                                "limit", "INT64", limit
                            )
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery search_by_company failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return (
            db.query(Event)
            .filter(
                Event.title.ilike(f"%{company_name}%") |
                Event.text.ilike(f"%{company_name}%")
            )
            .order_by(Event.pub_date.desc())
            .limit(limit)
            .all()
        )

    def get_by_section(self, db: Session, section: str, limit: int = 100) -> List[Any]:
        """Get events by BOE section"""
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
                    f"{settings.BIGQUERY_DATASET}.events"
                )
                query = (
                    f"SELECT * FROM `{table_id}` "
                    f"WHERE section = @section ORDER BY pub_date DESC LIMIT @limit"
                )
                job = client.query(
                    query,
                    job_config=bigquery.QueryJobConfig(
                        query_parameters=[
                            bigquery.ScalarQueryParameter(
                                "section", "STRING", section
                            ),
                            bigquery.ScalarQueryParameter(
                                "limit", "INT64", limit
                            )
                        ]
                    )
                )
                return [dict(row) for row in job]
            except Exception as e:
                logger.error(f"BigQuery get_by_section failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite
        return (
            db.query(Event)
            .filter(Event.section == section)
            .order_by(Event.pub_date.desc())
            .limit(limit)
            .all()
        )


events = CRUDEvent() 