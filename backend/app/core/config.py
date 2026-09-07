import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TactiVision AI"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ML_DIR: Path = BASE_DIR / "ml"
    
    # DB & Redis Connection
    # On Railway: set DATABASE_URL env var to sqlite:////data/tactivision.db
    # Locally: auto-falls-back to SQLite in the backend folder
    DATABASE_URL: str = "sqlite:////data/tactivision.db"
    REDIS_URL: str = "redis://redis:6379/0"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Model storage paths — /data volume on Railway, fallback to local ml/ dir for dev
    XG_MODEL_PATH: str = "/data/xg_model.pkl"
    SIMILARITY_MODEL_PATH: str = "/data/similarity.pkl"
    RAG_INDEX_PATH: str = "/data/faiss_index"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()

# Ensure directories exist (works both locally and on Railway /data volume)
try:
    os.makedirs("/data", exist_ok=True)
except PermissionError:
    pass  # Running locally without /data write access — fine

os.makedirs(os.path.dirname(settings.XG_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.SIMILARITY_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.RAG_INDEX_PATH), exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
