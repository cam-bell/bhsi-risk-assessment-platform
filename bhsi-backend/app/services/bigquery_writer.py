import enum
import json
import base64
from typing import Any, Dict, List
from google.cloud import bigquery
from threading import Lock
import logging
import time
import atexit
from datetime import datetime, date

def model_to_bq_dict(model, table_name: str) -> dict[str, Any]:
    """
    Convert a SQLAlchemy or Pydantic model to a BigQuery-compatible dict.
    Handles schema mapping and data type conversion for specific tables.
    """
    def convert_value(val):
        if isinstance(val, enum.Enum):
            return val.value
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, bytes):
            # Convert bytes to base64 string for BigQuery
            return base64.b64encode(val).decode('utf-8')
        if hasattr(val, "dict") and callable(val.dict):  # Pydantic
            return {
                k: convert_value(v)
                for k, v in val.dict().items()
            }
        if hasattr(val, "__table__"):  # SQLAlchemy model
            return {
                c.name: convert_value(getattr(val, c.name))
                for c in val.__table__.columns
            }
        if isinstance(val, dict):
            return {
                k: convert_value(v)
                for k, v in val.items()
            }
        if isinstance(val, list):
            return [convert_value(v) for v in val]
        return val

    # Get raw data from model
    if hasattr(model, "dict") and callable(model.dict):
        data = model.dict()
    elif hasattr(model, "__table__"):
        data = {
            c.name: getattr(model, c.name)
            for c in model.__table__.columns
        }
    elif hasattr(model, "__dict__"):
        data = {
            k: v for k, v in model.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
    else:
        data = dict(model)
    
    # Convert values
    converted_data = {
        k: convert_value(v)
        for k, v in data.items()
        if not k.startswith("_") and not callable(v)
    }
    
    # Apply schema mapping based on table
    return map_to_bigquery_schema(converted_data, table_name)

def map_to_bigquery_schema(data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Map SQLAlchemy model fields to BigQuery table schema.
    """
    if table_name == "raw_docs":
        # Map raw_docs fields
        return {
            "raw_id": data.get("raw_id"),
            "source": data.get("source"),
            "fetched_at": data.get("fetched_at"),
            "payload": data.get("payload"),  # Already converted to string/base64
            "meta": json.dumps(data.get("meta", {})) if data.get("meta") else None,
            "retries": data.get("retries", 0),
            "status": data.get("status", "pending")
        }
    
    elif table_name == "events":
        # Map events fields
        return {
            "event_id": data.get("event_id"),
            "title": data.get("title"),
            "text": data.get("text"),
            "source": data.get("source"),
            "section": data.get("section"),
            "pub_date": data.get("pub_date"),
            "url": data.get("url"),
            "embedding": data.get("embedding"),
            "embedding_model": data.get("embedding_model"),
            "risk_label": data.get("risk_label"),
            "rationale": data.get("rationale"),
            "confidence": data.get("confidence"),
            "classifier_ts": data.get("classifier_ts"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "alerted": data.get("alerted", False)
        }
    
    elif table_name == "assessment":
        # Map assessment fields
        return {
            "id": data.get("id"),
            "company_id": data.get("company_id"),
            "user_id": data.get("user_id"),
            "turnover": data.get("turnover"),
            "shareholding": data.get("shareholding"),
            "bankruptcy": data.get("bankruptcy"),
            "legal": data.get("legal"),
            "corruption": data.get("corruption"),
            "overall": data.get("overall"),
            "google_results": data.get("google_results"),
            "bing_results": data.get("bing_results"),
            "gov_results": data.get("gov_results"),
            "news_results": data.get("news_results"),
            "rss_results": data.get("rss_results"),
            "analysis_summary": data.get("analysis_summary"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at")
        }
    
    elif table_name == "companies":
        # Map companies fields
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "vat_number": data.get("vat_number"),
            "description": data.get("description"),
            "sector": data.get("sector"),
            "client_tier": data.get("client_tier"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at")
        }
    
    elif table_name == "user":
        # Map user fields
        return {
            "id": data.get("id"),
            "email": data.get("email"),
            "name": data.get("name"),
            "hashed_password": data.get("hashed_password"),
            "is_active": data.get("is_active"),
            "is_superuser": data.get("is_superuser"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at")
        }
    
    else:
        # Fallback: return data as-is
        return data

class BigQueryWriter:
    def __init__(self, batch_size=50):
        self.client = bigquery.Client()
        self.batch_size = batch_size
        self.buffers = {}  # {table: [row, ...]}
        self.lock = Lock()
        self._flushed = False
        atexit.register(self._flush_on_exit)

    def queue(self, table: str, model):
        """Queue a model for batched BigQuery insert."""
        try:
            row = model_to_bq_dict(model, table)
            with self.lock:
                if table not in self.buffers:
                    self.buffers[table] = []
                self.buffers[table].append(row)
                if len(self.buffers[table]) >= self.batch_size:
                    self._flush_table(table)
        except Exception as e:
            logging.error(f"Error queuing model for BigQuery: {e}")

    def flush(self):
        """Flush all buffers to BigQuery."""
        with self.lock:
            if self._flushed:
                return
            for table in list(self.buffers.keys()):
                self._flush_table(table)
            self._flushed = True

    def _flush_on_exit(self):
        try:
            self.flush()
        except Exception as e:
            logging.error(f"BigQueryWriter flush on exit failed: {e}")

    def _flush_table(self, table, max_retries=3):
        rows = self.buffers.get(table, [])
        if not rows:
            return
        
        # Add table prefix if not present
        if not table.startswith("solid-topic-443216-b2.risk_monitoring."):
            table = f"solid-topic-443216-b2.risk_monitoring.{table}"
        
        for attempt in range(max_retries):
            try:
                errors = self.client.insert_rows_json(table, rows)
                if not errors:
                    logging.info(
                        f"Inserted {len(rows)} rows into {table}"
                    )
                    self.buffers[table.replace("solid-topic-443216-b2.risk_monitoring.", "")] = []
                    return
                else:
                    logging.warning(
                        f"BigQuery insert error for {table} "
                        f"(attempt {attempt+1}/{max_retries}): {errors}"
                    )
            except Exception as e:
                logging.warning(
                    f"BigQuery insert exception for {table} "
                    f"(attempt {attempt+1}/{max_retries}): {e}"
                )
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        logging.error(
            f"Failed to insert {len(rows)} rows into {table} "
            f"after {max_retries} attempts"
        )

    def insert_model_async(self, table: str, model, background_tasks=None):
        """Queue insert in a FastAPI BackgroundTask (non-blocking)."""
        if background_tasks:
            background_tasks.add_task(self.queue, table, model)
        else:
            self.queue(table, model)

if __name__ == "__main__":
    import uuid
    import logging
    
    # Mock SQLAlchemy-like models
    class MockCompany:
        def __init__(self):
            self.id = "TESTVAT123"
            self.name = "Test Company"
            self.description = "A test company."
            self.sector = "Tech"
            self.client_tier = "A"
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    class RiskLevel(enum.Enum):
        GREEN = "green"
        ORANGE = "orange"
        RED = "red"

    class MockAssessment:
        def __init__(self):
            self.id = str(uuid.uuid4())
            self.company_id = "TESTVAT123"
            self.user_id = "user_1"
            self.turnover = RiskLevel.GREEN
            self.shareholding = RiskLevel.ORANGE
            self.bankruptcy = RiskLevel.GREEN
            self.legal = RiskLevel.RED
            self.corruption = RiskLevel.GREEN
            self.overall = RiskLevel.ORANGE
            self.google_results = "{}"
            self.bing_results = "{}"
            self.gov_results = "{}"
            self.news_results = "{}"
            self.rss_results = "{}"
            self.analysis_summary = "Test summary."
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    class MockEvent:
        def __init__(self):
            self.event_id = str(uuid.uuid4())
            self.title = "Test Event"
            self.text = "Event text."
            self.source = "NEWSAPI"
            self.section = "Legal"
            self.pub_date = datetime.utcnow().date()
            self.url = "http://example.com"
            self.embedding = "done"
            self.embedding_model = "test-embedding"
            self.risk_label = "High-Legal"
            self.alerted = self.risk_label in ["High-Legal", "High-Reg"]
            self.rationale = "Test rationale."
            self.confidence = 0.95
            self.classifier_ts = datetime.utcnow()
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
           

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    writer = BigQueryWriter(batch_size=2)  # Small batch for test
    
    # Insert mock data
    company = MockCompany()
    assessment = MockAssessment()
    event = MockEvent()
    
    writer.queue("companies", company)
    writer.queue("assessment", assessment)
    writer.queue("events", event)
    
    writer.flush()
    
    # Print/log buffer status
    for table in ["companies", "assessment", "events"]:
        count = len(writer.buffers.get(table, []))
        logging.info(f"Table '{table}' buffer after flush: {count} rows (should be 0 if successful)")
