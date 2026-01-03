"""
Layouts API Router

CRUD operations for EDI layout configurations.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from app.db import get_db_connection, get_cursor
from app.schemas.layout import LayoutConfig
from app.services.edi_segments import get_segments_for_type, get_all_available_keys

router = APIRouter()


class LayoutSummary(BaseModel):
    """Summary of a layout version for list view."""
    code: str
    name: str
    version_number: int
    status: str
    is_active: bool
    updated_at: Optional[datetime] = None


class LayoutDetail(BaseModel):
    """Full layout detail including config JSON."""
    code: str
    name: str
    version_number: int
    status: str
    is_active: bool
    config_json: dict
    updated_at: Optional[datetime] = None
    is_personal: bool = False


class LayoutUpdateRequest(BaseModel):
    """Request body for updating a layout."""
    config_json: dict


class SegmentInfo(BaseModel):
    """EDI segment mapping info."""
    segment: str
    key: str
    description: str


@router.get("/segments/{type_code}")
async def get_segments(type_code: str):
    """Get EDI segment mappings for a transaction type."""
    segments = get_segments_for_type(type_code)
    result = [
        SegmentInfo(segment=seg, key=info["key"], description=info["description"])
        for seg, info in segments.items()
    ]
    return result


@router.get("/", response_model=List[LayoutSummary])
async def get_all_layouts(user_id: Optional[str] = None):
    """
    Get all transaction types and their layout status.
    If user_id provided, returns user-specific status (e.g. active Draft).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # If user_id provided, we want to see:
        # 1. User's specific version status if exists
        # 2. Else System Default status
        
        if user_id:
            query = """
                SELECT 
                    tt.code, 
                    tt.name, 
                    COALESCE(ul.version_number, dl.version_number) as version_number,
                    COALESCE(ul.status, dl.status) as status,
                    COALESCE(ul.is_active, dl.is_active) as is_active,
                    COALESCE(ul.updated_at, dl.updated_at) as updated_at
                FROM transaction_types tt
                LEFT JOIN layout_versions dl ON tt.code = dl.transaction_type_code 
                    AND dl.user_id IS NULL 
                    AND dl.version_number = (
                        SELECT MAX(version_number) 
                        FROM layout_versions 
                        WHERE transaction_type_code = tt.code AND user_id IS NULL
                    )
                LEFT JOIN layout_versions ul ON tt.code = ul.transaction_type_code 
                    AND ul.user_id = %s 
                    AND ul.version_number = (
                        SELECT MAX(version_number) 
                        FROM layout_versions 
                        WHERE transaction_type_code = tt.code AND user_id = %s
                    )
                ORDER BY tt.code;
            """
            cur.execute(query, (user_id, user_id))
        else:
            # Original Admin Query (System Defaults)
            query = """
                SELECT 
                    tt.code, 
                    tt.name, 
                    lv.version_number,
                    lv.status,
                    lv.is_active,
                    lv.updated_at
                FROM transaction_types tt
                LEFT JOIN layout_versions lv ON tt.code = lv.transaction_type_code 
                    AND lv.user_id IS NULL
                    AND lv.version_number = (
                        SELECT MAX(version_number) 
                        FROM layout_versions 
                        WHERE transaction_type_code = tt.code AND user_id IS NULL
                    )
                ORDER BY tt.code;
            """
            cur.execute(query)
            
        results = cur.fetchall()
        
        return [
            LayoutSummary(
                code=row['code'],
                name=row['name'],
                version_number=row['version_number'] if row['version_number'] else 0,
                status=row['status'] if row['status'] else 'NONE',
                is_active=row['is_active'] if row['is_active'] is not None else False,
                updated_at=row['updated_at']
            )
            for row in results
        ]
        
    except Exception as e:
        print(f"Error fetching layouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/{type_code}", response_model=LayoutDetail)
