#!/usr/bin/env python3
"""
Generate NPC character images using Google's Imagen 4.

Art style: The Heist Game (bright, cartoony, fun, stylized, low-poly 3D)

Usage:
    python generate_npc_image.py --name "Rosa Martinez" --role "Parking Attendant" --gender female --clothing "reflective vest and uniform" --background "parking garage" --expression "bored"
    python generate_npc_image.py --name "Tommy Chen" --role "Food Truck Owner" --gender male --clothing "chef's apron and hat" --background "food truck" --details "holding spatula"
    
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

# ============================================
# HEIST GAME ART STYLE - ALWAYS CONSISTENT
# ============================================
HEIST_GAME_ART_STYLE = """3D render, cartoonish style,
cell-shaded, exaggerated features,
bright saturated colors, simplified geometry, stylized facial features,
clean flat shading, game character design, toon shader, minimal detail,
low-poly 3D model, mobile game art style"""


def generate_npc_image(name, role, gender="person", ethnicity=None, clothing=None, 
                       background=None, expression="friendly", details=None, 
                       attitude="approachable", output_file=None):
    """Generate NPC character portrait using Imagen 4 in Heist Game art style.
    
    Args:
        name: Character name
        role: Character's job/role (e.g., "Security Guard", "Food Truck Owner")
        gender: "male", "female", or "person" (default: "person")
        ethnicity: Character ethnicity (e.g., "Latina", "Asian", "Black", "White", "Middle Eastern")
        clothing: What they wear (e.g., "reflective vest and uniform", "chef's apron")
        background: Setting (e.g., "parking garage", "food truck", "museum hall")
        expression: Facial expression (default: "friendly")
        details: Additional visual details (e.g., "holding clipboard", "wearing glasses")
        attitude: Overall vibe (e.g., "approachable", "tired", "cheerful")
        output_file: Custom output path (optional)
    """
    
    print(f"🎨 Generating character portrait...")
    print(f"   Name: {name}")
    print(f"   Role: {role}")
    print(f"   Gender: {gender}")
    if ethnicity:
        print(f"   Ethnicity: {ethnicity}")
    if clothing:
        print(f"   Clothing: {clothing}")
    if background:
        print(f"   Background: {background}")
    print(f"   Expression: {expression}")
    if details:
        print(f"   Details: {details}")
    print(f"   Attitude: {attitude}")
    print()
    
    # Build character description
    character_parts = []
    
    # Ethnicity (if specified)
    if ethnicity:
        character_parts.append(ethnicity)
    
    # Gender and role
    if gender in ["male", "female"]:
        character_parts.append(f"{gender} {role}")
    else:
        character_parts.append(role)
    
    # Clothing
    if clothing:
        character_parts.append(f"wearing {clothing}")
    
    # Additional details
    if details:
        character_parts.append(details)
    
    character_description = ", ".join(character_parts)
    
    # Build detailed background setting
    if not background:
        background = "simple colorful indoor setting with ambient lighting"
    else:
        # Enhance background with Heist Game art style details
        background = f"{background}, vibrant colorful environment, good lighting, detailed scene elements"
    
    # Build final prompt
    prompt = f"""{HEIST_GAME_ART_STYLE},
{expression} expression, {attitude} personality,
character: {character_description},
background: {background},
portrait view, centered, waist-up composition,
The Heist game aesthetic"""
    
    print("📝 Prompt:")
    print(f"   {gender} {role} in Heist Game art style")
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
        description='Generate NPC character portraits using Imagen 4 (Heist Game art style)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Latina female parking attendant
  python generate_npc_image.py --name "Rosa Martinez" --role "Parking Attendant" \\
    --gender female --ethnicity "Latina" \\
    --clothing "reflective vest and uniform" \\
    --background "parking garage with security monitors and cars" \\
    --expression "bored" --details "looking at phone" --attitude "observant but tired"
  
  # Asian male food truck owner
  python generate_npc_image.py --name "Tommy Chen" --role "Food Truck Owner" \\
    --gender male --ethnicity "Asian" \\
    --clothing "chef's apron and hat" --background "food truck with menu board" \\
    --expression "friendly" --details "holding coffee cup" --attitude "chatty"
  
  # Black male security guard
  python generate_npc_image.py --name "Marcus Johnson" --role "Security Guard" \\
    --gender male --ethnicity "Black" \\
    --clothing "security uniform and badge" --background "museum hallway with artwork" \\
    --expression "serious" --attitude "professional"
        """
    )
    
    parser.add_argument(
        '--name',
        required=True,
        help='NPC name (e.g., "Rosa Martinez")'
    )
    
    parser.add_argument(
        '--role',
        required=True,
        help='NPC role/job (e.g., "Parking Attendant", "Security Guard")'
    )
    
    parser.add_argument(
        '--gender',
        default='person',
        choices=['male', 'female', 'person'],
        help='Gender (male, female, or person) - default: person'
    )
    
    parser.add_argument(
        '--ethnicity',
        help='Character ethnicity (e.g., "Latina", "Asian", "Black", "White", "Middle Eastern", "South Asian")'
    )
    
    parser.add_argument(
        '--clothing',
        help='What they wear (e.g., "reflective vest and uniform", "chef apron")'
    )
    
    parser.add_argument(
        '--background',
        help='Setting/background (e.g., "parking garage", "food truck", "museum")'
    )
    
    parser.add_argument(
        '--expression',
        default='friendly',
        help='Facial expression (e.g., "friendly", "bored", "serious") - default: friendly'
    )
    
    parser.add_argument(
        '--details',
        help='Additional details (e.g., "holding clipboard", "wearing glasses")'
    )
    
    parser.add_argument(
        '--attitude',
        default='approachable',
        help='Overall personality vibe (e.g., "approachable", "tired", "cheerful") - default: approachable'
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
        gender=args.gender,
        ethnicity=args.ethnicity,
        clothing=args.clothing,
        background=args.background,
        expression=args.expression,
        details=args.details,
        attitude=args.attitude,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
