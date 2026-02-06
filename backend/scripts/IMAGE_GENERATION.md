# Image Generation System

This system generates all visual assets for game experiences using Google Imagen API.

## Model Strategy

We use a **two-tier approach** to optimize quality and cost:

### Tier 1: Premium Quality (Imagen 4.0 - nano-banana)
**Used for:** Player role images (shared across all experiences)
- The Mastermind, Hacker, Safe Cracker, etc.
- Generated once in male/female versions
- Highest quality for player-facing characters
- Cost: ~$0.04 per image
- Total one-time cost: ~$0.96 for all 24 images

### Tier 2: Cost-Effective (Imagen 4.0 Fast)
**Used for:** Per-experience unique content
- Room/location images
- Item images  
- NPC character images
- Generated fresh for each new experience
- Good quality, fast, cost-effective
- Cost: ~$0.02 per image
- Typical experience cost: ~$0.32

**Why this works:**
- Players see their role avatar most → deserves premium quality
- Rooms/items/NPCs are unique per experience → hundreds of generations
- 50% cost savings on high-volume content
- Still excellent quality for environmental assets

## Architecture

### Storage Strategy

Images are stored **per experience ID** for reusability:

```
backend/generated_images/
├── museum_gala_vault/
│   ├── location_crew_hideout.png       (300x150px)
│   ├── location_grand_hall.png
│   ├── location_vault_room.png
│   ├── item_safe_cracking_tools.png    (80x80px)
│   ├── item_earpiece_set.png
│   └── item_gala_invitation.png
└── train_robbery/
    └── ...
```

**Benefits:**
- ✅ Generated once, reused for all games of same experience
- ✅ Cached permanently (no regeneration)
- ✅ Reduces API costs
- ✅ Faster subsequent games

### Generation Flow

1. **Host Clicks "Start Game"** → Backend checks if images exist for experience
2. **If Missing** → Generate images synchronously (blocks game start)
3. **Generation Order** → Rooms → Items → NPCs (using Imagen 3.0 Fast)
4. **Images Saved** → Stored in `backend/generated_images/[experience_id]/`
5. **Game Starts** → Players receive game with all images ready
6. **Frontend Requests** → Images served via HTTP endpoint

## Manual Generation Scripts

### Generate Location Images

```bash
cd backend
python scripts/generate_location_images.py experiences/museum_gala_vault.md
```

**Options:**
```bash
# Specify custom experience ID
python scripts/generate_location_images.py experiences/museum_gala_vault.md --experience-id custom_id
```

**What it does:**
- Parses experience file for locations
- Generates 300x150px images in Borderlands cel-shaded style
- Saves to `generated_images/[experience_id]/location_*.png`
- Skips existing images (safe to re-run)

### Generate Item Images

```bash
cd backend
python scripts/generate_item_images.py experiences/museum_gala_vault.md
```

**Options:**
```bash
# Specify custom experience ID
python scripts/generate_item_images.py experiences/museum_gala_vault.md --experience-id custom_id
```

**What it does:**
- Parses experience file for items
- Generates 80x80px photo-realistic item images
- Saves to `generated_images/[experience_id]/item_*.png`
- Skips existing images (safe to re-run)

### Generate Both (Convenience)

```bash
cd backend
python scripts/generate_location_images.py experiences/museum_gala_vault.md
python scripts/generate_item_images.py experiences/museum_gala_vault.md
```

Or create a convenience script to run both.

## Automatic Generation at Game Start

When the host clicks "Start Game", the backend automatically:

1. Checks if images exist for the experience ID
2. If missing, generates images synchronously (game waits)
3. Shows loading message to players: "🎨 Generating experience images..."
4. Generates in order: Rooms → Items → NPCs (using Imagen 3.0 Fast)
5. Game starts after images are ready
6. Subsequent games with same experience start instantly (cached)

**Generation time:** ~20-40 seconds for new experiences (faster with Imagen 3.0), instant for cached experiences

Logged to backend logs:
- `🎨 Starting image generation for [experience_id]...`
- `✅ Image generation complete for [experience_id]`

## Serving Images

Images are served via HTTP endpoints:

### Location Images
```
GET /api/images/{experience_id}/location/{location_id}
```

Example:
```
http://localhost:8000/api/images/museum_gala_vault/location/safe_house
```

### Item Images
```
GET /api/images/{experience_id}/item/{item_id}
```

Example:
```
http://localhost:8000/api/images/museum_gala_vault/item/burner_phone
```

### Check Generation Status
```
GET /api/images/{experience_id}/status
```

Response:
```json
{
  "experience_id": "museum_gala_vault",
  "location_images": 4,
  "item_images": 7,
  "ready": true
}
```

