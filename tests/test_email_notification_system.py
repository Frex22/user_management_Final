"""
Tests for the event-driven email notification system using Kafka and Celery.
"""

import json
import pytest
import uuid
import os
import asyncio
from unittest.mock import patch, MagicMock
from app.events.kafka_producer import publish_event
from app.events.kafka_utils import set_kafka_unavailable
from app.events.event_types import EventType
from app.models.user_model import User, UserRole
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_role_upgrade_email,
    send_professional_status_upgrade_email
)
from app.events.kafka_test_helper import clear_stored_test_events, get_last_stored_event


@pytest.fixture(autouse=True)
def clear_kafka_helper():
    # Automatically clear stored test events before each test
    clear_stored_test_events()
    # Ensure kafka simulation is off by default
    set_kafka_unavailable(False)
    # Ensure TEST_MODE is not set by default
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']
    yield # Run the test
    # Cleanup after test
    clear_stored_test_events()
    set_kafka_unavailable(False)
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']


@pytest.fixture
def mock_template_manager():
    manager = MagicMock(spec=TemplateManager)
    manager.render_template.return_value = "<html><body>Test Email Content</body></html>"
    return manager


@pytest.fixture
def email_service(mock_template_manager):
    return EmailService(template_manager=mock_template_manager)


@pytest.fixture
def test_user():
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.verification_token = "test-token-123"
    user.role = UserRole.AUTHENTICATED
    user.is_professional = False
    return user


class TestKafkaProducer:
    """Tests for the Kafka producer functionality."""

    @patch('app.events.kafka_producer.MockProducer', new_callable=MagicMock)
    async def test_publish_event_success(self, mock_producer):
        """Test that events are published to Kafka successfully."""
        # Configure the mock
        mock_producer.send.return_value = MagicMock()
        
        # Test data
        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test@example.com"}
        
        # Call the function
        result = await publish_event(topic, data, producer=mock_producer)
        
        # Assertions
        assert result is True
        mock_producer.send.assert_called_once()
        # Check that topic and data were passed correctly
        args, kwargs = mock_producer.send.call_args
        assert args[0] == topic.value  # Now using .value from enum
        # Check that timestamp was added to the data
        sent_data = kwargs.get('value', args[1] if len(args) > 1 else None)
        assert 'timestamp' in sent_data
        assert sent_data['email'] == "test@example.com"

    @patch('app.events.kafka_producer.MockProducer', new_callable=MagicMock)
    @patch('app.events.kafka_producer.handle_kafka_unavailable', lambda f: f)  # Disable decorator for this test
    async def test_publish_event_failure_without_decorator(self, mock_producer):
        """Test handling of Kafka publishing failures without the decorator."""
        # Configure the mock to raise an exception
        mock_producer.send.side_effect = Exception("Kafka error")
        
        # Test data
        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test@example.com"}
        
        # Call the function
        result = await publish_event(topic, data, producer=mock_producer)
        
        # Assertions
        assert result is False
        mock_producer.send.assert_called_once()
        
    @patch('app.events.kafka_producer._producer', new_callable=MagicMock)
    async def test_publish_event_failure_with_decorator(self, mock_producer):
        """Test handling of Kafka publishing failures with the decorator."""
        # Configure the mock to raise an exception
        mock_producer.send.side_effect = Exception("Kafka error")
        
        # Test data
        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test@example.com"}
        
        # Call the function
        result = await publish_event(topic, data)
        
        # Assertions - should return True because of the decorator
        assert result is True
        mock_producer.send.assert_called_once()

    @patch('app.events.kafka_producer._producer')  # Still mock the underlying producer for isolation
    async def test_publish_event_test_mode_env_variable(self, mock_producer):
        """Test that events are stored in test helper when TEST_MODE env var is set."""
        os.environ['TEST_MODE'] = 'True'
        topic = EventType.EMAIL_VERIFICATION
        data = {"email": "test-mode@example.com", "id": "123"}

        result = await publish_event(topic, data)

        assert result is True  # Decorator returns True on successful storage
        mock_producer.send.assert_not_called()  # Real producer should not be called

        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic.value
        assert stored_event[1]['email'] == "test-mode@example.com"
        assert 'timestamp' not in stored_event[1]  # Timestamp added later in mock publish

    @patch('app.events.kafka_producer._producer')  # Still mock the underlying producer for isolation
    async def test_publish_event_simulate_unavailable_flag(self, mock_producer):
        """Test that events are stored in test helper when simulate_kafka_unavailable is True."""
        set_kafka_unavailable(True)
        topic = EventType.ACCOUNT_LOCKED
        data = {"email": "simulate-locked@example.com", "id": "456"}

        result = await publish_event(topic, data)

        assert result is True  # Decorator returns True on successful storage
        mock_producer.send.assert_not_called()  # Real producer should not be called

        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic.value
        assert stored_event[1]['email'] == "simulate-locked@example.com"

    async def test_mock_producer_send(self):
        """Test the MockProducer's send method directly."""
        # Uses the _producer instance created at the end of kafka_producer.py
        from app.events.kafka_producer import _producer
        topic = EventType.ROLE_UPGRADE.value
        data = {"email": "mock-send@example.com", "new_role": "ADMIN"}

        # Ensure we are NOT in simulated unavailable mode for this test
        set_kafka_unavailable(False)
        if 'TEST_MODE' in os.environ:
            del os.environ['TEST_MODE']

        # The MockProducer.send is synchronous in the provided code, adjust if it becomes async
        result = await _producer.send(topic, data)

        assert result is True  # Mock send returns True

        # Check if it was stored in the test helper (as the mock send does)
        stored_event = get_last_stored_event()
        assert stored_event is not None
        assert stored_event[0] == topic
        assert stored_event[1]['email'] == "mock-send@example.com"

    async def test_mock_producer_send_simulated_failure(self):
        """Test the MockProducer's send method when simulating failure."""
        from app.events.kafka_producer import _producer
        topic = EventType.PROFESSIONAL_STATUS_UPGRADE.value
        data = {"email": "mock-fail@example.com"}

        set_kafka_unavailable(True)  # Simulate failure condition for MockProducer

        with pytest.raises(ConnectionError, match="Simulated Kafka connection error in MockProducer"):
            await _producer.send(topic, data)

        # Ensure failure simulation is reset
        set_kafka_unavailable(False)


