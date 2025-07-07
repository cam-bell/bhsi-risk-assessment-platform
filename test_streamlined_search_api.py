from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_streamlined_search():
    payload = {
        "company_name": "TestCompany",
        "start_date": "2024-06-01",
        "end_date": "2024-07-01",
        "days_back": 7,
        "include_boe": False,
        "include_news": True,
        "include_rss": False
    }
    response = client.post("/api/v1/streamlined/search", json=payload)
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == "__main__":
    test_streamlined_search() 