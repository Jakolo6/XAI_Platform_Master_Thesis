"""
Celery worker configuration.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "xai_finance_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.MAX_TRAINING_TIME_SECONDS,
    task_soft_time_limit=settings.MAX_TRAINING_TIME_SECONDS - 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.dataset_tasks.*": {"queue": "dataset"},
    "app.tasks.training_tasks.*": {"queue": "training"},
    "app.tasks.explanation_tasks.*": {"queue": "explanation"},
    "app.tasks.report_tasks.*": {"queue": "report"},
}

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-old-datasets": {
        "task": "app.tasks.dataset_tasks.cleanup_old_datasets",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "cleanup-expired-cache": {
        "task": "app.tasks.explanation_tasks.cleanup_expired_cache",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "app.tasks.dataset_tasks",
    "app.tasks.training_tasks",
    "app.tasks.explanation_tasks",
    "app.tasks.report_tasks",
])
