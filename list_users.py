"""List all users in the database."""
import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

conn = get_db_connection()
cur = get_cursor(conn)

cur.execute("SELECT id, email, role FROM users LIMIT 20")
rows = cur.fetchall()

if rows:
    print("Users in database:")
    for row in rows:
        print(f"  {row['email']} | role: {row['role'] or 'user'}")
else:
    print("No users found in the database")

conn.close()
