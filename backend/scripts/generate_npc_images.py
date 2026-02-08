#!/usr/bin/env python3
"""
Generate NPC images for an experience using Gemini 2.5 Flash Image.
Images are stored per experience ID for reusability across games.

Uses the fast/cheap Gemini Flash model for NPC portraits since there
can be many NPCs per experience and they are unique per scenario.
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
from config import GEMINI_API_KEY

OUTPUT_DIR = Path(__file__).parent.parent / "generated_images"

# Heist game art style - Borderlands aesthetic
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, expressive characters,
set in year 2020, contemporary clothing and technology (not futuristic)"""


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
    client: genai.Client
) -> str:
    """Generate a single NPC portrait image."""
    
    npc_id = npc.get('id', '')
    npc_name = npc.get('name', 'Unknown')
    
    output_path = OUTPUT_DIR / experience_id / f"npc_{npc_id}.png"
    
    # Skip if already exists
    if output_path.exists():
        print(f"✓ NPC image already exists: {npc_name}")
        return str(output_path)
    
    prompt = get_npc_prompt(npc)
    
    print(f"🎨 Generating NPC image: {npc_name} ({npc_id})")
    print(f"   Prompt: {prompt[:120]}...")
    
    try:
        # Use Gemini 2.5 Flash Image for fast, cheap NPC generation
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[prompt],
        )
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(str(output_path))
                print(f"   ✅ Saved: {output_path}")
                return str(output_path)
        
        print(f"   ❌ No image in response for {npc_name}")
        return None
            
    except Exception as e:
        print(f"   ❌ Error generating {npc_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_all_npc_images(experience_id: str, npcs: List[Dict]):
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
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.5)
    
    successful = [r for r in results if r is not None]
    print(f"\n✅ Generated {len(successful)}/{len(npcs)} NPC images")
    print(f"📁 Saved to: {OUTPUT_DIR / experience_id}/")
    
    return results


if __name__ == "__main__":
    print("Use via image_generator.py service or pass NPC data directly.")
