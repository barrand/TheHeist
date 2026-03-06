"""
Main FastAPI application
Initialize app, middleware, and routes
"""

import json
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import npc, websocket, rooms, images
from app.services.storage_service import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Load build stamp written by restart-app.sh
_build_info_path = os.path.join(os.path.dirname(__file__), "..", "build_info.json")
try:
    with open(_build_info_path) as _f:
        _build_info = json.load(_f)
    BUILD_TIME = _build_info.get("build_time", "unknown")
    GIT_HASH = _build_info.get("git_hash", "unknown")
except (FileNotFoundError, json.JSONDecodeError):
    BUILD_TIME = "unknown (run restart-app.sh to stamp)"
    GIT_HASH = "unknown"

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
app.include_router(images.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    storage.configure()
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📡 Server running on {settings.host}:{settings.port}")
    logger.info(f"🤖 Using Gemini NPC model: {settings.gemini_npc_model}")
    logger.info(f"🏗️  Build: {BUILD_TIME}  git:{GIT_HASH}")


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
        "build_time": BUILD_TIME,
        "git_hash": GIT_HASH,
    }
