# The Heist - Scripts

Python scripts for generating game content and prototypes.

---

## 📜 Scripts Overview

### 1. `generate_experience.py`
Generate complete heist experience files with tasks, NPCs, and dependencies.

**Usage:**
```bash
python generate_experience.py \
  --scenario "museum_gala_vault" \
  --roles "mastermind,hacker,grifter,safe_cracker" \
  --output "examples/my_heist.md"
```

**Features:**
- Generates discovery-based task systems
- Creates NPC personalities and clues
- Builds dependency chains
- Outputs markdown experience file

---

### 2. `generate_npc_image.py`
Generate NPC character portraits with theme-specific accent colors.

**Usage:**
```bash
# Using color scheme preset
python generate_npc_image.py \
  --name "Alex Rivera" \
  --role "Security Guard" \
  --gender person \
  --ethnicity "Latino" \
  --clothing "security uniform" \
  --background "museum entrance" \
  --accent-colors "purple"

# Custom colors
python generate_npc_image.py \
  --name "Sarah Chen" \
  --role "Curator" \
  --accent-colors "vibrant purple clothing, magenta accessories, cyan highlights"
```

**Color Schemes:**
- `gold` - Gold jewelry, bronze accents (classic luxury)
- `blue` - Cyan glowing, purple LEDs (tech heist)
- `purple` - Vibrant purple, magenta (night heist) ⭐ **Current theme**
- `red` - Red bandanas, orange highlights (high stakes)
- `green` - Emerald details, gold jewelry (money heist)
- `orange` - Warm orange, mustard yellow (vintage)

**Features:**
- Borderlands art style (2D illustration, cell-shaded)
- Fast generation (nano-banana / Gemini 2.5 Flash Image)
- Consistent theme integration
- 280x280px portraits

---

### 3. `generate_npc_prototype.py` ⭐ **NEW**
Generate standalone interactive NPC conversation prototypes for testing.

**Usage:**
```bash
python generate_npc_prototype.py \
  --name "Marcus Romano" \
  --role "Bank Security Chief" \
  --objective "Learn the night shift rotation schedule" \
  --info "Guards rotate every 4 hours: 8pm, 12am, 4am" \
  --scenario "You're a new janitor doing orientation" \
  --difficulty medium \
  --gender male \
  --ethnicity "Italian-American" \
  --clothing "security uniform" \
  --background "security office" \
  --expression "friendly but alert"
```

**Features:**
- 🎨 **Neon Purple theme** (matches Flutter app)
- 💬 **Free-form text input** (no multi-choice)
- 🤖 **LLM-powered detection** (checks if info was revealed)
- 🎭 **Auto-generates character image** (purple accents)
- 💪 **Difficulty settings** (easy, medium, hard)
- 📱 **Mobile-responsive** (480px max width)
- ⚡ **Standalone HTML** (no build step, just open in browser)

**Output:**
- `prototype/{name}_chat.html` - Interactive chat interface
- `prototype/{name}.png` - Character portrait (280x280px)

**Difficulty Levels:**
- **Easy**: Friendly, helpful, shares info willingly
- **Medium**: Professional, cautious, needs rapport building
- **Hard**: Suspicious, protective, requires significant trust

---

## 🚀 Quick Examples

### Generate a new NPC test scenario:
```bash
python generate_npc_prototype.py \
  --name "Dr. Elena Vasquez" \
  --role "Museum Curator" \
  --objective "Find out which painting is fake" \
  --info "The Monet in Gallery 3 is a replica" \
  --difficulty hard \
  --gender female \
  --ethnicity "Spanish" \
  --clothing "elegant blazer" \
  --background "museum gallery"
```

### Batch generate experience files:
```bash
# Generate multiple scenarios
for scenario in museum_gala train_robbery casino_heist; do
  python generate_experience.py --scenario "$scenario" --roles "mastermind,hacker,driver"
done
```

### Generate matching NPCs for a scenario:
```bash
# Generate security guard with purple theme
python generate_npc_image.py \
  --name "Alex Martinez" \
  --role "Security Guard" \
  --gender female \
  --clothing "uniform with vest" \
  --background "loading dock" \
  --accent-colors "purple"

# Generate matching prototype
python generate_npc_prototype.py \
  --name "Alex Martinez" \
  --role "Security Guard" \
  --objective "Learn camera blind spots" \
  --info "Northwest corner has no coverage" \
  --difficulty medium \
  --gender female \
  --clothing "uniform with vest"
```

---

## 📁 File Structure

```
scripts/
├── README.md                    (this file)
├── config.py                    (API key configuration)
├── generate_experience.py       (full heist generator)
├── generate_npc_image.py        (character portraits)
├── generate_npc_prototype.py    (interactive chat prototypes)
└── run_dev.sh                   (development server)

Generated files go to:
examples/                        (experience .md files)
prototype/                       (HTML prototypes & images)
```

---

## 🔑 Configuration

All scripts use `config.py` for API keys:

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

Create a `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

---

## 💡 Tips

**Testing NPC Conversations:**
1. Generate prototype with `generate_npc_prototype.py`
2. Open HTML file in browser
3. Test different conversation approaches
4. Adjust difficulty if needed
5. Use insights to improve experience generation

**Character Consistency:**
- Always use `--accent-colors "purple"` for current theme
- Keep character details consistent (gender, ethnicity, clothing)
- Use descriptive backgrounds for better context

**Rapid Iteration:**
- Prototypes are standalone (no build step)
- Regenerate anytime to test different scenarios
- Characters generate in ~7 seconds each

---

## 🐛 Troubleshooting

**"API key not found":**
- Check `.env` file exists
- Verify `GEMINI_API_KEY` is set
- Run from project root directory

**"No image generated":**
- Check Gemini API quota
- Verify API has image generation enabled
- Prototype will still work with placeholder

**"Import error":**
- Run `pip install -r requirements.txt`
- Ensure Python 3.9+

---

## 🎯 Next Steps

1. Generate prototypes for all major NPCs in scenarios
2. Test conversation flows with team
3. Refine difficulty settings based on testing
4. Use successful patterns in production app

---

**All scripts are ready to use!** 🎭✨
