import os

def set_db_env():
    """
    Set DATABASE_URL from environment or local.env file.
    DO NOT commit credentials to this file.
    """
    if os.environ.get("DATABASE_URL"):
        return
    
    try:
        from dotenv import load_dotenv
        load_dotenv("local.env")
    except ImportError:
        pass
    
    if not os.environ.get("DATABASE_URL"):
        raise ValueError("DATABASE_URL environment variable is not set. Add DATABASE_URL to local.env file.")

