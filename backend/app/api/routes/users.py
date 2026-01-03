"""
Users API Router

User management endpoints for superadmins.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db import get_db_connection, get_cursor

router = APIRouter()


class UserInfo(BaseModel):
    """User info for management view."""
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = "user"
    created_at: Optional[datetime] = None


class RoleUpdateRequest(BaseModel):
    """Request to update user role."""
    role: str


class UserSyncRequest(BaseModel):
    """Request to sync a user from Supabase auth."""
    id: str  # Supabase user ID
    email: str
    name: Optional[str] = None


@router.post("/sync")
async def sync_user(request: UserSyncRequest):
    """
    Create or update a user in PostgreSQL when they authenticate via Supabase.
    Called by the frontend after successful Supabase authentication.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Upsert: create if not exists, update if exists
        cur.execute("""
            INSERT INTO users (id, email, name, role, created_at)
            VALUES (%s, %s, %s, 'user', NOW())
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                name = COALESCE(EXCLUDED.name, users.name)
            RETURNING id, email, name, role
        """, (request.id, request.email.lower(), request.name))
        
        result = cur.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "user": {
                "id": result["id"],
                "email": result["email"],
                "name": result["name"],
                "role": result["role"]
            }
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error syncing user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[UserInfo])
async def get_all_users():
    """Get list of all users (superadmin only)."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT id, email, name, role, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        results = cur.fetchall()
        
        return [UserInfo(**row) for row in results]
        
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.put("/{user_id}/role")
async def update_user_role(user_id: str, request: RoleUpdateRequest):
    """Update a user's role (superadmin only)."""
    conn = None
    valid_roles = ["user", "admin", "superadmin"]
    
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            UPDATE users SET role = %s WHERE id = %s
            RETURNING id, email, role
        """, (request.role, user_id))
        
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        return {"success": True, "user_id": result["id"], "role": result["role"]}
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating user role: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
