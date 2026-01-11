"""
Admin API Router

Superadmin-only endpoints for platform analytics, user activity, and system health.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.db import get_db_connection, get_cursor

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class OverviewStats(BaseModel):
    """Platform overview statistics."""
    total_users: int
    active_users_7d: int
    active_users_30d: int
    total_conversions: int
    conversions_today: int
    conversions_week: int
    conversions_month: int
    new_users_7d: int


class ConversionsByType(BaseModel):
    """Conversion breakdown by transaction type."""
    transaction_type: str
    count: int
    percentage: float


class ActivityItem(BaseModel):
    """Single activity log entry."""
    id: int
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    details: dict
    created_at: datetime


class UserActivity(BaseModel):
    """User with activity stats."""
    id: str
    email: str
    name: Optional[str]
    role: str
    conversion_count: int
    last_active_at: Optional[datetime]
    created_at: datetime


class SystemHealth(BaseModel):
    """System health indicators."""
    database_connected: bool
    total_users: int
    total_conversions: int
    email_errors_24h: int
    recent_errors: List[dict]


# ============================================================================
# Helper Functions
# ============================================================================

def log_activity(
    user_id: Optional[str],
    user_email: Optional[str],
    action: str,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    """
    Log a user activity event.
    Call this from other routes to track actions.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            INSERT INTO activity_log (user_id, user_email, action, details, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, user_email, action, details or {}, ip_address, user_agent))
        
        # Also update user's last_active_at
        if user_id:
            cur.execute("""
                UPDATE users SET last_active_at = NOW() WHERE id = %s
            """, (user_id,))
        
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_stats():
    """Get platform overview statistics (superadmin only)."""
    conn = None
    supabase_conn = None
    try:
        from app.core.config import settings
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Total users from Railway DB
        cur.execute("SELECT COUNT(*) as count FROM users")
        total_users = cur.fetchone()["count"]
        
        # Active users (users with last_active_at in last 7 days)
        cur.execute("""
            SELECT COUNT(*) as count FROM users
            WHERE last_active_at > NOW() - INTERVAL '7 days'
        """)
        active_7d = cur.fetchone()["count"]
        
        # Active users (last 30 days)
        cur.execute("""
            SELECT COUNT(*) as count FROM users
            WHERE last_active_at > NOW() - INTERVAL '30 days'
        """)
        active_30d = cur.fetchone()["count"]
        
        # New users this week
        cur.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE created_at > NOW() - INTERVAL '7 days'
        """)
        new_users_7d = cur.fetchone()["count"]
        
        # Get conversion stats from Supabase documents table
        total_conversions = 0
        conversions_today = 0
        conversions_week = 0
        conversions_month = 0
        
        supabase_db_url = settings.SUPABASE_DB_URL
        if supabase_db_url:
            try:
                supabase_conn = psycopg2.connect(supabase_db_url)
                supabase_cur = supabase_conn.cursor(cursor_factory=RealDictCursor)
                
                # Total conversions
                supabase_cur.execute("SELECT COUNT(*) as count FROM documents")
                total_conversions = supabase_cur.fetchone()["count"]
                
                # Conversions today
                supabase_cur.execute("""
                    SELECT COUNT(*) as count FROM documents 
                    WHERE created_at > CURRENT_DATE
                """)
                conversions_today = supabase_cur.fetchone()["count"]
                
                # Conversions this week
                supabase_cur.execute("""
                    SELECT COUNT(*) as count FROM documents 
                    WHERE created_at > NOW() - INTERVAL '7 days'
                """)
                conversions_week = supabase_cur.fetchone()["count"]
                
                # Conversions this month
                supabase_cur.execute("""
                    SELECT COUNT(*) as count FROM documents 
                    WHERE created_at > NOW() - INTERVAL '30 days'
                """)
                conversions_month = supabase_cur.fetchone()["count"]
                
            except Exception as e:
                print(f"Error querying Supabase: {e}")
            finally:
                if supabase_conn:
                    supabase_conn.close()
        
        return OverviewStats(
            total_users=total_users,
            active_users_7d=active_7d,
            active_users_30d=active_30d,
            total_conversions=total_conversions,
            conversions_today=conversions_today,
            conversions_week=conversions_week,
            conversions_month=conversions_month,
            new_users_7d=new_users_7d
        )
        
    except Exception as e:
        print(f"Error fetching overview stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/stats/conversions-by-type", response_model=List[ConversionsByType])
async def get_conversions_by_type(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """Get conversion breakdown by transaction type from Supabase documents."""
    supabase_conn = None
    try:
        from app.core.config import settings
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        supabase_db_url = settings.SUPABASE_DB_URL
        if not supabase_db_url:
            return []
        
        supabase_conn = psycopg2.connect(supabase_db_url)
        cur = supabase_conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                transaction_type,
                COUNT(*) as count
            FROM documents 
            WHERE created_at > NOW() - INTERVAL '%s days'
              AND transaction_type IS NOT NULL
            GROUP BY transaction_type
            ORDER BY count DESC
        """, (days,))
        
        results = cur.fetchall()
        total = sum(r["count"] for r in results) if results else 0
        
        return [
            ConversionsByType(
                transaction_type=r["transaction_type"] or "unknown",
                count=r["count"],
                percentage=round(r["count"] / total * 100, 1) if total > 0 else 0
            )
            for r in results
        ]
        
    except Exception as e:
        print(f"Error fetching conversions by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if supabase_conn:
            supabase_conn.close()


@router.get("/stats/activity", response_model=List[ActivityItem])
async def get_activity_feed(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """Get recent activity feed with pagination."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        query = """
            SELECT id, user_id, user_email, action, details, created_at
            FROM activity_log
            WHERE 1=1
        """
        params = []
        
        if action:
            query += " AND action = %s"
            params.append(action)
        
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        return [
            ActivityItem(
                id=r["id"],
                user_id=r["user_id"],
                user_email=r["user_email"],
                action=r["action"],
                details=r["details"] or {},
                created_at=r["created_at"]
            )
            for r in results
        ]
        
    except Exception as e:
        print(f"Error fetching activity feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/stats/users", response_model=List[UserActivity])
async def get_user_activity_stats(
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("conversion_count", description="Sort by: conversion_count, last_active, created_at")
):
    """Get users with their activity statistics."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Get users with conversion counts
        order_clause = {
            "conversion_count": "conversion_count DESC",
            "last_active": "last_active_at DESC NULLS LAST",
            "created_at": "created_at DESC"
        }.get(sort_by, "conversion_count DESC")
        
        cur.execute(f"""
            SELECT 
                u.id, u.email, u.name, u.role, u.last_active_at, u.created_at,
                COALESCE(
                    (SELECT COUNT(*) FROM activity_log WHERE user_id = u.id AND action = 'conversion'),
                    0
                ) as conversion_count
            FROM users u
            ORDER BY {order_clause}
            LIMIT %s
        """, (limit,))
        
        results = cur.fetchall()
        
        return [
            UserActivity(
                id=r["id"],
                email=r["email"],
                name=r["name"],
                role=r["role"] or "user",
                conversion_count=r["conversion_count"],
                last_active_at=r["last_active_at"],
                created_at=r["created_at"]
            )
            for r in results
        ]
        
    except Exception as e:
        print(f"Error fetching user activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health indicators."""
    conn = None
    db_connected = False
    total_users = 0
    total_conversions = 0
    email_errors = 0
    recent_errors = []
    
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        db_connected = True
        
        # Total users
        cur.execute("SELECT COUNT(*) as count FROM users")
        total_users = cur.fetchone()["count"]
        
        # Total conversions from Supabase
        total_conversions = 0
        try:
            from app.core.config import settings
            import psycopg2 as pg
            from psycopg2.extras import RealDictCursor as RDC
            if settings.SUPABASE_DB_URL:
                supa_conn = pg.connect(settings.SUPABASE_DB_URL)
                supa_cur = supa_conn.cursor(cursor_factory=RDC)
                supa_cur.execute("SELECT COUNT(*) as count FROM documents")
                total_conversions = supa_cur.fetchone()["count"]
                supa_conn.close()
        except Exception as se:
            print(f"Error getting Supabase conversions: {se}")
        
        # Email errors in last 24h
        cur.execute("""
            SELECT COUNT(*) as count FROM inbound_email_errors 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        email_errors = cur.fetchone()["count"]
        
        # Recent errors (last 10)
        cur.execute("""
            SELECT id, user_id, raw_email_snippet, error_message, created_at
            FROM inbound_email_errors
            ORDER BY created_at DESC
            LIMIT 10
        """)
        errors = cur.fetchall()
        recent_errors = [
            {
                "id": e["id"],
                "user_id": e["user_id"],
                "snippet": (e["raw_email_snippet"] or "")[:100],
                "error": e["error_message"],
                "created_at": e["created_at"].isoformat() if e["created_at"] else None
            }
            for e in errors
        ]
        
    except Exception as e:
        print(f"Error fetching system health: {e}")
        # Don't raise - return partial data with db_connected = False
    finally:
        if conn:
            conn.close()
    
    return SystemHealth(
        database_connected=db_connected,
        total_users=total_users,
        total_conversions=total_conversions,
        email_errors_24h=email_errors,
        recent_errors=recent_errors
    )


@router.get("/stats/daily-conversions")
async def get_daily_conversions(
    days: int = Query(30, ge=1, le=90, description="Number of days")
):
    """Get daily conversion counts for charting."""
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        cur.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM activity_log
            WHERE action = 'conversion'
              AND created_at > NOW() - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """, (days,))
        
        results = cur.fetchall()
        
        return [
            {"date": r["date"].isoformat(), "count": r["count"]}
            for r in results
        ]
        
    except Exception as e:
        print(f"Error fetching daily conversions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
