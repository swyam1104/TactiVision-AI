from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "tactivision",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["ml.etl.ingest", "ml.xg_model.train", "ml.similarity.train_similarity"]
)

# Optional configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
