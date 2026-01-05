"""
Users API Router

User management endpoints for superadmins.
"""

import hashlib
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db import get_db_connection, get_cursor
from app.core.config import settings

router = APIRouter()


class UserInfo(BaseModel):
    """User info for management view."""
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = "user"
    inbound_email: Optional[str] = None
    created_at: Optional[datetime] = None


def generate_inbound_email(user_id: str) -> str:
    """
    Generate a unique inbound email address for a user.
    Format: user_{short_hash}@readableedi.com
    """
    short_id = hashlib.sha256(user_id.encode()).hexdigest()[:8]
    domain = getattr(settings, 'INBOUND_EMAIL_DOMAIN', 'readableedi.com')
    return f"user_{short_id}@{domain}"


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
        
        # Check if user exists by email first (to handle ID rotation)
        cur.execute("SELECT id, role FROM users WHERE email = %s", (request.email.lower(),))
        existing_user = cur.fetchone()
        
        if existing_user:
            # User exists! Check if ID needs migration
            if existing_user['id'] != request.id:
                print(f"Migrating user {request.email} from ID {existing_user['id']} to {request.id}")
                # Update ID and name, keeping role
                # Note: This might fail if there are FK constraints on old ID (e.g. layouts)
                # But necessary if Supabase ID changed.
                cur.execute("""
                    UPDATE users 
                    SET id = %s, name = COALESCE(%s, name)
                    WHERE email = %s
                    RETURNING id, email, name, role
                """, (request.id, request.name, request.email.lower()))
            else:
                # Same ID, just update details
                cur.execute("""
                    UPDATE users 
                    SET name = COALESCE(%s, name)
                    WHERE id = %s
                    RETURNING id, email, name, role
                """, (request.name, request.id))
        else:
            # New user - generate unique inbound email
            inbound_email = generate_inbound_email(request.id)
            cur.execute("""
                INSERT INTO users (id, email, name, role, inbound_email, created_at)
                VALUES (%s, %s, %s, 'user', %s, NOW())
                RETURNING id, email, name, role, inbound_email
            """, (request.id, request.email.lower(), request.name, inbound_email))
        
        result = cur.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "user": {
                "id": result["id"],
                "email": result["email"],
                "name": result["name"],
                "role": result["role"],
                "inbound_email": result.get("inbound_email")
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
