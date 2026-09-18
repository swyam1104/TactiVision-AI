import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent

def _get_default_db_url() -> str:
    # If running on Linux container with /data mount (e.g. Railway volume):
    if sys.platform != "win32" and Path("/data").is_dir():
        return "sqlite:////data/tactivision.db"
    # Otherwise default to the local SQLite database in the backend folder
    local_db = _BASE_DIR / "tactivision.db"
    return f"sqlite:///{str(local_db).replace(os.sep, '/')}"

def _resolve_model_path(subfolder: str, filename: str) -> str:
    local_path = _BASE_DIR / "ml" / subfolder / filename
    if local_path.exists():
        return str(local_path)
    if sys.platform != "win32" and Path("/data").is_dir():
        return f"/data/{filename}"
    return str(local_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "TactiVision AI"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = _BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    ML_DIR: Path = BASE_DIR / "ml"
    
    # DB & Redis Connection
    DATABASE_URL: str = _get_default_db_url()
    REDIS_URL: str = "redis://redis:6379/0"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Model storage paths (auto-resolves local ml/ dir or production /data mount)
    XG_MODEL_PATH: str = _resolve_model_path("xg_model", "xg_model.pkl")
    SIMILARITY_MODEL_PATH: str = _resolve_model_path("similarity", "similarity.pkl")
    RAG_INDEX_PATH: str = _resolve_model_path("rag", "faiss_index")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()

# Ensure directories exist
if sys.platform != "win32" and Path("/data").is_dir():
    try:
        os.makedirs("/data", exist_ok=True)
    except PermissionError:
        pass

os.makedirs(os.path.dirname(settings.XG_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.SIMILARITY_MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.RAG_INDEX_PATH), exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
