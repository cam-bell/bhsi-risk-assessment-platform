#!/usr/bin/env python3
"""
Authentication Service - JWT token management and user authentication
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings
from app.crud.bigquery_users import bigquery_users

logger = logging.getLogger(__name__)


class AuthService:
    """Service for JWT authentication and user management"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT token verification failed: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        try:
            user = await bigquery_users.authenticate_user(email, password)
            if user:
                return user
            return None
        except Exception as e:
            logger.error(f"Authentication failed for {email}: {e}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        try:
            payload = self.verify_token(token)
            if payload is None:
                return None
            
            user_id = payload.get("sub")
            if user_id is None:
                return None
            
            user = await bigquery_users.get_by_id(user_id, id_field="user_id")
            if user is None or not user.get('is_active', False):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Get current user failed: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any], created_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new user (admin only)"""
        try:
            # Check if creator is admin (if provided)
            if created_by:
                creator = await bigquery_users.get_by_id(created_by, id_field="user_id")
                if not creator or creator.get('user_type') != 'admin':
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only admins can create users"
                    )
            
            result = await bigquery_users.create_user(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password'],
                user_type=user_data.get('user_type', 'user'),
                created_by=created_by
            )
            
            if result:
                # BigQuery CRUD returns {"data": data} for users table
                # Extract the actual user data from the result
                if isinstance(result, dict) and 'data' in result:
                    return result['data']
                else:
                    return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User creation failed"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create user failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_all_users(self, current_user_id: str) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        try:
            users = await bigquery_users.get_all_users(current_user_id)
            return users
        except Exception as e:
            logger.error(f"Get all users failed: {e}")
            return []
    
    async def update_user(self, user_id: str, updates: Dict[str, Any], current_user_id: str) -> Optional[Dict[str, Any]]:
        """Update user (admin only or self)"""
        try:
            result = await bigquery_users.update_user(user_id, updates, current_user_id)
            return result
        except Exception as e:
            logger.error(f"Update user failed: {e}")
            return None
    
    async def deactivate_user(self, user_id: str, current_user_id: str) -> bool:
        """Deactivate a user (admin only)"""
        try:
            result = await bigquery_users.deactivate_user(user_id, current_user_id)
            return result
        except Exception as e:
            logger.error(f"Deactivate user failed: {e}")
            return False


# Global instance
auth_service = AuthService() 