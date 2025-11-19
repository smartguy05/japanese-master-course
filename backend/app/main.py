"""
Nihongo Sensei - FastAPI Application Entry Point

This is the main application file that initializes and configures FastAPI.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, lessons, flashcards, conversation
from app.config import settings
from app.services.redis_service import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    await redis_service.connect()
    print("Connected to Redis")

    yield

    # Shutdown
    print("Shutting down...")
    await redis_service.disconnect()
    print("Disconnected from Redis")

# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Japanese Learning Platform",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(flashcards.router)
app.include_router(conversation.router)


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns basic application health status and metadata.

    Returns:
        dict: Health status response containing:
            - status: Health status ("healthy")
            - service: Service name
            - version: Application version
            - timestamp: Current timestamp in ISO format
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.

    Returns:
        dict: Welcome message with API information
    """
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
    }
