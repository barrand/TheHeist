# Troubleshooting: Role Image Generation

## Issue

Getting "API Key not found" error when trying to generate role images, even though the API key is loading from `.env`.

```
❌ Error: 400 INVALID_ARGUMENT. API Key not found. Please pass a valid API key.
```

## API Key Status

✅ API key is present in `.env` file  
✅ API key is loading correctly (starts with: AIzaSyD6Hg69OL3ihApH...)  
✅ `google-genai` package is installed (version 1.47.0)  
❌ API key authentication failing with Google GenAI service

## Possible Causes

1. **API Key not activated for image generation**
   - Your key might only have text generation enabled
   - Image generation requires additional activation

2. **Region restrictions**
   - Image generation might not be available in your region

3. **API quota exceeded**
   - Check if you've hit daily/monthly limits

4. **API key format mismatch**
   - The SDK version might expect a different key format

## Solutions

### Option 1: Verify API Key Permissions

1. Go to https://aistudio.google.com/app/apikey
2. Check if your API key has these permissions:
   - ✅ Gemini API
   - ✅ **Imagen API** (required for image generation)
3. If Imagen isn't enabled, you may need to:
   - Create a new API key with Imagen enabled
   - Or enable Imagen for your existing key

### Option 2: Try Alternative API Key

If you have access to another Google Cloud project:

1. Create new API key from Google AI Studio
2. Ensure Imagen/image generation is enabled
3. Update `.env` file with new key:
   ```
   GEMINI_API_KEY=your_new_api_key_here
   ```

### Option 3: Generate Images Manually

Since the prompts are all ready, you can generate images using other tools:

**Using Google AI Studio Web Interface:**
1. Go to https://aistudio.google.com
2. Use the "Image Generation" feature
3. Copy prompts from `scripts/generate_role_images.py`
4. Paste each prompt and generate
5. Download and save to `output/role_images/`

**Example Prompt (Mastermind):**
```
2D illustration, comic book art style, bold thick outlines, cell-shaded, 
flat colors with subtle gradients, Borderlands game aesthetic, 
graphic novel style, vibrant saturated colors, stylized proportions, 
hand-drawn look, inked linework, simplified details, expressive characters,
confident and calculating expression, commanding and intelligent, natural leader personality,
character: distinguished older Strategic Planner, wearing tailored suit with rolled-up sleeves, 
tactical vest over dress shirt, vibrant purple clothing accents, magenta accessories, 
cyan highlights, holding tablet showing heist blueprints, wearing smart glasses,
background: command center with blueprints, maps, and monitors displaying floor plans, 
vibrant colorful environment, good lighting, detailed scene elements,
portrait view, centered, waist-up composition
```

### Option 4: Use Different Image Generation Service

Alternative services that work with similar prompts:

1. **DALL-E 3** (OpenAI)
2. **Midjourney**
3. **Stable Diffusion** (local or via API)
4. **Leonardo.ai**

All would work with the Borderlands-style prompts I've created.

### Option 5: Check API Key in Google Cloud Console

1. Go to https://console.cloud.google.com
2. Navigate to "APIs & Services" → "Credentials"
3. Find your API key
4. Check "API restrictions":
   - Make sure "Generative Language API" is allowed
   - Make sure "Imagen API" is allowed (if separate)
5. Check "Application restrictions":
   - Set to "None" for testing
6. Save and wait a few minutes for changes to propagate

## Testing After Fix

Once you've resolved the API issue, test with a single role:

```bash
cd scripts

# Test with one role first
python3 generate_role_images.py --role hacker

# If successful, generate all 12
python3 generate_role_images.py
```

## Alternative: Manual Generation Guide

If API issues persist, I can provide:
1. Individual prompts for each role (ready to copy/paste)
2. Scripts for other image generation services
3. Guide for using Stable Diffusion locally

## All Prompts Ready

The good news: All 12 role prompts are already crafted and ready in:
- `scripts/generate_role_images.py` (ROLE_DESIGNS dictionary)
- Each prompt is optimized for Borderlands art style
- Purple theme applied to all roles
- Just need working image generation API

## Quick Test

Try this minimal test to isolate the issue:

```python
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# Simple test
response = client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents='A purple cat in Borderlands art style',
)

print("Success!" if response else "Failed")
```

Save as `test_api.py` and run:
```bash
python3 test_api.py
```

## Current Status

- ✅ Scripts created and configured
- ✅ All 12 role designs ready
- ✅ Purple theme applied
- ✅ Documentation complete
- ❌ API authentication issue needs resolution
- ⏳ Images pending generation

## Next Steps

1. Resolve API key authentication
2. Generate all 12 role images
3. Copy to Flutter assets
4. Update UI to use portraits

Let me know which solution path you'd like to take!
