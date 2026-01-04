import sys
import os
import json
import traceback

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import get_db_connection, get_cursor

# Mock data
type_code = '810'
user_id = 'ab5b8832-af5d-48a5-a49b-5b08d509f6d6'
config = {"test_debug": "data"}

def test_update():
    print("Connecting...")
    conn = get_db_connection()
    cur = get_cursor(conn)
    print("Connected.")
    try:
        # 1. Check existing
        params = (type_code, user_id)
        user_filter = "AND user_id = %s"
        
        print("Checking existing draft...")
        cur.execute(f"""
            SELECT version_number, status 
            FROM layout_versions 
            WHERE transaction_type_code = %s {user_filter}
            ORDER BY version_number DESC 
            LIMIT 1;
        """, params)
        current = cur.fetchone()
        print(f"Current: {current}")
        
        should_create_new = False
        current_version = 0
        
        if not current:
            should_create_new = True
        else:
            current_version = current['version_number']
            if current['status'] == 'PRODUCTION':
                should_create_new = True
        
        print(f"Should create new: {should_create_new}")
        
        result = None
        if should_create_new:
            print("Fetching Max Version...")
            cur.execute("SELECT COALESCE(MAX(version_number), 0) FROM layout_versions WHERE transaction_type_code = %s", (type_code,))
            max_ver = cur.fetchone()[0]
            new_version = max_ver + 1
            print(f"New Version: {new_version}")
            
            creator = 'user' if user_id else 'admin'
            
            print("Inserting...")
            cur.execute("""
                INSERT INTO layout_versions 
                (transaction_type_code, version_number, status, config_json, is_active, created_by, updated_at, user_id)
                VALUES (%s, %s, 'DRAFT', %s, false, %s, NOW(), %s)
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at;
            """, (type_code, new_version, json.dumps(config), creator, user_id))
        else:
            print("Updating...")
            cur.execute(f"""
                UPDATE layout_versions 
                SET config_json = %s, updated_at = NOW()
                WHERE transaction_type_code = %s AND version_number = %s {user_filter}
                RETURNING transaction_type_code as code, version_number, status, is_active, config_json, updated_at;
            """, (json.dumps(config), type_code, current_version, user_id))
            
        result = cur.fetchone()
        print(f"Result raw: {result}")
        
        if result:
            conn.commit()
            print("Committed.")
            
            # Simulate LayoutDetail creation
            is_personal = bool(user_id and result.get('user_id') == user_id)
            print(f"Calculated is_personal: {is_personal}")
            
            print("Success!")
        else:
            print("Result is None!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_update()
