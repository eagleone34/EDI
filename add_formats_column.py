import os
import sys
import psycopg2
from dotenv import load_dotenv

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

def run_migration():
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Adding formats column to email_routes...")
        # Use simple array types for Supabase/Postgres
        sql = "ALTER TABLE email_routes ADD COLUMN IF NOT EXISTS formats TEXT[];"
        
        cur.execute(sql)
        conn.commit()
        
        print("Migration successful! Column 'formats' added.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
