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


# 10 NEW celebration scenarios (NO alcohol or smoking) - 3 characters only
CELEBRATION_VARIANTS = [
    {
        "num": 9,
        "name": "Tropical Beach Victory",
        "setting": "private tropical beach at sunset, white sand, palm trees swaying, turquoise water",
        "action": "relaxed celebratory poses on beach, arms around each other, big genuine smiles, bare feet in sand",
        "mood": "golden sunset glow, purple-orange sky, warm tropical atmosphere, peaceful victory",
        "composition": "medium group shot, beach paradise backdrop, casual triumphant mood"
    },
    {
        "num": 10,
        "name": "Private Jet Luxury",
        "setting": "inside luxury private jet cabin, leather seats, polished wood interior, champagne bucket visible but NOT being used",
        "action": "lounging victoriously in jet seats, high-fiving across aisle, feet up, totally relaxed and triumphant",
        "mood": "warm cabin lighting, golden accents, purple mood lighting, sophisticated wealth",
        "composition": "interior jet shot showing all three, luxury and success on display"
    },
    {
        "num": 11,
        "name": "Limousine Getaway",
        "setting": "inside stretch limousine back seat, tinted windows showing city lights outside, plush interior",
        "action": "throwing hands up celebrating, leaning back in seats, laughing together, pure joy and relief",
        "mood": "purple and cyan city lights through windows, golden interior lighting, energetic celebration",
        "composition": "tight interior shot, all three visible in luxurious back seat, victorious energy"
    },
    {
        "num": 12,
        "name": "Safe House Celebration",
        "setting": "cozy crew safe house living room, comfortable furniture, heist plans on coffee table, home-like atmosphere",
        "action": "casual group fist bump, sitting and standing together, genuine smiles of relief, celebrating like family",
        "mood": "warm comfortable lighting, purple and amber tones, home-like victory atmosphere",
        "composition": "medium interior shot, intimate celebration space, crew as family"
    },
    {
        "num": 13,
        "name": "Victory Portrait",
        "setting": "simple gradient background (dark purple to cyan), studio-style, no distractions",
        "action": "confident victory poses facing camera, arms crossed or raised, fierce triumphant expressions, power stance",
        "mood": "dramatic purple and cyan gradient background, golden rim lighting, heroic professional",
        "composition": "clean professional group shot, all three clearly visible, iconic team pose"
    },
    {
        "num": 14,
        "name": "Helicopter Escape",
        "setting": "inside helicopter in flight, city skyline visible through windows, pilot visible in background",
        "action": "celebrating in passenger seats, pointing down at city below, victorious gestures, exhilarated expressions",
        "mood": "golden hour light through windows, purple city lights below, adrenaline and freedom",
        "composition": "interior helicopter shot, city visible outside, escape and victory combined"
    },
    {
        "num": 15,
        "name": "Rooftop Pool Party",
        "setting": "luxury rooftop pool area at night, city skyline behind, lounge chairs and modern furniture",
        "action": "celebrating poolside, jumping with excitement, arms raised high, silhouettes against city lights",
        "mood": "vibrant purple and cyan city glow, pool water reflecting lights, party atmosphere",
        "composition": "wide rooftop shot, pool and city as backdrop, energetic celebration"
    },
    {
        "num": 16,
        "name": "Art Gallery Heist Success",
        "setting": "elegant art gallery at night, empty picture frames on walls, marble floors, dramatic lighting",
        "action": "walking away from gallery together, looking back with grins, confident swagger, mission accomplished",
        "mood": "dramatic gallery spotlights, purple shadows, golden art lighting, sophisticated setting",
        "composition": "medium shot walking away, empty frames hint at successful heist, cool confidence"
    },
    {
        "num": 17,
        "name": "Urban Alley Victory",
        "setting": "stylish urban alley with street art murals, neon signs, brick walls with graffiti",
        "action": "leaning against wall together, cool relaxed poses, fist bumps and high-fives, street-smart celebration",
        "mood": "vibrant neon signs (purple and cyan), urban glow, edgy street atmosphere",
        "composition": "street photography style, graffiti backdrop, authentic urban victory"
    },
    {
        "num": 18,
        "name": "Penthouse Overlook",
        "setting": "luxury penthouse balcony overlooking city at night, glass railing, modern architecture",
        "action": "standing at railing celebrating, arms spread wide, taking in the view they've earned, victorious silhouettes",
        "mood": "dramatic city lights below, purple-orange sky, golden penthouse lighting, on top of world",
        "composition": "balcony shot from inside looking out, city sprawl below, kings of the city"
    }
]


def generate_celebration_variant(variant_info, role_ids=['mastermind', 'safe_cracker', 'hacker']):
    """Generate a celebration image variant with 3 characters."""
    
    # Build detailed character descriptions using role designs - ONLY 3 CHARACTERS
    crew_members = []
    for role_id in role_ids[:3]:  # Changed from [:4] to [:3]
        if role_id in ROLE_DESIGNS:
            design = ROLE_DESIGNS[role_id]
            role_name = role_id.replace('_', ' ').title()
            # Mix male and female for variety
            gender = "man" if role_id == "mastermind" else ("woman" if role_id == "hacker" else "person")
            ethnicity_with_gender = f"{design['ethnicity']} {gender}"
            char_desc = f"{role_name} - {ethnicity_with_gender}, wearing {design['clothing']}, {design['details']}"
            crew_members.append(char_desc)
    
    crew_description = ". ".join(crew_members)
    
    # Build the prompt - NO ALCOHOL OR SMOKING, 3 CHARACTERS ONLY
    prompt = f"""{HEIST_ART_STYLE}.

Group shot of THREE heist crew members celebrating successful heist with these specific characters:
{crew_description}.

Setting: {variant_info['setting']}.

The crew is {variant_info['action']}.

Lighting and mood: {variant_info['mood']}.

Camera composition: {variant_info['composition']}.

IMPORTANT: EXACTLY 3 characters visible, NO MORE. NO alcohol (no wine, beer, champagne, cocktails), NO smoking (no cigarettes, cigars, vaping), NO text or words visible anywhere in image.
All three characters visible, facing toward camera, stylized illustration style, bold comic book aesthetic, vibrant heist game art."""
    
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
    print("🎨 Generating 10 NEW celebration image variants...")
    print("Each with 3 characters, unique setting, composition, and mood for review\n")
    
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
    print(f"📝 Files: crew_celebration_success_9.png through crew_celebration_success_18.png")
    print(f"\n💡 Review the images and keep your favorites alongside the 4 you already selected")
