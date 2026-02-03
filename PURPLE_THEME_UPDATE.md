# Purple Theme Update - Role & NPC Images

## Summary

Updated all role and NPC image generation to use a unified **purple night heist theme** for visual consistency. Removed all other color schemes (gold, blue, red, green, orange).

## Changes Made

### 1. ✅ Updated Role Images Script
**File:** `scripts/generate_role_images.py`

**Changed:** All 12 roles now use `"accent_colors": "purple"`

- **Mastermind** - Purple (was Gold)
- **Hacker** - Purple (was Blue)
- **Safe Cracker** - Purple (was Gold)
- **Driver** - Purple (was Red)
- **Insider** - Purple (was Green)
- **Grifter** - Purple ✓ (already purple)
- **Muscle** - Purple (was Red)
- **Lookout** - Purple (was Orange)
- **Fence** - Purple (was Green)
- **Cat Burglar** - Purple ✓ (already purple)
- **Cleaner** - Purple (was Blue)
- **Pickpocket** - Purple (was Orange)

### 2. ✅ Updated NPC Image Script
**File:** `scripts/generate_npc_image.py`

**Removed color schemes:**
- ❌ Gold - Classic heist luxury
- ❌ Blue - Tech heist
- ❌ Red - High stakes
- ❌ Green - Money heist
- ❌ Orange - Vintage heist

**Kept:**
- ✅ Purple - Night heist (vibrant purple, magenta, cyan highlights)

**Updated code:**
```python
# Before: Multiple color schemes
scheme_map = {
    "gold": [...],
    "blue": [...],
    "purple": [...],
    "red": [...],
    "green": [...],
    "orange": [...]
}

# After: Single purple theme
color_instructions = ["vibrant purple clothing accents", "magenta accessories", "cyan highlights"]
```

### 3. ✅ Updated Documentation
**Files:**
- `ROLE_IMAGE_DESIGNS.md`
- `GENERATE_ROLE_IMAGES_GUIDE.md`

**Changes:**
- Updated all role descriptions to show "Purple theme" instead of individual colors
- Updated color scheme section to explain unified purple aesthetic
- Updated examples to use `--accent-colors "purple"`

## Purple Theme Color Palette

The purple night heist theme includes:
- **Vibrant purple** - Primary color for clothing accents
- **Magenta** - Secondary color for accessories
- **Cyan highlights** - Tertiary color for glowing elements

This creates a cohesive Borderlands-style aesthetic that ties all characters together visually.

## Benefits

✅ **Visual Unity:** All characters share consistent color palette  
✅ **Cohesive Aesthetic:** Creates unified game identity  
✅ **Simpler System:** No need to choose/remember color schemes  
✅ **Night Heist Vibe:** Purple theme reinforces stealth/night operations  
✅ **Borderlands Style:** Vibrant colors match comic book art style

## Usage

### Generate All Role Images (with Purple Theme)
```bash
cd scripts
python3 generate_role_images.py
```

All 12 roles will automatically use the purple theme.

### Generate Individual Role
```bash
python3 generate_role_images.py --role hacker
python3 generate_role_images.py --role mastermind
```

### Generate NPC with Purple Theme
```bash
python3 generate_npc_image.py \
  --name "Rosa Martinez" \
  --role "Parking Attendant" \
  --gender female \
  --ethnicity "Latina" \
  --clothing "reflective vest and uniform" \
  --background "parking garage" \
  --expression "bored" \
  --accent-colors "purple"
```

The `--accent-colors` parameter now only accepts:
- `"purple"` - Uses the standard purple theme
- Custom list - e.g., `"vibrant purple jacket, magenta accessories, cyan glowing elements"`

## What Was Removed

### From generate_npc_image.py
- Gold color scheme and examples
- Blue color scheme and examples  
- Red color scheme and examples
- Green color scheme and examples
- Orange color scheme and examples
- Color scheme mapping logic (simplified to purple only)

### From Documentation
- References to multiple color schemes
- Color-coded role categories
- Theme-specific design rationale

## What Was Kept

✅ Borderlands art style (2D illustration, comic book, cell-shaded)  
✅ Character customization options (gender, ethnicity, clothing, etc.)  
✅ Background settings  
✅ Expression and attitude controls  
✅ Custom color option (can still specify exact colors if needed)  
✅ All 12 role character designs  
✅ Fast nano-banana image generation

## Files Modified

1. ✅ `scripts/generate_role_images.py` - All roles use purple
2. ✅ `scripts/generate_npc_image.py` - Removed other color schemes
3. ✅ `ROLE_IMAGE_DESIGNS.md` - Updated all role color references
4. ✅ `GENERATE_ROLE_IMAGES_GUIDE.md` - Updated guide with purple theme
5. ✅ `PURPLE_THEME_UPDATE.md` (NEW) - This summary document

## Before & After Comparison

### Before
```python
ROLE_DESIGNS = {
    "mastermind": {
        "accent_colors": "gold",  # Different colors per role
    },
    "hacker": {
        "accent_colors": "blue",
    },
    "driver": {
        "accent_colors": "red",
    }
}
```

### After
```python
ROLE_DESIGNS = {
    "mastermind": {
        "accent_colors": "purple",  # All use purple
    },
    "hacker": {
        "accent_colors": "purple",
    },
    "driver": {
        "accent_colors": "purple",
    }
}
```

## Visual Consistency

With all roles using the purple theme:
- Characters look like they belong to the same crew
- UI color palette (purple primary in design system) matches character art
- Night heist atmosphere reinforced throughout
- Easier to maintain visual consistency
- Players recognize it's all part of the same game world

## Next Steps

1. ✅ All scripts updated to purple theme
2. ✅ Documentation updated
3. ⏳ Generate all 12 role images with purple theme
4. ⏳ Regenerate any existing NPC images with purple theme (optional)
5. ⏳ Copy images to Flutter assets
6. ⏳ Update UI to use character portraits

## Testing

Verify purple theme works:
```bash
# List all roles (should all show purple in code)
cd scripts
python3 generate_role_images.py --list

# Generate test role
python3 generate_role_images.py --role hacker

# Check output
ls -la output/role_images/
```

## Complete! 🎭

All role and NPC image generation now uses a unified purple night heist theme. The visual identity is cohesive, the code is simpler, and the aesthetic matches your game's dark heist atmosphere.
