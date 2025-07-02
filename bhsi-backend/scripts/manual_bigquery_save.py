import os
from app.services.database_integration import DatabaseIntegrationService
from app.db.session import SessionLocal

def main():
    os.environ["USE_BIGQUERY"] = "1"  # Ensure BigQuery is enabled

    db = SessionLocal()
    integration_service = DatabaseIntegrationService()

    # Example payload for Banco Santander, 30 days back
    payload = {
        "source": "Banco Santander",
        "payload": b"Banco Santander test payload for BigQuery",
        "meta": {"company": "Banco Santander", "test": "real_bigquery"}
    }

    raw_doc, is_new = integration_service.raw_docs_crud.create_with_dedup(
        db, **payload
    )
    print("Saved to BigQuery:", is_new)
    print("Raw doc:", raw_doc)

if __name__ == "__main__":
    main()
