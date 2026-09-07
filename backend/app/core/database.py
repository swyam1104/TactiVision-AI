from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

import os
import logging

logger = logging.getLogger(__name__)

# Create engine with active connection check and fallback support
db_url = settings.DATABASE_URL

def _init_engine():
    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})
    
    try:
        test_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 2}
        )
        with test_engine.connect() as conn:
            pass
        return test_engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection to {db_url} failed: {e}. Falling back to local SQLite database.")
        # Use /data volume on Railway, local path for dev
        data_dir = "/data" if os.path.isdir("/data") and os.access("/data", os.W_OK) else \
                   os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_path = os.path.join(data_dir, "tactivision.db")
        return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

engine = _init_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that yields a database session.
    Ensures session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
