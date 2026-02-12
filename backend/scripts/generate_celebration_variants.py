#!/usr/bin/env python3
"""
Generate 8 different crew celebration image variants for review.
Each with unique setting, composition, and mood.
Uses specific character descriptions from role designs.
"""

from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# Art style EXACTLY matching individual role images
HEIST_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, NOT photorealistic,
set in year 2020, contemporary setting (not futuristic)"""

# Character descriptions from generate_role_images_gendered.py
ROLE_DESIGNS = {
    "mastermind": {
        "ethnicity": "distinguished 40-year-old Indian",
        "clothing": "tailored suit with rolled-up sleeves, tactical vest over dress shirt",
        "details": "holding tablet showing heist blueprints, wearing smart glasses",
    },
    "safe_cracker": {
        "ethnicity": "Middle Eastern",
        "clothing": "worn leather jacket, tool belt with precision instruments, magnifying headset",
        "details": "lockpicking tools visible in belt",
    },
    "hacker": {
        "ethnicity": "young Korean",
        "clothing": "tech hoodie with cyberpunk patches, fingerless gloves, AR glasses",
        "details": "neon underglow on equipment, laptop visible",
    }
}


# 8 different celebration scenarios (NO alcohol or smoking)
CELEBRATION_VARIANTS = [
    {
        "num": 1,
        "name": "Rooftop Victory",
        "setting": "urban rooftop at night, city lights twinkling below",
        "action": "throwing arms up in triumph, high-fiving each other, big smiles and laughter, celebrating against skyline",
        "mood": "vibrant purple neon city lights, golden victory glow, cyan skyline reflections",
        "composition": "group huddle, slight low angle, celebrating against dramatic cityscape"
    },
    {
        "num": 2,
        "name": "Getaway Car Celebration",
        "setting": "inside vintage getaway car speeding away, motion blur background",
        "action": "high-fiving and fist-bumping enthusiastically, throwing stolen cash in air playfully, ecstatic expressions",
        "mood": "golden hour lighting through car windows, purple shadows, warm triumphant glow",
        "composition": "tight interior shot, characters packed together celebrating, money floating"
    },
    {
        "num": 3,
        "name": "Hideout Victory",
        "setting": "cozy underground hideout with dim mood lighting, brick walls, scattered heist equipment",
        "action": "group fist bump in center, relaxed triumphant poses, genuine smiles and relief, celebrating success",
        "mood": "warm amber lighting, purple accent lights, cozy victorious atmosphere",
        "composition": "medium group shot around table with heist plans, intimate celebration mood"
    },
    {
        "num": 4,
        "name": "Dockside Escape",
        "setting": "industrial dockside at night, shipping containers in background, water reflections",
        "action": "group victory pose walking away from heist, confident swagger, looking back at camera with grins",
        "mood": "dramatic purple and cyan dock lights, golden moonlight reflections on water, cinematic",
        "composition": "wide action shot, walking toward camera, cool confident energy"
    },
    {
        "num": 5,
        "name": "Safe House Party",
        "setting": "modern safe house apartment with floor-to-ceiling windows, night city view",
        "action": "dancing and celebrating wildly, arms up in victory, genuine joy and relief, jumping with excitement",
        "mood": "vibrant neon city glow through windows, purple and cyan party lighting, energetic atmosphere",
        "composition": "dynamic action shot, mid-dance celebration, pure excitement"
    },
    {
        "num": 6,
        "name": "Warehouse Victory Huddle",
        "setting": "industrial warehouse with dramatic overhead lighting, urban grit",
        "action": "group huddle with hands stacked together in center, looking up at camera, fierce triumphant expressions",
        "mood": "dramatic spotlight from above, purple shadows, golden rim lighting, heroic composition",
        "composition": "low angle looking up, powerful team unity pose, dramatic lighting"
    },
    {
        "num": 7,
        "name": "Sunset Escape",
        "setting": "elevated escape route at golden hour, urban skyline silhouetted against sunset",
        "action": "silhouetted victory poses against sunset, raising arms high, celebrating freedom and success",
        "mood": "brilliant golden sunset, purple and orange sky, cyan city lights just turning on, epic scale",
        "composition": "wide cinematic shot, characters in triumphant silhouette, breathtaking backdrop"
    },
    {
        "num": 8,
        "name": "Victory Celebration",
        "setting": "modern penthouse safe house with city skyline view, sleek urban interior",
        "action": "group celebration with sparklers and confetti, victorious poses, arms raised in triumph, genuine joy",
        "mood": "vibrant purple and cyan city lights through windows, golden sparkler light, luxurious victory vibes",
        "composition": "glamorous celebration shot, wealth and success on display, vibrant energy"
    }
]


def generate_celebration_variant(variant_info, role_ids=['mastermind', 'safe_cracker', 'hacker']):
    """Generate a celebration image variant."""
    
    # Build detailed character descriptions using role designs
    crew_members = []
    for role_id in role_ids[:4]:
        if role_id in ROLE_DESIGNS:
            design = ROLE_DESIGNS[role_id]
            role_name = role_id.replace('_', ' ').title()
            # Mix male and female for variety
            gender = "man" if role_id == "mastermind" else ("woman" if role_id == "hacker" else "person")
            ethnicity_with_gender = f"{design['ethnicity']} {gender}"
            char_desc = f"{role_name} - {ethnicity_with_gender}, wearing {design['clothing']}, {design['details']}"
            crew_members.append(char_desc)
    
    crew_description = ". ".join(crew_members)
    
    # Build the prompt - NO ALCOHOL OR SMOKING
    prompt = f"""{HEIST_ART_STYLE}.

