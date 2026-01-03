"""Migration: Add name column to users table."""
import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

def run_migration():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    try:
        print("Checking for 'name' column in users table...")
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'name'
        """)
        if not cur.fetchone():
            print("Adding 'name' column...")
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN name VARCHAR(255)
            """)
            conn.commit()
            print("✅ Added 'name' column successfully!")
        else:
            print("ℹ️ 'name' column already exists")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
