import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.services.database_integration import DatabaseIntegrationService
from app.core.config import settings, Settings

@pytest.fixture
def db_session():
    # Use your actual test session fixture or in-memory SQLite for fallback
    from app.db.session import SessionLocal
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def integration_service():
    return DatabaseIntegrationService()

def sample_payload(test_id="default"):
    """Sample payload for testing"""
    return {
        "source": f"TEST_SOURCE_{test_id}",
        "payload": f"test payload content {test_id}".encode('utf-8'),
        "meta": {"test": "data", "test_id": test_id}
    }

def test_bigquery_success_path(db_session, integration_service):
    with patch.object(Settings, "is_bigquery_enabled", return_value=True), \
         patch("app.crud.raw_docs.bigquery.Client") as mock_bq_client:
        mock_client = MagicMock()
        mock_bq_client.return_value = mock_client
        mock_client.insert_rows_json.return_value = []
        raw_doc, is_new = integration_service.raw_docs_crud.create_with_dedup(
            db_session, **sample_payload("success")
        )
        assert is_new

def test_bigquery_failure_fallback_to_sqlite(db_session, integration_service):
    with patch.object(Settings, "is_bigquery_enabled", return_value=True), \
         patch("app.crud.raw_docs.bigquery.Client", side_effect=Exception("BigQuery error")):
        raw_doc, is_new = integration_service.raw_docs_crud.create_with_dedup(
            db_session, **sample_payload("fallback")
        )
        assert is_new  # Should fallback to SQLite

def test_data_integrity_both_backends(db_session, integration_service):
    with patch.object(Settings, "is_bigquery_enabled", return_value=False):
        raw_doc, is_new = integration_service.raw_docs_crud.create_with_dedup(
            db_session, **sample_payload("sqlite")
        )
        assert is_new
        assert raw_doc.source == "TEST_SOURCE_sqlite"
