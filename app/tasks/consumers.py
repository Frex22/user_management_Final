"""
Kafka consumers for processing email notification events.

This module defines consumers for Kafka topics that trigger Celery tasks
to handle email notifications.
"""

import logging
from celery import shared_task
from app.events.event_types import *
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_account_unlocked_email,
    send_role_upgrade_email,
    send_professional_status_upgrade_email
)

# Configure logger
logger = logging.getLogger(__name__)

@shared_task(name="consume_email_verification")
def process_email_verification(event_data):
    """
    Process an email verification event.
    
    Args:
        event_data (dict): Event data from Kafka
    """
    logger.info(f"Processing email verification event: {event_data}")
    return send_verification_email.delay(event_data)

@shared_task(name="consume_account_locked")
def process_account_locked(event_data):
    """
    Process an account locked event.
    
    Args:
        event_data (dict): Event data from Kafka
    """
    logger.info(f"Processing account locked event: {event_data}")
    return send_account_locked_email.delay(event_data)

@shared_task(name="consume_account_unlocked")
def process_account_unlocked(event_data):
    """
    Process an account unlocked event.
    
    Args:
        event_data (dict): Event data from Kafka
    """
    logger.info(f"Processing account unlocked event: {event_data}")
    return send_account_unlocked_email.delay(event_data)

@shared_task(name="consume_role_upgrade")
def process_role_upgrade(event_data):
    """
    Process a role upgrade event.
    
    Args:
        event_data (dict): Event data from Kafka
    """
    logger.info(f"Processing role upgrade event: {event_data}")
    return send_role_upgrade_email.delay(event_data)

@shared_task(name="consume_professional_status_upgrade")
def process_professional_status_upgrade(event_data):
    """
    Process a professional status upgrade event.
    
    Args:
        event_data (dict): Event data from Kafka
    """
    logger.info(f"Processing professional status upgrade event: {event_data}")
    return send_professional_status_upgrade_email.delay(event_data)

# Map of event types to consumer tasks
EVENT_CONSUMERS = {
    EMAIL_VERIFICATION: process_email_verification,
    ACCOUNT_LOCKED: process_account_locked,
    ACCOUNT_UNLOCKED: process_account_unlocked,
    ROLE_UPGRADE: process_role_upgrade,
    PROFESSIONAL_STATUS_UPGRADE: process_professional_status_upgrade
}

def register_kafka_consumers():
    """Register Kafka consumers with Celery."""
    logger.info("Registering Kafka consumers with Celery")
    # This would be used to register Kafka consumers with Celery Beat
    # or a custom Kafka consumer implementation
    pass