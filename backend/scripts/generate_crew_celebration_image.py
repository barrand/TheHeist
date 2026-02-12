#!/usr/bin/env python3
"""
Generate crew celebration image for game end screen.

Creates a celebratory group shot of 3-4 crew members together
in the Borderlands art style, showing their roles and celebrating
the successful heist.
"""

from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import json


# Art style EXACTLY matching individual role images
HEIST_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, NOT photorealistic,
set in year 2020, contemporary setting (not futuristic)"""


def load_role_descriptions():
    """Load role descriptions from roles.json"""
    roles_path = Path(__file__).parent.parent.parent / 'shared_data' / 'roles.json'
    
    with open(roles_path, 'r') as f:
        data = json.load(f)
    
    # Create role_id -> description mapping
    return {role['role_id']: role['description'] for role in data['roles']}


def generate_crew_celebration_image(role_ids, output_file=None):
    """Generate crew celebration image using Imagen 4.0.
    
    Args:
        role_ids: List of role IDs (e.g., ['mastermind', 'safe_cracker', 'hacker'])
        output_file: Custom output path
    """
    
    # Load role descriptions
    role_descriptions = load_role_descriptions()
    
    # Build character descriptions from roles
    crew_members = []
    for role_id in role_ids[:4]:  # Max 4 characters to avoid overcrowding
        if role_id in role_descriptions:
            role_name = role_id.replace('_', ' ').title()
            description = role_descriptions[role_id]
            crew_members.append(f"{role_name} ({description})")
    
    crew_description = ", ".join(crew_members)
    
    # Success/celebration scene
    action = """celebrating successful heist together,
    high-fiving, fist bumps, raising arms in victory,
    big smiles and laughter, victorious poses,
    sparkle effects and confetti in background,
    golden hour lighting, heroic composition"""
    color_mood = "vibrant purple lighting, golden yellow accents, cyan highlights, triumphant atmosphere"
    
    # Build the full prompt - ART STYLE FIRST!
    prompt = f"""{HEIST_ART_STYLE}.

Group shot of heist crew celebrating success: {crew_description}.

The crew is {action}.

Camera angle: Medium group shot, slight low angle to make them look heroic.
All characters visible from waist up, facing camera.
Urban heist setting background (dark city, warehouse interior).
{color_mood}.

Group composition, dynamic poses, stylized illustration style, bold comic book aesthetic."""
    
    # Truncate for display
    display_prompt = prompt[:150] + "..." if len(prompt) > 150 else prompt
    print(f"📝 Prompt:\n   {display_prompt}\n")
    print(f"👥 Crew roles: {', '.join(role_ids)}\n")
    
    print(f"🚀 Calling Imagen 4.0...")
    print(f"   Generating crew celebration image...")
    
    # Initialize client inside function to ensure API key is loaded
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Generate image using Imagen 4.0
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio='16:9',  # Wide format for group shot
            safety_filter_level='block_low_and_above',
            person_generation='allow_adult',
        )
    )
    
    # Save the image
    if not output_file:
        # Save to static images directory (same location as role portraits and scenarios)
        static_images_dir = Path(__file__).parent / 'output' / 'static_images'
        output_file = static_images_dir / 'crew_celebration_success.png'
    else:
        output_file = Path(output_file)
    
    # Create directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the generated image
    if response.generated_images:
        with open(output_file, 'wb') as f:
            f.write(response.generated_images[0].image.image_bytes)
        
        print(f"\n✅ Generated crew celebration image!")
        print(f"💾 Saved to: {output_file}")
        print(f"\nℹ️  Note: Image includes SynthID watermark (Google's authenticity mark)")
        print(f"🎨 Generated using Imagen 4.0 (high quality!)\n")
        
        return str(output_file)
    else:
        raise Exception("No image generated")


def generate_experience_celebration_image(experience_md_file):
    """Generate celebration image for an experience file.
    
    Args:
        experience_md_file: Path to experience markdown file
    """
    experience_path = Path(experience_md_file)
    
    # Parse experience file to extract role IDs
    # Look for "Selected Roles:" line
    role_ids = []
    
    with open(experience_path, 'r') as f:
        for line in f:
            if line.startswith('**Selected Roles**:'):
                # Extract roles like "Mastermind, Safe Cracker, Hacker"
                roles_text = line.split(':', 1)[1].strip()
                # Convert to role_ids (lowercase, underscored)
                role_names = [r.strip() for r in roles_text.split(',')]
                role_ids = [r.lower().replace(' ', '_') for r in role_names]
                break
    
    if not role_ids:
        print(f"❌ Could not find roles in {experience_path}")
        return
    
    print(f"📖 Experience: {experience_path.stem}")
    print(f"👥 Roles: {', '.join(role_ids)}\n")
    
    # Generate success image
    print("=" * 60)
    print("GENERATING SUCCESS CELEBRATION IMAGE")
    print("=" * 60)
    success_output = experience_path.parent / 'images' / f'{experience_path.stem}_success.png'
    generate_crew_celebration_image(role_ids, output_file=success_output)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Generate for specific experience file
        generate_experience_celebration_image(sys.argv[1])
    else:
        # Test with default roles
        print("🧪 Generating celebration image with default roles: Mastermind, Safe Cracker, Hacker\n")
        
        # Generate success image
        print("=" * 60)
        print("GENERATING SUCCESS CELEBRATION IMAGE")
        print("=" * 60)
        generate_crew_celebration_image(['mastermind', 'safe_cracker', 'hacker'])
        
        print("\n📝 Usage: python generate_crew_celebration_image.py <experience_file.md>")
        print("   Example: python generate_crew_celebration_image.py ../experiences/museum_gala_vault.md")