## Frontend Integration

### Loading Images with Placeholders

```dart
// Location image
Image.network(
  'http://localhost:8000/api/images/$experienceId/location/$locationId',
  width: 300,
  height: 150,
  errorBuilder: (context, error, stackTrace) {
    // Show emoji placeholder if image not ready
    return Container(
      width: 300,
      height: 150,
      color: AppColors.bgPrimary,
      child: Center(child: Text('📍', style: TextStyle(fontSize: 48))),
    );
  },
  loadingBuilder: (context, child, loadingProgress) {
    if (loadingProgress == null) return child;
    return CircularProgressIndicator();
  },
)

// Item image
Image.network(
  'http://localhost:8000/api/images/$experienceId/item/$itemId',
  width: 80,
  height: 80,
  errorBuilder: (context, error, stackTrace) {
    // Show emoji/icon placeholder
    return Icon(Icons.inventory_2, size: 40, color: AppColors.accentSecondary);
  },
)
```

## Image Specifications

### Location Images (Per-Experience)
- **Dimensions**: 300x150px (2:1 aspect ratio)
- **Style**: Borderlands cel-shaded, dark noir atmosphere
- **Format**: PNG
- **Model**: Imagen 3.0 Fast - cost-effective for unique content
- **Naming**: `location_{location_id}.png`
- **Storage**: `generated_images/{experience_id}/`

### Item Images (Per-Experience)
- **Dimensions**: 80x80px (1:1 square)
- **Style**: Photo-realistic product shot
- **Background**: Transparent or dark gradient
- **Format**: PNG
- **Model**: Imagen 3.0 Fast - cost-effective for unique content
- **Naming**: `item_{item_id}.png`
- **Storage**: `generated_images/{experience_id}/`

### NPC Images (Per-Experience)
- **Dimensions**: 256x256px square
- **Style**: Borderlands cel-shaded character portrait
- **Format**: PNG
- **Model**: Imagen 3.0 Fast - cost-effective for unique content
- **Naming**: `npc_{npc_id}.png`
- **Storage**: `generated_images/{experience_id}/`

### Player Role Images (Shared Across All Experiences)
- **Dimensions**: 256x256px square
- **Style**: Borderlands cel-shaded character portrait
- **Format**: PNG
- **Model**: Imagen 4.0 (nano-banana) - highest quality
- **Naming**: `{role_id}_{gender}.png` (e.g., `hacker_female.png`)
- **Storage**: `scripts/output/role_images/`
- **Note**: Generated once, reused for all experiences

## Cost Estimation

### Model Pricing (as of 2026)
- **Imagen 3.0 Fast**: ~$0.02 per image (per-experience content)
- **Imagen 4.0**: ~$0.04 per image (shared player roles)

### Per-Experience Generation Cost
**Typical Experience** (generated using Imagen 3.0 Fast):
- 5 locations × $0.02 = $0.10
- 8 items × $0.02 = $0.16
- 3 NPCs × $0.02 = $0.06
- **Total per experience: ~$0.32**

### One-Time Player Role Generation Cost
**All 12 Player Roles** (generated once using Imagen 4.0):
- 12 roles × 2 genders × $0.04 = $0.96
- **One-time cost, shared across all experiences**

### Overall Strategy
- ✅ **Per-experience content** (rooms, items, NPCs): Cheap & fast (Imagen 3.0)
- ✅ **Shared player roles**: Premium quality (Imagen 4.0)
- ✅ Experience images cached permanently, used for unlimited sessions
- ✅ Very cost-effective over time

## Troubleshooting

### Images not generating
1. Check backend logs: `tail -f /tmp/theheist-backend.log`
2. Look for: `🎨 Queued background image generation`
3. Check for errors in generation process

### Images not loading in frontend
1. Check image exists: `ls backend/generated_images/[experience_id]/`
2. Test endpoint: `curl http://localhost:8000/api/images/[experience_id]/location/safe_house`
3. Check browser console for 404 errors

### Re-generate all images
```bash
# Delete existing images
rm -rf backend/generated_images/museum_gala_vault/

# Re-run generation
python scripts/generate_location_images.py experiences/museum_gala_vault.md
python scripts/generate_item_images.py experiences/museum_gala_vault.md
```

## Future Enhancements

1. **Pre-generation**: Generate images when creating experience file
2. **WebSocket notifications**: Notify clients when images are ready
3. **Image optimization**: Compress images for faster loading
4. **Retina support**: Generate 2x versions for high-DPI displays
5. **CDN integration**: Serve from CDN in production
6. **Fallback images**: Generic location/item images if generation fails
