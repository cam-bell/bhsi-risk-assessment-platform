import requests
import time
import json
from tabulate import tabulate

# Service base URLs
SERVICES = {
    "Gemini": (
        "https://gemini-service-185303190462.europe-west1.run.app"
    ),
    "Embedder": (
        "https://embedder-service-185303190462.europe-west1.run.app"
    ),
    "VectorSearch": (
        "https://vector-search-185303190462.europe-west1.run.app"
    ),
    "BigQueryAnalytics": (
        "https://bigquery-analytics-185303190462.europe-west1.run.app"
    ),
}

# Endpoint definitions: (service, method, path, payload, expected_fields)
ENDPOINTS = [
    # Gemini Service
    (
        "Gemini",
        "POST",
        "/classify",
        {
            "text": "Sample document for risk classification.",
            "title": "Test Title",
            "source": "TestSource",
            "section": "TestSection"
        },
        ["label", "confidence", "reason", "method"],
    ),
    (
        "Gemini",
        "POST",
        "/generate",
        {"prompt": "Summarize this document."},
        ["text", "model"],
    ),
    (
        "Gemini",
        "POST",
        "/analyze_company",
        {
            "company_name": "TestCo",
            "company_data": {
                "search_results": [
                    {
                        "title": "Doc1",
                        "source": "TestSource",
                        "summary": "Summary1"
                    },
                    {
                        "title": "Doc2",
                        "source": "TestSource",
                        "summary": "Summary2"
                    }
                ],
                "other_info": "Some info"
            },
            "analysis_type": "comprehensive"
        },
        [
            "company_name",
            "risk_assessment",
            "analysis_summary",
            "confidence",
            "methodology",
            "analysis_method"
        ],
    ),
    # Embedder Service
    (
        "Embedder",
        "POST",
        "/embed",
        {"text": "Sample text for embedding."},
        ["embedding", "model"],
    ),
    # Vector Search Service
    (
        "VectorSearch",
        "POST",
        "/embed",
        {
            "documents": [
                {
                    "id": "doc1",
                    "text": "Sample doc for vector store.",
                    "metadata": {"type": "test"}
                }
            ]
        },
        ["status", "message", "added_documents", "total_documents"],
    ),
    (
        "VectorSearch",
        "POST",
        "/search",
        {"query": "Find this document."},
        ["results", "query", "total_results"],
    ),
    # BigQuery Analytics Service
    (
        "BigQueryAnalytics",
        "GET",
        "/analytics/company/TestCo",
        None,
        ["company_name", "analytics", "risk_profile"],
    ),
    (
        "BigQueryAnalytics",
        "GET",
        "/analytics/risk-trends",
        None,
        ["trends", "date"],
    ),
    (
        "BigQueryAnalytics",
        "GET",
        "/analytics/alerts",
        None,
        ["alerts", "count"],
    ),
    (
        "BigQueryAnalytics",
        "GET",
        "/analytics/sectors",
        None,
        ["sectors", "risk_levels"],
    ),
]

# Helper to check for placeholder/hardcoded values
PLACEHOLDER_VALUES = [
    0.5, "0.5", "fixed date", "2024-01-01", "placeholder", "test", "sample"
]


def is_placeholder(val):
    if isinstance(val, (int, float, str)):
        sval = str(val).lower()
        return any(str(ph).lower() in sval for ph in PLACEHOLDER_VALUES)
    return False


def check_expected_fields(data, expected_fields):
    if not isinstance(data, dict):
        return False
    for field in expected_fields:
        if field not in data:
            return False
    return True


def find_placeholders(data):
    suspicious = []
    if isinstance(data, dict):
        for k, v in data.items():
            if is_placeholder(v):
                suspicious.append((k, v))
            elif isinstance(v, (dict, list)):
                suspicious.extend(find_placeholders(v))
    elif isinstance(data, list):
        for item in data:
            suspicious.extend(find_placeholders(item))
    return suspicious


def main():
    results = []
    details = []
    for service, method, path, payload, expected_fields in ENDPOINTS:
        url = SERVICES[service] + path
        headers = {"Content-Type": "application/json"}
        start = time.time()
        try:
            if method == "POST":
                resp = requests.post(
                    url, json=payload, headers=headers, timeout=10
                )
            else:
                resp = requests.get(url, headers=headers, timeout=10)
            elapsed = resp.elapsed.total_seconds()
            content_type = resp.headers.get("Content-Type", "-")
            status = resp.status_code
            try:
                data = resp.json()
                json_valid = True
            except Exception:
                data = resp.text
                json_valid = False
            # Check for expected fields
            has_fields = (
                check_expected_fields(data, expected_fields)
                if json_valid else False
            )
            # Check for placeholders
            suspicious = find_placeholders(data) if json_valid else []
            # Log summary
            results.append([
                service,
                path,
                method,
                status,
                f"{elapsed:.2f}s",
                content_type,
                "Yes" if has_fields else "No",
                "Yes" if suspicious else "No",
            ])
            # Log details if failed
            if status != 200 or not has_fields or not json_valid or suspicious:
                details.append({
                    "service": service,
                    "path": path,
                    "status": status,
                    "json_valid": json_valid,
                    "has_fields": has_fields,
                    "suspicious": suspicious,
                    "response": data,
                })
        except Exception as e:
            elapsed = time.time() - start
            results.append([
                service,
                path,
                method,
                "ERR",
                f"{elapsed:.2f}s",
                "-",
                "No",
                "-",
            ])
            details.append({
                "service": service,
                "path": path,
                "status": "ERR",
                "error": str(e),
            })
    # Print summary table
    headers = [
        "Service", "Endpoint", "Method", "Status", "Time", "Content-Type",
        "Fields OK", "Placeholders?"
    ]
    print("\nCloud Services Validation Summary:\n")
    print(tabulate(results, headers=headers, tablefmt="github"))
    # Print details for failures
    if details:
        print("\n---\nDetails for failures or suspicious responses:\n")
        for d in details:
            print(json.dumps(d, indent=2, default=str))
            print("\n---\n")
    else:
        print("\nAll endpoints responded as expected.\n")


if __name__ == "__main__":
    main() 