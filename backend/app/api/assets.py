"""
Assets API
Serve static assets (images, etc.) to frontend
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assets", tags=["assets"])

# Assets directory
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"


@router.get("/images/{image_name}")
async def get_image(image_name: str):
    """
    Serve an image from the assets/images directory
    
    Args:
        image_name: Name of the image file (e.g., crew_celebration_success.png)
    
    Returns:
        Image file
    """
    # Security: Only allow PNG and JPG files, no path traversal
    if not image_name.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only PNG and JPG images allowed")
    
    if '..' in image_name or '/' in image_name:
        raise HTTPException(status_code=400, detail="Invalid image name")
    
    image_path = ASSETS_DIR / "images" / image_name
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_name}")
    
    logger.info(f"🖼️  Serving image: {image_name}")
    return FileResponse(image_path, media_type="image/png")


@router.get("/images")
async def list_images():
    """
    List all available images
    
    Returns:
        List of image filenames
    """
    images_dir = ASSETS_DIR / "images"
    
    if not images_dir.exists():
        return {"images": []}
    
    images = [
        f.name for f in images_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg']
    ]
    
    return {"images": sorted(images)}
