#!/usr/bin/env python3
"""
Generate location images for an experience using Gemini Flash Image.
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
        return float(match.group(1)) + 2.0
    return default


def get_location_prompt(location_name: str, visual_description: str = None) -> str:
    """Generate Imagen prompt for a location using detailed visual description.
    
    Args:
        location_name: Name of the location
        visual_description: Detailed visual description from experience file
    
    Returns:
        Complete prompt for Imagen
    """
    
    if visual_description:
        # Use the rich visual description from the experience file
        scene_description = visual_description
    else:
        # Fallback to generic description
        scene_description = f"{location_name}, dramatic lighting, detailed environment, heist atmosphere"
    
    prompt = f"""{HEIST_GAME_ART_STYLE},
environment scene: {scene_description},
wide establishing shot, cinematic composition, no people visible,
no border, no frame, no vignette, no rounded corners, no panel border,
image extends to all edges, full bleed"""
    
    return prompt


async def generate_location_image(
    location_name: str,
    location_id: str,
    experience_id: str,
    visual_description: str,
    client: genai.Client,
    max_retries: int = 3
) -> str:
    """Generate a single location image with retry on rate limit."""
    
    output_path = OUTPUT_DIR / experience_id / f"location_{location_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ Location image already exists: {location_name}")
        return str(output_path)
    
    # Generate prompt with visual description
    prompt = get_location_prompt(location_name, visual_description)
    
    print(f"🎨 Generating location image: {location_name} (model: {GEMINI_IMAGE_MODEL})")
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
            
            print(f"   ❌ No image in response for {location_name} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                continue

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

    print(f"   ❌ Failed to generate {location_name} after {max_retries} attempts")
    return None


async def generate_all_location_images(experience_id: str, locations: List[Dict], on_progress=None):
    """Generate images for all locations in an experience."""
    
    print(f"\n{'='*60}")
    print(f"Generating Location Images for Experience: {experience_id}")
    print(f"{'='*60}\n")
    
    # Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    results = []
    for location in locations:
        location_name = location.get('name', location.get('id', 'Unknown'))
        location_id = location.get('id', location_name.lower().replace(' ', '_'))
        visual_description = location.get('visual', '')
        
        result = await generate_location_image(
            location_name=location_name,
            location_id=location_id,
            experience_id=experience_id,
            visual_description=visual_description,
            client=client
        )
        results.append(result)
        if on_progress:
            await on_progress()
        
        # Small delay between requests (Gemini Flash Image has generous quotas)
        await asyncio.sleep(2)
    
    successful = [r for r in results if r is not None]
    print(f"\n✅ Generated {len(successful)}/{len(locations)} location images")
    print(f"📁 Saved to: {OUTPUT_DIR / experience_id}/")
    
    return results


def parse_experience_locations(experience_file: Path) -> List[Dict]:
    """Parse locations from an experience markdown file."""
    locations = []
    
    with open(experience_file, 'r') as f:
        content = f.read()
    
    # Simple parsing - look for location sections
    # In real implementation, would parse the markdown more thoroughly
    lines = content.split('\n')
    in_locations = False
    
    for line in lines:
        if '## Locations' in line:
            in_locations = True
            continue
        elif line.startswith('## ') and in_locations:
            break
        elif in_locations and line.startswith('- **'):
            # Extract location name
            # Format: - **ID**: `crew_hideout`
            parts = line.split('**')
            if len(parts) >= 2:
                location_name = parts[1].strip()
                location_id = location_name.lower().replace(' ', '_').replace('-', '_')
                locations.append({
                    'name': location_name,
                    'id': location_id
                })
    
    return locations


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate location images for an experience')
    parser.add_argument('experience_file', help='Path to experience markdown file')
    parser.add_argument('--experience-id', help='Experience ID (defaults to filename without extension)')
    
    args = parser.parse_args()
    
    experience_path = Path(args.experience_file)
    if not experience_path.exists():
        print(f"❌ Experience file not found: {experience_path}")
        return
    
    experience_id = args.experience_id or experience_path.stem
    
    # Parse locations from experience file
    locations = parse_experience_locations(experience_path)
    
    if not locations:
        print(f"❌ No locations found in {experience_path}")
        return
    
    print(f"Found {len(locations)} locations:")
    for loc in locations:
        print(f"  - {loc['name']} ({loc['id']})")
    
    # Generate images
    await generate_all_location_images(experience_id, locations)


if __name__ == "__main__":
    asyncio.run(main())
