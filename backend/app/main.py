"""
Main FastAPI application
Initialize app, middleware, and routes
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import npc, websocket, rooms

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for The Heist multiplayer game",
    debug=settings.debug
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(npc.router)
app.include_router(rooms.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📡 Server running on {settings.host}:{settings.port}")
    logger.info(f"🤖 Using Gemini NPC model: {settings.gemini_npc_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Shutting down The Heist Backend")


@app.get("/")
async def root():
    """
    Health check endpoint
    Returns basic service information
    """
    return {
        "status": "running",
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check
    Can be used by monitoring tools
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }
