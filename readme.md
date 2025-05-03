# User Management System

## Overview
This project is a comprehensive user management system designed to handle user registration, authentication, and role-based access control. It also includes an event-driven email notification system powered by **Celery** and **Kafka** for efficient and scalable email delivery.

## Features
- User registration and authentication
- Role-based access control
- Event-driven email notifications for:
  - Account verification
  - Account locking/unlocking
  - Role upgrades
  - Professional status upgrades
- Asynchronous task processing with Celery
- Reliable message brokering with Kafka
- Fallback mechanism for direct email delivery

## Issues and Pull Requests

### Quality Assurance (5 QA Issues)
1. **Issue #1**: Kafka connection error during event publishing
   - **Pull Request**: [Fix Kafka connection retry logic](#)
2. **Issue #2**: Email template rendering failure ([Link to Issue](#))
   - **Pull Request**: [Fix email template rendering logic](#)
3. **Issue #3**: Kafka issue with tests
   - **Pull Request**: [Fixed and added tests](#)
4. **Issue #4**: Missing Kafka topic for role upgrade events ([Link to Issue](#))
   - **Pull Request**: [Add Kafka topic for role upgrades](#)
5. **Issue #5**: Dockerfile issue for imports fixed
   - **Pull Request**: [Changed docker file and compose implementation](#)

### Test Coverage Improvement
- Added test for account verification email event
- Added test for account locked email event
- Added test for role upgrade email event
- Added test for professional status upgrade email event
- Added test for Kafka topic creation
- Added test for Celery task retry mechanism
- Added test for email template rendering
- Added test for Kafka message consumption
- Added test for logging configuration
- Added test for fallback email delivery mechanism

### New Feature Implementation
- Event-Driven Email Notifications with Celery and Kafka
- Retry Mechanism for Failed Email Deliveries


## Documentation
For detailed documentation, refer to the [documentation.md](documentation.md) file.

---
