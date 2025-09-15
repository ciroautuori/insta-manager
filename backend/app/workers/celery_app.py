from celery import Celery
import os
from app.core.config import settings

# Configurazione Celery
celery_app = Celery(
    "instadmin",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.publisher",
        "app.workers.analytics",
        "app.workers.maintenance"
    ]
)

# Configurazione task
celery_app.conf.update(
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Task routing
    task_routes={
        'app.workers.publisher.*': {'queue': 'publisher'},
        'app.workers.analytics.*': {'queue': 'analytics'},
        'app.workers.maintenance.*': {'queue': 'maintenance'},
    },
    
    # Task retry policy
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Beat schedule per task periodici
    beat_schedule={
        'refresh-instagram-tokens': {
            'task': 'app.workers.maintenance.refresh_instagram_tokens',
            'schedule': 60 * 60 * 24,  # Ogni 24 ore
        },
        'sync-analytics-daily': {
            'task': 'app.workers.analytics.sync_daily_analytics',
            'schedule': 60 * 60 * 6,   # Ogni 6 ore
        },
        'cleanup-failed-tasks': {
            'task': 'app.workers.maintenance.cleanup_failed_tasks',
            'schedule': 60 * 60 * 12,  # Ogni 12 ore
        }
    },
    
    # Scadenza task
    task_time_limit=30 * 60,  # 30 minuti
    task_soft_time_limit=25 * 60,  # 25 minuti
    
    # Retry configuration
    task_default_retry_delay=60,
    task_max_retries=3,
)
