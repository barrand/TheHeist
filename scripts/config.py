"""
Configuration management for The Heist game.
Loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the project root (parent of scripts/)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# Validate configuration
if not GEMINI_API_KEY or GEMINI_API_KEY == 'PASTE_YOUR_API_KEY_HERE':
    raise ValueError(
        "GEMINI_API_KEY not set! "
        "Please add your API key to the .env file. "
        "Get your key from: https://aistudio.google.com/app/apikey"
    )

# Project paths
DATA_DIR = project_root / 'data'
DESIGN_DIR = project_root / 'design'
EXAMPLES_DIR = project_root / 'examples'
SCRIPTS_DIR = project_root / 'scripts'

print(f"✓ Loaded config: Using {GEMINI_MODEL}")
