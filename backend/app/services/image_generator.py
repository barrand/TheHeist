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


async def generate_all_images_for_experience(experience_id: str, experience_dict: Dict) -> bool:
    """
    Generate all images for an experience synchronously at game start.
    This blocks until all images are generated.
    
    Generates in order: Locations → Items → NPCs
    
    Returns:
        bool: True if successful, False if error
    """
    
    # Check if already generating
    if experience_id in _generation_tasks:
        logger.info(f"🎨 Images already generating for {experience_id}, waiting...")
        # Wait for existing generation to complete
        while experience_id in _generation_tasks:
            await asyncio.sleep(0.5)
        return True
    
    # Check if images already exist
    exists, loc_count, item_count = check_images_exist(experience_id)
    if exists:
        logger.info(f"✅ Images already exist for {experience_id} ({loc_count} locations, {item_count} items)")
        return True
    
    logger.info(f"🎨 Generating images for {experience_id} at game start...")
    
    try:
        # Parse experience for images needed
        locations, items = parse_experience_for_generation(experience_dict)
        
        logger.info(f"🎨 Will generate: {len(locations)} locations, {len(items)} items")
        
        # Import generation functions
        import sys
        from pathlib import Path
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        sys.path.insert(0, str(scripts_dir))
        
        from generate_location_images import generate_all_location_images
        from generate_item_images import generate_all_item_images
        
        # Mark as generating
        _generation_tasks[experience_id] = True
        
        # Generate in order: Rooms → Items → NPCs
        logger.info(f"🎨 Step 1/2: Generating location images...")
        await generate_all_location_images(experience_id, locations)
        
        logger.info(f"🎨 Step 2/2: Generating item images...")
        await generate_all_item_images(experience_id, items)
        
        # NPCs are generated separately when experience is created
        # We don't regenerate them here
        
        logger.info(f"✅ All images generated for {experience_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Image generation failed for {experience_id}: {e}")
        return False
    finally:
        # Remove from tracking
        if experience_id in _generation_tasks:
            del _generation_tasks[experience_id]
