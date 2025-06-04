from fastapi import APIRouter
from app.api.v1.endpoints import auth, results, companies

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Results endpoints
api_router.include_router(results.router, prefix="/results", tags=["results"])

# Company endpoints
api_router.include_router(companies.router, prefix="/companies", tags=["companies"]) 