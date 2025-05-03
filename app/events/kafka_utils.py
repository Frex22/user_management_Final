import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Utility functions for Kafka-related operations

# Refactor simulate_kafka_unavailable to use a mutable object
simulate_kafka_unavailable = {"value": False}

def set_kafka_unavailable(unavailable: bool):
    """Sets the Kafka unavailability flag for testing purposes."""
    simulate_kafka_unavailable["value"] = unavailable
    logger.debug(f"set_kafka_unavailable called with unavailable={unavailable}")
    logger.debug(f"simulate_kafka_unavailable set to {simulate_kafka_unavailable['value']}")