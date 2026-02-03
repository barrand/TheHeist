#!/usr/bin/env python3
"""
Generate scene/location images using Google's Imagen 4.0.

Specifically for establishing shots of locations, not characters.
"""

from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY


# Art style EXACTLY matching role images - must be FIRST in prompt!
HEIST_SCENE_ART_STYLE = """2D illustration, comic book art style,
bold thick outlines, cell-shaded, flat colors with subtle gradients,
Borderlands game aesthetic, graphic novel style,
vibrant saturated colors, stylized proportions, hand-drawn look,
inked linework, simplified details, NOT photorealistic,
set in year 2020, contemporary setting (not futuristic)"""


def generate_scene_image(scene_description, accent_colors="purple", output_file=None):
    """Generate a scene/location image using Imagen 4.0.
    
    Args:
        scene_description: Full description of the scene/location
        accent_colors: Color scheme name (default: "purple")
        output_file: Custom output path
    """
    
    # Build the full prompt - ART STYLE FIRST!
    color_instructions = "vibrant purple lighting, magenta accents, cyan highlights"
    
    # Put art style FIRST to ensure it dominates over realistic scene description
    prompt = f"{HEIST_SCENE_ART_STYLE}. {scene_description}. {color_instructions}. Stylized illustration, not a photograph."
    
    # Truncate for display
    display_prompt = prompt[:120] + "..." if len(prompt) > 120 else prompt
    print(f"📝 Prompt:\n   {display_prompt}\n")
    
    print(f"🚀 Calling Imagen 4.0...")
    print(f"   Generating high-quality scene image...")
    
    # Initialize client inside function to ensure API key is loaded
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Generate image using Imagen 4.0
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio='1:1',
            safety_filter_level='block_low_and_above',
            person_generation='allow_adult',
        )
    )
    
    # Save the image
    if not output_file:
        output_file = Path('output') / 'scene.png'
    else:
        output_file = Path(output_file)
    
    # Create directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the generated image
    if response.generated_images:
        with open(output_file, 'wb') as f:
            f.write(response.generated_images[0].image.image_bytes)
        
        print(f"\n✅ Generated scene image!")
        print(f"💾 Saved to: {output_file}")
        print(f"\nℹ️  Note: Image includes SynthID watermark (Google's authenticity mark)")
        print(f"🎨 Generated using Imagen 4.0 (high quality!)\n")
    else:
        raise Exception("No image generated")


if __name__ == '__main__':
    # Test with a sample scene
    generate_scene_image(
        scene_description="Grand museum hall during elegant gala event, ornate columns, chandeliers",
        output_file="output/test_scene.png"
    )
