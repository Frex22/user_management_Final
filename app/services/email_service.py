# email_service.py
import logging
from builtins import ValueError, dict, str
from uuid import UUID
from app.events import event_types
from app.events.kafka_producer import publish_event
from app.models.user_model import User, UserRole
from app.utils.template_manager import TemplateManager
from settings.config import settings

# Configure logger
logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for handling email notifications through Kafka events.
    
    This service publishes events to Kafka topics, which are then consumed
    by Celery workers to send emails asynchronously.
    """
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize the EmailService.
        
        Args:
            template_manager: For handling email templates (used by direct email methods)
        """
        self.template_manager = template_manager
        logger.info("EmailService initialized with event-driven architecture using Kafka")

    async def send_verification_email(self, user: User):
        """
        Publish an email verification event to Kafka.
        
        Args:
            user: The user to send the verification email to
        """
        try:
            # Prepare user data for the event
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "verification_token": user.verification_token
            }
            
            # Publish the event to Kafka
            success = publish_event(event_types.EMAIL_VERIFICATION, user_data)
            
            if success:
                logger.info(f"Email verification event published for user {user.email}")
            else:
                logger.error(f"Failed to publish email verification event for user {user.email}")
                # Fallback to direct email if publishing fails
                self._direct_send_verification_email(user)
                
        except Exception as e:
            logger.error(f"Error publishing email verification event: {str(e)}")
            # Fallback to direct email if publishing fails
            self._direct_send_verification_email(user)

    async def send_account_locked_notification(self, user: User):
        """
        Publish an account locked notification event to Kafka.
        
        Args:
            user: The user to send the notification to
        """
        try:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
            }
            
            success = publish_event(event_types.ACCOUNT_LOCKED, user_data)
            
            if success:
                logger.info(f"Account locked event published for user {user.email}")
            else:
                logger.error(f"Failed to publish account locked event for user {user.email}")
                # Fallback to direct email
                await self._direct_send_user_email({
                    "name": user.first_name,
                    "email": user.email,
                    "support_email": "support@example.com"
                }, 'account_locked')
                
        except Exception as e:
            logger.error(f"Error publishing account locked event: {str(e)}")

    async def send_account_unlocked_notification(self, user: User):
        """
        Publish an account unlocked notification event to Kafka.
        
        Args:
            user: The user to send the notification to
        """
        try:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
            }
            
            success = publish_event(event_types.ACCOUNT_UNLOCKED, user_data)
            
            if success:
                logger.info(f"Account unlocked event published for user {user.email}")
            else:
                logger.error(f"Failed to publish account unlocked event for user {user.email}")
                
        except Exception as e:
            logger.error(f"Error publishing account unlocked event: {str(e)}")

    async def send_role_upgrade_notification(self, user: User, new_role: UserRole):
        """
        Publish a role upgrade notification event to Kafka.
        
        Args:
            user: The user to send the notification to
            new_role: The new role assigned to the user
        """
        try:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "new_role": new_role.name
            }
            
            success = publish_event(event_types.ROLE_UPGRADE, user_data)
            
            if success:
                logger.info(f"Role upgrade event published for user {user.email}")
            else:
                logger.error(f"Failed to publish role upgrade event for user {user.email}")
                
        except Exception as e:
            logger.error(f"Error publishing role upgrade event: {str(e)}")

    async def send_professional_status_notification(self, user: User):
        """
        Publish a professional status upgrade notification event to Kafka.
        
        Args:
            user: The user to send the notification to
        """
        try:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "is_professional": user.is_professional
            }
            
            success = publish_event(event_types.PROFESSIONAL_STATUS_UPGRADE, user_data)
            
            if success:
                logger.info(f"Professional status event published for user {user.email}")
            else:
                logger.error(f"Failed to publish professional status event for user {user.email}")
                
        except Exception as e:
            logger.error(f"Error publishing professional status event: {str(e)}")

    # Legacy direct email methods for fallback
    
    async def _direct_send_user_email(self, user_data: dict, email_type: str):
        """
        Legacy method to directly send an email without going through Kafka.
        Used as fallback when Kafka publishing fails.
        
        Args:
            user_data: User data for the email
            email_type: Type of email to send
        """
        from app.utils.smtp_connection import SMTPClient
        
        smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification",
            'account_unlocked': "Account Unlocked Notification",
            'role_upgrade': "Role Update Notification",
            'professional_status_upgrade': "Professional Status Update"
        }

        if email_type not in subject_map:
            raise ValueError("Invalid email type")

        html_content = self.template_manager.render_template(email_type, **user_data)
        smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])
        logger.info(f"Fallback direct email sent to {user_data['email']}")

    def _direct_send_verification_email(self, user: User):
        """
        Legacy method to directly send a verification email without going through Kafka.
        Used as fallback when Kafka publishing fails.
        
        Args:
            user: The user to send the verification email to
        """
        from app.utils.smtp_connection import SMTPClient
        
        smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        
        verification_url = f"{settings.server_base_url}/verify-email/{user.id}/{user.verification_token}"
        
        context = {
            "name": user.first_name,
            "verification_url": verification_url,
            "email": user.email
        }
        
        html_content = self.template_manager.render_template('email_verification', **context)
        smtp_client.send_email("Verify Your Account", html_content, user.email)
        logger.info(f"Fallback verification email sent directly to {user.email}")