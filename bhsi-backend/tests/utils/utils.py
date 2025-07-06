from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud import user as user_crud
from app.schemas.user import UserCreate


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def create_random_user(db: Session) -> Dict:
    email = "test@example.com"
    password = "testpassword123"
    user_in = UserCreate(email=email, password=password)
    user = user_crud.create(db, obj_in=user_in)
    return user


def get_test_company_data() -> Dict:
    return {
        "id": "test-company-id-123",
        "company_name": "Test Company",
        "days_back": 7,
        "include_boe": True,
        "include_news": False  # Avoid API costs in tests
    }


def get_test_search_response() -> Dict:
    return {
        "company_name": "Test Company",
        "search_date": "2025-06-17T14:30:45.123Z",
        "date_range": {
            "start": "2025-06-10",
            "end": "2025-06-17", 
            "days_back": 7
        },
        "results": [],
        "metadata": {
            "total_results": 0,
            "boe_results": 0,
            "news_results": 0,
            "high_risk_results": 0,
            "sources_searched": ["boe"]
        },
        "performance": {
            "total_time_seconds": "0.15",
            "search_time_seconds": "0.10", 
            "classification_time_seconds": "0.05",
            "keyword_efficiency": "100.0%",
            "llm_usage": "0.0%"
        }
    }


def get_test_classification_data() -> Dict:
    return {
        "text": "Concurso de acreedores de la empresa",
        "title": "Test Document",
        "source": "BOE",
        "section": "JUS"
    }


def get_test_analysis_data() -> Dict:
    return {
        "company_id": "test-company-id-123",
        "risk_scores": {
            "turnover": "green",
            "shareholding": "orange",
            "bankruptcy": "green",
            "legal": "green",
            "corruption": "green",
            "overall": "green"
        },
        "processed_results": {
            "google_results": "[]",
            "bing_results": "[]",
            "gov_results": "[]",
            "news_results": "[]",
            "analysis_summary": "{}"
        }
    } 