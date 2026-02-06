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
from app.core.config import get_settings

settings = get_settings()

# Image generation settings
LOCATION_WIDTH = 300
LOCATION_HEIGHT = 150
OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Style prompt for all location images
STYLE_PROMPT = """
Borderlands cel-shaded art style with thick black outlines, stylized comic book aesthetic.
Dark noir atmosphere with dramatic lighting. High contrast. Heist/crime theme.
Professional game art quality.
"""


def get_location_prompt(location_name: str, location_type: str = "interior") -> str:
    """Generate Imagen prompt for a location."""
    
    # Base descriptions for common location types
    base_descriptions = {
        "safe_house": "Secret hideout with planning table, maps on walls, dim lighting, crime board with photos and strings",
        "crew_hideout": "Underground crew headquarters, weapons on wall, computer monitors, tactical gear",
        "museum_grand_hall": "Elegant museum hall with high ceilings, chandeliers, marble floors, art on walls, formal atmosphere",
        "museum_basement": "Concrete service corridor with exposed pipes, industrial lighting, restricted area signs",
        "vault_room": "Heavy steel vault door, security systems, dim dramatic lighting, high security aesthetic",
        "loading_dock": "Industrial loading area with metal doors, cargo boxes, concrete floors",
        "security_room": "Room with multiple security monitors, control panels, swivel chairs, surveillance equipment",
        "office": "Corporate office with desk, computer, filing cabinets, fluorescent lighting",
        "kitchen": "Commercial kitchen with stainless steel appliances, prep stations, industrial aesthetic",
        "corridor": "Long hallway with doors, industrial or corporate aesthetic depending on location",
    }
    
    # Try to match location name to base description
    location_key = location_name.lower().replace(" ", "_")
    for key, desc in base_descriptions.items():
        if key in location_key:
            base_desc = desc
            break
    else:
        # Generic description
        base_desc = f"{location_name}, dramatic lighting, detailed environment"
    
    return f"{base_desc}. {STYLE_PROMPT}"


async def generate_location_image(
    location_name: str,
    location_id: str,
    experience_id: str,
    client: genai.Client
) -> str:
    """Generate a single location image."""
    
    output_path = OUTPUT_DIR / experience_id / f"location_{location_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ Location image already exists: {location_name}")
        return str(output_path)
    
    # Generate prompt
    prompt = get_location_prompt(location_name)
    
    print(f"🎨 Generating location image: {location_name}")
    print(f"   Prompt: {prompt[:100]}...")
    
    try:
        # Generate image using Imagen 4.0 (nano-banana)
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="3:2",  # Close to 300x150
                safety_filter_level="block_some",
                person_generation="allow_adult",
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
            print(f"❌ No image generated for {location_name}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating {location_name}: {e}")
        return None


async def generate_all_location_images(experience_id: str, locations: List[Dict]):
    """Generate images for all locations in an experience."""
    
    print(f"\n{'='*60}")
    print(f"Generating Location Images for Experience: {experience_id}")
    print(f"{'='*60}\n")
    
    # Initialize Gemini client
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    results = []
    for location in locations:
        location_name = location.get('name', location.get('id', 'Unknown'))
        location_id = location.get('id', location_name.lower().replace(' ', '_'))
        
        result = await generate_location_image(
            location_name=location_name,
            location_id=location_id,
            experience_id=experience_id,
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
