# Experience Files

This directory contains all playable heist experience files that can be loaded by the game.

## File Organization

### Production Experiences
Experience files ready for gameplay:
- `museum_gala_vault.md` - Manual crafted museum heist
- `generated_museum_gala_vault_2players.md` - AI-generated 2-player museum heist
- `generated_museum_4players.md` - AI-generated 4-player museum heist
- `generated_train_6players.md` - AI-generated 6-player train heist

### File Naming Convention

Generated files follow this pattern:
```
generated_{scenario_id}_{player_count}players.md
```

Examples:
- `generated_museum_gala_vault_2players.md`
- `generated_train_robbery_4players.md`
- `generated_bank_heist_6players.md`

## How Files Get Here

### 1. AI Generation (via `backend/scripts/generate_experience.py`)
Generated files are first saved to `backend/scripts/output/` for review:
```bash
cd backend/scripts
python generate_experience.py --scenario museum_gala_vault --roles mastermind hacker
# → saves to backend/scripts/output/museum_gala_vault_mastermind_hacker.md
```

### 2. Review and Move
After reviewing/editing the generated experience:
```bash
# Rename to match convention
mv backend/scripts/output/museum_gala_vault_mastermind_hacker.md \
   backend/experiences/generated_museum_gala_vault_2players.md
```

### 3. Manual Creation
You can also manually create experience files following the format in existing files.

## Loading Experiences

The `ExperienceLoader` service automatically finds files based on:
- Scenario ID (from `shared_data/scenarios.json`)
- Number of players
- File naming convention

Example:
```python
# When 2 players select museum_gala_vault scenario:
# Loader looks for: backend/experiences/generated_museum_gala_vault_2players.md
loader = ExperienceLoader(experiences_dir="experiences")
game_state = loader.load_experience("museum_gala_vault", ["mastermind", "hacker"])
```

## File Format

See existing files for the markdown format including:
- Scenario metadata (objective, timeline, locations)
- Role-specific tasks with dependencies
- NPC definitions
- Task types (🎮 minigame, 💬 NPC conversation, 🔍 search, etc.)
