import sys
import os

# Ensure the parent directory of 'app' is in the import path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../..')
    )
)

from app.crud.raw_docs import raw_docs

# Ensure BigQuery is enabled for this test
os.environ["USE_BIGQUERY"] = "1"

# Test payload and meta
test_payload = b"test document for deduplication"
test_meta = {"source": "test_script"}

def test_bigquery_raw_docs():
    print("\n[INFO] USE_BIGQUERY:", os.environ.get("USE_BIGQUERY"))
    # First insert (should be new)
    row1, is_new1 = raw_docs.create_with_dedup(
        source="test_source",
        payload=test_payload,
        meta=test_meta
    )
    print("First insert:", row1, "Is new:", is_new1)
    assert is_new1 is True, "First insert should be new"

    # Second insert (should be deduplicated)
    row2, is_new2 = raw_docs.create_with_dedup(
        source="test_source",
        payload=test_payload,
        meta=test_meta
    )
    print("Second insert:", row2, "Is new:", is_new2)
    assert is_new2 is False, "Second insert should be deduplicated"

    # Query unparsed documents
    docs = raw_docs.get_unparsed(limit=5)
    print("Unparsed docs (limit 5):", docs)
    assert any(
        d.get("raw_id", None) == row1["raw_id"] for d in docs
    ), "Inserted doc should be in unparsed docs"

if __name__ == "__main__":
    print("\n[INFO] To use BigQuery, set the environment variable before running:")
    print("export USE_BIGQUERY=1\n")
    test_bigquery_raw_docs() 