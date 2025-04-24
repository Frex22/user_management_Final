"""
Kafka producer for publishing email notification events.

This module provides functionality to publish events to Kafka topics, which will
then be consumed by Celery workers to send email notifications.
"""

import json
import logging
from kafka import KafkaProducer
from settings.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Create a Kafka producer instance
try:
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # Additional configurations for reliability
        retries=5,
        acks='all'  # Wait for all in-sync replicas to acknowledge the message
    )
    logger.info(f"Kafka producer initialized with bootstrap servers: {settings.kafka_bootstrap_servers}")
except Exception as e:
    logger.error(f"Failed to initialize Kafka producer: {str(e)}")
    # Fallback to None - application will handle this gracefully
    producer = None


def publish_event(topic: str, data: dict) -> bool:
    """
    Publish an event to a Kafka topic.
    
    Args:
        topic (str): The Kafka topic to publish to
        data (dict): The event data to publish
        
    Returns:
        bool: True if the event was published successfully, False otherwise
    """
    if not producer:
        logger.error(f"Cannot publish event to {topic}: Kafka producer not initialized")
        return False
    
    try:
        # Add timestamp to the event data
        from datetime import datetime
        data['timestamp'] = datetime.now().isoformat()
        
        # Send the event to Kafka
        future = producer.send(topic, data)
        # Wait for the send to complete
        future.get(timeout=10)
        logger.info(f"Event published to topic {topic}: {data}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish event to topic {topic}: {str(e)}")
        return False


def close_producer():
    """Close the Kafka producer to release resources."""
    if producer:
        producer.close()
        logger.info("Kafka producer closed")