"""Set superadmin role for a specific user."""
import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

conn = get_db_connection()
cur = get_cursor(conn)

cur.execute("""
    UPDATE users 
    SET role = 'superadmin' 
    WHERE email = 'mazen.alashkar@gmail.com'
    RETURNING email, role
""")

result = cur.fetchone()
conn.commit()

if result:
    print(f"✅ Updated: {result['email']} → {result['role']}")
else:
    print("❌ No user found with that email")

conn.close()
