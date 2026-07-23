import os
import threading
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.models.models import Match
from app.core.database import SessionLocal
from ml.etl.ingest import run_pipeline
from ml.xg_model.train import train_and_evaluate
from ml.similarity.train_similarity import train_similarity_model

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

def initialize_database_and_models():
    """Background startup task to create tables and pre-populate if empty."""
    logger.info("Verifying database tables...")
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if database is empty
        db = SessionLocal()
        try:
            match_count = db.query(Match).count()
            if match_count == 0:
                logger.info("Database is empty. Initiating automatic data ingestion pipeline...")
                # Run ingestion inline for startup, or in thread.
                # In thread prevents blocking FastAPI startup and allows fast health check reporting
                run_pipeline()
                logger.info("Startup data ingestion complete. Training models...")
                train_and_evaluate()
                train_similarity_model()
                logger.info("Startup training complete.")
            else:
                logger.info(f"Database verified. Found {match_count} matches.")
                
            # Check if models exist, if not, train them
            if not os.path.exists(settings.XG_MODEL_PATH) or not os.path.exists(settings.SIMILARITY_MODEL_PATH):
                logger.info("ML Models missing. Triggering initial training...")
                train_and_evaluate()
                train_similarity_model()
                logger.info("ML Model initialization complete.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Startup database initialization failed: {e}")

@app.on_event("startup")
def startup_event():
    """Initialize DB and models on startup."""
    # Run the database initialization in a separate thread so the server starts immediately
    thread = threading.Thread(target=initialize_database_and_models)
    thread.start()
