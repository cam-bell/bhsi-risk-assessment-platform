#!/usr/bin/env python3
"""
Authentication API Endpoints
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_active_user, get_current_admin_user
from app.crud.bigquery_users_crud import BigQueryUsersCRUD

logger = logging.getLogger(__name__)

router = APIRouter()
auth_service = AuthService()

# Helper function to convert datetime to ISO string
def format_datetime(dt) -> str:
    """Convert datetime object to ISO format string"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    user_type: str = "user"


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT tokens
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token = auth_service.create_access_token(
            data={"sub": user["user_id"], "email": user["email"], "user_type": user["user_type"]}
        )
        refresh_token = auth_service.create_refresh_token(
            data={"sub": user["user_id"], "email": user["email"]}
        )
        
        # Remove sensitive data from user response and format datetime
        user_response = {
            "user_id": user["user_id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "user_type": user["user_type"],
            "is_active": user["is_active"],
            "created_at": format_datetime(user["created_at"]),
            "last_login": format_datetime(user.get("last_login"))
        }
        
        logger.info(f"✅ User logged in: {user['email']}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_active_user)):
    """
    Refresh access token using current user
    """
    try:
        # Create new access token
        access_token = auth_service.create_access_token(
            data={"sub": current_user["user_id"], "email": current_user["email"], "user_type": current_user["user_type"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        user_type=current_user["user_type"],
        is_active=current_user["is_active"],
        created_at=format_datetime(current_user["created_at"]),
        last_login=format_datetime(current_user.get("last_login"))
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Create a new user (admin only)
    """
    try:
        user_data = {
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "password": request.password,
            "user_type": request.user_type
        }
        
        user = await auth_service.create_user(user_data, current_user["user_id"])
        
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            user_type=user["user_type"],
            is_active=user["is_active"],
            created_at=format_datetime(user["created_at"]),
            last_login=format_datetime(user.get("last_login"))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_admin_user)):
    """
    Get all users (admin only)
    """
    try:
        users = await auth_service.get_all_users(current_user["user_id"])
        
        return [
            UserResponse(
                user_id=user["user_id"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                user_type=user["user_type"],
                is_active=user["is_active"],
                created_at=format_datetime(user["created_at"]),
                last_login=format_datetime(user.get("last_login"))
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Get all users failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update user (admin only or self)
    """
    try:
        updates = {}
        if request.first_name is not None:
            updates["first_name"] = request.first_name
        if request.last_name is not None:
            updates["last_name"] = request.last_name
        if request.email is not None:
            updates["email"] = request.email
        if request.user_type is not None:
            updates["user_type"] = request.user_type
        if request.is_active is not None:
            updates["is_active"] = request.is_active
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No updates provided"
            )
        
        result = await auth_service.update_user(user_id, updates, current_user["user_id"])
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or update failed"
            )
        
        return UserResponse(
            user_id=result["user_id"],
            email=result["email"],
            first_name=result["first_name"],
            last_name=result["last_name"],
            user_type=result["user_type"],
            is_active=result["is_active"],
            created_at=format_datetime(result["created_at"]),
            last_login=format_datetime(result.get("last_login"))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Deactivate a user (admin only)
    """
    try:
        success = await auth_service.deactivate_user(user_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or deactivation failed"
            )
        
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 


@router.post("/init-admin", response_model=UserResponse)
async def create_initial_admin(request: CreateUserRequest):
    """
    Create initial admin user (temporary endpoint for setup)
    """
    try:
        # Check if any admin users already exist
        bigquery_users = BigQueryUsersCRUD()
        existing_admins = await bigquery_users.get_all_users("system")
        
        # If admin users exist, don't allow creation
        if existing_admins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin users already exist. Use regular admin endpoints."
            )
        
        # Create the admin user
        user_data = {
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "password": request.password,
            "user_type": "admin"  # Force admin type
        }
        
        user = await auth_service.create_user(user_data, None)  # No creator required for initial admin
        
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            user_type=user["user_type"],
            is_active=user["is_active"],
            created_at=format_datetime(user["created_at"]),
            last_login=format_datetime(user.get("last_login"))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create initial admin failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 