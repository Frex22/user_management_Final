"""
Helper functions for testing Kafka interactions, particularly when Kafka is unavailable
or running in a test mode where actual publishing is bypassed.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# In-memory storage for events captured during tests when Kafka is bypassed
_test_event_storage: List[Tuple[str, Dict]] = []

def store_test_event(topic: str, payload: Dict):
    """Stores an event in the in-memory list for test verification."""
    logger.info(f"store_test_event called with topic: {topic}, payload: {payload}")
    logger.debug(f"Storing test event for topic '{topic}': {payload}")
    _test_event_storage.append((topic, payload))

def get_stored_test_events() -> List[Tuple[str, Dict]]:
    """Returns all events stored during the test run."""
    return _test_event_storage

def clear_stored_test_events():
    """Clears the in-memory event storage."""
    logger.debug("Clearing stored test events.")
    _test_event_storage.clear()

def get_last_stored_event() -> Tuple[str, Dict] | None:
    """Returns the most recently stored event, if any."""
    if _test_event_storage:
        return _test_event_storage[-1]
    return None
