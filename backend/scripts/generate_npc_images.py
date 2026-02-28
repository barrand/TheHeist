#!/usr/bin/env python3
"""
Generate NPC images for an experience using Gemini Flash Image.
Images are stored per experience ID for reusability across games.

Uses GEMINI_IMAGE_MODEL (cheap/fast) — avoids the strict Imagen 10 req/min
quota limit. Centralized model name comes from config.py.
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

# Import from scripts config
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from config import GEMINI_API_KEY, GEMINI_IMAGE_MODEL

OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Heist game art style - Borderlands aesthetic
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, expressive characters,
set in year 2020, contemporary clothing and technology (not futuristic)"""


def _parse_retry_after(error_str: str, default: float = 15.0) -> float:
    """Extract the suggested retry delay (seconds) from a 429 error message."""
    import re
    match = re.search(r"retry in ([\d.]+)s", error_str)
    if match:
        return float(match.group(1)) + 2.0
    return default


def get_npc_prompt(npc: Dict) -> str:
    """Generate prompt for an NPC portrait from experience data.
    
    Args:
        npc: Dict with fields like name, role, gender, ethnicity, 
             clothing, expression, attitude, details, location
    """
    gender = npc.get('gender', 'person')
    role = npc.get('role', '')
    ethnicity = npc.get('ethnicity', '')
    clothing = npc.get('clothing', '')
    expression = npc.get('expression', 'friendly')
    attitude = npc.get('attitude', 'approachable')
    details = npc.get('details', '')
    location = npc.get('location', '')
    
    # Build character description
    character_desc = f"{gender} {role}"
    if ethnicity:
        character_desc = f"{ethnicity} {character_desc}"
    
    prompt = f"portrait of a {character_desc} in Borderlands art style"
    
    if clothing:
        prompt += f", wearing {clothing}"
    
    if location:
        prompt += f", {location} background"
    
    if expression:
        prompt += f", {expression} expression"
    
    if details:
        prompt += f", {details}"
    
    if attitude:
        prompt += f", {attitude} attitude"
    
    # Add heist theme colors
    prompt += ", purple and magenta accent lighting with cyan highlights, vibrant purple atmospheric glow, night heist theme"
    
    # Add art style
    prompt += f", {HEIST_GAME_ART_STYLE}"
    
    return prompt


async def generate_npc_image(
    npc: Dict,
    experience_id: str,
    client: genai.Client,
    max_retries: int = 3
) -> str:
    """Generate a single NPC portrait image with retry on rate limit."""
    
    npc_id = npc.get('id', '')
    npc_name = npc.get('name', 'Unknown')
    
    output_path = OUTPUT_DIR / experience_id / f"npc_{npc_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ NPC image already exists: {npc_name}")
        return str(output_path)
    
    prompt = get_npc_prompt(npc)
    
    print(f"🎨 Generating NPC image: {npc_name} ({npc_id}) (model: {GEMINI_IMAGE_MODEL})")
    print(f"   Prompt: {prompt[:120]}...")
    
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")

        try:
            # Use Gemini Flash Image (fast/cheap) via config's GEMINI_IMAGE_MODEL
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
            
            print(f"   ❌ No image in response for {npc_name} (attempt {attempt + 1}/{max_retries})")
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

    print(f"   ❌ Failed to generate {npc_name} after {max_retries} attempts")
    return None


async def generate_all_npc_images(experience_id: str, npcs: List[Dict], on_progress=None):
    """Generate images for all NPCs in an experience."""
    
    print(f"\n{'='*60}")
    print(f"Generating NPC Images for Experience: {experience_id}")
    print(f"{'='*60}\n")
    
    if not npcs:
        print("No NPCs to generate images for.")
        return []
    
    # Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    results = []
    for npc in npcs:
        result = await generate_npc_image(
            npc=npc,
            experience_id=experience_id,
            client=client
        )
        results.append(result)
        if on_progress:
            await on_progress()
        
        # Brief delay between NPC images (different model quota from Imagen)
        await asyncio.sleep(2)
    
    successful = [r for r in results if r is not None]
    print(f"\n✅ Generated {len(successful)}/{len(npcs)} NPC images")
    print(f"📁 Saved to: {OUTPUT_DIR / experience_id}/")
    
    return results


if __name__ == "__main__":
    print("Use via image_generator.py service or pass NPC data directly.")
