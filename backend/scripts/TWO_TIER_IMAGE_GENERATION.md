# Two-Tier Image Generation System 🎨💰

Smart cost-optimization: Premium quality for player avatars, economy mode for NPCs and objects.

## 📊 System Overview

### Tier 1: PREMIUM (Imagen 4.0)
**Use for:** Player role avatars (12 roles × 2 genders = 24 images)
**Model:** `imagen-4.0-generate-001`
**API:** `client.models.generate_images()`
**Quality:** Highest - stunning detail, excellent prompt adherence
**Cost:** Higher (but only 24 images needed)
**Script:** `generate_role_images_gendered.py` → calls `generate_npc_image.py`

### Tier 2: ECONOMY (Gemini 2.5 Flash Image)
**Use for:** NPCs, inventory items, objects, props (hundreds of images)
**Model:** `gemini-2.5-flash-image`
**API:** `client.models.generate_content()`
**Quality:** Good - fast, consistent, Borderlands style
**Cost:** Lower (optimized for volume)
**Script:** `generate_npc_image_fast.py`

## 🎯 When to Use Each Tier

### Use Imagen 4.0 (Premium) For:
✅ **Player role avatars** (12 roles × 2 genders)
- Mastermind, Hacker, Safe Cracker, Driver
- Insider, Grifter, Muscle, Lookout
- Fence, Cat Burglar, Cleaner, Pickpocket
- Reason: Players see these constantly, need premium quality

### Use Gemini Flash (Economy) For:
✅ **NPCs** (many per scenario)
- Security guards
- Museum curators
- Parking attendants
- Bystanders
- Witnesses

✅ **Inventory items**
- Lockpicks
- Keycards
- Documents
- Tools
- Disguises

✅ **Objects and props**
- Safes
- Security cameras
- Computers
- Vehicles
- Evidence items

## 💻 Script Usage

### Premium: Player Role Avatars

**Script:** `generate_role_images_gendered.py`

```bash
# Generate all 24 player avatars (12 roles × 2 genders)
python3 generate_role_images_gendered.py

# Generate specific role
python3 generate_role_images_gendered.py --role hacker

# Generate all female versions only
python3 generate_role_images_gendered.py --gender female
```

**Uses:** Imagen 4.0 via `generate_npc_image.py`

### Economy: NPCs and Objects

**Script:** `generate_npc_image_fast.py`

```bash
# Generate NPC character
python3 generate_npc_image_fast.py \
  --name "Rosa Martinez" \
  --role "Parking Attendant" \
  --gender female \
  --ethnicity "Latina" \
  --clothing "reflective vest and uniform" \
  --background "parking garage with cars" \
  --expression "bored" \
  --accent-colors "purple"

# Generate inventory object
python3 generate_npc_image_fast.py \
  --name "Lockpick Set" \
  --role "Tool" \
  --object \
  --description "professional lockpicking tools in leather case, metallic picks and tension wrenches" \
  --accent-colors "purple"

# Generate game object
python3 generate_npc_image_fast.py \
  --name "Museum Painting" \
  --role "Target" \
  --object \
  --description "valuable renaissance painting in ornate gold frame" \
  --accent-colors "purple"
```

## 📂 File Organization

```
scripts/
├── generate_npc_image.py              ← PREMIUM (Imagen 4.0) for role avatars
├── generate_npc_image_fast.py         ← ECONOMY (Gemini Flash) for NPCs/objects
├── generate_role_images_gendered.py   ← Orchestrator for 24 role avatars
└── output/
    └── static_images/                 ← PREMIUM: Static images (roles, scenarios, crew celebration)
    └── object_images/                 ← ECONOMY: Inventory/objects
```

## 💰 Cost Optimization

### Scenario: Museum Heist
- **Player avatars:** 24 images × Imagen 4.0 = Higher cost (one-time)
- **NPCs:** 50+ characters × Gemini Flash = Lower cost (per scenario)
- **Objects:** 100+ items × Gemini Flash = Lower cost (inventory)

### Savings Example
```
Imagen 4.0:    $$$$$  (use sparingly - 24 player avatars)
Gemini Flash:  $      (use freely - 150+ NPCs and objects)

Total savings: ~80-90% on non-player assets
```

### Smart Strategy
- **Premium where it matters** - Player sees their avatar constantly
- **Economy for volume** - NPCs appear briefly, don't need max quality
- **Consistent style** - Both use Borderlands art style

