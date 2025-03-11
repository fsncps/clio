from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Load DB connection string from environment variable or use a default fallback
DB_URL = os.getenv("CLIO_DB_URL")

# Ensure pymysql is used as the driver
if DB_URL.startswith("mysql://"):
    DB_URL = DB_URL.replace("mysql://", "mysql+pymysql://", 1)

# Create the database engine
engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)

# Create a session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function for getting a database session
def get_db():
    """Yield a new database session and ensure it closes properly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