class TestEmailService:
    """Tests for the EmailService class."""

    @patch('app.services.email_service.publish_event', new_callable=MagicMock)
    async def test_send_verification_email(self, mock_publish_event, email_service, test_user):
        """Test sending a verification email through Kafka."""
        # Configure the mock to return an awaitable value
        future = asyncio.Future()
        future.set_result(True)
        mock_publish_event.return_value = future

        # Call the service method
        await email_service.send_verification_email(test_user)

        # Assertions
        mock_publish_event.assert_called_once()
        args, _ = mock_publish_event.call_args
        assert args[0] == EventType.EMAIL_VERIFICATION
        assert args[1]['email'] == test_user.email
        assert args[1]['id'] == str(test_user.id)
        assert args[1]['verification_token'] == test_user.verification_token
    
    @patch('app.events.kafka_producer.publish_event')
    async def test_send_account_locked_notification(self, mock_publish_event, email_service, test_user):
        """Test sending an account locked notification through Kafka."""
        # Configure the mock
        mock_publish_event.return_value = True
        
        # Call the service method
        await email_service.send_account_locked_notification(test_user)
        
        # Assertions
        mock_publish_event.assert_called_once()
        args, _ = mock_publish_event.call_args
        assert args[0] == EventType.ACCOUNT_LOCKED
        assert args[1]['email'] == test_user.email

    @patch('app.events.kafka_producer.publish_event')
    async def test_send_role_upgrade_notification(self, mock_publish_event, email_service, test_user):
        """Test sending a role upgrade notification through Kafka."""
        # Configure the mock
        mock_publish_event.return_value = True
        
        # Call the service method
        new_role = UserRole.MANAGER
        await email_service.send_role_upgrade_notification(test_user, new_role)
        
        # Assertions
        mock_publish_event.assert_called_once()
        args, _ = mock_publish_event.call_args
        assert args[0] == EventType.ROLE_UPGRADE
        assert args[1]['email'] == test_user.email
        assert args[1]['new_role'] == new_role.name

    @patch('app.events.kafka_producer.publish_event')
    async def test_kafka_failure_fallback(self, mock_publish_event, email_service, test_user):
        """Test that the service falls back to direct email on Kafka failure."""
        # Configure the mock to simulate Kafka failure
        mock_publish_event.return_value = False
        
        # Mock the direct email method
        email_service._direct_send_verification_email = MagicMock()
        
        # Call the service method
        await email_service.send_verification_email(test_user)
        
        # Assertions
        mock_publish_event.assert_called_once()
        email_service._direct_send_verification_email.assert_called_once_with(test_user)


