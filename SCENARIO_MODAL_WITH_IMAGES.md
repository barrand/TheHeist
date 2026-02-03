# Scenario Selection Modal with Images ✅

Complete scenario selection system with 200px scene images and modal UI!

## 🎭 Implementation Complete

### What's New
1. ✅ **Scenario selection modal** (like role selection)
2. ✅ **11 scenario scene images** (200px × 200px)
3. ✅ **Economy tier** (Gemini Flash for cost savings)
4. ✅ **Simplified name entry** (no gender selector there)
5. ✅ **Gender toggle in role modal only**

## 📱 UI Flow

### Simplified Onboarding
```
Landing Page
    ↓
Enter Name Only (no gender)
    ↓
Join Lobby
    ↓
Host: Tap Scenario Button → Opens Modal
    ↓
Browse 11 Scenarios with 200px Images
    ↓
Select Scenario → Returns to Lobby
```

### Scenario Selector Button (Lobby)
```
┌──────────────────────────────────────┐
│  🎭 SCENARIO                         │
│                                      │
│  ┌────────────────────────────────┐ │
│  │ 🏛️ Museum Gala Vault Heist  > │ │ ← Tappable (host only)
│  │ Steal the jewels from the...   │ │
│  └────────────────────────────────┘ │
│  Tap to browse all scenarios        │
└──────────────────────────────────────┘
```

### Scenario Selection Modal
```
┌─────────────────────────────────────────────┐
│  SELECT SCENARIO                      ✕    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  [200x200]   Museum Gala Vault     ✓│   │
│  │  Scene       Heist                  │   │
│  │  Image       Infiltrate a gala,     │   │
│  │              secure access...       │   │
│  │                                     │   │
│  │              Required Roles:        │   │
│  │              [Mastermind]           │   │
│  │              [Safe Cracker]         │   │
│  │              [Insider]              │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  [200x200]   Casino Vault Night     │   │
│  │  Scene       Blend in on the       │   │
│  │  Image       floor, disable...      │   │
│  │                                     │   │
│  │              Required Roles:        │   │
│  │              [Mastermind] [Hacker]  │   │
│  │              [Safe Cracker]         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  (... 9 more scenarios ...)                │
└─────────────────────────────────────────────┘
```

## 🎨 Generated Scenario Images

All 11 dramatic establishing shots in Borderlands style:

1. **🏛️ Museum Gala Vault** (1.9M) - Grand hall, gala event
2. **🏰 Mansion Panic Room** (1.4M) - Luxury mansion interior
3. **🎰 Casino Vault Night** (1.8M) - Casino floor, neon lights
4. **🚂 Armored Train** (1.7M) - Train interior in motion
5. **🔬 Secure Lab** (1.9M) - High-tech research lab
6. **🏢 Office Bug Plant** (1.5M) - Executive office at night
7. **🖼️ Gallery Art Swap** (1.4M) - Modern art gallery
8. **🏦 Bank Safe Deposit** (1.9M) - Vault corridor
9. **🚔 Evidence Room** (1.8M) - Police storage room
10. **⛓️ Prison Extract** (1.7M) - Detention holding area
11. **🚢 Dockside Container** (1.7M) - Shipping yard at night

### Image Features
- **Size:** 200px × 200px display (1024×1024 source)
- **Model:** Gemini 2.5 Flash Image (economy tier)
- **Style:** Borderlands 2D illustration
- **Theme:** Purple night heist atmosphere
- **Setting:** Year 2020 contemporary
- **Total:** ~18MB for all 11 scenes

## 💻 Technical Implementation

### New Files Created

#### 1. `app/lib/widgets/modals/scenario_selection_modal.dart`
Modal UI for scenario selection:
- 600px wide modal
- 200px × 200px scene images
- Scenario name, summary, required roles
- Selection feedback with gold border
- Checkmark on selected scenario

#### 2. `app/lib/models/scenario.dart`
Scenario data model:
- scenarioId, name, theme, objective, summary
- rolesRequired list
- Auto-generated themeIcon (emoji)

#### 3. `app/lib/services/scenarios_service.dart`
Service to load scenarios:
- loadScenarios() from JSON
- getScenario(scenarioId)
- Caching for performance

#### 4. `scripts/generate_scenario_images.py`
Economy tier image generation:
- 11 scenario scene descriptions
- Uses `generate_npc_image_fast.py`
- Gemini Flash model for cost savings

#### 5. `scripts/generate_npc_image_fast.py`
Economy tier generator:
- Gemini 2.5 Flash Image
- For NPCs, objects, and scenes
- Cheaper than Imagen 4.0

### Updated Files

