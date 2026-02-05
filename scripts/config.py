"""
Configuration management for The Heist game.
Loads environment variables from .env file.

Centralized model configuration for all AI services:
- Experience Generation: Long-form heist scenario creation
- NPC Interactions: Real-time dialogue during gameplay (backend handles this)
- Image Generation: Role/scenario/NPC images (separate scripts)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the project root (parent of scripts/)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path, override=True)  # Override environment variables

# ============================================================================
# CENTRALIZED MODEL CONFIGURATION
# ============================================================================

# Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Experience Generation Model
# Used for: Generating full heist experiences with task trees, NPCs, discovery
# Needs: Long context, structured output, creativity
# Model: gemini-2.5-flash (fast, smart, cheap)
GEMINI_EXPERIENCE_MODEL = os.getenv('GEMINI_EXPERIENCE_MODEL', 'gemini-2.5-flash')

# NPC Interaction Model (used by backend during gameplay)
# Used for: Real-time NPC dialogue responses during gameplay
# Needs: Fast response, conversational, no thinking tokens
# Model: gemini-2.0-flash-lite (fastest, cheapest for real-time)
GEMINI_NPC_MODEL = os.getenv('GEMINI_NPC_MODEL', 'gemini-2.0-flash-lite')

# Image Generation Models
# Imagen 4.0: High-quality character portraits (roles, player avatars)
# Gemini 2.5 Flash Image: Fast, cheap for NPCs and objects
IMAGEN_MODEL = 'imagen-4.0-generate-001'
GEMINI_IMAGE_MODEL = 'gemini-2.5-flash-latest-image'

# ============================================================================

# Validate configuration
if not GEMINI_API_KEY or GEMINI_API_KEY == 'PASTE_YOUR_API_KEY_HERE':
    raise ValueError(
        "GEMINI_API_KEY not set! "
        "Please add your API key to the .env file. "
        "Get your key from: https://aistudio.google.com/app/apikey"
    )

# Project paths
DATA_DIR = project_root / 'shared_data'
DESIGN_DIR = project_root / 'design'
EXAMPLES_DIR = project_root / 'examples'
SCRIPTS_DIR = project_root / 'scripts'

print(f"✓ Loaded config:")
print(f"  - Experience Model: {GEMINI_EXPERIENCE_MODEL}")
print(f"  - NPC Model: {GEMINI_NPC_MODEL} (used by backend)")
print(f"  - Image Models: {IMAGEN_MODEL}, {GEMINI_IMAGE_MODEL}")
