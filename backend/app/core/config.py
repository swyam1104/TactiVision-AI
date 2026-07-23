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
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/tactivision"
    REDIS_URL: str = "redis://redis:6379/0"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Model storage paths
    XG_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "ml" / "xg_model" / "xg_model.pkl")
    SIMILARITY_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "ml" / "similarity" / "similarity.pkl")
    RAG_INDEX_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "ml" / "rag" / "faiss_index")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.XG_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.SIMILARITY_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.RAG_INDEX_PATH), exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
