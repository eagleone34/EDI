from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base_class import Base

# Import all models so they are registered with Base
from app.models.user import User, VerificationCode, Conversion
from app.models.integration import Integration, RoutingRule

# Create engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create database tables if they don't exist and run migrations."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    
    # Run layout migrations on startup
    try:
        from app.db import get_db_connection, get_cursor
        from app.core.migrations import run_layout_migrations, run_schema_migrations
        
        conn = get_db_connection()
        cur = get_cursor(conn)
        
        # Run schema migrations (creates missing tables)
        run_schema_migrations(conn, cur)
        
        # Run layout migrations
        run_layout_migrations(conn, cur)
        
        conn.close()
        print("Database migrations completed successfully.")
    except Exception as e:
        print(f"Layout migration warning: {e}")

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
