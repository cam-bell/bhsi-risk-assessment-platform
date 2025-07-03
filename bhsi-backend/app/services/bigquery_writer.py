import enum
from typing import Any
from google.cloud import bigquery
from threading import Lock
import logging
import time
import atexit
from datetime import datetime, date

def model_to_bq_dict(model) -> dict[str, Any]:
    """
    Convert a SQLAlchemy or Pydantic model to a BigQuery-compatible dict.
    Handles:
      - SQLAlchemy models (excludes _sa_instance_state, serializes Enums and datetimes)
      - Pydantic models (using .dict(), serializes nested structures)
      - Nested dicts/lists, None, and safe attribute filtering
    """
    def convert_value(val):
        if isinstance(val, enum.Enum):
            return val.value
        if isinstance(val, (datetime, date)):
            return val.isoformat()
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

    # Pydantic
    if hasattr(model, "dict") and callable(model.dict):
        data = model.dict()
    # SQLAlchemy
    elif hasattr(model, "__table__"):
        data = {
            c.name: getattr(model, c.name)
            for c in model.__table__.columns
        }
    # Fallback: generic object with __dict__
    elif hasattr(model, "__dict__"):
        data = {
            k: v for k, v in model.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
    else:
        data = dict(model)
    # Final pass: filter out private/callable attributes, serialize values
    return {
        k: convert_value(v)
        for k, v in data.items()
        if not k.startswith("_") and not callable(v)
    }

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
        row = model_to_bq_dict(model)
        with self.lock:
            if table not in self.buffers:
                self.buffers[table] = []
            self.buffers[table].append(row)
            if len(self.buffers[table]) >= self.batch_size:
                self._flush_table(table)

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
        for attempt in range(max_retries):
            errors = self.client.insert_rows_json(table, rows)
            if not errors:
                logging.info(
                    f"Inserted {len(rows)} rows into {table}"
                )
                self.buffers[table] = []
                return
            logging.warning(
                f"BigQuery insert error for {table} "
                f"(attempt {attempt+1}/{max_retries}): {errors}"
            )
            time.sleep(2 ** attempt)
        logging.error(
            f"Failed to insert {len(rows)} rows into {table} "
            f"after {max_retries} attempts: {errors}"
        )
        # Optionally: keep buffer for manual retry, or clear if you want to drop

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
            self.vat = "TESTVAT123"
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
    
    writer.queue("solid-topic-443216-b2.risk_monitoring.companies", company)
    writer.queue("solid-topic-443216-b2.risk_monitoring.assessment", assessment)
    writer.queue("solid-topic-443216-b2.risk_monitoring.events", event)
    
    writer.flush()
    
    # Print/log buffer status
    for table in [
        "solid-topic-443216-b2.risk_monitoring.companies",
        "solid-topic-443216-b2.risk_monitoring.assessment",
        "solid-topic-443216-b2.risk_monitoring.events"
    ]:
        count = len(writer.buffers.get(table, []))
        logging.info(f"Table '{table}' buffer after flush: {count} rows (should be 0 if successful)")