#### `app/lib/screens/landing_page.dart`
- ✅ Removed gender selector from name dialogs
- ✅ Simplified to name-only input
- ✅ Removed playerGender parameter

#### `app/lib/screens/room_lobby_screen.dart`
- ✅ Added scenario loading
- ✅ Replaced inline list with button + modal
- ✅ Added `_openScenarioSelectionModal()`
- ✅ Scenario button shows icon, name, objective
- ✅ Chevron icon indicates tappable (host only)

#### `app/pubspec.yaml`
- ✅ Added `assets/scenarios/` directory

## 🎯 User Experience

### Host Flow
1. Create room, enter name
2. See lobby with scenario button
3. **Tap scenario button** → Opens modal
4. Browse 11 scenarios with **200px images**
5. Read descriptions and required roles
6. **Tap to select** → Modal closes
7. Selected scenario shown in lobby

### Player Flow
1. Join room, enter name
2. See lobby with scenario display (read-only)
3. View host's selected scenario
4. Cannot tap or change (only host controls)

### Gender Selection Flow
1. Name entry: **No gender selector** ✅
2. Role modal: **Gender toggle present** (Female default)
3. Switch gender: **Instant image updates**
4. Select role: Modal closes

## 💰 Cost Optimization

### Two-Tier Strategy Working

**Premium Tier (Imagen 4.0):**
- 24 player role avatars
- High quality, seen constantly
- Generated once, reused forever

**Economy Tier (Gemini Flash):**
- 11 scenario scenes (generated ✅)
- Future: 50+ NPCs per scenario
- Future: 100+ inventory objects
- Lower cost, seen briefly

**Savings:**
- Scenarios: ~70% cost savings vs Imagen 4.0
- NPCs: ~70% cost savings (when generated)
- Objects: ~70% cost savings (when generated)
- Player avatars: Premium quality maintained

## 📂 Asset Organization

```
app/assets/
├── roles/                    ← PREMIUM (Imagen 4.0)
│   ├── mastermind_male.png   24 files
│   ├── mastermind_female.png
│   └── ...
├── scenarios/                ← ECONOMY (Gemini Flash)
│   ├── museum_gala_vault.png 11 files
│   ├── casino_vault_night.png
│   └── ...
├── images/npcs/              ← ECONOMY (future)
└── data/
    ├── roles.json
    └── scenarios.json
```

## 🎨 Visual Design

### Scenario Modal Layout
- **Left:** 200px × 200px scene image
- **Right:** Name, summary, required role tags
- **Selection:** Gold border + checkmark
- **Scrollable:** All 11 scenarios fit comfortably

### Scene Image Style
- Establishing shots of heist locations
- Borderlands art style (consistent with roles)
- Purple theme lighting
- Year 2020 contemporary setting
- Dramatic atmosphere

## ✅ Complete Feature Set

### Name Entry
- ✅ Simple name-only input
- ✅ No gender selection here
- ✅ Cleaner onboarding

### Scenario Selection
- ✅ Modal UI (like role selection)
- ✅ 11 scenarios with 200px images
- ✅ Descriptions and summaries
- ✅ Required roles displayed
- ✅ Host-only control
- ✅ Visual selection feedback

### Role Selection
- ✅ Modal UI with 200px images
- ✅ Gender toggle (Female default)
- ✅ 24 role avatars (male/female)
- ✅ Descriptions and minigames
- ✅ Diverse cast

### Image Generation
- ✅ Premium tier (Imagen 4.0) for player avatars
- ✅ Economy tier (Gemini Flash) for scenarios
- ✅ Ready for NPCs and objects

## 🚀 Ready to Test

### Test Checklist
- [ ] Name entry has no gender selector
- [ ] Host can tap scenario button
- [ ] Scenario modal opens with 11 options
- [ ] 200px scenario images display
- [ ] Scenario selection works
- [ ] Selected scenario updates in lobby
- [ ] Players see selected scenario (read-only)
- [ ] Role modal has gender toggle
- [ ] Gender selector not in name entry

### Expected Experience
1. **Faster onboarding** - Just name, no extra steps
2. **Visual browsing** - 200px scenario scenes
3. **Informed choice** - Read descriptions before selecting
4. **Cost-effective** - Economy tier for scenarios
5. **Professional UI** - Consistent modal design

---

**Summary:**
- **Scenario images:** 11 generated ✅
- **Model:** Gemini Flash (economy) ✅
- **Size:** 200px × 200px ✅
- **Modal UI:** Complete ✅
- **Gender entry:** Removed from name dialogs ✅
- **Gender toggle:** In role modal only ✅
- **Total assets:** 24 roles + 11 scenarios = 35 images

**Cost savings:** ~70% on scenarios vs Imagen 4.0 while maintaining visual quality! 💰✨
