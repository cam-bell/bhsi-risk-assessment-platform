from fastapi import APIRouter
from app.api.v1.endpoints import companies, streamlined_search, analysis, search, auth, rag_nlp_analysis

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Search endpoints - Main functionality (streamlined search)
# Updated to use streamlined search for better performance
api_router.include_router(streamlined_search.router, prefix="/streamlined", tags=["search"])

# Legacy search endpoints (for backward compatibility)
api_router.include_router(search.router, tags=["search"])

# Company analysis endpoints
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])

# Management analysis endpoints - Executive summaries and insights
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"]) 

# 🚀 NEW: RAG Natural Language Analysis - ADDITIVE FEATURE (can be removed easily)
api_router.include_router(rag_nlp_analysis.router, prefix="/analysis", tags=["rag-nlp"]) 