import os
import sys
import psycopg2
from dotenv import load_dotenv

def run_migration():
    """
    Runs the migration to add the formats column to email_routes.
    Accessible from start.py or direct execution.
    """
    # Try loading from local.env or backend/.env if not in production
    # In production (Railway), env vars are usually pre-loaded, but this is safe
    env_path = os.path.join(os.getcwd(), 'local.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), 'backend', '.env')
        if not os.path.exists(env_path):
             env_path = os.path.join(os.getcwd(), '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not found. Skipping migration (might be build step).")
        return

    print(f"Connecting to database to run migrations...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking/Adding 'formats' column to email_routes...")
        # Idempotent SQL
        sql = "ALTER TABLE email_routes ADD COLUMN IF NOT EXISTS formats TEXT[];"
        
        cur.execute(sql)
        conn.commit()
        
        print("Migration successful! Column 'formats' verified.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration Error: {e}")
        # We don't exit(1) here to avoid crashing the whole app start if DB is transiently down,
        # but for schema changes it might be better to crash. 
        # For now, let's print error but allow app to try starting (or uvicorn will fail if DB is truly down).
        pass

if __name__ == "__main__":
    run_migration()
