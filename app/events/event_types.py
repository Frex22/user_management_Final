"""
Event types for the Kafka message broker.
This module defines constants for Kafka topics used in the email notification system.
"""

from enum import Enum

class EventType(Enum):
    EMAIL_VERIFICATION = "email_verification"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    ROLE_UPGRADE = "role_upgrade"
    PROFESSIONAL_STATUS_UPGRADE = "professional_status_upgrade"

# Kafka topics for email notifications
EMAIL_VERIFICATION = "email_verification"
ACCOUNT_LOCKED = "account_locked"
ACCOUNT_UNLOCKED = "account_unlocked"
ROLE_UPGRADE = "role_upgrade"
PROFESSIONAL_STATUS_UPGRADE = "professional_status_upgrade"

# Map of event types to their user-friendly descriptions
EVENT_DESCRIPTIONS = {
    EMAIL_VERIFICATION: "Email verification notification",
    ACCOUNT_LOCKED: "Account locking notification",
    ACCOUNT_UNLOCKED: "Account unlocking notification",
    ROLE_UPGRADE: "Role upgrade notification",
    PROFESSIONAL_STATUS_UPGRADE: "Professional status upgrade notification"
}