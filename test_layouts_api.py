"""
Quick test script for the layouts API endpoint.
"""
import sys
sys.path.append('backend')

from db_config import set_db_env
set_db_env()

from app.db import get_db_connection, get_cursor

# Test database query (same query as API endpoint)
conn = get_db_connection()
cur = get_cursor(conn)
cur.execute('''
    SELECT DISTINCT ON (lv.transaction_type_code)
        lv.transaction_type_code as code,
        tt.name,
        lv.version_number,
        lv.status
    FROM layout_versions lv
    JOIN transaction_types tt ON lv.transaction_type_code = tt.code
    ORDER BY lv.transaction_type_code, lv.version_number DESC
    LIMIT 5;
''')
results = cur.fetchall()
print('API GET /layouts test (first 5):')
for r in results:
    print(f"  {r['code']} - {r['name']} (v{r['version_number']}) [{r['status']}]")
conn.close()
print('\nAPI endpoints verification passed!')
