from app.api.v1.endpoints import search, streamlined_search, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(streamlined_search.router, prefix="/streamlined", tags=["streamlined_search"]) 