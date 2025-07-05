#!/usr/bin/env python3
"""
BigQuery CRUD operations for Users model
"""

import logging
import uuid
import bcrypt
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import bigquery
from app.crud.bigquery_crud import BigQueryCRUDBase

logger = logging.getLogger(__name__)


class BigQueryUsersCRUD(BigQueryCRUDBase):
    """BigQuery CRUD operations for Users model"""
    
    def __init__(self):
        super().__init__(table_name="users")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        user_type: str = "user",
        created_by: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.get_by_email(email)
            if existing_user:
                logger.warning(f"User with email {email} already exists")
                return None
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user data
            user_data = {
                "user_id": str(uuid.uuid4()),
                "email": email.lower().strip(),
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "hashed_password": hashed_password,
                "user_type": user_type.lower(),
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            result = await self.create(user_data)
            logger.info(f"✅ Created new user: {email} ({user_type})")
            return result
            
        except Exception as e:
            logger.error(f"❌ BigQuery create_user failed: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            query = f"""
            WITH LatestUsers AS (
                SELECT 
                    *,
                    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) as rn
                FROM `{self.table_id}`
            )
            SELECT *
            FROM LatestUsers
            WHERE email = @email AND rn = 1
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("email", "STRING", email.lower().strip())
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return self._convert_from_bq_format(dict(row))
            
            return None
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_email failed: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        try:
            user = await self.get_by_email(email)
            if not user:
                return None
            
            if not user.get('is_active', False):
                logger.warning(f"User {email} is not active")
                return None
            
            if not self.verify_password(password, user['hashed_password']):
                logger.warning(f"Invalid password for user {email}")
                return None
            
            # Update last login
            await self.update_last_login(user['user_id'])
            
            logger.info(f"✅ User authenticated: {email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ BigQuery authenticate_user failed: {e}")
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            # Get the current user data
            user = await self.get_by_id(user_id, id_field="user_id")
            if not user:
                logger.warning(f"User {user_id} not found for last_login update")
                return False
            
            # Create a new record with updated last_login
            # This is the BigQuery streaming buffer workaround
            updated_user_data = user.copy()
            updated_user_data['last_login'] = datetime.utcnow().isoformat()
            updated_user_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Remove any query-specific fields that shouldn't be in the table
            updated_user_data.pop('rn', None)
            
            # Insert the updated user record
            result = await self.create(updated_user_data)
            if result:
                logger.info(f"✅ Updated last_login for user: {user_id}")
                return True
            else:
                logger.error(f"❌ Failed to create updated last_login record: {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery update_last_login failed: {e}")
            return False
    
    async def get_all_users(self, current_user_id: str) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        try:
            # Check if current user is admin
            current_user = await self.get_by_id(current_user_id, id_field="user_id")
            if not current_user or current_user.get('user_type') != 'admin':
                logger.warning(f"User {current_user_id} attempted to access all users without admin privileges")
                return []
            
            # Get the latest record for each user (due to INSERT approach)
            query = f"""
            WITH LatestUsers AS (
                SELECT 
                    user_id,
                    email,
                    first_name,
                    last_name,
                    user_type,
                    is_active,
                    created_at,
                    last_login,
                    updated_at,
                    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) as rn
                FROM `{self.table_id}`
            )
            SELECT 
                user_id, email, first_name, last_name, user_type, is_active, created_at, last_login
            FROM LatestUsers
            WHERE rn = 1
            ORDER BY created_at DESC
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [self._convert_from_bq_format(dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_all_users failed: {e}")
            return []
    
    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any],
        current_user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Update user (admin only or self)"""
        try:
            # Check permissions
            current_user = await self.get_by_id(current_user_id, id_field="user_id")
            if not current_user:
                return None
            
            # Only admin can update other users, or user can update themselves
            if (current_user.get('user_type') != 'admin' and 
                current_user_id != user_id):
                logger.warning(f"User {current_user_id} attempted to update user {user_id} without permission")
                return None
            
            # Get the current user data
            user = await self.get_by_id(user_id, id_field="user_id")
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            # Apply updates to the user data
            updated_user_data = user.copy()
            for key, value in updates.items():
                updated_user_data[key] = value
            
            # Add updated timestamp
            updated_user_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Remove any query-specific fields that shouldn't be in the table
            updated_user_data.pop('rn', None)
            
            # Create a new record with the updated data
            # This is the BigQuery streaming buffer workaround
            result = await self.create(updated_user_data)
            if result:
                logger.info(f"✅ Updated user: {user_id}")
                return updated_user_data
            else:
                logger.error(f"❌ Failed to create updated user record: {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ BigQuery update_user failed: {e}")
            return None
    
    async def deactivate_user(self, user_id: str, current_user_id: str) -> bool:
        """Deactivate a user (admin only)"""
        try:
            # Check if current user is admin
            current_user = await self.get_by_id(current_user_id, id_field="user_id")
            if not current_user or current_user.get('user_type') != 'admin':
                logger.warning(f"User {current_user_id} attempted to deactivate user {user_id} without admin privileges")
                return False
            
            # Prevent admin from deactivating themselves
            if user_id == current_user_id:
                logger.warning(f"Admin {current_user_id} attempted to deactivate themselves")
                return False
            
            # Get the current user data
            user = await self.get_by_id(user_id, id_field="user_id")
            if not user:
                logger.warning(f"User {user_id} not found for deactivation")
                return False
            
            # Create a new record with is_active = False
            # This is the BigQuery streaming buffer workaround
            deactivated_user_data = {
                "user_id": user_id,
                "email": user.get('email', ''),
                "first_name": user.get('first_name', ''),
                "last_name": user.get('last_name', ''),
                "hashed_password": user.get('hashed_password', ''),
                "user_type": user.get('user_type', 'user'),
                "is_active": False,  # This is the key change
                "created_at": user.get('created_at', datetime.utcnow().isoformat()),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": user.get('last_login')
            }
            
            # Insert the deactivated user record
            result = await self.create(deactivated_user_data)
            if result:
                logger.info(f"✅ Deactivated user: {user_id}")
                return True
            else:
                logger.error(f"❌ Failed to create deactivated user record: {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ BigQuery deactivate_user failed: {e}")
            return False
    
    async def get_by_id(self, user_id: str, id_field: str = "user_id") -> Optional[Dict[str, Any]]:
        """Get user by ID (latest record)"""
        try:
            query = f"""
            WITH LatestUsers AS (
                SELECT 
                    *,
                    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) as rn
                FROM `{self.table_id}`
            )
            SELECT *
            FROM LatestUsers
            WHERE user_id = @user_id AND rn = 1
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return self._convert_from_bq_format(dict(row))
            
            return None
            
        except Exception as e:
            logger.error(f"❌ BigQuery get_by_id failed: {e}")
            return None


# Global instance
bigquery_users = BigQueryUsersCRUD() 