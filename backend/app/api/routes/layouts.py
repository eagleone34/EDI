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
async def get_all_layouts():
    """
    Get list of all layout configurations with their current status.
    Returns one entry per transaction type (the active/latest version).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Get the latest version for each transaction type
        query = """
            SELECT DISTINCT ON (lv.transaction_type_code)
                lv.transaction_type_code as code,
                tt.name,
                lv.version_number,
                lv.status,
                lv.is_active,
                lv.updated_at
            FROM layout_versions lv
            JOIN transaction_types tt ON lv.transaction_type_code = tt.code
            ORDER BY lv.transaction_type_code, lv.version_number DESC;
        """
        cur.execute(query)
        results = cur.fetchall()
        
        return [LayoutSummary(**row) for row in results]
        
    except Exception as e:
        print(f"Error fetching layouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/{type_code}", response_model=LayoutDetail)
async def get_layout(type_code: str):
    """
    Get the full layout configuration for a specific transaction type.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        query = """
            SELECT 
                lv.transaction_type_code as code,
                tt.name,
                lv.version_number,
                lv.status,
                lv.is_active,
                lv.config_json,
                lv.updated_at
            FROM layout_versions lv
            JOIN transaction_types tt ON lv.transaction_type_code = tt.code
            WHERE lv.transaction_type_code = %s
            ORDER BY lv.version_number DESC
            LIMIT 1;
        """
        cur.execute(query, (type_code,))
        result = cur.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Layout for {type_code} not found")
        
        return LayoutDetail(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching layout {type_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.put("/{type_code}", response_model=LayoutDetail)
async def update_layout(type_code: str, request: LayoutUpdateRequest):
    """
    Update the layout configuration for a transaction type.
    Creates a new DRAFT version if the current version is PRODUCTION.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Get current version info
        cur.execute("""
            SELECT version_number, status 
            FROM layout_versions 
            WHERE transaction_type_code = %s 
            ORDER BY version_number DESC 
            LIMIT 1;
        """, (type_code,))
        current = cur.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail=f"Layout for {type_code} not found")
        
        current_version = current['version_number']
        current_status = current['status']
        
        if current_status == 'PRODUCTION':
            # Create a new DRAFT version
            new_version = current_version + 1
            cur.execute("""
                INSERT INTO layout_versions 
                (transaction_type_code, version_number, status, config_json, is_active, created_by, updated_at)
                VALUES (%s, %s, 'DRAFT', %s, false, 'admin', NOW())
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at;
            """, (type_code, new_version, json.dumps(request.config_json)))
        else:
            # Update existing DRAFT version
            cur.execute("""
                UPDATE layout_versions 
                SET config_json = %s, updated_at = NOW()
                WHERE transaction_type_code = %s AND version_number = %s
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at;
            """, (json.dumps(request.config_json), type_code, current_version))
        
        conn.commit()
        result = cur.fetchone()
        
        # Fetch name from transaction_types
        cur.execute("SELECT name FROM transaction_types WHERE code = %s;", (type_code,))
        type_info = cur.fetchone()
        
        return LayoutDetail(
            code=result['code'],
            name=type_info['name'] if type_info else type_code,
            version_number=result['version_number'],
            status=result['status'],
            is_active=result['is_active'],
            config_json=result['config_json'],
            updated_at=result['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating layout {type_code}: {e}")
        if conn:
            conn.rollback()
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

