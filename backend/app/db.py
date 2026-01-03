import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

def get_db_connection():
    """Create a new database connection."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    return conn

def get_cursor(conn):
    """Get a dict cursor from connection."""
    return conn.cursor(cursor_factory=RealDictCursor)
