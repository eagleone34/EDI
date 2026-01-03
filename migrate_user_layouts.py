"""
Migration Script: Add user roles and per-user layouts

This script:
1. Adds 'role' column to users table
2. Adds 'user_id' column to layout_versions table
3. Sets your account as superadmin
"""

import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

def run_migration():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    try:
        # 1. Check if role column exists in users
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role'
        """)
        if not cur.fetchone():
            print("Adding 'role' column to users table...")
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(20) DEFAULT 'user'
            """)
            print("  ✓ Added role column")
        else:
            print("  ✓ role column already exists")
        
        # 2. Check if user_id column exists in layout_versions
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'layout_versions' AND column_name = 'user_id'
        """)
        if not cur.fetchone():
            print("Adding 'user_id' column to layout_versions table...")
            cur.execute("""
                ALTER TABLE layout_versions 
                ADD COLUMN user_id VARCHAR(255) REFERENCES users(id)
            """)
            print("  ✓ Added user_id column (NULL = system default)")
        else:
            print("  ✓ user_id column already exists")
        
        # 3. Set your account as superadmin
        cur.execute("""
            UPDATE users SET role = 'superadmin' 
            WHERE email LIKE '%mazen%' OR email LIKE '%admin%'
            RETURNING email
        """)
        updated = cur.fetchall()
        if updated:
            for row in updated:
                print(f"  ✓ Set {row['email']} as superadmin")
        else:
            print("  ⚠ No admin accounts found to upgrade")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show current schema
        print("\nCurrent layout_versions columns:")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'layout_versions' 
            ORDER BY ordinal_position
        """)
        for row in cur.fetchall():
            print(f"  {row['column_name']}: {row['data_type']}")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
