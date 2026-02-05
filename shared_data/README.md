# Shared Data

This directory contains **shared configuration data** used by both frontend and backend.

## Files

### `roles.json`
Defines all playable character roles in the game:
- Role IDs (mastermind, hacker, safe_cracker, etc.)
- Display names and descriptions
- Role-specific minigames
- Character art/icons

**Used by:**
- **Frontend** (`frontend/lib/services/roles_service.dart`) - Role selection UI
- **Backend scripts** (`backend/scripts/generate_experience.py`) - AI experience generation

### `scenarios.json`
Defines all heist scenarios available in the game:
- Scenario IDs (museum_gala_vault, train_robbery, etc.)
- Titles and descriptions
- Required/recommended roles
- Difficulty ratings
- Thumbnail images

**Used by:**
- **Frontend** (`frontend/lib/services/scenarios_service.dart`) - Scenario selection UI
- **Backend scripts** (`backend/scripts/generate_experience.py`) - AI experience generation

## Integration

### Frontend
The Flutter app accesses these files via a symlink:
```
frontend/assets/data/ → ../../shared_data/
```

Files are bundled into the app at build time via `pubspec.yaml`:
```yaml
assets:
  - assets/data/
```

### Backend Scripts
Python scripts access files directly:
```python
DATA_DIR = PROJECT_ROOT / 'shared_data'
roles = load_json(DATA_DIR / 'roles.json')
```

## Single Source of Truth

These files are the **authoritative source** for:
- What roles exist in the game
- What scenarios are available
- Role capabilities and minigames

Any changes here automatically affect both frontend and backend.

## Adding New Content

### New Role
1. Edit `roles.json`
2. Add role definition with minigames
3. Frontend and backend will pick it up automatically

### New Scenario
1. Edit `scenarios.json`
2. Add scenario definition
3. Create experience file in `backend/experiences/`
4. Frontend and backend will pick it up automatically
