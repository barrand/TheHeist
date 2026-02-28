#!/usr/bin/env python3
"""
Generate item images for an experience using Gemini Flash Image.
Images are stored per experience ID for reusability across games.

Uses GEMINI_IMAGE_MODEL (cheap/fast) — same quota pool as text generation,
not subject to the strict Imagen 10 req/min limit.
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

# Import from scripts config (not backend app config)
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from config import GEMINI_API_KEY, GEMINI_IMAGE_MODEL

OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Heist game art style - same as NPCs use
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details,
set in year 2020, contemporary styling (not futuristic)"""


def _parse_retry_after(error_str: str, default: float = 15.0) -> float:
    """Extract the suggested retry delay (seconds) from a 429 error message."""
    import re
    match = re.search(r"retry in ([\d.]+)s", error_str)
    if match:
        return float(match.group(1)) + 2.0  # Add a small buffer
    return default


def get_item_prompt(item_name: str, item_description: str, visual_description: str = "") -> str:
    """Generate Imagen prompt for an item using detailed visual description.
    
    Args:
        item_name: Name of the item
        item_description: Basic description (fallback)
        visual_description: Detailed visual description from experience file
    
    Returns:
        Complete prompt for Imagen
    """
    
    if visual_description:
        # Use the rich visual description from the experience file
        item_details = visual_description
    else:
        # Fallback to basic description
        item_details = item_description or f"{item_name}, detailed object"
    
    # Build prompt similar to NPC generation - with PURE BLACK background
    prompt = f"""{HEIST_GAME_ART_STYLE},
item: {item_details},
centered product shot, pure black background (RGB 0,0,0), professional game asset,
no shadows on background, item fully isolated"""
    
    return prompt


async def generate_item_image(
    item_name: str,
    item_id: str,
    item_description: str,
    visual_description: str,
    experience_id: str,
    client: genai.Client,
    max_retries: int = 3
) -> str:
    """Generate a single item image with automatic retry for safety filter blocks."""
    
    clean_id = item_id.removeprefix("item_")
    output_path = OUTPUT_DIR / experience_id / f"item_{clean_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ Item image already exists: {item_name}")
        return str(output_path)
    
    # Generate prompt with visual description
    prompt = get_item_prompt(item_name, visual_description, item_description)
    
    print(f"🎨 Generating item image: {item_name} (model: {GEMINI_IMAGE_MODEL})")
    print(f"   Prompt: {prompt[:100]}...")
    
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")

        try:
            # Use Gemini Flash Image (fast/cheap) — avoids the strict Imagen quota
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"]
                ),
            )
            
            # Save image
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(str(output_path))
                    print(f"   ✅ Saved: {output_path}")
                    return str(output_path)
            
            print(f"   ⚠️  No image in response (attempt {attempt + 1}/{max_retries}) - likely safety filter block")
            if attempt < max_retries - 1:
                continue  # Retry

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait = _parse_retry_after(error_str)
                print(f"   ⏳ Rate limited — waiting {wait:.1f}s before retry...")
                await asyncio.sleep(wait)
            elif attempt < max_retries - 1:
                print(f"   ❌ Error on attempt {attempt + 1}/{max_retries}: {e}")
            else:
                import traceback
                traceback.print_exc()
    
    # All retries failed
    print(f"   ❌ Failed to generate {item_name} after {max_retries} attempts")
    return None


async def generate_all_item_images(experience_id: str, items: List[Dict], on_progress=None):
    """Generate images for all items in an experience."""
    
    print(f"\n{'='*60}")
    print(f"Generating Item Images for Experience: {experience_id}")
    print(f"{'='*60}\n")
    
    # Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    results = []
    for item in items:
        item_name = item.get('name', 'Unknown Item')
        item_id = item.get('id', item_name.lower().replace(' ', '_'))
        item_description = item.get('description', '')
        visual_description = item.get('visual', '')
        
        result = await generate_item_image(
            item_name=item_name,
            item_id=item_id,
            item_description=item_description,
            visual_description=visual_description,
            experience_id=experience_id,
            client=client
        )
        results.append(result)
        if on_progress:
            await on_progress()
        
        # Small delay between requests (Gemini Flash Image has generous quotas)
        await asyncio.sleep(2)
    
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
