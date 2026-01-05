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

def reload_schema():
    print("Setting up environment...")
    
    # Change CWD to root so dotenv finds local.env
    original_cwd = os.getcwd()
    try:
        os.chdir(root_dir)
        print(f"Changed CWD to: {os.getcwd()}")
        
        try:
            db_config.set_db_env()
        except Exception as e:
            # If it fails, print but check env var anyway (maybe passed via shell)
            print(f"Warning setting env: {e}")
            
    finally:
        os.chdir(original_cwd)

    # Now verify DATABASE_URL is set
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not found in environment or local.env!")
        return

    # Masking password for log safety
    safe_url = url.split("@")[-1] if "@" in url else "..."
    print(f"Connecting to database: ...@{safe_url}")
    
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Executing NOTIFY pgrst, 'reload schema'...")
        cur.execute("NOTIFY pgrst, 'reload schema';")
        
        print("Schema reload notification sent successfully.")
        
    except Exception as e:
        print(f"Error executing reload: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reload_schema()
