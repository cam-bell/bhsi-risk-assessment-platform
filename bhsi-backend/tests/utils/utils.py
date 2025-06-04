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
        "name": "Test Company",
        "description": "A test company for automated testing"
    }


def get_test_analysis_data() -> Dict:
    return {
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