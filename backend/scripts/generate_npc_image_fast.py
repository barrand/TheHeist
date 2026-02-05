#!/usr/bin/env python3
"""
Generate NPC and object images using Google's Gemini 2.5 Flash Image (fast & cheap).

This is the ECONOMY tier for high-volume generation:
- NPCs (many per scenario)
- Inventory items
- Objects and props
- Background elements

For PREMIUM quality (player avatars), use generate_role_images_gendered.py with Imagen 4.0.

Art style: Borderlands-style 2D illustration (cell-shaded comic book aesthetic)
- Bold thick outlines, vibrant colors, graphic novel style
- Hand-drawn look with simplified details and expressive characters
- Integrates UI theme accent colors for visual consistency
- Set in the year 2020 (contemporary, not futuristic)

Benefits of Gemini 2.5 Flash Image:
- ⚡ Lightning fast generation (optimized for high-volume)
- 💰 Significantly cheaper than Imagen 4.0
- 🎯 Good quality for NPCs and objects
- 🎭 Consistent Borderlands art style

Color Scheme:
- "purple" - Night heist theme (vibrant purple, magenta, cyan highlights)

Usage:
    # NPC character
    python generate_npc_image_fast.py --name "Rosa Martinez" --role "Parking Attendant" --gender female --ethnicity "Latina" --clothing "reflective vest" --background "parking garage" --expression "bored" --accent-colors "purple"
    
    # Inventory object
    python generate_npc_image_fast.py --name "Lockpick Set" --role "Tool" --type object --description "professional lockpicking tools in leather case" --accent-colors "purple"
    
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
                       is_object=False, object_description=None):
    """Generate NPC character or object using Gemini 2.5 Flash Image (fast & cheap).
    
    For NPCs:
        name: NPC name (e.g., "Rosa Martinez")
        role: NPC role (e.g., "Parking Attendant")
        gender: "male", "female", or "person"
        ethnicity: (optional) e.g., "Latina", "Asian", "Black"
        clothing: (optional) what they wear
        background: (optional) setting/environment
        expression: (optional) facial expression
        details: (optional) specific props or features
        attitude: (optional) personality/vibe
        accent_colors: "purple" for night heist theme
    
    For Objects:
        name: Object name (e.g., "Lockpick Set")
        role: Object type (e.g., "Tool", "Weapon", "Document")
        is_object: True
        object_description: Detailed description
        accent_colors: "purple" for theme
    
    Returns:
        Path to saved image file
    """
    
    print("🎨 Generating character portrait...")
    if not is_object:
        print(f"   Name: {name}")
        print(f"   Role: {role}")
        print(f"   Gender: {gender}")
        if ethnicity:
            print(f"   Ethnicity: {ethnicity}")
        if clothing:
            print(f"   Clothing: {clothing}")
        if background:
            print(f"   Background: {background}")
        if expression:
            print(f"   Expression: {expression}")
        if details:
            print(f"   Details: {details}")
        if attitude:
            print(f"   Attitude: {attitude}")
        if accent_colors:
            print(f"   Accent Colors: {accent_colors}")
    else:
        print(f"   Object: {name}")
        print(f"   Type: {role}")
        print(f"   Description: {object_description}")
        if accent_colors:
            print(f"   Theme: {accent_colors}")
    print()
    
    # Build the prompt
    if is_object:
        # Object/inventory item prompt
        prompt = f"{object_description}, {HEIST_GAME_ART_STYLE}"
        if accent_colors == "purple":
            prompt += ", purple and magenta accent lighting, night heist atmosphere"
    else:
        # Character prompt
        character_desc = f"{gender} {role}"
        if ethnicity:
            character_desc = f"{ethnicity} {character_desc}"
        
        prompt = f"{character_desc} in Borderlands art style"
        
        if clothing:
            prompt += f", wearing {clothing}"
        
        if background:
            prompt += f", {background}"
        
        if expression:
            prompt += f", {expression} expression"
        
        if details:
            prompt += f", {details}"
        
        if attitude:
            prompt += f", {attitude} attitude"
        
        # Add color instructions
        if accent_colors == "purple":
            prompt += ", purple and magenta accent lighting with cyan highlights, vibrant purple atmospheric glow, night heist theme"
        
        # Add art style details
        prompt += f", {HEIST_GAME_ART_STYLE}"
    
    print("📝 Prompt:")
    print(f"   {prompt[:100]}..." if len(prompt) > 100 else f"   {prompt}")
    print()
    
    try:
        print("🚀 Calling Gemini 2.5 Flash Image...")
        print("   Fast & cost-effective generation...")
        print()
        
        # Create client with API key
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Use Gemini 2.5 Flash Image for fast, cheap generation
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[prompt],  # Must be a list!
        )
        
        # Determine output path
        if output_file:
            output_path = Path(output_file)
        else:
            # Default: output/npc_images/{name_snake_case}.png
            name_safe = name.lower().replace(' ', '_').replace("'", '')
            if is_object:
                output_path = Path('output/object_images') / f"{name_safe}.png"
            else:
                output_path = Path('output/npc_images') / f"{name_safe}.png"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract image from response parts
        image_saved = False
        for part in response.parts:
            if part.inline_data is not None:
                # Convert inline_data to PIL Image and save
                image = part.as_image()
                image.save(str(output_path))
                
                print(f"✅ Generated {'object' if is_object else 'character portrait'}!")
                print(f"💾 Saved to: {output_path}")
                
                # Try to get dimensions
                try:
                    print(f"📏 Size: {image.width}x{image.height}")
                except:
                    pass
                
                print()
                print("ℹ️  Note: Image includes SynthID watermark (Google's authenticity mark)")
                print("⚡ Generated using Gemini 2.5 Flash Image (fast & cheap!)")
                print()
                
                image_saved = True
                return str(output_path)
        
        if not image_saved:
            print("❌ Error: No image generated in response")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        print(f"   This might be because:")
        print(f"   - Gemini API is not enabled on your account (check Google AI Studio)")
        print(f"   - Image generation is not available in your region")
        print(f"   - API quota exceeded")
        print(f"   - Missing dependency: 'google-genai' (run: pip install google-genai)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate NPC and object images using Gemini 2.5 Flash Image (fast & cheap)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # NPC character
  python generate_npc_image_fast.py --name "Rosa Martinez" --role "Parking Attendant" \\
    --gender female --ethnicity "Latina" \\
    --clothing "reflective vest and uniform" \\
    --background "parking garage with security monitors" \\
    --expression "bored" --details "looking at phone" \\
    --accent-colors "purple"
  
  # Inventory object
  python generate_npc_image_fast.py --name "Lockpick Set" --role "Tool" \\
    --object --description "professional lockpicking tools in leather case, metallic picks" \\
    --accent-colors "purple"
  
  # Game item
  python generate_npc_image_fast.py --name "Security Keycard" --role "Item" \\
    --object --description "electronic keycard with magnetic strip and hologram" \\
    --accent-colors "purple"

Cost Comparison:
  - Gemini 2.5 Flash Image: Fast & cheap (use for NPCs, objects)
  - Imagen 4.0: Premium quality (use for player role avatars only)
        """
    )
    
    # Character/NPC arguments
    parser.add_argument('--name', required=True, help='Character or object name')
    parser.add_argument('--role', required=True, help='Role/type (e.g., "Guard", "Tool")')
    parser.add_argument('--gender', default='person', help='Gender: male, female, or person')
    parser.add_argument('--ethnicity', help='Ethnicity (e.g., "Latina", "Asian")')
    parser.add_argument('--clothing', help='What they wear')
    parser.add_argument('--background', help='Setting/environment')
    parser.add_argument('--expression', default='friendly', help='Facial expression')
    parser.add_argument('--details', help='Specific props or features')
    parser.add_argument('--attitude', default='approachable', help='Personality/vibe')
    
    # Object-specific arguments
    parser.add_argument('--object', action='store_true', help='Generate object/item instead of character')
    parser.add_argument('--description', help='Full object description (if --object)')
    
    # Theme
    parser.add_argument('--accent-colors', default='purple', help='Color theme (purple for heist)')
    
    # Output
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if args.object and not args.description:
        print("❌ Error: --description required when --object is used")
        sys.exit(1)
    
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
        accent_colors=args.accent_colors,
        output_file=args.output,
        is_object=args.object,
        object_description=args.description
    )


if __name__ == '__main__':
    main()
