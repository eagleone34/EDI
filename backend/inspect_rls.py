import sys
import os

# Add backend to path (current dir)
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Add root to path for db_config
root_dir = os.path.dirname(backend_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    import db_config
    from app.db import get_db_connection
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def inspect_rls_policies():
    print("Setting up environment...")
    
    original_cwd = os.getcwd()
    try:
        os.chdir(root_dir)
        try:
            db_config.set_db_env()
        except Exception as e:
            pass
    finally:
        os.chdir(original_cwd)

    if not os.environ.get("DATABASE_URL"):
        print("ERROR: DATABASE_URL not found!")
        return

    print("Connecting to database...")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if RLS is enabled
        print("\n--- RLS Status ---")
        cur.execute("""
            SELECT relname, relrowsecurity 
            FROM pg_class 
            WHERE relname = 'documents';
        """)
        rls_status = cur.fetchone()
        if rls_status:
             print(f"Table 'documents' RLS enabled: {rls_status[1]}")
        
        # List Policies
        print("\n--- RLS Policies ---")
        cur.execute("""
            SELECT polname, polcmd, polroles, polqual, polwithcheck
            FROM pg_policy
            WHERE polrelid = 'documents'::regclass;
        """)
        policies = cur.fetchall()
        for pol in policies:
            print(f"Policy: {pol[0]}")
            print(f"  Command: {pol[1]}")
            print(f"  Roles: {pol[2]}")
            print(f"  Qual (USING): {pol[3]}")
            print(f"  Check (WITH CHECK): {pol[4]}")
            print("-" * 20)

    except Exception as e:
        print(f"Error inspecting RLS: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_rls_policies()
