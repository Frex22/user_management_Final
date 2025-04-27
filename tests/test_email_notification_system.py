"""
Tests for the event-driven email notification system using Kafka and Celery.
"""

import json
import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.events.kafka_producer import publish_event
from app.events import event_types
from app.models.user_model import User, UserRole
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_role_upgrade_email,
    send_professional_status_upgrade_email
)


@pytest.fixture
def mock_template_manager():
    manager = MagicMock(spec=TemplateManager)
    manager.render_template.return_value = "<html><body>Test Email Content</body></html>"
    return manager


@pytest.fixture
def email_service(mock_template_manager):
    return EmailService(mock_template_manager)


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

    @patch('app.events.kafka_producer.producer')
    def test_publish_event_success(self, mock_producer):
        """Test that events are published to Kafka successfully."""
        # Configure the mock
        mock_producer.send.return_value.get.return_value = MagicMock()
        
        # Test data
        topic = event_types.EMAIL_VERIFICATION
        data = {"email": "test@example.com"}
        
        # Call the function
        result = publish_event(topic, data)
        
        # Assertions
        assert result is True
        mock_producer.send.assert_called_once()
        # Check that topic and data were passed correctly
        args, kwargs = mock_producer.send.call_args
        assert args[0] == topic
        # Check that timestamp was added to the data
        sent_data = kwargs.get('value', args[1] if len(args) > 1 else None)
        assert 'timestamp' in sent_data
        assert sent_data['email'] == "test@example.com"

    @patch('app.events.kafka_producer.producer')
    def test_publish_event_failure(self, mock_producer):
        """Test handling of Kafka publishing failures."""
        # Configure the mock to raise an exception
        mock_producer.send.side_effect = Exception("Kafka error")
        
        # Test data
        topic = event_types.EMAIL_VERIFICATION
        data = {"email": "test@example.com"}
        
        # Call the function
        result = publish_event(topic, data)
        
        # Assertions
        assert result is False
        mock_producer.send.assert_called_once()


class TestEmailService:
    """Tests for the EmailService class."""

    @patch('app.events.kafka_producer.publish_event')
    async def test_send_verification_email(self, mock_publish_event, email_service, test_user):
        """Test sending a verification email through Kafka."""
        # Configure the mock
        mock_publish_event.return_value = True
        
        # Call the service method
        await email_service.send_verification_email(test_user)
        
        # Assertions
        mock_publish_event.assert_called_once()
        args, _ = mock_publish_event.call_args
        assert args[0] == event_types.EMAIL_VERIFICATION
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
        assert args[0] == event_types.ACCOUNT_LOCKED
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
        assert args[0] == event_types.ROLE_UPGRADE
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
        mock_template_manager.render_template.assert_called_once()
        mock_smtp_client.send_email.assert_called_once()
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
        mock_smtp_client.send_email.assert_called_once()
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
        mock_smtp_client.send_email.assert_called_once()
        assert result['status'] == 'success'