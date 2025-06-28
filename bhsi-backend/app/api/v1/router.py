from fastapi import APIRouter
from app.api.v1.endpoints import companies, streamlined_search, analysis

api_router = APIRouter()

# Search endpoints - Main functionality (streamlined search)
# Updated to use streamlined search for better performance
api_router.include_router(streamlined_search.router, tags=["search"])

# Company analysis endpoints
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])

# Management analysis endpoints - Executive summaries and insights
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"]) 