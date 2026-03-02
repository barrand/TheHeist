#!/usr/bin/env python3
"""
Compare image generation across Gemini 2.5 Flash, 3.1 Flash, and 3 Pro Image models.

Standardized output:
- Items: 1:1 aspect ratio, 512x512 (smallest)
- Locations: 16:9 aspect ratio, 1024x576 (1K)
- NPCs: 1:1 aspect ratio, 1024x1024 (1K)

Output structure: generated_images_comparison/{scenario_id}-{model_name}/

Usage:
  python compare_image_models.py scenario1.json scenario2.json
  python compare_image_models.py backend/experiences/generated_museum_gala_vault_mastermind_safe_cracker.json backend/experiences/generated_bank_safe_deposit_mastermind_safe_cracker.json
"""

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_IMAGE_MODEL, GEMINI_IMAGE_MODEL_31

# Models to compare
MODELS = [
    GEMINI_IMAGE_MODEL,           # gemini-2.5-flash-image
    GEMINI_IMAGE_MODEL_31,       # gemini-3.1-flash-image-preview
    "gemini-3-pro-image-preview",
]

# Output specs: (aspect_ratio, resize_to (width, height) or None)
ITEM_SPEC = ("1:1", (512, 512))
LOCATION_SPEC = ("16:9", (1024, 576))
NPC_SPEC = ("1:1", (1024, 1024))

OUTPUT_BASE = Path(__file__).parent.parent / "generated_images_comparison"

HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details,
set in year 2020, contemporary styling (not futuristic),
no thought bubbles, no speech bubbles, no titles, no captions (environmental text like signs is fine)"""


def _model_to_folder_name(model: str) -> str:
    """Convert model ID to safe folder name."""
    return re.sub(r"[^\w\-.]", "-", model)


def get_location_prompt(location_name: str, visual_description: str = "") -> str:
    scene = visual_description or f"{location_name}, dramatic lighting, heist atmosphere"
    return f"""{HEIST_GAME_ART_STYLE},
environment scene: {scene},
wide establishing shot, cinematic composition, no people visible,
no border, no frame, image extends to all edges, full bleed"""


def get_item_prompt(item_name: str, visual_description: str, item_description: str = "") -> str:
    details = visual_description or item_description or f"{item_name}, detailed object"
    return f"""{HEIST_GAME_ART_STYLE},
item: {details},
centered product shot, pure black background, professional game asset,
no shadows on background, item fully isolated"""


def get_npc_prompt(npc: dict) -> str:
    gender = npc.get("gender", "person")
    role = npc.get("role", "")
    ethnicity = npc.get("ethnicity", "")
    clothing = npc.get("clothing", "")
    expression = npc.get("expression", "friendly")
    attitude = npc.get("attitude", "approachable")
    details = npc.get("details", "")
    location = npc.get("location", "")
    character_desc = f"{ethnicity} {gender} {role}".strip() if ethnicity else f"{gender} {role}"
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
    prompt += ", purple and magenta accent lighting, night heist theme"
    prompt += f", {HEIST_GAME_ART_STYLE}"
    prompt += ", no thought bubbles, no speech bubbles, no titles, no captions"
    return prompt


def _resize_image(image_path: Path, target_size: tuple) -> None:
    """Resize image to target (width, height) using PIL."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        img.save(image_path)
    except Exception as e:
        print(f"   ⚠️  Resize failed: {e}")


async def generate_one_image(
    client: genai.Client,
    model: str,
    prompt: str,
    output_path: Path,
    label: str,
    aspect_ratio: str,
    resize_to: tuple = None,
) -> bool:
    """Generate a single image with the given model, aspect ratio, and optional resize."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        config = types.GenerateContentConfig(
            response_modalities=["Text", "Image"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        )
        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=config,
        )
        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(str(output_path))
                if resize_to:
                    _resize_image(output_path, resize_to)
                print(f"   ✅ {label}: {output_path.name}")
                return True
        print(f"   ❌ {label}: No image in response")
        return False
    except Exception as e:
        print(f"   ❌ {label}: {e}")
        return False


async def run_comparison(experience_jsons: list[Path]):
    """Generate images for each scenario with all 3 models."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    for exp_path in experience_jsons:
        data = json.loads(exp_path.read_text())
        scenario_id = data.get("scenario_id", exp_path.stem)

        locations = data.get("locations", [])[:1]
        items = data.get("items", [])[:1]
        npcs = data.get("npcs", [])[:1]

        if not locations and not items and not npcs:
            print(f"⚠️  Skipping {scenario_id}: no locations, items, or NPCs")
            continue

        print(f"\n{'='*70}")
        print(f"Scenario: {scenario_id}")
        print(f"  Models: {MODELS}")
        print(f"  Specs: Items 1:1@512, Locations 16:9@1024x576, NPCs 1:1@1024")
        print(f"{'='*70}\n")

        for model in MODELS:
            model_folder = _model_to_folder_name(model)
            out_dir = OUTPUT_BASE / f"{scenario_id}-{model_folder}"

            for loc in locations:
                name = loc.get("name", loc.get("id", "Unknown"))
                loc_id = loc.get("id", name.lower().replace(" ", "_"))
                visual = loc.get("visual", "")
                prompt = get_location_prompt(name, visual)
                print(f"📍 {model_folder} Location: {name}")
                await generate_one_image(
                    client, model, prompt,
                    out_dir / f"location_{loc_id}.png", model_folder,
                    aspect_ratio=LOCATION_SPEC[0],
                    resize_to=LOCATION_SPEC[1],
                )
                await asyncio.sleep(2)

            for item in items:
                name = item.get("name", item.get("id", "Unknown"))
                item_id = item.get("id", "item").replace("item_", "")
                visual = item.get("visual", "")
                desc = item.get("description", "")
                prompt = get_item_prompt(name, visual, desc)
                print(f"📦 {model_folder} Item: {name}")
                await generate_one_image(
                    client, model, prompt,
                    out_dir / f"item_{item_id}.png", model_folder,
                    aspect_ratio=ITEM_SPEC[0],
                    resize_to=ITEM_SPEC[1],
                )
                await asyncio.sleep(2)

            for npc in npcs:
                name = npc.get("name", npc.get("id", "Unknown"))
                npc_id = npc.get("id", "npc")
                prompt = get_npc_prompt(npc)
                print(f"👤 {model_folder} NPC: {name}")
                await generate_one_image(
                    client, model, prompt,
                    out_dir / f"npc_{npc_id}.png", model_folder,
                    aspect_ratio=NPC_SPEC[0],
                    resize_to=NPC_SPEC[1],
                )
                await asyncio.sleep(2)

    print(f"\n✅ Done. Compare images in: {OUTPUT_BASE}")
    for d in sorted(OUTPUT_BASE.iterdir()):
        if d.is_dir():
            print(f"   {d.name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare image models across scenarios")
    parser.add_argument("experience_jsons", type=Path, nargs="+",
                        help="Paths to experience JSON files")
    parser.add_argument("--clean", action="store_true",
                        help="Delete existing comparison folders before running")
    args = parser.parse_args()

    for p in args.experience_jsons:
        if not p.exists():
            print(f"❌ File not found: {p}")
            sys.exit(1)

    if args.clean and OUTPUT_BASE.exists():
        for d in OUTPUT_BASE.iterdir():
            if d.is_dir():
                import shutil
                shutil.rmtree(d)
                print(f"🗑️  Deleted {d.name}")

    asyncio.run(run_comparison(args.experience_jsons))


if __name__ == "__main__":
    main()
