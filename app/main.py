from builtins import Exception
import logging
from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware  # Import the CORSMiddleware
from app.database import Database
from app.dependencies import get_settings
from app.events.kafka_producer import close_producer
from app.routers import user_routes
from app.utils.api_description import getDescription

# Configure logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Management",
    description=getDescription(),
    version="0.0.1",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
# CORS middleware configuration
# This middleware will enable CORS and allow requests from any origin
# It can be configured to allow specific methods, headers, and origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of origins that are allowed to access the server, ["*"] allows all
    allow_credentials=True,  # Support credentials (cookies, authorization headers, etc.)
    allow_methods=["*"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allowed HTTP headers
)

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    # Initialize database connection
    Database.initialize(settings.database_url, settings.debug)
    
    # Log startup of Kafka-based email notification system
    logger.info("Starting event-driven email notification system with Kafka and Celery")
    
    # Import Celery app to ensure tasks are registered
    # This is needed for Celery worker to discover tasks
    from app.tasks.celery_app import celery_app
    logger.info("Celery tasks registered")

@app.on_event("shutdown")
async def shutdown_event():
    # Close Kafka producer connection
    close_producer()
    logger.info("Kafka producer connection closed")

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"message": "An unexpected error occurred."})

app.include_router(user_routes.router)