## 🎨 Quality Comparison

### Imagen 4.0 (Premium)
- **Resolution:** 1024×1024
- **Detail:** Excellent facial features, texture, lighting
- **Prompt adherence:** Very high
- **Speed:** ~8-10 seconds per image
- **Best for:** Hero characters, player avatars

### Gemini 2.5 Flash Image (Economy)
- **Resolution:** 1024×1024
- **Detail:** Good, stylized Borderlands aesthetic
- **Prompt adherence:** Good
- **Speed:** ~5-7 seconds per image
- **Best for:** NPCs, objects, props, background elements

## 🔄 Migration Guide

### If You Need to Switch Tiers

**Upgrade NPC to Premium:**
```bash
# Use the main script (will use Imagen 4.0)
python3 generate_npc_image.py --name "Important NPC" --role "Boss" ...
```

**Downgrade to Economy:**
```bash
# Use the fast script (will use Gemini Flash)
python3 generate_npc_image_fast.py --name "Background Guard" --role "Security" ...
```

## 📝 Current Setup

### Premium Tier (Imagen 4.0)
✅ **24 role avatars generated**
- All in `scripts/output/static_images/`
- Deployed to `frontend/assets/static/`
- Male and female versions
- Ages: 15 (teens) to 40 (experienced)
- Diverse ethnicities
- Year 2020 setting
- 200×200px display in UI

### Economy Tier (Gemini Flash)
⚙️ **Ready for NPC generation**
- Script: `generate_npc_image_fast.py`
- Output: `scripts/output/npc_images/`
- Also supports objects: `scripts/output/object_images/`

## 🎮 Game Development Workflow

### Phase 1: Player Avatars (Done ✅)
```bash
cd scripts
python3 generate_role_images_gendered.py
cp output/static_images/*_*.png ../../frontend/assets/static/
```

### Phase 2: Scenario NPCs (Future)
```bash
cd scripts
python3 generate_npc_image_fast.py --name "Museum Guard" ...
python3 generate_npc_image_fast.py --name "Security Chief" ...
python3 generate_npc_image_fast.py --name "Curator" ...
# Generate 50+ NPCs quickly and cheaply
```

### Phase 3: Inventory Items (Future)
```bash
cd scripts
python3 generate_npc_image_fast.py --object --name "Lockpick" ...
python3 generate_npc_image_fast.py --object --name "Keycard" ...
python3 generate_npc_image_fast.py --object --name "Blueprint" ...
# Generate 100+ items quickly
```

## 📈 Scalability

### Single Scenario (Museum Heist)
- **Player avatars:** 24 images (Imagen 4.0) = $$$
- **NPCs:** 50 images (Gemini Flash) = $
- **Objects:** 100 images (Gemini Flash) = $$
- **Total:** 174 images, mostly economy tier

### Multiple Scenarios (5 Heists)
- **Player avatars:** 24 images (reused!) = $$$
- **NPCs:** 250 images (5 × 50) (Gemini Flash) = $$$
- **Objects:** 500 images (5 × 100) (Gemini Flash) = $$$$$
- **Total:** 774 images, 97% economy tier

**Smart cost optimization!** 🎯

## 🎨 Art Style Consistency

Both tiers use the same Borderlands art style:
- Bold thick outlines
- Cell-shaded comic book aesthetic
- Vibrant saturated colors
- Purple night heist theme
- Year 2020 contemporary setting

**Result:** Visual consistency across all game assets despite using different models!

## ✅ Summary

### Current Status
- ✅ **Imagen 4.0** - 24 player role avatars (premium quality)
- ✅ **Gemini Flash** - Ready for NPCs and objects (economy mode)
- ✅ **Both scripts** - Working and tested
- ✅ **Smart strategy** - Premium where visible, economy for volume

### Scripts Available
1. `generate_npc_image.py` - Premium (Imagen 4.0)
2. `generate_npc_image_fast.py` - Economy (Gemini Flash)
3. `generate_role_images_gendered.py` - Orchestrator for role avatars

### Next Steps
When you need to generate:
- **NPCs:** Use `generate_npc_image_fast.py`
- **Inventory:** Use `generate_npc_image_fast.py --object`
- **New roles:** Use `generate_role_images_gendered.py`

---

**Result:** Professional player avatars + cost-effective asset generation! 🎉💰
