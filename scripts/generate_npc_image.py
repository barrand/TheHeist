#!/usr/bin/env python3
"""
Generate NPC character images using Google's Imagen 4.

Art style: Prison Boss mobile game (bright, cartoony, fun, stylized)

Usage:
    python generate_npc_image.py --name "Maria Santos" --role "Security Guard" --scenario museum
    python generate_npc_image.py --name "Carlos" --role "Delivery Driver" --traits "overworked,chatty" --output carlos.png
    
Requirements:
    pip install google-genai pillow
"""

import argparse
import sys
from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# Configure Imagen client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_npc_image(name, role, scenario="heist", traits=None, output_file=None):
    """Generate NPC character portrait using Imagen 4 in Prison Boss style."""
    
    print(f"🎨 Generating character portrait...")
    print(f"   Name: {name}")
    print(f"   Role: {role}")
    print(f"   Scenario: {scenario}")
    if traits:
        print(f"   Traits: {traits}")
    print()
    
    # Build character description
    trait_text = f", {traits}" if traits else ""
    
    # Build scenario context
    scenario_context = {
        "museum": "museum security, art gallery, sophisticated setting",
        "train": "train station, railway, vintage locomotive setting",
        "bank": "bank vault, financial institution, professional setting",
        "mansion": "luxury estate, wealthy household, elegant setting",
        "casino": "casino floor, gambling hall, glamorous setting",
        "heist": "crime scene, urban setting, nighttime atmosphere"
    }.get(scenario.lower(), "urban heist setting")
    
    # Construct prompt in Prison Boss style
    prompt = f"""Character portrait of {name}, a {role}{trait_text}.

ART STYLE: Prison Boss mobile game style
- Bright, vibrant, saturated colors
- Cartoony and stylized (NOT realistic)
- Bold outlines and cel-shaded look
- Exaggerated features and expressions
- Fun, playful, slightly quirky
- Mobile game character design aesthetic
- Clean, simple shapes with personality

CHARACTER DETAILS:
- Profession: {role}
- Context: {scenario_context}
- Make them memorable and distinctive
- Show personality through pose and expression
- Appropriate clothing/uniform for their role
- Friendly but characterful

COMPOSITION:
- Portrait style (chest up or waist up)
- Centered character
- Simple, clean background (subtle scene context)
- Well-lit, bright mood
- Professional mobile game character art quality

AVOID:
- Photorealism
- Dark, gritty, or serious tones
- Complex, busy backgrounds
- Weapons or threatening elements
- Overly detailed or realistic rendering
"""
    
    print("📝 Prompt:")
    print(f"   '{name}' as Prison Boss-style {role}")
    print()
    
    try:
        print("🚀 Calling Imagen 4 API...")
        print("   This may take 10-20 seconds...")
        print()
        
        # Use Imagen 4 for image generation
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio='1:1',  # Square portrait
                person_generation='allow_adult'  # Allow generating people
            )
        )
        
        # Determine output path
        if output_file:
            output_path = Path(output_file)
        else:
            # Default: output/npc_images/{name_snake_case}.png
            name_safe = name.lower().replace(' ', '_').replace("'", '')
            output_path = Path('output/npc_images') / f"{name_safe}.png"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the first (and only) generated image
        if response.generated_images:
            image = response.generated_images[0].image
            image.save(str(output_path))
            
            print(f"✅ Generated character portrait!")
            print(f"💾 Saved to: {output_path}")
            
            # Try to get dimensions (may not work with all PIL Image types)
            try:
                print(f"📏 Size: {image.width}x{image.height}")
            except:
                pass
            
            print()
            print("ℹ️  Note: Image includes SynthID watermark (Google's authenticity mark)")
            print()
            
            return str(output_path)
        else:
            print("❌ Error: No images generated")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        print(f"   This might be because:")
        print(f"   - Imagen API is not enabled on your account (check Google AI Studio)")
        print(f"   - Image generation is not available in your region")
        print(f"   - API quota exceeded")
        print(f"   - Missing dependency: 'google-genai' (run: pip install google-genai)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate NPC character portraits using Imagen 4 (Prison Boss style)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_npc_image.py --name "Maria Santos" --role "Security Guard" --scenario museum
  python generate_npc_image.py --name "Carlos" --role "Delivery Driver" --traits "tired,overworked"
  python generate_npc_image.py --name "Harold Matthews" --role "Vault Manager" --traits "proud dad" --output harold.png
        """
    )
    
    parser.add_argument(
        '--name',
        required=True,
        help='NPC name (e.g., "Maria Santos")'
    )
    
    parser.add_argument(
        '--role',
        required=True,
        help='NPC role/job (e.g., "Security Guard", "Janitor")'
    )
    
    parser.add_argument(
        '--scenario',
        default='heist',
        help='Scenario type (museum, train, bank, mansion, casino, heist) - default: heist'
    )
    
    parser.add_argument(
        '--traits',
        help='Personality traits (comma-separated, e.g., "tired,chatty,frustrated")'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (default: output/npc_images/{name}.png)'
    )
    
    args = parser.parse_args()
    
    # Generate the NPC image
    generate_npc_image(
        name=args.name,
        role=args.role,
        scenario=args.scenario,
        traits=args.traits,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
