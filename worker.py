"""
Worker script for processing email notification events from Kafka with Celery.

This script starts a Celery worker that consumes events from Kafka topics
and processes them using the defined tasks.

Usage:
    python worker.py
"""

import logging
import os
from app.tasks.celery_app import celery_app
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_account_unlocked_email,
    send_role_upgrade_email,
    send_professional_status_upgrade_email
)
from app.tasks.consumers import (
    process_email_verification,
    process_account_locked,
    process_account_unlocked,
    process_role_upgrade,
    process_professional_status_upgrade
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    """
    Start the Celery worker for processing Kafka events.
    
    This will register all the email notification tasks with Celery and
    start the worker to consume events from Kafka.
    
    To run this worker:
    celery -A worker worker --loglevel=info
    """
    logger.info("Starting Celery worker for processing Kafka events")
    
    # Register all tasks with Celery
    celery_app.tasks.register(send_verification_email)
    celery_app.tasks.register(send_account_locked_email)
    celery_app.tasks.register(send_account_unlocked_email)
    celery_app.tasks.register(send_role_upgrade_email)
    celery_app.tasks.register(send_professional_status_upgrade_email)
    
    # Register all consumers with Celery
    celery_app.tasks.register(process_email_verification)
    celery_app.tasks.register(process_account_locked)
    celery_app.tasks.register(process_account_unlocked)
    celery_app.tasks.register(process_role_upgrade)
    celery_app.tasks.register(process_professional_status_upgrade)
    
    logger.info("All tasks registered successfully")
    logger.info("Ready to process events from Kafka topics")
    
    # The actual worker is started by running:
    # celery -A worker worker --loglevel=info