import os
import sys
import gzip
import shutil
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent

def _get_default_db_url() -> str:
    # 1. Check if an external /data/tactivision.db exists (e.g. mounted persistent volume)
    if Path("/data/tactivision.db").exists():
        return "sqlite:////data/tactivision.db"
    
    local_db = _BASE_DIR / "tactivision.db"
    local_db_gz = _BASE_DIR / "tactivision.db.gz"

    # Automatically decompress tactivision.db.gz if tactivision.db is not extracted yet
    if not local_db.exists() and local_db_gz.exists():
        try:
            with gzip.open(local_db_gz, "rb") as f_in:
                with open(local_db, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception:
            pass

    # 2. Check local database in backend folder (/app/tactivision.db in container or local backend/tactivision.db)
    if local_db.exists():
        return f"sqlite:///{str(local_db).replace(os.sep, '/')}"
    # 3. Default fallback
    return f"sqlite:///{str(local_db).replace(os.sep, '/')}"

def _resolve_model_path(subfolder: str, filename: str) -> str:
    local_path = _BASE_DIR / "ml" / subfolder / filename
    if local_path.exists():
        return str(local_path)
    if Path(f"/data/{filename}").exists():
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
