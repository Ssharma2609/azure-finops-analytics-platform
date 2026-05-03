"""
Celery application configuration.
"""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "azure_cost_simulator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.scheduled_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "generate-daily-data": {
        "task": "tasks.scheduled_tasks.generate_daily_data",
        "schedule": 86400.0,  # Every 24 hours
    },
    "run-anomaly-detection": {
        "task": "tasks.scheduled_tasks.run_anomaly_detection",
        "schedule": 3600.0,  # Every hour
    },
    "refresh-forecast": {
        "task": "tasks.scheduled_tasks.refresh_forecast",
        "schedule": 21600.0,  # Every 6 hours
    },
}
