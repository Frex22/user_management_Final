import pytest
import os
import uuid
from unittest.mock import patch, MagicMock
from app.events.kafka_producer import publish_event
from app.events.kafka_utils import set_kafka_unavailable
from app.events.event_types import EventType
from app.events.kafka_test_helper import clear_stored_test_events, get_last_stored_event
from httpx import AsyncClient
from app.main import app # Assuming your FastAPI app instance is here
import asyncio


# Fixture to automatically clear kafka helper and reset flags
@pytest.fixture(autouse=True)
def manage_kafka_test_state():
    clear_stored_test_events()
    set_kafka_unavailable(False)
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']
    yield # Run the test
    clear_stored_test_events()
    set_kafka_unavailable(False)
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']


class TestKafkaProducerLogic:
    """Tests focusing on the kafka_producer.py logic and its helpers."""

    @patch('app.events.kafka_producer._producer')
    async def test_publish_event_success_mocked(self, mock_producer):
        """Test successful publish path (mocking the underlying send)."""
        mock_producer.send.return_value = MagicMock() # Simulate successful send

        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test-success@example.com"}
        result = await publish_event(topic, data)

        assert result is True
        mock_producer.send.assert_called_once()
        args, kwargs = mock_producer.send.call_args
        assert args[0] == topic.value
        sent_data = kwargs.get('value', args[1] if len(args) > 1 else None)
        assert 'timestamp' in sent_data # Timestamp should be added by publish_event
        assert sent_data['email'] == "test-success@example.com"
        assert get_last_stored_event() is None # Should not use test helper

    @patch('app.events.kafka_producer._producer')
    async def test_publish_event_test_mode_env_variable(self, mock_producer):
        """Test TEST_MODE=True uses kafka_test_helper."""
        os.environ['TEST_MODE'] = 'True'
        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test-mode@example.com", "id": "123"}

        result = await publish_event(topic, data)

        assert result is True # Decorator returns True on successful storage
        mock_producer.send.assert_not_called() # Real producer should not be called

        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic.value
        assert stored_event[1]['email'] == "test-mode@example.com"

    @patch('app.events.kafka_producer._producer')
    async def test_publish_event_simulate_unavailable_flag(self, mock_producer):
        """Test set_kafka_unavailable(True) uses kafka_test_helper."""
        set_kafka_unavailable(True)
        topic = EventType.ACCOUNT_LOCKED
        data = {"email": "simulate-locked@example.com", "id": "456"}

        result = await publish_event(topic, data)

        assert result is True # Decorator returns True on successful storage
        mock_producer.send.assert_not_called() # Real producer should not be called

        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic.value
        assert stored_event[1]['email'] == "simulate-locked@example.com"

    @patch('app.events.kafka_producer._producer')
    async def test_publish_event_failure_with_decorator(self, mock_producer):
        """Test exception during publish is handled by decorator (returns True)."""
        mock_producer.send.side_effect = Exception("Kafka connection error")

        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test-fail@example.com"}
        result = await publish_event(topic, data)

        assert result is True # Decorator handles exception, returns True
        mock_producer.send.assert_called_once()
        assert get_last_stored_event() is None # Should not use test helper in this case

    async def test_mock_producer_send_direct(self):
        """Test the MockProducer's send method directly (stores in helper)."""
        from app.events.kafka_producer import _producer # The instance at the end of the file
        topic_val = EventType.ROLE_UPGRADE.value
        data = {"email": "mock-send@example.com", "new_role": "ADMIN"}

        # Ensure not in simulated unavailable mode
        set_kafka_unavailable(False)
        if 'TEST_MODE' in os.environ: del os.environ['TEST_MODE']

        result = await _producer.send(topic_val, data)

        assert result is True # Mock send returns True

        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic_val
        assert stored_event[1]['email'] == "mock-send@example.com"

    async def test_mock_producer_send_simulated_failure(self):
        """Test MockProducer's send raises error when unavailable flag is set."""
        from app.events.kafka_producer import _producer
        topic_val = EventType.PROFESSIONAL_STATUS_UPGRADE.value
        data = {"email": "mock-fail@example.com"}

        set_kafka_unavailable(True) # Simulate failure condition

        with pytest.raises(ConnectionError, match="Simulated Kafka connection error in MockProducer"):
            await _producer.send(topic_val, data)

        # Reset flag
        set_kafka_unavailable(False)


# Integration-style test (requires running docker-compose environment)
# This test assumes the API triggers the kafka publish event correctly.
# It doesn't verify consumption, only that the publish logic is likely hit.
@pytest.mark.asyncio
async def test_api_triggers_publish_email_verification():
    """
    Test that calling the registration API likely triggers publish_event.
    Uses TEST_MODE to capture the event via kafka_test_helper.
    """
    os.environ['TEST_MODE'] = 'True' # Ensure event is captured by helper

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Use a unique email for each test run if needed
        unique_email = f"kafka-integ-{uuid.uuid4()}@example.com"
        registration_payload = {
            "email": unique_email,
            "password": "strongpassword123",
            "full_name": "Kafka Integration Test User",
            "role": "AUTHENTICATED"  # Updated to a valid role value
            # Add other required fields based on UserCreate schema
        }
        # Update endpoint if necessary
        endpoint = "/register/"  # Corrected URL for the registration endpoint
        try:
            response = await client.post(endpoint, json=registration_payload)
            # Check if registration itself was successful (or accepted)
            # Adjust status code based on your API design (e.g., 201 Created or 200 OK)
            assert response.status_code in [200, 201]

            # Allow some time for the async publish_event to potentially run
            await asyncio.sleep(0.1)

            # Check if the event was captured by the test helper
            stored_event = get_last_stored_event()
            assert stored_event is not None, "No event captured by kafka_test_helper"
            assert stored_event[0] == EventType.EMAIL_VERIFICATION.value
            assert stored_event[1]['email'] == unique_email

        except Exception as e:
            pytest.fail(f"API call failed or assertion error: {e}\nResponse: {response.text if 'response' in locals() else 'No response'}")
        finally:
            # Clean up environment variable
             if 'TEST_MODE' in os.environ: del os.environ['TEST_MODE']

# TODO: Add similar integration tests for other event types if API endpoints exist
# e.g., test_api_triggers_publish_account_locked, test_api_triggers_publish_role_upgrade
