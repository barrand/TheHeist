# Backend Assets

Static assets served by the backend or used by the frontend.

## Directory Structure

```
backend/assets/
└── images/
    ├── crew_celebration_success.png    # Success end screen image
    ├── crew_celebration_failure.png    # Failure end screen image
    └── (future: role images, scenario images, etc.)
```

## Crew Celebration Images

**Generated with:** `backend/scripts/generate_crew_celebration_image.py`

### crew_celebration_success.png
- **Purpose**: Game end screen for successful heist
- **Content**: Mastermind, Safe Cracker, and Hacker celebrating together
- **Style**: Borderlands comic book art (matches role images)
- **Mood**: Triumphant, high-fives, victory poses, golden lighting
- **Aspect Ratio**: 16:9 (wide format for group shot)
- **Size**: ~1.8MB

### crew_celebration_failure.png
- **Purpose**: Game end screen for failed heist
- **Content**: Mastermind, Safe Cracker, and Hacker in defeat/caught
- **Style**: Borderlands comic book art (matches role images)
- **Mood**: Defeated but defiant, police lights, dramatic shadows
- **Aspect Ratio**: 16:9 (wide format)
- **Size**: ~1.6MB

## Regenerating Images

If you need to regenerate crew celebration images with different roles:

```bash
cd backend/scripts

# Generate for specific experience
python generate_crew_celebration_image.py ../experiences/museum_gala_vault.md

# Test with default roles
python generate_crew_celebration_image.py
```

Then move the generated images from `scripts/output/` to `assets/images/`.

## Serving Images

These images can be:
1. **Backend-served**: Add static file serving endpoint in FastAPI
2. **Frontend assets**: Copy to `frontend/web/assets/images/` for Flutter web
3. **CDN**: Upload to cloud storage for production

Currently stored in backend for easy access and version control.
