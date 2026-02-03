# Guide: Generating Role Character Images

## Overview

I've created a comprehensive system to generate character portraits for all 12 roles using the same Borderlands art style as your NPC portraits.

## What's Been Created

### 1. Main Script: `scripts/generate_role_images.py`
This script generates character portraits for all 12 heist roles with unique designs for each.

**Features:**
- Uses same Borderlands art style as NPCs
- Each role has distinctive character design
- Color-coded by heist theme
- Batch generate all roles or individual ones
- Detailed character descriptions for each role

### 2. Documentation: `ROLE_IMAGE_DESIGNS.md`
Complete reference showing:
- Visual design for each role
- Character descriptions
- Minigames associated with each role
- Color scheme rationale
- Integration instructions for Flutter UI

## The 12 Role Designs

Each role has a carefully crafted prompt that captures their essence:

1. **Mastermind** - Distinguished leader in command center (Purple theme)
2. **Hacker** - Tech genius surrounded by glowing monitors (Purple theme)
3. **Safe Cracker** - Patient expert with tools at vault (Purple theme)
4. **Driver** - Cool professional with getaway car (Purple theme)
5. **Insider** - Corporate infiltrator in business attire (Purple theme)
6. **Grifter** - Charming manipulator at gala event (Purple theme)
7. **Muscle** - Imposing enforcer in tactical gear (Purple theme)
8. **Lookout** - Alert observer on rooftop (Purple theme)
9. **Fence** - Street-smart dealer in alley shop (Purple theme)
10. **Cat Burglar** - Agile infiltrator scaling building (Purple theme)
11. **Cleaner** - Meticulous professional with UV light (Purple theme)
12. **Pickpocket** - Invisible street artist in crowd (Purple theme)

## Usage Commands

### List All Roles
```bash
cd scripts
python3 generate_role_images.py --list
```

### Generate All 12 Roles
```bash
python3 generate_role_images.py
```

### Generate Specific Role
```bash
python3 generate_role_images.py --role hacker
python3 generate_role_images.py --role cat_burglar
python3 generate_role_images.py --role mastermind
```

## Troubleshooting

### API Key Issue
If you get "API Key not found" error, verify:

1. **Check .env file has API key:**
   ```bash
   cat .env | grep GEMINI_API_KEY
   ```

2. **Verify API key is valid:**
   - Go to https://aistudio.google.com/app/apikey
   - Check your key is active
   - Ensure Gemini API is enabled

3. **Test API key directly:**
   ```bash
   cd scripts
   python3 -c "from config import GEMINI_API_KEY; print(f'Key loaded: {GEMINI_API_KEY[:20]}...')"
   ```

### Alternative: Generate Manually

If the script has issues, you can generate each role manually using `generate_npc_image.py`:

```bash
# Example: Generate Hacker
python3 generate_npc_image.py \
  --name "The Hacker" \
  --role "Tech Specialist" \
  --gender person \
  --ethnicity "young Asian" \
  --clothing "tech hoodie with cyberpunk patches, fingerless gloves, AR glasses" \
  --background "dark room filled with multiple glowing monitors showing code and security feeds" \
  --expression "focused and intense" \
  --details "neon underglow on equipment, tangled cables and wires around, laptop open" \
  --attitude "tech-obsessed genius, in the zone" \
  --accent-colors "blue" \
  --output "output/role_images/hacker.png"
```

All the prompts are in `scripts/generate_role_images.py` in the `ROLE_DESIGNS` dictionary.

## Output Structure

Generated images will be saved to:
```
output/
  role_images/
    mastermind.png
    hacker.png
    safe_cracker.png
    driver.png
    insider.png
    grifter.png
    muscle.png
    lookout.png
    fence.png
    cat_burglar.png
    cleaner.png
    pickpocket.png
```

## Integration with Flutter

### Step 1: Copy Images to Assets
```bash
# Create assets directory
mkdir -p app/assets/roles

# Copy generated images
cp output/role_images/*.png app/assets/roles/
```

### Step 2: Update pubspec.yaml
```yaml
flutter:
  assets:
    - assets/roles/
```

### Step 3: Update Role Selection Modal

**Current UI (with emoji icons):**
```dart
Icon(
  Icons.star,  // Mastermind
  size: 48,
  color: AppColors.accentPrimary,
)
```

**Updated UI (with character portraits):**
```dart
ClipRRect(
  borderRadius: BorderRadius.circular(8),
  child: Image.asset(
    'assets/roles/mastermind.png',
    width: 100,
    height: 100,
    fit: BoxFit.cover,
  ),
)
```

### Example Full Role Card

```dart
Container(
  decoration: BoxDecoration(
    border: Border.all(color: AppColors.accentPrimary),
    borderRadius: BorderRadius.circular(12),
  ),
  child: Column(
    children: [
      // Character portrait
      ClipRRect(
        borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
        child: Image.asset(
          'assets/roles/${roleId}.png',
          width: double.infinity,
          height: 150,
          fit: BoxFit.cover,
        ),
      ),
      
      // Role info
      Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          children: [
            Text(
              roleName,
              style: TextStyle(
                color: AppColors.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              roleDescription,
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    ],
  ),
)
```

## Benefits of Character Portraits

✅ **Professional Look:** Game-quality character art  
✅ **Visual Consistency:** Matches NPC portraits  
✅ **Better UX:** Players connect with characters, not emojis  
✅ **Personality:** Each role has distinctive appearance  
✅ **Unified Theme:** Purple night heist aesthetic throughout  
✅ **Memorable:** Easier to remember roles by appearance  

## Next Steps

1. ✅ Script created and tested
2. ✅ Documentation written
3. ⏳ Generate all 12 role images
4. ⏳ Copy images to Flutter assets
5. ⏳ Update pubspec.yaml
6. ⏳ Update role selection modal UI
7. ⏳ Test image loading and display

## Quick Start

To generate all role images right now:

```bash
cd /Users/bbarrand/Documents/Projects/TheHeist/scripts
python3 generate_role_images.py
```

This will generate all 12 character portraits in about 2-3 minutes using nano-banana's fast generation.

## Notes

- Images use Google's SynthID watermark (authenticity mark)
- Generation is very fast (~2-3 seconds per image)
- Cost-effective using nano-banana model
- High-quality results in Borderlands style
- Can regenerate individual roles if needed

## Questions?

If you encounter any issues:
1. Check the API key in `.env`
2. Verify Google GenAI SDK is installed: `pip install google-genai`
3. Try generating one role first to test: `python3 generate_role_images.py --role hacker`
4. Check output folder permissions: `ls -la output/`

---

**Ready to generate?** Run `python3 generate_role_images.py` to create all 12 role portraits! 🎭
