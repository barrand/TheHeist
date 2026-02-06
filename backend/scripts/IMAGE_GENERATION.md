# Image Generation System

This system generates location and item images for game experiences using Google Imagen API.

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
3. **Generation Order** → Rooms → Items → NPCs (using nano-banana/Imagen 4.0)
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
4. Generates in order: Rooms → Items → NPCs (using nano-banana/Imagen 4.0)
5. Game starts after images are ready
6. Subsequent games with same experience start instantly (cached)

**Generation time:** ~30-60 seconds for new experiences, instant for cached experiences

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

### Location Images
- **Dimensions**: 300x150px (2:1 aspect ratio)
- **Style**: Borderlands cel-shaded, dark noir atmosphere
- **Format**: PNG
- **Model**: Imagen 4.0 (nano-banana) - highest quality
- **Naming**: `location_{location_id}.png`

### Item Images
- **Dimensions**: 80x80px (1:1 square)
- **Style**: Photo-realistic product shot
- **Background**: Transparent or dark gradient
- **Format**: PNG
- **Model**: Imagen 4.0 (nano-banana) - highest quality
- **Naming**: `item_{item_id}.png`

## Cost Estimation

**Imagen 4.0 (nano-banana) Pricing** (as of 2026):
- ~$0.04 per image generation (highest quality model)

**Typical Experience**:
- 5 locations × $0.04 = $0.20
- 8 items × $0.04 = $0.32
- **Total per experience: ~$0.52**

**Reusability**:
- Generated once per experience
- Cached permanently for that experience
- Used for unlimited game sessions
- Very cost-effective over time
- Higher quality worth the cost for immersive experience

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
