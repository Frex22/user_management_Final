# Reflection on Final Project: Event-Driven Email Notifications with Celery and Kafka

**Name:** Aakash32  
**Course:** IS601 - Web Systems development
**Date:** May 3, 2025  

---

### **Reflection on Learnings**

Throughout this course, I have gained valuable insights into software engineering principles, particularly in the areas of test-driven development, event-driven architecture, and scalable system design. Working on the final project, I chose to implement the "Event-Driven Email Notifications with Celery and Kafka" feature, which challenged me to integrate modern tools and frameworks into an existing system.

This project required me to refactor the email notification system to use Celery for asynchronous task processing and Kafka for reliable message brokering. I learned how to define event types, configure Kafka topics, and implement Celery tasks to handle various email notification events. Additionally, I explored retry mechanisms, logging, and monitoring to ensure the reliability and maintainability of the system.

The experience of working with Docker, setting up Kafka, and writing unit tests for event processing was particularly rewarding. It reinforced the importance of modular design, thorough testing, and clear documentation in building scalable and maintainable systems.

---


#### **Test Coverage Improvement (10 New Tests)**:
1.  Add test for account verification email event
2.  Add test for account locked email event
3.  Add test for role upgrade email event
4.  Add test for professional status upgrade email event
5.  Add test for Kafka topic creation
6.  Add test for Celery task retry mechanism
7.  Add test for email template rendering
8.  Add test for Kafka message consumption
9.  Add test for logging configuration
10. Add test for fallback email delivery mechanism

#### **New Feature Implementation (2 Features)**:
1.  Event-Driven Email Notifications with Celery and Kafka
2.  Retry Mechanism for Failed Email Deliveries

---

### **DockerHub Repository**

The project has been successfully deployed to DockerHub. You can find the repository at the following link:  
[DockerHub Repository Link](https://hub.docker.com/r/as49/qrcode/tags)

---

### **Commit History**

I ensured a consistent history of work on the project, with over 10 meaningful commits demonstrating progress and adherence to a professional development process. The commits include feature implementations, bug fixes, and test additions.

---

This project has been a challenging yet rewarding experience, allowing me to apply the concepts learned throughout the course to a real-world scenario. I am confident that the skills and knowledge gained will be invaluable in my future endeavors as a software engineer.

---

**Special Thanks**

I would like to extend my heartfelt gratitude to my instructor, Keith Williams, for his exceptional guidance and support throughout this course. His expertise and passion for software engineering have been truly inspiring. The knowledge and skills I have gained under his mentorship will undoubtedly serve as a strong foundation for my future endeavors in the field. Thank you for being a great software engineer and an even greater mentor!
