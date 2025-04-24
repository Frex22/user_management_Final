"""
Celery configuration for the email notification system.

This module sets up Celery to work with Kafka as the message broker and Redis
as the result backend for handling email notification tasks.
"""

import logging
from celery import Celery
from settings.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    'email_tasks',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_queue='email_tasks',
    # Retry configuration
    task_default_retry_delay=settings.email_task_retry_delay,
    task_max_retries=settings.email_task_retry_count,
    # Routes for different task types
    task_routes={
        'app.tasks.email_tasks.*': {'queue': 'email_tasks'},
    }
)

# This ensures that Celery doesn't silently ignore exceptions
celery_app.conf.update(
    task_track_started=True,
    task_publish_retry=True,
)

logger.info("Celery application configured with broker: %s", settings.celery_broker_url)