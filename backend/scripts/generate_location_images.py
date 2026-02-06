#!/usr/bin/env python3
"""
Generate location images for an experience using Google Imagen.
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

# Import from scripts config (not backend app config)
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from config import GEMINI_API_KEY

# Image generation settings
LOCATION_WIDTH = 300
LOCATION_HEIGHT = 150
OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Heist game art style - same as NPCs use
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details,
set in year 2020, contemporary styling (not futuristic)"""


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
    
    # Build prompt similar to NPC generation
    prompt = f"""{HEIST_GAME_ART_STYLE},
environment scene: {scene_description},
wide establishing shot, cinematic composition, no people visible"""
    
    return prompt


async def generate_location_image(
    location_name: str,
    location_id: str,
    experience_id: str,
    visual_description: str,
    client: genai.Client
) -> str:
    """Generate a single location image."""
    
    output_path = OUTPUT_DIR / experience_id / f"location_{location_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ Location image already exists: {location_name}")
        return str(output_path)
    
    # Generate prompt with visual description
    prompt = get_location_prompt(location_name, visual_description)
    
    print(f"🎨 Generating location image: {location_name}")
    print(f"   Prompt: {prompt[:100]}...")
    
    try:
        # Generate image using Imagen 4.0 Fast (cheapest publicly available model)
        response = client.models.generate_images(
            model='imagen-4.0-fast-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",  # Wide landscape format for locations
                safety_filter_level="block_low_and_above",
                # Note: person_generation not specified - Imagen 4.0 Fast doesn't support allow_adult
            )
        )
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"   📁 Output path: {output_path.absolute()}")
        
        if response.generated_images:
            image = response.generated_images[0]
            print(f"   💾 Writing {len(image.image.image_bytes)} bytes...")
            with open(output_path, 'wb') as f:
                f.write(image.image.image_bytes)
            
            if output_path.exists():
                print(f"   ✅ Saved: {output_path} ({output_path.stat().st_size} bytes)")
                return str(output_path)
            else:
                print(f"   ❌ File not found after save: {output_path}")
                return None
        else:
            print(f"   ❌ No image in response for {location_name}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error generating {location_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_all_location_images(experience_id: str, locations: List[Dict]):
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
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.5)
    
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
            # Format: - **Safe House** - Description
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
