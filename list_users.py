"""List all users in the database."""
import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

def list_users():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    try:
        cur.execute("SELECT id, email, role, name FROM users")
        users = cur.fetchall()
        
        if not users:
            print("No users found in the database")
        else:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user['id']}")
                print(f"Email: {user['email']}")
                print(f"Role: {user['role']}")
                print(f"Name: {user['name']}")
                print("-" * 30)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_users()
