
import sys
import os
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))


from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

def debug_documents():
    print("Connecting to database...")
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    try:
        # Fetch latest 5 documents
        print("\nFetching latest 5 documents...")
        cur.execute("""
            SELECT 
                id, 
                user_id, 
                filename, 
                transaction_type, 
                transaction_name, 
                trading_partner,
                source, 
                created_at,
                LENGTH(pdf_url) as pdf_len,
                LENGTH(html_url) as html_len
            FROM documents 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        if not rows:
            print("No documents found!")
        else:
            for row in rows:
                print("-" * 50)
                # Row is already a RealDictRow (accessible as dict)
                # Convert to standard dict for json serialization
                row_dict = dict(row)
                
                # Handle datetime serialization
                for k, v in row_dict.items():
                    if isinstance(v, datetime):
                        row_dict[k] = v.isoformat()
                        
                print(json.dumps(row_dict, indent=2))
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_documents()