class TestCeleryTasks:
    """Tests for Celery tasks."""
    
    @patch('app.tasks.email_tasks.smtp_client')
    @patch('app.tasks.email_tasks.template_manager')
    def test_send_verification_email_task(self, mock_template_manager, mock_smtp_client):
        """Test the Celery task for sending verification emails."""
        # Configure the mocks
        mock_template_manager.render_template.return_value = "<html>Test</html>"
        
        # Test data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "first_name": "Test",
            "verification_token": "test-token-123"
        }
        
        # Call the task
        result = send_verification_email(user_data)
        
        # Assertions
        mock_template_manager.render_template.assert_called_once()
        mock_smtp_client.send_email.assert_called_once()
        assert result['status'] == 'success'
        
    @patch('app.tasks.email_tasks.smtp_client')
    @patch('app.tasks.email_tasks.template_manager')
    def test_send_account_locked_email_task(self, mock_template_manager, mock_smtp_client):
        """Test the Celery task for sending account locked emails."""
        # Configure the mocks
        mock_template_manager.render_template.return_value = "<html>Test</html>"
        
        # Test data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "first_name": "Test"
        }
        
        # Call the task
        result = send_account_locked_email(user_data)
        
        # Assertions
        mock_template_manager.render_template.assert_called_once_with(
            'account_locked', 
            name=user_data['first_name'],
            email=user_data['email'],
            support_email='support@example.com'
        )
        mock_smtp_client.send_email.assert_called_once_with(
            "Account Locked Notification", 
            "<html>Test</html>", 
            user_data['email']
        )
        assert result['status'] == 'success'

    @patch('app.tasks.email_tasks.smtp_client')
    @patch('app.tasks.email_tasks.template_manager')
    def test_send_role_upgrade_email_task(self, mock_template_manager, mock_smtp_client):
        """Test the Celery task for sending role upgrade emails."""
        # Configure the mocks
        mock_template_manager.render_template.return_value = "<html>Test</html>"
        
        # Test data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "first_name": "Test",
            "new_role": UserRole.MANAGER.name
        }
        
        # Call the task
        result = send_role_upgrade_email(user_data)
        
        # Assertions
        mock_template_manager.render_template.assert_called_once()
        mock_smtp_client.send_email.assert_called_once_with(
            "Role Update Notification",
            "<html>Test</html>",
            user_data['email']
        )
        assert result['status'] == 'success'
        
    @patch('app.tasks.email_tasks.smtp_client')
    @patch('app.tasks.email_tasks.template_manager')
    def test_send_professional_status_upgrade_email_task(self, mock_template_manager, mock_smtp_client):
        """Test the Celery task for sending professional status emails."""
        # Configure the mocks
        mock_template_manager.render_template.return_value = "<html>Test</html>"
        
        # Test data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "first_name": "Test",
            "is_professional": True
        }
        
        # Call the task
        result = send_professional_status_upgrade_email(user_data)
        
        # Assertions
        mock_template_manager.render_template.assert_called_once()
        mock_smtp_client.send_email.assert_called_once_with(
            "Professional Status Update",
            "<html>Test</html>",
            user_data['email']
        )
        assert result['status'] == 'success'