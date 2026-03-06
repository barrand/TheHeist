"""
Images API endpoints
Serve generated location, item, and NPC images.
Uses StorageService for GCS-backed persistence on Cloud Run.
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.storage_service import storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["images"])

IMAGES_DIR = Path(__file__).parent.parent.parent / "generated_images"


def _serve_image(key: str, description: str):
    """Resolve an image via storage service and return a FileResponse."""
    local = storage.local_path(key)
    if local is None:
        logger.warning(f"{description} not found: {key}")
        raise HTTPException(status_code=404, detail=f"{description} not found")

    return FileResponse(
        path=str(local),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/{experience_id}/location/{location_id}")
async def get_location_image(experience_id: str, location_id: str):
    bare_id = location_id.removeprefix("location_")
    key = f"generated_images/{experience_id}/location_{bare_id}.png"
    return _serve_image(key, "Location image")


@router.get("/{experience_id}/item/{item_id}")
async def get_item_image(experience_id: str, item_id: str):
    bare_id = item_id.removeprefix("item_")
    key = f"generated_images/{experience_id}/item_{bare_id}.png"
    return _serve_image(key, "Item image")


@router.get("/{experience_id}/npc/{npc_id}")
async def get_npc_image(experience_id: str, npc_id: str):
    bare_id = npc_id.removeprefix("npc_")
    key = f"generated_images/{experience_id}/npc_{bare_id}.png"
    return _serve_image(key, "NPC image")


@router.get("/{experience_id}/status")
async def get_image_generation_status(experience_id: str):
    prefix = f"generated_images/{experience_id}"
    location_images = len(storage.list_files(prefix, suffix="location_"))
    item_images = len(storage.list_files(prefix, suffix="item_"))
    npc_images = len(storage.list_files(prefix, suffix="npc_"))

    # list_files suffix matches end-of-name so re-count properly
    all_keys = storage.list_files(prefix, suffix=".png")
    location_images = sum(1 for k in all_keys if "/location_" in k)
    item_images = sum(1 for k in all_keys if "/item_" in k)
    npc_images = sum(1 for k in all_keys if "/npc_" in k)

    return {
        "experience_id": experience_id,
        "location_images": location_images,
        "item_images": item_images,
        "npc_images": npc_images,
        "ready": location_images > 0 or item_images > 0 or npc_images > 0,
    }