async def get_layout(type_code: str, user_id: Optional[str] = None):
    """
    Get the active layout configuration for a specific transaction type.
    Priority:
    1. User's Draft
    2. User's Production
    3. System Default (if user_id provided)
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Determine query strategy
        if user_id:
             # Try to find specific user version first
            cur.execute("""
                SELECT version_number, status, config_json, is_active, updated_at, user_id
                FROM layout_versions l
                JOIN transaction_types t ON l.transaction_type_code = t.code
                WHERE l.transaction_type_code = %s AND l.user_id = %s
                ORDER BY l.version_number DESC
                LIMIT 1;
            """, (type_code, user_id))
            result = cur.fetchone()
            
            if not result:
                # Fallback to system default
                cur.execute("""
                    SELECT version_number, status, config_json, is_active, updated_at, NULL as user_id
                    FROM layout_versions l
                    JOIN transaction_types t ON l.transaction_type_code = t.code
                    WHERE l.transaction_type_code = %s AND l.user_id IS NULL
                    ORDER BY l.version_number DESC
                    LIMIT 1;
                """, (type_code,))
                result = cur.fetchone()
        else:
            # System defaults only (Admin view or generic)
            cur.execute("""
                SELECT version_number, status, config_json, is_active, updated_at, NULL as user_id
                FROM layout_versions l
                JOIN transaction_types t ON l.transaction_type_code = t.code
                WHERE l.transaction_type_code = %s AND l.user_id IS NULL
                ORDER BY l.version_number DESC
                LIMIT 1;
            """, (type_code,))
            result = cur.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Layout for {type_code} not found")
            
        # Fetch name
        cur.execute("SELECT name FROM transaction_types WHERE code = %s;", (type_code,))
        type_info = cur.fetchone()
            
        return LayoutDetail(
            code=type_code,
            name=type_info['name'] if type_info else type_code,
            version_number=result['version_number'],
            status=result['status'],
            is_active=result['is_active'],
            config_json=result['config_json'],
            updated_at=result['updated_at'],
            is_personal=bool(user_id and result.get('user_id') == user_id) # Crude check, but let's be more precise
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.put("/{type_code}", response_model=LayoutDetail)
async def update_layout(type_code: str, request: LayoutUpdateRequest, user_id: Optional[str] = None):
    """
    Update layout configuration.
    - If user_id provided: Create/Update USER specific version.
    - If user_id None: Create/Update SYSTEM DEFAULT version (Superadmin only).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # 1. Check for existing DRAFT for this scope
        params = (type_code, user_id) if user_id else (type_code,)
        user_filter = "AND user_id = %s" if user_id else "AND user_id IS NULL"
        
        cur.execute(f"""
            SELECT version_number, status 
            FROM layout_versions 
            WHERE transaction_type_code = %s {user_filter}
            ORDER BY version_number DESC 
            LIMIT 1;
        """, params)
        current = cur.fetchone()
        
        should_create_new = False
        current_version = 0
        
        if not current:
            # First time for this user? Need to find base version number?
            # Actually, version numbers can be independent or shared sequence.
            # Independent sequence per user is cleaner, but complex to track globally.
            # Let's just find the MAX version globally to be safe + 1.
            should_create_new = True
        else:
            current_version = current['version_number']
            if current['status'] == 'PRODUCTION':
                should_create_new = True
            
        if should_create_new:
            # Determine new version number (globally unique for simplicity usually, or scoped)
            # Let's make it simple: just MAX(version) + 1 for this type, regardless of user.
            cur.execute("SELECT COALESCE(MAX(version_number), 0) as max_version FROM layout_versions WHERE transaction_type_code = %s", (type_code,))
            max_ver = cur.fetchone()['max_version']
            new_version = max_ver + 1
            
            creator = user_id if user_id else 'admin'
            
            cur.execute("""
                INSERT INTO layout_versions 
                (transaction_type_code, version_number, status, config_json, is_active, created_by, updated_at, user_id)
                VALUES (%s, %s, 'DRAFT', %s, false, %s, NOW(), %s)
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at, user_id;
            """, (type_code, new_version, json.dumps(request.config_json), creator, user_id))
        else:
            # Update existing DRAFT
            cur.execute(f"""
                UPDATE layout_versions 
                SET config_json = %s, updated_at = NOW()
                WHERE transaction_type_code = %s AND version_number = %s {user_filter}
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at, user_id;
            """, (json.dumps(request.config_json), type_code, current_version) + ((user_id,) if user_id else ()))
        
        result = cur.fetchone()
        conn.commit()
        
        # Fetch name from transaction_types (if needed for response, otherwise type_code is fine)
        cur.execute("SELECT name FROM transaction_types WHERE code = %s;", (type_code,))
        type_info = cur.fetchone()

        # Simplify is_personal logic: if we passed a user_id to update, it is personal. 
        # Or check result user_id if returned.
        is_personal_val = False
        if user_id:
             is_personal_val = True
        elif result.get('user_id'):
             is_personal_val = True

        return LayoutDetail(
            code=result['code'],
            name=type_info['name'] if type_info else type_code, # Simplified, frontend handles names usually or fetched above
            version_number=result['version_number'],
            status=result['status'],
            is_active=result['is_active'],
            config_json=result['config_json'],
            updated_at=result['updated_at'],
            is_personal=is_personal_val
        )
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating layout: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


