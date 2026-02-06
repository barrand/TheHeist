"""
Background image generation service.
Generates location and item images for experiences.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Track generation tasks to avoid duplicates
_generation_tasks = {}


def parse_experience_for_generation(experience_dict: Dict) -> tuple[List[Dict], List[Dict]]:
    """
    Parse experience data to extract locations and items that need images.
    
    Args:
        experience_dict: Parsed experience data from experience_loader
    
    Returns:
        tuple: (locations, items) lists
    """
    locations = []
    items = []
    
    # Extract locations
    if 'locations' in experience_dict:
        for loc_name in experience_dict['locations']:
            location_id = loc_name.lower().replace(' ', '_').replace('-', '_')
            locations.append({
                'name': loc_name,
                'id': location_id
            })
    
    # Extract items from items_by_location
    if 'items_by_location' in experience_dict:
        seen_items = set()
        for location_items in experience_dict['items_by_location'].values():
            for item in location_items:
                item_id = item.get('id', '')
                if item_id and item_id not in seen_items:
                    seen_items.add(item_id)
                    items.append({
                        'id': item_id,
                        'name': item.get('name', ''),
                        'description': item.get('description', '')
                    })
    
    return locations, items


def check_images_exist(experience_id: str) -> tuple[bool, int, int]:
    """
    Check if images exist for an experience.
    
    Returns:
        tuple: (all_exist, location_count, item_count)
    """
    images_dir = Path(__file__).parent.parent.parent / "generated_images" / experience_id
    
    if not images_dir.exists():
        return False, 0, 0
    
    location_count = len(list(images_dir.glob("location_*.png")))
    item_count = len(list(images_dir.glob("item_*.png")))
    
    # Consider images ready if we have at least some
    has_images = location_count > 0 or item_count > 0
    
    return has_images, location_count, item_count


async def generate_images_background(experience_id: str, experience_dict: Dict):
    """
    Generate images in the background for an experience.
    Non-blocking - called when game starts.
    """
    
    # Check if already generating
    if experience_id in _generation_tasks:
        logger.info(f"🎨 Images already generating for {experience_id}")
        return
    
    # Check if images already exist
    exists, loc_count, item_count = check_images_exist(experience_id)
    if exists:
        logger.info(f"🎨 Images already exist for {experience_id} ({loc_count} locations, {item_count} items)")
        return
    
    logger.info(f"🎨 Starting background image generation for {experience_id}")
    
    try:
        # Parse experience for images needed
        locations, items = parse_experience_for_generation(experience_dict)
        
        logger.info(f"🎨 Need to generate {len(locations)} location images and {len(items)} item images")
        
        # Import generation functions
        from backend.scripts.generate_location_images import generate_all_location_images
        from backend.scripts.generate_item_images import generate_all_item_images
        
        # Mark as generating
        _generation_tasks[experience_id] = True
        
        # Generate in background (don't await)
        async def generate():
            try:
                # Generate locations first (more important for immersion)
                await generate_all_location_images(experience_id, locations)
                
                # Then generate items
                await generate_all_item_images(experience_id, items)
                
                logger.info(f"✅ Background image generation complete for {experience_id}")
            except Exception as e:
                logger.error(f"❌ Background image generation failed for {experience_id}: {e}")
            finally:
                # Remove from tracking
                if experience_id in _generation_tasks:
                    del _generation_tasks[experience_id]
        
        # Schedule generation task
        asyncio.create_task(generate())
        
    except Exception as e:
        logger.error(f"❌ Error starting background generation: {e}")
        if experience_id in _generation_tasks:
            del _generation_tasks[experience_id]


def trigger_image_generation_if_needed(experience_id: str, experience_dict: Dict):
    """
    Synchronous wrapper to trigger background image generation.
    Call this when a game starts.
    """
    # Check if images exist
    exists, _, _ = check_images_exist(experience_id)
    
    if not exists and experience_id not in _generation_tasks:
        # Create async task
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(generate_images_background(experience_id, experience_dict))
            logger.info(f"🎨 Queued background image generation for {experience_id}")
        except RuntimeError:
            # No event loop - we're probably in a sync context
            logger.warning(f"⚠️ Could not start background generation - no event loop")
