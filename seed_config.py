import os

def set_db_env():
    """
    Set DATABASE_URL from environment or .env file.
    DO NOT commit credentials to this file.
    """
    if os.environ.get("DATABASE_URL"):
        return
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    if not os.environ.get("DATABASE_URL"):
        raise ValueError("DATABASE_URL environment variable is not set. Create a .env file with DATABASE_URL=your_connection_string")