Group shot of heist crew celebrating successful heist with these specific characters:
{crew_description}.

Setting: {variant_info['setting']}.

The crew is {variant_info['action']}.

Lighting and mood: {variant_info['mood']}.

Camera composition: {variant_info['composition']}.

IMPORTANT: NO alcohol (no wine, beer, champagne, cocktails), NO smoking (no cigarettes, cigars, vaping), NO text or words visible anywhere in image.
All characters visible, facing toward camera, stylized illustration style, bold comic book aesthetic, vibrant heist game art."""
    
    print(f"\n{'='*60}")
    print(f"VARIANT {variant_info['num']}: {variant_info['name']}")
    print(f"{'='*60}")
    print(f"📝 Setting: {variant_info['setting']}")
    print(f"🎬 Action: {variant_info['action'][:80]}...")
    print(f"🎨 Mood: {variant_info['mood'][:80]}...")
    print(f"\n🚀 Generating with Imagen 4.0...")
    
    # Initialize client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Generate image
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio='16:9',
            safety_filter_level='block_low_and_above',
            person_generation='allow_adult',
        )
    )
    
    # Save the image
    output_dir = Path(__file__).parent / 'output' / 'static_images'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'crew_celebration_success_{variant_info["num"]}.png'
    
    if response.generated_images:
        with open(output_file, 'wb') as f:
            f.write(response.generated_images[0].image.image_bytes)
        
        print(f"✅ Generated variant {variant_info['num']}: {variant_info['name']}")
        print(f"💾 Saved to: {output_file}")
        return str(output_file)
    else:
        raise Exception("No image generated")


if __name__ == '__main__':
    print("🎨 Generating 8 celebration image variants...")
    print("Each with unique setting, composition, and mood for review\n")
    
    for variant in CELEBRATION_VARIANTS:
        try:
            generate_celebration_variant(variant)
        except Exception as e:
            print(f"❌ Error generating variant {variant['num']}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print("✅ ALL VARIANTS GENERATED!")
    print(f"{'='*60}")
    print(f"📁 Location: backend/scripts/output/static_images/")
    print(f"📝 Files: crew_celebration_success_1.png through crew_celebration_success_8.png")
    print(f"\n💡 Review the images and rename your favorite to crew_celebration_success.png")
