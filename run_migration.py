import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from seed_config import set_db_env
    set_db_env()
    print("Loaded DB config from seed_config.py")
except ImportError:
    pass

# Try loading from local.env first, as it was found in the root
env_path = os.path.join(os.getcwd(), 'local.env')
if not os.path.exists(env_path):
    # Fallback to backend/.env
    env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables.")
    sys.exit(1)

SQL_FILE = r"C:\Users\mazen\.gemini\antigravity\brain\d84e5431-7c88-4e47-91e7-33eb860095a1\phase2_schema.sql"

def run_migration():
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print(f"Reading SQL from {SQL_FILE}...")
        with open(SQL_FILE, 'r') as f:
            sql = f.read()
            
        print("Executing SQL...")
        cur.execute(sql)
        conn.commit()
        
        print("Migration successful! Tables created.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
