#!/usr/bin/env python3
"""
Generate NPC character images using Google's Imagen 4.0.

Art style: Borderlands-style 2D illustration (cell-shaded comic book aesthetic)
- Bold thick outlines, vibrant colors, graphic novel style
- Hand-drawn look with simplified details and expressive characters
- Integrates UI theme accent colors for visual consistency
- Set in the year 2020 (contemporary, not futuristic)

Benefits of Imagen 4.0:
- 🎨 High-quality, detailed images
- 🎯 Excellent prompt adherence
- 🎭 Character consistency across multiple generations
- ✨ Professional-grade illustrations

Color Scheme:
- "purple" - Night heist theme (vibrant purple, magenta, cyan highlights)

Usage:
    python generate_npc_image.py --name "Rosa Martinez" --role "Parking Attendant" --gender female --ethnicity "Latina" --clothing "reflective vest" --background "parking garage" --expression "bored" --accent-colors "purple"
    python generate_npc_image.py --name "Alex Kim" --role "Hacker" --gender person --ethnicity "Asian" --clothing "tech hoodie" --background "server room" --expression "focused" --accent-colors "purple"
    
Requirements:
    pip install google-genai pillow
"""

import argparse
import sys
from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# ============================================
# HEIST GAME ART STYLE - BORDERLANDS
# ============================================
HEIST_GAME_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, expressive characters,
set in year 2020, contemporary clothing and technology (not futuristic)"""


def generate_npc_image(name, role, gender="person", ethnicity=None, clothing=None, 
                       background=None, expression="friendly", details=None, 
                       attitude="approachable", accent_colors=None, output_file=None,
                       use_premium_model=False):
    """Generate character portrait in Borderlands style.
    
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
        accent_colors: List of color accents for UI theme consistency (e.g., ["purple clothing accents", "magenta accessories"])
                      or color scheme name: "purple" (vibrant purple, magenta, cyan highlights)
        output_file: Custom output path (optional)
        use_premium_model: If True, use Imagen 4.0 (for shared player roles). 
                          If False, use Imagen 3.0 Fast (for per-experience NPCs). Default: False
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
    if accent_colors:
        print(f"   Accent Colors: {accent_colors}")
    print()
    
    # Process accent colors - use purple theme
    color_instructions = None
    if accent_colors:
        if isinstance(accent_colors, str):
            # Use purple theme color palette
            color_instructions = ["vibrant purple clothing accents", "magenta accessories", "cyan highlights"]
        elif isinstance(accent_colors, list):
            # Custom color list provided
            color_instructions = accent_colors
    
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
    
    # Accent colors (integrated into character description)
    if color_instructions:
        character_parts.append(", ".join(color_instructions))
    
    # Additional details
    if details:
        character_parts.append(details)
    
    character_description = ", ".join(character_parts)
    
    # Build detailed background setting
    if not background:
        background = "simple colorful indoor setting with ambient lighting"
    else:
        # Enhance background with Borderlands art style details
        background = f"{background}, vibrant colorful environment, good lighting, detailed scene elements"
    
    # Build final prompt
    prompt = f"""{HEIST_GAME_ART_STYLE},
{expression} expression, {attitude} personality,
character: {character_description},
background: {background},
portrait view, centered, waist-up composition"""
    
    print("📝 Prompt:")
    print(f"   {gender} {role} in Borderlands art style")
    print()
    
    try:
        print("🚀 Calling Imagen 4.0...")
        print("   Generating high-quality character portrait...")
        print()
        
        # Create client with API key
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Choose model based on use case
        model = 'imagen-4.0-generate-001' if use_premium_model else 'imagen-3.0-generate-001'
        model_name = "Imagen 4.0 (premium)" if use_premium_model else "Imagen 3.0 Fast (cost-effective)"
        
        print(f"   Model: {model_name}")
        
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
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
        
        # Extract and save image
        image_saved = False
        for generated_image in response.generated_images:
            # Save the image
            generated_image.image.save(str(output_path))
            
            print(f"✅ Generated character portrait!")
            print(f"💾 Saved to: {output_path}")
            
            # Try to get dimensions
            try:
                print(f"📏 Size: {generated_image.image.width}x{generated_image.image.height}")
            except:
                pass
            
            print()
            print("ℹ️  Note: Image includes SynthID watermark (Google's authenticity mark)")
            print("🎨 Generated using Imagen 4.0 (high quality!)")
            print()
            
            image_saved = True
            return str(output_path)
        
        if not image_saved:
            print("❌ Error: No image generated in response")
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
        description='Generate NPC character portraits using Imagen 4.0 (Borderlands art style)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Latina female parking attendant (Purple theme)
  python generate_npc_image.py --name "Rosa Martinez" --role "Parking Attendant" \\
    --gender female --ethnicity "Latina" \\
    --clothing "reflective vest and uniform" \\
    --background "parking garage with security monitors and cars" \\
    --expression "bored" --details "looking at phone" --attitude "observant but tired" \\
    --accent-colors "purple"
  
  # Asian male food truck owner (Purple theme)
  python generate_npc_image.py --name "Tommy Chen" --role "Food Truck Owner" \\
    --gender male --ethnicity "Asian" \\
    --clothing "chef's apron and hat" --background "food truck with menu board" \\
    --expression "friendly" --details "holding coffee cup" --attitude "chatty" \\
    --accent-colors "purple"
  
  # Black male security guard (Purple theme with custom accents)
  python generate_npc_image.py --name "Marcus Johnson" --role "Security Guard" \\
    --gender male --ethnicity "Black" \\
    --clothing "security uniform and badge" --background "museum hallway with artwork" \\
    --expression "serious" --attitude "professional" \\
    --accent-colors "vibrant purple badge, magenta trim, cyan highlights"
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
        '--accent-colors',
        help='Color scheme for UI consistency: "purple" (default night heist theme), or custom colors (e.g., "vibrant purple accents, magenta accessories")'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (default: output/npc_images/{name}.png)'
    )
    
    args = parser.parse_args()
    
    # Process accent colors - split comma-separated string into list if needed
    accent_colors = None
    if args.accent_colors:
        # Check if it's a scheme name (single word) or custom colors (comma-separated)
        if ',' in args.accent_colors:
            accent_colors = [c.strip() for c in args.accent_colors.split(',')]
        else:
            accent_colors = args.accent_colors
    
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
        accent_colors=accent_colors,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
