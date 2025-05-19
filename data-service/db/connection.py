import os
from dotenv import load_dotenv

# Load environment variables at the very top
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL from environment, preferring Railway's internal URL in production
DATABASE_URL = os.getenv('DATABASE_URL')  # Railway's internal URL in production
if not DATABASE_URL:
    # Fall back to public connection string for local development
    DATABASE_URL = os.getenv('PUBLIC_DATA_SERVICE_DB_CONNECTION_STRING')

if not DATABASE_URL:
    raise ValueError("Neither DATABASE_URL nor PUBLIC_DATA_SERVICE_DB_CONNECTION_STRING environment variables are set")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables.
    """
    from .models import Base
    Base.metadata.create_all(bind=engine) 