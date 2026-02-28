"""
Images API endpoints
Serve generated location, item, and NPC images
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["images"])

# Image directory
IMAGES_DIR = Path(__file__).parent.parent.parent / "generated_images"


@router.get("/{experience_id}/location/{location_id}")
async def get_location_image(experience_id: str, location_id: str):
    """
    Get location image for an experience.
    Returns the image file or 404 if not found.
    """
    bare_id = location_id.removeprefix("location_")
    image_path = IMAGES_DIR / experience_id / f"location_{bare_id}.png"
    
    if not image_path.exists():
        logger.warning(f"Location image not found: {image_path}")
        raise HTTPException(status_code=404, detail="Location image not found")
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400"  # Cache for 1 day
        }
    )


@router.get("/{experience_id}/item/{item_id}")
async def get_item_image(experience_id: str, item_id: str):
    """
    Get item image for an experience.
    Returns the image file or 404 if not found.
    """
    # Strip existing prefix to avoid double-prefixing (item_id may already be "item_foo")
    bare_id = item_id.removeprefix("item_")
    image_path = IMAGES_DIR / experience_id / f"item_{bare_id}.png"
    
    if not image_path.exists():
        logger.warning(f"Item image not found: {image_path}")
        raise HTTPException(status_code=404, detail="Item image not found")
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400"  # Cache for 1 day
        }
    )


@router.get("/{experience_id}/npc/{npc_id}")
async def get_npc_image(experience_id: str, npc_id: str):
    """
    Get NPC image for an experience.
    Returns the image file or 404 if not found.
    """
    bare_id = npc_id.removeprefix("npc_")
    image_path = IMAGES_DIR / experience_id / f"npc_{bare_id}.png"
    
    if not image_path.exists():
        logger.warning(f"NPC image not found: {image_path}")
        raise HTTPException(status_code=404, detail="NPC image not found")
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400"  # Cache for 1 day
        }
    )


@router.get("/{experience_id}/status")
async def get_image_generation_status(experience_id: str):
    """
    Check if images exist for an experience.
    Returns counts of location, item, and NPC images.
    """
    exp_dir = IMAGES_DIR / experience_id
    
    if not exp_dir.exists():
        return {
            "experience_id": experience_id,
            "location_images": 0,
            "item_images": 0,
            "npc_images": 0,
            "ready": False
        }
    
    # Count existing images
    location_images = len(list(exp_dir.glob("location_*.png")))
    item_images = len(list(exp_dir.glob("item_*.png")))
    npc_images = len(list(exp_dir.glob("npc_*.png")))
    
    return {
        "experience_id": experience_id,
        "location_images": location_images,
        "item_images": item_images,
        "npc_images": npc_images,
        "ready": location_images > 0 or item_images > 0 or npc_images > 0
    }