class PromoteResponse(BaseModel):
    """Response from promote action."""
    success: bool
    message: str
    code: str
    version_number: int
    status: str


@router.post("/{type_code}/promote", response_model=PromoteResponse)
async def promote_layout(type_code: str):
    """
    Promote a DRAFT layout to PRODUCTION.
    - Sets the DRAFT version to PRODUCTION and is_active=true
    - Sets previous PRODUCTION version to ARCHIVED and is_active=false
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Get the latest DRAFT version
        cur.execute("""
            SELECT id, version_number 
            FROM layout_versions 
            WHERE transaction_type_code = %s AND status = 'DRAFT'
            ORDER BY version_number DESC 
            LIMIT 1;
        """, (type_code,))
        draft = cur.fetchone()
        
        if not draft:
            raise HTTPException(status_code=400, detail=f"No DRAFT version found for {type_code}")
        
        # Archive current PRODUCTION versions
        cur.execute("""
            UPDATE layout_versions 
            SET status = 'ARCHIVED', is_active = false, updated_at = NOW()
            WHERE transaction_type_code = %s AND status = 'PRODUCTION';
        """, (type_code,))
        
        # Promote DRAFT to PRODUCTION
        cur.execute("""
            UPDATE layout_versions 
            SET status = 'PRODUCTION', is_active = true, updated_at = NOW()
            WHERE id = %s
            RETURNING version_number;
        """, (draft['id'],))
        
        conn.commit()
        result = cur.fetchone()
        
        return PromoteResponse(
            success=True,
            message=f"Version {result['version_number']} promoted to PRODUCTION",
            code=type_code,
            version_number=result['version_number'],
            status="PRODUCTION"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error promoting layout {type_code}: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.post("/{type_code}/lock", response_model=PromoteResponse)
async def lock_layout(type_code: str):
    """
    Lock a PRODUCTION layout version.
    Locked versions cannot be edited or overwritten.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Get the current PRODUCTION version
        cur.execute("""
            SELECT id, version_number, status
            FROM layout_versions 
            WHERE transaction_type_code = %s AND status = 'PRODUCTION' AND is_active = true
            ORDER BY version_number DESC 
            LIMIT 1;
        """, (type_code,))
        production = cur.fetchone()
        
        if not production:
            raise HTTPException(status_code=400, detail=f"No PRODUCTION version found for {type_code}")
        
        # Update to LOCKED status
        cur.execute("""
            UPDATE layout_versions 
            SET status = 'LOCKED', updated_at = NOW()
            WHERE id = %s
            RETURNING version_number;
        """, (production['id'],))
        
        conn.commit()
        result = cur.fetchone()
        
        return PromoteResponse(
            success=True,
            message=f"Version {result['version_number']} is now LOCKED (immutable)",
            code=type_code,
            version_number=result['version_number'],
            status="LOCKED"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error locking layout {type_code}: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.delete("/{type_code}")
async def restore_default_layout(type_code: str, user_id: Optional[str] = None):
    """
    Restore the default layout for a transaction type.
    - If user_id provided: Deletes ALL 'user' versions for this type.
    - If user_id None: (Admin) Not supported or maybe deletes draft? 
      For now, let's only support restoring USER defaults.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="Cannot restore default for global system layouts. This is for user overrides only.")

    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)

        # Check if user actually has any versions
        cur.execute("SELECT COUNT(*) as count FROM layout_versions WHERE transaction_type_code = %s AND user_id = %s", (type_code, user_id))
        count = cur.fetchone()['count']
        
        if count == 0:
             return {"message": "No custom layout found. Already using default."}

        # Delete all versions for this user and type
        cur.execute("""
            DELETE FROM layout_versions 
            WHERE transaction_type_code = %s AND user_id = %s
        """, (type_code, user_id))
        
        conn.commit()
        return {"message": "Custom layout deleted. Restored to system default."}

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error restoring default: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

