#!/usr/bin/env python3
"""
Generate celebration image variants with RANDOM crew characters.
Each variant uses 3 randomly selected characters from all 12 roles.
Uses specific character descriptions from role designs.
"""

from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import random

# Art style EXACTLY matching individual role images
HEIST_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, NOT photorealistic,
set in year 2020, contemporary setting (not futuristic)"""

# ALL 12 character descriptions (NO glasses/eyewear, NO screens/tablets/laptops)
ROLE_DESIGNS = {
    "mastermind": {
        "ethnicity": "distinguished 40-year-old Indian",
        "clothing": "tailored suit with rolled-up sleeves, tactical vest over dress shirt",
        "details": "confident leadership presence",
    },
    "safe_cracker": {
        "ethnicity": "Middle Eastern",
        "clothing": "worn leather jacket, tool belt with precision instruments",
        "details": "lockpicking tools visible in belt, stethoscope around neck",
    },
    "hacker": {
        "ethnicity": "young Korean",
        "clothing": "tech hoodie with cyberpunk patches, fingerless gloves",
        "details": "neon underglow visible, tech-focused appearance",
    },
    "driver": {
        "ethnicity": "Latina/Latino",
        "clothing": "leather racing jacket with sponsor patches, driving gloves",
        "details": "holding car keys, radio earpiece visible, racing watch on wrist",
    },
    "insider": {
        "ethnicity": "professional Black",
        "clothing": "crisp business suit, company ID badge displayed, polished appearance",
        "details": "holding briefcase and access card, perfectly groomed",
    },
    "grifter": {
        "ethnicity": "charismatic European",
        "clothing": "expensive designer suit, silk pocket square, luxury watch",
        "details": "multiple fake badges and IDs visible in pocket, perfectly styled",
    },
    "muscle": {
        "ethnicity": "imposing Polynesian with muscular build",
        "clothing": "tactical gear, reinforced vest, fingerless tactical gloves, combat boots",
        "details": "ear piece visible, utility belt with tactical equipment",
    },
    "lookout": {
        "ethnicity": "sharp-eyed young adult South Asian",
        "clothing": "tactical urban wear, multiple pockets, binoculars around neck",
        "details": "holding radio, scanning surroundings alertly",
    },
    "fence": {
        "ethnicity": "street-smart 40-year-old white",
        "clothing": "vintage jacket covered in pins and patches, multiple rings, layers of necklaces",
        "details": "examining jewel with magnifying loupe, street-smart appearance",
    },
    "cat_burglar": {
        "ethnicity": "agile Japanese",
        "clothing": "form-fitting black stealth suit, climbing harness, soft-soled boots",
        "details": "grappling equipment visible, climbing gloves",
    },
    "cleaner": {
        "ethnicity": "meticulous Scandinavian",
        "clothing": "professional dark suit with latex gloves tucked in pocket",
        "details": "holding UV flashlight, spray bottle visible",
    },
    "pickpocket": {
        "ethnicity": "street-smart young adult Southeast Asian",
        "clothing": "inconspicuous casual street clothes, light jacket with hidden pockets, sneakers",
        "details": "hands showing subtle sleight-of-hand gesture, innocent appearance",
    }
}


# 10 NEW international/travel celebration scenarios - 3 characters only
CELEBRATION_VARIANTS = [
    {
        "num": 19,
        "name": "Dubai Burj Khalifa",
        "setting": "luxury Dubai penthouse with Burj Khalifa visible through floor-to-ceiling windows, modern Arabian architecture",
        "action": "celebrating against iconic Dubai skyline, arms raised triumphantly, exhilarated expressions, on top of the world",
        "mood": "golden desert sunset glow, purple city lights, cyan modern LED lighting, opulent victory",
        "composition": "wide shot with Burj Khalifa prominent, three celebrating against iconic backdrop"
    },
    {
        "num": 20,
        "name": "Mexico City Colorful Streets",
        "setting": "vibrant Mexico City street with colorful colonial buildings, papel picado banners overhead, festive atmosphere",
        "action": "dancing celebration in street, arms up with joy, genuine excitement, cultural victory celebration",
        "mood": "warm golden evening light, vibrant colors (purple, orange, cyan), festive energy",
        "composition": "street celebration shot, colorful buildings as backdrop, authentic Mexican setting"
    },
    {
        "num": 21,
        "name": "Luxury Train Orient Express",
        "setting": "inside elegant vintage train cabin, art deco interior, passing countryside visible through window",
        "action": "lounging victoriously in plush train seats, toasting with glasses raised (non-alcoholic), relaxed triumph",
        "mood": "warm vintage golden lighting, purple velvet seats, classic luxury atmosphere",
        "composition": "intimate train cabin interior, all three visible in classic travel setting"
    },
    {
        "num": 22,
        "name": "Tokyo Shibuya Crossing",
        "setting": "overlooking famous Shibuya crossing at night, neon signs everywhere, bustling Tokyo energy",
        "action": "celebrating on elevated walkway, pointing at city below, excited gestures, cyberpunk victory",
        "mood": "vibrant neon lights (purple, cyan, pink), futuristic glow, high-energy Tokyo atmosphere",
        "composition": "elevated shot with crossing visible below, iconic Tokyo neon backdrop"
    },
    {
        "num": 23,
        "name": "Paris Eiffel Tower Rooftop",
        "setting": "Parisian rooftop terrace at night, Eiffel Tower illuminated in background, classic French architecture",
        "action": "arms around each other celebrating, looking toward Eiffel Tower, romantic victory moment",
        "mood": "golden Eiffel Tower lights, purple Parisian night sky, classic European elegance",
        "composition": "rooftop shot with Eiffel Tower prominent, three celebrating in foreground"
    },
    {
        "num": 24,
        "name": "Rio de Janeiro Beach",
        "setting": "Copacabana beach at golden hour, Sugarloaf Mountain visible, tropical Brazilian coast",
        "action": "celebrating on beach, jumping with excitement, arms raised, genuine joy and freedom",
        "mood": "warm Brazilian sunset, purple-orange sky, tropical celebration energy",
        "composition": "beach shot with iconic Rio mountains in background, energetic celebration"
    },
    {
        "num": 25,
        "name": "Swiss Alps Cable Car",
        "setting": "inside glass cable car high above Swiss Alps, snow-capped peaks visible, dramatic mountain scenery",
        "action": "celebrating in cable car, pointing at peaks below, exhilarated by height and success",
        "mood": "bright alpine sunlight, purple mountain shadows, cyan sky, breathtaking scale",
        "composition": "interior cable car shot, mountains visible through glass, elevated victory"
    },
    {
        "num": 26,
        "name": "Singapore Marina Bay",
        "setting": "Marina Bay Sands rooftop infinity pool area, Singapore skyline at night, futuristic cityscape",
        "action": "celebrating poolside at iconic location, arms raised against skyline, modern luxury victory",
        "mood": "vibrant purple and cyan city lights, golden pool lighting, futuristic atmosphere",
        "composition": "iconic Singapore backdrop, three celebrating at world-famous location"
    },
    {
        "num": 27,
        "name": "New York Times Square",
        "setting": "Times Square at night, massive LED billboards everywhere, quintessential NYC energy",
        "action": "celebrating in heart of Times Square, arms up in victory, surrounded by lights and energy",
        "mood": "vibrant billboard lights (purple, cyan, gold), electric NYC atmosphere, urban triumph",
        "composition": "wide shot capturing Times Square chaos, three celebrating in iconic location"
    },
    {
        "num": 28,
        "name": "Venice Gondola Night",
        "setting": "in ornate Venetian gondola at night, historic canal buildings and bridges, romantic Italian setting",
        "action": "relaxed celebration in gondola, casual poses, genuine relief and happiness, floating victory",
        "mood": "warm golden canal lights, purple evening sky, romantic Italian ambiance",
        "composition": "gondola shot with Venice architecture, intimate celebration on water"
    }
]


def generate_celebration_variant(variant_info, role_ids=None):
    """Generate a celebration image variant with 3 RANDOM characters."""
    
    # Randomly select 3 different roles if not provided
    if role_ids is None:
        role_ids = random.sample(list(ROLE_DESIGNS.keys()), 3)
    
    # Build detailed character descriptions using role designs - ONLY 3 CHARACTERS
    crew_members = []
    for role_id in role_ids[:3]:
        if role_id in ROLE_DESIGNS:
            design = ROLE_DESIGNS[role_id]
            role_name = role_id.replace('_', ' ').title()
            # Randomly choose gender for each character
            gender = random.choice(["man", "woman"])
            ethnicity_with_gender = f"{design['ethnicity']} {gender}"
            char_desc = f"{role_name} - {ethnicity_with_gender}, wearing {design['clothing']}, {design['details']}"
            crew_members.append(char_desc)
    
    crew_description = ". ".join(crew_members)
    
    # Print which roles were selected for this variant
    print(f"🎭 Selected roles: {', '.join(role_ids)}")
    
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
    print("🎨 Generating 10 NEW celebration variants with RANDOM characters...")
    print("Each variant will have 3 randomly selected crew members from all 12 roles\n")
    print("🎲 Characters will be different in each image for variety!\n")
    
    # Set random seed for reproducibility during this run, but different each time script runs
    random.seed()
    
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
    print(f"📝 Files: crew_celebration_success_19.png through crew_celebration_success_28.png")
    print(f"\n💡 Each image has different random crew members!")
    print(f"💡 NO glasses/eyewear, NO screens/tablets/laptops in character descriptions")
