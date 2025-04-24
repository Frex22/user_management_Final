"""
Celery tasks for processing email notifications.

This module defines tasks that process email notification events from Kafka
and send emails using the SMTP client.
"""

import logging
from celery import shared_task
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import UserRole

# Configure logger
logger = logging.getLogger(__name__)

# Initialize dependencies
template_manager = TemplateManager()
smtp_client = SMTPClient(
    server=settings.smtp_server,
    port=settings.smtp_port,
    username=settings.smtp_username,
    password=settings.smtp_password
)

@shared_task(bind=True, max_retries=settings.email_task_retry_count)
def send_verification_email(self, user_data):
    """
    Send an email verification email.
    
    Args:
        user_data (dict): User data containing id, email, first_name, verification_token
    """
    try:
        logger.info(f"Processing verification email for {user_data.get('email')}")
        verification_url = f"{settings.server_base_url}/verify-email/{user_data.get('id')}/{user_data.get('verification_token')}"
        
        context = {
            "name": user_data.get("first_name", "User"),
            "verification_url": verification_url,
            "email": user_data.get("email")
        }
        
        html_content = template_manager.render_template('email_verification', **context)
        smtp_client.send_email("Verify Your Account", html_content, user_data.get("email"))
        
        logger.info(f"Verification email sent to {user_data.get('email')}")
        return {"status": "success", "message": f"Verification email sent to {user_data.get('email')}"}
    
    except Exception as exc:
        logger.error(f"Failed to send verification email: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=settings.email_task_retry_delay)

@shared_task(bind=True, max_retries=settings.email_task_retry_count)
def send_account_locked_email(self, user_data):
    """
    Send an account locked notification email.
    
    Args:
        user_data (dict): User data containing email, first_name
    """
    try:
        logger.info(f"Processing account locked email for {user_data.get('email')}")
        
        context = {
            "name": user_data.get("first_name", "User"),
            "email": user_data.get("email"),
            "support_email": "support@example.com"
        }
        
        html_content = template_manager.render_template('account_locked', **context)
        smtp_client.send_email("Account Locked Notification", html_content, user_data.get("email"))
        
        logger.info(f"Account locked email sent to {user_data.get('email')}")
        return {"status": "success", "message": f"Account locked email sent to {user_data.get('email')}"}
    
    except Exception as exc:
        logger.error(f"Failed to send account locked email: {str(exc)}")
        raise self.retry(exc=exc, countdown=settings.email_task_retry_delay)

@shared_task(bind=True, max_retries=settings.email_task_retry_count)
def send_account_unlocked_email(self, user_data):
    """
    Send an account unlocked notification email.
    
    Args:
        user_data (dict): User data containing email, first_name
    """
    try:
        logger.info(f"Processing account unlocked email for {user_data.get('email')}")
        
        context = {
            "name": user_data.get("first_name", "User"),
            "email": user_data.get("email")
        }
        
        html_content = template_manager.render_template('account_unlocked', **context)
        smtp_client.send_email("Account Unlocked Notification", html_content, user_data.get("email"))
        
        logger.info(f"Account unlocked email sent to {user_data.get('email')}")
        return {"status": "success", "message": f"Account unlocked email sent to {user_data.get('email')}"}
    
    except Exception as exc:
        logger.error(f"Failed to send account unlocked email: {str(exc)}")
        raise self.retry(exc=exc, countdown=settings.email_task_retry_delay)

@shared_task(bind=True, max_retries=settings.email_task_retry_count)
def send_role_upgrade_email(self, user_data):
    """
    Send a role upgrade notification email.
    
    Args:
        user_data (dict): User data containing email, first_name, new_role
    """
    try:
        logger.info(f"Processing role upgrade email for {user_data.get('email')}")
        
        new_role = user_data.get('new_role')
        role_description = {
            UserRole.AUTHENTICATED.name: "regular authenticated user",
            UserRole.MANAGER.name: "manager with additional privileges",
            UserRole.ADMIN.name: "administrator with full system access"
        }.get(new_role, "user with updated permissions")
        
        context = {
            "name": user_data.get("first_name", "User"),
            "email": user_data.get("email"),
            "new_role": new_role,
            "role_description": role_description
        }
        
        html_content = template_manager.render_template('role_upgrade', **context)
        smtp_client.send_email("Role Update Notification", html_content, user_data.get("email"))
        
        logger.info(f"Role upgrade email sent to {user_data.get('email')}")
        return {"status": "success", "message": f"Role upgrade email sent to {user_data.get('email')}"}
    
    except Exception as exc:
        logger.error(f"Failed to send role upgrade email: {str(exc)}")
        raise self.retry(exc=exc, countdown=settings.email_task_retry_delay)

@shared_task(bind=True, max_retries=settings.email_task_retry_count)
def send_professional_status_upgrade_email(self, user_data):
    """
    Send a professional status upgrade notification email.
    
    Args:
        user_data (dict): User data containing email, first_name, is_professional
    """
    try:
        logger.info(f"Processing professional status email for {user_data.get('email')}")
        
        is_professional = user_data.get('is_professional', False)
        status_text = "upgraded to professional status" if is_professional else "changed from professional status"
        
        context = {
            "name": user_data.get("first_name", "User"),
            "email": user_data.get("email"),
            "is_professional": is_professional,
            "status_text": status_text
        }
        
        html_content = template_manager.render_template('professional_status_upgrade', **context)
        smtp_client.send_email("Professional Status Update", html_content, user_data.get("email"))
        
        logger.info(f"Professional status email sent to {user_data.get('email')}")
        return {"status": "success", "message": f"Professional status email sent to {user_data.get('email')}"}
    
    except Exception as exc:
        logger.error(f"Failed to send professional status email: {str(exc)}")
        raise self.retry(exc=exc, countdown=settings.email_task_retry_delay)