"""
Test User Sync Logic Locally with ID Rotation
"""
import sys
import uuid
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

def test_sync_logic():
    print("Testing user sync logic...")
    
    # 1. Create initial user
    email = "test.collision@example.com"
    old_id = str(uuid.uuid4())
    name = "Old User Name"
    
    conn = None
    try:
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Cleanup first
        cur.execute("DELETE FROM users WHERE email = %s", (email,))
        conn.commit()
        
        print(f"Creating initial user {email} (ID: {old_id})...")
        cur.execute("""
            INSERT INTO users (id, email, name, role, created_at)
            VALUES (%s, %s, %s, 'user', NOW())
        """, (old_id, email, name))
        conn.commit()
        
        # 2. Simulate Sync with NEW ID (Supabase ID rotation)
        new_id = str(uuid.uuid4())
        print(f"Attempting sync with NEW ID {new_id} (same email)...")
        
        # Logic from backend/app/api/routes/users.py
        # Check if user exists by email first
        cur.execute("SELECT id, role FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            if existing_user['id'] != new_id:
                print(f"Migrating user {email} from ID {existing_user['id']} to {new_id}")
                cur.execute("""
                    UPDATE users 
                    SET id = %s, name = %s
                    WHERE email = %s
                    RETURNING id, email, name, role
                """, (new_id, "New User Name", email))
            else:
                 print("IDs match (unexpected for test)")
        else:
            print("User not found (unexpected for test)")
            
        result = cur.fetchone()
        conn.commit()
        
        print("\n✅ Success!")
        print(f"User synced: {result}")
        print(f"Old ID: {old_id}")
        print(f"New ID: {result['id']}")
        assert result['id'] == new_id
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_sync_logic()
