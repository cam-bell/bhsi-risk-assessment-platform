#!/usr/bin/env python3
"""
BHSI Corporate Risk Assessment API
Main application entry point combining search and analysis capabilities
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

# Create main FastAPI application
app = FastAPI(
    title="BHSI Corporate Risk Assessment API",
    description="Comprehensive company risk assessment using BOE documents and news sources with Cloud Gemini analysis",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with all endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "BHSI Corporate Risk Assessment API",
        "description": "Comprehensive D&O risk assessment using BOE and news sources",
        "version": "1.0.0",
        "features": [
            "Unified search across BOE and news sources",
            "Cloud Gemini risk classification",
            "Intelligent rate limit handling",
            "Company risk analysis with smart cloud routing"
        ],
        "endpoints": {
            "search": f"{settings.API_V1_STR}/search",
            "companies": f"{settings.API_V1_STR}/companies",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "BHSI Corporate Risk Assessment API is running",
        "version": "1.0.0"
    } 