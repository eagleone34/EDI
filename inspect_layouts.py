"""
Script to inspect layout_versions table and identify duplicates
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import get_db_connection, get_cursor

def inspect_layouts():
    conn = get_db_connection()
    cur = get_cursor(conn)
    
    print("=" * 80)
    print("1. All entries in transaction_types table:")
    print("=" * 80)
    cur.execute("SELECT code, name FROM transaction_types ORDER BY code")
    for row in cur.fetchall():
        print(f"  {row['code']}: {row['name']}")
    
    print("\n" + "=" * 80)
    print("2. All layout_versions entries (checking for duplicates):")
    print("=" * 80)
    cur.execute("""
        SELECT id, transaction_type_code, version_number, status, is_active, user_id, created_by
        FROM layout_versions 
        ORDER BY transaction_type_code, user_id, version_number
    """)
    for row in cur.fetchall():
        user_str = row['user_id'][:8] if row['user_id'] else 'SYSTEM'
        print(f"  ID:{row['id']} | {row['transaction_type_code']} v{row['version_number']} | {row['status']:12} | active:{row['is_active']} | user:{user_str}")
    
    print("\n" + "=" * 80)
    print("3. Check for duplicate transaction_type codes:")
    print("=" * 80)
    cur.execute("""
        SELECT code, COUNT(*) as count 
        FROM transaction_types 
        GROUP BY code 
        HAVING COUNT(*) > 1
    """)
    dups = cur.fetchall()
    if dups:
        for row in dups:
            print(f"  DUPLICATE: {row['code']} appears {row['count']} times!")
    else:
        print("  No duplicates in transaction_types")
    
    print("\n" + "=" * 80)
    print("4. Check for multiple system layouts per transaction type:")
    print("=" * 80)
    cur.execute("""
        SELECT transaction_type_code, COUNT(*) as count, array_agg(status) as statuses
        FROM layout_versions 
        WHERE user_id IS NULL
        GROUP BY transaction_type_code
        HAVING COUNT(*) > 1
    """)
    multi = cur.fetchall()
    if multi:
        for row in multi:
            print(f"  {row['transaction_type_code']}: {row['count']} versions - {row['statuses']}")
    else:
        print("  Each transaction type has at most 1 system layout")
    
    conn.close()

if __name__ == "__main__":
    inspect_layouts()
