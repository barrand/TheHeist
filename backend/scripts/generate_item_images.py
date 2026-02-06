#!/usr/bin/env python3
"""
Generate item images for an experience using Google Imagen.
Images are stored per experience ID for reusability across games.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

# Image generation settings
ITEM_SIZE = 80  # Square
OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Style prompt for all item images
STYLE_PROMPT = """
Product photography style. Clean, well-lit, professional.
Slight shadow for depth. Transparent or subtle dark gradient background.
High detail, realistic rendering. Studio lighting.
"""


def get_item_prompt(item_name: str, item_description: str) -> str:
    """Generate Imagen prompt for an item."""
    
    # Use item description as base
    base_desc = item_description if item_description else item_name
    
    # Add specific details for common item types
    item_lower = item_name.lower()
    
    if "phone" in item_lower or "burner" in item_lower:
        extra = "black flip phone or smartphone, realistic product shot"
    elif "tool" in item_lower or "lockpick" in item_lower:
        extra = "professional lockpick tools in leather case, metallic tools"
    elif "keycard" in item_lower or "badge" in item_lower or "card" in item_lower:
        extra = "security access card with magnetic stripe, corporate ID badge"
    elif "earpiece" in item_lower or "radio" in item_lower:
        extra = "small black wireless earpiece with cable, communications device"
    elif "food" in item_lower or "apple" in item_lower or "snack" in item_lower:
        extra = "fresh food item, appetizing"
    elif "weapon" in item_lower or "gun" in item_lower:
        extra = "tactical equipment, professional grade"
    elif "cable" in item_lower or "wire" in item_lower:
        extra = "coiled cable or wire, technical equipment"
    elif "key" in item_lower:
        extra = "metal key or keyring, detailed"
    else:
        extra = "detailed object, professional product shot"
    
    return f"{base_desc}. {extra}. {STYLE_PROMPT}"


async def generate_item_image(
    item_name: str,
    item_id: str,
    item_description: str,
    experience_id: str,
    client: genai.Client
) -> str:
    """Generate a single item image."""
    
    output_path = OUTPUT_DIR / experience_id / f"item_{item_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ Item image already exists: {item_name}")
        return str(output_path)
    
    # Generate prompt
    prompt = get_item_prompt(item_name, item_description)
    
    print(f"🎨 Generating item image: {item_name}")
    print(f"   Prompt: {prompt[:100]}...")
    
    try:
        # Generate image using Imagen 3.0 Fast (cheapest for per-experience content)
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # Square
                safety_filter_level="block_some",
                person_generation="dont_allow",  # Items shouldn't have people
            )
        )
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if response.generated_images:
            image = response.generated_images[0]
            with open(output_path, 'wb') as f:
                f.write(image.image.image_bytes)
            
            print(f"✓ Saved: {output_path}")
            return str(output_path)
        else:
            print(f"❌ No image generated for {item_name}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating {item_name}: {e}")
        return None


async def generate_all_item_images(experience_id: str, items: List[Dict]):
    """Generate images for all items in an experience."""
    
    print(f"\n{'='*60}")
    print(f"Generating Item Images for Experience: {experience_id}")
    print(f"{'='*60}\n")
    
    # Initialize Gemini client
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    results = []
    for item in items:
        item_name = item.get('name', 'Unknown Item')
        item_id = item.get('id', item_name.lower().replace(' ', '_'))
        item_description = item.get('description', '')
        
        result = await generate_item_image(
            item_name=item_name,
            item_id=item_id,
            item_description=item_description,
            experience_id=experience_id,
            client=client
        )
        results.append(result)
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.5)
    
    successful = [r for r in results if r is not None]
    print(f"\n✅ Generated {len(successful)}/{len(items)} item images")
    print(f"📁 Saved to: {OUTPUT_DIR / experience_id}/")
    
    return results


def parse_experience_items(experience_file: Path) -> List[Dict]:
    """Parse items from an experience markdown file."""
    items = []
    
    with open(experience_file, 'r') as f:
        content = f.read()
    
    # Parse items by location
    lines = content.split('\n')
    in_items = False
    current_item = None
    
    for line in lines:
        if '## Items by Location' in line:
            in_items = True
            continue
        elif line.startswith('## ') and in_items and 'Items' not in line:
            break
        elif in_items:
            if line.startswith('- **ID**:'):
                # New item
                if current_item and current_item.get('id'):
                    items.append(current_item)
                current_item = {}
                # Extract ID: - **ID**: `item_id`
                id_part = line.split('`')
                if len(id_part) >= 2:
                    current_item['id'] = id_part[1].strip()
            elif current_item is not None:
                if '**Name**:' in line:
                    parts = line.split('**Name**:')
                    if len(parts) >= 2:
                        current_item['name'] = parts[1].strip()
                elif '**Description**:' in line:
                    parts = line.split('**Description**:')
                    if len(parts) >= 2:
                        current_item['description'] = parts[1].strip()
    
    # Add last item
    if current_item and current_item.get('id'):
        items.append(current_item)
    
    return items


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate item images for an experience')
    parser.add_argument('experience_file', help='Path to experience markdown file')
    parser.add_argument('--experience-id', help='Experience ID (defaults to filename without extension)')
    
    args = parser.parse_args()
    
    experience_path = Path(args.experience_file)
    if not experience_path.exists():
        print(f"❌ Experience file not found: {experience_path}")
        return
    
    experience_id = args.experience_id or experience_path.stem
    
    # Parse items from experience file
    items = parse_experience_items(experience_path)
    
    if not items:
        print(f"❌ No items found in {experience_path}")
        return
    
    print(f"Found {len(items)} items:")
    for item in items:
        print(f"  - {item.get('name', 'Unknown')} ({item['id']})")
    
    # Generate images
    await generate_all_item_images(experience_id, items)


if __name__ == "__main__":
    asyncio.run(main())
