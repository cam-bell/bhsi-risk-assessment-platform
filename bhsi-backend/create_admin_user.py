#!/usr/bin/env python3
"""
Script to create an admin user for testing user management functionality
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auth_service import AuthService
from app.crud.bigquery_users import BigQueryUsersCRUD

async def create_admin_user():
    """Create an admin user for testing"""
    
    auth_service = AuthService()
    users_crud = BigQueryUsersCRUD()
    
    # Admin user data
    admin_data = {
        "email": "admin@bhsi.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "admin123",
        "user_type": "admin"
    }
    
    try:
        # Create the admin user
        user = await auth_service.create_user(admin_data, "system")
        
        print("✅ Admin user created successfully!")
        print(f"Email: {user['email']}")
        print(f"Name: {user['first_name']} {user['last_name']}")
        print(f"Role: {user['user_type']}")
        print(f"User ID: {user['user_id']}")
        print("\nYou can now login with:")
        print(f"Email: {admin_data['email']}")
        print(f"Password: {admin_data['password']}")
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(create_admin_user()) 