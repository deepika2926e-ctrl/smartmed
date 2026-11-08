import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL.strip()

# Create SQLAlchemy engine with graceful connection handling
try:
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
    else:
        # MySQL or PostgreSQL connection
        engine = create_engine(
            db_url,
            pool_recycle=3600,
            pool_pre_ping=True
        )
        # Test connection immediately
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to primary database: {db_url.split('@')[-1] if '@' in db_url else 'database'}")
except Exception as e:
    logger.warning(
        f"Could not connect to primary database ({e}). "
        f"Falling back to local SQLite database 'smartmed.db' for seamless local development without XAMPP."
    )
    sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "smartmed.db"))
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
