import os

def set_db_env():
    """
    Set DATABASE_URL from environment or local.env file.
    DO NOT commit credentials to this file.
    """
    # Check if already set (e.g., from Railway env vars)
    if os.environ.get("DATABASE_URL"):
        return
    
    # For local development, load from local.env file
    try:
        from dotenv import load_dotenv
        load_dotenv("local.env")
    except ImportError:
        pass
    
    if not os.environ.get("DATABASE_URL"):
        raise ValueError("DATABASE_URL environment variable is not set. Add DATABASE_URL to local.env file.")

