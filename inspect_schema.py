
import sys
import os

# Add backend to path to import app.db
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app.db import get_db_connection
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    table_name = 'layout_versions'
    
    # Query columns
    cur.execute(f"""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
    """)
    
    print(f"Schema for {table_name}:")
    for row in cur.fetchall():
        print(row)
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
